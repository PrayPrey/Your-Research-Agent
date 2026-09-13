# Phase 4.5 Synthesis Results
Date: 2026-08-03
Research: SFT training source identity effect on code benchmark performance (H-D1)

## Key Outcomes
- Predictions supported: 2/3 (P1 SUPPORTED, P2 PARTIALLY_SUPPORTED, P3 SUPPORTED)
- Refined core statement: Source identity → significant HumanEval+ pass@1 differences at 1.3B (29.6pp max), embedding-alignment-predicted (CodeBERT ρ=1.0, p=0.042), with HE-only showing unexpected cross-benchmark generalization advantage
- Main theoretical contribution: First permutation-tested evidence that code-embedding distributional alignment predicts SFT source condition pass@1 rank order (ρ=1.0, p=0.042, n=10,000)
- Critical limitation: MBPP+ evaluation incomplete in H-E2 and H-C1; core claims restricted to HumanEval+ as primary benchmark

## Hypothesis Outcomes
- h-e1: VALIDATED (MUST_WORK gate SATISFIED) — MiniLM all 8 pairs below 0.95; CodeBERT LeetCode pairs 0.909, 0.946
- h-e2: VALIDATED (MUST_WORK gate SATISFIED) — ANOVA F=11.37, p=0.020; 29.6pp max pairwise contrast
- h-m1: LIMITATION_RECORDED (SHOULD_WORK FAILED) — HE+ inversion 2/3 seeds; MBPP+ inversion absent; HE-only dominates both benchmarks
- h-m2: VALIDATED (SHOULD_WORK SATISFIED) — CodeBERT ρ=1.0, p=0.042; MiniLM ρ=0.8 concordant
- h-c1: LIMITATION_RECORDED (SHOULD_WORK FAILED) — η² inflated by seed collapse; absolute spread 5.5pp vs 31.9pp at 1.3B

## Lessons for Future Pipelines
- MBPP+ evaluation must be saved explicitly to CSV — H-E2 EvalPlus output was computed but not persisted in the analysis-ready format
- η² is an unreliable cross-scale effect size metric when within-condition seed variance changes with scale; use absolute condition spread as primary metric
- With n=4 conditions, Spearman permutation p-value minimum is 1/24 ≈ 0.042 — design for ≥5 conditions or treat as directional evidence
- HumanEval-only SFT generalizes to MBPP+ better than MBPP-only SFT — symmetric specialization assumption fails; this is a publishable finding
- Equal-mix underperforms single-source at limited scale — source specificity dominates diversity at small token budgets
