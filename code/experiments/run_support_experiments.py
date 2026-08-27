#!/usr/bin/env python3
"""Run the original 240-update support suite and create support-matrix raw data."""
from __future__ import annotations

import sys
from pathlib import Path
CODE_ROOT = Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import argparse
import csv
import subprocess
import sys
from pathlib import Path
import networkx as nx

from core.ddg import support_from_shortest_paths
from verification.exact_helpers import triangulated_grid

ROOT = Path(__file__).resolve().parents[2]
LEGACY = ROOT / "code" / "legacy" / "experiments.py"


def create_support_matrix_example(output_csv: Path, output_meta: Path) -> None:
    graph, boundary = triangulated_grid(5)
    paths = [nx.single_source_dijkstra(graph, s, weight="weight")[1] for s in boundary]
    candidates = []
    for edge in graph.edges():
        matrix = support_from_shortest_paths(paths, boundary, edge)
        score = sum(sum(row) for row in matrix)
        candidates.append((score, edge, matrix))
    _, edge, matrix = max(candidates, key=lambda x: x[0])
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["source_index", "target_index", "changed"])
        for i, row in enumerate(matrix):
            for j, val in enumerate(row):
                w.writerow([i, j, int(val)])
    import json
    output_meta.write_text(json.dumps({
        "graph": "exact-integer triangulated 5x5 grid",
        "boundary_size": len(boundary),
        "edge": repr(edge),
        "changed_entries": sum(sum(row) for row in matrix),
    }, indent=2) + "\n", encoding="utf-8")


def run(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(LEGACY), "--out", str(out_dir)], check=True, cwd=ROOT)
    create_support_matrix_example(out_dir / "data" / "support_matrix_example.csv", out_dir / "data" / "support_matrix_metadata.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=ROOT / "reproduction_runs" / "main_suite")
    args = ap.parse_args()
    run(args.out_dir)
