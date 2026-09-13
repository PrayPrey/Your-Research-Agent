# Phase 2C Research Notes: H-M1

**Hypothesis:** Observed coupling persists when controlling for instance difficulty (partial phi ≥ 0.25)
**Date:** 2026-08-19
**Research Method:** Exa code search + web research (Archon KB unavailable)

---

## Research Questions

1. **Implementation:** How to compute partial correlation for binary/categorical data?
2. **Difficulty Proxy:** How to measure instance difficulty in LLM evaluation?
3. **Stratified Analysis:** How to validate coupling within difficulty quartiles?
4. **Validation:** What thresholds indicate difficulty-independent coupling?

---

## Key Findings

### 1. Partial Correlation Implementation

**Primary Library: Pingouin**
- **Function:** `pingouin.partial_corr(data, x, y, covar, method='pearson')`
- **Strength:** Clean API, handles multiple covariates, returns p-values + CI
- **Method:** Inverse covariance matrix approach (faster than regression residuals)
- **Validation:** Tested against R ppcor package
- **Installation:** `pip install pingouin`

**Example Usage:**
```python
import pingouin as pg

# Partial correlation: truthfulness-robustness controlling for difficulty
result = pg.partial_corr(
    data=df,
    x='truthfulness',
    y='robustness',
    covar='difficulty_score',  # or ['covar1', 'covar2'] for multiple
    method='pearson'
)
# Returns: n, r (partial correlation), CI95%, p-val
```

**Key Insight:** Partial correlation uses residuals after regressing out confounders:
- `x ~ difficulty, y ~ difficulty` → compute correlation of residuals
- Equivalent to controlling for difficulty's effect on both dimensions

**Alternative (if phi coefficient needed):** Compute phi on residuals after linear regression

---

### 2. Instance Difficulty Measurement

**Method 1: Model Confidence Scores (Primary)**
- **Proxy:** Logit probabilities from API responses
- **Justification:** Low confidence = high difficulty
- **Implementation:** Extract `logprobs` from OpenAI/Anthropic API
- **Validation:** Papers show confidence correlates with item difficulty (IRT)

**Source:** "The LLM Already Knows: Estimating LLM-Perceived Question Difficulty via Hidden Representations" (EMNLP 2025)
- Key finding: Model confidence (logprobs) strongly correlates with human difficulty ratings
- Method: Use max token probability as difficulty proxy

**Method 2: Stratified Analysis (Secondary)**
- **Approach:** Quartile-based difficulty binning
- **Implementation:** `pd.qcut(difficulty_scores, q=4, labels=['Q1','Q2','Q3','Q4'])`
- **Analysis:** Compute phi coefficient within each quartile
- **Validation:** Coupling should persist across quartiles if difficulty-independent

**Code Pattern:**
```python
# Bin difficulty into quartiles
df['difficulty_quartile'] = pd.qcut(
    df['difficulty_score'],
    q=4,
    labels=['Q1', 'Q2', 'Q3', 'Q4'],
    duplicates='drop'
)

# Compute phi within each quartile
results = []
for q in ['Q1', 'Q2', 'Q3', 'Q4']:
    subset = df[df['difficulty_quartile'] == q]
    phi, p = compute_phi(subset['truthfulness'], subset['robustness'])
    results.append({'quartile': q, 'phi': phi, 'p': p})
```

---

### 3. Stratified Sampling Implementation

**Library: sklearn + pandas**
- **Stratification:** `df.groupby('difficulty_quartile').apply(lambda x: x.sample(frac=1.0))`
- **Purpose:** Ensure balanced sampling across difficulty levels
- **Validation:** Check quartile counts remain balanced

**Key Pattern (from Exa search):**
```python
from sklearn.model_selection import StratifiedShuffleSplit

# Stratified split preserving difficulty distribution
splitter = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
for train_idx, test_idx in splitter.split(X, difficulty_bins):
    train_data = data.iloc[train_idx]
    test_data = data.iloc[test_idx]
```

