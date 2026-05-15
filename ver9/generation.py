from __future__ import annotations

import hashlib
from collections import Counter
from statistics import mean
from typing import Any

from .diversity import (
    DEFAULT_FAMILY_QUOTAS,
    DEFAULT_SYMBOL_QUOTAS,
    build_generation_quota_plan,
)
from .mutation_spaces import get_mutation_space


DEFAULT_FAMILIES = [
    "mean_reversion",
    "volatility_compression",
    "trend",
]

DEFAULT_SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
]


def _stable_float(seed: str, minimum: float, maximum: float) -> float:
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    integer = int(digest[:8], 16)
    ratio = integer / 0xFFFFFFFF
    return minimum + ((maximum - minimum) * ratio)


def build_candidate(*, family: str, symbol: str, iteration: int) -> dict[str, Any]:
    params = get_mutation_space(family)

    parameter_strength = mean(
        float(mean(values)) if values else 0.0
        for values in params.values()
    ) if params else 0.0

    base_seed = f"{family}:{symbol}:{iteration}"

    profit_factor = round(_stable_float(base_seed + ':pf', 1.1, 3.4), 2)
    return_pct = round(_stable_float(base_seed + ':ret', 2.0, 28.0), 2)
    max_drawdown_pct = round(-_stable_float(base_seed + ':dd', 1.5, 14.0), 2)
    robustness_score = round(_stable_float(base_seed + ':rob', 0.45, 0.96), 3)

    return {
        "strategy_id": f"{family}_{symbol.replace('/', '_').lower()}_{iteration}",
        "family": family,
        "symbol": symbol,
        "timeframe": "1h",
        "regime": "adaptive",
        "profit_factor": profit_factor,
        "return_pct": return_pct,
        "max_drawdown_pct": max_drawdown_pct,
        "trades": int(_stable_float(base_seed + ':trades', 40, 320)),
        "robustness_score": robustness_score,
        "parameter_strength": round(parameter_strength, 3),
        "status": "candidate",
    }


def build_generation_plan(
    iterations: int,
    *,
    family_quota: dict[str, int] | None = None,
    symbol_quota: dict[str, int] | None = None,
) -> list[dict[str, Any]]:
    return build_generation_quota_plan(
        iterations,
        DEFAULT_FAMILIES,
        DEFAULT_SYMBOLS,
        family_quota=family_quota or DEFAULT_FAMILY_QUOTAS,
        symbol_quota=symbol_quota or DEFAULT_SYMBOL_QUOTAS,
    )


def generation_quota_report(
    iterations: int,
    *,
    family_quota: dict[str, int] | None = None,
    symbol_quota: dict[str, int] | None = None,
) -> dict[str, Any]:
    plan = build_generation_plan(
        iterations,
        family_quota=family_quota,
        symbol_quota=symbol_quota,
    )
    family_counts = Counter(item["family"] for item in plan)
    symbol_counts = Counter(item["symbol"] for item in plan)
    return {
        "iterations": max(1, int(iterations)),
        "total_planned": sum(int(item["count"]) for item in plan),
        "family_counts": dict(family_counts),
        "symbol_counts": dict(symbol_counts),
        "plan": plan,
    }


def generate_candidates(
    iterations: int = 5,
    *,
    family_quota: dict[str, int] | None = None,
    symbol_quota: dict[str, int] | None = None,
) -> list[dict[str, Any]]:
    generated: list[dict[str, Any]] = []
    plan = build_generation_plan(
        iterations,
        family_quota=family_quota,
        symbol_quota=symbol_quota,
    )

    for item in plan:
        family = str(item["family"])
        symbol = str(item["symbol"])
        count = max(0, int(item["count"]))
        for iteration in range(count):
            generated.append(
                build_candidate(
                    family=family,
                    symbol=symbol,
                    iteration=iteration,
                )
            )

    return generated