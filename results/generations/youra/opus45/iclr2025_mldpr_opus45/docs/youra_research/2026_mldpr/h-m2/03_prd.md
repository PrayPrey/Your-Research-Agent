# Product Requirements Document: h-m2

**Hypothesis:** Shape Descriptor Differentiation for HuggingFace Dataset Cluster Centroids
**Date:** 2026-03-27
**Author:** Anonymous
**Version:** 1.0
**Status:** Draft

---

## Executive Summary

This PRD defines the requirements for implementing hypothesis h-m2: validating that different adoption mechanisms (benchmark designation, publication cycles, trend following) produce measurably distinct cluster centroid shape signatures. This is a MECHANISM hypothesis with a SHOULD_WORK gate that determines whether shape descriptors can differentiate the clusters identified in h-e1.

**Key Objective:** Demonstrate that cluster centroids exhibit distinct shape descriptor profiles, with inter-cluster variance exceeding intra-cluster variance by a ratio > 2.0 on at least 2 of 4 descriptors.

---

## Problem Statement

### Background
Building on h-e1's validated DTW clustering (silhouette=0.289, k=4, Jaccard=0.991) and h-m1's validated PELT changepoint detection (detection_rate=81%, mean_cps=0.96), we now need to establish that the identified clusters represent meaningfully different adoption mechanisms. Shape descriptors provide objective criteria for characterizing and differentiating cluster centroids.

### Problem Definition
There is no validated evidence that the k=4 clusters from h-e1 exhibit distinct shape signatures. Without shape differentiation, clusters may be statistical artifacts rather than reflections of different adoption mechanisms. This hypothesis bridges clustering structure (h-e1) and archetype alignment (h-m3).

### Impact
- **If shape descriptors differentiate clusters:** Validates that clusters represent distinct adoption mechanisms; enables archetype alignment in h-m3
- **If shape descriptors fail:** Document as limitation; clusters may require alternative characterization methods

---

## Functional Requirements

### FR-1: Data Loading Module

**FR-1.1: Reuse h-e1 Data Pipeline**
- Load preprocessed time series from h-e1 execution
- Reuse same 500 dataset samples for controlled comparison
- **Cache Path:** `../h-e1/code/dataset_cache.json`
- **Fallback:** Re-collect via HuggingFace Hub API

**FR-1.2: Load Cluster Assignments**
- Load k=4 cluster assignments from h-e1
- Extract cluster centroids from TimeSeriesKMeans model
- Validate centroid shape: (k, T) where T=52 (normalized weeks)

**FR-1.3: Continuation Context**
- Document data source consistency with h-e1 and h-m1
- Reuse changepoint methodology from h-m1 for one descriptor

### FR-2: Baseline Model Implementation

**FR-2.1: Simple Summary Statistics**
- Compute only (mean, std, trend_coefficient) per centroid
- **Code:**
```python
def baseline_descriptors(centroid):
    """Baseline: simple summary statistics only."""
    return {
        "mean": np.mean(centroid),
        "std": np.std(centroid),
        "trend": np.polyfit(range(len(centroid)), centroid, 1)[0]
    }
```
- Compute inter-cluster vs intra-cluster variance ratio
- This represents the null hypothesis: shape doesn't matter

**FR-2.2: Random Descriptor Assignment**
- Assign random descriptor values to centroids
- Variance ratio should be ~1.0 (no differentiation)
- Baseline for statistical significance

### FR-3: Proposed Model Implementation

**FR-3.1: Shape Descriptor Computation**
- Implement 4 shape descriptors based on Phase 2C specification:

| Descriptor | Definition | Range |
|------------|------------|-------|
| **growth_ratio** | Proportion of positive gradient values | [0, 1] |
| **peak_timing** | Normalized position of first peak | [0, 1] |
| **changepoint_count** | Number of PELT changepoints | [0, 5+] |
| **derivative_variance** | Variance of gradient | [0, inf) |

**FR-3.2: Shape Descriptor Analyzer Class**
```python
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

        # 4. Derivative variance
        derivative_variance = np.var(gradient)

        return {
            "growth_ratio": growth_ratio,
            "peak_timing": peak_timing,
            "changepoint_count": n_changepoints,
            "derivative_variance": derivative_variance
        }
```

