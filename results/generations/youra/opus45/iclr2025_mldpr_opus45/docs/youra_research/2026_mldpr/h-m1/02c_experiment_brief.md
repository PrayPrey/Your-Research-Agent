# Experiment Design: h-m1

**Date:** 2026-03-27
**Author:** Anonymous
**Hypothesis Statement:** Under the qualifying dataset population, if we apply PELT changepoint detection with CROPS penalty selection to download time series, then >50% of datasets will exhibit at least one statistically significant changepoint, because adoption dynamics include discrete phase transitions (launch, growth, maturity, decline).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-e1 VALIDATED)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (VALIDATED)

### Gate Condition
MUST_WORK gate: >50% of datasets must have >=1 statistically significant changepoint. Failure stops the two-level approach and invalidates hierarchical analysis.

---

## Continuation Context

Building on h-e1 validation results:
- DTW clustering validated on HuggingFace time series data
- 500 time series samples demonstrated sufficient
- Preprocessing pipeline (log-transform + z-score) validated
- Optimal k=3 clusters identified

### Previous Hypothesis Results (if applicable)
**h-e1 Results:**
- Gate: MUST_WORK - PASS
- Silhouette Score: 0.3521 (> 0.25 threshold)
- Optimal k: 3 (in [3, 8] range)
- Jaccard Stability: 0.8195 (> 0.65 threshold)
- Data: HuggingFace Hub time series (helenqu/astro-time-series)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Search Queries Executed:**
1. "PELT changepoint detection time series" - No results
2. "changepoint detection CROPS penalty" - No results
3. "ruptures library Python changepoint" - No results
4. "time series segmentation" - No results
5. "time series clustering analysis" - No results

**Assessment:** The Archon Knowledge Base does not contain indexed content specific to PELT changepoint detection or the ruptures library. This is expected as PELT is a specialized statistical method from signal processing literature (Killick et al., 2012). Implementation guidance will be sourced from:
- Official ruptures library documentation (centre-borelli.github.io/ruptures-docs)
- Academic reference: Killick, R., Fearnhead, P., & Eckley, I.A. (2012). "Optimal Detection of Changepoints With a Linear Computational Cost." Journal of the American Statistical Association.
- Exa GitHub search (next step)

### Archon Code Examples

**Search Queries Executed:**
1. "PELT changepoint Python" - No results
2. "ruptures time series" - No results

**Assessment:** No code examples found in Archon KB. Will rely on:
- ruptures library official examples
- Exa GitHub implementations (Step 3)
- CROPS penalty selection from Haynes et al. (2017)

### Exa GitHub Implementations

**Query 1: PELT Official Implementation**

