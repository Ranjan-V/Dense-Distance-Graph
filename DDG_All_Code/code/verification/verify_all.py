#!/usr/bin/env python3
"""Run every named finite theorem/algorithm verifier requested by the release package."""
from __future__ import annotations
import json, sys
from pathlib import Path
CODE_ROOT=Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path: sys.path.insert(0,str(CODE_ROOT))
from verification.verify_support_equivalence import run as support
from verification.verify_interval_theorem import run as interval
from verification.verify_replacement_identity import run as identity
from verification.verify_peak_unimodality import run as unimodal
from verification.verify_three_region_structure import run as regions
from verification.verify_interval_patch_lower_bound import run as lower
from verification.verify_aek import run as aek

def run(output: Path|None=None) -> dict:
    result={
        "support_equivalence":support(),
        "interval_theorem":interval(),
        "replacement_identity":identity(),
        "peak_unimodality":unimodal(),
        "three_region_structure":regions(),
        "interval_patch_lower_bound":lower(),
        "active_edge_kernel":aek(),
    }
    result["status"]="PASS" if all(v.get("status")=="PASS" for v in result.values() if isinstance(v,dict)) else "FAIL"
    if output is not None:
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    if result["status"]!="PASS": raise AssertionError(result)
    return result

if __name__=='__main__': print(json.dumps(run(),indent=2))
