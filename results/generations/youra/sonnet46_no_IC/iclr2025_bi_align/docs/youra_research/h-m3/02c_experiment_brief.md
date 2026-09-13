# Experiment Design: h-m3

**Date:** 2026-08-04
**Author:** Anonymous
**Hypothesis Statement:** The bidirectional alignment gap (Delta = LC_winrate - win_rate) is smaller for high-capability models: Kruskal-Wallis on Delta across win_rate quartiles p < 0.05.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** — Tests capability-modulated alignment gap via nonparametric ANOVA (Kruskal-Wallis) on quartile-grouped Delta values.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-E1 PASSED (r_partial=0.9851, p=1.69e-170), H-M1 PASSED (|β_win_rate_std|=21.34 >> |β_avg_length_std|=4.37), H-M2 PASSED (rho(resid)=0.9739, p=2.37e-144)
**Gate Status:** SHOULD_WORK — Kruskal-Wallis p < 0.05 on Delta across quartiles required; failure documents limitation, does not invalidate H-E1/H-M1/H-M2

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (MUST_WORK — PASSED), h-m1 (MUST_WORK — PASSED), h-m2 (SHOULD_WORK — PASSED)

### Gate Condition
SHOULD_WORK — if Kruskal-Wallis p ≥ 0.05 on Delta across win_rate quartiles, document as scope limitation. Does NOT invalidate H-E1, H-M1, or H-M2. Continue to H-C1 regardless.

---

## Continuation Context

**From H-E1 Validation (h-e1/04_validation.md):**
- r_partial = 0.9851, p = 1.69e-170, n = 223
- VIF: win_rate = 1.764, avg_length = 1.764 (well below 5.0)

**From H-M1 Validation (h-m1/04_validation.md):**
- |β_win_rate_std| = 21.3391 >> |β_avg_length_std| = 4.3720
- R² = 0.9628, Breusch-Pagan p = 0.011 (mild heteroscedasticity, non-critical)
- OLS code infrastructure reusable (same CSV, StandardScaler, statsmodels)

**From H-M2 Validation (h-m2/04_validation.md):**
- rho(win_rate_resid, lc_resid) = 0.9739, p = 2.37e-144
- Bootstrap CI 95%: [0.9619, 0.9806]
- FWL consistency delta = 0.0112 < 0.02 (mechanistic confirmation)

**Key implication for H-M3:** The strong capability signal in H-E1/M1/M2 strongly predicts Kruskal-Wallis will pass. The within-RLHF observation from prior pipeline (GPT-4 Δ=−8.8pp vs wizardlm Δ=−32pp) provides direct empirical precedent. N=222 with 4 quartiles gives ~55 models/quartile — well above the "≥5 per group" requirement for Kruskal-Wallis.

**Known risk:** Δ = LC_winrate − win_rate contains a mathematical dependency on win_rate (−win_rate term). The Spearman ρ(win_rate, Δ) will be trivially negative due to composition. The OLS on Δ ~ win_rate_std + avg_length_std addresses this by partialling out the confound. The Kruskal-Wallis remains the primary gate test.

### Previous Hypothesis Results (if applicable)
H-M2 residual OLS infrastructure fully reusable. Data loading, StandardScaler, and CSV parsing are established from h-e1/h-m1/h-m2 pipelines. H-M3 adds only: (1) Delta computation, (2) quartile binning with pd.qcut, (3) Kruskal-Wallis call, (4) Spearman ρ(win_rate, Δ) secondary test, (5) OLS on Δ for partial contribution.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Archon KB contains only diffusion-model content (no relevance to statistical analysis of LLM evaluation scores).

**Query 1: Kruskal-Wallis nonparametric test quartile analysis statistical experiment design**
- No relevant results (max similarity ≈ 0.30; all diffusion/image-generation content)

**Query 2: alignment gap bidirectional LLM evaluation capability win rate**
- No relevant results (max similarity ≈ 0.37; all HuggingFace diffusers community content)

*Note: Archon KB is domain-specific to prior pipeline work (diffusion models). Statistical analysis grounded in Exa search results below.*

### Archon Code Examples

**Query 1: Kruskal-Wallis scipy quartile nonparametric**
- No relevant results (all PyTorch distributed / diffusion scheduler content)

*Implementation grounded entirely in Exa findings; standard scipy/scikit-posthocs APIs documented below.*

