#!/usr/bin/env python3
"""Aggregate the deterministic support-scaling table from raw sequential-update data."""
from __future__ import annotations

import sys
from pathlib import Path
CODE_ROOT = Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import argparse
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def run(input_csv: Path, output_csv: Path) -> None:
    df = pd.read_csv(input_csv)
    agg = df.groupby(["family", "r", "k"], as_index=False).agg(
        changed_entries=("changed_entries", "median"),
        descriptors=("active_row_descriptors", "median"),
        compression_ratio=("compression_ratio", "median"),
        unique_shapes=("unique_row_interval_shapes", "median"),
    )
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    agg.to_csv(output_csv, index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    run(args.input, args.output)
