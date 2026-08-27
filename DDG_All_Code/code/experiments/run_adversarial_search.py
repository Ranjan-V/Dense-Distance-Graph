#!/usr/bin/env python3
"""Run the exact exhaustive + mutation/annealing falsification campaign."""
from __future__ import annotations

import sys
from pathlib import Path
CODE_ROOT = Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "code" / "legacy" / "exact_falsification.py"


def run(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(SCRIPT), "--out", str(output)], check=True, cwd=ROOT)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "reproduction_runs" / "exact_falsification.json")
    args = ap.parse_args()
    run(args.out)
