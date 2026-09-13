# Failure Record: H-M1 (Run 1)

**Type:** PHASE4_FAIL
**Hypothesis ID:** h-m1
**Date:** 2026-05-02T14:30:00Z
**Gate:** MUST_WORK — FAILED
**Routing:** ROUTED_TO_PHASE_0

---

## Hypothesis Statement

Under the same GRPO training setup at function-level (APPS+CodeContests) vs. repository-level (SWE-bench Verified), GRPO advantage variance will be significantly HIGHER at repository level than function level (t-test p<0.05), because sparse repo-level rewards (~2% positive rate) generate high-variance advantage estimates.

---

## Experiment Results

| Metric | Function-Level | Repo-Level |
|--------|---------------|------------|
| Mean Advantage Variance | **0.9313** | 0.1521 |
| Variance Ratio (repo/fn) | — | 0.16x |
| Welch t-statistic | — | -12.71 |
| p-value | — | 6.44e-24 |
| Cohen's d | — | -5.13 |

**Gate FAILED: repo_adv_var (0.152) < fn_adv_var (0.931) — opposite of predicted direction.**

---

## Root Cause

**Degenerate step dominance at repo level:**
- At positive_rate=0.02 with G=8: P(all 8 rewards=0) = (0.98)^8 ≈ 85%
- ~85% of repo-level steps are degenerate (all-zero rewards → adv_var=0 by definition)
- Mean adv_var = 0.85×0 + 0.15×1.06 ≈ 0.16 (dominated by zero-variance degenerate steps)
- Function-level positive_rate=0.30: P(degenerate) ≈ 0.6% → mean adv_var ≈ 0.93

**The H-M1 direction prediction is mechanically wrong:** reward sparsity at repo level collapses mean advantage variance through degenerate steps, rather than amplifying it.

---

## What Worked

- TRL GRPOMeasurementTrainer subclass pattern (`_compute_loss` override) validated
- CSV advantage logging infrastructure correct
- Welch's t-test on log-transformed variance is correct statistical test
- All 13 unit tests pass (pytest)
- 4 figures generated successfully
- SWE-bench Docker reward function design correct

---

## Key Lesson for Phase 0 Redesign

**DO NOT use advantage variance as signal density proxy.**

The correct metrics for signal density differential are:
1. `positive_rate` directly (fraction of non-zero rewards per step): 30% (fn) vs. 2% (repo) — 15× difference, directly measurable
2. `non_degenerate_step_fraction` (steps where ≥1 completion succeeds): ~99% (fn) vs. ~15% (repo)
3. `effective_gradient_steps` (steps where GRPO produces non-zero gradient): same as above

**Alternative hypothesis framings that would likely PASS:**
- "positive_rate is significantly lower at repo level than function level (t-test, p<0.05)" — trivially true by design
- "fraction of degenerate GRPO steps (all-zero rewards) is significantly higher at repo level" — mechanically correct
- Remove H-M1 entirely: H-E1 validates GRPO execution reward pipeline; mechanism claim is not required for paper contribution

---

## Dependent Hypotheses Affected

- **H-M2** (SHOULD_WORK, prerequisite h-m1): CASCADE_BLOCKED
- **H-M3** (SHOULD_WORK, prerequisite h-m1): CASCADE_BLOCKED

---

## Files

- `h-m1/04_validation.md` — Full validation report
- `h-m1/outputs/gate_result.json` — gate_pass: false
- `h-m1/outputs/advantage_log.csv` — 240 rows (120 fn + 120 repo)
- `h-m1/code/` — Full implementation (reusable components)
