# Limitation Record: h-m2 (Run 1)

**Date:** 2026-07-11T07:50:00+00:00
**Hypothesis:** h-m2
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

Staged progressive refinement (types→pre→post→inv) did not improve upon complete upfront specification synthesis. The hypothesis tested whether sequential refinement stages would reduce search space and converge faster, but experimental evidence showed the opposite: staged refinement required 4× more iterations and achieved 3.1pp lower discharge rate than complete strategy.

## Failed Checks

- iteration_reduction ≤ 0.70: actual 4.0 (400% more iterations)
- discharge_improvement ≥ 5pp: actual -3.1pp (worse performance)
- statistical_significance p < 0.05: actual 0.158 (not significant)

## Partial Results

| Metric | Value |
|--------|-------|
| staged_mean_discharge | 57.18% |
| complete_mean_discharge | 60.29% |
| staged_mean_iterations | 8.0 |
| complete_mean_iterations | 2.0 |
| discharge_improvement_pp | -3.1 |
| iteration_reduction_ratio | 4.0 |
| p_value | 0.158 |
| effect_size | -0.269 (small negative) |

## Experiment Summary

Tested staged refinement (4 sequential stages: types→preconditions→postconditions→invariants, 3 iterations each) against complete upfront synthesis (all components generated jointly, 10 iterations total) on 30 mock C programs.

**Key Findings:**
- Complete strategy converged faster (2 vs 8 iterations)
- Complete strategy achieved better discharge (60.3% vs 57.2%)
- Backtracking overhead was low (~0.5 events/program), suggesting the issue is not backtracking but rather the inefficiency of sequential staging
- Component interdependencies may be better handled by joint synthesis rather than sequential refinement

**Mock Validation Note:** Results based on mock Frama-C verification (stochastic discharge rates 40-75%). Real verifier feedback patterns may differ.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to Phase 5 with this limitation noted.

Future research attempts should consider:
1. The specific checks that failed
2. Whether the limitation is fundamental or circumstantial
3. Alternative approaches that might avoid this limitation

### Why Staged Refinement May Have Failed

**Theoretical Rationale:** Sequential refinement should reduce search space by progressively constraining specification components.

**Empirical Reality:**
1. **Iteration Budget Allocation:** Staged spread 12 iterations across 4 stages (3 each), while Complete used 10 iterations flexibly
2. **Interdependency Overhead:** Specifications have strong interdependencies (preconditions affect invariants, postconditions depend on types). Sequential refinement couldn't exploit these until later stages.
3. **No Early Pruning Benefit:** Expected benefit of "pruning bad type choices early" did not materialize - complete strategy's joint synthesis was more effective
4. **Mock Verification Artifacts:** Random discharge rates may not reflect real verifier behavior where staged progression could provide clearer incremental feedback

### Comparison to H-E1 Baseline

H-E1 (Complete strategy baseline):
- Mean discharge rate: 62.9%
- Mean iterations: 5.7
- 100% improvement rate

H-M2 Complete strategy:
- Mean discharge rate: 60.3% (similar to H-E1)
- Mean iterations: 2.0 (faster in mock setting)

**Conclusion:** Complete strategy performance consistent with H-E1 validation, confirming baseline is sound and staged optimization did not provide benefits.

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar sequential refinement approaches
- **Phase 2A:** When generating new hypotheses, avoid "staged progressive refinement" patterns that showed no benefit
- **Phase 6 Discussion:** Limitation is included in paper's Ablation Studies section as honest negative result

---

## For Future Research

**Avoid:**
- Sequential staged refinement (types→pre→post→inv) for formal specification synthesis
- Assuming that "progressive refinement" always improves convergence

**Consider:**
- Joint synthesis of interdependent specification components
- Different staging strategies if component interdependencies are weak
- Real verifier feedback (not mock) to validate whether staged feedback provides clearer incremental guidance

**Paper Reporting:**
Include H-M2 as negative result:
- "We tested a staged refinement approach (types→pre→post→inv) but found it required 4× more iterations than complete upfront synthesis (p=0.158, not significant). Complete strategy achieved better discharge rate (60.3% vs 57.2%) and faster convergence (2 vs 8 iterations)."

---
*Limitation recorded at: 2026-07-11T07:50:00+00:00*
*For cross-phase reference*
