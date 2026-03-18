from __future__ import annotations

from agentic_sandbox.models import LessonItem


LESSONS: list[LessonItem] = [
    LessonItem(
        lesson_id="eng-001",
        prompt="What is the English word for 'chat'?",
        answer="cat",
        hint="It is a small pet that says meow.",
    ),
    LessonItem(
        lesson_id="eng-002",
        prompt="What is the English word for 'chien'?",
        answer="dog",
        hint="It is a friendly animal that barks.",
    ),
    LessonItem(
        lesson_id="eng-003",
        prompt="What is the English word for 'pomme'?",
        answer="apple",
        hint="It is a fruit that can be red or green.",
    ),
    LessonItem(
        lesson_id="eng-004",
        prompt="Complete the sentence with one word: 'The sun is ...'?",
        answer="bright",
        hint="It means full of light.",
        difficulty=2,
    ),
    LessonItem(
        lesson_id="eng-005",
        prompt="Complete the sentence with one word: 'I read a ...'?",
        answer="book",
        hint="You can open it and turn its pages.",
        difficulty=2,
    ),
]


def find_lesson(lesson_id: str | None) -> LessonItem | None:
    if lesson_id is None:
        return None
    for lesson in LESSONS:
        if lesson.lesson_id == lesson_id:
            return lesson
    return None


def next_lesson(level: int, completed_turns: int) -> LessonItem:
    eligible_lessons = [lesson for lesson in LESSONS if lesson.difficulty <= max(level, 1)]
    if not eligible_lessons:
        eligible_lessons = LESSONS
    index = completed_turns % len(eligible_lessons)
    return eligible_lessons[index]
