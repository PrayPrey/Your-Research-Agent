# Experiment Design: h-m1

**Date:** 2026-08-04
**Author:** Anonymous
**Hypothesis Statement:** In standardized OLS (LC_winrate ~ win_rate_std + avg_length_std) on N=222, |β_win_rate_std| > |β_avg_length_std| (or Shapley(win_rate) > Shapley(avg_length) if VIF ≥ 5). Capability dominates verbosity as predictor of LC preference.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** — Tests causal dominance via standardized OLS + VIF-contingent Shapley fallback.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 PASSED (r_partial=0.9851, p=1.69e-170, VIF=1.764)
**Gate Status:** MUST_WORK — |β_win_rate_std| > |β_avg_length_std| required

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (MUST_WORK — PASSED)

### Gate Condition
MUST_WORK — if H-M1 fails (|β_win_rate_std| ≤ |β_avg_length_std| AND Shapley(win_rate) ≤ Shapley(avg_length)), document as scope limitation; H-E1 result remains valid.

---

## Continuation Context

**From H-E1 Validation (04_validation.md):**
- r_partial = 0.9851, p = 1.69e-170, n = 223
- Bootstrap 95% CI: [0.9760, 0.9876]
- VIF: win_rate = 1.764, avg_length = 1.764 (well below threshold of 5.0)
- **Critical implication:** VIF < 5 confirmed → OLS beta coefficient comparison is valid; Shapley fallback NOT required (though implemented as contingency)
- **Expected direction:** Given r_partial = 0.9851, standardized OLS should show overwhelming β_win_rate_std dominance

### Previous Hypothesis Results (if applicable)
H-E1: existence confirmed at r_partial = 0.9851. OLS code infrastructure reusable (same CSV, same loading pipeline). StandardScaler and OLS are additive steps on top of h-e1's data loading.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Archon KB contains only diffusion-model content (no relevance to statistical regression analysis).

**Query 1: standardized OLS regression coefficient dominance analysis**
- No relevant results (max similarity < 0.35; all HuggingFace diffusers content)

**Query 2: VIF collinearity Shapley value feature importance statsmodels**
- No relevant results (max similarity < 0.34; all diffusion-model content)

**Query 3: statsmodels OLS standardized regression sklearn permutation importance**
- No relevant results (max similarity < 0.37; diffusion/PyTorch content)

*Note: Archon KB is domain-specific to prior pipeline work (diffusion models). Statistical analysis implementation grounded in Exa search results below.*

### Archon Code Examples

No relevant code examples found in Archon KB for OLS regression or dominance analysis.

---

### Exa GitHub Implementations

**Query 1: statsmodels OLS standardized coefficients VIF Python regression**

**Source 1: statsmodels.stats.outliers_influence.variance_inflation_factor** (official docs)
- **URL:** https://www.statsmodels.org/dev/generated/statsmodels.stats.outliers_influence.variance_inflation_factor.html
- **Relevance:** Official API for VIF computation — exact function for H-M1 collinearity diagnostic
- **Key API:**
  ```python
  from statsmodels.stats.outliers_influence import variance_inflation_factor
  # standardize=True (default in v0.15+) ensures numerical stability
  vif = variance_inflation_factor(X.values, idx)
  ```
- **VIF threshold:** > 5 = highly collinear; < 5 = safe for beta comparison
- **Key insight:** standardize=True parameter added in v0.15 for numerical stability — use this

**Source 2: statsmodels.regression.linear_model.OLS** (official)
- **URL:** https://www.statsmodels.org/dev/generated/statsmodels.regression.linear_model.OLS.html
- **Relevance:** OLS regression engine for standardized coefficient extraction
- **Key API:**
  ```python
  import statsmodels.api as sm
  X_with_const = sm.add_constant(X_std)
  model = sm.OLS(y, X_with_const)
  results = model.fit()
  # results.params → standardized coefficients (intercept, β_win_rate_std, β_avg_length_std)
  # results.pvalues → p-values for each coefficient
  ```

**Source 3: StackOverflow — VIF with OLS Results** (statsmodels community)
- **URL:** https://stackoverflow.com/questions/42258241/vif-by-coef-in-ols-regression-results-python
- **Relevance:** Complete pattern for VIF computation from OLS model exog matrix
- **Key Code:**
  ```python
  from statsmodels.stats.outliers_influence import variance_inflation_factor
  variables = lm.model.exog
  vif = [variance_inflation_factor(variables, i) for i in range(variables.shape[1])]
  vif_df = pd.DataFrame({'variables': lm.model.exog_names, 'vif': vif})
  ```

