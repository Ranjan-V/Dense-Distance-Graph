#!/usr/bin/env python3
"""Run the original 240-update support/DDG experiment suite from source."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
CODE_ROOT=Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path: sys.path.insert(0,str(CODE_ROOT))
from experiments.run_support_experiments import run
ROOT=Path(__file__).resolve().parents[2]
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--out-dir',type=Path,default=ROOT/'reproduction_runs/main_suite'); a=ap.parse_args(); run(a.out_dir)