---

### Exa GitHub Implementations

**Query 1: Kruskal-Wallis test quartile groups scipy statsmodels Python alignment gap analysis**

**Source 1: scipy.stats.kruskal (official docs)**
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html
- **Relevance:** Exact API for H-M3 primary gate test
- **Key API:**
  ```python
  from scipy import stats
  H, p = stats.kruskal(q1_delta, q2_delta, q3_delta, q4_delta)
  # Returns: KruskalResult(statistic=H, pvalue=p)
  # Requirement: >= 5 samples per group (N≈55/quartile satisfies this)
  ```
- **Pattern:** Pass each quartile's Delta values as separate positional arguments
- **Note:** Groups must be separated before passing — cannot pass group labels directly

**Source 2: scikit-posthocs tutorial (official docs)**
- **URL:** https://scikit-posthocs.readthedocs.io/en/latest/tutorial.html
- **Relevance:** Dunn post-hoc test needed for H-C1 (next hypothesis) — implement here for continuity
- **Key API:**
  ```python
  import scikit_posthocs as sp
  # After Kruskal-Wallis:
  dunn_result = sp.posthoc_dunn(df, val_col='delta', group_col='quartile', p_adjust='bonferroni')
  # Returns DataFrame of pairwise p-values; focus: Q1 vs Q4
  ```
- **Pattern:** Works directly on DataFrames with val_col/group_col specification

**Source 3: Python Handbook: Kruskal-Wallis (rcompanion.org)**
- **URL:** https://rcompanion.org/python/F08.html
- **Relevance:** Complete workflow with effect size (epsilon-squared) and multiple post-hoc options
- **Key pattern:**
  ```python
  import pingouin as pg
  # Alternative to scipy for single-call syntax:
  pg.kruskal(data=df, dv='delta', between='quartile')
  # Includes effect size H/df directly in output
  ```
- **Effect size:** Epsilon-squared = H / (N - 1); for H-M3 use as secondary reporting metric

**Source 4: AlpacaEval leaderboard CSV (tatsu-lab/alpaca_eval)**
- **URL:** https://github.com/tatsu-lab/alpaca_eval
- **Relevance:** Confirms CSV structure with win_rate, length_controlled_winrate, avg_length columns
- **Loading:** `pd.read_csv('docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv')`
- **Confirmed columns (from h-e1 validation):** win_rate, length_controlled_winrate, avg_length, N=222 rows

**Source 5: Dubois et al. 2024 (arXiv:2404.04475)**
- **URL:** https://arxiv.org/html/2404.04475v1
- **Relevance:** GLM-based length control mechanism underlying LC_winrate computation; confirms Δ interpretation
- **Key insight:** LC_winrate corrects for length bias via GLM — Δ = LC_winrate − win_rate represents the residual alignment adjustment after length debiasing

**Serena Analysis Needed:** false — statistical analysis; no complex neural network code to analyze

---

### 🎯 Implementation Priority Assessment

**CRITICAL: This is a statistical analysis experiment on pre-computed leaderboard data — no model training or GPU required.**

This is NOT a paper-reproduction DL experiment. The "implementation" is:
1. Load AlpacaEval 2.0 CSV (already verified cached at `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv`)
2. Compute Delta = LC_winrate − win_rate
3. Bin into quartiles via pd.qcut
4. Run Kruskal-Wallis via scipy.stats.kruskal
5. Run secondary analyses (Spearman, OLS on Delta, Dunn post-hoc)

**Recommended Implementation Path:**
- Primary: scipy.stats.kruskal + scikit-posthocs for Dunn post-hoc
- Fallback: pingouin.kruskal (equivalent, single DataFrame call)
- Justification: scipy + scikit-posthocs is the standard Python nonparametric analysis stack; matches h-e1/h-m1/h-m2 library dependencies (scipy, pandas, pingouin already installed)

### Code Analysis (Serena MCP)

*Skipped* — Code from Exa search results is sufficiently clear; no complex architecture requiring semantic analysis. All required APIs (scipy.stats.kruskal, scikit-posthocs.posthoc_dunn, pd.qcut) are well-documented standard library calls.

---

## Experiment Specification

### Dataset

