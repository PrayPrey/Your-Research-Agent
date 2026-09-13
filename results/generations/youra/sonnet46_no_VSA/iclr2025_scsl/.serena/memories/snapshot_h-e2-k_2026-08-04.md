# Hypothesis Completion Snapshot: h-e2-k

**Date:** 2026-08-04T08:30:00+00:00
**Hypothesis:** h-e2-k
**Statement:** Hutchinson trace estimator with K=10 Rademacher probes achieves adequate SNR for per-sample minority/majority discrimination, evidenced by AUROC plateau (AUROC_K=20 - AUROC_K=10 < 0.01) across 5 seeds
**Final Status:** FAILED
**Gate Result:** FAIL (MUST_WORK)

## Results
- delta_10_20 = 0.01117 (threshold: < 0.01) → FAIL
- K=10 AUROC: 0.8974 ± 0.0028
- K=20 AUROC: 0.9086 ± 0.0022
- K=50 AUROC: 0.9130 ± 0.0020
- Analytical AUROC: 0.9189 ± —
- Plateau achieved at K=20→50 (delta=0.0044 < 0.01)
- Analytical cross-check: gap ≈ 0.006 < 0.05 (estimator correct)

## Key Findings
- Hutchinson estimator is correctly implemented and validated
- AUROC plateau requires K=20, not K=10
- Per failure route: use K=20 (or K=50) as primary K in H-E2-exist

## Reusable Code
- `run_experiment.py`: WaterbirdsDataset, load_model (fc-replace before load_state_dict), extract_features, compute_hutchinson_traces, compute_analytical_traces, verify_traces, save_figures
- fc must be replaced to nn.Linear(2048,2) BEFORE load_state_dict (checkpoint has 2-class head)

---
*Per-hypothesis snapshot for Phase 2A/5/6 reference*
