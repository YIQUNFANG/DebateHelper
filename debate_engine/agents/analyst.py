"""分析师 — 心理情报探员

技能：归因理论、自恋创伤检测
任务：解码「他们为什么这么说」
"""

import json
from openai import AsyncOpenAI

SYSTEM_PROMPT = """\
你是「分析师」，一位精通社会心理学、归因理论和自恋创伤检测的专家。\
你的任务是解码对手在冲突或辩论中发送消息背后的心理动机。

给定对话的背景和对手的消息，生成一个 JSON 分析，包含以下字段：

{
  "motive_analysis": "简明解释对方为什么说了这些话，引用归因理论\
（内部归因 vs 外部归因、基本归因错误、自利性偏差）。",
  "emotional_trigger": "驱动该消息的具体情绪（如：害怕失去地位、\
自尊受伤、被揭穿的焦虑、控制欲）。",
  "underlying_insecurity": "消息所揭示的深层不安全感或脆弱性——\
他们在保护或补偿什么。",
  "communication_style": "分类他们的沟通风格：攻击型、被动攻击型、\
轻蔑型、转移型、自大型 或 受害者姿态型。",
  "leverage_points": ["列出 2-3 个可以在回复中合理利用的心理施压点。"]
}

规则：
- 精确分析，基于可观察的语言线索，不要过度推测。
- 所有分析必须用中文输出。
- 仅输出有效 JSON —— 不要 markdown 代码块，不要额外评论。
"""


class AnalystAgent:
    def __init__(self, client: AsyncOpenAI, model: str):
        self.client = client
        self.model = model

    async def run(self, context: str, opponent_message: str, history: str = "") -> dict:
        user_parts = []
        if history:
            user_parts.append(f"历史对话记录：\n{history}\n")
        user_parts.append(f"当前对话背景：\n{context}")
        user_parts.append(f"\n对手的消息：\n{opponent_message}")

        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0.4,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "\n".join(user_parts)},
            ],
        )
        text = response.choices[0].message.content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(text)
