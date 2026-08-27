"""Dense-distance-graph and changed-support routines."""
from __future__ import annotations

from collections.abc import Hashable, Sequence
import networkx as nx

from .graph_utils import path_uses_edge, cyclic_intervals
from .shortest_paths import boundary_distances_and_paths, boundary_distance_matrix

Node = Hashable


def explicit_ddg(graph: nx.Graph, boundary: Sequence[Node]) -> list[list[float]]:
    """Materialize the boundary-to-boundary distance matrix."""
    return boundary_distance_matrix(graph, boundary)


def support_from_shortest_paths(
    paths: Sequence[dict[Node, list[Node]]],
    boundary: Sequence[Node],
    edge: tuple[Node, Node],
) -> list[list[bool]]:
    k = len(boundary)
    out = [[False] * k for _ in range(k)]
    for i in range(k):
        for j, t in enumerate(boundary):
            if i != j and path_uses_edge(paths[i][t], edge):
                out[i][j] = True
    return out


def extract_support_descriptors(
    graph: nx.Graph,
    boundary: Sequence[Node],
    edge: tuple[Node, Node],
) -> list[tuple[int, int] | None]:
    """Algorithmic support extraction given the current shortest-path trees/paths.

    This routine recomputes those paths for verification.  The theorem's O(k)-descriptor
    claim is a representation bound once the trees are available; it is not an update-time claim.
    """
    _, paths = boundary_distances_and_paths(graph, boundary)
    support = support_from_shortest_paths(paths, boundary, edge)
    desc: list[tuple[int, int] | None] = []
    for row in support:
        ints = cyclic_intervals(row)
        if len(ints) > 1:
            raise AssertionError("support theorem violated: more than one cyclic interval in a row")
        desc.append(ints[0] if ints else None)
    return desc
