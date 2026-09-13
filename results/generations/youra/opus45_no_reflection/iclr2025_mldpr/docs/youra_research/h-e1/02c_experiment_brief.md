# Experiment Design: H-E1

**Date:** 2026-08-18
**Author:** Anonymous
**Hypothesis Statement:** PELT change-point detection identifies statistically significant change point in aggregate Gini coefficient time series within 2019-2022 window at α=0.05
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites - first hypothesis)
**Gate Status:** MUST_WORK - PENDING

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (root hypothesis)

### Gate Condition
MUST_WORK gate: If no statistically significant change point detected in 2019-2022 at α=0.05, entire verification stops. Failure triggers PIVOT to quarterly aggregation or Bai-Perron method.

---

## Continuation Context

First hypothesis in chain - no previous context.

### Previous Hypothesis Results (if applicable)
N/A - This is the first hypothesis in the verification sequence.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

No direct PELT/change-point detection content in Archon KB. Archon primarily indexes HuggingFace, diffusers, and ML model documentation. PELT is a statistical time series method outside Archon's scope.

### Archon Code Examples

No relevant Gini coefficient or time series analysis code found in Archon index. This is expected as Archon focuses on ML model code, not statistical analysis pipelines.

### Exa GitHub Implementations

**ruptures library (PELT algorithm):**
- Source: https://github.com/deepcharles/ruptures (2K+ stars)
- Reference: Killick et al. (2012) "Optimal detection of changepoints with a linear computational cost" JASA 107(500):1590-1598
- Models: `"l1"`, `"l2"`, `"rbf"` (kernel-based)
- Complexity: O(CKn) average case

**PELT Usage Pattern:**
```python
import ruptures as rpt

# Fit PELT with rbf kernel (robust to distributional assumptions)
algo = rpt.Pelt(model="rbf", min_size=3, jump=1).fit(signal)
change_points = algo.predict(pen=penalty_value)
```

**Papers With Code Data:**
- Source: https://github.com/paperswithcode/paperswithcode-data (932 stars)
- Data: HuggingFace datasets (evaluation-tables, papers-with-abstracts)
- Format: JSON dumps with task-dataset-metric triplets
- Note: PWC API deprecated July 2025, use archived dumps

**Gini Coefficient Implementation:**
- Source: https://github.com/oliviaguest/gini, pysal/inequality
- O(n log n) implementation using sorted array formula:
```python
def gini(array):
    array = np.sort(array.flatten())
    n = array.shape[0]
    index = np.arange(1, n + 1)
    return (np.sum((2 * index - n - 1) * array)) / (n * np.sum(array))
```

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is a statistical analysis experiment, not ML model reproduction. Use established statistical libraries:
1. **ruptures** - Official PELT implementation (Killick et al. 2012)
2. **scipy.stats** - Statistical tests
3. **pysal.inequality** or custom - Gini coefficient

**Recommended Implementation Path:**
- Primary: ruptures library for PELT, custom Gini from research
- Fallback: statsmodels change-point methods if ruptures insufficient
- Justification: ruptures is the canonical PELT implementation cited in literature

### Code Analysis (Serena MCP)

Not applicable - this experiment uses established statistical libraries (ruptures, scipy) rather than custom ML models requiring codebase analysis.

---

## Experiment Specification

### Dataset

**Dataset:** Papers With Code Historical Data
**Type:** programmatic-api (archived JSON dumps)
**Source:** https://huggingface.co/datasets/pwc-archive/evaluation-tables

**Statistics:**
- Time range: 2018-2024 (monthly aggregation)
- Expected records: ~326,000 evaluation table rows
- Output: ~72 monthly Gini values (6 years × 12 months)

**Preprocessing:**
1. Download evaluation-tables.json from HuggingFace
2. Parse task-dataset-metric triplets with paper associations
3. Filter to 2018-01-01 through 2024-12-31
4. Aggregate to monthly benchmark usage counts
5. Compute monthly Gini coefficient of benchmark distribution

**Augmentation:** N/A (statistical analysis, not ML training)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `pwc-archive/evaluation-tables`
- Code:
```python
from datasets import load_dataset
# Load evaluation tables
eval_tables = load_dataset("pwc-archive/evaluation-tables")
# Or direct download:
# curl -L -O "https://huggingface.co/datasets/pwc-archive/files/resolve/main/jul-28-evaluation-tables.json.gz"
```

