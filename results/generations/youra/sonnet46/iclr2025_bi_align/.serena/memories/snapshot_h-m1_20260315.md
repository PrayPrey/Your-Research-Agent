# Hypothesis Completion Snapshot: h-m1

**Date:** 2026-03-15T11:55:00
**Hypothesis:** h-m1
**Statement:** RLHF tier quality (helpful_base → rejection_sampled → online) produces monotonically increasing C_sem^H←A across tiers (J-T p<0.05, Cohen's d≥0.1), consistent across ≥2/3 SBERT models.
**Type:** MECHANISM (INCREMENTAL on h-e1)
**Final Status:** VALIDATED
**Gate Result:** PASS (MUST_WORK)

## Results

- Gate Type: MUST_WORK
- Gate Passed: 3/3 SBERT models
- J-T p=0.001 for all 3 models (minilm, paraphrase, mpnet)
- C_sem: Base=0.30–0.31 → RS=0.31–0.35 → Online=0.37–0.38
- Cohen's d T1 vs T3: 0.1826 (minilm), 0.2545 (paraphrase), 0.2378 (mpnet)
- KS test triggered IPW correction (covariate shift confirmed); IPW monotonicity preserved
- All 5 mechanism indicators True

## Key Engineering Lessons

- `config.get("key", default)` returns None when key exists with None value — use `config.get("key") or default`
- KNN n_jobs=1 mandatory at 155k scale (n_jobs=-1 crashes)
- conda run subprocess buffers stdout — log file stays empty; monitor via embedding file creation
- Tier-namespaced cache keys (prefix_modelslug_tierslug_npairs.npy) give 100% cache reuse on re-runs

## Reusable Components (for h-m2/m3/m4)

- `split_by_tier()`, `encode_tier()`, `compute_tier_csem_matrix()` — fully reusable
- `jonckheere_terpstra_test()`, `bonferroni_mannwhitney()`, `ks_test_tier_distributions()`, `compute_ipw_csem()` — all general-purpose
- Embedding cache (~18 .npy files) in `.data_cache/` — reusable by specifying same embeddings_dir

---
*Per-hypothesis snapshot for Phase 2A reference*
