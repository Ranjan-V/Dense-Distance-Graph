"""Replacement-slack computations and shape predicates."""
from __future__ import annotations

from collections.abc import Hashable, Sequence
import math
import networkx as nx

from .shortest_paths import boundary_distance_matrix
from .graph_utils import cyclic_interval_values

Node = Hashable


def replacement_slack_matrix(
    graph: nx.Graph,
    boundary: Sequence[Node],
    edge: tuple[Node, Node],
) -> list[list[float]]:
    """Compute rho_e^P(s,t)=d_{P-e}(s,t)-d_P(s,t), with +inf on disconnection."""
    before = boundary_distance_matrix(graph, boundary)
    deleted = graph.copy()
    deleted.remove_edge(*edge)
    after_delete = boundary_distance_matrix(deleted, boundary)
    out: list[list[float]] = []
    for a, b in zip(after_delete, before):
        out.append([math.inf if math.isinf(x) else x - y for x, y in zip(a, b)])
    return out


def peak_unimodal(values: Sequence[float | int]) -> bool:
    """Nondecreasing followed by nonincreasing, ignoring equal differences."""
    seen_down = False
    for a, b in zip(values, values[1:]):
        if b < a:
            seen_down = True
        elif b > a and seen_down:
            return False
    return True


def three_region_classes(values: Sequence[float | int], delta: float | int) -> list[str]:
    """Classify a peak-unimodal row as below/at-or-above threshold."""
    if not peak_unimodal(values):
        raise ValueError("three-region conclusion requires a peak-unimodal profile")
    return ["middle" if x >= delta else "outer" for x in values]


def interval_slack_values(
    slack_row: Sequence[float | int], affected_mask: Sequence[bool]
) -> list[float | int]:
    return cyclic_interval_values(slack_row, affected_mask)
