from __future__ import annotations

from typing import Any

from .execution import execute_allocations
from .portfolio import allocate
from .registry import list_candidates
from .risk import RiskMonitor
from .state import append_cycle, append_execution, append_risk_event, quarantine_strategy, summarize_state


class DaemonError(RuntimeError):
    pass


class Version9Daemon:
    def __init__(self, *, capital: float = 10000.0, max_positions: int = 3, live: bool = False) -> None:
        self.capital = capital
        self.max_positions = max_positions
        self.live = live
        self.risk_monitor = RiskMonitor()

    def build_cycle(self) -> dict[str, Any]:
        candidates = list_candidates(status="deployable")
        if not candidates:
            candidates = list_candidates(status="probationary")
        if not candidates:
            candidates = list_candidates(status="validated")

        portfolio = allocate(candidates, max_positions=self.max_positions)
        execution = execute_allocations(portfolio, capital=self.capital, live=self.live)
        risk_state = self.risk_monitor.evaluate_portfolio(
            portfolio_drawdown_pct=-2.5 if execution.filled_orders else -6.0,
            rolling_loss_streak=0 if execution.filled_orders else 1,
            volatility_regime_score=0.55 if execution.filled_orders else 0.78,
        )

        cycle = {
            "portfolio": portfolio,
            "execution": execution.as_dict(),
            "risk": risk_state.as_dict(),
            "state_summary": summarize_state(),
        }
        append_cycle(cycle)
        append_execution(execution.as_dict())
        append_risk_event(risk_state.as_dict())

        if not risk_state.approved:
            for allocation in portfolio:
                strategy_id = str(allocation.get("strategy_id") or "")
                if strategy_id:
                    quarantine_strategy(strategy_id, risk_state.reason)

        return cycle

    def run_once(self) -> dict[str, Any]:
        return self.build_cycle()


def run_daemon_once(*, capital: float = 10000.0, max_positions: int = 3, live: bool = False) -> dict[str, Any]:
    daemon = Version9Daemon(capital=capital, max_positions=max_positions, live=live)
    return daemon.run_once()
