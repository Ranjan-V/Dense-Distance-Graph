#!/usr/bin/env python3
"""Run the exact finite Active-Edge Kernel validation."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
CODE_ROOT=Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path: sys.path.insert(0,str(CODE_ROOT))
from verification.verify_aek import run
ROOT=Path(__file__).resolve().parents[2]
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,default=ROOT/'reproduction_runs/aek_exact.json'); a=ap.parse_args(); x=run(); a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8'); print(json.dumps(x,indent=2))
