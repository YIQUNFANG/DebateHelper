"""DebateOrchestrator — async pipeline managing the four-agent workflow."""

import asyncio
from openai import AsyncOpenAI
from debate_engine.agents import AnalystAgent, LogicianAgent, TacticianAgent, CopywriterAgent


class State:
    """Shared state object passed through the pipeline."""

    def __init__(self, context: str, opponent_message: str, goal: str, history: str = ""):
        self.context = context
        self.opponent_message = opponent_message
        self.goal = goal
        self.history = history
        self.analyst_report: dict | None = None
        self.logician_report: dict | None = None
        self.battle_plan: dict | None = None
        self.responses: dict | None = None


class DebateOrchestrator:
    def __init__(self, base_url: str, api_key: str, model: str, output_lang: str = "zh"):
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.analyst = AnalystAgent(self.client, model, output_lang=output_lang)
        self.logician = LogicianAgent(self.client, model, output_lang=output_lang)
        self.tactician = TacticianAgent(self.client, model, output_lang=output_lang)
        self.copywriter = CopywriterAgent(self.client, model, output_lang=output_lang)

    async def run(self, state: State, on_phase=None) -> State:
        """Execute the full pipeline, calling on_phase(name) at each stage."""

        # Phase 1: Parallel analysis
        if on_phase:
            on_phase("parallel_analysis")
        analyst_task = self.analyst.run(
            state.context, state.opponent_message, history=state.history
        )
        logician_task = self.logician.run(
            state.context, state.opponent_message, history=state.history
        )
        state.analyst_report, state.logician_report = await asyncio.gather(
            analyst_task, logician_task
        )

        # Phase 2: Strategic synthesis
        if on_phase:
            on_phase("strategic_synthesis")
        state.battle_plan = await self.tactician.run(
            context=state.context,
            opponent_message=state.opponent_message,
            goal=state.goal,
            analyst_report=state.analyst_report,
            logician_report=state.logician_report,
            history=state.history,
        )

        # Phase 3: Response generation
        if on_phase:
            on_phase("response_generation")
        state.responses = await self.copywriter.run(
            context=state.context,
            opponent_message=state.opponent_message,
            goal=state.goal,
            battle_plan=state.battle_plan,
            history=state.history,
        )

        return state
