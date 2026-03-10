"""Logician — Structural Intelligence Agent

Skills: Formal Logic, Fallacy Detection
Task: Identify "where they went wrong"
"""

import json
from openai import AsyncOpenAI

_BASE_PROMPT = """\
你是「逻辑师」，一位精通形式逻辑、非形式谬误和论证理论的专家。\
你的任务是从结构上拆解对手的论证，找出每一个逻辑漏洞。

给定背景和对手的消息，生成一个 JSON 分析，包含以下字段：

{{
  "fallacies": [
    {{
      "name": "谬误名称（如：稻草人谬误、人身攻击、转移注意力、\
虚假二分法、诉诸权威、滑坡谬误、诉诸传统 等）",
      "quote": "对手消息中犯下此谬误的原文引用。",
      "explanation": "解释为什么这构成了所指谬误——引用逻辑结构。"
    }}
  ],
  "invalid_premises": [
    {{
      "premise": "陈述隐含或显式的前提。",
      "why_invalid": "解释为什么此前提不成立、虚假或具有误导性。"
    }}
  ],
  "argument_structure": "描述整体论证结构：演绎、归纳、溯因、\
还是纯修辞性？结论是否得到支撑？",
  "strongest_counterpoints": ["列出 2-3 个简明有力的反驳点，\
能直接击溃核心论点。"]
}}

规则：
- 只标记真正的谬误——不要过度检测。
- 如果论证实际上是合理的，诚实地说明。
- {lang_instruction}
- 仅输出有效 JSON —— 不要 markdown 代码块，不要额外评论。
"""


class LogicianAgent:
    def __init__(self, client: AsyncOpenAI, model: str, output_lang: str = "zh"):
        self.client = client
        self.model = model
        if output_lang == "en":
            lang_instruction = "All analysis must be output in English."
        else:
            lang_instruction = "所有分析必须用中文输出。"
        self.system_prompt = _BASE_PROMPT.format(lang_instruction=lang_instruction)

    async def run(self, context: str, opponent_message: str, history: str = "") -> dict:
        user_parts = []
        if history:
            user_parts.append(f"历史对话记录：\n{history}\n")
        user_parts.append(f"当前对话背景：\n{context}")
        user_parts.append(f"\n对手的消息：\n{opponent_message}")

        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0.3,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": "\n".join(user_parts)},
            ],
        )
        text = response.choices[0].message.content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(text)
