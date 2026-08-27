#!/usr/bin/env python3
"""Exact finite checks focused on Corollary 8.3 (three-region correction)."""
from __future__ import annotations
import json, sys
from pathlib import Path
CODE_ROOT=Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path: sys.path.insert(0,str(CODE_ROOT))
from verification.verify_peak_unimodality import run as _combined_run

def run() -> dict:
    x=_combined_run()
    out={"status":"PASS" if x["three_region_failures"]==0 else "FAIL",
         "arithmetic":x["arithmetic"],"affected_rows_checked":x["affected_rows_checked"],
         "three_region_failures":x["three_region_failures"]}
    if out["status"]!="PASS": raise AssertionError(out)
    return out

if __name__=='__main__': print(json.dumps(run(),indent=2))
