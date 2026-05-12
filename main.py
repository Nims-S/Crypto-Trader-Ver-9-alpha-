from __future__ import annotations

import argparse
import json
from pathlib import Path

from ver9.artifacts import ArtifactManager, build_artifact
from ver9.protections import ProtectionEngine
from ver9.universe import DEFAULT_UNIVERSE, PairUniverseManager


def dump(payload: dict, output_file: str | None = None) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True)
    if output_file:
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8")
    print(text)


def cmd_universe(args: argparse.Namespace) -> None:
    manager = PairUniverseManager()
    approved = manager.evaluate(DEFAULT_UNIVERSE)
    dump({"approved_universe": approved}, args.output_file)


def cmd_protections(args: argparse.Namespace) -> None:
    engine = ProtectionEngine()
    decision = engine.evaluate(
        portfolio_drawdown_pct=args.drawdown,
        rolling_loss_streak=args.loss_streak,
        volatility_regime_score=args.volatility,
    )
    dump(decision.__dict__, args.output_file)


def cmd_artifact(args: argparse.Namespace) -> None:
    manager = ArtifactManager()
    artifact = build_artifact(
        cycle_id=args.cycle_id,
        config={"mode": "alpha"},
        survivors=[{"strategy_id": "btc_mr_alpha"}],
        portfolio=[{"symbol": "BTC/USDT", "allocation": 0.4}],
        protections=[{"status": "approved"}],
    )
    path = manager.save(artifact)
    dump({"artifact_path": str(path)}, args.output_file)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="main.py")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("universe")
    p.add_argument("--output-file", default=None)
    p.set_defaults(func=cmd_universe)

    p = sub.add_parser("protections")
    p.add_argument("--drawdown", type=float, default=-4.0)
    p.add_argument("--loss-streak", type=int, default=1)
    p.add_argument("--volatility", type=float, default=0.5)
    p.add_argument("--output-file", default=None)
    p.set_defaults(func=cmd_protections)

    p = sub.add_parser("artifact")
    p.add_argument("--cycle-id", default="cycle_alpha")
    p.add_argument("--output-file", default=None)
    p.set_defaults(func=cmd_artifact)

    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
