"""Exact-integer graph constructions used only for finite theorem checks."""
from __future__ import annotations

from collections.abc import Iterable
import networkx as nx


def triangulated_grid(m: int = 4) -> tuple[nx.Graph, list[int]]:
    if m < 2:
        raise ValueError("m must be at least 2")
    g = nx.Graph()
    edges: list[tuple[int, int]] = []
    for i in range(m):
        for j in range(m):
            u = i * m + j
            g.add_node(u)
            if i + 1 < m:
                edges.append(tuple(sorted((u, (i + 1) * m + j))))
            if j + 1 < m:
                edges.append(tuple(sorted((u, i * m + j + 1))))
            if i + 1 < m and j + 1 < m:
                if (i + j) % 2 == 0:
                    edges.append(tuple(sorted((u, (i + 1) * m + j + 1))))
                else:
                    edges.append(tuple(sorted((i * m + j + 1, (i + 1) * m + j))))
    edges = sorted(set(edges))
    # Base weights vary deterministically; powers of two make every simple path weight distinct.
    scale = 1 << (len(edges) + 2)
    for idx, (u, v) in enumerate(edges):
        base = 1 + ((17 * idx + 5) % 11)
        g.add_edge(u, v, weight=base * scale + (1 << idx))
    b: list[int] = []
    for j in range(m):
        b.append(j)
    for i in range(1, m):
        b.append(i * m + m - 1)
    for j in range(m - 2, -1, -1):
        b.append((m - 1) * m + j)
    for i in range(m - 2, 0, -1):
        b.append(i * m)
    return g, b


def path_uses(path: list[int], edge: tuple[int, int]) -> bool:
    ek = frozenset(edge)
    return any(frozenset((path[i], path[i + 1])) == ek for i in range(len(path) - 1))


def changed_after_increase(
    graph: nx.Graph, edge: tuple[int, int], delta: int, s: int, t: int
) -> tuple[int, int]:
    d0 = nx.shortest_path_length(graph, s, t, weight="weight")
    h = graph.copy()
    h[edge[0]][edge[1]]["weight"] += delta
    d1 = nx.shortest_path_length(h, s, t, weight="weight")
    return d0, d1


def ensure_unique_shortest_paths(graph: nx.Graph, sources: Iterable[int] | None = None) -> None:
    """Brute-force uniqueness check on small positive-weight test graphs."""
    srcs = list(graph.nodes()) if sources is None else list(sources)
    for s in srcs:
        dist = nx.single_source_dijkstra_path_length(graph, s, weight="weight")
        # Dynamic program on strictly increasing distance order counts shortest paths.
        count = {v: 0 for v in graph.nodes()}
        count[s] = 1
        for u in sorted(dist, key=lambda x: dist[x]):
            for v, data in graph[u].items():
                w = data["weight"]
                if dist.get(v) == dist[u] + w:
                    count[v] += count[u]
        bad = [v for v in dist if count[v] != 1]
        if bad:
            raise AssertionError(f"nonunique shortest path from {s} to {bad[0]}")
