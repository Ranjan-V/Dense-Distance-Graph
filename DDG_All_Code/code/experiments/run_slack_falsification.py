#!/usr/bin/env python3
"""Run the two original randomized replacement-slack stress suites.

The 60-graph suite runs its original legacy script unchanged.  The 400-graph suite runs
the exact same independent seed/configuration ranges in deterministic process chunks and
then sums them; this produces the same JSON as the original monolithic script while making
the release driver more robust on constrained runners.
"""
from __future__ import annotations
import argparse, json, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEGACY = ROOT / "code" / "legacy"
CHUNK = ROOT / "code" / "experiments" / "run_extended_stress_chunk.py"


def run(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(LEGACY / "conjecture_stress.py"), "--out", str(out_dir / "conjecture_stress.json")], check=True, cwd=ROOT)
    with tempfile.TemporaryDirectory(prefix="ddg_extended_chunks_") as td:
        tdir = Path(td)
        partials: list[Path] = []
        commands: list[list[str]] = []
        for start in range(0, 300, 50):
            p = tdir / f"outer_{start:03d}_{start+50:03d}.json"; partials.append(p)
            commands.append([sys.executable, str(CHUNK), "outerplanar", str(start), str(start + 50), "--out", str(p)])
        for start in range(0, 100, 25):
            p = tdir / f"random_{start:03d}_{start+25:03d}.json"; partials.append(p)
            commands.append([sys.executable, str(CHUNK), "random_planar", str(start), str(start + 25), "--out", str(p)])
        def _run(cmd: list[str]) -> None:
            subprocess.run(cmd, check=True, cwd=ROOT, stdout=subprocess.DEVNULL)
        with ThreadPoolExecutor(max_workers=min(6, len(commands))) as pool:
            futures = [pool.submit(_run, cmd) for cmd in commands]
            for fut in as_completed(futures):
                fut.result()
        total = {"graphs": 0, "rows_tested": 0, "counterexample": None}
        for p in partials:
            x = json.loads(p.read_text(encoding="utf-8"))
            total["graphs"] += x["graphs"]
            total["rows_tested"] += x["rows_tested"]
            if total["counterexample"] is None and x["counterexample"] is not None:
                total["counterexample"] = x["counterexample"]
        (out_dir / "extended_stress.json").write_text(json.dumps(total, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(total, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=ROOT / "reproduction_runs" / "stress")
    a = ap.parse_args(); run(a.out_dir)
