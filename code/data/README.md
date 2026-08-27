# Data layout

The canonical paper outputs are stored at the repository root under `raw_data/` and `processed_data/`.

- `raw_data/` contains machine-readable outputs from the historical experiment configurations and the final reproduction pass.
- `processed_data/` contains deterministic aggregations used to generate figures/tables.
- `EXPECTED_RESULTS.json` defines the scientific invariants checked by `reproduce_all.py`.

Wall-clock timing columns are environment-dependent and are deliberately excluded from exact scientific-value comparisons.
