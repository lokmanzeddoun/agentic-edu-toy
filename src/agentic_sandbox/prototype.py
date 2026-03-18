from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agentic_sandbox.agents import (
    LevelAdapterAgent,
    NarratorAgent,
    ProfessorAgent,
    SafetyModeratorAgent,
)
from agentic_sandbox.config import get_settings
from agentic_sandbox.llm import OpenAILLMService
from agentic_sandbox.memory import DEFAULT_STORAGE_PATH, load_session, reset_session, save_session
from agentic_sandbox.models import AgentResponse, PrototypeStatus, SessionState
from agentic_sandbox.workflow import EducationalToyWorkflow


@dataclass(slots=True)
class EducationalToyPrototype:
    state: SessionState
    workflow: EducationalToyWorkflow
    llm_enabled: bool = False
    llm_model: str | None = None

    @classmethod
    def from_storage(cls, storage_path: Path = DEFAULT_STORAGE_PATH) -> "EducationalToyPrototype":
        state = load_session(storage_path)
        settings = get_settings()
        llm_service = None
        if settings.llm_enabled:
            llm_service = OpenAILLMService(
                api_key=settings.openai_api_key or "",
                model=settings.openai_model,
            )
        workflow = EducationalToyWorkflow(
            safety=SafetyModeratorAgent(),
            professor=ProfessorAgent(),
            level_adapter=LevelAdapterAgent(),
            narrator=NarratorAgent(),
            llm_service=llm_service,
        )
        return cls(
            state=state,
            workflow=workflow,
            llm_enabled=settings.llm_enabled,
            llm_model=settings.openai_model if settings.llm_enabled else None,
        )

    def status(self) -> PrototypeStatus:
        storage_path = self.state.storage_path or DEFAULT_STORAGE_PATH
        return PrototypeStatus(
            ready=True,
            learner_name=self.state.profile.learner_name,
            level=self.state.profile.level,
            storage_path=storage_path,
            llm_enabled=self.llm_enabled,
            llm_model=self.llm_model,
        )

    def bootstrap(self, learner_name: str | None = None, age: int | None = None) -> str:
        if learner_name:
            self.state.profile.learner_name = learner_name
        if age:
            self.state.profile.age = age
        message = self.workflow.bootstrap(self.state)
        save_session(self.state)
        return message

    def handle_turn(self, learner_input: str) -> AgentResponse:
        response = self.workflow.handle_turn(self.state, learner_input)
        save_session(self.state)
        return response

    def reset(self) -> SessionState:
        self.state = reset_session(self.state.storage_path or DEFAULT_STORAGE_PATH)
        return self.state
