# Product Requirements Document: h-m1

**Hypothesis:** PELT Changepoint Detection for HuggingFace Dataset Download Trajectories
**Date:** 2026-03-27
**Author:** Anonymous
**Version:** 1.0
**Status:** Draft

---

## Executive Summary

This PRD defines the requirements for implementing hypothesis h-m1: validating that PELT changepoint detection with CROPS penalty selection can identify statistically significant lifecycle phase transitions in HuggingFace dataset download trajectories. This is a MECHANISM hypothesis with a MUST_WORK gate that determines whether the two-level hierarchical approach (changepoint + clustering) is viable.

**Key Objective:** Demonstrate that >50% of HuggingFace datasets exhibit at least one statistically significant changepoint, validating the existence of discrete adoption phases (launch, growth, maturity, decline).

---

## Problem Statement

### Background
Building on h-e1's validated finding that meaningful clustering structure exists in HuggingFace download trajectories (silhouette=0.289, k=4, Jaccard=0.991), we now need to establish that individual datasets exhibit discrete lifecycle phases. The two-level hierarchical analysis requires both: (1) phase detection within datasets, and (2) clustering across phase-normalized trajectories.

### Problem Definition
There is no validated evidence that HuggingFace dataset download trajectories contain discrete changepoints representing lifecycle transitions. Without phase detection, the proposed two-level hierarchical approach collapses to single-level clustering, losing methodological novelty.

### Impact
- **If changepoints exist (>50%):** Enables phase-normalized clustering (H-M2, H-M3)
- **If changepoints fail (<50%):** Two-level approach invalid; consider single-level fallback or alternative phase detection (BOCPD)

---

## Functional Requirements

### FR-1: Data Loading Module

**FR-1.1: Reuse h-e1 Data Pipeline**
- Load preprocessed time series from h-e1 execution
- Reuse same 500 dataset samples for controlled comparison
- **Cache Path:** `h-e1/code/dataset_cache.json` (if available)
- **Fallback:** Re-collect via HuggingFace Hub API

**FR-1.2: Data Format Validation**
- Validate time series length >= 12 time points
- Ensure log-transform + z-score preprocessing applied
- Convert to numpy array format for ruptures library

**FR-1.3: Continuation Context**
- Document data source consistency with h-e1
- Log any differences in preprocessing or sample selection

### FR-2: Preprocessing Pipeline

**FR-2.1: Log Transformation**
- Apply `np.log1p(downloads)` to handle exponential growth
- Preserve zero values safely
- **Source:** h-e1 validated preprocessing

**FR-2.2: Z-Score Normalization**
- Apply per-series normalization: `(x - mean) / std`
- Handle constant series (std=0) with epsilon

**FR-2.3: Missing Value Handling**
- Forward-fill for isolated missing values
- Interpolation for gaps < 3 time points
- Exclude series with > 10% missing values

### FR-3: Baseline Model Implementation

**FR-3.1: Random Changepoint Placement**
- Randomly place 0-4 changepoints per time series
- Uniform distribution over valid positions
- Compute detection rate as comparison baseline

**FR-3.2: No Changepoint (Null Model)**
- Assume zero changepoints for all time series
- Detection rate = 0% (trivial baseline)

**FR-3.3: Fixed-Interval Segmentation**
- Place changepoints at fixed intervals (e.g., every 6 months)
- Compute detection rate for comparison

### FR-4: Proposed Model Implementation

**FR-4.1: PELT Algorithm Initialization**
- Implement using `ruptures.Pelt` class
- **Cost Model:** "l2" (Gaussian likelihood, fastest)
- **min_size:** 3 (minimum segment length)
- **jump:** 1 (evaluate all positions)
- **Source:** ruptures library (deepcharles/ruptures)

**FR-4.2: CROPS-Style Penalty Selection**
- Implement grid search over penalty range [1.0, 100.0]
- Evaluate 20 penalty values (log-spaced)
- Select penalty using BIC criterion: `pen = 2 * log(n)`
- **Reference:** Haynes et al. (2017), Lancaster MATH337 course

