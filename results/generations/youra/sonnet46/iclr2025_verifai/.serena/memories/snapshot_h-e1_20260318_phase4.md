# Hypothesis Completion Snapshot: h-e1 Phase 4

**Date:** 2026-03-18T18:00:00+00:00
**Hypothesis:** h-e1
**Statement:** For problems where m_p >= 2 compilable solutions exist, D_p (mean pairwise normalized Hamming distance over ALL k=5 solutions) is strictly positive (D_p > 0) for a non-trivial fraction (>=60%) of problems across all required model-benchmark pairs.
**Final Status:** PASSED
**Gate Result:** PASS (MUST_WORK gate satisfied)

## Results
- All 5 model-benchmark pairs exceeded 60% D_p > 0 fraction gate
- Llama3-8B × HumanEval+: 86.6%, D_p_mean=0.290
- Llama3-8B × MBPP+: 70.4%, D_p_mean=0.241
- DeepSeek-Coder-6.7B × HumanEval+: 86.6%, D_p_mean=0.326
- DeepSeek-Coder-6.7B × MBPP+: 64.3%, D_p_mean=0.227
- CodeLlama-7B × MBPP+: 71.2%, D_p_mean=0.240
- m_p >= 2 coverage: 100% for all pairs

## Key Technical Findings (for downstream h-m1..h-m4)
- EvalPlus v0.3.1 --test_details: base_fail_tests/plus_fail_tests are FAILING TEST INPUTS (not indices)
- Binary vector reconstruction: hash-based index map (_make_index_map) for O(1) lookup — critical for performance
- EvalPlus output path: {samples_basename}_eval_results.json (next to samples file, NOT in output_dir)
- T_p varies per problem (variable-length binary vectors): always use shape[1] >= 1, not fixed T
- D_p=0 cases: predominantly Unanimous Pass (near-trivial), no Partial Collapse detected
- MBPP+ has ~30% unanimous pass problems → lower D_p fractions than HumanEval+ (~10%)
- Reuse build_pair_matrices() from h-e1/code/src/data_extraction.py directly in downstream hypotheses
- Cache *_eval_results.json files — EvalPlus evaluation is expensive (~minutes per pair)

## Phase 4 Completion
- 15/15 tasks completed (LIGHT tier, 1 coder-validator cycle)
- 38 unit tests all pass
- 13 figures generated in h-e1/code/figures/
- Results in h-e1/code/results/summary.json and h-e1/experiment_results.json
- Checkpoint archived: 04_checkpoint_archived_2026-03-18T174500.yaml
- Phase 4 complete for h-e1. Next: h-m1 unblocked (prerequisites: []).

---
*Phase 4 completion snapshot — 2026-03-18*
