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
from debate_engine.i18n import detect_lang, get_strings

console = Console()

# ── Fancy block-character banner ──────────────────────────────────────────────

BANNER = r"""
[bold cyan]██████╗ [bold magenta]███████╗[bold cyan]██████╗  [bold magenta] █████╗ [bold cyan]████████╗[bold magenta]███████╗[/]
[bold cyan]██╔══██╗[bold magenta]██╔════╝[bold cyan]██╔══██╗[bold magenta]██╔══██╗[bold cyan]╚══██╔══╝[bold magenta]██╔════╝[/]
[bold cyan]██║  ██║[bold magenta]█████╗  [bold cyan]██████╔╝[bold magenta]███████║[bold cyan]   ██║   [bold magenta]█████╗  [/]
[bold cyan]██║  ██║[bold magenta]██╔══╝  [bold cyan]██╔══██╗[bold magenta]██╔══██║[bold cyan]   ██║   [bold magenta]██╔══╝  [/]
[bold cyan]██████╔╝[bold magenta]███████╗[bold cyan]██████╔╝[bold magenta]██║  ██║[bold cyan]   ██║   [bold magenta]███████╗[/]
[bold cyan]╚═════╝ [bold magenta]╚══════╝[bold cyan]╚═════╝ [bold magenta]╚═╝  ╚═╝[bold cyan]   ╚═╝   [bold magenta]╚══════╝[/]

[bold green]██╗  ██╗[bold yellow]███████╗[bold green]██╗     [bold yellow]██████╗ [bold green]███████╗[bold yellow]██████╗ [/]
[bold green]██║  ██║[bold yellow]██╔════╝[bold green]██║     [bold yellow]██╔══██╗[bold green]██╔════╝[bold yellow]██╔══██╗[/]
[bold green]███████║[bold yellow]█████╗  [bold green]██║     [bold yellow]██████╔╝[bold green]█████╗  [bold yellow]██████╔╝[/]
[bold green]██╔══██║[bold yellow]██╔══╝  [bold green]██║     [bold yellow]██╔═══╝ [bold green]██╔══╝  [bold yellow]██╔══██╗[/]
[bold green]██║  ██║[bold yellow]███████╗[bold green]███████╗[bold yellow]██║     [bold green]███████╗[bold yellow]██║  ██║[/]
[bold green]╚═╝  ╚═╝[bold yellow]╚══════╝[bold green]╚══════╝[bold yellow]╚═╝     [bold green]╚══════╝[bold yellow]╚═╝  ╚═╝[/]
"""