**FR-4.3: Changepoint Detection**
```python
import ruptures as rpt

def detect_changepoints_pelt(time_series, model="l2", min_size=3, penalty=None):
    """
    PELT changepoint detection with BIC penalty.

    Args:
        time_series: (T,) numpy array - preprocessed time series
        model: cost function ("l2" recommended)
        min_size: minimum segment length
        penalty: penalty value (default: BIC)

    Returns:
        changepoints: list of changepoint indices (excluding endpoint)
    """
    algo = rpt.Pelt(model=model, min_size=min_size, jump=1)
    algo.fit(time_series)

    if penalty is None:
        penalty = 2 * np.log(len(time_series))  # BIC

    result = algo.predict(pen=penalty)
    return result[:-1]  # Exclude endpoint
```

**FR-4.4: Detection Rate Computation**
- Count datasets with >= 1 changepoint
- Compute proportion: `n_with_changepoint / total_datasets`
- Target: detection_rate > 0.50

### FR-5: Evaluation Module

**FR-5.1: Primary Metrics**
| Metric | Target | Required |
|--------|--------|----------|
| Detection Rate | > 0.50 | Yes (MUST_WORK gate) |
| Mean Changepoints/Dataset | 1-5 expected | No (informational) |

**FR-5.2: Secondary Metrics**
| Metric | Purpose |
|--------|---------|
| Changepoint Count Distribution | Validate expected lifecycle phases |
| Temporal Distribution | Where changepoints occur (early/mid/late) |
| Penalty Sensitivity | Stability across penalty values |

**FR-5.3: Baseline Comparison**
- PELT detection rate vs Random detection rate
- PELT vs Fixed-interval detection
- Confirm PELT detects meaningful structure (not random artifacts)

### FR-6: Visualization Requirements

**FR-6.1: Required Figure (Mandatory)**
- **Gate Metrics Comparison:** Bar chart showing detection rate vs 50% threshold

**FR-6.2: Additional Figures (Autonomous)**
1. **Changepoint Distribution Histogram:** Count of changepoints per dataset
2. **Example Time Series with Changepoints:** 3-5 examples showing detected changepoints
3. **Penalty Sensitivity Plot:** Detection rate vs penalty value (CROPS-style elbow)
4. **Temporal Changepoint Heatmap:** When changepoints occur across lifecycle

**FR-6.3: Figure Output**
- Save all figures to `h-m1/figures/` directory
- Use PNG format with 300 DPI
- Include descriptive titles and axis labels

### FR-7: Results Persistence

**FR-7.1: Validation Report**
- Save results to `h-m1/04_validation.md`
- Include all metric values with pass/fail status
- Record execution timestamp and parameters

**FR-7.2: Artifacts**
- Save changepoint indices per dataset
- Save penalty selection curve data
- Save preprocessing parameters for reproducibility

---

## Non-Functional Requirements

### NFR-1: Performance
- Complete full pipeline in < 15 minutes on single CPU
- Handle >= 500 time series efficiently
- PELT is O(n) per series - no GPU required

### NFR-2: Reproducibility
- Fixed random seed (42) for any stochastic operations
- Log all hyperparameters (model, min_size, penalty)
- Document ruptures library version

### NFR-3: Code Quality
- Type hints for all functions
- Docstrings with parameter descriptions
- Modular design with clear separation of concerns

### NFR-4: Error Handling
- Handle edge cases: constant series, very short series
- Graceful degradation for API failures
- Checkpoint capability for long-running operations

---

## Technical Specifications

### Dependencies
```
ruptures>=1.1.0
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.5.0
seaborn>=0.12.0
huggingface_hub>=0.20.0  # if re-collecting data
```

### Hardware Requirements
- Single CPU (PELT is not parallelized by default)
- Minimum 8GB RAM
- No GPU required

