# Hypothesis Completion Snapshot: H-ExecTraceDiversity-v2 Phase 2A

**Date:** 2026-03-19T08:36:00
**Hypothesis:** H-ExecTraceDiversity-v2
**Phase:** 2A-Dialogue (hypothesis generation)
**Final Status:** COMPLETE
**Convergence:** Exchange 15, all 6 criteria met

## Hypothesis
Under EvalPlus augmented test evaluation (HumanEval+ and MBPP+) with k=5 solutions per problem,
D_p (mean pairwise Hamming distance of binary test-case pass/fail vectors across ALL k solutions)
correlates positively with pass@k (Spearman ρ ≥ 0.20, bootstrap 95% CI excluding 0, within
difficulty tiers) for ≥3/5 model-benchmark pairs AND ≥2/3 distinct models.

## Hypothesis Chain (Phase 2B targets)
- H-M1 (MUST_WORK): B_p matrix coverage ≥90% per pair (EvalPlus --test-details infrastructure)
- H-M2 (MUST_WORK): OLS beta(D_p) > 0 after pass@1 covariate, ≥3/5 pairs, no sign reversal
- H-M3 (MUST_WORK, PRIMARY): Within-tier Spearman ρ(D_p, pass@k) ≥ 0.20, CI excludes 0, ≥3/5 pairs
- H-M4 (SHOULD_WORK): Entropy H_p vs D_p hierarchical ΔR² comparison

## Key Design Decisions
- Gate: ≥3/5 model-benchmark pairs AND ≥2/3 distinct models (dual gate — prevents single-model artifact)
- D_p correctness inflation mitigated by: OLS with pass@1 covariate (H-M2) + within-tier Spearman (H-M3)
- Architecture-independence guaranteed by construction: oracle outputs only, no model internals
- H_p = per-test-case entropy (marginal); D_p = pairwise inter-solution Hamming (joint) — orthogonal aspects of B_p

## Data Sources (all pre-existing, no new inference needed)
- B_p matrices: h-e1/code/results/ (validated in Phase 4)
- pass@k, pass@1: h-m1/results/pass_at_1_hm1_verified.json
- Difficulty tiers: h-m2/results/tier_assignments.csv
- Models: Llama3-8B, CodeLlama-7B, DeepSeek-Coder-6.7B
- Benchmarks: HumanEval+ (164 problems), MBPP+ (378 problems)

## Output Files (research folder: 20260316_verifia)
- discussion_log.md: 53KB, 15 exchanges, Final Assessments section
- 03_refinement.yaml: PRIMARY Phase 2B input (v10.0.0 Free-Parse, 12/12 checks pass)
- 02_synthesis.yaml: synthesis details
- 01_round_table/final_opinions.yaml: all 6 agent assessments
- 03_refinement.md: human-readable summary

## Archon Project
- Project ID: 94413f02-017b-4434-b4ff-c60aef5de9bb
- Pipeline Phase 2A task: done
- All 5 step tasks (2A-0, 2A-P, 2A-1, 2A-2, 2A-3): done

## Next Phase
Phase 2B: Sub-hypothesis decomposition and verification planning
Starting from H-M1 (B_p matrix infrastructure verification).
H-E1 existence proof already PASSED — skip to H-M1.
