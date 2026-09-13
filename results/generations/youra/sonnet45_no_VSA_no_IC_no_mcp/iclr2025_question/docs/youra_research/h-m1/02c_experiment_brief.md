# Experiment Design: H-M1

**Date:** 2026-08-25
**Author:** Anonymous
**Hypothesis Statement:** Under retrospective validation using the corpus from H-E1, if we measure correlation between 10-sample overhead (O_10) and full-dataset overhead (O_full), then correlation r will exceed 0.7, because overhead operations (like KL divergence in h-e1) scale predictably across sample sizes.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests correlation mechanism for overhead scaling.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** YES (H-E1 completed with PASS)
**Gate Status:** MUST_WORK (validation required for dependent hypotheses)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (corpus collection)

### Gate Condition
**Type:** MUST_WORK
**Failure Impact:** Predictive scaling invalid → framework collapses
**Success Criteria:**
- Primary: Correlation r >0.7 between O_10 and O_full
- Secondary: Scaling factor k consistent within hypothesis types (CV <30%)

---

## Continuation Context

This hypothesis tests the core assumption (A1) that micro-pilot overhead correlates with full-scale overhead. H-E1 provided the corpus of 32 hypotheses with both measurements. Without this correlation, the entire Pilot-Driven Viability Gates framework cannot extrapolate from micro-pilot (Gate 1) to full-scale predictions.

### Previous Hypothesis Results (H-E1)

**Hypothesis:** H-E1 (Retrospective ML Projects Corpus Exists)
**Result:** ✅ PASS
**Key Outputs:**
- Valid corpus: 32 hypotheses with dual-scale overhead data
- Stratification: Low=11, Mid=11, High=10 (CV=0.044)
- Data location: `experiments/h-e1_corpus_collection/code/experiments/h-e1_corpus_collection/data/retrospective_corpus/papers_metadata.json`
- Overhead fields available: `micro_pilot.overhead_percent` (O_10) and `full_scale.overhead_percent` (O_full)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP service unavailable - relying on standard statistical analysis libraries*

### Archon Code Examples

*MCP service unavailable - using scipy.stats and sklearn.linear_model standard implementations*

### Exa GitHub Implementations

*MCP service unavailable - correlation analysis is standard statistical operation*

### 🎯 Implementation Priority Assessment

**Implementation Approach:** Standard statistical analysis (correlation + linear regression)

**Recommended Implementation Path:**
- Primary: scipy.stats.pearsonr for correlation, sklearn.linear_model.LinearRegression for scaling factor k
- Fallback: numpy correlation coefficient (np.corrcoef) if sklearn unavailable
- Justification: Correlation analysis is well-established statistical operation, no need for custom implementation or MCP search

### Code Analysis (Serena MCP)

*Serena MCP unavailable - correlation implementation is standard library usage*

---

## Experiment Specification

### Dataset

**Name:** Retrospective ML Overhead Corpus v1.0 (from H-E1)
**Type:** custom
**Source:** Local file from H-E1 validation
**Size:** 32 papers with micro-pilot and full-scale overhead measurements
**Format:** JSON with fields: paper_id, title, venue, year, hypothesis_type, overhead_measurements

**Data Structure:**
```json
{
  "overhead_measurements": {
    "micro_pilot": {
      "sample_size": int,
      "overhead_percent": float  // O_10
    },
    "full_scale": {
      "sample_size": int,
      "overhead_percent": float  // O_full
    }
  },
  "hypothesis_type": str  // attention, gradient, regularization, normalization
}
```

**Stratification:**
- Low overhead (<20%): 11 hypotheses
- Mid overhead (20-80%): 11 hypotheses
- High overhead (>80%): 10 hypotheses

**Loading Information** (for Phase 4 download):
- Method: Local file read
- Identifier: `experiments/h-e1_corpus_collection/code/experiments/h-e1_corpus_collection/data/retrospective_corpus/papers_metadata.json`
- Code: 
```python
import json
with open('papers_metadata.json', 'r') as f:
    corpus = json.load(f)
```

### Models

#### Baseline Model

**Type:** Statistical null hypothesis (random correlation)
**Expected Baseline:** r = 0 (no correlation between O_10 and O_full)
**Justification:** If overhead scaling is random/unpredictable, correlation would be near zero.

**Loading Information** (for Phase 4 download):
- Method: N/A (baseline is statistical comparison)
- Identifier: N/A
- Code: `baseline_r = 0  # Null hypothesis: no correlation`

#### Proposed Model

**Architecture:** Pearson correlation + Linear regression scaling model

**Core Mechanism Implementation:**

