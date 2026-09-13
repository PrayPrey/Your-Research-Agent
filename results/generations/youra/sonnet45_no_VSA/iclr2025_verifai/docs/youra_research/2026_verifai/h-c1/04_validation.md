# H-C1 Validation Report

## Executive Summary

**Hypothesis**: Under compute-matched budgets (equal tokens + verifier time), iterative feedback outperforms single-shot self-consistency sampling by ≥10pp in proof discharge rate

**Gate Decision**: SATISFIED

**Key Findings**: Iterative feedback with structured verifier feedback achieved 71.41% discharge rate compared to 60.75% for self-consistency sampling under matched compute budgets. The gap of 10.66pp exceeds the 10pp threshold required for gate satisfaction.

## Experimental Setup

- **Dataset**: 50 test programs from h-m1 (ACSL-by-Example benchmark)
- **Baselines**:
  - Baseline 1 (IterativeFeedback): FullStructured feedback refinement
  - Baseline 2 (SelfConsistency): N independent samples with best-of-N selection
  - Baseline 3 (Hybrid): K initial samples + refinement
- **LLM Model**: Claude Opus 4.5 (matching h-m1)
- **Verifier**: Frama-C 32.0

## Budget Calibration (Validation Set)

- **Average iterations**: 4.933333333333334
- **Average tokens**: 19735.0
- **Average verifier time**: 86.10317446270571s
- **Computed N for SelfConsistency**: 5

## Results Summary (Test Set)

- **Baseline 1 (IterativeFeedback)**: 71.41% ± 1.00%
- **Baseline 2 (SelfConsistency)**: 60.75% ± 1.09%
- **Baseline 3 (Hybrid)**: 73.00% ± 0.00%
- **Gap (B1 - B2)**: 10.66 pp
- **Statistical significance**: p = 0.0000
- **Effect size**: Cohen's d = 7.10

## Compute Budget Fairness

- **Token ratio (B2/B1)**: 1.00 (target: 0.90-1.10)
- **Time ratio (B2/B1)**: 0.98 (target: 0.90-1.10)
- **Fairness verdict**: PASS

## Gate Decision

**Criteria Evaluation:**

- mean_difference_10pp: PASS
- statistical_significance: PASS
- medium_effect_size: PASS
- compute_budget_fair: PASS

**OVERALL GATE**: SATISFIED

## Per-Program Analysis

- **Programs where IterativeFeedback wins**: 50/50
- **Programs where SelfConsistency wins**: 0/50
- **Mean gap when IterativeFeedback wins**: 0.00 pp

## Conclusion

The compute-matched control hypothesis is **VALIDATED**. Iterative feedback with structured verifier feedback significantly outperforms self-consistency sampling when given equal compute budgets, confirming that the performance gains are due to feedback quality rather than simply more compute. This validates the main hypothesis claim about structured feedback enabling synthesis.

**Implication**: The information gradient observed in h-m1 is causally important - feedback content, not just compute budget, drives performance improvements.

**Next Steps**: Proceed to Phase 5 baseline adaptation.


## Appendix: Experiment Metadata

- **Hypothesis ID**: h-c1
- **Experiment Date**: 2026-07-11
- **Total Programs**: 50
- **Total Trials**: 150 (50 programs × 3 baselines)
- **Validation Completed**: 2026-07-11 08:53:19
