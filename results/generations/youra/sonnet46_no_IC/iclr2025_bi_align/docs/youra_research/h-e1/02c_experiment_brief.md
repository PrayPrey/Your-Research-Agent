# Experiment Design: h-e1

**Date:** 2026-08-04
**Author:** Anonymous
**Hypothesis Statement:** Under AlpacaEval 2.0 N=222 models, ρ(win_rate, LC_winrate | avg_length) > 0, p < 0.05, |r_partial| ≥ 0.15. Model capability independently predicts length-debiased preference beyond verbosity.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** None required (foundation hypothesis)
**Gate Status:** MUST_WORK — pending experiment execution

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK — if H-E1 partial correlation fails (r_partial ≤ 0 OR p ≥ 0.05 OR |r_partial| < 0.15), stop pipeline and route to Phase 0 with documented failure mode.

---

## Continuation Context

First hypothesis in the verification chain — no prior hypothesis results to inherit.

### Previous Hypothesis Results (if applicable)
None — h-e1 has no prerequisites.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Archon KB did not contain directly relevant statistical analysis or LLM evaluation literature (KB is populated with diffusion model content). No matching past implementation cases found for partial correlation analysis on LLM leaderboard data.

**Query 1: partial correlation statistical analysis LLM evaluation**
- No relevant results (similarity scores < 0.45; all diffusion-model content)

**Query 2: pingouin partial_corr bootstrap scipy statsmodels OLS**
- No relevant results (similarity scores < 0.42; all diffusion-model content)

*Note: Archon KB is domain-specific to prior pipeline work (diffusion models). Statistical analysis implementation grounded in Exa search results below.*

### Archon Code Examples

No relevant code examples found in Archon KB for this statistical analysis domain.

---

### Exa GitHub Implementations

**Query 1: AlpacaEval leaderboard win_rate length_controlled_winrate partial correlation Python**

**Source 1: tatsu-lab/alpaca_eval** (⭐ 2010)
- **URL:** https://github.com/tatsu-lab/alpaca_eval
- **Relevance:** Official AlpacaEval repository — defines the exact CSV format and column names used in this experiment
- **Key Data Format:**
  ```
  name, length_controlled_winrate, win_rate, avg_length, link, samples, filter
  ```
- **Dataset URL (raw CSV):** https://raw.githubusercontent.com/tatsu-lab/alpaca_eval/main/docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv
- **Key Insight:** LC win rate computed via GLM controlling for length; ρ(LC, ChatBot Arena) = 0.98; win_rate and LC_winrate are empirically distinct (Dubois 2024 arXiv 2404.04475)

**Source 2: tatsu-lab/alpaca_eval — metrics.py** (official)
- **URL:** https://github.com/tatsu-lab/alpaca_eval/blob/15fd513071d389b79dab27fd464800c6fe10c15a/src/alpaca_eval/metrics.py
- **Key Code:**
  ```python
  def pairwise_to_winrate(preferences):
      out = AbsoluteScoringRule().describe_head2head(preferences)
      return out
  ```
- **Insight:** win_rate = mean(preferences) * 100 where preferences ∈ {0, 0.5, 1}; LC_winrate is GLM-corrected version

**Query 2: pingouin partial_corr Spearman correlation statsmodels OLS Python**

**Source 3: raphaelvallat/pingouin** (pingouin-stats.org)
- **URL:** https://pingouin-stats.org/generated/pingouin.partial_corr.html
- **Relevance:** Canonical Python library for partial correlation — exact function to implement H-E1
- **Key API:**
  ```python
  import pingouin as pg
  result = pg.partial_corr(
      data=df,
      x='win_rate',
      y='length_controlled_winrate',
      covar='avg_length',
      method='spearman'
  )
  # Returns DataFrame with columns: n, r, CI95, p-val
  ```
