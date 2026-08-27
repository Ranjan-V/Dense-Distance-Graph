#!/usr/bin/env python3
"""Internal deterministic chunk runner for the original 400-graph extended stress suite.

The chunks are independent seed ranges from the unchanged legacy configuration.  Splitting
across fresh processes avoids long-lived interpreter overhead while preserving every graph,
seed, weight rule, candidate-edge limit, and exact aggregation performed by the original script.
"""
from __future__ import annotations
import argparse, importlib.util, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEGACY = ROOT / "code" / "legacy" / "extended_stress.py"
spec = importlib.util.spec_from_file_location("extended_stress_legacy", LEGACY)
legacy = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(legacy)


def run(kind: str, start: int, end: int, output: Path) -> dict:
    total = {"graphs": 0, "rows_tested": 0, "counterexample": None}
    if kind == "outerplanar":
        for seed in range(start, end):
            k = [12, 16, 20, 24, 32][seed % 5]
            g, boundary = legacy.outerplanar(k, 5000 + seed)
            rows, ce = legacy.check(g, boundary, max_edges=20)
            total["graphs"] += 1; total["rows_tested"] += rows
            if ce:
                ce.update(family="outerplanar", seed=seed, k=k)
                total["counterexample"] = ce
                break
    elif kind == "random_planar":
        for seed in range(start, end):
            m = [6, 7, 8, 9][seed % 4]
            g, boundary = legacy.ex.make_random_planar(m, 6000 + seed)
            rows, ce = legacy.check(g, boundary, max_edges=12)
            total["graphs"] += 1; total["rows_tested"] += rows
            if ce:
                ce.update(family="random_planar", seed=seed, m=m)
                total["counterexample"] = ce
                break
    else:
        raise ValueError(f"unknown chunk family: {kind}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(total, indent=2) + "\n", encoding="utf-8")
    return total


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["outerplanar", "random_planar"])
    ap.add_argument("start", type=int)
    ap.add_argument("end", type=int)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    print(json.dumps(run(a.kind, a.start, a.end, a.out), indent=2))
