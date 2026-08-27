#!/usr/bin/env python3
"""Regenerate all four computational figures embedded in the manuscript."""
from __future__ import annotations

import sys
from pathlib import Path
CODE_ROOT = Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]


def _save(fig, outdir: Path, name: str) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(outdir / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(outdir / f"{name}.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def support_scaling(raw: Path, processed: Path, outdir: Path) -> None:
    df = pd.read_csv(raw / "sequential_updates.csv")
    agg = df.groupby(["family", "r", "k"], as_index=False).agg(
        changed_entries=("changed_entries", "median"),
        descriptors=("active_row_descriptors", "median"),
        compression_ratio=("compression_ratio", "median"),
        unique_shapes=("unique_row_interval_shapes", "median"),
    )
    processed.mkdir(parents=True, exist_ok=True)
    agg.to_csv(processed / "support_scaling_summary.csv", index=False)
    markers = ["o", "s", "^", "D", "x"]
    lines = ["-", "--", "-.", ":", "-"]
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    for z, (family, g) in enumerate(agg.groupby("family")):
        g = g.sort_values("r")
        ax.plot(g["r"], g["changed_entries"], marker=markers[z % len(markers)], linestyle=lines[z % len(lines)], label=f"{family}: changed entries")
        ax.plot(g["r"], g["descriptors"], marker=markers[(z + 2) % len(markers)], linestyle="--", label=f"{family}: row intervals")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("piece size r"); ax.set_ylabel("median count per update")
    ax.set_title("Value changes can be dense while support stays structured")
    ax.grid(True, which="both", alpha=0.25); ax.legend(fontsize=7, ncol=2)
    _save(fig, outdir, "support_scaling")


def runtime_benchmark(raw: Path, outdir: Path) -> None:
    df = pd.read_csv(raw / "single_edge_benchmark.csv")
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.plot(df["r"], df["full_ddg_recompute_ms"] * 1000, marker="o", linestyle="-", label="full DDG rematerialization")
    ax.plot(df["r"], df["oracle_update_plus_query_us"], marker="s", linestyle="--", label="single-active-edge oracle")
    ax.set_yscale("log")
    ax.set_xlabel("piece size r"); ax.set_ylabel("microseconds (Python prototype)")
    ax.set_title("Prototype cost: rematerialization vs implicit edge-weight oracle")
    ax.grid(True, which="both", alpha=0.25); ax.legend()
    _save(fig, outdir, "runtime_benchmark")


def slack_profile(raw: Path, outdir: Path) -> None:
    df = pd.read_csv(raw / "slack_profile_example.csv")
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.plot(df["position"], df["replacement_slack"], marker="o", linestyle="-")
    ax.set_xlabel("boundary position within affected cyclic interval")
    ax.set_ylabel("replacement slack rho_e(s,t)")
    ax.set_title("Replacement-slack profile from the pre-proof falsification suite")
    ax.grid(True, alpha=0.25)
    _save(fig, outdir, "slack_profile")


def support_matrix(raw: Path, outdir: Path) -> None:
    df = pd.read_csv(raw / "support_matrix_example.csv")
    k = 1 + max(int(df["source_index"].max()), int(df["target_index"].max()))
    mat = np.zeros((k, k), dtype=int)
    for row in df.itertuples(index=False):
        mat[int(row.source_index), int(row.target_index)] = int(row.changed)
    fig, ax = plt.subplots(figsize=(5.8, 4.8))
    ax.imshow(mat, cmap="Greys", interpolation="nearest", aspect="auto", vmin=0, vmax=1)
    ax.set_xlabel("boundary target index")
    ax.set_ylabel("boundary source index")
    ax.set_title("Illustrative changed-entry support matrix")
    _save(fig, outdir, "support_matrix_example")


def generate(raw: Path, processed: Path, outdir: Path) -> None:
    support_scaling(raw, processed, outdir)
    runtime_benchmark(raw, outdir)
    slack_profile(raw, outdir)
    support_matrix(raw, outdir)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, required=True)
    ap.add_argument("--processed", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    generate(args.raw, args.processed, args.out)