```python
import numpy as np
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression

# Extract overhead arrays from corpus
o10_values = [paper['overhead_measurements']['micro_pilot']['overhead_percent'] 
              for paper in corpus]
ofull_values = [paper['overhead_measurements']['full_scale']['overhead_percent'] 
                for paper in corpus]

# Compute Pearson correlation
r, p_value = pearsonr(o10_values, ofull_values)

# Fit linear regression: O_full = k × O_10
X = np.array(o10_values).reshape(-1, 1)
y = np.array(ofull_values)
model = LinearRegression()
model.fit(X, y)
k = model.coef_[0]  # Scaling factor

# Per-type analysis
hypothesis_types = set(paper['hypothesis_type'] for paper in corpus)
k_by_type = {}
for htype in hypothesis_types:
    type_papers = [p for p in corpus if p['hypothesis_type'] == htype]
    o10_type = [p['overhead_measurements']['micro_pilot']['overhead_percent'] 
                for p in type_papers]
    ofull_type = [p['overhead_measurements']['full_scale']['overhead_percent'] 
                  for p in type_papers]
    X_type = np.array(o10_type).reshape(-1, 1)
    y_type = np.array(ofull_type)
    model_type = LinearRegression()
    model_type.fit(X_type, y_type)
    k_by_type[htype] = model_type.coef_[0]

# Compute coefficient of variation (CV) for k across types
cv = np.std(list(k_by_type.values())) / np.mean(list(k_by_type.values()))
```

### Training Protocol

**N/A** - Statistical analysis, not ML training.

**Analysis Protocol:**
1. Load corpus from H-E1 output (32 papers)
2. Extract O_10 and O_full arrays
3. Compute global Pearson correlation r
4. Fit global linear regression for scaling factor k
5. Group papers by hypothesis_type
6. Compute per-type scaling factors k_attention, k_gradient, k_regularization, k_normalization
7. Compute coefficient of variation (CV) across per-type k values
8. Statistical significance test: p-value <0.05 for correlation

### Evaluation

**Primary Metric:** Pearson correlation coefficient r
- **Success Threshold:** r >0.7
- **Baseline:** r = 0 (null hypothesis)
- **Statistical Test:** p-value <0.05 for significance

**Secondary Metrics:**
1. **Scaling Factor k:** Slope of linear regression O_full = k × O_10
   - **Interpretation:** Average multiplier from micro-pilot to full-scale
   
2. **Per-Type Scaling Consistency:** Coefficient of variation (CV) of k across hypothesis types
   - **Success Threshold:** CV <30% (consistent scaling within types)
   - **Failure Threshold:** CV >50% (requires per-type calibration)

3. **R² Score:** Goodness of fit for linear regression
   - **Target:** R² >0.5 (linear model explains >50% variance)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical correlation analysis
- Library: scipy.stats (pearsonr), sklearn.metrics (r2_score)
- Code:
```python
from scipy.stats import pearsonr
from sklearn.metrics import r2_score
import numpy as np

# Primary metric
r, p_value = pearsonr(o10_values, ofull_values)

# Secondary metrics
r2 = r2_score(ofull_values, model.predict(X))
cv = np.std(list(k_by_type.values())) / np.mean(list(k_by_type.values()))
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Correlation Scatter Plot**: O_10 vs O_full with regression line
  - X-axis: Micro-pilot overhead O_10 (%)
  - Y-axis: Full-scale overhead O_full (%)
  - Points colored by hypothesis type
  - Regression line with equation: O_full = k × O_10
  - Annotate r value and p-value

#### Additional Figures (LLM Autonomous)

1. **Per-Type Scaling Factors**: Bar chart of k values by hypothesis type
   - Shows consistency/variation across types
   - Horizontal line at mean k
   - Error bars if multiple papers per type

2. **Residual Plot**: Prediction error vs O_10
   - Check linearity assumption
   - Identify outliers

3. **Gate Metrics Comparison**: Bar chart
   - Metric: Pearson r
   - Baseline: 0 (null hypothesis)
   - Achieved: actual r value
   - Threshold: 0.7 (success criteria)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Pearson r >0.7 (exceeds baseline r=0 and meets success threshold)
3. p-value <0.05 (statistically significant correlation)
4. CV <30% (consistent scaling across hypothesis types)

---

## Appendix: Reference Implementations

### Standard Statistical Libraries

**scipy.stats.pearsonr:**
- Documentation: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html
- Usage: `r, p_value = pearsonr(x, y)`
- Returns correlation coefficient and two-tailed p-value

**sklearn.linear_model.LinearRegression:**
- Documentation: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html
- Usage: `model.fit(X, y); k = model.coef_[0]`
- Returns regression coefficients (slope k)

### Analysis Pattern

Standard correlation + regression workflow:
1. Extract parallel arrays (O_10, O_full)
2. Compute Pearson r and p-value
3. Fit LinearRegression to get scaling factor k
4. Group by categorical variable (hypothesis_type)
5. Compute per-group k values
6. Calculate coefficient of variation across groups

**No specialized implementation needed** - standard statistical analysis pattern.

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-25

### Workflow History for This Hypothesis

**Phase 2C Completion:**
- Experiment design completed: 2026-08-25
- MCP services unavailable (Archon, Exa, Serena)
- Experiment specification based on standard statistical analysis (scipy, sklearn)
- Prerequisites validated: H-E1 completed with corpus available

**Next Steps:**
- Phase 3: Implementation Planning (PRD, Architecture, Logic, Config generation)
- Phase 4: Code implementation and validation

---

*MCP Tools Status: Archon (unavailable), Exa (unavailable), Serena (unavailable)*
*Experiment specification uses standard statistical libraries (scipy, sklearn)*
*Next Phase: Phase 3 - Implementation Planning*
