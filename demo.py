#!/usr/bin/env python3
"""Demo runner — runs the full pipeline with mocked LLM calls (no API key needed)."""

import asyncio
import json
import signal
import sys
from unittest.mock import AsyncMock, MagicMock, patch

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box

from debate_engine.engine import DebateOrchestrator, State
from debate_engine.context_history import ContextHistory

console = Console()

BANNER = r"""
 ____       _           _         _____             _
|  _ \  ___| |__   __ _| |_ ___  | ____|_ __   __ _(_)_ __   ___
| | | |/ _ \ '_ \ / _` | __/ _ \ |  _| | '_ \ / _` | | '_ \ / _ \
| |_| |  __/ |_) | (_| | ||  __/ | |___| | | | (_| | | | | |  __/
|____/ \___|_.__/ \__,_|\__\___| |_____|_| |_|\__, |_|_| |_|\___|
                                               |___/
"""

PHASE_LABELS = {
    "parallel_analysis": "[bold cyan]阶段一：[/] 分析师 + 逻辑师 并行运行中...",
    "strategic_synthesis": "[bold yellow]阶段二：[/] 战术师 合成作战计划中...",
    "response_generation": "[bold green]阶段三：[/] 文案师 生成三级回复中...",
}

GOAL_CHOICES = {"1": "Debate", "2": "De-escalate", "3": "Burn"}
GOAL_MAP = {"Debate": "辩论", "De-escalate": "降级", "Burn": "焚烧"}

# ── Mock Responses ───────────────────────────────────────────────────────────

