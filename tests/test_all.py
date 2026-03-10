"""Tests for debate-engine — no API key needed (all LLM calls mocked)."""

import asyncio
import json
import sys
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))


# ── 1. Import Tests ──────────────────────────────────────────────────────────

def test_package_import():
    from debate_engine import __version__
    assert __version__ == "1.0.0"
    print("[PASS] Package import + version")


def test_agents_import():
    from debate_engine.agents import AnalystAgent, LogicianAgent, TacticianAgent, CopywriterAgent
    assert all([AnalystAgent, LogicianAgent, TacticianAgent, CopywriterAgent])
    print("[PASS] All 4 agents importable")


def test_engine_import():
    from debate_engine.engine import DebateOrchestrator, State
    assert DebateOrchestrator and State
    print("[PASS] Engine importable")


def test_cli_import():
    from debate_engine.cli import parse_args, resolve_goal
    assert resolve_goal("burn") == "Burn"
    assert resolve_goal("焚烧") == "Burn"
    assert resolve_goal("1") == "Debate"
    assert resolve_goal("2") == "De-escalate"
    assert resolve_goal("3") == "Burn"
    assert resolve_goal("debate") == "Debate"
    assert resolve_goal("降级") == "De-escalate"
    print("[PASS] CLI import + goal resolution")


# ── 2. Context History Tests ─────────────────────────────────────────────────

def test_history_lifecycle():
    from debate_engine.context_history import ContextHistory

    h = ContextHistory()
    filepath = h.filepath
    assert Path(filepath).exists(), "History file should exist after init"
    assert h.round_count() == 0
    assert h.format_for_agents() == ""

    # Append a round
    h.append_round(
        context="test context",
        opponent_message="test msg",
        goal="Burn",
        analyst_report={"motive_analysis": "test motive", "communication_style": "aggressive"},
        logician_report={"fallacies": [{"name": "Ad Hominem"}], "argument_structure": "none"},
        battle_plan={"strategic_summary": "test strategy"},
        responses={"tier_1_surgeon": {"label": "Surgeon", "response": "resp1"}},
    )
    assert h.round_count() == 1

    # Verify file has content
    data = json.loads(Path(filepath).read_text())
    assert len(data) == 1
    assert data[0]["input"]["context"] == "test context"

    # Format for agents
    formatted = h.format_for_agents()
    assert "第 1 轮" in formatted
    assert "test context" in formatted
    assert "test motive" in formatted

    # Append second round
    h.append_round(
        context="ctx2", opponent_message="msg2", goal="Debate",
        analyst_report={"motive_analysis": "m2", "communication_style": "passive"},
        logician_report={"fallacies": [], "argument_structure": "weak"},
        battle_plan={"strategic_summary": "strat2"},
        responses={},
    )
    assert h.round_count() == 2
    formatted2 = h.format_for_agents()
    assert "第 1 轮" in formatted2
    assert "第 2 轮" in formatted2

    # Cleanup
    h._delete()
    assert not Path(filepath).exists(), "History file should be deleted"
    print("[PASS] History lifecycle (create → append → format → delete)")


# ── 3. State Tests ───────────────────────────────────────────────────────────

def test_state():
    from debate_engine.engine import State

    s = State("bg", "msg", "Burn", history="prior context")
    assert s.context == "bg"
    assert s.opponent_message == "msg"
    assert s.goal == "Burn"
    assert s.history == "prior context"
    assert s.analyst_report is None
    assert s.logician_report is None
    assert s.battle_plan is None
    assert s.responses is None
    print("[PASS] State initialization")


# ── 4. Agent Tests (mocked LLM) ─────────────────────────────────────────────

MOCK_ANALYST = {
    "motive_analysis": "测试动机分析",
    "emotional_trigger": "测试触发点",
    "underlying_insecurity": "测试不安全感",
    "communication_style": "攻击型",
    "leverage_points": ["杠杆1", "杠杆2"],
}

