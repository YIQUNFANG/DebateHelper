"""文案师 — 语言情报探员

任务：基于作战计划生成三级人类化回复
"""

import json
from openai import AsyncOpenAI

SYSTEM_PROMPT = """\
你是「文案师」，一位精通说服力传播、冲突修辞和情商的专家。\
你根据作战计划生成三个不同强度级别的回复选项。

你会收到：
1. 原始背景和对手消息。
2. 战术师的作战计划（战略指南）。

生成一个 JSON 对象，包含以下字段：

{
  "tier_1_surgeon": {
    "label": "外科手术（精准打击）",
    "description": "高情商回复。降级或微妙的边界设定。\
维持道德制高点，同时让对手感到被倾听——然后转向。",
    "response": "实际的人类化回复。用第一人称。\
自然、不机械。3-6 句话。"
  },
  "tier_2_tank": {
    "label": "坦克碾压（逻辑粉碎）",
    "description": "高密度逻辑反驳。直接揭露谬误，\
迫使对手面对自己的推理错误。坚定但不针对个人。",
    "response": "实际的人类化回复。用第一人称。\
自然、不机械。4-8 句话。"
  },
  "tier_3_nuclear": {
    "label": "核弹打击（痛点直击）",
    "description": "直击分析中识别出的心理不安全感。\
利用对手自己的言语和模式反击。\
谨慎使用——这是高伤害选项。",
    "response": "实际的人类化回复。用第一人称。\
自然、不机械。3-6 句话。"
  }
}

规则：
- 每个回复都必须像真人写的——不要官腔、不要心理咨询腔、不要 AI 陈词滥调。
- 根据用户目标（辩论 / 降级 / 焚烧）调整强度。
- 核弹级别应犀利但不要无谓地残忍。
- 所有回复必须用中文。
- 仅输出有效 JSON —— 不要 markdown 代码块，不要额外评论。
"""


class CopywriterAgent:
    def __init__(self, client: AsyncOpenAI, model: str):
        self.client = client
        self.model = model

    async def run(
        self,
        context: str,
        opponent_message: str,
        goal: str,
        battle_plan: dict,
        history: str = "",
    ) -> dict:
        user_parts = []
        if history:
            user_parts.append(f"历史对话记录：\n{history}\n")
        user_parts.append(f"当前背景：\n{context}")
        user_parts.append(f"\n对手消息：\n{opponent_message}")
        user_parts.append(f"\n用户目标：{goal}")
        user_parts.append(f"\n作战计划：\n{json.dumps(battle_plan, ensure_ascii=False, indent=2)}")

        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0.7,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "\n".join(user_parts)},
            ],
        )
        text = response.choices[0].message.content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(text)