SCENARIOS = {
    "default": {
        "analyst": {
            "motive_analysis": (
                "评论者使用'倒贴'和'廉价'这两个带有强烈性别规训色彩的词，"
                "本质上是在执行一种社会惩罚机制——惩罚一个女性主动表达爱意、"
                "打破了'男追女'的传统权力结构。这是典型的基本归因错误："
                "他们将你的主动求婚归因于你的'价值低'，而非你的勇气和自信。"
                "在归因理论框架下，这是一种防御性外部归因——通过贬低你的行为"
                "来维护他们内心中'女性不该主动'的既有信念体系。"
            ),
            "emotional_trigger": (
                "嫉妒与认知失调的混合体。看到一个女生勇敢追爱并被接受，"
                "触发了他们对自身感情状况的不满（单身焦虑或关系中缺乏被爱的安全感）。"
                "另一种可能：他们内化了'女性主动=掉价'的厌女叙事，"
                "看到有人打破这个叙事会产生强烈不适，因为这威胁到了他们的世界观。"
            ),
            "underlying_insecurity": (
                "他们可能从未体验过被人全力以赴地爱，"
                "也没有勇气主动表达过自己的感情。看到你做了他们不敢做的事，"
                "用贬低来消解自己的无力感。或者他们在亲密关系中把'被追求'等同于"
                "'被需要'和'有价值'，你的行为动摇了他们衡量自我价值的唯一标尺。"
            ),
            "communication_style": "攻击型（aggressive）+ 道德审判型",
            "leverage_points": [
                "他们用'倒贴'和'廉价'暴露了自己把感情当作交易的思维——爱情在他们眼里是议价，不是表达。",
                "他们对一个陌生人的幸福时刻进行恶意评价，说明他们自己的生活中严重缺乏幸福感。",
                "他们躲在评论区输出恶意却不敢暴露自己，说明他们深知自己的观点不堪一击。",
            ],
        },
        "logician": {
            "fallacies": [
                {
                    "name": "预设前提谬误（Begging the Question）",
                    "quote": "倒贴",
                    "explanation": (
                        "'倒贴'这个词预设了一个未经论证的前提：女性主动求婚=失去价值。"
                        "这个前提本身就是需要被证明的论点，而非事实。"
                        "将'主动'等同于'低价值'是一个隐含的逻辑跳跃，"
                        "完全忽略了主动表达感情是勇气和自信的体现。"
                    ),
                },
                {
                    "name": "诉诸传统谬误（Appeal to Tradition）",
                    "quote": "倒贴、廉价",
                    "explanation": (
                        "评论者隐含的逻辑链条是：'传统上求婚应该由男方发起 → "
                        "女方主动求婚违反了传统 → 所以这是错的/廉价的'。"
                        "这是经典的诉诸传统谬误——'一直以来都是这样做的'不构成"
                        "'应该这样做'的有效论据。按此逻辑，女性也不该工作、不该投票。"
                    ),
                },
                {
                    "name": "人身攻击谬误（Ad Hominem）",
                    "quote": "廉价",
                    "explanation": (
                        "评论者没有对求婚行为本身提出任何实质性批评，"
                        "而是直接用'廉价'来贬低行为者的人格和价值。"
                        "这是典型的人身攻击——攻击人而非论点。"
                    ),
                },
            ],
            "invalid_premises": [
                {
                    "premise": "女性主动求婚意味着男方不够爱她或她'配不上'。",
                    "why_invalid": (
                        "主动求婚只能说明求婚者有勇气、有确定性、有表达爱的能力。"
                        "谁先开口与谁更爱谁之间没有任何因果关系。"
                    ),
                },
                {
                    "premise": "一个人的'价值'由是否被追求来决定。",
                    "why_invalid": (
                        "将个人价值与'被动等待被追求'绑定，本质上是一种物化思维——"
                        "把人当商品，把感情当拍卖。一个人的价值从来不由别人追不追她来定义。"
                    ),
                },
            ],
            "argument_structure": (
                "零论证结构。评论者没有提供任何推理过程，"
                "仅仅是将内化的性别偏见包装成价值判断直接抛出。"
                "这不是论证，而是基于厌女文化的条件反射。"
            ),
            "strongest_counterpoints": [
                "主动求婚需要的勇气，远大于躲在评论区贬低别人幸福所需的勇气。",
                "把爱情当作'谁先开口谁就输了'的博弈——这恰恰是很多人一辈子得不到真爱的原因。",
                "全世界越来越多的女性在主动求婚，你的观念不是'传统'，是'过时'。",
            ],
        },
        "tactician": {
            "strategic_summary": (
                "对手的攻击建立在一个腐朽的性别规训之上：'女人不该主动'。"
                "最优策略是三步走：第一，揭示他们'倒贴'叙事背后的物化逻辑——"
                "把人当商品估价；第二，反转框架——不是你'廉价'，而是他们"
                "把爱情理解为议价和博弈才是真正可悲的；第三，用你的幸福本身"
                "作为最终武器——你已经得到了你想要的，而他们只得到了一条酸评。"
            ),
            "attack_vectors": [
                {
                    "fallacy_exploited": "预设前提谬误",
                    "psychological_link": "他们把'主动=掉价'当作不言自明的真理，因为承认'主动=勇气'会暴露他们自己不敢主动追爱的懦弱。",
                    "recommended_move": "直接拆解'倒贴'的底层逻辑：它预设了爱情是一场交易，谁先出价谁就亏了。",
                    "expected_reaction": "大概率会用'你开心就好'之类的阴阳怪气来保留面子。",
                },
                {
                    "fallacy_exploited": "诉诸传统谬误",
                    "psychological_link": "他们依赖传统性别规范来获取安全感。当有人打破规范并且幸福时，他们的安全感就崩塌了。",
                    "recommended_move": "用归谬法：按你的逻辑，女人也不该主动表白、不该先说我爱你？",
                    "expected_reaction": "可能会说'这不一样'但说不出哪里不一样。",
                },
            ],
            "tone_guidance": {
                "surgeon": "云淡风轻的幸福感。让他们感受到你完全不在意他们的看法。",
                "tank": "冷静拆解。把'倒贴'和'廉价'背后的每一层逻辑谬误都摊开。",
                "nuclear": "怜悯式的降维打击。不是愤怒，而是'我替你的爱情观感到难过'。",
            },
            "traps_to_avoid": [
                "不要解释你和伴侣的关系有多好——你没有义务向陌生人自证幸福。",
                "不要显得被伤害了——任何防御姿态都会被他们解读为'戳中了'。",
                "不要攻击对方的感情状况——这会拉低你的格局，让战场变成互撕。",
            ],
        },
        "copywriter": {
            "tier_1_surgeon": {
                "label": "外科手术（精准打击）",
                "description": "高情商回复。不解释、不防御，用轻盈的幸福感碾压恶意。",
                "response": (
                    "哈哈谢谢关注～不过我觉得敢爱敢表达从来不叫廉价，"
                    "不敢爱还要酸别人的幸福，那才叫拧巴。"
                    "我求婚了，他答应了，我们都很开心——这就够了。"
                    "祝你也能早日遇到一个让你愿意放下'矜持'的人。"
                ),
            },
            "tier_2_tank": {
                "label": "坦克碾压（逻辑粉碎）",
                "description": "逐层拆解'倒贴'和'廉价'背后的逻辑谬误。",
                "response": (
                    "「倒贴」这个词有个隐含前提：爱情是一场交易，谁先出价谁就亏了。"
                    "按这个逻辑，先表白的人是倒贴，先说「我爱你」的人也是倒贴，"
                    "先关心对方的人还是倒贴——那你理想中的爱情是什么？两个人比赛谁更冷漠？\n\n"
                    "「廉价」更有意思。一个人鼓起勇气、精心准备、在众人面前表达爱意，"
                    "这需要的勇气和真心，远比躲在屏幕后面打两个字来得「昂贵」。\n\n"
                    "你不是在评价我的求婚，你是在暴露你对爱情的理解——"
                    "停留在「谁追谁就谁赢了」的阶段。这不叫传统，这叫遗憾。"
                ),
            },
            "tier_3_nuclear": {
                "label": "核弹打击（痛点直击）",
                "description": "怜悯式降维打击。不愤怒，而是用一种'我替你感到遗憾'的姿态。",
                "response": (
                    "我发了一个求婚视频，记录了我人生中最勇敢、最幸福的时刻。"
                    "你看完之后，从你人生经验里能挤出来的全部感受就是'倒贴'和'廉价'。\n\n"
                    "说真的，我不生气，我心疼你。"
                    "一个人得对爱情失望到什么程度，才会觉得主动去爱一个人是丢脸的事？"
                    "得活在多深的恐惧里，才会把「先开口」等于「输了」？\n\n"
                    "我求了婚，他说了愿意，我们在笑。"
                    "而你呢——你在别人的幸福底下打字，告诉自己这叫'廉价'。"
                    "我们俩谁的人生更廉价，评论区的人看得很清楚。"
                ),
            },
        },
    },
}