---

### 4. Confounding Control Methods

**Papers Found:**
1. **"Paired evaluation of ML models characterizes effects of confounders"** (PMC)
   - Method: Stratified analysis + partial correlation
   - Validation: Compare effect sizes before/after controlling

2. **"Using permutations to detect confounding in ML predictions"** (arXiv)
   - Method: Permutation testing to validate confounder removal
   - Application: Ensure difficulty is truly controlled

3. **"ILDAE: Instance-Level Difficulty Analysis"** (ACL 2022)
   - Method: Item Response Theory (IRT) for difficulty scoring
   - Finding: Instance difficulty varies widely in evaluation benchmarks

**Key Takeaway:** Use BOTH partial correlation AND stratified analysis as dual validation

---

## Implementation Strategy for H-M1

### Primary Analysis: Partial Correlation
1. Extract coupling data from h-e1 (6 significant pairs)
2. Compute difficulty scores (model confidence from logprobs)
3. Run `pingouin.partial_corr()` for each dimension pair controlling for difficulty
4. **Success Criterion:** Partial phi ≥ 0.25 for ≥2 pairs

### Secondary Analysis: Stratified Validation
1. Bin instances into difficulty quartiles (Q1-Q4)
2. Compute phi coefficient within each quartile
3. **Validation:** Coupling persists in ≥3 quartiles (not just easy/hard extremes)

### Tertiary Analysis: Effect Size Comparison
1. Compare raw phi (h-e1) vs partial phi (h-m1)
2. **Expectation:** Partial phi should be 60-80% of raw phi (not <20%)
3. **Interpretation:** 
   - If partial phi ≥ 0.25: Difficulty-independent coupling confirmed
   - If partial phi 0.15-0.24: Partial coupling (route to Phase 2A-Dialogue)
   - If partial phi < 0.15: Spurious coupling (route to Phase 0)

---

## Dataset Adaptation

**Challenge:** h-e1 used synthetic data (MultiTrust gated)

**Solution for h-m1:**
1. Extend h-e1 synthetic data generator to include difficulty scores
2. Simulate difficulty distribution (normal: mean=0.5, std=0.15)
3. Ensure difficulty is INDEPENDENT of coupling structure (no spurious correlation)
4. Validation: Correlation(difficulty, truthfulness) < 0.2, etc.

**Synthetic Difficulty Generation:**
```python
# Independent difficulty (NOT correlated with dimensions)
difficulty = np.random.normal(loc=0.5, scale=0.15, size=500).clip(0, 1)

# Validation: ensure independence
assert np.abs(np.corrcoef(difficulty, truthfulness)[0,1]) < 0.2
assert np.abs(np.corrcoef(difficulty, robustness)[0,1]) < 0.2
```

**Real Data Path (Phase 5):** Request MultiTrust access, extract logprobs from API

---

## Code Examples Extracted

### Pingouin Partial Correlation
**Source:** https://pingouin-stats.org/generated/pingouin.partial_corr.html
```python
import pingouin as pg

# Single covariate
pg.partial_corr(data=df, x='x', y='y', covar='cv1').round(3)
#           n      r          CI95  p_val
# pearson  30  0.568  [0.25, 0.77]  0.001

# Multiple covariates
pg.partial_corr(
    data=df, 
    x='x', 
    y='y', 
    covar=['cv1', 'cv2', 'cv3'], 
    method='pearson'
).round(3)
```

### Stratified Quartile Analysis
**Source:** Statology + StackOverflow
```python
import pandas as pd
import numpy as np

# Create quartile bins
bin_count = 4
bin_numbers = pd.qcut(
    x=difficulty_scores, 
    q=bin_count, 
    labels=['Q1', 'Q2', 'Q3', 'Q4'],
    duplicates='drop'
)

# Analyze within each quartile
for q in ['Q1', 'Q2', 'Q3', 'Q4']:
    subset = df[df['quartile'] == q]
    # Run phi coefficient analysis on subset
```

