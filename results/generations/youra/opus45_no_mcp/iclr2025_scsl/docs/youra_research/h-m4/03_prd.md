# Product Requirements Document: H-M4
## Benchmark-Relative Crystallization Timing Validation

**Version:** 1.0
**Date:** 2026-08-19
**Hypothesis ID:** H-M4
**Type:** MECHANISM
**Author:** Anonymous

---

## Executive Summary

This PRD specifies requirements for validating whether crystallization peak timing is benchmark-relative at 20-40% of training duration. Building on H-M3's validated detection method, H-M4 tests whether the detected crystallization timing generalizes across Waterbirds, CelebA, and ColoredMNIST benchmarks when normalized to percentage of total training epochs.

**Gate Condition:** Crystallization peak occurs within 20-40% of normalized training duration for all 3 benchmarks. Variance in normalized timing <10% across benchmarks.

---

## Problem Statement

H-M3 validated the second derivative detection method with 100% reliability on Waterbirds (detection at epoch 3 of 100 = 3%). This is below the hypothesized 20-40% range. H-M4 tests whether crystallization timing follows a consistent relative pattern across benchmarks with different training durations (Waterbirds: 100 epochs, CelebA: 50 epochs, ColoredMNIST: 30 epochs).

---

## Functional Requirements

### FR-1: Multi-Benchmark Training Runs
- **ID:** FR-1
- **Priority:** MUST
- **Description:** Train ResNet-50 baseline models on all 3 benchmarks with full training runs, recording WGA at each epoch
- **Acceptance Criteria:**
  - Train on Waterbirds (100 epochs), CelebA (50 epochs), ColoredMNIST (30 epochs)
  - Use standard WILDS training configurations
  - Record WGA curve at every epoch
  - Run 5 random seeds per benchmark (15 total runs)

### FR-2: Crystallization Detection via H-M3 Method
- **ID:** FR-2
- **Priority:** MUST
- **Description:** Apply H-M3's validated second derivative detection method to each WGA curve
- **Acceptance Criteria:**
  - Use compute_wga_second_derivative with window_size=5
  - Use detect_crystallization_peak with prominence_threshold=0.005
  - Return detected epoch, prominence, and SNR for each run
  - Reuse H-M3 code without modification

### FR-3: Normalized Timing Computation
- **ID:** FR-3
- **Priority:** MUST
- **Description:** Convert absolute peak epochs to percentage of total training duration
- **Acceptance Criteria:**
  - Formula: normalized_timing = (peak_epoch / total_epochs) × 100%
  - Handle each benchmark's different total epochs correctly
  - Return normalized timing for each detected peak

### FR-4: Range Compliance Analysis
- **ID:** FR-4
- **Priority:** MUST
- **Description:** Test whether normalized timing falls within 20-40% range for all benchmarks
- **Acceptance Criteria:**
  - Check: 20% <= normalized_timing <= 40%
  - Compute compliance rate: % of benchmarks in range
  - Report per-benchmark compliance status

### FR-5: Cross-Benchmark Variance Analysis
- **ID:** FR-5
- **Priority:** MUST
- **Description:** Compute variance in normalized timing across benchmarks
- **Acceptance Criteria:**
  - Aggregate normalized timings across all detected peaks
  - Compute mean and standard deviation
  - Target: variance (std) < 10%

### FR-6: Per-Seed Consistency Analysis
- **ID:** FR-6
- **Priority:** SHOULD
- **Description:** Analyze within-benchmark timing variance across 5 seeds
- **Acceptance Criteria:**
  - Compute per-benchmark timing variance across seeds
  - Identify outlier seeds (>2 std from mean)
  - Report seed consistency per benchmark

### FR-7: Gate Evaluation
- **ID:** FR-7
- **Priority:** MUST
- **Description:** Evaluate SHOULD_WORK gate based on timing analysis
- **Acceptance Criteria:**
  - PASS: All 3 benchmarks in 20-40% range AND variance <10%
  - CONDITIONAL PASS: Timing outside 20-40% but consistent pattern documented
  - FAIL: No consistent pattern across benchmarks