**FR-3.3: Descriptor Matrix Construction**
- Compute descriptors for all k=4 centroids
- Construct descriptor matrix: shape (k, 4)
- Normalize descriptors to [0, 1] range for fair comparison

### FR-4: Variance Ratio Analysis

**FR-4.1: Inter-Cluster Variance**
- Compute variance of each descriptor across k centroids
- Formula: `var([d_1, d_2, ..., d_k])` for each descriptor

**FR-4.2: Intra-Cluster Variance (Bootstrap)**
- For each cluster, bootstrap sample members
- Compute descriptor variance within cluster
- Average across clusters for intra-cluster variance
- **Bootstrap parameters:** n_bootstrap=100, seed=42

**FR-4.3: Variance Ratio Computation**
```python
def compute_variance_ratio(inter_variance, intra_variance, epsilon=1e-8):
    """
    Compute inter/intra variance ratio per descriptor.

    Args:
        inter_variance: dict of per-descriptor inter-cluster variance
        intra_variance: dict of per-descriptor intra-cluster variance

    Returns:
        dict: variance ratios per descriptor
    """
    ratios = {}
    for desc in inter_variance.keys():
        ratios[desc] = inter_variance[desc] / (intra_variance[desc] + epsilon)
    return ratios
```

### FR-5: Evaluation Module

**FR-5.1: Primary Metrics**
| Metric | Target | Required |
|--------|--------|----------|
| Distinct Profiles | All k centroids have different profiles | Yes |
| Variance Ratio > 2.0 | On >= 2 of 4 descriptors | Yes (SHOULD_WORK gate) |

**FR-5.2: Secondary Metrics**
| Metric | Purpose |
|--------|---------|
| Pairwise Descriptor Distance | Confirm no two clusters are identical |
| Descriptor Correlation | Check for redundant descriptors |
| Profile Clustering | Do descriptors naturally cluster? |

**FR-5.3: Baseline Comparison**
- Shape descriptors variance ratio vs Summary statistics variance ratio
- Shape descriptors vs Random assignment variance ratio
- Confirm shape descriptors capture meaningful structure

### FR-6: Visualization Requirements

**FR-6.1: Required Figure (Mandatory)**
- **Gate Metrics Bar Chart:** Variance ratio per descriptor with 2.0 threshold line

**FR-6.2: Additional Figures (Autonomous)**
1. **Cluster Centroid Overlay:** All k=4 centroids on same axes
2. **Shape Descriptor Radar Chart:** One radar per cluster showing 4 descriptors
3. **Descriptor Space Scatter:** 2D projection (PCA or t-SNE) of 4D descriptor space
4. **Inter-Cluster Distance Heatmap:** Pairwise descriptor distances

**FR-6.3: Figure Output**
- Save all figures to `h-m2/figures/` directory
- Use PNG format with 300 DPI
- Include descriptive titles and axis labels

### FR-7: Results Persistence

**FR-7.1: Validation Report**
- Save results to `h-m2/04_validation.md`
- Include all metric values with pass/fail status
- Record execution timestamp and parameters

**FR-7.2: Artifacts**
- Save descriptor matrix (k x 4)
- Save variance ratios per descriptor
- Save centroid data for reproducibility

---

## Non-Functional Requirements

### NFR-1: Performance
- Complete full pipeline in < 5 minutes on single CPU
- Handle k=4 centroids efficiently
- No GPU required (analysis task)

### NFR-2: Reproducibility
- Fixed random seed (42) for bootstrap operations
- Log all hyperparameters (min_prominence, penalty)
- Document library versions (scipy, ruptures)

### NFR-3: Code Quality
- Type hints for all functions
- Docstrings with parameter descriptions
- Modular design with clear separation of concerns

### NFR-4: Error Handling
- Handle edge cases: constant centroids, no peaks detected
- Graceful degradation for flat centroids
- Validate centroid input shapes

---

## Technical Specifications

### Dependencies
```
numpy>=1.24.0
scipy>=1.10.0
ruptures>=1.1.0
matplotlib>=3.5.0
seaborn>=0.12.0
scikit-learn>=1.0.0  # for pairwise_distances
```

