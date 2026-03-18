from __future__ import annotations

import json
from pathlib import Path

from agentic_sandbox.models import LearnerProfile, SessionEvent, SessionState


DEFAULT_STORAGE_DIR = Path(".agentic_sandbox")
DEFAULT_STORAGE_PATH = DEFAULT_STORAGE_DIR / "session.json"


def load_session(storage_path: Path = DEFAULT_STORAGE_PATH) -> SessionState:
    if not storage_path.exists():
        state = SessionState(storage_path=storage_path)
        state.storage_path = storage_path
        return state

    payload = json.loads(storage_path.read_text(encoding="utf-8"))
    state = SessionState.model_validate(payload)
    state.storage_path = storage_path
    return state


def save_session(state: SessionState, storage_path: Path | None = None) -> Path:
    target = storage_path or state.storage_path or DEFAULT_STORAGE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    serialized = state.model_dump(mode="json")
    serialized["storage_path"] = str(target)
    target.write_text(json.dumps(serialized, indent=2), encoding="utf-8")
    state.storage_path = target
    return target


def reset_session(storage_path: Path = DEFAULT_STORAGE_PATH) -> SessionState:
    state = SessionState(profile=LearnerProfile(), history=[], storage_path=storage_path)
    save_session(state, storage_path)
    return state


def append_event(state: SessionState, speaker: str, message: str) -> None:
    state.history.append(SessionEvent(speaker=speaker, message=message))
