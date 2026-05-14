from __future__ import annotations

import hashlib
from statistics import mean
from typing import Any

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


def generate_candidates(iterations: int = 5) -> list[dict[str, Any]]:
    generated: list[dict[str, Any]] = []

    for family in DEFAULT_FAMILIES:
        for symbol in DEFAULT_SYMBOLS:
            for iteration in range(iterations):
                generated.append(
                    build_candidate(
                        family=family,
                        symbol=symbol,
                        iteration=iteration,
                    )
                )

    return generated
