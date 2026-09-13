# Hypothesis Completion Snapshot: H-DpResidual-v1 Phase 2A

**Date:** 2026-03-19T11:54:00
**Hypothesis:** H-DpResidual-v1
**Phase:** 2A-Dialogue (hypothesis generation)
**Final Status:** COMPLETE
**Convergence:** Exchange 15, all 6 criteria met

## Hypothesis
Under EvalPlus augmented evaluation (HumanEval+ and MBPP+) with k=5 solutions per problem,
D_p_residual (mean pairwise Hamming distance residualized against Bernoulli expectation via C(5,2)
cross-fitting) positively predicts pass@1 after controlling for cross-model difficulty, for ≥3/5
model-benchmark pairs, because partial competence → structured solution modes → super-Bernoulli
behavioral fluctuations.

## Key Refinements vs v2 (H-ExecTraceDiversity-v2)
- **DV change**: pass@k (saturates) → pass@1 (full variance, no saturation)
- **IV change**: raw D_p → D_p_residual (Bernoulli-residualized via C(5,2) splits)
- **Difficulty control**: 1-pass@1 (circular) → cross-model pass@1 (independent, from other model families)
- **Mechanism test**: eigenvalue test (underpowered k=5) → within-vs-between Hamming distance test

## Hypothesis Chain (Phase 2B targets)
- H-E1 (PROVEN, BUILD_ON): D_p > 0 for ≥60% of problems — 64-87% confirmed
- H-M1 (PROVEN, BUILD_ON): B_p matrix coverage = 1.0 — confirmed
- H-M2_v3 (MUST_WORK): OLS β(D_p_residual) > 0 after cross-model difficulty, ≥3/5 pairs
  - Monte Carlo calibration: |mean D_p_residual| < 0.002 under Bernoulli null
- H-M3_v3 (MUST_WORK): Within-tier Spearman ρ(D_p_residual, pass@1) ≥ 0.15, mid-difficulty band, ≥3/5 pairs
  - Regime-specific: β₂ larger in mid-band [0.3,0.7] vs extremes
- H-M4_v3 (SHOULD_WORK): H_p entropy ΔR² > 0.02 over D_p_residual alone
- P3 (mechanism): Between-cluster > within-cluster Hamming distance beyond Bernoulli null, ≥60% contested problems

## Data Sources (all pre-existing)
- B_p matrices: h-m1/results/ (coverage=1.0 validated)
- pass@1 per problem: h-m1/results/ (directly computable)
- Models: Llama3-8B, CodeLlama-7B, DeepSeek-Coder-6.7B
- Benchmarks: HumanEval+ (164 problems), MBPP+ (378 problems)
- 5 model-benchmark pairs total

## Output Files (research folder: 20260316_verifia)
- discussion_log.md: 51697 bytes, 15 exchanges, Final Assessments section
- 03_refinement.yaml: 26659 bytes, Phase 2B primary input (v10.0.0 Free-Parse)
- 02_synthesis.yaml: 7497 bytes, synthesis details
- 01_round_table/final_opinions.yaml: 7362 bytes, all 6 agent assessments
- 03_refinement.md: 6607 bytes, human-readable summary

## Archon Project
- Project ID: 68e25d1c-70d9-49fd-ab7a-bf18fafc4e4e
- Pipeline title: "Anonymous Pipeline: Execution Trace Diversity predicts pass@1 (v3)"
- All step tasks (2A-0, 2A-P, 2A-1, 2A-2): done
- Phase 1 task: done

## Next Phase
Phase 2B: Sub-hypothesis decomposition and verification planning.
Starting from H-M2_v3 (H-E1 and H-M1 are BUILD_ON — skip their verification gates).
Key Phase 2B note: use D_p_residual formulation, cross-model difficulty, pass@1 DV throughout.
