"""Graph and boundary-order helpers used by the reproducibility package."""
from __future__ import annotations

from typing import Hashable, Iterable, Sequence
import random
import networkx as nx

Node = Hashable


def boundary_cycle(m: int, n: int) -> list[tuple[int, int]]:
    """Return the outer-face boundary order of an m-by-n grid."""
    if m < 2 or n < 2:
        raise ValueError("grid dimensions must be at least 2")
    b: list[tuple[int, int]] = []
    for j in range(n):
        b.append((0, j))
    for i in range(1, m):
        b.append((i, n - 1))
    for j in range(n - 2, -1, -1):
        b.append((m - 1, j))
    for i in range(m - 2, 0, -1):
        b.append((i, 0))
    return b


def cyclic_intervals(mask: Sequence[bool]) -> list[tuple[int, int]]:
    """Maximal true cyclic intervals, represented by inclusive endpoint indices."""
    a = [bool(x) for x in mask]
    k = len(a)
    if k == 0 or not any(a):
        return []
    if all(a):
        return [(0, k - 1)]
    starts = [i for i in range(k) if a[i] and not a[(i - 1) % k]]
    out: list[tuple[int, int]] = []
    for st in starts:
        en = st
        while a[(en + 1) % k] and (en + 1) % k != st:
            en = (en + 1) % k
        out.append((st, en))
    return out


def cyclic_interval_values(values: Sequence[float | int], mask: Sequence[bool]) -> list[float | int]:
    """Values in boundary order on a unique nonempty cyclic interval."""
    ints = cyclic_intervals(mask)
    if len(ints) != 1:
        return []
    st, en = ints[0]
    k = len(mask)
    out: list[float | int] = []
    i = st
    while True:
        out.append(values[i])
        if i == en:
            break
        i = (i + 1) % k
    return out


def path_uses_edge(path: Sequence[Node], edge: tuple[Node, Node]) -> bool:
    ek = frozenset(edge)
    return any(frozenset((path[i], path[i + 1])) == ek for i in range(len(path) - 1))


def add_reproducible_unique_float_weights(
    graph: nx.Graph,
    seed: int,
    *,
    base: float = 1.0,
    spread: float = 1.0,
) -> None:
    """Historical floating-weight generator used only by randomized stress experiments."""
    rng = random.Random(seed)
    for idx, (u, v) in enumerate(graph.edges()):
        graph[u][v]["weight"] = base + spread * rng.random() + 1e-9 * (idx + 1)
