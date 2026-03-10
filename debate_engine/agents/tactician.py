"""战术师 — 战略情报探员

任务：融合心理分析 + 逻辑分析 → 生成作战计划
"""

import json
from openai import AsyncOpenAI

SYSTEM_PROMPT = """\
你是「战术师」，一位精通辩论策略的大师。你将心理情报和逻辑分析\
融合为一份可执行的辩论战略。

你会收到两份报告：
1. 分析师的心理画像（动机、触发点、不安全感）。
2. 逻辑师的结构分析（谬误、无效前提、反击点）。

你的任务是生成一份统一的「作战计划」—— 一份将对手的每个逻辑谬误\
关联到其心理脆弱性的战略指南。

生成一个 JSON 对象，包含以下字段：

{
  "strategic_summary": "2-3 句概述推荐的整体策略。",
  "attack_vectors": [
    {
      "fallacy_exploited": "要利用的谬误名称。",
      "psychological_link": "这个谬误如何关联到对方的不安全感或情绪触发点。",
      "recommended_move": "建议执行的具体修辞或逻辑动作。",
      "expected_reaction": "对手可能如何回应。"
    }
  ],
  "tone_guidance": {
    "surgeon": "外科手术式回复的语调和策略建议。",
    "tank": "坦克碾压式回复的语调和策略建议。",
    "nuclear": "核弹打击式回复的语调和策略建议。"
  },
  "traps_to_avoid": ["列出 2-3 个对手可能使用的反击手段，你不应落入的陷阱。"]
}

规则：
- 策略要有效，不要无谓地残忍。
- 根据用户的目标（辩论 / 降级 / 焚烧）调整策略。
- 所有内容必须用中文输出。
- 仅输出有效 JSON —— 不要 markdown 代码块，不要额外评论。
"""


class TacticianAgent:
    def __init__(self, client: AsyncOpenAI, model: str):
        self.client = client
        self.model = model

    async def run(
        self,
        context: str,
        opponent_message: str,
        goal: str,
        analyst_report: dict,
        logician_report: dict,
        history: str = "",
    ) -> dict:
        user_parts = []
        if history:
            user_parts.append(f"历史对话记录：\n{history}\n")
        user_parts.append(f"当前背景：\n{context}")
        user_parts.append(f"\n对手消息：\n{opponent_message}")
        user_parts.append(f"\n用户目标：{goal}")
        user_parts.append(f"\n分析师报告：\n{json.dumps(analyst_report, ensure_ascii=False, indent=2)}")
        user_parts.append(f"\n逻辑师报告：\n{json.dumps(logician_report, ensure_ascii=False, indent=2)}")

        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0.5,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "\n".join(user_parts)},
            ],
        )
        text = response.choices[0].message.content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(text)
