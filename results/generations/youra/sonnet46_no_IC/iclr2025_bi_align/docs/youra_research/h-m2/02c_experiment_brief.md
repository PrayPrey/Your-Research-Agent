# Experiment Design: h-m2

**Date:** 2026-08-04
**Author:** Anonymous
**Hypothesis Statement:** LC evaluator rewards capability-intrinsic properties proportionate to capability: ρ(win_rate_resid, lc_resid) > 0, p < 0.05, where residuals are obtained by regressing out avg_length from both win_rate and LC_winrate.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (SHOULD_WORK) Template** — Mechanistic confirmation via residualization. Tests FWL theorem equivalence and explicit residual capability signal.

---

## Workflow Status

**Verification State:** ACTIVE (IN_PROGRESS for h-m2)
**Prerequisites Satisfied:** H-E1 PASS (r_partial=0.9851, p=1.69e-170), H-M1 PASS (|β_win_rate|=21.34 >> |β_avg_length|=4.37)
**Gate Status:** SHOULD_WORK — failure documents mechanism complexity, does not invalidate H-E1/H-M1

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM (Causal Step 2)
- **Prerequisites:** H-E1 (COMPLETED/PASS), H-M1 (COMPLETED/PASS)

### Gate Condition

**SHOULD_WORK** — Primary: ρ(win_rate_resid, lc_resid) > 0 AND p < 0.05. Consistency: result within 0.02 of H-E1 r_partial=0.9851 (FWL theorem mathematical identity). Failure narrows scope but does not stop pipeline.

---

## Continuation Context

H-M2 is Causal Step 2 in the verification chain. Prior validated findings:
- **H-E1** (Spearman partial r=0.9851, p=1.69e-170, N=223): Capability independently predicts LC_winrate after controlling avg_length. VIF=1.764 (no multicollinearity issue). Bootstrap CI [0.9760, 0.9876] tightly bounds the effect.
- **H-M1** (|β_win_rate_std|=21.3391 >> |β_avg_length_std|=4.3720, R2=0.9628, p_win=4.58e-145): Capability dominates verbosity as predictor of LC preference. OLS path was active (VIF=1.764 < 5).

**Expected H-M2 outcome:** By the Frisch-Waugh-Lovell (FWL) theorem, regressing out avg_length from both win_rate and LC_winrate and computing Spearman correlation of the residuals is mathematically equivalent to the H-E1 partial correlation. Expected ρ ≈ 0.985, p << 0.05. This is mechanistic confirmation (explicit residual isolation) rather than mathematical redundancy.

### Previous Hypothesis Results (if applicable)

**H-E1 Key Results:**
- r_partial = 0.9851, p = 1.69e-170, n = 223
- Bootstrap 95% CI: [0.9760, 0.9876]
- VIF: win_rate=1.764, avg_length=1.764

**H-M1 Key Results:**
- |β_win_rate_std| = 21.3391, p = 4.58e-145
- |β_avg_length_std| = 4.3720
- R2 = 0.9628
- Breusch-Pagan: stat=8.946, p=0.011 (mild heteroscedasticity, non-critical)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "partial correlation residualization statistical analysis"**
- Archon KB is domain-specialized for diffusion models (image generation). No directly relevant results for statistical analysis methods.
- Fallback: Exa code search and pingouin documentation used as primary sources.

**Query 2: "Spearman correlation residuals regression confound control"**
- No relevant results from Archon KB (diffusion model content only).

**Note:** Archon KB does not contain statistical analysis / LLM evaluation methodology content. All implementation grounding from Exa (high-quality results obtained).

### Archon Code Examples

**Query: "scipy spearman bootstrap confidence interval"**
- No relevant code examples (Archon KB limited to diffusion models).
- All code implementation grounded in Exa results below.

### Exa GitHub Implementations

**Query 1: "partial correlation residualization scipy statsmodels python implementation"**

**Source 1: python-fiddle.com — Partial Correlation via Residuals Tutorial**
- URL: https://python-fiddle.com/tutorials/partial-correlation
- **Core pattern (residual approach):**
  ```python
  def residuals_after_regression(y, x):
      x_with_const = np.column_stack([np.ones(len(x)), x])
      coeffs, _, _, _ = np.linalg.lstsq(x_with_const, y, rcond=None)
      return y - x_with_const @ coeffs

  exercise_resid = residuals_after_regression(exercise, age)
  weight_resid   = residuals_after_regression(weight, age)
  r_partial, p_partial = pearsonr(exercise_resid, weight_resid)
  ```
