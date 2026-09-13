# Product Requirements Document: H-M3
## Second Derivative Detection Method Validation

**Version:** 1.0
**Date:** 2026-08-19
**Hypothesis ID:** H-M3
**Type:** MECHANISM
**Author:** Anonymous

---

## Executive Summary

This PRD specifies requirements for validating a crystallization detection method using second derivative analysis of Worst-Group Accuracy (WGA) curves. The method applies 5-epoch rolling window smoothing followed by numerical differentiation to identify crystallization as a significant negative peak in d²WGA/dt².

**Gate Condition:** Detection method validates with >80% reliability across random seeds. Peak timing variance <5 epochs.

---

## Problem Statement

After confirming crystallization exists (H-E1), gradient starvation mechanism (H-M1), and classifier commitment (H-M2), we need a reliable automated detection method. Manual inspection of WGA curves is subjective and not scalable. H-M3 proposes d²WGA/dt² with 5-epoch smoothing as a robust detection approach.

---

## Functional Requirements

### FR-1: WGA Curve Loading
- **ID:** FR-1
- **Priority:** MUST
- **Description:** Load pre-computed WGA curves from H-E1/H-M1/H-M2 checkpoints or compute fresh curves if unavailable
- **Acceptance Criteria:**
  - Load WGA arrays from checkpoint files (numpy .npy format)
  - Support 3 benchmarks: Waterbirds, CelebA, ColoredMNIST
  - Handle 5 random seeds per benchmark (15 total curves)

### FR-2: Rolling Window Smoothing
- **ID:** FR-2
- **Priority:** MUST
- **Description:** Apply uniform rolling window smoothing to WGA curves before differentiation
- **Acceptance Criteria:**
  - Implement using scipy.ndimage.uniform_filter1d
  - Support configurable window sizes [3, 5, 7] epochs
  - Handle edge effects with 'nearest' mode
  - Primary validation uses window_size=5

### FR-3: Second Derivative Computation
- **ID:** FR-3
- **Priority:** MUST
- **Description:** Compute d²WGA/dt² using numerical differentiation
- **Acceptance Criteria:**
  - Use numpy.gradient for central difference approximation
  - Apply twice: first derivative then second derivative
  - Output array same length as input WGA curve

### FR-4: Crystallization Peak Detection
- **ID:** FR-4
- **Priority:** MUST
- **Description:** Detect crystallization as significant negative peak in d²WGA/dt²
- **Acceptance Criteria:**
  - Use scipy.signal.find_peaks on negated d²WGA/dt²
  - Apply prominence threshold (default: 0.005)
  - Return: detected (bool), epoch (int), prominence (float), SNR (float)
  - Select strongest peak if multiple detected

### FR-5: Multi-Window Sensitivity Analysis
- **ID:** FR-5
- **Priority:** MUST
- **Description:** Test detection consistency across smoothing windows [3, 5, 7]
- **Acceptance Criteria:**
  - Run detection for each window size
  - Compute window robustness: % of windows detecting same peak ± 3 epochs
  - Report per-window detection results

### FR-6: Cross-Seed Statistical Analysis
- **ID:** FR-6
- **Priority:** MUST
- **Description:** Aggregate results across 5 seeds per benchmark
- **Acceptance Criteria:**
  - Compute detection rate: % of seeds with detected peak
  - Compute timing variance: std of detected peak epochs
  - Target: detection rate >80%, variance <5 epochs

### FR-7: Cross-Benchmark Analysis
- **ID:** FR-7
- **Priority:** SHOULD
- **Description:** Compare detection across Waterbirds, CelebA, ColoredMNIST
- **Acceptance Criteria:**
  - Normalize peak timing to % of training duration
  - Compute cross-benchmark correlation
  - Report per-benchmark detection rates

---

## Non-Functional Requirements

### NFR-1: Computational Efficiency
- Analysis of 15 WGA curves should complete in <60 seconds
- Memory usage <2GB for all curves loaded simultaneously

### NFR-2: Reproducibility
- Identical results given same input curves and parameters
- No stochastic components in detection algorithm

### NFR-3: Code Quality
- Type hints for all functions
- Docstrings with parameter descriptions
- Unit tests for core functions

---

## Success Criteria

### Primary Metrics (Gate Condition)
| Metric | Target | Failure Threshold |
|--------|--------|-------------------|
| Detection Rate (5-epoch window) | >80% | <50% |
| Peak Timing Variance | <5 epochs | >10 epochs |
| Signal-to-Noise Ratio (SNR) | >2.0 | <1.0 |

### Secondary Metrics
| Metric | Target |
|--------|--------|
| Window Robustness | >70% windows agree |
| Cross-Benchmark Consistency | >0.6 correlation |

---

## Data Requirements

### Input Data
| Dataset | Source | Size | Purpose |
|---------|--------|------|---------|
| Waterbirds WGA curves | H-E1 checkpoints | 5 seeds × 100 epochs | Primary validation |
| CelebA WGA curves | H-E1 checkpoints | 5 seeds × 50 epochs | Generalization |
| ColoredMNIST WGA curves | H-E1 checkpoints | 5 seeds × 30 epochs | Generalization |

### Output Data
| File | Description |
|------|-------------|
| detection_results.json | Per-seed, per-benchmark detection results |
| aggregated_metrics.yaml | Summary statistics and gate evaluation |
| figures/*.png | Visualization plots |

---

## Dependencies

### Prerequisites
- H-M2 PASS (completed): Classifier commitment confirmed
- H-E1 checkpoints: WGA curves available

### Software Dependencies
- Python 3.8+
- numpy ≥1.20
- scipy ≥1.7
- matplotlib ≥3.4

---

## Visualization Requirements

### Required Figures
1. **Gate Metrics Comparison** - Target vs actual bar chart
2. **WGA with Derivatives** - 3-panel: raw, smoothed, d²WGA/dt² with peak
3. **Window Size Comparison** - Overlay of d²WGA/dt² for windows [3,5,7]
4. **Detection Heatmap** - Seeds × Benchmarks showing peak epochs
5. **SNR Distribution** - Box plot across conditions
6. **Timing Variance** - Bar chart per benchmark

---

## Appendix: Algorithm Pseudo-code

```python
def validate_detection_method(wga_curves: dict, window: int = 5) -> dict:
    results = []
    for benchmark, seeds in wga_curves.items():
        for seed_id, wga in seeds.items():
            # Smooth
            smoothed = uniform_filter1d(wga, size=window, mode='nearest')
            # Differentiate twice
            d1 = np.gradient(smoothed)
            d2 = np.gradient(d1)
            # Detect peak
            peaks, props = find_peaks(-d2, prominence=0.005)
            if len(peaks) > 0:
                best = np.argmax(props['prominences'])
                results.append({
                    'benchmark': benchmark,
                    'seed': seed_id,
                    'detected': True,
                    'epoch': peaks[best],
                    'prominence': props['prominences'][best],
                    'snr': props['prominences'][best] / np.std(d2)
                })
            else:
                results.append({
                    'benchmark': benchmark,
                    'seed': seed_id,
                    'detected': False
                })
    return aggregate_results(results)
```

---

*Generated: 2026-08-19 | Phase 3 Implementation Planning | H-M3*
