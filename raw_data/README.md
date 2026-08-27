# Raw data

This directory contains the historical machine-readable outputs retained for provenance and the `regenerated/` outputs from the final validation pass.

The four replacement-slack campaign counts are regenerated from source and asserted by `reproduce_all.py`:

- sequential suite: 3,445 eligible rows;
- 60-graph stress suite: 6,912;
- 400-graph stress suite: 26,897;
- exact-integer campaign: 6,870;
- combined total: 44,124.

Timing fields are environment-dependent and are not exact manifest assertions. See `RESULT_PROVENANCE.md` for commands, seeds, graph families, output files, and aggregation rules.