**Query 2: sklearn permutation_importance Shapley dominance regression Python**

**Source 4: sklearn.inspection.permutation_importance** (official scikit-learn docs)
- **URL:** https://scikit-learn.org/stable/modules/generated/sklearn.inspection.permutation_importance.html
- **Relevance:** Official permutation importance API — fallback dominance metric when VIF ≥ 5
- **Key API:**
  ```python
  from sklearn.inspection import permutation_importance
  from sklearn.linear_model import LinearRegression
  model = LinearRegression().fit(X_std, y)
  result = permutation_importance(model, X_std, y, n_repeats=30, random_state=42)
  # result.importances_mean → [importance_win_rate_std, importance_avg_length_std]
  ```
- **Note:** Use R² as scoring metric; compare importances_mean[0] (win_rate) vs importances_mean[1] (avg_length)

**Source 5: AlpacaEval Official Repository** (tatsu-lab)
- **URL:** https://github.com/tatsu-lab/alpaca_eval
- **Relevance:** Confirms dataset column names and confirms win_rate = mean(preferences)*100, LC_winrate = GLM-corrected
- **Key note:** LCAE increases correlation with ChatBot Arena from 0.93 to 0.98; length gameability reduced 3x

**Source 6: Dubois 2024 — Length-Controlled AlpacaEval** (arXiv 2404.04475)
- **URL:** https://arxiv.org/html/2404.04475v2
- **Relevance:** Defines the GLM that produces LC_winrate; documents that LC correction removes length bias while preserving quality signal
- **Key insight:** LC_winrate residualizes out length via GLM — so β_win_rate_std in OLS on LC_winrate tests what quality signal REMAINS after length correction

**Serena Analysis Needed:** false — statsmodels and sklearn APIs are fully documented; no complex proprietary code requiring semantic analysis

---

### 🎯 Implementation Priority Assessment

**CRITICAL: This is a statistical observational study, not a paper reproduction experiment.**

This experiment performs original statistical analysis on AlpacaEval 2.0 leaderboard CSV. No "author's official implementation" applies. Analysis builds directly on h-e1 infrastructure.

**Recommended Implementation Path:**
- Primary: `statsmodels.OLS` with `sklearn.StandardScaler` for standardized regression (β comparison)
- Fallback (VIF ≥ 5): `sklearn.inspection.permutation_importance` on `LinearRegression` for dominance
- **VIF from h-e1:** win_rate=1.764, avg_length=1.764 → OLS beta path confirmed valid (fallback precautionary only)
- Justification: StandardScaler + OLS is canonical for standardized regression; permutation_importance is model-agnostic dominance measure

### Code Analysis (Serena MCP)

*Skipped* — statsmodels and sklearn APIs are fully documented with runnable examples. No complex implementation requiring semantic code analysis.

---

## Experiment Specification

### Dataset

**Name:** AlpacaEval 2.0 Leaderboard (weighted_alpaca_eval_gpt4_turbo_leaderboard.csv)
**Type:** standard (real leaderboard data, pre-computed by tatsu-lab team)
**Source:** https://github.com/tatsu-lab/alpaca_eval

**Statistics:**
- N = 222 models (full leaderboard population)
- Columns used: `win_rate`, `length_controlled_winrate`, `avg_length`
- No train/val/test split — full dataset is the analysis population
- Expected N_clean ≥ 200 after dropping rows with missing values
- Reuses h-e1 loaded and cleaned DataFrame (same pipeline)

**Preprocessing:**
1. Load CSV with `pandas.read_csv()` (same as h-e1)
2. Drop rows with NaN in {win_rate, length_controlled_winrate, avg_length}
3. Assert N_clean ≥ 200
4. **NEW:** Apply `sklearn.preprocessing.StandardScaler` to win_rate and avg_length
5. OLS requires intercept — add constant via `sm.add_constant()`

**Synthetic Data Policy:** CONFIRMED REAL DATA — AlpacaEval 2.0 leaderboard is publicly available dataset of pre-computed LLM evaluation scores. Type = standard. NOT synthetic.

**Loading Information** (for Phase 4 download):
- Method: local CSV (already cached in repository from h-e1)
- Identifier: `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv`
- Code:
  ```python
  import pandas as pd
  from sklearn.preprocessing import StandardScaler
  
  df = pd.read_csv('docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv')
  df = df.dropna(subset=['win_rate', 'length_controlled_winrate', 'avg_length'])
  assert len(df) >= 200, f"Expected ≥200 models, got {len(df)}"
  
  scaler = StandardScaler()
  df['win_rate_std'] = scaler.fit_transform(df[['win_rate']])
  df['avg_length_std'] = scaler.fit_transform(df[['avg_length']])
  ```

