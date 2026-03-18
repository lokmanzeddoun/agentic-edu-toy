from __future__ import annotations

from dataclasses import dataclass

from agentic_sandbox.curriculum import find_lesson, next_lesson
from agentic_sandbox.memory import append_event
from agentic_sandbox.models import (
    AgentResponse,
    EvaluationResult,
    LearnerProfile,
    SafetyDecision,
    SessionState,
)


BLOCKED_TERMS = {
    "kill",
    "hate",
    "sex",
    "weapon",
    "suicide",
    "bomb",
}


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


@dataclass(slots=True)
class SafetyModeratorAgent:
    def review_input(self, learner_input: str) -> SafetyDecision:
        normalized = _normalize(learner_input)
        if not normalized:
            return SafetyDecision(
                allowed=False,
                reason="Empty input is not useful for the lesson.",
                sanitized_input="",
            )

        if any(term in normalized for term in BLOCKED_TERMS):
            return SafetyDecision(
                allowed=False,
                reason="The input contains content that is outside the child-safe learning scope.",
                sanitized_input="",
            )

        return SafetyDecision(
            allowed=True,
            reason="Input accepted.",
            sanitized_input=normalized,
        )

    def review_output(self, text: str) -> str:
        sanitized = text
        for term in BLOCKED_TERMS:
            sanitized = sanitized.replace(term, "[filtered]")
        return sanitized


@dataclass(slots=True)
class ProfessorAgent:
    def ensure_current_question(self, profile: LearnerProfile) -> str:
        if profile.current_prompt and profile.expected_answer and profile.current_lesson_id:
            return profile.current_prompt

        lesson = next_lesson(profile.level, profile.total_turns)
        profile.current_lesson_id = lesson.lesson_id
        profile.current_prompt = lesson.prompt
        profile.expected_answer = lesson.answer
        return lesson.prompt

    def evaluate_answer(self, profile: LearnerProfile, learner_input: str) -> EvaluationResult:
        lesson = find_lesson(profile.current_lesson_id)
        if lesson is None or profile.expected_answer is None:
            lesson = next_lesson(profile.level, profile.total_turns)
            profile.current_lesson_id = lesson.lesson_id
            profile.current_prompt = lesson.prompt
            profile.expected_answer = lesson.answer

        normalized_answer = _normalize(profile.expected_answer or lesson.answer)
        normalized_input = _normalize(learner_input)
        is_correct = normalized_input == normalized_answer

        return EvaluationResult(
            is_correct=is_correct,
            expected_answer=lesson.answer,
            learner_answer=learner_input,
            hint=lesson.hint,
            lesson_id=lesson.lesson_id,
        )

    def prepare_next_question(self, profile: LearnerProfile) -> str:
        lesson = next_lesson(profile.level, profile.total_turns)
        profile.current_lesson_id = lesson.lesson_id
        profile.current_prompt = lesson.prompt
        profile.expected_answer = lesson.answer
        return lesson.prompt


@dataclass(slots=True)
class LevelAdapterAgent:
    def update_profile(self, profile: LearnerProfile, evaluation: EvaluationResult) -> str:
        profile.total_turns += 1
        if evaluation.is_correct:
            profile.correct_answers += 1
            profile.encouragement_streak += 1
            if profile.correct_answers and profile.correct_answers % 3 == 0:
                profile.level += 1
            profile.last_feedback = "correct"
            profile.detected_emotion = "confident"
            return "confident"

        profile.incorrect_answers += 1
        profile.encouragement_streak = 0
        profile.last_feedback = "needs_support"
        profile.detected_emotion = "frustrated"
        return "frustrated"


@dataclass(slots=True)
class NarratorAgent:
    def compose_response(
        self,
        profile: LearnerProfile,
        evaluation: EvaluationResult,
        next_prompt: str,
    ) -> str:
        learner_name = profile.learner_name
        if evaluation.is_correct:
            return (
                f"Great job, {learner_name}. Your answer '{evaluation.learner_answer}' is correct. "
                f"Let us continue. Next question: {next_prompt}"
            )

        return (
            f"Nice try, {learner_name}. The expected answer was '{evaluation.expected_answer}'. "
            f"Hint: {evaluation.hint} Next question: {next_prompt}"
        )


@dataclass(slots=True)
class MetaAgent:
    safety: SafetyModeratorAgent
    professor: ProfessorAgent
    level_adapter: LevelAdapterAgent
    narrator: NarratorAgent

    def bootstrap(self, state: SessionState) -> str:
        prompt = self.professor.ensure_current_question(state.profile)
        opening = (
            f"Hello {state.profile.learner_name}. I am ready to help you practice English. "
            f"First question: {prompt}"
        )
        append_event(state, "system", opening)
        return opening

    def handle_turn(self, state: SessionState, learner_input: str) -> AgentResponse:
        safety_decision = self.safety.review_input(learner_input)
        append_event(state, "learner", learner_input)

        if not safety_decision.allowed:
            blocked_message = (
                "I can only continue with safe learning content. "
                "Please answer the lesson question using simple child-friendly language."
            )
            safe_output = self.safety.review_output(blocked_message)
            append_event(state, "moderator", safe_output)
            return AgentResponse(response_text=safe_output, emotion="guarded")

        self.professor.ensure_current_question(state.profile)
        evaluation = self.professor.evaluate_answer(state.profile, safety_decision.sanitized_input)
        emotion = self.level_adapter.update_profile(state.profile, evaluation)
        next_prompt = self.professor.prepare_next_question(state.profile)
        narrative = self.narrator.compose_response(state.profile, evaluation, next_prompt)
        safe_output = self.safety.review_output(narrative)
        append_event(state, "system", safe_output)

        return AgentResponse(
            response_text=safe_output,
            evaluation=evaluation,
            next_prompt=next_prompt,
            emotion=emotion,
        )
