#!/usr/bin/env python3
"""Backward-compatible alias for verification.verify_all."""
from __future__ import annotations
import json, sys
from pathlib import Path
CODE_ROOT=Path(__file__).resolve().parents[1]
if str(CODE_ROOT) not in sys.path: sys.path.insert(0,str(CODE_ROOT))
from verification.verify_all import run
if __name__=='__main__': print(json.dumps(run(),indent=2))
