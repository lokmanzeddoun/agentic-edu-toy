from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, Field


class LessonItem(BaseModel):
    lesson_id: str
    prompt: str
    answer: str
    hint: str
    difficulty: int = 1
    theme: str = "english_vocabulary"


class LearnerProfile(BaseModel):
    learner_name: str = "Learner"
    age: int = 7
    level: int = 1
    total_turns: int = 0
    correct_answers: int = 0
    incorrect_answers: int = 0
    encouragement_streak: int = 0
    detected_emotion: str = "neutral"
    current_lesson_id: str | None = None
    current_prompt: str | None = None
    expected_answer: str | None = None
    last_feedback: str | None = None


class SessionEvent(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    speaker: str
    message: str


class SessionState(BaseModel):
    profile: LearnerProfile = Field(default_factory=LearnerProfile)
    history: list[SessionEvent] = Field(default_factory=list)
    storage_path: Path | None = None


class SafetyDecision(BaseModel):
    allowed: bool
    reason: str
    sanitized_input: str


class EvaluationResult(BaseModel):
    is_correct: bool
    expected_answer: str
    learner_answer: str
    hint: str
    lesson_id: str


class AgentResponse(BaseModel):
    response_text: str
    evaluation: EvaluationResult | None = None
    next_prompt: str | None = None
    emotion: str = "neutral"


class PrototypeStatus(BaseModel):
    ready: bool
    learner_name: str
    level: int
    storage_path: Path
    llm_enabled: bool = False
    llm_model: str | None = None