---

### Models

#### Baseline Model

**Architecture:** Verbosity-only null model — LC_winrate ~ avg_length_std only
**Description:** Baseline hypothesis that verbosity alone (avg_length) predicts LC preference. Operationalized as OLS regression with only avg_length_std as predictor.
**Operationalization:**
```python
import statsmodels.api as sm
X_baseline = sm.add_constant(df[['avg_length_std']])
baseline_model = sm.OLS(df['length_controlled_winrate'], X_baseline).fit()
# β_avg_length_std from baseline_model = verbosity-only predictor weight
```

**Loading Information** (for Phase 4 download):
- Method: N/A — statistical null model, no pretrained weights to load
- Identifier: N/A
- Code: N/A (computed from data directly)

---

#### Proposed Model

**Architecture:** Full standardized OLS — LC_winrate ~ win_rate_std + avg_length_std

**Core Mechanism Implementation:**

```python
# Core Mechanism: Standardized OLS Dominance Analysis (H-M1)
# Based on: statsmodels OLS + sklearn StandardScaler (sources 1-3 above)
# Input: AlpacaEval 2.0 DataFrame (N≥200), StandardScaler-normalized predictors
# Output: dominance verdict (win_rate vs avg_length) with VIF-contingent path

import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.inspection import permutation_importance
from statsmodels.stats.outliers_influence import variance_inflation_factor

def compute_h_m1_dominance(df: pd.DataFrame) -> dict:
    """
    Test H-M1: |β_win_rate_std| > |β_avg_length_std| in standardized OLS.
    VIF-contingent: if VIF ≥ 5, fall back to permutation importance.
    """
    scaler = StandardScaler()
    X_std = scaler.fit_transform(df[['win_rate', 'avg_length']])
    y = df['length_controlled_winrate'].values

    # VIF diagnostic (reuse from h-e1: expected ~1.764 for both)
    X_sm = sm.add_constant(X_std)
    vif_win = variance_inflation_factor(X_sm, 1)   # win_rate_std
    vif_len = variance_inflation_factor(X_sm, 2)   # avg_length_std

    if max(vif_win, vif_len) < 5:
        # PRIMARY PATH: OLS beta comparison (VIF < 5 confirmed from h-e1)
        model = sm.OLS(y, X_sm).fit()
        beta_win = abs(model.params[1])     # |β_win_rate_std|
        beta_len = abs(model.params[2])     # |β_avg_length_std|
        p_win    = model.pvalues[1]
        p_len    = model.pvalues[2]
        dominance_path = "OLS_beta"
        passes_gate = (beta_win > beta_len) and (p_win < 0.05)
        return {"path": dominance_path, "beta_win": beta_win, "beta_len": beta_len,
                "p_win": p_win, "p_len": p_len, "vif_win": vif_win, "vif_len": vif_len,
                "passes_gate": passes_gate, "r2": model.rsquared}
    else:
        # FALLBACK PATH: permutation importance (Shapley proxy)
        lr = LinearRegression().fit(X_std, y)
        perm = permutation_importance(lr, X_std, y, n_repeats=30, random_state=42)
        imp_win = perm.importances_mean[0]  # win_rate importance
        imp_len = perm.importances_mean[1]  # avg_length importance
        dominance_path = "permutation_importance"
        passes_gate = imp_win > imp_len
        return {"path": dominance_path, "imp_win": imp_win, "imp_len": imp_len,
                "vif_win": vif_win, "vif_len": vif_len, "passes_gate": passes_gate}
```

---

### Training Protocol

**Note:** This is a statistical observational study — no model training, no optimizer, no epochs. The "protocol" is the statistical analysis pipeline, extending h-e1.

**Analysis Pipeline (Sequential):**
1. Data loading and quality check — reuse h-e1 pipeline (same CSV)
2. StandardScaler normalization of win_rate and avg_length
3. VIF diagnostic — from h-e1: expected ~1.764 for both; confirms OLS beta path
4. PRIMARY: Standardized OLS (LC_winrate ~ win_rate_std + avg_length_std)
   - Report: β_win_rate_std, β_avg_length_std, p-values, R²
   - Dominance check: |β_win_rate_std| > |β_avg_length_std|
5. OLS DIAGNOSTICS:
   - Breusch-Pagan test (heteroscedasticity)
   - Q-Q plot of residuals (normality check)
   - Residual vs fitted plot
6. FALLBACK (if VIF ≥ 5): sklearn permutation_importance (n_repeats=30, seed=42)
7. Report: dominance verdict, path taken (OLS or permutation), R², diagnostics

