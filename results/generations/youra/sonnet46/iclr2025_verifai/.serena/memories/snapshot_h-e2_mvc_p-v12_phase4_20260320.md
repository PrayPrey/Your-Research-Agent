# H-E2 (H-MVC_p-v12) Phase 4 Completion Snapshot

**Completed:** 2026-03-20T14:35:00Z
**Pipeline:** TEST_verifiai / 20260316_verifia
**Archon Task:** 1a279783-24a9-447c-8bf7-67255904ab01 (done)

## Gate Result: PASS (MUST_WORK)

- **Pairs Passing:** 5/5 (threshold: 3/5)
- **rho Range:** 0.509 – 0.851
- **All p_boot:** 0.0000 (no bootstrap resample yielded rho ≤ 0 out of 10,000)

## Per-Pair Results

| Pair | rho | p_boot | n |
|------|-----|--------|---|
| llama3_humaneval | 0.5090 | 0.0000 | 164 |
| llama3_mbpp | 0.7880 | 0.0000 | 378 |
| deepseek_humaneval | 0.7110 | 0.0000 | 164 |
| deepseek_mbpp | 0.8507 | 0.0000 | 378 |
| codellama_mbpp | 0.8489 | 0.0000 | 378 |

## Unlocked Hypotheses

- **h-m1** (MECHANISM, MUST_WORK): OLS regression pass@1 ~ LOOM + MVC_p → now READY
- **h-m2** (MECHANISM, SHOULD_WORK): Tau sensitivity rho(tau=3/4/5) monotonicity → now READY
- **h-m3** (MECHANISM, SHOULD_WORK): Permutation test → already READY (no prerequisites)

## Key Files

- `h-e2/04_validation.md` — Phase 4 validation report
- `h-e2/code/run_experiment.py` — Single-file experiment (LIGHT tier)
- `h-e2/results/h_e2_results.json` — Detailed per-pair results
- `h-e2/experiment_results.json` — Full structured results with mock_data_detection PASSED
- `h-e2/04_checkpoint_archived_20260320T143600Z.yaml` — Archived checkpoint

## Hyperparameters Confirmed

- tau=4, k=5, n_boot=10000, bootstrap_seed=42, rho_threshold=0.10, gate_min_pairs=3

## Next Action

Execute Phase 2C → 3 → 4 for h-m1 (READY, prerequisite h-e2 PASS).
