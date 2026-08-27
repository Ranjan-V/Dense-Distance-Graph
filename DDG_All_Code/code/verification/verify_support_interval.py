#!/usr/bin/env python3
"""Finite exact checks for Proposition 5.1 and Theorem 5.3."""
from __future__ import annotations

import sys
from pathlib import Path
CODE_ROOT = Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import json
import networkx as nx

from core.graph_utils import cyclic_intervals
from verification.exact_helpers import triangulated_grid, path_uses, ensure_unique_shortest_paths


def run() -> dict[str, int | str]:
    cases = 0
    rows = 0
    support_failures = 0
    interval_failures = 0
    for m in (3, 4, 5):
        graph, boundary = triangulated_grid(m)
        ensure_unique_shortest_paths(graph, boundary)
        # Use the first 12 edges (or all if fewer); exact integer arithmetic throughout.
        edges = list(graph.edges())[:12]
        scale = 1 << (graph.number_of_edges() + 2)
        for edge in edges:
            before_dist = {}
            before_paths = {}
            for s in boundary:
                d, p = nx.single_source_dijkstra(graph, s, weight="weight")
                before_dist[s] = d
                before_paths[s] = p
            updated = graph.copy()
            updated[edge[0]][edge[1]]["weight"] += scale
            after_dist = {
                s: nx.single_source_dijkstra_path_length(updated, s, weight="weight")
                for s in boundary
            }
            for s in boundary:
                mask = []
                for t in boundary:
                    predicted = s != t and path_uses(before_paths[s][t], edge)
                    actual = after_dist[s][t] > before_dist[s][t]
                    if predicted != actual:
                        support_failures += 1
                    mask.append(actual)
                    cases += 1
                if sum(mask):
                    rows += 1
                    if len(cyclic_intervals(mask)) != 1:
                        interval_failures += 1
    result = {
        "status": "PASS" if not support_failures and not interval_failures else "FAIL",
        "arithmetic": "exact integers",
        "pair_checks": cases,
        "affected_rows_checked": rows,
        "support_failures": support_failures,
        "interval_failures": interval_failures,
    }
    if result["status"] != "PASS":
        raise AssertionError(result)
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
