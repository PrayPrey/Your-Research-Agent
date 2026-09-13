# Phase 2B Context: H-E1

**Generated:** 2026-08-04 (JIT from 02b_verification_plan.md)
**Hypothesis ID:** h-e1
**Type:** EXISTENCE
**Gate:** MUST_WORK

---

## Hypothesis Statement

Under AlpacaEval 2.0 N=222 models with confirmed columns (win_rate, length_controlled_winrate, avg_length), if model capability (win_rate) is higher, then length-debiased preference (LC_winrate) is also higher after controlling for verbosity (avg_length), because capability has a length-independent quality component (desirability channel).

**Formally:** ρ(win_rate, LC_winrate | avg_length) > 0, p < 0.05, |r_partial| ≥ 0.15

---

## Experimental Setup

**Dataset:**
- Name: AlpacaEval 2.0 Leaderboard
- Type: standard
- Source: https://github.com/tatsu-lab/alpaca_eval
- Path: docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv
- Columns: name, length_controlled_winrate, win_rate, avg_length
- N: 222 models
- Hypothesis Fit: Pre-computed evaluation scores for all variables; no model training needed; confirmed accessible

**Model:**
- Name: N/A — statistical analysis study
- Type: observational analysis
- Source: AlpacaEval 2.0 CSV provides pre-computed scores for 222 LLMs
- Hypothesis Fit: No model needed; analysis operates on leaderboard data

---

## Variables

- **Independent:** win_rate (continuous; human preference win fraction; capability proxy)
- **Dependent:** length_controlled_winrate (continuous; GLM-debiased preference score)
- **Controlled:** avg_length (continuous; mean response token length; verbosity confound)

---

## Verification Protocol

1. Load AlpacaEval 2.0 CSV; drop missing values; verify N ≥ 200 after cleaning.
2. Compute VIF(win_rate, avg_length) as diagnostic for H-M1 gate design.
3. Run `pingouin.partial_corr(x='win_rate', y='length_controlled_winrate', covar='avg_length', method='spearman')`.
4. Bootstrap CI (1000 resamples) for Spearman correlations as robustness check.
5. Replicate on N=58 typed subset for comparison with h-m1 prior results.

---

## Success Criteria

- **Primary:** r_partial > 0 AND p < 0.05 (two-tailed) AND |r_partial| ≥ 0.15
- **Secondary:** Bootstrap 95% CI for r_partial excludes 0

**Gate:** MUST_WORK — if H-E1 fails: STOP, route to Phase 0 with documented failure mode.

---

## Prerequisites

None (foundation hypothesis)

---

## Baseline Methods (From Phase 2B)

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|-----------------|
| h-m1: Mann-Whitney on RLHF vs SFT Δ | p=0.662, Cohen's d=0.136 (FAIL) | AlpacaEval 2.0 N=58 typed subset | Categorical training_type too coarse |
| Dubois 2024 GLM length control | ρ(win_rate, LC_winrate) ≈ 0.94 | AlpacaEval 2.0 N=222 | Documents correlation but does not test partial correlation |
| Null model (no capability effect) | H0: ρ = 0 | N/A | Verbosity-only explanation |

---

## Key Assumptions

- A1: win_rate is a valid proxy for model capability
- A2: VIF(win_rate, avg_length) < 5
- A3: Capability-Δ relationship generalizes from N=58 to N=222
- A4: AlpacaEval 2.0 dataset is representative
- A5: Directional prediction holds: high capability → smaller |Δ|
