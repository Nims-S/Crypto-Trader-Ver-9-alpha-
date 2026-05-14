from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

STATE_PATH = Path("state") / "ver9_runtime_state.json"


def _now() -> str:
    return datetime.now(UTC).isoformat()


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {
            "created_at": _now(),
            "updated_at": _now(),
            "cycles": [],
            "executions": [],
            "risk_events": [],
            "quarantined_strategies": [],
        }
    payload = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("runtime state must be a JSON object")
    payload.setdefault("created_at", _now())
    payload.setdefault("updated_at", _now())
    payload.setdefault("cycles", [])
    payload.setdefault("executions", [])
    payload.setdefault("risk_events", [])
    payload.setdefault("quarantined_strategies", [])
    return payload


def save_state(state: dict[str, Any]) -> Path:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    state = dict(state)
    state["updated_at"] = _now()
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True, default=str), encoding="utf-8")
    return STATE_PATH


def append_cycle(cycle: dict[str, Any]) -> dict[str, Any]:
    state = load_state()
    state["cycles"].append(cycle)
    save_state(state)
    return cycle


def append_execution(execution: dict[str, Any]) -> dict[str, Any]:
    state = load_state()
    state["executions"].append(execution)
    save_state(state)
    return execution


def append_risk_event(event: dict[str, Any]) -> dict[str, Any]:
    state = load_state()
    state["risk_events"].append(event)
    save_state(state)
    return event


def quarantine_strategy(strategy_id: str, reason: str) -> dict[str, Any]:
    state = load_state()
    quarantined = state.setdefault("quarantined_strategies", [])
    record = {
        "strategy_id": strategy_id,
        "reason": reason,
        "timestamp": _now(),
    }
    quarantined.append(record)
    save_state(state)
    return record


def summarize_state() -> dict[str, Any]:
    state = load_state()
    return {
        "path": str(STATE_PATH),
        "cycle_count": len(state.get("cycles") or []),
        "execution_count": len(state.get("executions") or []),
        "risk_event_count": len(state.get("risk_events") or []),
        "quarantined_count": len(state.get("quarantined_strategies") or []),
        "latest_cycle": (state.get("cycles") or [{}])[-1] if state.get("cycles") else {},
        "latest_execution": (state.get("executions") or [{}])[-1] if state.get("executions") else {},
    }
