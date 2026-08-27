# Code package

This directory has two layers.

1. `core/`, `verification/`, `experiments/`, and `figures/` are the modular reusable implementation and validation layer.
2. `legacy/` preserves the original experiment programs that produced the manuscript's historical 240-update, stress-suite, exact-falsification, and lower-bound outputs. Only output-path plumbing was changed to remove machine-specific paths; seeds, graph families, algorithms, and experiment configurations are unchanged.

## Quick checks

From the package root:

```bash
PYTHONPATH=code python code/verification/verify_all_theorems.py
pytest -q
```

## Historical/full experiments

```bash
python code/experiments/run_support_experiments.py --out-dir reproduction_runs/main_suite
python code/experiments/run_slack_falsification.py --out-dir reproduction_runs/stress
python code/experiments/run_adversarial_search.py --out reproduction_runs/exact_falsification.json
python code/legacy/constant_patch_lower_bound_check.py --out reproduction_runs/constant_patch_lower_bound_check.json
```

The single command `python reproduce_all.py` runs the complete validation workflow and exits nonzero on a required mismatch.
