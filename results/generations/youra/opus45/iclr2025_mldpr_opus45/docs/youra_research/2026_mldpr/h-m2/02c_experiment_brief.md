# Experiment Design: h-m2

**Date:** 2026-03-27
**Author:** Anonymous
**Hypothesis Statement:** Under the clustered dataset population, if different adoption mechanisms (benchmark designation, publication cycles, trend following) drive download behavior, then cluster centroids will exhibit distinct shape signatures measurable via shape descriptors (derivative sign patterns, peak timing, changepoint count), because mechanism differences manifest as trajectory shape differences.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Hypothesis** - Tests whether shape descriptors differentiate cluster centroids.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** Yes (h-m1 PASSED)
**Gate Status:** SHOULD_WORK (failure = documented limitation, continue)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (PELT phase detection - PASSED)

### Gate Condition
**Gate Type:** SHOULD_WORK
- If PASS: Proceed to h-m3
- If FAIL: Document limitation, continue to h-m3

---

## Continuation Context

This is a continuation experiment building on h-e1 (clustering) and h-m1 (changepoint detection).

### Previous Hypothesis Results

**h-e1 Results (DTW Clustering):**
- Silhouette Score: 0.289 (> 0.25 threshold)
- Optimal k: 4 clusters
- Jaccard Stability: 0.991 (> 0.65 threshold)
- 500 datasets analyzed

**h-m1 Results (PELT Changepoint Detection):**
- Detection Rate: 81% (> 50% threshold)
- Mean Changepoints: 0.96 per series
- 405/500 series have at least one changepoint

**Proven Components to Reuse:**
- HuggingFace dataset cache (h-e1/code/dataset_cache.json)
- Cluster assignments (k=4)
- Changepoint detection results

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Time series shape descriptors clustering**
- Limited direct matches in Archon KB (focused on diffusion models)
- Key insight: Shape-based analysis requires custom feature extraction

**Query 2: tslearn time series features**
- No direct matches for shape descriptor computation

**Note:** Archon KB does not contain time series shape descriptor cases. Research grounded in Exa findings.

### Archon Code Examples

No directly applicable code examples found in Archon KB for time series shape descriptors. Implementation will be based on Exa GitHub findings and scientific literature.

### Exa GitHub Implementations

**Repository 1**: scipy.signal.find_peaks (SciPy documentation)
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html
- **Relevance**: Peak detection for time series shape analysis
- **Key Code**:
  ```python
  from scipy.signal import find_peaks
  peaks, properties = find_peaks(x, prominence=1, width=20)
  # properties contains: prominences, widths, left_ips, right_ips
  ```
- **Used For**: Peak timing shape descriptor

**Repository 2**: tslearn - Time Series Clustering
- **URL**: https://tslearn.readthedocs.io/en/stable/user_guide/clustering.html
- **Relevance**: KShape and TimeSeriesKMeans for shape-based clustering
- **Key Code**:
  ```python
  from tslearn.clustering import KShape, TimeSeriesKMeans
  ks = KShape(n_clusters=3, verbose=True)
  y_pred = ks.fit_predict(X_train)
  # Access cluster_centers_ for centroid analysis
  ```
- **Used For**: Understanding shape-based clustering centroids

**Repository 3**: Cluster Evaluation Metrics
- **URL**: Various (Medium, sklearn documentation)
- **Relevance**: Inter-cluster vs intra-cluster variance computation
- **Key Insight**:
  - Silhouette score measures cluster separation
  - Davies-Bouldin index measures average similarity ratio
  - Inter-cluster variance / intra-cluster variance ratio > 2 indicates good separation

**Serena Analysis Needed**: false

### Implementation Priority Assessment

**CRITICAL: For shape descriptor experiments, use standard scipy/numpy for custom implementation**

**Recommended Implementation Path:**
- Primary: scipy.signal.find_peaks + numpy gradient for shape descriptors
- Fallback: tslearn shape features if available
- Justification: Standard scientific Python libraries, well-documented, easily reproducible

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Shape descriptors use standard numpy/scipy operations that don't require deep code analysis.

