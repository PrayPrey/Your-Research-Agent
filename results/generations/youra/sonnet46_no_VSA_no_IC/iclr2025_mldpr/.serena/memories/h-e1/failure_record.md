# Failure Record: h-e1 (H-CoVReuse-v1)

## Status: FAILED — ROUTED_TO_PHASE_0

## Hypothesis
High-reuse benchmarks (high paper_count) show higher result CoV than low-reuse benchmarks.

## Results (2026-08-21)
- N = 111 benchmarks (pwc-archive/evaluation-tables)
- Spearman rho = -0.2841 (NEGATIVE — opposite direction)
- p-value = 0.0025 (significant, wrong direction)
- Partial rho (age-adjusted) = 0.0202 (non-significant, p=0.834)
- Quartile ratio Q4/Q1 = 0.592 (high-reuse has LOWER CoV)
- Permutation p-value = 0.0

## Gate: MUST_WORK FAIL
Condition: rho > 0 AND pval < 0.05. rho is negative.

## Root Cause
Causal mechanism inverted. High-reuse benchmarks converge to performance ceiling
("Goodhart's Law / benchmark saturation"): community pressure to "solve" popular
benchmarks reduces score variance, not increases it. Hypothesis assumed competition
creates noise; reality is competition creates convergence.

## Lessons for Phase 0 Redesign
1. Popular benchmarks get "solved" — CoV drops as scores cluster near ceiling
2. Age confound does not explain the effect (partial rho ~0, p=0.834)
3. Effect is real and replicable (permutation null p=0.0) but direction is inverted
4. Reframe: consider saturation hypothesis — CoV decreases with reuse (confirmed here),
   or investigate CoV as function of max-score proximity / benchmark maturity
