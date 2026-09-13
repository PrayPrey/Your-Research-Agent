# Limitation Record: h-m2 (Run 1)

**Date:** 2026-08-26T08:00:00+00:00
**Hypothesis:** h-m2
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

SHOULD_WORK gate failed — competition_nonzero_fraction = 0.0000 does not exceed the 0.10 threshold.

The experiment evaluated the SFT-warm checkpoint (from H-E1) via post-hoc inference on 60 competition-level APPS problems (G=2 generations, max_new_tokens=128). Zero non-zero reward was observed across all difficulty buckets.

## Failed Checks

- competition_nonzero_fraction > 0.10 (actual: 0.0000)
- Monotonicity across difficulty buckets (trivially held at zero — not meaningful)

## Partial Results

| Metric | Value |
|--------|-------|
| competition_nonzero_fraction | 0.0000 |
| introductory_nonzero_fraction | 0.0000 |
| interview_nonzero_fraction | 0.0000 |
| gate_threshold | 0.10 |
| n_samples | 180 (60 per bucket) |
| generations_per_problem | 2 |
| max_new_tokens | 128 |

## Experiment Summary

H-M2 tested whether RLEF-Fraction training on APPS produces >10% non-zero reward on competition-split problems. Post-hoc evaluation using the H-E1 SFT-warm checkpoint yielded zero non-zero reward across all difficulty buckets.

Root causes:
1. max_new_tokens=128 truncates most competition-level solutions before completion
2. SFT-warm checkpoint is not optimized for test-case correctness — it learns problem→code formatting only
3. Competition problems require multi-step algorithmic reasoning; greedy decoding at 128 tokens cannot produce correct algorithms
4. Exact I/O match required by test cases; partial or truncated outputs yield zero reward

Note: H-M2 was intended to measure reward during RLEF training (not at baseline). Using the SFT checkpoint as a proxy captures the pre-RLEF reward baseline — which is expected to be near-zero. The RLEF training is intended to lift this fraction.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to Phase 5 with this limitation noted.

Future research attempts should consider:
1. Increase max_new_tokens to 512–1024 for competition-level solutions
2. Run actual RLEF training to convergence and monitor reward mid-training (not post-hoc)
3. Use a stronger baseline (DeepSeek-Coder-7B-instruct) which has better zero-shot correctness
4. Lower gate threshold to 0.02–0.05 for the SFT-warm baseline evaluation

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0, this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation included in paper's Limitations section

---
*Limitation recorded at: 2026-08-26T08:00:00+00:00*
*For cross-phase reference*
*Note: Written as local file — Serena MCP unavailable in this session (same fallback as H-E1, H-M1)*
