"""Internationalization — Chinese (zh) and English (en) UI strings."""

import locale as _locale

STRINGS: dict[str, dict] = {
    "zh": {
        # Startup
        "subtitle": "多智能体论证分析 — 支持多轮对话历史上下文",
        "api_info": "API: {base_url}  模型: {model}",
        # Pipeline phases
        "phase_parallel": "[bold cyan]阶段一：[/] 分析师 + 逻辑师 并行运行中...",
        "phase_synthesis": "[bold yellow]阶段二：[/] 战术师 合成作战计划中...",
        "phase_responses": "[bold green]阶段三：[/] 文案师 生成三级回复中...",
        # Goal labels
        "goal_debate": "辩论",
        "goal_deescalate": "降级",
        "goal_burn": "焚烧",
        # Input prompts
        "prompt_context": "[bold magenta]背景[/]（什么情况？）",
        "prompt_message": "[bold red]对方消息[/]（对方说了什么？）",
        "prompt_goal_header": "[bold]选择你的目标：[/]",
        "goal_1_label": "  [cyan]1[/] 辩论   — 在逻辑和内容上取胜",
        "goal_2_label": "  [yellow]2[/] 降级   — 化解冲突但不退让",
        "goal_3_label": "  [red]3[/] 焚烧   — 最大伤害",
        "prompt_goal": "[bold]目标 [1/2/3][/]",
        # Input table
        "table_title": "输入场景（第 {round_num} 轮）",
        "table_col_field": "字段",
        "table_col_content": "内容",
        "table_row_context": "背景",
        "table_row_message": "对方消息",
        "table_row_goal": "目标",
        # Round info
        "history_loaded": "[dim]已加载前 {n} 轮对话历史作为上下文[/]",
        "round_done": "[bold]第 {round_num} 轮分析完成",
        "round_saved": "[dim]第 {round_num} 轮已保存至会话历史[/]",
        # Summary report
        "summary_title": "[bold]综合分析报告[/]",
        "section_psych": "[bold cyan]◆ 心理分析摘要[/]",
        "label_motive": "  动机：",
        "label_trigger": "  触发点：",
        "label_insecurity": "  不安全感：",
        "label_style": "  沟通风格：",
        "section_logic": "[bold blue]◆ 逻辑分析摘要[/]",
        "label_fallacy": "  谬误{i}：",
        "label_arg_structure": "  论证结构：",
        "section_tactics": "[bold yellow]◆ 战术摘要[/]",
        "section_traps": "[dim red]◆ 需要避开的陷阱[/]",
        # Session
        "prompt_again": "[bold]继续分析下一条消息？[/]",
        "session_end": "[dim]会话结束，历史文件已清理。[/]",
        "error_prefix": "[bold red]错误：[/] ",
        "api_key_prompt": "[bold]API Key[/]",
        # Agent language instructions
        "agent_lang": "所有分析必须用中文输出。",
        "agent_lang_response": "所有回复必须用中文。",
    },
    "en": {
        # Startup
        "subtitle": "Multi-agent argument analysis — with multi-round context memory",
        "api_info": "API: {base_url}  Model: {model}",
        # Pipeline phases
        "phase_parallel": "[bold cyan]Phase 1:[/] Analyst + Logician running in parallel...",
        "phase_synthesis": "[bold yellow]Phase 2:[/] Tactician synthesizing battle plan...",
        "phase_responses": "[bold green]Phase 3:[/] Copywriter generating 3-tier responses...",
        # Goal labels
        "goal_debate": "Debate",
        "goal_deescalate": "De-escalate",
        "goal_burn": "Burn",
        # Input prompts
        "prompt_context": "[bold magenta]Context[/] (What's the situation?)",
        "prompt_message": "[bold red]Opponent's Message[/] (What did they say?)",
        "prompt_goal_header": "[bold]Choose your goal:[/]",
        "goal_1_label": "  [cyan]1[/] Debate      — Win on logic and substance",
        "goal_2_label": "  [yellow]2[/] De-escalate — Defuse without conceding",
        "goal_3_label": "  [red]3[/] Burn        — Maximum damage",
        "prompt_goal": "[bold]Goal [1/2/3][/]",
        # Input table
        "table_title": "Input Scenario (Round {round_num})",
        "table_col_field": "Field",
        "table_col_content": "Content",
        "table_row_context": "Context",
        "table_row_message": "Opponent Message",
        "table_row_goal": "Goal",
        # Round info
        "history_loaded": "[dim]Loaded {n} prior round(s) as context[/]",
        "round_done": "[bold]Round {round_num} Analysis Complete",
        "round_saved": "[dim]Round {round_num} saved to session history[/]",
        # Summary report
        "summary_title": "[bold]Comprehensive Analysis Report[/]",
        "section_psych": "[bold cyan]◆ Psychological Analysis[/]",
        "label_motive": "  Motive: ",
        "label_trigger": "  Trigger: ",
        "label_insecurity": "  Insecurity: ",
        "label_style": "  Comm. Style: ",
        "section_logic": "[bold blue]◆ Logic Analysis[/]",
        "label_fallacy": "  Fallacy {i}: ",
        "label_arg_structure": "  Argument Structure: ",
        "section_tactics": "[bold yellow]◆ Tactical Summary[/]",
        "section_traps": "[dim red]◆ Traps to Avoid[/]",
        # Session
        "prompt_again": "[bold]Continue analyzing another message?[/]",
        "session_end": "[dim]Session ended. History file cleaned up.[/]",
        "error_prefix": "[bold red]Error:[/] ",
        "api_key_prompt": "[bold]API Key[/]",
        # Agent language instructions
        "agent_lang": "All analysis must be output in English.",
        "agent_lang_response": "All responses must be in English.",
    },
}


def detect_lang() -> str:
    """Auto-detect language from system locale. Returns 'zh' or 'en'."""
    try:
        lang_code = _locale.getdefaultlocale()[0] or ""
        if lang_code.startswith("zh"):
            return "zh"
    except Exception:
        pass
    return "en"


def get_strings(lang: str) -> dict:
    """Return UI string dict for the given lang code."""
    return STRINGS.get(lang, STRINGS["en"])