GOAL_CHOICES = {"1": "Debate", "2": "De-escalate", "3": "Burn"}
GOAL_ALIASES = {
    "debate": "Debate", "辩论": "Debate",
    "de-escalate": "De-escalate", "降级": "De-escalate",
    "burn": "Burn", "焚烧": "Burn",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="debate-engine",
        description="DebateHelper — Multi-agent argument analysis & tactical response CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  # Interactive mode (recommended)
  debate-engine --api-key sk-xxx

  # One-shot mode
  debate-engine --api-key sk-xxx \\
    -c "I posted a proposal video" \\
    -m "That's pathetic" \\
    -g burn

  # Chinese interface
  debate-engine --lang zh --api-key sk-xxx

  # Any OpenAI-compatible API (Ollama / LM Studio / Gemini / Azure)
  debate-engine --base-url http://localhost:11434/v1 --api-key ollama --model llama3
""",
    )

    api = p.add_argument_group("API Configuration")
    api.add_argument("--base-url", metavar="URL",
                     help="OpenAI-compatible API endpoint (default: $API_BASE_URL or https://api.openai.com/v1)")
    api.add_argument("--api-key", metavar="KEY",
                     help="API key (default: $API_KEY)")
    api.add_argument("--model", metavar="MODEL",
                     help="Model name (default: $MODEL_NAME or gpt-4o)")

    lang = p.add_argument_group("Language")
    lang.add_argument("--lang", metavar="LANG", choices=["zh", "en", "auto"],
                      default="auto",
                      help="UI language: zh (Chinese), en (English), auto (detect from locale). Default: auto")

    one_shot = p.add_argument_group("One-shot mode (skip interactive prompts when all provided)")
    one_shot.add_argument("-c", "--context", metavar="TEXT",
                          help="Conversation context / background")
    one_shot.add_argument("-m", "--message", metavar="TEXT",
                          help="Opponent's message")
    one_shot.add_argument("-g", "--goal", metavar="GOAL",
                          choices=["debate", "de-escalate", "burn", "辩论", "降级", "焚烧", "1", "2", "3"],
                          help="Goal: debate/de-escalate/burn or 1/2/3")

    return p.parse_args()


def resolve_config(args: argparse.Namespace, S: dict) -> tuple[str, str, str]:
    """Resolve API config: CLI flags > env vars > .env file > interactive prompt."""
    load_dotenv()

    base_url = args.base_url or os.getenv("API_BASE_URL") or "https://api.openai.com/v1"
    api_key = args.api_key or os.getenv("API_KEY")
    model = args.model or os.getenv("MODEL_NAME") or "gpt-4o"

    if not api_key:
        api_key = Prompt.ask(S["api_key_prompt"])

    return base_url, api_key, model


def resolve_goal(raw: str) -> str:
    """Normalize goal input to internal key."""
    if raw in GOAL_CHOICES:
        return GOAL_CHOICES[raw]
    return GOAL_ALIASES.get(raw.lower(), raw)


def resolve_lang(raw: str) -> str:
    """Resolve language setting."""
    if raw == "auto":
        return detect_lang()
    return raw


def collect_input(S: dict) -> tuple[str, str, str]:
    """Gather context, opponent message, and goal interactively."""
    console.print()
    context = Prompt.ask(S["prompt_context"])
    console.print()
    opponent_message = Prompt.ask(S["prompt_message"])
    console.print()
    console.print(S["prompt_goal_header"])
    console.print(S["goal_1_label"])
    console.print(S["goal_2_label"])
    console.print(S["goal_3_label"])
    goal_key = Prompt.ask(S["prompt_goal"], choices=["1", "2", "3"])
    return context, opponent_message, GOAL_CHOICES[goal_key]


def render_input(context: str, opponent_message: str, goal: str, round_num: int, S: dict) -> None:
    goal_display = {
        "Debate": S["goal_debate"],
        "De-escalate": S["goal_deescalate"],
        "Burn": S["goal_burn"],
    }
    table = Table(
        title=S["table_title"].format(round_num=round_num),
        box=box.ROUNDED,
        title_style="bold white",
        show_lines=True,
    )
    table.add_column(S["table_col_field"], style="bold", width=16)
    table.add_column(S["table_col_content"], ratio=1)
    table.add_row(S["table_row_context"], context)
    table.add_row(S["table_row_message"], f"[bold red]{opponent_message}[/]")
    table.add_row(S["table_row_goal"], f"[bold magenta]{goal_display.get(goal, goal)}[/]")
    console.print(table)


def render_summary(analyst: dict, logician: dict, plan: dict, S: dict) -> None:
    lines = []
    lines.append(S["section_psych"])
    lines.append(f"{S['label_motive']}{analyst.get('motive_analysis', '—')}")
    lines.append(f"{S['label_trigger']}{analyst.get('emotional_trigger', '—')}")
    lines.append(f"{S['label_insecurity']}{analyst.get('underlying_insecurity', '—')}")
    lines.append(f"{S['label_style']}{analyst.get('communication_style', '—')}")

    lines.append("")
    lines.append(S["section_logic"])
    for i, f in enumerate(logician.get("fallacies", []), 1):
        label = S["label_fallacy"].format(i=i)
        lines.append(f"{label}{f.get('name', '?')}  <- \"{f.get('quote', '')}\"")
    lines.append(f"{S['label_arg_structure']}{logician.get('argument_structure', '—')}")

    lines.append("")
    lines.append(S["section_tactics"])
    lines.append(f"  {plan.get('strategic_summary', '—')}")

    traps = plan.get("traps_to_avoid", [])
    if traps:
        lines.append("")
        lines.append(S["section_traps"])
        for t in traps:
            lines.append(f"  * {t}")

    console.print()
    console.print(
        Panel(
            "\n".join(lines),
            title=S["summary_title"],
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
    S: dict,
) -> None:
    """Execute one full analysis round."""
    round_num = history.round_count() + 1

    render_input(context, opponent_message, goal, round_num, S)
    console.print()

    phase_labels = {
        "parallel_analysis": S["phase_parallel"],
        "strategic_synthesis": S["phase_synthesis"],
        "response_generation": S["phase_responses"],
    }

    history_text = history.format_for_agents()
    if round_num > 1:
        console.print(S["history_loaded"].format(n=round_num - 1))

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
        label = phase_labels.get(name, name)
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
    console.rule(S["round_done"].format(round_num=round_num), style="green")

    render_summary(state.analyst_report, state.logician_report, state.battle_plan, S)
    render_responses(state.responses)

    console.print()
    console.print(S["round_saved"].format(round_num=round_num))
    console.rule("[dim]", style="dim")


async def async_main() -> None:
    args = parse_args()
    lang = resolve_lang(args.lang)
    S = get_strings(lang)

    console.print(BANNER)
    console.print(f"[dim]{S['subtitle']}\n[/]")

    base_url, api_key, model = resolve_config(args, S)
    console.print(f"[dim]{S['api_info'].format(base_url=base_url, model=model)}[/]\n")

    orchestrator = DebateOrchestrator(base_url, api_key, model, output_lang=lang)
    history = ContextHistory()

    def _sigint_handler(sig, frame):
        console.print(f"\n{S['session_end']}")
        sys.exit(0)

    signal.signal(signal.SIGINT, _sigint_handler)

    # One-shot mode: all inputs provided via CLI
    if args.context and args.message and args.goal:
        goal = resolve_goal(args.goal)
        await run_round(orchestrator, history, args.context, args.message, goal, S)
        return

    # Interactive loop
    while True:
        try:
            context, opponent_message, goal = collect_input(S)
        except (EOFError, KeyboardInterrupt):
            break

        try:
            await run_round(orchestrator, history, context, opponent_message, goal, S)
        except Exception as e:
            console.print(f"\n{S['error_prefix']}{e}")
            continue

        console.print()
        try:
            again = Prompt.ask(
                S["prompt_again"],
                choices=["y", "n"],
                default="n",
            )
        except (EOFError, KeyboardInterrupt):
            break
        if again != "y":
            break

    console.print(S["session_end"])


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