### Models

#### Baseline Model

**Model:** Single Monotonic Trend (Null Hypothesis H0)
**Type:** Statistical model
**Architecture:** Linear regression on Gini time series

**Description:** Fit single linear trend to entire 2018-2024 Gini series. This represents H0 (no structural break).

**Loading Information** (for Phase 4 download):
- Method: scipy
- Identifier: `scipy.stats.linregress`
- Code:
```python
from scipy.stats import linregress
slope, intercept, r_value, p_value, std_err = linregress(time_index, gini_series)
```

#### Proposed Model

**Architecture:** PELT Change-Point Detection + Segmented Trends
**Type:** Statistical model

**Description:** Apply PELT to detect change points, then fit separate linear trends to each segment. Compare fit quality via BIC.

**Core Mechanism Implementation:**

```python
# Core Mechanism: PELT Change-Point Detection on Gini Time Series
# Based on: Killick et al. (2012) JASA, ruptures library

import numpy as np
import ruptures as rpt
from scipy.stats import linregress

class GiniChangePointDetector:
    """
    Detect structural breaks in benchmark concentration time series.
    H1: Change point exists in 2019-2022 window.
    """
    def __init__(self, model="rbf", min_size=3, target_window=(2019, 2022)):
        self.algo = rpt.Pelt(model=model, min_size=min_size, jump=1)
        self.target_window = target_window
    
    def compute_gini(self, counts):
        """Gini coefficient for benchmark usage distribution."""
        counts = np.sort(counts.flatten())
        n = len(counts)
        index = np.arange(1, n + 1)
        return (np.sum((2 * index - n - 1) * counts)) / (n * np.sum(counts))
    
    def detect(self, gini_series, penalty=None):
        """
        Args:
            gini_series: (T,) array of monthly Gini values
        Returns:
            change_points: list of indices, target_hit: bool
        """
        # Auto-select penalty via BIC if not provided
        if penalty is None:
            penalty = np.log(len(gini_series)) * gini_series.var()
        
        self.algo.fit(gini_series.reshape(-1, 1))
        change_points = self.algo.predict(pen=penalty)
        
        # Check if any change point falls in target window
        # Assume monthly indices: 2019 = index 12, 2022 = index 48
        target_indices = range(12, 48)  # Adjust based on actual start date
        target_hit = any(cp in target_indices for cp in change_points[:-1])
        
        return change_points, target_hit

# Integration: Run after Gini time series computed from PWC data
```

### Training Protocol

**Note:** This is statistical analysis, not ML training. Parameters below are analysis settings.

**Algorithm:** PELT (Pruned Exact Linear Time)
- **Model:** `"rbf"` (radial basis function kernel)
- **Source:** Killick et al. (2012), ruptures default

**Penalty Selection:**
- Method: BIC-based (Bayesian Information Criterion)
- Formula: `pen = log(n) * variance(signal)`
- **Source:** ruptures documentation, standard practice

**Significance Level:** α = 0.05
- **Source:** Phase 2B success criteria

**Minimum Segment Length:** 3 months
- **Source:** Reasonable for monthly time series

**Seeds:** 1 (PELT is deterministic, no randomness)

> ⚠️ **EXISTENCE (PoC)**: Single run sufficient. PELT has no stochastic component.

### Evaluation

**Primary Metrics:**
1. **Change Point Detection:** Binary (detected in 2019-2022 or not)
2. **Statistical Significance:** p-value < 0.05 for segmented vs monotonic model comparison
3. **BIC Comparison:** BIC(segmented) < BIC(monotonic)

**Success Criteria (PoC: Direction-based):**
- Change point detected within 2019-2022 window
- Segmented model BIC < Single monotonic BIC

