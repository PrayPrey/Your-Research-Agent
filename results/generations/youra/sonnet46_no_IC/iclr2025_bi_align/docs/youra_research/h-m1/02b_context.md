# Per-Hypothesis Context: H-M1

**Generated:** 2026-08-04 (JIT from 02b_verification_plan.md)
**Source:** docs/youra_research/02b_verification_plan.md §2.2

---

## Hypothesis Summary

- **ID:** H-M1
- **Type:** MECHANISM
- **Gate:** MUST_WORK
- **Prerequisites:** H-E1 (PASSED — r_partial=0.9851, p=1.69e-170)

**Statement:** In standardized OLS regression (LC_winrate ~ win_rate_std + avg_length_std) on AlpacaEval 2.0 N=222, the absolute standardized coefficient for capability (|β_win_rate_std|) exceeds that for verbosity (|β_avg_length_std|), indicating capability is the dominant predictor of length-debiased preference beyond verbosity.

---

## Experimental Setup

**Dataset:**
- Name: AlpacaEval 2.0 Leaderboard
- Type: standard
- Source: https://github.com/tatsu-lab/alpaca_eval
- Path: docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv
- Hypothesis Fit: N=222 models with win_rate, length_controlled_winrate, avg_length — full population for OLS analysis

**Model:**
- Name: N/A — statistical analysis
- Type: observational
- Hypothesis Fit: Reuses h-e1 data pipeline; adds StandardScaler normalization and OLS regression

---

## Verification Protocol

1. Apply StandardScaler to win_rate and avg_length
2. Run OLS: LC_winrate ~ win_rate_std + avg_length_std (statsmodels OLS)
3. IF VIF(win_rate_std, avg_length_std) < 5: compare |β_win_rate_std| vs |β_avg_length_std|
4. IF VIF ≥ 5: run Shapley-value dominance analysis (sklearn permutation importance)
5. Report OLS diagnostics: Breusch-Pagan test, QQ plot, residual plot

**Success Criteria:**
- Primary: |β_win_rate_std| > |β_avg_length_std|, both with p < 0.05
- Alternative (if VIF ≥ 5): Shapley(win_rate) > Shapley(avg_length)

---

## Previous Hypothesis Context (H-E1 Validation)

H-E1 PASSED with r_partial=0.9851, p=1.69e-170, n=223. Bootstrap CI 95%: [0.9760, 0.9876]. VIF: win_rate=1.764, avg_length=1.764 (no multicollinearity). This confirms:
- VIF < 5 → OLS beta comparison is valid (not Shapley fallback)
- Very strong partial correlation → |β_win_rate_std| >> |β_avg_length_std| expected
- Code infrastructure from h-e1 reusable (same CSV, same loading pipeline)
