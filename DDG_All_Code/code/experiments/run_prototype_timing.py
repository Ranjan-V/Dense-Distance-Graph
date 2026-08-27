#!/usr/bin/env python3
"""Regenerate the environment-dependent prototype timing data only.

This script reports implementation timings; it does not assert an algorithmic speedup.
"""
from __future__ import annotations
import argparse, shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LEGACY=ROOT/'code/legacy/experiments.py'
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,default=ROOT/'raw_data/regenerated/single_edge_benchmark.csv'); a=ap.parse_args()
    with tempfile.TemporaryDirectory(prefix='ddg_timing_') as td:
        outdir=Path(td); subprocess.run([sys.executable,str(LEGACY),'--out',str(outdir)],check=True,cwd=ROOT)
        src=outdir/'data/single_edge_benchmark.csv'; a.out.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,a.out)
    print(a.out)