- **Method:** Inverse covariance matrix (not OLS residuals) — faster, matches R ppcor package
- **Numerical stability:** Standardizes data before covariance computation (PR #510 fix)

**Source 4: statsmodels OLS** (for H-M1 gate design)
- **URL:** https://www.statsmodels.org/devel/generated/statsmodels.regression.linear_model.OLS.html
- **Key API:**
  ```python
  import statsmodels.api as sm
  from sklearn.preprocessing import StandardScaler
  scaler = StandardScaler()
  X_std = scaler.fit_transform(df[['win_rate', 'avg_length']])
  X_with_const = sm.add_constant(X_std)
  model = sm.OLS(df['length_controlled_winrate'], X_with_const)
  results = model.fit()
  ```

**Serena Analysis Needed:** false — code is clear from documentation

---

### 🎯 Implementation Priority Assessment

**CRITICAL: This is a statistical observational study, not a paper reproduction experiment.**

This experiment does NOT reproduce a paper — it performs original statistical analysis on the AlpacaEval 2.0 leaderboard CSV. No "author's official implementation" applies.

**Recommended Implementation Path:**
- Primary: `pingouin.partial_corr()` with `method='spearman'` — canonical Python partial correlation implementation
- Fallback: Manual residual regression (OLS of avg_length→win_rate, OLS of avg_length→LC_winrate, then Spearman of residuals)
- Justification: pingouin uses inverse covariance matrix method (faster, validated against R ppcor); Spearman is robust to outliers and does not assume normality of leaderboard scores

---

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. pingouin and statsmodels APIs are well-documented with complete examples. No complex implementation requiring semantic code analysis.

---

## Experiment Specification

### Dataset

**Name:** AlpacaEval 2.0 Leaderboard (weighted_alpaca_eval_gpt4_turbo_leaderboard.csv)
**Type:** standard (real leaderboard data, pre-computed by tatsu-lab team)
**Source:** https://github.com/tatsu-lab/alpaca_eval

**Statistics:**
- N = 222 models (full leaderboard)
- Columns used: `win_rate`, `length_controlled_winrate`, `avg_length`
- No train/val/test split — full dataset is the analysis population
- Expected N_clean ≥ 200 after dropping rows with missing values

**Preprocessing:**
1. Load CSV with `pandas.read_csv()`
2. Drop rows with NaN in any of {win_rate, length_controlled_winrate, avg_length}
3. Assert N_clean ≥ 200 (failure = data integrity error)
4. No normalization needed for Spearman partial correlation (rank-based, scale-invariant)

**Synthetic Data Policy:** CONFIRMED REAL DATA — AlpacaEval 2.0 leaderboard is a publicly available dataset of pre-computed LLM evaluation scores. Type = standard. NOT synthetic.

**Loading Information** (for Phase 4 download):
- Method: local CSV (already cached in repository)
- Identifier: `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv`
- Code:
  ```python
  import pandas as pd
  df = pd.read_csv('docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv')
  df = df.dropna(subset=['win_rate', 'length_controlled_winrate', 'avg_length'])
  assert len(df) >= 200, f"Expected ≥200 models, got {len(df)}"
  ```

---

### Models

#### Baseline Model

**Architecture:** Null model — H0: ρ(win_rate, LC_winrate | avg_length) = 0
**Description:** No association between model capability (win_rate) and length-debiased preference (LC_winrate) after controlling for verbosity. Verbosity alone explains the win_rate → LC_winrate relationship.
**Operationalization:** Statistical threshold r_partial = 0; baseline performance = no significant partial correlation

**Loading Information** (for Phase 4 download):
- Method: N/A — statistical null hypothesis, no model to load
- Identifier: N/A
- Code: N/A (baseline is the null statistical outcome, not a model)

---

#### Proposed Model

**Architecture:** Partial correlation analysis — win_rate predicts LC_winrate after controlling for avg_length

**Core Mechanism Implementation:**

```python
# Core Mechanism: Spearman Partial Correlation (H-E1)
# Based on: pingouin library (raphaelvallat/pingouin, pingouin-stats.org)
# Input: AlpacaEval 2.0 leaderboard DataFrame with N≥200 rows
# Output: partial correlation result with r, p-val, CI95

import pandas as pd
import pingouin as pg
import numpy as np
from scipy import stats

def compute_h_e1_partial_correlation(df: pd.DataFrame) -> dict:
    """
    Test H-E1: ρ(win_rate, LC_winrate | avg_length) > 0, p < 0.05, |r| ≥ 0.15
    
    Args:
        df: DataFrame with columns win_rate, length_controlled_winrate, avg_length
    Returns:
        dict with r_partial, p_val, ci95, n, passes_gate
    """
    # Primary: Spearman partial correlation via pingouin
    result = pg.partial_corr(
        data=df,
        x='win_rate',
        y='length_controlled_winrate',
        covar='avg_length',
        method='spearman',
        alternative='greater'       # one-sided: test r > 0
    )
    r_partial = result['r'].values[0]
    p_val = result['p-val'].values[0]
    ci95 = result['CI95%'].values[0]
    n = result['n'].values[0]
    
    # Gate check
    passes_gate = (r_partial > 0) and (p_val < 0.05) and (abs(r_partial) >= 0.15)
    
    return {
        'r_partial': r_partial, 'p_val': p_val,
        'ci95': ci95, 'n': n, 'passes_gate': passes_gate
    }

# Bootstrap robustness check (1000 resamples)
def bootstrap_partial_corr(df, n_bootstrap=1000, random_state=42):
    rng = np.random.default_rng(random_state)
    boot_rs = []
    for _ in range(n_bootstrap):
        sample = df.sample(n=len(df), replace=True, random_state=rng.integers(1e9))
        r = pg.partial_corr(sample, x='win_rate', y='length_controlled_winrate',
                            covar='avg_length', method='spearman')['r'].values[0]
        boot_rs.append(r)
    ci_lower, ci_upper = np.percentile(boot_rs, [2.5, 97.5])
    return ci_lower, ci_upper, boot_rs
```

---

### Training Protocol

**Note:** This is a statistical observational study — no model training, no optimizer, no epochs. The "protocol" is the statistical analysis pipeline.

**Analysis Pipeline:**
1. Data loading and quality check (assert N ≥ 200)
2. VIF diagnostic: `from statsmodels.stats.outliers_influence import variance_inflation_factor`
3. Primary analysis: `pingouin.partial_corr()` — Spearman, one-sided (alternative='greater')
4. Bootstrap robustness: 1000 resamples, seed=42, report 95% CI
5. Replication on N=58 typed subset (models with known training_type from h-m1)
6. Full N=222 is the primary analysis; N=58 is replication/comparison

**Hyperparameters (Statistical):**
- alpha = 0.05 (significance threshold)
- n_bootstrap = 1000
- random_state = 42
- r_partial_threshold = 0.15 (minimum effect size)
- VIF_threshold = 5.0 (collinearity diagnostic for H-M1)

**Seeds:** 1 (seed=42 for bootstrap only)

> ⚠️ **EXISTENCE (PoC)**: Single analysis pipeline. No training loop.

---

### Evaluation

**Primary Metrics:**
- r_partial: Spearman partial correlation coefficient (win_rate, LC_winrate | avg_length)
- p_val: one-sided p-value (alternative='greater', i.e., r > 0)
- CI95: 95% confidence interval from bootstrap

**Success Criteria:**
- r_partial > 0 AND p_val < 0.05 AND |r_partial| ≥ 0.15
- Bootstrap CI lower bound > 0 (secondary confirmation)

**Expected Baseline Performance (from literature):**
- Dubois 2024: ρ(win_rate, LC_winrate) ≈ 0.94 (unconditional Spearman)
- h-m1 within-RLHF observation: visible capability gradient → expect r_partial > 0
- Expected r_partial range: 0.15–0.50 (after controlling for avg_length)
- Source: arXiv 2404.04475, h-m1 04_validation.md

**Task Type:** statistical correlation analysis (no classification/regression model)
**Library:** pingouin (partial_corr), scipy.stats (spearmanr for verification), statsmodels (VIF, OLS)
**Metrics Loading Code:**
```python
import pingouin as pg
from statsmodels.stats.outliers_influence import variance_inflation_factor
import statsmodels.api as sm
```

---

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing r_partial vs threshold (0.15); p_val vs alpha (0.05)

#### Additional Figures (LLM Autonomous)

Based on this statistical analysis hypothesis, recommended figures:
1. **Scatter plot:** win_rate vs LC_winrate (color-coded by avg_length quartile) — shows raw relationship and verbosity confound
2. **Partial regression plot:** residualized win_rate vs residualized LC_winrate (after removing avg_length) — directly visualizes the partial correlation
3. **Bootstrap distribution:** histogram of 1000 bootstrap r_partial values with CI bands
4. **VIF diagnostic table/bar:** VIF(win_rate), VIF(avg_length) — multicollinearity check
5. **Δ = LC_winrate − win_rate vs win_rate scatter:** with trend line — shows bidirectional alignment gap pattern

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (data loads, N ≥ 200, pingouin executes)
2. r_partial > 0 AND p_val < 0.05 AND |r_partial| ≥ 0.15

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

No relevant sources found (Archon KB does not contain LLM evaluation / statistical analysis content).
- Query 1 (partial correlation statistical analysis LLM evaluation): max similarity 0.453, all diffusion-model content
- Query 2 (pingouin partial_corr bootstrap statsmodels OLS): max similarity 0.413, all diffusion-model content

### B. GitHub Implementations (Exa)

**Repository 1: tatsu-lab/alpaca_eval** (⭐ 2010)
- **URL:** https://github.com/tatsu-lab/alpaca_eval
- **Query Used:** AlpacaEval leaderboard win_rate length_controlled_winrate partial correlation Python
- **Relevance:** Official dataset source; defines column names and CSV format used in experiment
- **Key Data Confirmed:**
  ```
  columns: name, length_controlled_winrate, win_rate, avg_length, link, samples, filter
  N=222 rows in weighted_alpaca_eval_gpt4_turbo_leaderboard.csv
  ```
- **Used For:** Dataset specification, column name confirmation, data loading code

**Repository 2: tatsu-lab/alpaca_eval — notebooks/length_controlled.ipynb**
- **URL:** https://github.com/tatsu-lab/alpaca_eval/blob/main/notebooks/length_controlled.ipynb
- **Relevance:** Official Jupyter notebook implementing length-controlled analysis; uses Spearman correlation and causal inference framing
- **Key Insight:** Authors use Spearman for leaderboard correlation; note causal inference interpretation of LC win rate
- **Used For:** Justification for Spearman over Pearson; corroborates one-sided test rationale

**Repository 3: raphaelvallat/pingouin** (pingouin-stats.org)
- **URL:** https://pingouin-stats.org/generated/pingouin.partial_corr.html
- **Query Used:** pingouin partial_corr Spearman correlation statsmodels OLS Python
- **Relevance:** Canonical partial correlation library — direct implementation of the primary statistical test
- **Key Code:**
  ```python
  # Spearman partial correlation with one covariate
  result = pg.partial_corr(
      data=df, x='win_rate', y='length_controlled_winrate',
      covar='avg_length', method='spearman', alternative='greater'
  )
  # Returns: n, r, CI95%, p-val
  ```
- **Method:** Inverse covariance matrix (matches R ppcor); validated against R; handles Spearman via rank transformation
- **Numerical Stability:** PR #510 — standardizes before covariance (scale-invariant, no effect on result)
- **Used For:** Core mechanism pseudo-code, primary statistical test implementation

**Repository 4: statsmodels OLS** (statsmodels.org)
- **URL:** https://www.statsmodels.org/devel/generated/statsmodels.regression.linear_model.OLS.html
- **Relevance:** Standard library for OLS regression; used for VIF diagnostic and standardized regression (H-M1 gate)
- **Key Code:**
  ```python
  import statsmodels.api as sm
  from statsmodels.stats.outliers_influence import variance_inflation_factor
  X = df[['win_rate', 'avg_length']]
  vif = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
  ```
- **Used For:** VIF diagnostic, OLS training protocol for H-M1

### C. Code Analysis (Serena)

Serena analysis: Not performed — code from search results was sufficiently clear. pingouin and statsmodels APIs are fully documented with runnable examples.

### D. Previous Hypothesis Context

Previous Context: None — h-e1 is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (AlpacaEval 2.0 CSV) | Exa GitHub | tatsu-lab/alpaca_eval (Repo B.1) |
| Column names (win_rate, length_controlled_winrate, avg_length) | Exa GitHub | tatsu-lab/alpaca_eval CSV raw (B.1) |
| Primary test (pingouin.partial_corr) | Exa code search | raphaelvallat/pingouin (B.3) |
| Spearman method choice | Exa notebook | length_controlled.ipynb (B.2) |
| Bootstrap protocol (n=1000, seed=42) | Phase 2B roadmap | 02b_verification_plan.md §2.2 H-E1 |
| VIF diagnostic | Exa code search | statsmodels OLS (B.4) |
| Alpha = 0.05, r_partial ≥ 0.15 | Phase 2B roadmap | 02b_verification_plan.md §2.2 H-E1 |
| Expected baseline (ρ ≈ 0.94 unconditional) | Phase 2B roadmap | Dubois 2024 arXiv 2404.04475 |
| N=58 replication | Phase 2B roadmap | 02b_verification_plan.md §2.2 H-E1 A3 |
| Visualization (scatter, partial regression plot) | Domain knowledge | Statistical best practice |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-04

### Workflow History for This Hypothesis
- 2026-08-04T00:00:00Z: Phase 2B completed; h-e1 identified as MUST_WORK foundation
- 2026-08-04T07:59:00Z: h-e1 set to IN_PROGRESS by hypothesis loop
- 2026-08-04: Phase 2C experiment design initiated (UNATTENDED mode)

---

*MCP Tools Used: Archon (Knowledge + Code — no relevant results), Exa (GitHub — 4 sources), Serena (Skipped — code clear)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
