# Phase 2B Context: H-M2

**Hypothesis ID:** h-m2
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Generated:** 2026-08-04 (JIT from 02b_verification_plan.md)

---

## Hypothesis Statement

LC evaluator rewards capability-intrinsic properties proportionate to capability: ρ(win_rate_residual, lc_resid) > 0, p < 0.05, where residuals are obtained by regressing out avg_length from both win_rate and LC_winrate.

**Full Statement (from 02b_verification_plan.md §2.2):**

High-capability models (high win_rate) receive higher LC_winrate not merely because of length effects but because the LC GLM correction reveals a residual capability signal: ρ(win_rate_residual, LC_winrate_residual) > 0 after partialling out avg_length from both variables. This confirms the LC evaluator rewards capability-intrinsic properties.

---

## Experimental Setup (from Phase 2A via Phase 2B)

### Dataset

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | AlpacaEval 2.0 Leaderboard (standard) | N=222 models with win_rate, length_controlled_winrate, avg_length confirmed accessible. Single-CSV design. |
| **Path** | docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv | Already downloaded, verified in h-e1/h-m1 pipeline |
| **Type** | standard | Pre-computed evaluation scores; no model training required |

### Model

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Model** | N/A — statistical analysis study | No model training or inference required |
| **Analysis** | Observational; operates on pre-computed AlpacaEval 2.0 scores | Reuses h-e1/h-m1 code infrastructure |

---

## Variables

- **Independent:** win_rate residualized on avg_length (win_rate_resid)
- **Dependent:** LC_winrate residualized on avg_length (lc_resid)
- **Controlled:** avg_length (regressed out from both IV and DV)

---

## Verification Protocol

1. Regress win_rate on avg_length; save residuals (win_rate_resid)
2. Regress LC_winrate on avg_length; save residuals (lc_resid)
3. Compute Spearman ρ(win_rate_resid, lc_resid) with bootstrap CI (1000 resamples)
4. Consistency check: result should be numerically close to H-E1 r_partial (within 0.02)
5. Report as mechanistic confirmation of residual capability signal

---

## Success Criteria

- **Primary:** ρ(win_rate_resid, lc_resid) > 0 AND p < 0.05
- **Consistency:** Numerically close to H-E1 r_partial (within 0.02)

---

## Prerequisites

- **H-E1:** COMPLETED (PASS) — r_partial=0.9851, p=1.69e-170
- **H-M1:** COMPLETED (PASS) — |β_win_rate_std|=21.34 >> |β_avg_length_std|=4.37

---

## Gate Condition

**SHOULD_WORK** — failure documents mechanism complexity, does not invalidate H-E1 or H-M1.

---

## Baseline Methods

| Method | Performance | Dataset | Limitation |
|--------|-------------|---------|------------|
| H-E1 partial correlation | r_partial=0.9851, p=1.69e-170 | AlpacaEval N=222 | Tests existence but not residual confirmation |
| H-M1 OLS betas | |β_win_rate|=21.34 >> |β_avg_length|=4.37 | AlpacaEval N=222 | Tests dominance but not residual isolation |
| Dubois 2024 GLM | ρ(win_rate, LC_winrate)≈0.94 | AlpacaEval 2.0 | Documents raw correlation, no residual confirmation |

---

## Prior Context (From H-E1 + H-M1 Validation)

- **H-E1:** Spearman partial r=0.9851, p=1.69e-170, Bootstrap CI [0.9760, 0.9876], VIF=1.764 (no multicollinearity)
- **H-M1:** |β_win_rate_std|=21.3391 vs |β_avg_length_std|=4.3720, R2=0.9628
- **Key insight:** VIF=1.764 means collinearity is not a concern; OLS residualization is clean
- **Expected H-M2 result:** ρ(win_rate_resid, lc_resid) ≈ 0.985 (mathematically equivalent to H-E1 r_partial via FWL theorem)

---

## Dependency Chain

```
H-E1 (MUST_WORK, PASS) → H-M1 (MUST_WORK, PASS) → H-M2 (SHOULD_WORK, IN_PROGRESS)
```

---

## Key Assumptions

| ID | Assumption | Status |
|----|------------|--------|
| A1 | win_rate is valid capability proxy | Validated in H-E1/H-M1 |
| A2 | VIF(win_rate, avg_length) < 5 | CONFIRMED: VIF=1.764 |
| A3 | Partial correlation via residuals = partial correlation directly | Mathematical identity (FWL theorem) — H-M2 is explicit confirmation |

---

## Research Gap

H-M2 mechanistically confirms WHY H-E1 partial correlation holds: the LC evaluator itself rewards capability-intrinsic properties (the portion of win_rate unexplained by verbosity independently predicts the portion of LC_winrate unexplained by verbosity). This goes beyond correlation to explicit residual confirmation.