- **Key insight:** Residual approach makes partial correlation concept explicit; orthogonal to control variable.

**Source 2: statsmodels regression plots — Partial Regression (Added Variable) Plots**
- URL: https://www.statsmodels.org/devel/examples/notebooks/generated/regression_plots.html
- **Key insight:** In partial regression, regress DV on all controls except Xk, regress Xk on controls. The residuals' regression slope equals the OLS coefficient for Xk. This is the FWL theorem in practice.

**Source 3: pgmpy.ci_tests.pearsonr — Conditional Independence via Partial Correlation**
- URL: https://pgmpy.org/_modules/pgmpy/ci_tests/pearsonr.html
- **Core implementation:**
  ```python
  design_matrix = np.column_stack([np.ones(n_samples), data.loc[:, Z].to_numpy()])
  X_coef = np.linalg.lstsq(design_matrix, data.loc[:, X], rcond=None)[0]
  Y_coef = np.linalg.lstsq(design_matrix, data.loc[:, Y], rcond=None)[0]
  residual_X = data.loc[:, X] - design_matrix @ X_coef
  residual_Y = data.loc[:, Y] - design_matrix @ Y_coef
  coef = np.corrcoef(residual_X, residual_Y)[0, 1]
  ```

**Source 4: pingouin.partial_corr documentation**
- URL: https://pingouin-stats.org/generated/pingouin.partial_corr.html
- **Key insight:** pingouin uses inverse covariance matrix method (faster); validates against ppcor R package. Already used in H-E1 and H-M1. H-M2 uses explicit residual method for mechanistic clarity.

**Query 2: "AlpacaEval leaderboard win_rate LC_winrate statistical analysis python pandas"**

**Source 5: tatsu-lab/alpaca_eval leaderboard CSV**
- URL: https://raw.githubusercontent.com/tatsu-lab/alpaca_eval/main/docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv
- **Columns confirmed:** name, length_controlled_winrate, win_rate, avg_length
- **Dataset confirmed accessible at:** docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv

**Source 6: tatsu-lab/alpaca_eval length_controlled.ipynb**
- URL: https://github.com/tatsu-lab/alpaca_eval/blob/main/notebooks/length_controlled.ipynb
- **Key insight:** win_rate Spearman correlation with Arena = 0.936. LC_winrate (LCAE) correlation with Arena = 0.98 (Dubois 2024). Verbosity gameability for win_rate = 21.3%, for LCAE = ~6%.

**Source 7: Dubois et al. 2024 — Length-Controlled AlpacaEval (arXiv 2404.04475)**
- URL: https://arxiv.org/html/2404.04475v2
- **Key insight:** LC correction via GLM predicting preferences based on length difference. LC_winrate answers counterfactual: "What would preference be if both outputs had same length?" This is the mechanism H-M2 tests residually.

### 🎯 Implementation Priority Assessment

**This is NOT a paper reproduction experiment.** H-M2 is a novel statistical analysis on pre-computed scores. No official implementation to reproduce — the experiment implements the residualization protocol described in H-M2 specification.

**Recommended Implementation Path:**
- Primary: Build on h-e1/h-m1 code infrastructure (already validates on this dataset); add explicit residualization step using scipy/numpy lstsq
- Fallback: Use pingouin.partial_corr with x_covar/y_covar for consistency check, then verify against manual residuals
- Justification: FWL theorem guarantees equivalence; explicit residuals provide mechanistic transparency for the paper

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear for this statistical analysis experiment. No complex DL architecture requiring Serena semantic analysis. The experiment is pure Python statistical code (~50 lines).

---

## Experiment Specification

### Dataset

**Name:** AlpacaEval 2.0 Leaderboard
**Version:** weighted_alpaca_eval_gpt4_turbo (GPT-4 Turbo as annotator)
**Type:** standard (pre-computed evaluation scores; real data)
**Source:** tatsu-lab/alpaca_eval GitHub (Dubois et al. 2024, arXiv 2404.04475)
**Cache Path:** docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv

