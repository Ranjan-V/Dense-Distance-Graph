"""Shortest-path utilities for floating and exact-integer validation."""
from __future__ import annotations

from collections.abc import Hashable, Sequence
import heapq
import math
import networkx as nx

Node = Hashable


def boundary_distances_and_paths(graph: nx.Graph, boundary: Sequence[Node]):
    """Return exact-for-input Dijkstra maps and chosen shortest paths for each boundary source."""
    dists = []
    paths = []
    for s in boundary:
        d, p = nx.single_source_dijkstra(graph, s, weight="weight")
        dists.append(d)
        paths.append(p)
    return dists, paths


def boundary_distance_matrix(graph: nx.Graph, boundary: Sequence[Node]) -> list[list[float]]:
    out: list[list[float]] = []
    for s in boundary:
        d = nx.single_source_dijkstra_path_length(graph, s, weight="weight")
        out.append([float(d[t]) if t in d else math.inf for t in boundary])
    return out


def exact_dijkstra(adj: Sequence[Sequence[tuple[int, int]]], source: int) -> tuple[list[int | None], list[int]]:
    """Dijkstra on nonnegative integer adjacency lists; None denotes unreachable."""
    n = len(adj)
    d: list[int | None] = [None] * n
    p = [-1] * n
    d[source] = 0
    pq: list[tuple[int, int]] = [(0, source)]
    while pq:
        du, u = heapq.heappop(pq)
        if d[u] != du:
            continue
        for v, w in adj[u]:
            if w < 0:
                raise ValueError("exact_dijkstra requires nonnegative weights")
            nd = du + w
            if d[v] is None or nd < d[v]:
                d[v] = nd
                p[v] = u
                heapq.heappush(pq, (nd, v))
    return d, p


def exact_dijkstra_with_path_counts(
    adj: Sequence[Sequence[tuple[int, int]]], source: int
) -> tuple[list[int | None], list[int]]:
    """Return exact distances and counts of shortest paths for positive/integer-weight test graphs."""
    n = len(adj)
    d: list[int | None] = [None] * n
    count = [0] * n
    d[source] = 0
    count[source] = 1
    pq: list[tuple[int, int]] = [(0, source)]
    while pq:
        du, u = heapq.heappop(pq)
        if d[u] != du:
            continue
        for v, w in adj[u]:
            nd = du + w
            if d[v] is None or nd < d[v]:
                d[v] = nd
                count[v] = count[u]
                heapq.heappush(pq, (nd, v))
            elif nd == d[v]:
                count[v] += count[u]
    return d, count
