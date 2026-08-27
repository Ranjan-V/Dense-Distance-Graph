from __future__ import annotations

import math
import networkx as nx
import pytest

from core.graph_utils import cyclic_intervals, path_uses_edge
from core.shortest_paths import exact_dijkstra
from core.replacement_slack import replacement_slack_matrix, peak_unimodal, three_region_classes
from core.active_edge_kernel import ActiveEdgeKernel
from verification.verify_interval_patch_lower_bound import build_instance


def test_exact_dijkstra_and_negative_failure():
    adj = [[(1, 2), (2, 10)], [(0, 2), (2, 3)], [(0, 10), (1, 3)]]
    dist, parent = exact_dijkstra(adj, 0)
    assert dist == [0, 2, 5]
    assert parent[2] == 1
    with pytest.raises(ValueError):
        exact_dijkstra([[(1, -1)], [(0, -1)]], 0)


def test_cyclic_intervals_wrap():
    assert cyclic_intervals([True, True, False, False, True]) == [(4, 1)]
    assert cyclic_intervals([False, True, True, False]) == [(1, 2)]
    assert cyclic_intervals([False, False]) == []


def test_support_equivalence_unique_small():
    g = nx.Graph()
    g.add_weighted_edges_from([(0, 1, 1), (1, 2, 2), (0, 2, 9), (2, 3, 1), (1, 3, 8)], weight="weight")
    edge = (1, 2)
    d0, paths = nx.single_source_dijkstra(g, 0, weight="weight")
    h = g.copy(); h[1][2]["weight"] += 20
    d1 = nx.single_source_dijkstra_path_length(h, 0, weight="weight")
    for t in g.nodes:
        assert (d1[t] > d0[t]) == path_uses_edge(paths[t], edge)


def test_replacement_slack_and_shape_predicates():
    g = nx.Graph()
    g.add_weighted_edges_from([(0, 1, 1), (1, 2, 2), (0, 2, 8), (2, 3, 1), (1, 3, 7)], weight="weight")
    rho = replacement_slack_matrix(g, [0, 2, 3], (1, 2))
    assert rho[0][1] == 5
    assert rho[0][2] == 4
    assert peak_unimodal([1, 3, 5, 5, 4, 2])
    assert not peak_unimodal([1, 3, 2, 4])
    assert three_region_classes([1, 3, 5, 5, 4, 2], 4) == ["outer", "outer", "middle", "middle", "middle", "outer"]
    with pytest.raises(ValueError):
        three_region_classes([1, 3, 2, 4], 3)


def test_aek_exact_small_and_failure_handling():
    g = nx.Graph()
    g.add_weighted_edges_from([(0, 1, 2), (1, 2, 3), (0, 2, 10), (2, 3, 1), (1, 3, 9)], weight="weight")
    kernel = ActiveEdgeKernel.preprocess(g, [0, 3], [(1, 2)])
    assert kernel.query(0, 3) == nx.shortest_path_length(g, 0, 3, weight="weight")
    kernel.update_weight((1, 2), 20)
    g[1][2]["weight"] = 20
    assert kernel.query(0, 3) == nx.shortest_path_length(g, 0, 3, weight="weight")
    with pytest.raises(KeyError):
        kernel.update_weight((0, 1), 4)
    with pytest.raises(ValueError):
        kernel.update_weight((1, 2), -1)
    with pytest.raises(KeyError):
        kernel.query(0, 2)


def test_lower_bound_construction_shape():
    g, boundary, edge, delta = build_instance(8)
    assert len(boundary) == 8
    assert g.number_of_nodes() == 64
    assert edge == (0, 1)
    assert delta > 0
    assert nx.check_planarity(g)[0]