### Algorithm Reference
- **PELT:** Killick, R., Fearnhead, P., & Eckley, I.A. (2012). "Optimal Detection of Changepoints With a Linear Computational Cost." JASA.
- **CROPS:** Haynes, K., Eckley, I.A., & Fearnhead, P. (2017). "Computationally Efficient Changepoint Detection for a Range of Penalties." JCGS.

---

## Success Criteria

### Gate Condition: MUST_WORK

**Pass Criteria:**
1. `detection_rate > 0.50` (>50% of datasets have >= 1 changepoint)

**Secondary Validation:**
2. Changepoint locations are interpretable (not uniformly random)
3. Mean changepoints per dataset in expected range [1, 5]

**Consequence of Failure:**
- STOP: Two-level hierarchical approach is invalid
- Consider: Single-level clustering fallback or alternative phase detection (BOCPD)

### Mechanism Verification
- PELT algorithm runs without error on all time series
- Detection rate significantly exceeds random baseline
- Changepoints align with intuitive lifecycle phases

---

## Data Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  h-e1 Data      │────▶│  Preprocessing   │────▶│  PELT Detection │
│  (500 series)   │     │  (log + z-score) │     │  (BIC penalty)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Validation     │◀────│  Detection Rate  │◀────│  Changepoint    │
│  Report         │     │  Computation     │     │  Aggregation    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

---

## Acceptance Criteria

### AC-1: Data Loading
- [ ] Successfully loads h-e1 preprocessed data OR re-collects via API
- [ ] Validates >= 500 time series available
- [ ] Confirms preprocessing consistency with h-e1

### AC-2: PELT Implementation
- [ ] ruptures library installed and functional
- [ ] PELT runs without error on all time series
- [ ] BIC penalty computed correctly

### AC-3: Detection Rate
- [ ] Changepoints detected for each time series
- [ ] Detection rate computed as proportion with >= 1 changepoint
- [ ] Rate compared against 50% threshold

### AC-4: Baseline Comparison
- [ ] Random baseline implemented
- [ ] Fixed-interval baseline implemented
- [ ] PELT exceeds both baselines

### AC-5: Visualization
- [ ] Gate metrics bar chart generated
- [ ] Additional figures generated
- [ ] All saved to h-m1/figures/

### AC-6: Gate Validation
- [ ] Pass/Fail determination based on detection_rate > 0.50
- [ ] Results written to 04_validation.md
- [ ] Gate result recorded in verification_state.yaml

---

## Traceability

| Requirement | Source |
|-------------|--------|
| Detection rate > 50% | Phase 2B hypothesis specification |
| PELT algorithm | Literature (Killick et al., 2012) |
| BIC penalty | CROPS methodology (Haynes et al., 2017) |
| ruptures implementation | Phase 2C GitHub research (deepcharles/ruptures) |
| 500 datasets | Continuation from h-e1 |
| Preprocessing pipeline | h-e1 validated approach |

---

## Appendix

### A. Phase 2C Reference
- Source: `h-m1/02c_experiment_brief.md`
- Contains: Full experiment specification with pseudo-code

### B. Hypothesis Chain
```
h-e1 (EXISTENCE) ──▶ h-m1 (MECHANISM) ──▶ h-m2 (MECHANISM) ──▶ h-m3 (MECHANISM)
     │                    │                    │                    │
  VALIDATED           MUST_WORK           SHOULD_WORK          SHOULD_WORK
   (PASS)             (current)
```

### C. Prerequisite Results (h-e1)
- Gate: MUST_WORK - **PASS**
- Silhouette Score: 0.289 (> 0.25 threshold)
- Optimal k: 4 (in [3, 8] range)
- Jaccard Stability: 0.991 (> 0.65 threshold)
- Data: HuggingFace Hub API (real dataset download statistics)

---

*Generated by Phase 3 Implementation Planning*
*Source: Phase 2C Experiment Brief (h-m1/02c_experiment_brief.md)*