**Hyperparameters (Statistical):**
- alpha = 0.05 (significance threshold for p-values)
- VIF_threshold = 5.0 (OLS vs fallback gate)
- n_repeats = 30 (permutation importance repeats, if needed)
- random_state = 42
- Scaler: StandardScaler (zero mean, unit variance)

**Seeds:** 1 (seed=42 for permutation importance only)

> ⚠️ **MECHANISM (PoC)**: Single analysis pipeline. No training loop.

**Continuation from H-E1:**
- VIF confirmed: win_rate=1.764, avg_length=1.764 → OLS beta path is valid
- h-e1 code infrastructure reused for data loading

---

### Evaluation

**Primary Metrics:**
- `beta_win_rate_std`: standardized OLS coefficient for win_rate_std
- `beta_avg_length_std`: standardized OLS coefficient for avg_length_std
- `p_win`, `p_len`: p-values for each coefficient
- `r2`: OLS R² (model fit quality)
- `vif_win`, `vif_len`: VIF values (from h-e1: expected ~1.764)

**Success Criteria (MUST_WORK gate):**
- PRIMARY (OLS path): |β_win_rate_std| > |β_avg_length_std| AND p_win < 0.05
- FALLBACK (permutation path): Shapley(win_rate) > Shapley(avg_length)
- Both paths: dominance direction consistent

**Expected Baseline Performance (from h-e1 + literature):**
- VIF ~ 1.764 (confirmed from h-e1) → OLS beta path active
- r_partial = 0.9851 from h-e1 → very high → |β_win_rate_std| >> |β_avg_length_std| strongly expected
- Dubois 2024: LC_winrate GLM corrects for length → LC_winrate captures quality independent of length → β_win should dominate
- Expected: |β_win_rate_std| ≈ 0.8-0.99, |β_avg_length_std| ≈ 0.01-0.20

**Task Type:** statistical dominance analysis (no classification/regression model training)
**Library:** statsmodels (OLS, VIF), sklearn (StandardScaler, permutation_importance), scipy
**Metrics Loading Code:**
```python
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LinearRegression
```

---

### Visualization Requirements

#### Required Figure (Mandatory)
- **Dominance Comparison**: Bar chart showing |β_win_rate_std| vs |β_avg_length_std| with p-value annotations

#### Additional Figures (LLM Autonomous)

Based on this standardized regression / dominance analysis hypothesis:
1. **Standardized coefficient plot**: horizontal bar chart of OLS coefficients with 95% CI error bars
2. **VIF diagnostic table**: bar chart of VIF values for win_rate and avg_length (with threshold line at 5.0)
3. **OLS residual plot**: fitted vs residuals scatter (heteroscedasticity check)
4. **Q-Q plot**: normality of OLS residuals
5. **Scatter plot**: win_rate_std vs LC_winrate (color by avg_length quartile) — shows raw dominance
6. **Comparison with h-e1**: table showing r_partial (h-e1) alongside β_win_rate_std (h-m1) — narrative continuity

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (StandardScaler, VIF, OLS/permutation all execute)
2. |β_win_rate_std| > |β_avg_length_std| (OLS path) OR Shapley(win_rate) > Shapley(avg_length) (fallback)
3. VIF < 5 confirmed (consistent with h-e1 finding of 1.764)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No relevant sources found (Archon KB does not contain statistical regression / dominance analysis content).
- Query 1 (standardized OLS regression dominance): max similarity < 0.35, all diffusion-model content
- Query 2 (VIF collinearity Shapley statsmodels): max similarity < 0.34, all diffusion-model content
- Query 3 (statsmodels OLS sklearn permutation importance): max similarity < 0.37, diffusion/PyTorch content

### B. GitHub Implementations (Exa)

**Source 1: statsmodels variance_inflation_factor** (statsmodels official)
- **URL:** https://www.statsmodels.org/dev/generated/statsmodels.stats.outliers_influence.variance_inflation_factor.html
- **Query Used:** statsmodels OLS standardized coefficients VIF Python regression
- **Relevance:** Official VIF API; standardize=True default in v0.15+ for numerical stability
- **Key Code:**
  ```python
  from statsmodels.stats.outliers_influence import variance_inflation_factor
  vif = variance_inflation_factor(X.values, idx)  # standardize=True default
  ```
- **Used For:** VIF diagnostic step in H-M1 protocol; gate selection (OLS vs permutation)

