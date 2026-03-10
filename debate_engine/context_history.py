"""Context history manager — creates, appends, reads, and cleans up session history."""

import json
import atexit
from datetime import datetime
from pathlib import Path
import tempfile


class ContextHistory:
    """Manages a JSON history file that persists across rounds within a session."""

    def __init__(self):
        self._rounds: list[dict] = []
        # Use a tempfile so it works regardless of cwd
        self._file = Path(tempfile.mktemp(prefix="debate_history_", suffix=".json"))
        self._flush()
        atexit.register(self._delete)

    def _flush(self) -> None:
        self._file.write_text(
            json.dumps(self._rounds, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _delete(self) -> None:
        try:
            self._file.unlink(missing_ok=True)
        except Exception:
            pass

    @property
    def filepath(self) -> str:
        return str(self._file)

    def append_round(
        self,
        context: str,
        opponent_message: str,
        goal: str,
        analyst_report: dict,
        logician_report: dict,
        battle_plan: dict,
        responses: dict,
    ) -> None:
        self._rounds.append({
            "round": len(self._rounds) + 1,
            "timestamp": datetime.now().isoformat(),
            "input": {
                "context": context,
                "opponent_message": opponent_message,
                "goal": goal,
            },
            "analysis": {
                "analyst": analyst_report,
                "logician": logician_report,
            },
            "tactics": battle_plan,
            "responses": responses,
        })
        self._flush()

    def get_rounds(self) -> list[dict]:
        return list(self._rounds)

    def round_count(self) -> int:
        return len(self._rounds)

    def clear(self) -> None:
        """Clear all rounds and reset to a fresh session."""
        self._rounds.clear()
        self._flush()

    def format_for_agents(self) -> str:
        """Build a concise text summary of prior rounds for agent context injection."""
        if not self._rounds:
            return ""

        parts = []
        for r in self._rounds:
            inp = r["input"]
            analysis = r["analysis"]
            tactics = r["tactics"]
            resp = r["responses"]

            part = (
                f"=== 第 {r['round']} 轮 ===\n"
                f"背景：{inp['context']}\n"
                f"对方消息：{inp['opponent_message']}\n"
                f"目标：{inp['goal']}\n"
                f"动机分析：{analysis['analyst'].get('motive_analysis', '')}\n"
                f"沟通风格：{analysis['analyst'].get('communication_style', '')}\n"
                f"谬误："
            )
            fallacies = analysis["logician"].get("fallacies", [])
            part += "、".join(f.get("name", "?") for f in fallacies)
            part += f"\n战术摘要：{tactics.get('strategic_summary', '')}\n"

            for tier_key in ("tier_1_surgeon", "tier_2_tank", "tier_3_nuclear"):
                tier = resp.get(tier_key, {})
                if tier:
                    part += f"回复[{tier.get('label', tier_key)}]：{tier.get('response', '')}\n"

            parts.append(part)

        return "\n".join(parts)