**Expected Baseline Performance:**
- Koch et al. (2021): Gini ~0.6-0.7 for 2015-2020
- Single monotonic trend should show R² < 0.9 if structural break exists

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: time_series_analysis
- Library: scipy.stats, custom
- Code:
```python
from scipy.stats import f_oneway
# BIC comparison for model selection
def compute_bic(residuals, n_params, n_samples):
    rss = np.sum(residuals**2)
    return n_samples * np.log(rss / n_samples) + n_params * np.log(n_samples)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart showing:
  - Change point detected (yes/no)
  - BIC comparison (segmented vs monotonic)
  - p-value for significance test

#### Additional Figures (LLM Autonomous)

Based on time series analysis nature:
1. **Gini Time Series Plot**: Monthly Gini values 2018-2024 with detected change points marked as vertical lines
2. **Segmented Fit Comparison**: Overlay of single trend vs segmented trends
3. **Residual Analysis**: Residuals from both models to visualize fit quality

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** Yes - PELT algorithm detects change points by minimizing penalized cost
- **mechanism_isolatable:** Yes - Change point indices directly reported by algorithm
- **baseline_measurable:** Yes - Single trend R² and BIC computable

### Architecture Compatibility
PELT requires 1D signal input. Gini time series is 1D (T,). Compatible.

### Activation Indicators
- **mechanism_log_message:** `"PELT detected N change point(s) at indices: [...]"`
- **tensor_shape_change:** Input (T,) → Output list of K+1 segment boundaries
- **metric_delta_expected:** If change point in 2019-2022, segmented BIC should be lower than monotonic BIC

### Failure Detection
1. No change points detected (empty list except final index)
2. Change points outside 2019-2022 window
3. Segmented BIC >= Monotonic BIC (no improvement)

### Success Criteria
- **hypothesis_support_threshold:** Change point index ∈ [12, 48] (2019-2022)
- **hypothesis_support_metric:** BIC_segmented < BIC_monotonic

### Mechanism Verification Code
```python
def verify_mechanism(change_points, gini_series, dates):
    # Check 1: Change point detected
    if len(change_points) <= 1:
        return {"status": "FAIL", "reason": "No change points detected"}
    
    # Check 2: Change point in target window
    target_cps = [cp for cp in change_points[:-1] 
                  if dates[cp].year >= 2019 and dates[cp].year <= 2022]
    if not target_cps:
        return {"status": "FAIL", "reason": "No change point in 2019-2022"}
    
    # Check 3: BIC improvement
    bic_mono = compute_bic_monotonic(gini_series)
    bic_seg = compute_bic_segmented(gini_series, change_points)
    if bic_seg >= bic_mono:
        return {"status": "FAIL", "reason": f"No BIC improvement: {bic_seg:.2f} >= {bic_mono:.2f}"}
    
    return {"status": "PASS", "change_point": target_cps[0], "bic_improvement": bic_mono - bic_seg}
```

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Change point detected in 2019-2022 window
3. BIC(segmented) < BIC(monotonic)

---

## Appendix: Reference Implementations

### PELT Implementation
- **Library:** ruptures
- **Source:** https://github.com/deepcharles/ruptures
- **Citation:** Killick, R., Fearnhead, P., & Eckley, I. (2012). Optimal detection of changepoints with a linear computational cost. JASA, 107(500), 1590-1598.
- **Documentation:** https://centre-borelli.github.io/ruptures-docs/

### Gini Coefficient
- **Library:** pysal.inequality or custom
- **Source:** https://github.com/pysal/inequality
- **Formula:** `G = (Σᵢ (2i - n - 1) * xᵢ) / (n * Σᵢ xᵢ)` for sorted array

### Papers With Code Data
- **Repository:** https://github.com/paperswithcode/paperswithcode-data
- **HuggingFace:** https://huggingface.co/datasets/pwc-archive/evaluation-tables
- **Format:** JSON with task-dataset-metric-paper associations

### Baseline Reference
- **Paper:** Koch et al. (2021) "Reduced, Reused and Recycled: The Life of a Dataset in Machine Learning Research"
- **Finding:** Gini coefficient ~0.6-0.7 for benchmark concentration 2015-2020
- **Data:** Papers With Code + Semantic Scholar

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-18

### Workflow History for This Hypothesis
- 2026-08-18: Hypothesis h-e1 set to IN_PROGRESS (Phase 2C started)
- 2026-08-18: Experiment design completed (02c_experiment_brief.md)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web Search)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