**Source 2: statsmodels OLS** (official docs)
- **URL:** https://www.statsmodels.org/dev/generated/statsmodels.regression.linear_model.OLS.html
- **Relevance:** OLS regression API; params → standardized coefficients when X is StandardScaler-normalized
- **Key Code:**
  ```python
  import statsmodels.api as sm
  X_sm = sm.add_constant(X_std)
  results = sm.OLS(y, X_sm).fit()
  # results.params[1] = β_win_rate_std
  # results.params[2] = β_avg_length_std
  ```
- **Used For:** Core mechanism pseudo-code; beta comparison implementation

**Source 3: StackOverflow VIF pattern** (statsmodels community)
- **URL:** https://stackoverflow.com/questions/42258241/vif-by-coef-in-ols-regression-results-python
- **Relevance:** Complete pattern for extracting VIF from OLS exog matrix with variable names
- **Used For:** VIF DataFrame construction with named features

**Source 4: sklearn permutation_importance** (scikit-learn official)
- **URL:** https://scikit-learn.org/stable/modules/generated/sklearn.inspection.permutation_importance.html
- **Relevance:** Fallback dominance metric when VIF ≥ 5; model-agnostic; works with LinearRegression
- **Key Code:**
  ```python
  from sklearn.inspection import permutation_importance
  from sklearn.linear_model import LinearRegression
  lr = LinearRegression().fit(X_std, y)
  result = permutation_importance(lr, X_std, y, n_repeats=30, random_state=42)
  # result.importances_mean → per-feature importance (R² decrease when permuted)
  ```
- **Used For:** Shapley-proxy fallback in core mechanism pseudo-code

**Source 5: AlpacaEval official** (tatsu-lab)
- **URL:** https://github.com/tatsu-lab/alpaca_eval
- **Relevance:** Dataset source; LC_winrate confirmed as GLM length-controlled version of win_rate
- **Used For:** Dataset specification, understanding why β_win should dominate (LC already corrects length)

**Source 6: Dubois 2024 paper** (arXiv)
- **URL:** https://arxiv.org/html/2404.04475v2
- **Relevance:** Defines the GLM producing LC_winrate; confirms length-independent quality signal preserved
- **Used For:** Theoretical justification for why β_win_rate_std > β_avg_length_std expected

### C. Code Analysis (Serena)

Serena analysis: Not performed — statsmodels and sklearn APIs fully documented with complete runnable examples. Core mechanism based on official documentation, not proprietary code.

### D. Previous Hypothesis Context

**Source:** H-E1 Phase 4 Validation Report (docs/youra_research/h-e1/04_validation.md)
- **Reused Components:**
  - Dataset loading: same CSV, same dropna pipeline
  - VIF values: win_rate=1.764, avg_length=1.764 (no multicollinearity → OLS beta path confirmed)
  - Code structure: h-e1 data loading reused, StandardScaler added on top
- **Why Reused:** Controlled comparison — only the statistical test changes (partial_corr → standardized OLS); same data pipeline ensures consistency

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (AlpacaEval 2.0 CSV) | Previous hypothesis | H-E1 validation; tatsu-lab/alpaca_eval (B.5) |
| Column names (win_rate, length_controlled_winrate, avg_length) | Previous hypothesis | H-E1; tatsu-lab/alpaca_eval (B.5) |
| StandardScaler normalization | sklearn docs | StandardScaler API (implied by B.4) |
| Primary test (OLS beta comparison) | Exa docs search | statsmodels OLS (B.2); Phase 2B §2.2 H-M1 |
| VIF computation | Exa docs search | statsmodels VIF (B.1, B.3) |
| VIF threshold (5.0) | Exa docs + stdlib convention | statsmodels VIF docs (B.1) |
| Fallback (permutation_importance) | Exa docs search | sklearn permutation_importance (B.4) |
| VIF < 5 confirmation | Previous hypothesis | H-E1 validation (VIF=1.764) |
| Expected β dominance | Phase 2B roadmap | 02b_verification_plan.md §2.2 H-M1 |
| LC_winrate mechanism | Exa search | Dubois 2024 arXiv 2404.04475 (B.6) |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-04

### Workflow History for This Hypothesis
- 2026-08-04T00:00:00Z: Phase 2B completed; h-m1 identified as MUST_WORK mechanism hypothesis
- 2026-08-04T08:15:38Z: H-E1 PASSED (r_partial=0.9851, p=1.69e-170); h-m1 prerequisites satisfied
- 2026-08-04T08:18:58Z: h-m1 set to IN_PROGRESS by hypothesis loop
- 2026-08-04: Phase 2C experiment design initiated (UNATTENDED mode)

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (GitHub — 6 sources), Serena (Skipped — code clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
