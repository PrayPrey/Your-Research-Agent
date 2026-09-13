# Phase 2A Completion Snapshot: H-ClusterDominance-v4

**Date:** 2026-03-19T15:38:00
**Phase:** 2A-Dialogue COMPLETE
**Hypothesis:** H-ClusterDominance-v4
**Research Folder:** /home/anonymous/YouRA_results_new_4/TEST_verifiai/docs/youra_research/20260316_verifia/

## Hypothesis Statement
PCD (Passing Cluster Dominance = |dominant_passing_cluster| / k) is a statistically significant positive OLS predictor of pass@1 (β > 0, p < 0.05) for ≥3/5 model-benchmark pairs (Llama3-8B, CodeLlama-7B, DeepSeek-6.7B × HumanEval+, MBPP+), after controlling for D_p and self-bootstrapped difficulty.

## Sub-Hypotheses for Phase 2B
- H-E1_v4 (MUST_WORK): MC Bernoulli null exceedance — observed PCD > Q_0.95(null) AND ES ≥ 0.5 for ≥50% mid-θ problems in ≥3/5 pairs
- H-M1_v4 (MUST_WORK): OLS β(PCD) > 0, p < 0.05, ΔR² ≥ 0.02 out-of-sample for ≥3/5 pairs; FCD negative control β ≈ 0
- H-M2_v4 (MUST_WORK): Spearman ρ(PCD, pass@1) ≥ 0.15, bootstrap CI excludes 0, in 0.2 ≤ pass@1 ≤ 0.8 tier, ≥3/5 pairs
- H-M3_v4 (SHOULD_WORK): Observational Baron-Kenny mediation D_p → PCD → pass@1 for ≥2/5 pairs

## Key Design Decisions from Discussion
1. PCD ≠ pass@1: structural concentration vs. frequency — empirically distinguishable
2. FCD (Failing Cluster Dominance) negative control is required — decisive specificity test
3. MC Bernoulli null: n=100,000, conditions on empirical passing trace label distribution
4. Dual-threshold null rejection: 95th percentile + standardized ES ≥ 0.5
5. Residualized ΔR² (r_PCD predicts r_pass): core mechanical coupling falsification
6. Cross-validated ΔR²: 20× problem-stratified 50/50 splits (not single split)
7. H-M3_v4 is observational mediation ONLY — not causal (fixed temperature per model)
8. Difficulty: self-bootstrapped = 1 − mean_pass@1 across 6 pairs (no external CSV)

## Infrastructure Status
- Solution generation: reuse v3 codebase ✓
- EvalPlus evaluation: reuse v3 codebase ✓
- MC Bernoulli null: reuse h-e1_v3 infrastructure (proven 5/5 pairs, |mean_null|<0.002) ✓
- NEW: PCD computation (dominant passing cluster from binary trace vectors)
- NEW: FCD computation (dominant failing cluster)
- NEW: Residualized ΔR² + cross-validation code

## Phase 2A Outputs Generated
- discussion_log.md (15 exchanges, all 6 personas, CONVERGED)
- 03_refinement.yaml (primary Phase 2B input)
- 02_synthesis.yaml (synthesis details)
- 01_round_table/final_opinions.yaml (agent assessments)
- 03_refinement.md (human-readable summary)

## Archon Status
- Pipeline Project: 522b1b41-c34a-490c-9265-def341674d73
- Phase 2A task: 2d3d8da9 → done
- Step tasks: 2A-0/P/1/2/3 all → done

## Next Phase: Phase 2B
