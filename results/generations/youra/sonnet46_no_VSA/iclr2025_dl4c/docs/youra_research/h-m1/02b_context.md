# Phase 2B Context: H-M1
# JIT-Generated from 02b_verification_plan.md by Phase 2C step-01

---

## Hypothesis Information

- **ID:** H-M1
- **Type:** MECHANISM
- **Gate:** SHOULD_WORK
- **Prerequisites:** H-E2 (VALIDATED)
- **Statement:** Cross-benchmark transfer is asymmetric: HumanEval-only training outperforms MBPP-only on HumanEval+, and MBPP-only training outperforms HumanEval-only on MBPP+ (directional inversion pattern), consistent across ≥2/3 seeds at 1.3B scale, confirming same-source specialization advantage (P2).

## Why This Matters

The inversion pattern is the single most compelling evidence for the alignment mechanism. A model that simply learns "more code" would not show this pattern — it requires source-specific representational specialization.

## Experimental Setup (from Phase 2A via Phase 2B)

### Dataset
- **Primary:** HumanEval+ (164 problems) and MBPP+ (374 problems) — EvalPlus suite
- **Type:** standard (established benchmarks)
- **Source:** evalplus/evalplus GitHub repo
- **Hypothesis Fit:** The two benchmarks have structurally distinct problem types (doctest-style vs utility-style), making them ideal for testing cross-benchmark asymmetric transfer.

### Model
- **Name:** DeepSeek-Coder-Base-1.3B
- **Type:** Pretrained code LLM
- **Source:** deepseek-ai/deepseek-coder-1.3b-base (HuggingFace)
- **Hypothesis Fit:** 1.3B scale where H-E2 showed significant source effect; same model family ensures controlled comparison.

### Analysis Reuses H-E2 Data
- Extract pass@1 per source condition from H-E2 runs (already completed)
- Compare HumanEval-only vs MBPP-only on both benchmarks
- Check rank order inversion across ≥2/3 seeds
- Additional check: LeetCode-only vs MBPP-only inversion

## Success Criterion

Both inversions (HE-only > MBPP-only on HumanEval+, MBPP-only > HE-only on MBPP+) present in ≥2/3 seeds at 1.3B.

## Baseline & Comparison Targets

- HumanEval-only pass@1 on HumanEval+ vs MBPP+
- MBPP-only pass@1 on HumanEval+ vs MBPP+
- LeetCode-only as additional cross-condition check
- Equal-mix as falsifier baseline

## Gate Conditions

- SHOULD_WORK gate: failure does not block pipeline; partial result noted
- H-E2 MUST be VALIDATED (confirmed: VALIDATED)

## Compute

Zero additional training. Analysis-only experiment using H-E2 checkpoint results.

## Dependencies

- H-E2 validation results (pass@1 per source × benchmark × seed)
- EvalPlus evaluation already run on H-E2 checkpoints
