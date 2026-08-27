"""Exact fixed-active-edge kernel from Theorem 7.1."""
from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Hashable, Iterable
import heapq
import math
import networkx as nx

Node = Hashable
Edge = tuple[Node, Node]


@dataclass
class ActiveEdgeKernel:
    """Metric-closure kernel for a fixed set of active edges F.

    Preprocessing removes F, computes the static metric among query terminals B and
    active endpoints X, and stores the current active weights separately.  Changing
    an active weight is O(1); a terminal query runs dense Dijkstra on {s,t} union X.
    """

    terminals: tuple[Node, ...]
    active_edges: tuple[Edge, ...]
    endpoints: tuple[Node, ...]
    metric: dict[Node, dict[Node, float | int]]
    active_weights: dict[frozenset[Node], float | int]

    @classmethod
    def preprocess(cls, graph: nx.Graph, terminals: Iterable[Node], active_edges: Iterable[Edge]):
        b = tuple(terminals)
        f = tuple(active_edges)
        h = graph.copy()
        endpoints: list[Node] = []
        active_weights: dict[frozenset[Node], float | int] = {}
        for u, v in f:
            if not graph.has_edge(u, v):
                raise ValueError(f"active edge {(u, v)!r} is not in graph")
            w = graph[u][v]["weight"]
            if w < 0:
                raise ValueError("active weights must remain nonnegative")
            active_weights[frozenset((u, v))] = w
            h.remove_edge(u, v)
            if u not in endpoints:
                endpoints.append(u)
            if v not in endpoints:
                endpoints.append(v)
        terminal_set: list[Node] = []
        for x in [*b, *endpoints]:
            if x not in terminal_set:
                terminal_set.append(x)
        metric: dict[Node, dict[Node, float | int]] = {}
        for s in terminal_set:
            d = nx.single_source_dijkstra_path_length(h, s, weight="weight")
            metric[s] = {t: d[t] for t in terminal_set if t in d}
        return cls(b, f, tuple(endpoints), metric, active_weights)

    def update_weight(self, edge: Edge, weight: float | int) -> None:
        if weight < 0:
            raise ValueError("active weights must remain nonnegative")
        key = frozenset(edge)
        if key not in self.active_weights:
            raise KeyError("edge is not in the fixed active set")
        self.active_weights[key] = weight

    def query(self, s: Node, t: Node) -> float:
        if s not in self.terminals or t not in self.terminals:
            raise KeyError("queries are defined only for the preprocessed terminal set")
        nodes: list[Node] = []
        for x in [s, t, *self.endpoints]:
            if x not in nodes:
                nodes.append(x)
        idx = {x: i for i, x in enumerate(nodes)}
        dist = [math.inf] * len(nodes)
        dist[idx[s]] = 0
        pq: list[tuple[float | int, int]] = [(0, idx[s])]
        adjacency: list[list[tuple[int, float | int]]] = [[] for _ in nodes]
        for i, u in enumerate(nodes):
            for j in range(i + 1, len(nodes)):
                v = nodes[j]
                w = self.metric.get(u, {}).get(v, math.inf)
                if math.isfinite(w):
                    adjacency[i].append((j, w))
                    adjacency[j].append((i, w))
        for u, v in self.active_edges:
            if u in idx and v in idx:
                w = self.active_weights[frozenset((u, v))]
                adjacency[idx[u]].append((idx[v], w))
                adjacency[idx[v]].append((idx[u], w))
        while pq:
            du, i = heapq.heappop(pq)
            if du != dist[i]:
                continue
            if nodes[i] == t:
                return du
            for j, w in adjacency[i]:
                nd = du + w
                if nd < dist[j]:
                    dist[j] = nd
                    heapq.heappush(pq, (nd, j))
        return math.inf
