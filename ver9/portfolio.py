from __future__ import annotations

from typing import Any


FAMILY_PENALTIES = {
    "trend": 0.85,
    "mean_reversion": 1.0,
    "volatility_compression": 0.95,
}


def candidate_score(candidate: dict[str, Any]) -> float:
    pf = float(candidate.get("profit_factor") or 0.0)
    ret = float(candidate.get("return_pct") or 0.0)
    dd = abs(float(candidate.get("max_drawdown_pct") or 0.0))
    robustness = float(candidate.get("robustness_score") or 0.0)

    family = str(candidate.get("family") or "")
    penalty = FAMILY_PENALTIES.get(family, 0.9)

    score = ((pf * 2.0) + (ret / 10.0) + (robustness * 5.0)) / max(dd, 1.0)
    return round(score * penalty, 4)


def allocate(candidates: list[dict[str, Any]], *, max_positions: int = 3) -> list[dict[str, Any]]:
    ranked = sorted(candidates, key=candidate_score, reverse=True)

    allocations: list[dict[str, Any]] = []
    used_symbols: set[str] = set()

    for candidate in ranked:
        symbol = str(candidate.get("symbol"))
        if symbol in used_symbols:
            continue

        allocations.append(
            {
                "strategy_id": candidate.get("strategy_id"),
                "symbol": symbol,
                "family": candidate.get("family"),
                "allocation_pct": round(1 / max_positions, 3),
                "score": candidate_score(candidate),
                "status": candidate.get("status"),
            }
        )

        used_symbols.add(symbol)

        if len(allocations) >= max_positions:
            break

    return allocations
