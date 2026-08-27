#!/usr/bin/env python3
"""Exact checker for the explicit construction in Theorem 8.4."""
from __future__ import annotations

import sys
from pathlib import Path
CODE_ROOT = Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import json
import networkx as nx


def build_instance(k: int) -> tuple[nx.Graph, list[int], tuple[int, int], int]:
    if k < 3:
        raise ValueError("k must be at least 3")
    m = k - 2
    r = k * k
    a = 3 * m + 2
    g = nx.Graph()
    g.add_nodes_from(range(r))
    g.add_edge(0, 1, weight=1)  # e=(s,v)
    for x in range(1, m + 1):
        g.add_edge(x, x + 1, weight=1)
    g.add_edge(m + 1, 0, weight=a)
    prev = 1
    for x in range(k, r):
        g.add_edge(prev, x, weight=1)
        prev = x
    return g, list(range(k)), (0, 1), 4 * m + 2


def _unique_all_pairs(g: nx.Graph) -> bool:
    for s in g.nodes():
        dist = nx.single_source_dijkstra_path_length(g, s, weight="weight")
        cnt = {v: 0 for v in g.nodes()}
        cnt[s] = 1
        for u in sorted(dist, key=lambda x: dist[x]):
            for v, data in g[u].items():
                if dist.get(v) == dist[u] + data["weight"]:
                    cnt[v] += cnt[u]
        if any(cnt[v] != 1 for v in dist):
            return False
    return True


def run(k_min: int = 3, k_max: int = 32) -> dict:
    checks = []
    for k in range(k_min, k_max + 1):
        m = k - 2
        g, boundary, edge, delta = build_instance(k)
        assert g.number_of_nodes() == k * k
        assert nx.check_planarity(g)[0]
        assert _unique_all_pairs(g)
        d0 = nx.single_source_dijkstra_path_length(g, 0, weight="weight")
        deleted = g.copy(); deleted.remove_edge(*edge)
        dd = nx.single_source_dijkstra_path_length(deleted, 0, weight="weight")
        slack = [dd[t] - d0[t] for t in boundary[1:]]
        expected = [4 * m + 1] + [4 * m + 1 - 2 * i for i in range(1, m + 1)]
        assert slack == expected
        assert len(set(slack)) == k - 1
        updated = g.copy(); updated[0][1]["weight"] += delta
        d1 = nx.single_source_dijkstra_path_length(updated, 0, weight="weight")
        corr = [d1[t] - d0[t] for t in boundary[1:]]
        assert corr == slack
        checks.append({
            "k": k,
            "r": k * k,
            "affected_targets": k - 1,
            "distinct_corrections": len(set(corr)),
            "first_correction": corr[0],
            "last_correction": corr[-1],
        })
    return {
        "status": "PASS",
        "arithmetic": "exact integers",
        "checked_k_range": [k_min, k_max],
        "instances": len(checks),
        "checks": checks,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