**Statistics:**
- N = 222–223 models (after dropping rows with missing values in the 3 key columns)
- Columns used: `win_rate`, `length_controlled_winrate` (= LC_winrate), `avg_length`
- No train/val/test splits — cross-sectional observational analysis
- No preprocessing beyond dropna() on the 3 columns of interest

**Preprocessing:**
1. `df = pd.read_csv(csv_path)`
2. `df = df.dropna(subset=['win_rate', 'length_controlled_winrate', 'avg_length'])`
3. Verify N ≥ 200 after cleaning
4. No normalization required (residualization is scale-invariant)

**Synthetic data policy:** CONFIRMED COMPLIANT — real dataset (standard type), pre-computed from human preference annotations over 805 instruction-following tasks.

**Loading Information** (for Phase 4 download):
- Method: pandas.read_csv (local file)
- Identifier: `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv`
- Code: `df = pd.read_csv('docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv')`

### Models

#### Baseline Model

**Architecture:** N/A — no ML model training
**Type:** observational statistical analysis
**Description:** Analysis operates on pre-computed win_rate and LC_winrate scores from AlpacaEval 2.0 leaderboard. "Baseline" in this context is the null model: ρ(win_rate_resid, lc_resid) = 0.

**Baseline comparison:**
- Null: No residual correlation (verbosity fully explains LC preference)
- H-E1 result: r_partial = 0.9851 (expected to match via FWL theorem)

**Loading Information** (for Phase 4 download):
- Method: N/A (no model download required)
- Identifier: N/A
- Code: N/A

#### Proposed Model

**Architecture:** Explicit residualization procedure (FWL mechanistic confirmation)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Residual Capability Signal Confirmation (H-M2)
# Tests FWL theorem: ρ(win_rate_resid, lc_resid) ≡ r_partial(H-E1)
# Based on: pgmpy.ci_tests.pearsonr, python-fiddle residual tutorial

import numpy as np
import pandas as pd
from scipy import stats