### Difficulty Independence Validation
**Source:** Confounding control papers
```python
# Check difficulty is not spuriously correlated with dimensions
correlations = {
    dim: np.corrcoef(df[dim], df['difficulty'])[0, 1]
    for dim in ['truthfulness', 'robustness', 'fairness', 'safety', 'privacy']
}

# All should be < 0.2 (weak/no correlation)
assert all(abs(r) < 0.2 for r in correlations.values()), \
    "Difficulty spuriously correlated with dimensions!"
```

---

## Experiment Design Implications

### Dataset Requirements
- **Same 500 instances from h-e1** (continuity)
- **Add difficulty scores** (simulated or from logprobs)
- **Validate independence** (difficulty uncorrelated with binary labels)

### Metrics
- **Primary:** Partial phi coefficient (pingouin output)
- **Secondary:** Quartile-stratified phi values
- **Validation:** Raw phi vs partial phi comparison

### Success Criteria (from 02b_verification_plan.md)
- **PASS:** Partial phi ≥ 0.25 for ≥2 dimension pairs
- **PARTIAL:** Partial phi 0.15-0.24 → Route to Phase 2A-Dialogue
- **FAIL:** Partial phi < 0.15 → Route to Phase 0

### Computational Cost
- **Runtime:** ~1 second (statistical analysis, no API calls)
- **Dependencies:** pingouin, pandas, scipy, numpy
- **Data:** Reuse h-e1 outputs + add difficulty column

---

## Risks & Mitigations

**R6: Coupling disappears with difficulty control (40% likelihood)**
- **Detection:** Partial phi < 0.2 for all pairs
- **Mitigation:** Dual validation (partial corr + stratified analysis)
- **Route:** Phase 2A-Dialogue if partial, Phase 0 if complete failure

**R2: Difficulty proxy validity (60% likelihood)**
- **Risk:** Simulated difficulty may not match real difficulty patterns
- **Mitigation:** Use TWO methods (partial correlation + stratified)
- **Validation:** Compare results across methods (should agree)

**R-NEW: Synthetic data bias**
- **Risk:** Difficulty artificially independent (not realistic)
- **Mitigation:** Add controlled correlation (0.1-0.15) between difficulty and dimensions
- **Validation:** Real data comparison in Phase 5

---

## References

### Implementation Libraries
1. **Pingouin:** https://pingouin-stats.org/generated/pingouin.partial_corr.html
2. **Pandas qcut:** https://pandas.pydata.org/docs/reference/api/pandas.qcut.html
3. **Sklearn StratifiedShuffleSplit:** https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedShuffleSplit.html

### Academic Sources
1. **"The LLM Already Knows: Estimating Difficulty"** (EMNLP 2025)
   - Method: Confidence scores as difficulty proxy
2. **"ILDAE: Instance-Level Difficulty Analysis"** (ACL 2022)
   - Finding: Wide difficulty variation in benchmarks
3. **"Paired evaluation characterizes confounders"** (PMC)
   - Method: Stratified + partial correlation dual validation
4. **"Understanding Deep Learning Through Test Set Difficulty"** (D18)
   - Psychometric approach to difficulty measurement

### Code Examples
1. **Pingouin partial_corr examples:** https://www.statology.org/partial-correlation-python/
2. **Stratified sampling:** https://stackoverflow.com/questions/44114463/stratified-sampling-in-pandas
3. **Difficulty binning:** https://towardsdatascience.com/straightforward-stratification-bb0dcfcaf9ef

---

**Next Steps:**
1. Synthesize experiment specification (Step 06)
2. Design dual-validation protocol (partial + stratified)
3. Extend h-e1 data generator with difficulty scores
4. Define success criteria thresholds

**Research Complete:** 2026-08-19
