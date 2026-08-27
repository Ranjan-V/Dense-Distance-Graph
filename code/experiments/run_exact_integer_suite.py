#!/usr/bin/env python3
"""Run the original exact-integer exhaustive/falsification suite from source."""
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/'code/legacy/exact_falsification.py'
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,default=ROOT/'reproduction_runs/exact_falsification.json'); a=ap.parse_args(); a.out.parent.mkdir(parents=True,exist_ok=True); subprocess.run([sys.executable,str(SCRIPT),'--out',str(a.out)],check=True,cwd=ROOT)