def regress_out(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Regress x out of y; return residuals (orthogonal to x)."""
    X = np.column_stack([np.ones(len(x)), x])
    coefs, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ coefs

def residual_capability_signal(df: pd.DataFrame) -> dict:
    """
    H-M2: Confirm residual capability signal after removing avg_length.
    Args:
        df: DataFrame with win_rate, length_controlled_winrate, avg_length
    Returns:
        dict with rho, p_value, bootstrap_ci, fwl_delta
    """
    win = df['win_rate'].values
    lc  = df['length_controlled_winrate'].values
    avg_len = df['avg_length'].values

    # Regress out avg_length from both variables
    win_resid = regress_out(win, avg_len)
    lc_resid  = regress_out(lc,  avg_len)

    # Spearman correlation of residuals
    rho, p_val = stats.spearmanr(win_resid, lc_resid)

    # Bootstrap CI (1000 resamples, seed=42)
    rng = np.random.default_rng(42)
    n = len(win_resid)
    boot_rhos = [stats.spearmanr(win_resid[idx := rng.integers(0, n, n)],
                                  lc_resid[idx])[0] for _ in range(1000)]
    ci = (np.percentile(boot_rhos, 2.5), np.percentile(boot_rhos, 97.5))

    return {'rho': rho, 'p_value': p_val, 'bootstrap_ci_95': ci}
```

### Training Protocol

**Note:** This is a statistical analysis study — no model training. "Protocol" describes the analysis execution plan.

**Optimizer:** N/A
**Learning Rate:** N/A
**Batch Size:** N/A
**Epochs:** N/A
**Loss:** N/A

**Analysis Execution Protocol:**
1. Load CSV: `pd.read_csv(...)`, dropna on 3 columns, verify N ≥ 200
2. Compute residuals: regress avg_length out of win_rate → `win_rate_resid`; regress avg_length out of LC_winrate → `lc_resid`
3. Compute Spearman ρ(win_rate_resid, lc_resid) using `scipy.stats.spearmanr`
4. Bootstrap CI: 1000 resamples, random_state=42
5. Consistency check: compare ρ against H-E1 r_partial (0.9851); flag if |Δ| > 0.02
6. Record FWL delta = |ρ_H-M2 - r_partial_H-E1| as diagnostic
7. Generate visualizations (scatter plot of residuals + regression line + diagnostic)

**Seeds:** random_state=42 (for bootstrap only; main analysis is deterministic)
**Runtime:** < 1 second (CPU-only, N=222 data points)

**Libraries:**
```
numpy, pandas, scipy.stats, statsmodels.api, pingouin, matplotlib
```

### Evaluation

**Primary Metrics:**
- **rho (Spearman ρ):** Spearman correlation of win_rate_resid vs lc_resid; gate requires > 0 AND p < 0.05
- **p_value:** Two-tailed p-value for Spearman ρ; gate requires p < 0.05
- **Bootstrap 95% CI:** Must exclude 0 (consistency with H-E1)
- **FWL Delta:** |ρ_H-M2 − r_partial_H-E1|; expected < 0.02 (mechanistic consistency)

**Success Criteria (SHOULD_WORK gate):**
- Primary: ρ > 0 AND p < 0.05
- Consistency: |ρ − 0.9851| < 0.02 (FWL theorem verification)

**Expected performance (based on H-E1 results):**
- Expected ρ ≈ 0.985 (mathematically equivalent via FWL)
- Expected p ≈ 1.69e-170 (same data, mathematically equivalent test)
- Expected FWL delta < 0.005

**Failure detection:**
- IF ρ ≤ 0 OR p ≥ 0.05: SHOULD_WORK gate fails; document mechanism complexity
- IF |ρ − r_partial_H-E1| > 0.02: Unexpected implementation discrepancy; debug residualization code

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical correlation analysis
- Library: scipy.stats.spearmanr, numpy.percentile (bootstrap)
- Code: `rho, p = scipy.stats.spearmanr(win_resid, lc_resid)`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart with ρ_H-M2 vs expected (H-E1 r_partial), p-value comparison

#### Additional Figures (LLM Autonomous)

Based on the residualization nature of H-M2:
1. **Scatter Plot:** win_rate_resid vs lc_resid with regression line and Spearman ρ annotation
2. **Residual Distribution Plots:** Histogram of win_rate_resid and lc_resid side by side (verify approximate normality of residuals)
3. **Partial Regression Plot (statsmodels):** Added-variable plot for win_rate controlling avg_length → visual of what H-M2 is testing
4. **FWL Consistency Check Plot:** Scatter of [H-E1 r_partial vs H-M2 ρ] comparison with diagonal line (should lie on diagonal)
5. **Bootstrap Distribution:** Histogram of 1000 bootstrap ρ values with 95% CI marked

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. ρ(win_rate_resid, lc_resid) > 0 AND p < 0.05

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Archon KB Result:** No domain-relevant content found. Archon KB contains diffusion model content only. All implementation research sourced from Exa.

### B. GitHub Implementations (Exa)

**Repository 1: python-fiddle.com — Partial Correlation via Residuals**
- URL: https://python-fiddle.com/tutorials/partial-correlation
- Query: "partial correlation residualization scipy statsmodels python implementation"
- Relevance: Canonical residual-based partial correlation implementation
- Key Code Used:
  ```python
  def residuals_after_regression(y, x):
      x_with_const = np.column_stack([np.ones(len(x)), x])
      coeffs, _, _, _ = np.linalg.lstsq(x_with_const, y, rcond=None)
      return y - x_with_const @ coeffs
  ```
- Used For: Core `regress_out()` function in `core_mechanism_pseudocode`

**Repository 2: pgmpy.ci_tests.pearsonr**
- URL: https://pgmpy.org/_modules/pgmpy/ci_tests/pearsonr.html
- Query: "partial correlation residualization scipy statsmodels python implementation"
- Relevance: Production-quality conditional independence test via residualization
- Key Code Used:
  ```python
  design_matrix = np.column_stack([np.ones(n_samples), data.loc[:, Z].to_numpy()])
  X_coef = np.linalg.lstsq(design_matrix, data.loc[:, X], rcond=None)[0]
  residual_X = data.loc[:, X] - design_matrix @ X_coef
  ```
- Used For: Validation of residualization implementation pattern

**Repository 3: statsmodels regression plots**
- URL: https://www.statsmodels.org/devel/examples/notebooks/generated/regression_plots.html
- Query: "partial correlation residualization scipy statsmodels python implementation"
- Relevance: Added-variable (partial regression) plots; FWL theorem visualization
- Used For: Visualization step (partial regression plot); confirms H-M2 = FWL visual

**Repository 4: tatsu-lab/alpaca_eval leaderboard CSV**
- URL: https://raw.githubusercontent.com/tatsu-lab/alpaca_eval/main/docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv
- Query: "AlpacaEval leaderboard win_rate LC_winrate statistical analysis python pandas"
- Relevance: Exact dataset used in experiment; columns confirmed
- Used For: Dataset specification; confirms local cache path is correct

**Repository 5: tatsu-lab/alpaca_eval length_controlled.ipynb**
- URL: https://github.com/tatsu-lab/alpaca_eval/blob/main/notebooks/length_controlled.ipynb
- Query: "AlpacaEval leaderboard win_rate LC_winrate statistical analysis python pandas"
- Relevance: Author's own analysis of win_rate vs LC_winrate; Spearman Arena correlation
- Key data: win_rate Spearman Arena=0.936; LC_winrate Arena=0.98; verbosity gameability 21% vs 6%
- Used For: Background for expected residual correlation magnitude

**Repository 6: Dubois et al. 2024 — arXiv 2404.04475**
- URL: https://arxiv.org/html/2404.04475v2
- Query: "AlpacaEval leaderboard win_rate LC_winrate statistical analysis"
- Relevance: Source paper for LC_winrate construction via GLM; H-M2 tests residual of THIS correction
- Used For: Understanding the mechanism that H-M2 confirms (LC GLM corrects for length → residual reflects capability-intrinsic quality)

**Repository 7: pingouin.partial_corr documentation**
- URL: https://pingouin-stats.org/generated/pingouin.partial_corr.html
- Query: "partial correlation residualization scipy statsmodels python implementation"
- Relevance: Library used in H-E1 for partial_corr; H-M2 uses explicit residuals for mechanistic clarity
- Used For: Consistency check (pingouin result should match explicit residual result)

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. The experiment is pure statistical Python (~50 lines), no complex DL architecture requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Reports for H-E1 and H-M1

**H-E1 (docs/youra_research/h-e1/04_validation.md):**
- r_partial = 0.9851 ← target for FWL consistency check in H-M2
- p = 1.69e-170
- VIF = 1.764 (confirms no collinearity concern)
- Bootstrap CI: [0.9760, 0.9876]

**H-M1 (docs/youra_research/h-m1/04_validation.md):**
- R2 = 0.9628 (OLS model quality)
- Both predictors significant (p_win = 4.58e-145, p_len significant)
- Code infrastructure established and validated

**Reused Components:**
- CSV loading + dropna pipeline
- VIF computation code
- Bootstrap CI function
- Output figure directory structure

**Why Reused:** Ensures controlled comparison — only the analysis step changes (residualization vs partial_corr vs OLS). Same N, same dataset, same preprocessing.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Validated from H-E1/H-M1 | 02b_context.md + h-e1/04_validation.md |
| CSV path | Exa GitHub (tatsu-lab) | Source B.4 |
| Core residualization code | Exa (python-fiddle, pgmpy) | Sources B.1, B.2 |
| FWL theorem rationale | statsmodels docs | Source B.3 |
| Expected ρ value | H-E1 validation result | Source D |
| Bootstrap CI method | H-E1/H-M1 established pattern | Source D |
| Library choices (scipy, numpy) | All Exa sources | Sources B.1–B.7 |
| Visualization design | statsmodels partial regression | Source B.3 |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-04

### Workflow History for This Hypothesis

| Event | Timestamp | Details |
|-------|-----------|---------|
| H-M2 set to IN_PROGRESS | 2026-08-04T08:39:18 | External loop starting Phase 2C → 3 → 4 |
| Phase 2C experiment design started | 2026-08-04 | Unattended mode |
| Phase 2C experiment design completed | 2026-08-04 | This file |

---

*MCP Tools Used: Exa (GitHub/Code Search — 2 queries, 7 sources). Archon KB not domain-relevant for statistical analysis. Serena not required (pure statistical Python).*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