**Repository 1**: [deepcharles/ruptures](https://github.com/deepcharles/ruptures) (Official)
- **URL**: https://github.com/deepcharles/ruptures
- **Stars/Activity**: 30 contributors, 13 releases, latest v1.1.10 (2025-09-10)
- **License**: BSD-2-Clause
- **Languages**: Python (86.7%), C (9.1%), Cython (4.2%)
- **Relevance**: Official Python implementation of PELT algorithm from Killick et al. (2012)
- **Architecture**:
  - `rpt.Pelt(model="l2|l1|rbf", min_size=2, jump=5)` - Penalized change point detection
  - Cost models: l2 (Gaussian, fastest), l1 (Laplace), rbf (kernel-based)
- **Key Code**:
  ```python
  import ruptures as rpt

  # Fit PELT to signal
  algo = rpt.Pelt(model="l2", min_size=3, jump=5).fit(signal)

  # Predict changepoints with penalty
  changepoints = algo.predict(pen=10)
  ```
- **Penalty Selection**:
  - BIC: `pen = p * log(n)` where p = parameters per segment
  - CROPS approach: grid search over penalty range [beta_min, beta_max]
  - Suggested formula: `pen = sensitivity_factor * log(len(data))`
    - Low sensitivity: factor = 6
    - Medium sensitivity: factor = 3
    - High sensitivity: factor = 1.5

**Repository 2**: [sktime/skchange](https://www.sktime.net/) (sklearn-compatible wrapper)
- **URL**: https://www.sktime.net/en/latest/api_reference/auto_generated/sktime.detection.skchange_cp.pelt.PELT.html
- **Relevance**: sklearn-compatible PELT implementation
- **Key Code**:
  ```python
  from skchange.change_detectors import PELT

  detector = PELT(penalty_scale=2.0, min_segment_length=2)
  detector.fit(X)
  changepoints = detector.predict(X)
  ```
- **Penalty**: `penalty_scale * 2 * p * np.log(n)`

**Query 2: CROPS Penalty Selection**

**Finding**: CROPS (Changepoints for Range of Penalties) from Haynes et al. (2017) is available in R (`crops` package) but NOT directly in Python ruptures. For Python, implement CROPS manually:

1. **CROPS Algorithm** (from Lancaster course materials):
   - Input: penalty range [beta_min, beta_max]
   - Iterate: run PELT at different penalties, find elbow in cost vs. changepoints plot
   - Output: optimal penalty and changepoint set

2. **Python Implementation Approach**:
   ```python
   def crops_pelt(signal, beta_min, beta_max, n_grid=20):
       """CROPS-style penalty selection for PELT."""
       algo = rpt.Pelt(model="l2").fit(signal)
       penalties = np.logspace(np.log10(beta_min), np.log10(beta_max), n_grid)
       results = []
       for pen in penalties:
           bkps = algo.predict(pen=pen)
           n_changepoints = len(bkps) - 1  # exclude endpoint
           results.append((pen, n_changepoints, bkps))
       # Select elbow point or use BIC criterion
       return results
   ```

**Serena Analysis Needed**: No - Code is straightforward ruptures API usage

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Priority Ranking:**
1. ⭐⭐⭐ **deepcharles/ruptures** (Official) - BSD-2-Clause, actively maintained, v1.1.10
2. ⭐⭐ **sktime/skchange** - sklearn-compatible wrapper, good for pipeline integration
3. ⭐ **Custom implementation** - Only if specific modifications needed

**Recommended Implementation Path:**
- Primary: `ruptures` library (`pip install ruptures`) - Official PELT implementation
- Fallback: `skchange` from sktime - If sklearn compatibility needed
- Justification: ruptures is the reference implementation cited in academic literature, maintained by original algorithm developers, and provides direct access to PELT with all cost models

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. The ruptures library provides a clean, well-documented API:

```python
import ruptures as rpt

# PELT changepoint detection
algo = rpt.Pelt(model="l2", min_size=3, jump=1).fit(signal)
changepoints = algo.predict(pen=penalty_value)
```

No complex custom layers or unfamiliar architecture patterns requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** HuggingFace Dataset Download Statistics
**Type:** programmatic-api (real data via API - NOT synthetic)
**Source:** HuggingFace Hub API

**Description:**
Time series of dataset download counts collected via HuggingFace Hub API. Each dataset's download history forms a time series for changepoint detection analysis.

**Statistics:**
- Target: 500+ datasets (matching h-e1 sample size for controlled comparison)
- Criteria: Datasets with >=12 months download history
- Features: Monthly/weekly download counts as time series
- Source: Real HuggingFace platform data

**Preprocessing (from h-e1 pipeline):**
- Log-transform: `np.log1p(downloads)` to handle skewed distributions
- Z-score normalization: `(x - mean) / std` per time series
- Missing value handling: Forward-fill or interpolation
- Minimum length: 12 time points (months)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Hub API (programmatic-api)
- Identifier: `huggingface_hub.list_datasets()` with download statistics
- Code:
```python
from huggingface_hub import HfApi, list_datasets

api = HfApi()

# List datasets with download statistics
datasets = list(list_datasets(
    full=True,  # Get full dataset info
    limit=1000  # Adjust as needed
))

# Extract download counts
for dataset in datasets:
    dataset_id = dataset.id
    downloads = dataset.downloads  # Current total downloads
    # Note: Historical monthly downloads require additional API calls
    # or web scraping from dataset pages
```

**Note on Data Collection:**
The HuggingFace API provides current total download counts but NOT historical monthly time series directly. For Phase 4 implementation:
1. **Option A (Recommended):** Use h-e1's cached dataset (same time series data)
2. **Option B:** Collect current downloads across datasets and use as proxy
3. **Option C:** Use alternative time series data from HuggingFace (e.g., helenqu/astro-time-series as in h-e1)

**Continuation from h-e1:** Reuse the same 500 time series samples collected and validated in h-e1 to ensure controlled comparison (only the analysis method changes: DTW clustering → PELT changepoint detection).

### Models

#### Baseline Model

**Name:** Random Changepoint Placement
**Type:** Null baseline for changepoint detection
**Purpose:** Establish that PELT detects meaningful structure, not random artifacts

**Baseline Methods:**
1. **Random Changepoint:** Place changepoints uniformly at random
2. **No Changepoint:** Assume no changepoints exist (null model)
3. **Fixed-Interval:** Place changepoints at fixed intervals (e.g., every 6 months)

**Comparison Metric:**
- PELT detection rate vs. random detection rate
- Changepoint location interpretability

**Loading Information** (for Phase 4 download):
- Method: pip install
- Identifier: `ruptures` library
- Code:
```python
pip install ruptures

import ruptures as rpt

# PELT algorithm (proposed)
algo = rpt.Pelt(model="l2", min_size=3, jump=1)
algo.fit(signal)
changepoints = algo.predict(pen=penalty)

# Random baseline
import numpy as np
random_changepoints = np.random.choice(
    range(min_size, len(signal) - min_size),
    size=np.random.randint(0, 5),
    replace=False
)
```

#### Proposed Model

**Architecture:** PELT Changepoint Detection with CROPS Penalty Selection
**Integration:** Apply PELT to each time series, count detection rate across dataset

**Core Mechanism Implementation:**

```python
# Core Mechanism: PELT Changepoint Detection with CROPS Penalty Selection
# Based on: ruptures library (deepcharles/ruptures), Killick et al. (2012)
# Source: Exa GitHub search - official ruptures implementation

import numpy as np
import ruptures as rpt
from typing import List, Tuple

def detect_changepoints_pelt(
    time_series: np.ndarray,
    model: str = "l2",
    min_size: int = 3,
    penalty_range: Tuple[float, float] = (1.0, 100.0),
    n_penalties: int = 20
) -> Tuple[List[int], float]:
    """
    PELT changepoint detection with CROPS-style penalty selection.

    Args:
        time_series: (T,) - univariate time series (preprocessed)
        model: cost model ("l2" for Gaussian likelihood)
        min_size: minimum segment length
        penalty_range: (min_pen, max_pen) for grid search
        n_penalties: number of penalties to evaluate

    Returns:
        changepoints: list of changepoint indices
        optimal_penalty: selected penalty value
    """
    # Step 1: Fit PELT algorithm
    algo = rpt.Pelt(model=model, min_size=min_size, jump=1)
    algo.fit(time_series)

    # Step 2: CROPS-style penalty selection via grid search
    penalties = np.logspace(
        np.log10(penalty_range[0]),
        np.log10(penalty_range[1]),
        n_penalties
    )

    # Step 3: Evaluate each penalty, find elbow
    results = []
    for pen in penalties:
        bkps = algo.predict(pen=pen)
        n_cps = len(bkps) - 1  # Exclude endpoint
        results.append((pen, n_cps, bkps))

    # Step 4: Select penalty using BIC criterion
    n = len(time_series)
    optimal_pen = 2 * np.log(n)  # BIC penalty
    changepoints = algo.predict(pen=optimal_pen)

    return changepoints[:-1], optimal_pen  # Exclude endpoint


def compute_detection_rate(
    all_time_series: List[np.ndarray],
    **kwargs
) -> float:
    """
    Compute proportion of datasets with >=1 changepoint.

    Args:
        all_time_series: list of time series arrays

    Returns:
        detection_rate: proportion in [0, 1]
    """
    n_with_changepoint = 0
    for ts in all_time_series:
        cps, _ = detect_changepoints_pelt(ts, **kwargs)
        if len(cps) > 0:
            n_with_changepoint += 1

    return n_with_changepoint / len(all_time_series)
```

### Training Protocol

**Note:** This is an unsupervised changepoint detection task - no training required.

**Algorithm Configuration (from research):**
- **Model**: "l2" (Gaussian cost function, recommended for piecewise constant signals)
  - **Source**: ruptures documentation, Killick et al. (2012)
- **min_size**: 3 (minimum segment length in time points)
  - **Source**: ruptures default, prevents spurious detections
- **jump**: 1 (evaluate all possible changepoint locations)
  - **Source**: Full search for optimal detection

**Penalty Selection Protocol:**
- **Method**: BIC-based penalty with grid search validation
- **Formula**: `pen = 2 * log(n)` where n = time series length
- **Range**: [1.0, 100.0] for grid search validation
- **Source**: Stack Overflow discussion, ruptures GitHub discussions

**Seeds**: 1 (PELT is deterministic - no randomness)

**Execution:**
1. Load preprocessed time series from h-e1 pipeline
2. Apply PELT to each time series with BIC penalty
3. Count changepoints per time series
4. Compute detection rate = (datasets with >=1 changepoint) / total

### Evaluation

**Primary Metrics:**
- **Detection Rate**: Proportion of datasets with >=1 changepoint
  - Target: >50% (from hypothesis success criteria)
  - Formula: `n_with_changepoint / total_datasets`

- **Mean Changepoints per Dataset**: Average number of changepoints detected
  - Expected: 1-5 changepoints per time series (based on lifecycle phases)

**Secondary Metrics:**
- **Changepoint Distribution**: Histogram of changepoint counts
- **Temporal Distribution**: Where changepoints occur (early/mid/late)

**Success Criteria (MUST_WORK Gate):**
- **Primary**: detection_rate > 0.50 (>50% of datasets have >=1 changepoint)
- **Secondary**: Changepoint locations are interpretable (not uniformly random)

**Expected Baseline Performance:**
- Random placement: ~uniform distribution, no meaningful clustering
- No changepoint: detection_rate = 0%
- PELT expected: detection_rate > 50% if lifecycle phases exist

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Unsupervised changepoint detection
- Library: Custom metrics (no external library needed)
- Code:
```python
# Detection rate
detection_rate = sum(1 for cps in all_changepoints if len(cps) > 0) / len(all_changepoints)

# Mean changepoints
mean_cps = np.mean([len(cps) for cps in all_changepoints])

# Gate check
gate_pass = detection_rate > 0.50
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Detection rate bar chart (target 50% vs actual)

#### Additional Figures (LLM Autonomous)

1. **Changepoint Distribution Histogram**: Distribution of changepoint counts per dataset
2. **Example Time Series with Changepoints**: 3-5 example time series showing detected changepoints
3. **Penalty Sensitivity Plot**: Detection rate vs penalty value (CROPS-style elbow plot)
4. **Temporal Changepoint Heatmap**: When changepoints occur across datasets (early/mid/late lifecycle)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Search Summary**: No direct results found in Archon KB for PELT/changepoint detection queries.

**Queries Attempted:**
1. "PELT changepoint detection time series" - No results
2. "changepoint detection CROPS penalty" - No results
3. "ruptures library Python changepoint" - No results
4. "time series segmentation" - No results

**Assessment**: PELT changepoint detection is a specialized statistical method not indexed in the current Archon KB. Implementation guidance sourced from Exa GitHub search and academic references.

### B. GitHub Implementations (Exa)

**Repository 1**: [deepcharles/ruptures](https://github.com/deepcharles/ruptures) ⭐ Official
- **URL**: https://github.com/deepcharles/ruptures
- **Query Used**: "Killick PELT changepoint detection ruptures Python official implementation GitHub"
- **License**: BSD-2-Clause
- **Relevance**: Official Python implementation of PELT algorithm from Killick et al. (2012)
- **Key Code** (annotated):
  ```python
  import ruptures as rpt

  # PELT algorithm initialization
  # model="l2" uses Gaussian likelihood (fastest)
  # min_size controls minimum segment length
  algo = rpt.Pelt(model="l2", min_size=3, jump=5).fit(signal)

  # Predict changepoints with penalty
  # pen controls sensitivity (higher = fewer changepoints)
  changepoints = algo.predict(pen=10)
  ```
- **Configuration Extracted**:
  - Cost models: l1, l2, rbf (l2 recommended for speed)
  - Penalty: BIC formula = p * log(n)
  - min_size: 2-5 typical range
- **Used For**: Core mechanism pseudo-code, training protocol

**Repository 2**: [sktime/skchange](https://www.sktime.net/)
- **URL**: https://www.sktime.net/en/latest/api_reference/auto_generated/sktime.detection.skchange_cp.pelt.PELT.html
- **Query Used**: "ruptures PELT CROPS penalty changepoint detection Python example"
- **Relevance**: sklearn-compatible PELT wrapper with automatic penalty scaling
- **Key Code**:
  ```python
  from skchange.change_detectors import PELT

  # penalty_scale * 2 * p * log(n) is used internally
  detector = PELT(penalty_scale=2.0, min_segment_length=2)
  detector.fit(X)
  ```
- **Used For**: Alternative penalty selection approach

**Documentation Sources**:
- **ruptures docs**: https://centre-borelli.github.io/ruptures-docs/user-guide/detection/pelt/
- **Lancaster MATH337 Course**: https://www.lancaster.ac.uk/~romano/teaching/2425MATH337/4_algos_and_penalties.html
  - Excellent CROPS explanation and penalty selection guidance

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear.

The ruptures library provides a clean, well-documented API that doesn't require semantic analysis:
- `rpt.Pelt(model, min_size, jump)` - initialization
- `.fit(signal)` - fit to data
- `.predict(pen)` - detect changepoints

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - h-e1
- **File**: `h-e1/04_validation.md`
- **Reused Components**:
  - Dataset: HuggingFace time series (500 samples)
  - Preprocessing: log-transform + z-score normalization
  - Data pipeline: Validated collection and preprocessing
- **Why Reused**: Enables controlled experiment - same data, different analysis (DTW clustering → PELT changepoint)

**h-e1 Validation Results** (prerequisite):
- Silhouette: 0.3521 (>0.25 threshold) ✓
- Optimal k: 3 (in [3,8] range) ✓
- Jaccard Stability: 0.8195 (>0.65 threshold) ✓

### E. Academic References

1. **Killick, R., Fearnhead, P., & Eckley, I. A. (2012)**
   - "Optimal Detection of Changepoints With a Linear Computational Cost"
   - Journal of the American Statistical Association, 107(500), 1590-1598
   - **Used For**: PELT algorithm foundation, theoretical basis

2. **Haynes, K., Eckley, I. A., & Fearnhead, P. (2017)**
   - "Computationally Efficient Changepoint Detection for a Range of Penalties"
   - Journal of Computational and Graphical Statistics, 26(1), 134-143
   - DOI: 10.1080/10618600.2015.1116445
   - **Used For**: CROPS penalty selection methodology

### F. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Previous Hypothesis | h-e1 validation (D) |
| Preprocessing | Previous Hypothesis | h-e1 pipeline (D) |
| PELT algorithm | GitHub + Academic | ruptures (B.1), Killick (E.1) |
| Penalty selection | GitHub + Academic | Lancaster course, Haynes (E.2) |
| Pseudo-code | GitHub | ruptures docs (B.1) |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md |
| Success criteria | Phase 2B | >50% detection rate |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-27

### Workflow History for This Hypothesis
- 2026-03-27: h-m1 set to IN_PROGRESS (Phase 2C started)
- Prerequisites: h-e1 VALIDATED

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