---

## Experiment Specification

### Dataset

**Dataset**: HuggingFace Dataset Download Statistics (reused from h-e1/h-m1)
**Type**: custom (programmatic-api)

**Loading Information**:
- Method: Reuse cached data from h-e1
- Identifier: h-e1/code/dataset_cache.json
- Code:
  ```python
  import json
  with open("../h-e1/code/dataset_cache.json", "r") as f:
      data = json.load(f)
  # Contains: download time series for 500 datasets
  ```

**Statistics**:
- Total datasets: 500
- Time series length: Variable (normalized to 52 weeks)
- Clusters: k=4 (from h-e1)

**Preprocessing**:
- Already preprocessed in h-e1: log-transform, z-score normalization
- Reuse cluster assignments

**Augmentation**: None (analysis task, not training)

### Models

#### Baseline Model

**Architecture**: Simple summary statistics comparison
**Configuration**: Compare clusters using only (mean, std, trend_coefficient)

**Loading Information**:
- Method: Custom implementation
- Identifier: N/A
- Code:
  ```python
  def baseline_descriptors(centroid):
      return {
          "mean": np.mean(centroid),
          "std": np.std(centroid),
          "trend": np.polyfit(range(len(centroid)), centroid, 1)[0]
      }
  ```

#### Proposed Model

**Architecture**: Shape Descriptor Analysis Pipeline

**Core Mechanism Implementation:**

```python
# Core Mechanism: Shape Descriptors for Cluster Differentiation
# Based on: scipy.signal.find_peaks, numpy gradient, ruptures PELT

import numpy as np
from scipy.signal import find_peaks
import ruptures as rpt

class ShapeDescriptorAnalyzer:
    """
    Compute shape descriptors for time series centroids.
    Tests if clusters have distinct shape signatures.
    """
    def __init__(self, min_prominence=0.1):
        self.min_prominence = min_prominence

    def compute_descriptors(self, centroid):
        """
        Args:
            centroid: (T,) - normalized time series centroid
        Returns:
            dict: shape descriptors
        """
        # 1. Derivative sign pattern (growth vs decline phases)
        gradient = np.gradient(centroid)
        sign_pattern = np.sign(gradient)
        growth_ratio = np.mean(sign_pattern > 0)

        # 2. Peak timing (when does trajectory peak?)
        peaks, props = find_peaks(centroid, prominence=self.min_prominence)
        peak_timing = peaks[0] / len(centroid) if len(peaks) > 0 else 0.5

        # 3. Changepoint count (from h-m1 methodology)
        algo = rpt.Pelt(model="l2", min_size=3).fit(centroid)
        n_changepoints = len(algo.predict(pen=2*np.log(len(centroid)))) - 1

        return {
            "growth_ratio": growth_ratio,
            "peak_timing": peak_timing,
            "changepoint_count": n_changepoints,
            "derivative_variance": np.var(gradient)
        }

# Integration: Apply to each cluster centroid from h-e1
```

### Training Protocol

**Note**: This is an analysis task, not a training task. No model training required.

**Computational Protocol**:
- **Step 1**: Load cluster centroids from h-e1 (k=4)
- **Step 2**: Compute shape descriptors for each centroid
- **Step 3**: Compute inter-cluster descriptor variance
- **Step 4**: Compute intra-cluster descriptor variance (via bootstrap)
- **Step 5**: Compare variance ratio

**Seeds**: 1 (fixed) - Bootstrap uses seed=42

**Dependencies**:
- numpy >= 1.24
- scipy >= 1.10
- ruptures >= 1.1

### Evaluation

**Primary Metrics**:
- Descriptor Profile Distinctness: Cluster centroids occupy distinct regions of descriptor space
- Variance Ratio: Inter-cluster variance / intra-cluster variance > 2.0 on key descriptors

**Success Criteria**:
- PRIMARY: Each cluster centroid has a distinct shape descriptor profile (no two clusters have identical profiles across all descriptors)
- SECONDARY: Variance ratio > 2.0 on at least 2 of 4 descriptors