# ── Rendering (same as cli.py) ───────────────────────────────────────────────

def render_input(context, opponent_message, goal, round_num):
    table = Table(title=f"输入场景（第 {round_num} 轮）", box=box.ROUNDED,
                  title_style="bold white", show_lines=True)
    table.add_column("字段", style="bold", width=16)
    table.add_column("内容", ratio=1)
    table.add_row("背景", context)
    table.add_row("对方消息", f"[bold red]{opponent_message}[/]")
    table.add_row("目标", f"[bold magenta]{GOAL_MAP.get(goal, goal)}[/]")
    console.print(table)


def render_summary(analyst, logician, plan):
    lines = []
    lines.append("[bold cyan]◆ 心理分析摘要[/]")
    lines.append(f"  动机：{analyst.get('motive_analysis', '—')}")
    lines.append(f"  触发点：{analyst.get('emotional_trigger', '—')}")
    lines.append(f"  不安全感：{analyst.get('underlying_insecurity', '—')}")
    lines.append(f"  沟通风格：{analyst.get('communication_style', '—')}")
    lines.append("")
    lines.append("[bold blue]◆ 逻辑分析摘要[/]")
    for i, f in enumerate(logician.get("fallacies", []), 1):
        lines.append(f"  谬误{i}：{f.get('name', '?')}  ← 「{f.get('quote', '')}」")
    lines.append(f"  论证结构：{logician.get('argument_structure', '—')}")
    lines.append("")
    lines.append("[bold yellow]◆ 战术摘要[/]")
    lines.append(f"  {plan.get('strategic_summary', '—')}")
    traps = plan.get("traps_to_avoid", [])
    if traps:
        lines.append("")
        lines.append("[dim red]◆ 需要避开的陷阱[/]")
        for t in traps:
            lines.append(f"  • {t}")
    console.print()
    console.print(Panel("\n".join(lines), title="[bold]综合分析报告[/]",
                        title_align="left", border_style="bright_white", padding=(1, 2)))


