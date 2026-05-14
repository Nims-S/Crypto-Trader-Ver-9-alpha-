from __future__ import annotations

from typing import Any

VALID_TRANSITIONS = {
    "candidate": {"validated", "quarantined"},
    "validated": {"probationary", "quarantined"},
    "probationary": {"deployable", "quarantined"},
    "deployable": {"live", "quarantined"},
    "live": {"quarantined"},
    "quarantined": {"validated"},
}


def normalize_status(status: str) -> str:
    return status.strip().lower()


class LifecycleError(RuntimeError):
    pass


def transition(record: dict[str, Any], target_status: str) -> dict[str, Any]:
    current = normalize_status(str(record.get("status") or "candidate"))
    target = normalize_status(target_status)

    allowed = VALID_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise LifecycleError(f"invalid transition: {current} -> {target}")

    updated = dict(record)
    updated["status"] = target
    return updated


def auto_promote(record: dict[str, Any]) -> dict[str, Any]:
    updated = dict(record)

    robustness = float(updated.get("robustness_score") or 0.0)
    profit_factor = float(updated.get("profit_factor") or 0.0)
    drawdown = float(updated.get("max_drawdown_pct") or 0.0)

    if robustness >= 0.75 and profit_factor >= 1.8 and drawdown >= -10:
        updated["status"] = "validated"

    if robustness >= 0.82 and profit_factor >= 2.0 and drawdown >= -8:
        updated["status"] = "probationary"

    if robustness >= 0.88 and profit_factor >= 2.2 and drawdown >= -6:
        updated["status"] = "deployable"

    return updated
