#!/usr/bin/env python3
"""Exact-integer equality checks for Theorem 7.1."""
from __future__ import annotations

import sys
from pathlib import Path
CODE_ROOT = Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import json
import random
import networkx as nx

from core.active_edge_kernel import ActiveEdgeKernel
from verification.exact_helpers import triangulated_grid


def run(seed: int = 777) -> dict[str, int | str]:
    rng = random.Random(seed)
    graph, boundary = triangulated_grid(5)
    edges = list(graph.edges())
    queries = 0
    failures = 0
    for q in (1, 2, 4):
        active = rng.sample(edges, q)
        kernel = ActiveEdgeKernel.preprocess(graph, boundary, active)
        base = {frozenset(e): graph[e[0]][e[1]]["weight"] for e in active}
        for _ in range(90):
            current = graph.copy()
            for e in active:
                key = frozenset(e)
                multiplier = rng.randint(1, 4)
                w = base[key] + multiplier * 1009
                kernel.update_weight(e, w)
                current[e[0]][e[1]]["weight"] = w
            s, t = rng.sample(boundary, 2)
            got = kernel.query(s, t)
            want = nx.shortest_path_length(current, s, t, weight="weight")
            queries += 1
            if got != want:
                failures += 1
    result = {
        "status": "PASS" if failures == 0 else "FAIL",
        "arithmetic": "exact integers",
        "queries": queries,
        "failures": failures,
    }
    if failures:
        raise AssertionError(result)
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
