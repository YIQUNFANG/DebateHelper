#!/usr/bin/env python3
"""Debate Engine CLI — multi-agent argument analysis and response generation."""

import argparse
import asyncio
import os
import signal
import sys

from dotenv import load_dotenv
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
GOAL_ALIASES = {
    "debate": "Debate", "辩论": "Debate",
    "de-escalate": "De-escalate", "降级": "De-escalate",
    "burn": "Burn", "焚烧": "Burn",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="debate-engine",
        description="多智能体论证分析与回复生成 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
示例:
  # 交互模式（推荐）
  debate-engine --api-key sk-xxx

  # 单次模式
  debate-engine --api-key sk-xxx \\
    --context "我发了一个求婚视频" \\
    --message "倒贴，廉价" \\
    --goal burn

  # 使用 .env 文件
  cp .env.example .env   # 编辑 .env 填入密钥
  debate-engine

  # 使用环境变量
  export API_KEY=sk-xxx
  debate-engine

  # 兼容任何 OpenAI API（Ollama / LM Studio / Azure 等）
  debate-engine --base-url http://localhost:11434/v1 --api-key ollama --model llama3
""",
    )

    api = p.add_argument_group("API 配置")
    api.add_argument("--base-url", metavar="URL",
                     help="OpenAI 兼容 API 地址 (默认: $API_BASE_URL 或 https://api.openai.com/v1)")
    api.add_argument("--api-key", metavar="KEY",
                     help="API 密钥 (默认: $API_KEY)")
    api.add_argument("--model", metavar="MODEL",
                     help="模型名称 (默认: $MODEL_NAME 或 gpt-4o)")

    one_shot = p.add_argument_group("单次模式（全部提供则跳过交互输入）")
    one_shot.add_argument("-c", "--context", metavar="TEXT",
                          help="对话背景")
    one_shot.add_argument("-m", "--message", metavar="TEXT",
                          help="对方的消息")
    one_shot.add_argument("-g", "--goal", metavar="GOAL",
                          choices=["debate", "de-escalate", "burn", "辩论", "降级", "焚烧", "1", "2", "3"],
                          help="目标: debate/de-escalate/burn 或 辩论/降级/焚烧 或 1/2/3")

    return p.parse_args()


def resolve_config(args: argparse.Namespace) -> tuple[str, str, str]:
    """Resolve API config: CLI flags > env vars > .env file > interactive prompt."""
    load_dotenv()

    base_url = args.base_url or os.getenv("API_BASE_URL") or "https://api.openai.com/v1"
    api_key = args.api_key or os.getenv("API_KEY")
    model = args.model or os.getenv("MODEL_NAME") or "gpt-4o"

    if not api_key:
        api_key = Prompt.ask("[bold]API Key[/]")

    return base_url, api_key, model


def resolve_goal(raw: str) -> str:
    """Normalize goal input to internal key."""
    if raw in GOAL_CHOICES:
        return GOAL_CHOICES[raw]
    return GOAL_ALIASES.get(raw.lower(), raw)


def collect_input() -> tuple[str, str, str]:
    """Gather context, opponent message, and goal interactively."""
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
    return context, opponent_message, GOAL_CHOICES[goal_key]


def render_input(context: str, opponent_message: str, goal: str, round_num: int) -> None:
    table = Table(
        title=f"输入场景（第 {round_num} 轮）",
        box=box.ROUNDED,
        title_style="bold white",
        show_lines=True,
    )
    table.add_column("字段", style="bold", width=16)
    table.add_column("内容", ratio=1)
    table.add_row("背景", context)
    table.add_row("对方消息", f"[bold red]{opponent_message}[/]")
    table.add_row("目标", f"[bold magenta]{GOAL_MAP.get(goal, goal)}[/]")
    console.print(table)


def render_summary(analyst: dict, logician: dict, plan: dict) -> None:
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
    console.print(
        Panel(
            "\n".join(lines),
            title="[bold]综合分析报告[/]",
            title_align="left",
            border_style="bright_white",
            padding=(1, 2),
        )
    )


def render_responses(responses: dict) -> None:
    tiers = [
        ("tier_1_surgeon", "green"),
        ("tier_2_tank", "blue"),
        ("tier_3_nuclear", "red"),
    ]
    for key, color in tiers:
        tier = responses.get(key, {})
        label = tier.get("label", key)
        desc = tier.get("description", "")
        body = tier.get("response", "—")

        console.print()
        console.print(
            Panel(
                f"[dim]{desc}[/]\n\n{body}",
                title=f"[bold {color}]{label}[/]",
                border_style=color,
                padding=(1, 2),
            )
        )


async def run_round(
    orchestrator: DebateOrchestrator,
    history: ContextHistory,
    context: str,
    opponent_message: str,
    goal: str,
) -> None:
    """Execute one full analysis round."""
    round_num = history.round_count() + 1

    render_input(context, opponent_message, goal, round_num)
    console.print()

    history_text = history.format_for_agents()
    if round_num > 1:
        console.print(f"[dim]已加载前 {round_num - 1} 轮对话历史作为上下文[/]")

    state = State(
        context=context,
        opponent_message=opponent_message,
        goal=goal,
        history=history_text,
    )

    current_status = None

    def on_phase(name: str) -> None:
        nonlocal current_status
        if current_status:
            current_status.stop()
        label = PHASE_LABELS.get(name, name)
        current_status = console.status(label, spinner="dots")
        current_status.start()

    try:
        state = await orchestrator.run(state, on_phase=on_phase)
    finally:
        if current_status:
            current_status.stop()

    history.append_round(
        context=context,
        opponent_message=opponent_message,
        goal=goal,
        analyst_report=state.analyst_report,
        logician_report=state.logician_report,
        battle_plan=state.battle_plan,
        responses=state.responses,
    )

    console.print()
    console.rule(f"[bold]第 {round_num} 轮分析完成", style="green")

    render_summary(state.analyst_report, state.logician_report, state.battle_plan)
    render_responses(state.responses)

    console.print()
    console.print(f"[dim]第 {round_num} 轮已保存至会话历史[/]")
    console.rule("[dim]", style="dim")


async def async_main() -> None:
    args = parse_args()

    console.print(BANNER, style="bold cyan")
    console.print("[dim]多智能体论证分析 — 支持多轮对话历史上下文\n[/]")

    base_url, api_key, model = resolve_config(args)
    console.print(f"[dim]API: {base_url}  模型: {model}[/]\n")

    orchestrator = DebateOrchestrator(base_url, api_key, model)
    history = ContextHistory()

    def _sigint_handler(sig, frame):
        console.print("\n[dim]会话结束，历史文件已清理。[/]")
        sys.exit(0)

    signal.signal(signal.SIGINT, _sigint_handler)

    # One-shot mode: all inputs provided via CLI
    if args.context and args.message and args.goal:
        goal = resolve_goal(args.goal)
        await run_round(orchestrator, history, args.context, args.message, goal)
        return

    # Interactive loop
    while True:
        try:
            context, opponent_message, goal = collect_input()
        except (EOFError, KeyboardInterrupt):
            break

        try:
            await run_round(orchestrator, history, context, opponent_message, goal)
        except Exception as e:
            console.print(f"\n[bold red]错误：[/] {e}")
            continue

        console.print()
        try:
            again = Prompt.ask(
                "[bold]继续分析下一条消息？[/]",
                choices=["y", "n"],
                default="n",
            )
        except (EOFError, KeyboardInterrupt):
            break
        if again != "y":
            break

    console.print("[dim]会话结束，历史文件已清理。[/]")


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