### Hardware Requirements
- Single CPU
- Minimum 4GB RAM
- No GPU required

### Algorithm Reference
- **Peak Detection:** scipy.signal.find_peaks (SciPy documentation)
- **PELT Changepoints:** Killick et al. (2012), ruptures library
- **Variance Ratio:** F-statistic analogy for cluster separation

---

## Success Criteria

### Gate Condition: SHOULD_WORK

**Pass Criteria:**
1. Each cluster centroid has a distinct descriptor profile (no identical profiles)
2. Variance ratio > 2.0 on at least 2 of 4 descriptors

**Secondary Validation:**
3. Shape descriptors outperform simple summary statistics
4. Descriptor profiles are interpretable (align with adoption mechanisms)

**Consequence of Failure:**
- DOCUMENT: Limitation noted, proceed to h-m3
- CONSIDER: Alternative characterization methods

### Mechanism Verification
- Shape descriptors successfully computed for all centroids
- Inter-cluster variance measurably exceeds intra-cluster variance
- Descriptors capture meaningful shape differences

---

## Data Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  h-e1 Centroids │────▶│  Shape Descriptor │────▶│  Descriptor     │
│  (k=4)          │     │  Computation      │     │  Matrix (k×4)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Validation     │◀────│  Variance Ratio  │◀────│  Inter/Intra    │
│  Report         │     │  Analysis        │     │  Variance       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

---

## Acceptance Criteria

### AC-1: Data Loading
- [ ] Successfully loads h-e1 cluster centroids
- [ ] Validates k=4 centroids available
- [ ] Confirms centroid shape (k, T)

### AC-2: Shape Descriptor Implementation
- [ ] All 4 descriptors computed without error
- [ ] Descriptors normalized to comparable ranges
- [ ] PELT integration from h-m1 working

### AC-3: Variance Analysis
- [ ] Inter-cluster variance computed per descriptor
- [ ] Intra-cluster variance computed via bootstrap
- [ ] Variance ratios computed correctly

### AC-4: Baseline Comparison
- [ ] Summary statistics baseline implemented
- [ ] Shape descriptors outperform baseline
- [ ] Statistical significance assessed

### AC-5: Visualization
- [ ] Gate metrics bar chart generated
- [ ] Additional figures generated
- [ ] All saved to h-m2/figures/

### AC-6: Gate Validation
- [ ] Pass/Fail determination based on variance ratio criteria
- [ ] Results written to 04_validation.md
- [ ] Gate result recorded in verification_state.yaml

---

## Traceability

| Requirement | Source |
|-------------|--------|
| k=4 centroids | h-e1 validated clustering |
| PELT methodology | h-m1 changepoint detection |
| Variance ratio > 2.0 | Phase 2C hypothesis specification |
| Shape descriptors | Phase 2C Exa research (scipy, tslearn) |
| 4 descriptor types | Phase 2C experiment brief |
| Bootstrap n=100 | Statistical best practices |

---

## Appendix

### A. Phase 2C Reference
- Source: `h-m2/02c_experiment_brief.md`
- Contains: Full experiment specification with pseudo-code

### B. Hypothesis Chain
```
h-e1 (EXISTENCE) ──▶ h-m1 (MECHANISM) ──▶ h-m2 (MECHANISM) ──▶ h-m3 (MECHANISM)
     │                    │                    │                    │
  VALIDATED           VALIDATED            SHOULD_WORK          SHOULD_WORK
   (PASS)              (PASS)              (current)
```

### C. Prerequisite Results

**h-e1 (DTW Clustering):**
- Gate: MUST_WORK - **PASS**
- Silhouette Score: 0.289 (> 0.25 threshold)
- Optimal k: 4 (in [3, 8] range)
- Jaccard Stability: 0.991 (> 0.65 threshold)

**h-m1 (PELT Changepoint Detection):**
- Gate: MUST_WORK - **PASS**
- Detection Rate: 81% (> 50% threshold)
- Mean Changepoints: 0.96 per series
- 405/500 series have at least one changepoint

---

*Generated by Phase 3 Implementation Planning*
*Source: Phase 2C Experiment Brief (h-m2/02c_experiment_brief.md)*
