# Structural Compression in Dynamic Dense Distance Graphs - Reproducibility Package

## Paper and authors

**Title:** Structural Compression in Dynamic Dense Distance Graphs

- **Ranjan Veerabhadraswamy** — `ranjanvswamyjnv2005@gmail.com` — ORCID `0009-0007-5974-6877`
- **Ajith Jubilson Emerson** — `ajith.jubilson@vitap.ac.in` — ORCID `0000-0001-6677-2917` — **Corresponding Author**

**Affiliation for both authors:** School of Computer Science and Engineering, Vellore Institute of Technology, Andhra Pradesh, Amaravati, Andhra Pradesh 522241, India.

## Purpose and scientific boundary

This repository contains the code, data, verification scripts, and reproducibility materials accompanying the Algorithmica submission. The mathematics is frozen. The package does **not** claim a general sublinear-update DDG, `O(sqrt(r))` arbitrary-edge update time, a solution to general online decremental DDG maintenance, an improved dynamic planar APSP exponent, or a general `Omega(sqrt(r))` dynamic-update lower bound.

Finite computational checks supplement the manuscript proofs; they are not proofs themselves.

## Layout

- `code/core/` — graph, exact-shortest-path, DDG, replacement-slack, and Active-Edge Kernel implementations.
- `code/verification/` — named finite theorem/result verifiers.
- `code/experiments/` — public experiment entry points.
- `code/legacy/` — original historical programs retained for provenance.
- `tests/` — fast unit/expected-failure tests.
- `raw_data/` — shipped machine-readable historical outputs; `raw_data/regenerated/` is created by reproduction.
- `processed_data/` — deterministic derived summaries.
- `reproduced_figures/` — freshly generated computational figures.
- `docs/` and root audit Markdown files — theorem, proof, complexity, citation, novelty, provenance, reproducibility, claim, changelog, and human-check records.
- `EXPECTED_RESULTS.json` — post-computation assertion manifest for published finite outputs.

## Environment

Validated release environment:

- Python 3.13.5
- NetworkX 3.6.1
- NumPy 2.3.5
- SciPy 1.17.0
- Matplotlib 3.10.8
- pandas 2.2.3
- pytest 9.0.2

Install with either:

```bash
python -m venv .venv
. .venv/bin/activate          # Linux/macOS
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

or:

```bash
conda env create -f environment.yml
conda activate ddg-sicomp-repro
```

## Quick validation

```bash
python reproduce_all.py --quick
```

This runs `pytest`, all exact modular theorem/result verifiers, validates the shipped deterministic raw outputs against the manifest, rebuilds processed summaries, and regenerates figures. On the final validation machine this completed in **14.64 s** wall-clock time; the clean-extracted supplement repeated it in **14.66 s**. Runtime is environment-dependent and is not a scientific result.

Equivalent individual commands include:

```bash
pytest -q
PYTHONPATH=code python code/verification/verify_all.py
```

## Full authoritative reproduction

```bash
python reproduce_all.py --full
```

The default command `python reproduce_all.py` is equivalent to `--full`.

The full driver:

1. records the environment;
2. runs unit tests and exact modular verifiers;
3. reruns the original 240-update suite;
4. reruns the deterministic 60-graph and 400-graph slack campaigns;
5. reruns the exact-integer/adversarial/AEK campaign;
6. reruns the explicit interval-patch construction checker;
7. writes regenerated raw outputs;
8. derives processed summaries;
9. compares computed scientific values to `EXPECTED_RESULTS.json` only **after** computation;
10. regenerates every computational figure;
11. writes `REPRODUCIBILITY_REPORT.md` and exits nonzero on a required mismatch.

On the final validation machine the authoritative full command completed in **30.86 s** wall-clock time; the clean-extracted supplement repeated the complete run in **34.44 s**. This measured duration is environment-dependent and is not used in any manuscript claim.

## Public verification scripts

```text
code/verification/
  verify_support_equivalence.py
  verify_interval_theorem.py
  verify_replacement_identity.py
  verify_peak_unimodality.py
  verify_three_region_structure.py
  verify_interval_patch_lower_bound.py
  verify_aek.py
  verify_all.py
```

Public experiment entry points are under `code/experiments/`, including the original support suite, slack falsification, exact-integer suite, adversarial search, AEK validation, prototype timing, and figure generation.

## Expected finite scientific outputs

The authoritative rerun must reproduce:

- 240 sequential updates;
- 3,445 sequential eligible slack rows;
- 6,912 rows in the 60-graph stress campaign;
- 26,897 rows in the 400-graph campaign;
- 37,254 original/pre-exact rows;
- 6,870 additional exact-integer rows;
- **44,124 combined eligible replacement-slack rows**;
- 256 exact support-check instances with zero support/interval failures;
- 405 adversarial mutation/annealing evaluations;
- 810 exact AEK validation queries with zero discrepancies;
- 30 explicit interval-patch construction instances for `k=3..32`.

See `RESULT_PROVENANCE.md` for scripts, seeds, graph families, parameters, raw outputs, and aggregation rules. Timing fields are environment-dependent and intentionally excluded from exact scientific equality assertions.

## Figure regeneration

The full/quick driver regenerates computational figures automatically. Standalone command:

```bash
PYTHONPATH=code python code/figures/generate_all_figures.py \
  --raw raw_data/regenerated \
  --processed processed_data \
  --out reproduced_figures
```

Generated computational figures are `support_matrix_example`, `slack_profile`, `support_scaling`, and `runtime_benchmark` in PDF/PNG. The conceptual support-vs-values figure is generated in LaTeX/TikZ. No plotted data are manually edited.

## Raw/processed data and comparison

All reported finite experimental quantities have a raw machine-readable source under `raw_data/`. Derived summaries are under `processed_data/`. A successful full reproduction ends with:

```json
{"status": "PASS", "total_slack_rows": 44124}
```

Use `REPRODUCIBILITY_REPORT.md`, `processed_data/validation_summary.json`, `EXPECTED_RESULTS.json`, and `RESULT_PROVENANCE.md` to compare regenerated outputs with the manuscript.

## License

See `LICENSE`. The accompanying authors' code and data are packaged for scholarly peer review and reproducibility.
