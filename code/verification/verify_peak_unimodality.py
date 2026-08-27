#!/usr/bin/env python3
"""Finite exact checks for Theorem 8.2 and Corollary 8.3."""
from __future__ import annotations

import sys
from pathlib import Path
CODE_ROOT = Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import json
import math
import networkx as nx

from core.graph_utils import cyclic_intervals, cyclic_interval_values
from core.replacement_slack import peak_unimodal
from verification.exact_helpers import triangulated_grid, path_uses, ensure_unique_shortest_paths


def _three_regions(seq: list[int], delta: int) -> bool:
    labels = [x >= delta for x in seq]
    # True positions must form an ordinary interval in this already-linearized affected row.
    idx = [i for i, x in enumerate(labels) if x]
    return not idx or idx == list(range(idx[0], idx[-1] + 1))


def run() -> dict[str, int | str]:
    rows = 0
    unimodal_failures = 0
    region_failures = 0
    for m in (3, 4, 5):
        graph, boundary = triangulated_grid(m)
        ensure_unique_shortest_paths(graph, boundary)
        for edge in list(graph.edges())[:14]:
            deleted = graph.copy()
            deleted.remove_edge(*edge)
            for s in boundary:
                d0, paths = nx.single_source_dijkstra(graph, s, weight="weight")
                mask = [s != t and path_uses(paths[t], edge) for t in boundary]
                ints = cyclic_intervals(mask)
                if len(ints) != 1:
                    continue
                dd = nx.single_source_dijkstra_path_length(deleted, s, weight="weight")
                slack = []
                finite = True
                for t in boundary:
                    if t in dd:
                        slack.append(dd[t] - d0[t])
                    else:
                        slack.append(math.inf)
                seq = cyclic_interval_values(slack, mask)
                if not seq:
                    continue
                rows += 1
                if not peak_unimodal(seq):
                    unimodal_failures += 1
                finite_seq = [x for x in seq if math.isfinite(x)]
                if finite_seq:
                    levels = {min(finite_seq), max(finite_seq), (min(finite_seq) + max(finite_seq)) // 2}
                    for delta in levels:
                        if not _three_regions(finite_seq, int(delta)):
                            region_failures += 1
    result = {
        "status": "PASS" if not unimodal_failures and not region_failures else "FAIL",
        "arithmetic": "exact integers",
        "affected_rows_checked": rows,
        "unimodality_failures": unimodal_failures,
        "three_region_failures": region_failures,
    }
    if result["status"] != "PASS":
        raise AssertionError(result)
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