**Metrics Loading Information**:
- Task Type: clustering_analysis
- Library: sklearn.metrics (for pairwise distances), custom
- Code:
  ```python
  from sklearn.metrics import pairwise_distances
  # Compute descriptor distance matrix
  desc_matrix = np.array([[d["growth_ratio"], d["peak_timing"],
                           d["changepoint_count"], d["derivative_variance"]]
                          for d in descriptors])
  dist_matrix = pairwise_distances(desc_matrix)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart (variance ratio)

#### Additional Figures (LLM Autonomous)
- Cluster centroid overlay plot (all centroids on same axes)
- Shape descriptor radar chart (one per cluster)
- Descriptor space scatter plot (2D projection of 4D descriptor space)
- Inter-cluster distance heatmap

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | Shape descriptors can be computed from centroids | TRUE |
| Mechanism Isolatable | Descriptors can be compared vs baseline (summary stats only) | TRUE |
| Baseline Measurable | Baseline uses only mean/std/trend | TRUE |

### Architecture Compatibility Check

**Required Features:**
- Cluster centroids from h-e1 (TimeSeriesKMeans output)
- Normalized time series data
- PELT algorithm from ruptures library

**Incompatible Architectures:**
- None - this is a pure analysis task using standard scientific Python

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "Shape descriptors computed for {k} centroids" | shape_analyzer.py |
| Tensor Shape | descriptors matrix shape = (k, 4) | compute_descriptors() |
| Metric Delta | variance_ratio > 1.0 (showing differentiation) | evaluate.py |

**Activation Verification Code:**

```python
def verify_mechanism_activated(results):
    indicators = {
        "descriptors_computed": results.get("n_descriptors") == 4,
        "all_clusters_analyzed": results.get("n_clusters") == 4,
        "variance_computed": results.get("inter_variance") is not None,
        "effect_measurable": results.get("variance_ratio", 0) > 1.0
    }
    return all(indicators.values()), indicators
```

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | All descriptors computed |
| Effect Measurable | variance_ratio > 1.0 | Inter/intra variance ratio |
| Hypothesis Supported | variance_ratio > 2.0 on >= 2 descriptors | Per-descriptor analysis |

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Shape descriptors successfully computed for all centroids
3. Cluster centroids show distinct descriptor profiles (not all identical)
4. At least one variance ratio > 2.0

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Note**: Archon KB did not contain directly applicable time series shape descriptor cases. Implementation grounded in Exa findings and scientific Python documentation.

### B. GitHub Implementations (Exa)

**Source 1**: SciPy find_peaks documentation
- **URL**: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html
- **Query Used**: "time series shape descriptors clustering Python scipy"
- **Used For**: Peak timing descriptor

**Source 2**: tslearn documentation
- **URL**: https://tslearn.readthedocs.io/en/stable/user_guide/clustering.html
- **Query Used**: "tslearn time series feature extraction shape based clustering"
- **Used For**: Understanding shape-based clustering methodology

**Source 3**: Cluster evaluation metrics (Medium articles)
- **Query Used**: "cluster centroid shape analysis inter-cluster variance"
- **Used For**: Variance ratio methodology

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Reports - h-e1, h-m1
- **Files**: `h-e1/04_validation.md`, `h-m1/04_validation.md`
- **Reused Components**:
  - Dataset cache: HuggingFace download statistics (500 datasets)
  - Cluster assignments: k=4 from h-e1
  - Changepoint methodology: PELT with BIC penalty from h-m1
- **Why Reused**: Enables controlled experiment - only shape descriptors are new

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset | Previous | h-e1 cache |
| Cluster centroids | Previous | h-e1 TimeSeriesKMeans |
| Peak detection | Exa | scipy.signal.find_peaks |
| Changepoint count | Previous | h-m1 PELT methodology |
| Variance ratio | Exa | sklearn + literature |
| Shape descriptors | Synthesis | Custom based on Exa findings |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-03-27T12:45:00Z

### Workflow History for This Hypothesis
- h-m2 set to IN_PROGRESS (hypothesis loop)
- Phase 2C experiment design started
- Phase 2C experiment design completed

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