**Name:** AlpacaEval 2.0 Leaderboard
**Version:** weighted_alpaca_eval_gpt4_turbo (as of 2024)
**Type:** standard (pre-computed LLM evaluation leaderboard scores)
**Source:** tatsu-lab/alpaca_eval GitHub repository
**N:** N=222 models (N=223 including header; 222 valid models after any NaN drops)

**Confirmed columns (from h-e1/h-m1/h-m2 validation):**
- `win_rate`: Raw human preference win fraction (capability proxy), range [0, 1]
- `length_controlled_winrate`: GLM-debiased preference score (Dubois 2024), range [0, 1]
- `avg_length`: Mean response token length (verbosity proxy)

**Derived variable:**
- `delta` = `length_controlled_winrate` − `win_rate` (alignment gap; DV for H-M3)
- Expected range: approximately [−0.40, +0.10] based on prior pipeline observations (mean Δ ≈ −16.37pp from h-m1)

**Quartile variable:**
- `quartile` = pd.qcut(df['win_rate'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
- Q1 = lowest win_rate (lowest capability), Q4 = highest win_rate (highest capability)
- Expected N per quartile: ~55 models (222/4 = 55.5)

**Preprocessing:**
1. Load CSV with `pd.read_csv(cache_path)`
2. Drop rows where any of [win_rate, length_controlled_winrate, avg_length] is NaN
3. Verify N ≥ 200 after cleaning (from h-e1: N=223 before drop, expect ~222 clean)
4. Compute delta = length_controlled_winrate − win_rate
5. Create quartile labels via pd.qcut(df['win_rate'], q=4, labels=['Q1','Q2','Q3','Q4'])
6. Verify quartile group sizes ≥ 5 each (Kruskal-Wallis requirement)

**No augmentation required** — observational study on fixed leaderboard scores.

**Loading Information** (for Phase 4 download):
- Method: local CSV (already cached)
- Identifier: `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv`
- Code:
  ```python
  import pandas as pd
  df = pd.read_csv('docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv')
  df = df.dropna(subset=['win_rate', 'length_controlled_winrate', 'avg_length'])
  df['delta'] = df['length_controlled_winrate'] - df['win_rate']
  df['quartile'] = pd.qcut(df['win_rate'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
  ```

### Models

#### Baseline Model

**Architecture:** N/A — no model training or inference
**Description:** This experiment operates on pre-computed evaluation scores from the AlpacaEval 2.0 leaderboard CSV. The "baseline" is the null hypothesis: Kruskal-Wallis H = 0, i.e., Delta distributions are identical across capability quartiles.

**Statistical baseline:**
- H0: Median Δ is equal across Q1, Q2, Q3, Q4
- Expected under H0: Kruskal-Wallis p ≥ 0.05
- Expected under H1 (our hypothesis): Kruskal-Wallis p < 0.05

**Loading Information** (for Phase 4 download):
- Method: N/A (no model weights)
- Identifier: N/A
- Code: N/A (leaderboard scores are pre-computed)

#### Proposed Model

**Architecture:** Baseline + Quartile-Stratified Delta Analysis

**Core Mechanism Implementation:**

```python
# Core Mechanism: Capability-Quartile Delta Distribution Test
# Based on: scipy.stats.kruskal, scikit-posthocs.posthoc_dunn
# Source: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html
# Source: https://scikit-posthocs.readthedocs.io/en/latest/tutorial.html

import numpy as np
import pandas as pd
import scipy.stats as stats
import scikit_posthocs as sp
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm

def run_hm3_experiment(df):
    """
    H-M3: Bidirectional alignment gap (Delta) is smaller for high-capability models.

    Args:
        df: DataFrame with win_rate, length_controlled_winrate, avg_length, delta, quartile
    Returns:
        dict with primary test result and secondary analyses
    """
    # Step 1: Extract Delta per quartile (primary test groups)
    q_groups = [df[df['quartile'] == q]['delta'].values
                for q in ['Q1', 'Q2', 'Q3', 'Q4']]
    assert all(len(g) >= 5 for g in q_groups), "Kruskal-Wallis requires >= 5/group"

    # Step 2: Primary gate test — Kruskal-Wallis on Delta across quartiles
    H_stat, kw_p = stats.kruskal(*q_groups)

    # Step 3: Secondary — Spearman rho(win_rate, delta) [note: mathematical dependency]
    rho_raw, p_rho = stats.spearmanr(df['win_rate'], df['delta'])

    # Step 4: OLS on Delta to partial out composition artifact
    # Delta = LC_winrate - win_rate; OLS controls for win_rate contribution
    scaler = StandardScaler()
    X_std = scaler.fit_transform(df[['win_rate', 'avg_length']])
    X_ols = sm.add_constant(X_std)
    ols_delta = sm.OLS(df['delta'], X_ols).fit()
    beta_win, beta_len = ols_delta.params[1], ols_delta.params[2]

    # Step 5: Effect size (epsilon-squared for Kruskal-Wallis)
    n = len(df)
    epsilon_sq = (H_stat - len(q_groups) + 1) / (n - len(q_groups))

    return {
        'kruskal_H': H_stat, 'kruskal_p': kw_p,
        'rho_win_delta': rho_raw, 'rho_p': p_rho,
        'ols_beta_win_std': beta_win, 'ols_beta_len_std': beta_len,
        'epsilon_squared': epsilon_sq, 'n_total': n,
        'quartile_medians': {q: np.median(g) for q, g in zip(['Q1','Q2','Q3','Q4'], q_groups)}
    }
```

### Training Protocol

**No model training required.** This is a statistical analysis study.

**From Previous Hypotheses (H-E1, H-M1, H-M2) — established configuration:**
- **Random state:** 42 (fixed for bootstrap resampling)
- **Bootstrap resamples:** 1000 (consistent with H-E1/M1/M2 pipeline)
- **VIF threshold:** 5.0 (pre-validated at 1.764; OLS interpretation confirmed valid)
- **Alpha:** 0.05 (two-tailed for Spearman; one-tailed for Kruskal-Wallis direction check)
- **Bonferroni correction:** Applied in Dunn post-hoc for H-C1 forward-compatibility
- **Seeds:** 1 (fixed; bootstrap uses random_state=42)

**Statistical Protocol:**
1. Load data and compute Delta + quartiles (Step 1)
2. Verify quartile group sizes ≥ 5 (Kruskal-Wallis requirement)
3. Run primary gate: Kruskal-Wallis H-test on Delta across Q1–Q4
4. Compute effect size: epsilon-squared = (H − k + 1) / (N − k), where k=4 groups
5. Secondary: Spearman ρ(win_rate, Delta) with bootstrap CI (note mathematical dependency caveat)
6. Secondary: OLS Δ ~ win_rate_std + avg_length_std (partial contribution analysis)
7. Run Dunn post-hoc with Bonferroni (for H-C1 forward-compatibility; focus on Q1 vs Q4)
8. Report quartile median Delta values as descriptive statistics

**Compute requirements:** CPU-only, < 1 second runtime. No GPU needed.
**Libraries:** pandas, numpy, scipy, statsmodels, scikit-posthocs, sklearn, pingouin, matplotlib/seaborn

**Rationale for rationale:** All hyperparameters (alpha=0.05, n_bootstrap=1000, random_state=42) reused from h-e1/h-m1/h-m2 pipeline for controlled comparison. Bonferroni correction selected per Phase 2B verification plan Section 2.2.

### Evaluation

**Primary Metric (gate):** Kruskal-Wallis p-value on Delta across win_rate quartiles
- **Success:** p < 0.05 (SHOULD_WORK gate satisfied)
- **Failure:** p ≥ 0.05 (document as scope limitation; pipeline continues to H-C1)

**Secondary Metrics:**
- Spearman ρ(win_rate, Δ): expected < 0 (negative correlation; caveat: mathematical dependency)
- OLS Δ ~ win_rate_std + avg_length_std: β_win_std direction and significance
- Epsilon-squared: effect size for Kruskal-Wallis (> 0.06 = medium, > 0.14 = large)
- Quartile median Delta: monotonic decrease Q1→Q4 confirms directionality

**Expected Results (from prior pipeline):**
- Kruskal-Wallis: H likely > 100 (given rho=0.9851 from H-E1); p << 0.001
- ρ(win_rate, Δ): expected ≈ −0.90 to −0.99 (strong negative; partially mathematical)
- Median Delta by quartile: Q1 (most negative) → Q4 (least negative / closest to 0)
- Epsilon-squared: expected "large" (> 0.14) given strength of H-E1 signal

**PoC Success Check:**
1. Code runs without error
2. Kruskal-Wallis p < 0.05 (primary gate)
3. Quartile median Delta shows monotonic trend Q1 < Q2 < Q3 < Q4 (directionality confirmation)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: nonparametric statistical test
- Library: scipy.stats (primary), scikit-posthocs (post-hoc), pingouin (alternative)
- Code:
  ```python
  from scipy import stats
  import scikit_posthocs as sp
  H, p = stats.kruskal(*[df[df['quartile']==q]['delta'].values for q in ['Q1','Q2','Q3','Q4']])
  dunn = sp.posthoc_dunn(df, val_col='delta', group_col='quartile', p_adjust='bonferroni')
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar/box chart comparing Delta distributions across Q1–Q4 quartiles with Kruskal-Wallis p-value annotation

#### Additional Figures (LLM Autonomous)

**Recommended for H-M3:**
1. **Boxplot:** Delta distribution per quartile (Q1–Q4) with median lines, jittered data points, and significance brackets (Q1 vs Q4 p-value from Dunn)
2. **Scatter plot:** win_rate vs Delta scatter with quartile color-coding and linear/LOWESS trend line
3. **Heatmap:** Dunn post-hoc pairwise p-values (4×4 matrix with Bonferroni correction)
4. **Violin plot:** Delta density per quartile overlaid with median markers

**Output Location:** `docs/youra_research/h-m3/figures/`

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `docs/youra_research/h-m3/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Kruskal-Wallis p < 0.05 on Delta across win_rate quartiles

**Mechanism Verification Protocol:**

| Element | Specification |
|---------|--------------|
| `mechanism_exists` | Delta = LC_winrate − win_rate is computable from CSV columns |
| `mechanism_isolatable` | Quartile binning separates capability levels; Kruskal-Wallis isolates group differences |
| `baseline_measurable` | H0 (equal medians across quartiles) is the statistical null |
| `architecture_compatibility` | N/A — observational study; N=222 >> 5 per quartile minimum |
| `mechanism_log_message` | "H-M3: KW H={H:.4f}, p={p:.2e}, epsilon_sq={eps:.4f}" |
| `metric_delta_expected` | Kruskal-Wallis p << 0.05; epsilon_sq > 0.14 (large effect) |
| `mechanism_verification_code` | `assert kw_p < 0.05, f"Gate FAILED: KW p={kw_p:.4f} >= 0.05"` |
| `hypothesis_support_threshold` | Kruskal-Wallis p < 0.05 |
| `hypothesis_support_metric` | kruskal_p |

**Architecture compatibility check:** N=222, 4 quartiles, ~55 models/quartile >> minimum 5/group. No architecture needed; CSV loading is the only dependency. Confirmed cached at `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv` (validated in h-e1, h-m1, h-m2).

**Failure detection:** If Kruskal-Wallis p ≥ 0.05, check: (1) correct column name `length_controlled_winrate` vs `lc_winrate`; (2) quartile group sizes ≥ 5; (3) no NaN in delta column. Mathematical dependency of Delta on win_rate makes H0 rejection nearly certain given H-E1 results.

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

Archon KB contained no relevant results for statistical nonparametric analysis (domain is diffusion models).
- All 3 knowledge queries returned max similarity < 0.38 (diffusion/PyTorch distributed content)
- All 2 code example queries returned irrelevant results (PyTorch distributed, diffusion schedulers)

### B. GitHub Implementations (Exa)

**Repository 1: scipy.stats.kruskal (SciPy official)**
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html
- **Query Used:** "Kruskal-Wallis test quartile groups scipy statsmodels Python alignment gap analysis"
- **Relevance:** Exact API for H-M3 primary gate test
- **Key Code (annotated):**
  ```python
  from scipy import stats
  # Pass each group's values as separate positional arguments
  H, p = stats.kruskal(q1_values, q2_values, q3_values, q4_values)
  # Used as basis for: primary gate test implementation
  ```
- **Used For:** Primary Kruskal-Wallis gate test (Step 3 in pseudo-code)

**Repository 2: scikit-posthocs tutorial**
- **URL:** https://scikit-posthocs.readthedocs.io/en/latest/tutorial.html
- **Query Used:** Same query as above
- **Relevance:** Dunn post-hoc test with Bonferroni correction for pairwise comparisons
- **Key Code (annotated):**
  ```python
  import scikit_posthocs as sp
  # Direct DataFrame API — val_col is DV, group_col is IV
  dunn = sp.posthoc_dunn(df, val_col='delta', group_col='quartile', p_adjust='bonferroni')
  # Q1 vs Q4 result: dunn.loc['Q1', 'Q4']
  # Used as basis for: H-C1 forward-compatible post-hoc implementation
  ```
- **Used For:** Post-hoc Dunn test implementation; Bonferroni correction

**Repository 3: Python Handbook: Kruskal-Wallis (rcompanion.org)**
- **URL:** https://rcompanion.org/python/F08.html
- **Relevance:** Complete workflow with effect size epsilon-squared computation
- **Key Code (annotated):**
  ```python
  # Effect size for Kruskal-Wallis (epsilon-squared)
  Data['Likert.rank'] = Data['Likert'].rank()
  pg.anova(data=Data, dv='Likert.rank', between='Speaker', effsize='n2')
  # Equivalent direct formula: epsilon_sq = (H - k + 1) / (N - k)
  # Used as basis for: effect size reporting
  ```
- **Used For:** Effect size (epsilon-squared) computation in evaluation metrics

**Repository 4: AlpacaEval (tatsu-lab/alpaca_eval)**
- **URL:** https://github.com/tatsu-lab/alpaca_eval
- **Query Used:** "AlpacaEval 2.0 win_rate LC_winrate alignment gap capability quartile analysis"
- **Relevance:** Confirms CSV structure; Dubois 2024 (arXiv:2404.04475) GLM methodology
- **Used For:** Dataset specification and Delta interpretation

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from Exa results was sufficiently clear. All required APIs are standard library calls with explicit documentation.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Reports — h-e1, h-m1, h-m2
- **h-e1/04_validation.md:** r_partial=0.9851, VIF=1.764, N=223, bootstrap CI [0.976, 0.988]
- **h-m1/04_validation.md:** β_win_rate_std=21.34, β_avg_length_std=4.37, R²=0.9628
- **h-m2/04_validation.md:** rho(resid)=0.9739, FWL delta=0.0112, pingouin r=0.9851

**Reused Components:**
- CSV path: `docs/data_AlpacaEval_2/weighted_alpaca_eval_gpt4_turbo_leaderboard.csv` (verified)
- Column names: win_rate, length_controlled_winrate, avg_length (confirmed)
- Hyperparameters: alpha=0.05, n_bootstrap=1000, random_state=42
- StandardScaler, statsmodels OLS code structure (for secondary OLS on Delta)

**Why Reused:** Enables controlled experiment — only the DV (Delta instead of LC_winrate) and test (Kruskal-Wallis instead of partial correlation/OLS) change from prior hypotheses.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: AlpacaEval 2.0 CSV | Prior pipeline + Exa | h-e1 validation; tatsu-lab/alpaca_eval |
| Delta computation | Phase 2B plan | 02b_verification_plan.md §2.2 (H-M3) |
| Quartile binning via pd.qcut | Phase 2B plan | 02b_verification_plan.md §2.2 (H-M3) |
| Kruskal-Wallis API | Exa (scipy docs) | Source B.1 (scipy.stats.kruskal) |
| Dunn post-hoc API | Exa (scikit-posthocs) | Source B.2 (posthoc_dunn, Bonferroni) |
| Effect size (epsilon-squared) | Exa (rcompanion) | Source B.3 |
| Spearman ρ(win_rate, Δ) secondary | Phase 2B plan | 02b_verification_plan.md §2.2 (H-M3) |
| OLS on Δ (partial analysis) | Phase 2B plan + h-m1 | 02b_verification_plan.md; h-m1 OLS code |
| Hyperparameters (alpha, bootstrap) | Prior pipeline | h-e1/h-m1/h-m2 04_validation.md |
| Visualization approach | Phase 2B plan | 02b_verification_plan.md §2.2 (H-M3) |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-04T09:25:00Z

### Workflow History for This Hypothesis
- 2026-08-04T09:01:24Z: h-m3 set to IN_PROGRESS (external hypothesis loop)
- 2026-08-04T09:25:00Z: Phase 2C experiment design COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code, no relevant results — domain mismatch), Exa (scipy docs, scikit-posthocs, rcompanion, alpaca_eval), Serena (skipped — clear code)*
*All specifications grounded in researched implementations and prior pipeline validation results*
*Next Phase: Phase 3 - Implementation Planning*