MOCK_LOGICIAN = {
    "fallacies": [{"name": "人身攻击", "quote": "测试", "explanation": "测试解释"}],
    "invalid_premises": [{"premise": "假前提", "why_invalid": "原因"}],
    "argument_structure": "零论证结构",
    "strongest_counterpoints": ["反击1", "反击2"],
}

MOCK_TACTICIAN = {
    "strategic_summary": "测试战略摘要",
    "attack_vectors": [{"fallacy_exploited": "人身攻击", "psychological_link": "link",
                         "recommended_move": "move", "expected_reaction": "reaction"}],
    "tone_guidance": {"surgeon": "温和", "tank": "冷静", "nuclear": "犀利"},
    "traps_to_avoid": ["陷阱1"],
}

MOCK_COPYWRITER = {
    "tier_1_surgeon": {"label": "外科手术", "description": "desc1", "response": "回复1"},
    "tier_2_tank": {"label": "坦克碾压", "description": "desc2", "response": "回复2"},
    "tier_3_nuclear": {"label": "核弹打击", "description": "desc3", "response": "回复3"},
}


def _make_mock_client(return_json: dict):
    """Create a mock AsyncOpenAI client that returns the given JSON."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps(return_json, ensure_ascii=False)

    mock_client.chat = MagicMock()
    mock_client.chat.completions = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    return mock_client


def test_analyst_agent():
    from debate_engine.agents import AnalystAgent
    client = _make_mock_client(MOCK_ANALYST)
    agent = AnalystAgent(client, "test-model")
    result = asyncio.run(agent.run("背景", "消息", history="历史"))
    assert result["motive_analysis"] == "测试动机分析"
    assert result["communication_style"] == "攻击型"
    # Verify history was included in the prompt
    call_args = client.chat.completions.create.call_args
    user_msg = call_args.kwargs["messages"][1]["content"]
    assert "历史" in user_msg
    print("[PASS] AnalystAgent (mocked)")


def test_logician_agent():
    from debate_engine.agents import LogicianAgent
    client = _make_mock_client(MOCK_LOGICIAN)
    agent = LogicianAgent(client, "test-model")
    result = asyncio.run(agent.run("背景", "消息"))
    assert len(result["fallacies"]) == 1
    assert result["fallacies"][0]["name"] == "人身攻击"
    print("[PASS] LogicianAgent (mocked)")


def test_tactician_agent():
    from debate_engine.agents import TacticianAgent
    client = _make_mock_client(MOCK_TACTICIAN)
    agent = TacticianAgent(client, "test-model")
    result = asyncio.run(agent.run("背景", "消息", "Burn", MOCK_ANALYST, MOCK_LOGICIAN, history="历史"))
    assert result["strategic_summary"] == "测试战略摘要"
    call_args = client.chat.completions.create.call_args
    user_msg = call_args.kwargs["messages"][1]["content"]
    assert "历史" in user_msg
    print("[PASS] TacticianAgent (mocked)")


def test_copywriter_agent():
    from debate_engine.agents import CopywriterAgent
    client = _make_mock_client(MOCK_COPYWRITER)
    agent = CopywriterAgent(client, "test-model")
    result = asyncio.run(agent.run("背景", "消息", "Burn", MOCK_TACTICIAN))
    assert result["tier_1_surgeon"]["label"] == "外科手术"
    assert result["tier_3_nuclear"]["response"] == "回复3"
    print("[PASS] CopywriterAgent (mocked)")


# ── 5. Full Pipeline Test (mocked) ──────────────────────────────────────────

def test_full_pipeline():
    from debate_engine.engine import DebateOrchestrator, State

    with patch("debate_engine.engine.AsyncOpenAI") as MockClient:
        mock_instance = MagicMock()
        MockClient.return_value = mock_instance

        orchestrator = DebateOrchestrator("http://fake", "fake-key", "fake-model")

        # Patch each agent's run method
        orchestrator.analyst.run = AsyncMock(return_value=MOCK_ANALYST)
        orchestrator.logician.run = AsyncMock(return_value=MOCK_LOGICIAN)
        orchestrator.tactician.run = AsyncMock(return_value=MOCK_TACTICIAN)
        orchestrator.copywriter.run = AsyncMock(return_value=MOCK_COPYWRITER)

        state = State("背景", "消息", "Burn", history="先前上下文")

        phases = []
        def on_phase(name):
            phases.append(name)

        result = asyncio.run(orchestrator.run(state, on_phase=on_phase))

        # Verify pipeline phases
        assert phases == ["parallel_analysis", "strategic_synthesis", "response_generation"]

        # Verify state populated
        assert result.analyst_report == MOCK_ANALYST
        assert result.logician_report == MOCK_LOGICIAN
        assert result.battle_plan == MOCK_TACTICIAN
        assert result.responses == MOCK_COPYWRITER

        # Verify analyst + logician ran in parallel (both called)
        orchestrator.analyst.run.assert_called_once()
        orchestrator.logician.run.assert_called_once()

        # Verify history was passed
        analyst_call = orchestrator.analyst.run.call_args
        assert analyst_call.kwargs.get("history") == "先前上下文"

        print("[PASS] Full pipeline (mocked, 3 phases, history threaded)")


# ── 6. CLI Argument Parsing Test ─────────────────────────────────────────────

def test_cli_args_one_shot():
    from debate_engine.cli import parse_args
    test_args = [
        "--api-key", "sk-test",
        "--base-url", "http://localhost:1234/v1",
        "--model", "llama3",
        "-c", "测试背景",
        "-m", "测试消息",
        "-g", "burn",
    ]
    with patch("sys.argv", ["debate-engine"] + test_args):
        args = parse_args()
        assert args.api_key == "sk-test"
        assert args.base_url == "http://localhost:1234/v1"
        assert args.model == "llama3"
        assert args.context == "测试背景"
        assert args.message == "测试消息"
        assert args.goal == "burn"
    print("[PASS] CLI one-shot argument parsing")


def test_cli_args_minimal():
    from debate_engine.cli import parse_args
    with patch("sys.argv", ["debate-engine"]):
        args = parse_args()
        assert args.api_key is None
        assert args.base_url is None
        assert args.context is None
    print("[PASS] CLI minimal argument parsing")


# ── 7. Markdown Fence Stripping ──────────────────────────────────────────────

def test_markdown_fence_stripping():
    from debate_engine.agents import AnalystAgent

    # Simulate LLM returning JSON wrapped in markdown fences
    fenced = "```json\n" + json.dumps(MOCK_ANALYST, ensure_ascii=False) + "\n```"
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = fenced
    mock_client.chat = MagicMock()
    mock_client.chat.completions = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    agent = AnalystAgent(mock_client, "test")
    result = asyncio.run(agent.run("bg", "msg"))
    assert result["motive_analysis"] == "测试动机分析"
    print("[PASS] Markdown fence stripping")


# ── Run All ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Debate Engine Test Suite (no API key needed)")
    print("=" * 60)
    print()

    tests = [
        test_package_import,
        test_agents_import,
        test_engine_import,
        test_cli_import,
        test_history_lifecycle,
        test_state,
        test_analyst_agent,
        test_logician_agent,
        test_tactician_agent,
        test_copywriter_agent,
        test_full_pipeline,
        test_cli_args_one_shot,
        test_cli_args_minimal,
        test_markdown_fence_stripping,
    ]

    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {t.__name__}: {e}")
            failed += 1

    print()
    print("=" * 60)
    total = passed + failed
    if failed == 0:
        print(f"ALL {total} TESTS PASSED")
    else:
        print(f"{passed}/{total} passed, {failed} FAILED")
    print("=" * 60)
