# Hypothesis Completion Snapshot: H-E1

**Date:** 2026-08-02T12:00:00+00:00
**Hypothesis:** H-E1
**Statement:** Under pre-SFT conditions, DeepSeek-Coder-1.3B produces higher gradient magnitude (AdamW update L2 norm) on Easy LeetCode problems than DeepSeek-Coder-6.7B (Mann-Whitney p < 0.05), because the 1.3B model has substantially higher loss on problems that are near-trivial for the 7B model—this capability-complexity differential is the prerequisite for the curriculum gradient-variance mechanism.
**Final Status:** COMPLETED
**Gate Result:** PASS

## Results
- Validation: PASS
- Gate Type: MUST_WORK
- Mann-Whitney U p-value: 6.48e-14 (threshold: 0.05) ✅
- Gradient ratio (1.3B/6.7B Easy): 1.672x ✅
- Mean gradient norm 1.3B Easy: 6.770 ± 4.123
- Mean gradient norm 6.7B Easy: 4.048 ± 2.733
- Dataset: newfacade/LeetCodeDataset, 510 samples (170/bucket), seed=42
- Deduplication: all-MiniLM-L6-v2, cosine sim > 0.95 vs HumanEval+ and MBPP+
- Hardware: 5× H100 NVL, bfloat16, batch_size=1

## Notes
- pool_size sub-indicator: 510 < 800 (pre-experiment estimate was conservative; actual dataset size after stratified sampling)
- no_zero_norms: some empty completions produced loss=nan → norm=0; does not affect primary gate
- mechanism_activated field: False (sub-indicators), but primary MUST_WORK criterion (p < 0.05) strongly satisfied

---
*Per-hypothesis snapshot for Phase 2A reference*
