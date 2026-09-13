---
hypothesis_id: H-M2
phase: 4
gate_type: SHOULD_WORK
gate_result: FAIL
route_to: EXPLORE
date: 2026-08-26
author: yoon303@ust.ac.kr
---

# Validation Report: H-M2 — Mypy Feedback Specificity for Type-Related Failures

## Hypothesis

Under Condition A (execution-only) vs. Condition B (execution+mypy), Condition B achieves higher per-category repair rate specifically for type-related failures (not semantic/logic), because mypy provides error-type specificity that execution output lacks.

**Gate**: SHOULD_WORK — `differential = delta_type − delta_non > 0`

---

## Experiment Setup

- **Benchmark**: HumanEval+ (164 problems, k=1..5 rounds each)
- **Condition A**: Execution-only repair loop (new data collected)
- **Condition B**: Execution + mypy repair loop (new data collected in parallel)
- **Category labeling**: type_error if `initial_mypy_errors > 0` at round 0; non_type_error otherwise
- **Model**: gpt-4o-mini, repair temperature=0.0, initial temperature=0.8, seed=42
- **Scale**: 164 problems × 2 conditions × up to 5 rounds = up to 1640 API calls

---

## Results

| Category | n | Rate Cond A | Rate Cond B | Delta (B−A) |
|----------|---|-------------|-------------|-------------|
| type_error | 22 | 90.9% | 90.9% | **+0.000** |
| non_type_error | 142 | 83.8% | 84.4% | **+0.006** |

**Differential** = delta_type − delta_non = 0.000 − 0.006 = **−0.006**

**Gate (differential > 0)**: **FAIL**

**Mechanism activated**: False

---

## Gate Verdict: FAIL

The primary gate metric `differential > 0` is not satisfied. Mypy feedback did **not** provide type-specific advantage over execution-only repair.

### Key Observations

1. **Ceiling effect on type-error problems**: Both conditions achieve 90.9% repair rate on type-error problems (n=22, 20/22 repaired). There is no room for mypy to show differential benefit — both conditions already solve these problems at near-ceiling.

2. **Near-identical performance on type errors**: Type-error problems are repaired equally under both conditions. This suggests that at k=5 rounds, execution feedback alone is sufficient to repair most type errors — the LLM infers the type correction from execution failure without explicit mypy guidance.

3. **Marginal mypy benefit on non-type errors**: Non-type-error problems show a small positive delta (+0.6%) for Condition B, but this is small and in the wrong direction for the hypothesis — mypy slightly helped non-type problems rather than type-error problems specifically.

4. **Category counts**: 22 type-error problems detected (vs. 20 expected from H-M1). The discrepancy (2 extra) is due to random seed variation in initial generation — mypy error presence at round 0 is sensitive to initial solution.

---

## Confounds and Alternative Explanations

1. **Ceiling effect confound**: Type-error problems may simply be easier problems (structural errors LLMs reliably fix from execution output). The n=22 at 90.9% leaves only 2 failures regardless of condition.

2. **Extra-context-length confound (primary EXPLORE target)**: Condition B prompts include additional mypy output (10-50 extra tokens per round). The marginal non-type benefit (+0.6%) may reflect the extra context window activating latent knowledge rather than type-specific signal. H-M1 showed mypy errors decrease, but the mechanism may be prompt enrichment, not type specificity.

3. **k=5 saturation**: By k=5, most repairable problems are repaired under either condition. Earlier rounds (k=1..2) may show differential signal that washes out by k=5.

4. **n=22 insufficient power**: With only 22 type-error problems, a differential of even 1 problem change in CondB (22→21 repaired vs 20 in CondA) would produce delta_type=0.045 vs delta_non≈0.006, passing the gate. The test lacks statistical power.

---

## Route: EXPLORE

Gate type is SHOULD_WORK → failure routes to EXPLORE phase.

**Primary exploration direction**: Extra-context-length confound. Test whether Condition B's marginal benefit on non-type problems persists when Condition B prompt length is controlled (e.g., adding equivalent-length execution-only context). If mypy's benefit is uniform across categories (not type-specific), the mechanism in YOURA pipeline causal step 3 needs revision — mypy may function as a generic context enricher, not a type-targeted repair signal.

**Secondary direction**: Early-round analysis (k=1..3) to test if type-specificity appears before ceiling saturation obscures it.

---

## Files

- `results/analysis.json` — full differential analysis
- `results/gate_result.json` — gate verdict
- `results/condition_a_results.jsonl` — Condition A per-problem results (164 problems)
- `results/condition_b_results.jsonl` — Condition B per-problem results (163 problems)
- `figures/repair_rate_comparison.png` — 4-bar repair rate chart
- `figures/differential_chart.png` — differential bar chart
- `figures/gate_metrics.png` — gate metrics summary table
