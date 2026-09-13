---
name: snapshot_h-e1_20260317
description: Phase 4 completion snapshot for h-e1 - PARTIAL gate with LIMITATION_RECORDED reflection outcome
type: project
---

# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-03-17T07:32:00Z
**Hypothesis:** h-e1 — Cross-Benchmark × Cross-Corpus Contamination Matrix Existence
**Statement:** Measurable contamination (LONGEST-MATCH z-score > 2 in ≥1 benchmark-corpus pair) exists in standard LLM evaluation benchmarks against major pretraining corpora — producing a non-trivial contamination matrix with ≥3 benchmark-corpus pairs showing elevated n-gram overlap.
**Final Status:** PARTIAL
**Gate Result:** PARTIAL (MUST_WORK gate)
**Reflection:** LIMITATION_RECORDED

## Results

- Validation: PARTIAL
- Gate Type: MUST_WORK
- Reflection outcome: LIMITATION_RECORDED
- Algorithm validated: 53/53 tests pass
- Contaminated cells: 0/8 (scale constraint)
- ROOTS corpus: unavailable (gated)
- Limitation: n=13/mincount=5 requires >100M docs; 10k-doc PoC produces all-zero scores

## Infrastructure Created (Reusable)

- code/config.py, data_loader.py, ngram.py, minhash_audit.py, visualize.py, run.py
- Full contamination matrix with per-cell checkpointing
- 53 unit tests covering all modules
- 3 figures generated (contamination_matrix.png, gate_metrics.png, zscore_distributions.png)

---
*Per-hypothesis snapshot for Phase 2A reference*
