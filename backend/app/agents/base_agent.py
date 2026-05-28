"""
backend/app/agents/base_agent.py — Abstract Base Agent
=======================================================
DESIGN PATTERN: Template Method Pattern

Every agent in this system shares:
1. A connection to the LLM (Claude via Anthropic SDK)
2. A standard logging interface that appends to state.agent_logs
3. Error handling with retry logic for transient API failures
4. Status tracking (PENDING → RUNNING → COMPLETED/FAILED)

The BaseAgent provides all of this. Concrete agents (ProfilingAgent,
CleaningAgent, etc.) inherit from BaseAgent and only implement `execute()`.

WHY ANTHROPIC SDK DIRECTLY (not LangChain wrappers)?
- Full control over streaming, tool_use blocks, and response metadata
- Access to the latest Claude features without waiting for LangChain updates
- Explicit error handling (RateLimitError, APIConnectionError, etc.)
- Cleaner code: no abstraction layers between us and the model
- Easier to tune: max_tokens, stop_sequences, temperature per agent

WHY ASYNC?
The entire system is async. FastAPI is async. LangGraph nodes are async.
Anthropic SDK has native async support. Using async means that while one
agent is waiting for the LLM to respond, the event loop can handle other
requests. This is critical for a concurrent multi-user system.
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

import anthropic

from app.config import settings
from app.orchestration.state import (
    AgentLog,
    AgentStatus,
    AnalystState,
    WorkflowStage,
    make_agent_log,
)
from app.utils.logger import get_logger


class BaseAgent(ABC):
    """
    Abstract base class for all analysis agents.

    Subclasses must implement:
        async def execute(self, state: AnalystState) -> dict

    The returned dict should contain ONLY the state fields that this agent
    updated. LangGraph merges it into the shared state.
    """

    def __init__(self, agent_name: str, agent_stage: WorkflowStage):
        """
        Args:
            agent_name: Short identifier used in logs ("profiling", "cleaning", etc.)
            agent_stage: The WorkflowStage this agent corresponds to
        """
        self.name = agent_name
        self.stage = agent_stage
        self.logger = get_logger(f"agent.{agent_name}")

        # Initialize the Anthropic async client
        # Using AsyncAnthropic for non-blocking LLM calls
        self._client = anthropic.AsyncAnthropic(
            api_key=settings.anthropic_api_key,
            # Timeout: 60s for complex analytical tasks (vs default 10s)
            timeout=anthropic.Timeout(60.0, read=60.0),
            # Built-in retry for 429 (rate limit) and 5xx errors
            max_retries=3,
        )

    # ── Abstract Method ───────────────────────────────────────────────────────

    @abstractmethod
    async def execute(self, state: AnalystState) -> dict:
        """
        Execute this agent's logic.

        Receives the full shared state. Returns a dict of ONLY the state
        fields this agent modified. Unmodified fields should NOT be included
        to avoid accidentally overwriting other agents' work.

        Example return value from ProfilingAgent:
            return {
                "current_stage": WorkflowStage.PROFILING,
                "agent_statuses": {...updated statuses...},
                "row_count": 5000,
                "column_profiles": [...],
                "data_quality_issues": [...],
                "data_quality_score": 72.5,
                "should_skip_cleaning": False,
                "agent_logs": [log1, log2, log3],  # Will be APPENDED to existing logs
            }
        """
        ...

    # ── LLM Interface ─────────────────────────────────────────────────────────

    async def ask_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.1,
    ) -> str:
        """
        Send a prompt to Claude and return the response text.

        Args:
            prompt: The user message content
            system_prompt: Optional system-level context (defaults to expert analyst)
            max_tokens: Override per-request token limit
            temperature: 0.0 = deterministic, 1.0 = creative. For analysis,
                         use low temperatures (0.0-0.2) for consistent outputs.

        Returns:
            Response text from Claude

        Raises:
            anthropic.RateLimitError: Too many requests (handled by retry logic in _client)
            anthropic.APIError: Other API errors
        """
        effective_system = system_prompt or self._default_system_prompt()
        effective_max_tokens = max_tokens or settings.claude_max_tokens

        self.logger.debug(
            "LLM request",
            model=settings.claude_model,
            prompt_preview=prompt[:100] + "..." if len(prompt) > 100 else prompt,
        )

        response = await self._client.messages.create(
            model=settings.claude_model,
            max_tokens=effective_max_tokens,
            temperature=temperature,
            system=effective_system,
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract text from the response
        # Claude returns content as a list of blocks (text, tool_use, etc.)
        text_blocks = [block.text for block in response.content if hasattr(block, "text")]
        result = "\n".join(text_blocks)

        self.logger.debug(
            "LLM response received",
            output_tokens=response.usage.output_tokens,
            stop_reason=response.stop_reason,
        )

        return result

    async def ask_llm_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_schema_hint: Optional[str] = None,
    ) -> str:
        """
        Ask LLM for a response that must be valid JSON.

        The prompt is augmented to instruct Claude to return ONLY JSON with
        no preamble, no markdown code fences, no commentary.
        """
        json_instruction = (
            "\n\nIMPORTANT: Respond with ONLY valid JSON. "
            "No preamble text, no markdown code fences (```), no explanation after. "
            "Your entire response must be parseable by json.loads()."
        )
        if json_schema_hint:
            json_instruction += f"\n\nExpected JSON structure:\n{json_schema_hint}"

        return await self.ask_llm(
            prompt=prompt + json_instruction,
            system_prompt=system_prompt,
            temperature=0.0,  # Zero temperature for consistent JSON structure
        )

    def _default_system_prompt(self) -> str:
        """
        Default system prompt for this agent.
        Subclasses can override for specialized expertise.
        """
        return (
            "You are an expert senior data scientist and business analyst with 15+ years "
            "of experience in data engineering, statistical analysis, and business intelligence. "
            "You analyze datasets with precision and provide clear, actionable insights. "
            "You are direct, specific, and always ground your analysis in the actual data. "
            "Never make up statistics or trends that aren't in the data."
        )

    # ── Logging Helpers ───────────────────────────────────────────────────────

    def log(self, message: str, level: str = "INFO") -> AgentLog:
        """
        Create a single AgentLog entry for this agent.
        Usage:
            logs = [self.log("Starting profiling"), self.log("Found 5 issues")]
            return {"agent_logs": logs}
        """
        return make_agent_log(self.name, self.stage, message, level)

    def log_info(self, message: str) -> AgentLog:
        return self.log(message, "INFO")

    def log_warning(self, message: str) -> AgentLog:
        return self.log(message, "WARNING")

    def log_error(self, message: str) -> AgentLog:
        return self.log(message, "ERROR")

    # ── Status Helpers ────────────────────────────────────────────────────────

    def _start_status(self, state: AnalystState) -> Dict[str, AgentStatus]:
        """Return updated agent_statuses with this agent set to RUNNING."""
        statuses = dict(state.get("agent_statuses", {}))
        statuses[self.name] = AgentStatus.RUNNING
        return statuses

    def _complete_status(self, state: AnalystState) -> Dict[str, AgentStatus]:
        """Return updated agent_statuses with this agent set to COMPLETED."""
        statuses = dict(state.get("agent_statuses", {}))
        statuses[self.name] = AgentStatus.COMPLETED
        return statuses

    def _fail_status(self, state: AnalystState) -> Dict[str, AgentStatus]:
        """Return updated agent_statuses with this agent set to FAILED."""
        statuses = dict(state.get("agent_statuses", {}))
        statuses[self.name] = AgentStatus.FAILED
        return statuses

    def _skip_status(self, state: AnalystState) -> Dict[str, AgentStatus]:
        """Return updated agent_statuses with this agent set to SKIPPED."""
        statuses = dict(state.get("agent_statuses", {}))
        statuses[self.name] = AgentStatus.SKIPPED
        return statuses