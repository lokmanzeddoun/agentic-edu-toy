from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from typing_extensions import TypedDict

from langgraph.graph import END, StateGraph

from agentic_sandbox.agents import (
    LevelAdapterAgent,
    NarratorAgent,
    ProfessorAgent,
    SafetyModeratorAgent,
)
from agentic_sandbox.memory import append_event
from agentic_sandbox.models import AgentResponse, SessionState


class WorkflowState(TypedDict, total=False):
    state: SessionState
    learner_input: str
    safety_decision: Any
    evaluation: Any
    emotion: str
    next_prompt: str
    agent_response: AgentResponse


@dataclass(slots=True)
class EducationalToyWorkflow:
    safety: SafetyModeratorAgent
    professor: ProfessorAgent
    level_adapter: LevelAdapterAgent
    narrator: NarratorAgent
    llm_service: Any | None = None
    graph: Any = field(init=False, repr=False)

    def __post_init__(self) -> None:
        graph = StateGraph(WorkflowState)
        graph.add_node("safety", self._safety_node)
        graph.add_node("evaluate", self._evaluate_node)
        graph.add_node("adapt", self._adapt_node)
        graph.add_node("next_question", self._next_question_node)
        graph.add_node("respond", self._respond_node)
        graph.add_node("blocked", self._blocked_node)

        graph.set_entry_point("safety")
        graph.add_conditional_edges(
            "safety",
            self._route_after_safety,
            {
                "blocked": "blocked",
                "evaluate": "evaluate",
            },
        )
        graph.add_edge("evaluate", "adapt")
        graph.add_edge("adapt", "next_question")
        graph.add_edge("next_question", "respond")
        graph.add_edge("respond", END)
        graph.add_edge("blocked", END)
        self.graph = graph.compile()

    def bootstrap(self, state: SessionState) -> str:
        prompt = self.professor.ensure_current_question(state.profile)
        opening = (
            f"Hello {state.profile.learner_name}. I am ready to help you practice English. "
            f"First question: {prompt}"
        )
        append_event(state, "system", opening)
        return opening

    def handle_turn(self, state: SessionState, learner_input: str) -> AgentResponse:
        append_event(state, "learner", learner_input)
        result = self.graph.invoke(
            {
                "state": state,
                "learner_input": learner_input,
            }
        )
        return result["agent_response"]

    def _route_after_safety(self, state: dict[str, Any]) -> str:
        return "evaluate" if state["safety_decision"].allowed else "blocked"

    def _safety_node(self, graph_state: dict[str, Any]) -> dict[str, Any]:
        safety_decision = self.safety.review_input(graph_state["learner_input"])
        return {"safety_decision": safety_decision}

    def _evaluate_node(self, graph_state: dict[str, Any]) -> dict[str, Any]:
        state: SessionState = graph_state["state"]
        sanitized_input = graph_state["safety_decision"].sanitized_input
        self.professor.ensure_current_question(state.profile)
        evaluation = self.professor.evaluate_answer(state.profile, sanitized_input)
        return {"evaluation": evaluation}

    def _adapt_node(self, graph_state: dict[str, Any]) -> dict[str, Any]:
        state: SessionState = graph_state["state"]
        evaluation = graph_state["evaluation"]
        emotion = self.level_adapter.update_profile(state.profile, evaluation)
        return {"emotion": emotion}

    def _next_question_node(self, graph_state: dict[str, Any]) -> dict[str, Any]:
        state: SessionState = graph_state["state"]
        next_prompt = self.professor.prepare_next_question(state.profile)
        return {"next_prompt": next_prompt}

    def _respond_node(self, graph_state: dict[str, Any]) -> dict[str, Any]:
        state: SessionState = graph_state["state"]
        evaluation = graph_state["evaluation"]
        next_prompt = graph_state["next_prompt"]
        emotion = graph_state["emotion"]

        if self.llm_service is not None:
            response_text = self.llm_service.create_tutor_response(
                profile=state.profile,
                evaluation=evaluation,
                next_prompt=next_prompt,
                emotion=emotion,
            )
        else:
            response_text = self.narrator.compose_response(state.profile, evaluation, next_prompt)

        safe_output = self.safety.review_output(response_text)
        append_event(state, "system", safe_output)
        return {
            "agent_response": AgentResponse(
                response_text=safe_output,
                evaluation=evaluation,
                next_prompt=next_prompt,
                emotion=emotion,
            )
        }

    def _blocked_node(self, graph_state: dict[str, Any]) -> dict[str, Any]:
        state: SessionState = graph_state["state"]
        blocked_message = (
            "I can only continue with safe learning content. "
            "Please answer the lesson question using simple child-friendly language."
        )
        safe_output = self.safety.review_output(blocked_message)
        append_event(state, "moderator", safe_output)
        return {
            "agent_response": AgentResponse(
                response_text=safe_output,
                emotion="guarded",
            )
        }