def render_responses(responses):
    for key, color in [("tier_1_surgeon", "green"), ("tier_2_tank", "blue"), ("tier_3_nuclear", "red")]:
        tier = responses.get(key, {})
        console.print()
        console.print(Panel(
            f"[dim]{tier.get('description', '')}[/]\n\n{tier.get('response', '—')}",
            title=f"[bold {color}]{tier.get('label', key)}[/]",
            border_style=color, padding=(1, 2),
        ))


# ── Main ─────────────────────────────────────────────────────────────────────

async def main():
    console.print(BANNER, style="bold cyan")
    console.print("[dim]多智能体论证分析 — 演示模式（无需 API 密钥）\n[/]")

    history = ContextHistory()
    scenario = SCENARIOS["default"]

    signal.signal(signal.SIGINT, lambda s, f: (console.print("\n[dim]会话结束。[/]"), sys.exit(0)))

    while True:
        round_num = history.round_count() + 1

        console.print()
        context = Prompt.ask("[bold magenta]背景[/]（什么情况？）")
        console.print()
        opponent_message = Prompt.ask("[bold red]对方消息[/]（对方说了什么？）")
        console.print()
        console.print("[bold]选择你的目标：[/]")
        console.print("  [cyan]1[/] 辩论   — 在逻辑和内容上取胜")
        console.print("  [yellow]2[/] 降级   — 化解冲突但不退让")
        console.print("  [red]3[/] 焚烧   — 最大伤害")
        goal_key = Prompt.ask("[bold]目标 [1/2/3][/]", choices=["1", "2", "3"])
        goal = GOAL_CHOICES[goal_key]

        render_input(context, opponent_message, goal, round_num)
        console.print()

        if round_num > 1:
            console.print(f"[dim]已加载前 {round_num - 1} 轮对话历史作为上下文[/]")

        # Simulate pipeline phases
        with console.status(PHASE_LABELS["parallel_analysis"], spinner="dots"):
            await asyncio.sleep(1.2)
        with console.status(PHASE_LABELS["strategic_synthesis"], spinner="dots"):
            await asyncio.sleep(0.8)
        with console.status(PHASE_LABELS["response_generation"], spinner="dots"):
            await asyncio.sleep(1.0)

        history.append_round(
            context=context, opponent_message=opponent_message, goal=goal,
            analyst_report=scenario["analyst"], logician_report=scenario["logician"],
            battle_plan=scenario["tactician"], responses=scenario["copywriter"],
        )

        console.print()
        console.rule(f"[bold]第 {round_num} 轮分析完成", style="green")

        render_summary(scenario["analyst"], scenario["logician"], scenario["tactician"])
        render_responses(scenario["copywriter"])

        console.print()
        console.print(f"[dim]第 {round_num} 轮已保存至会话历史[/]")
        console.rule("[dim]", style="dim")

        console.print()
        again = Prompt.ask("[bold]继续分析下一条消息？[/]", choices=["y", "n"], default="n")
        if again != "y":
            break

    console.print("[dim]会话结束，历史文件已清理。[/]")


if __name__ == "__main__":
    asyncio.run(main())
