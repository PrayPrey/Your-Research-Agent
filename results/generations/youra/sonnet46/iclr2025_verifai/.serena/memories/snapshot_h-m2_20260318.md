# Hypothesis Completion Snapshot: h-m2

**Date:** 2026-03-18T13:00:00+00:00
**Hypothesis:** h-m2
**Statement:** Under model-specific pass@1 stratification, if problems are assigned to hard (pass@1=0.0) and easy (pass@1>=0.6) tiers per model, then tier assignments reflect genuine competence differences (Jaccard similarity of hard-tier problem sets across models > 0.3), because structurally hard problems tend to be hard across different architectures.
**Final Status:** COMPLETED
**Gate Result:** PASS
**Gate Type:** SHOULD_WORK (strict J > 0.3)

## Results

- Validation: PASS (3/3 model pairs exceed J > 0.3 threshold)
- Max Jaccard: 0.5462 (llama3-8B vs codellama-7B)
- All pairs: llama3-codellama=0.5462, llama3-deepseek=0.5305, codellama-deepseek=0.4561
- Consensus hard set: 133 problems (24.5% of 542 universally hard)
- 542-row tier_assignments.csv generated

## Key Data for h-m3

- Input file: `h-m2/results/tier_assignments.csv` (columns: task_id, benchmark, llama3_tier, codellama_tier, deepseek_tier, n_models_hard, n_models_easy)
- Hard tier sizes: llama3=228, codellama=341, deepseek=173
- Easy tier sizes: llama3=167, codellama=37, deepseek=200 (CodeLlama borderline — use MBPP tiers for ECE)
- HARD_THRESHOLD=0.0, EASY_THRESHOLD=0.6
- Conda env: youra-h-m2

## Lessons Learned

- pyproject.toml: use `build-backend = "setuptools.build_meta"` (not `setuptools.backends.legacy:build`)
- Test fixtures: always manually verify Jaccard calculations before coding tests
- itertools.combinations with sorted(keys) ensures deterministic pair ordering
- np.isclose required for 6-point float bin matching in histograms

---
*Per-hypothesis snapshot for Phase 2A/h-m3 reference*