---

## Non-Functional Requirements

### NFR-1: Computational Requirements
- Full training runs: ~6 hours per benchmark on V100
- Total: 15 runs × avg 2 hours = ~30 GPU-hours
- Analysis of curves: <5 minutes

### NFR-2: Data Storage
- Checkpoint storage: ~500MB per run (model + WGA curve)
- Total storage: ~8GB for all checkpoints

### NFR-3: Reproducibility
- Fixed random seeds: [0, 1, 2, 3, 4]
- Deterministic training where possible
- Exact reproduction of H-M3 detection algorithm

---

## Success Criteria

### Primary Metrics (Gate Condition)
| Metric | Target | Conditional | Failure |
|--------|--------|-------------|---------|
| Benchmarks in 20-40% Range | 3/3 (100%) | Document actual range | <1/3 |
| Normalized Timing Variance | <10% | <15% with explanation | >15% |
| Detection Rate | >80% | >60% | <50% |

### Secondary Metrics
| Metric | Target |
|--------|--------|
| Per-Benchmark Seed Variance | <5% normalized |
| Mean Normalized Timing | Report actual value |

---

## Data Requirements

### Input Data
| Dataset | Source | Size | Training Duration |
|---------|--------|------|-------------------|
| Waterbirds | WILDS API | 4,795 train | 100 epochs |
| CelebA | WILDS API | 162,770 train | 50 epochs |
| ColoredMNIST | Custom loader | 50,000 train | 30 epochs |

### Output Data
| File | Description |
|------|-------------|
| timing_results.json | Per-seed, per-benchmark normalized timing |
| aggregated_metrics.yaml | Summary statistics and gate evaluation |
| figures/*.png | Visualization plots |

---

## Dependencies

### Prerequisites
- H-M3 PASS (completed): Detection method validated (100% rate, SNR 5.64)
- H-M3 code available for reuse

### Software Dependencies
- Python 3.8+
- PyTorch ≥1.10
- torchvision ≥0.11
- wilds ≥2.0
- numpy ≥1.20
- scipy ≥1.7
- matplotlib ≥3.4

---

## Visualization Requirements

### Required Figures
1. **Gate Metrics Comparison** - Target vs actual bar chart (range compliance, variance)
2. **Normalized Timing Bar Chart** - Per-benchmark timing with 20-40% range shaded
3. **WGA Curves Overlay** - 3-panel: normalized x-axis (% of training)
4. **Timing Distribution** - Box plot of normalized timing across seeds per benchmark
5. **Cross-Benchmark Regression** - Absolute epoch vs total epochs scatter plot

---

## Appendix: Algorithm Pseudo-code

```python
def analyze_benchmark_timing(wga_curves: dict, configs: dict) -> dict:
    results = {}
    for benchmark, wga in wga_curves.items():
        config = configs[benchmark]
        # Apply H-M3 detection
        d2 = compute_wga_second_derivative(wga, window_size=5)
        peak_info = detect_crystallization_peak(d2)
        
        if peak_info['detected']:
            # Normalize timing
            norm_timing = (peak_info['epoch'] / config.total_epochs) * 100.0
            in_range = 20 <= norm_timing <= 40
        else:
            norm_timing = None
            in_range = False
        
        results[benchmark] = {
            'peak_epoch': peak_info['epoch'],
            'total_epochs': config.total_epochs,
            'normalized_timing_percent': norm_timing,
            'in_20_40_range': in_range,
            'snr': peak_info['snr']
        }
    
    # Compute variance
    valid_timings = [r['normalized_timing_percent'] for r in results.values() if r['normalized_timing_percent']]
    variance = np.std(valid_timings) if len(valid_timings) > 1 else 0.0
    
    return {
        'per_benchmark': results,
        'mean_timing': np.mean(valid_timings),
        'variance': variance,
        'gate_pass': all(r['in_20_40_range'] for r in results.values()) and variance < 10.0
    }
```

---

*Generated: 2026-08-19 | Phase 3 Implementation Planning | H-M4*
