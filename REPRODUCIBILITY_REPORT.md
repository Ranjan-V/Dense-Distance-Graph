# Reproducibility Report

Status: **PASS**

## Reproduced manuscript counts

- Sequential updates: 240
- Sequential eligible slack rows: 3445
- 60-graph stress rows: 6912
- 400-graph stress rows: 26897
- Original/pre-exact total: 37254
- Exact eligible slack rows: 6870
- **Grand total: 44124**
- Exact support-check instances: 256
- Exact support failures: 0
- Exact interval failures: 0
- Adversarial mutation/annealing evaluations: 405
- Exact AEK queries/failures: 810/0
- Interval-patch construction instances: 30 (k=3..32)

The reported 44,124-row count reproduces exactly. Timings were rerun but are explicitly environment-dependent and are not compared byte-for-byte. Finite checks complement; they do not replace, the manuscript proofs.

## Environment

```json
{
  "python": "3.11.9",
  "platform": "Windows-10-10.0.26200-SP0",
  "networkx": "3.6.1",
  "numpy": "1.26.4",
  "scipy": "1.11.1",
  "matplotlib": "3.10.8",
  "pandas": "2.3.3"
}
```
