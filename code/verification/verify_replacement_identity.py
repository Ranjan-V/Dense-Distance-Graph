#!/usr/bin/env python3
"""Finite exact checks for Proposition 6.1."""
from __future__ import annotations

import sys
from pathlib import Path
CODE_ROOT = Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import json
import networkx as nx

from verification.exact_helpers import triangulated_grid, path_uses, ensure_unique_shortest_paths


def run() -> dict[str, int | str]:
    checked = 0
    failures = 0
    for m in (3, 4):
        graph, boundary = triangulated_grid(m)
        ensure_unique_shortest_paths(graph, boundary)
        scale = 1 << (graph.number_of_edges() + 2)
        for edge in list(graph.edges())[:10]:
            deleted = graph.copy()
            deleted.remove_edge(*edge)
            updated = graph.copy()
            delta = 3 * scale
            updated[edge[0]][edge[1]]["weight"] += delta
            for s in boundary:
                d0, paths = nx.single_source_dijkstra(graph, s, weight="weight")
                dd = nx.single_source_dijkstra_path_length(deleted, s, weight="weight")
                d1 = nx.single_source_dijkstra_path_length(updated, s, weight="weight")
                for t in boundary:
                    if s == t or not path_uses(paths[t], edge):
                        continue
                    replacement = dd.get(t, float("inf"))
                    rhs = d0[t] + min(delta, replacement - d0[t])
                    checked += 1
                    if d1[t] != rhs:
                        failures += 1
    result = {
        "status": "PASS" if failures == 0 else "FAIL",
        "arithmetic": "exact integers",
        "affected_pairs_checked": checked,
        "failures": failures,
    }
    if failures:
        raise AssertionError(result)
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
