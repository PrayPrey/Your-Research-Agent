---
stepsCompleted: ['step-01', 'step-02', 'step-03', 'step-04', 'step-05', 'step-06', 'step-07', 'step-08']
completed: true
hypothesis_id: h-m2
hypothesis_type: MECHANISM
phase: Phase 3
date: 2026-03-21
---

# Product Requirements Document (PRD): H-M2 Finite Variance

**Hypothesis:** SGD with fixed hyperparameters produces finite-variance test accuracy distribution with Gaussian-like tails, validated through excess kurtosis 95% CI ∈ [−2, +2].

**Gate Type:** MUST_WORK

---

## Executive Summary

This PRD defines the implementation requirements for validating the finite variance mechanism (H-M2) in neural network training trajectories. This is an **analysis-only hypothesis** that reuses h-m1 training artifacts to verify that different initial weight configurations (proven independent in h-m1) lead to different optimization trajectories and final model states.

**Success Criteria:**
- **Primary (MUST_WORK):** Final weight configurations differ significantly across seeds for all 4 conditions (mean pairwise distance > 0, p < 0.05)
- **Secondary (SHOULD):** Loss trajectories show measurable divergence (CV of final loss ≥ 1%)

**Implementation Type:** Statistical analysis using h-m1 experiment artifacts (NO NEW TRAINING)

---

## Problem Statement

### Research Question
Do different initial weight configurations (validated in h-m1) lead to different optimization trajectories and final model states under deterministic training?

### Context
H-M2 is a MECHANISM hypothesis that validates the second causal assumption: independent initial weights lead to trajectory divergence. This validates the mechanism by which initial variance propagates through training.

**Causal Chain:**
- H-M1 (PASSED): Different seeds → Different initial weights ✓
- **H-M2 (THIS):** Different initial weights → Different trajectories + final weights
- H-M3 (BLOCKED): Trajectory variance → CLT-predicted variance scaling

### Constraints
- **Prerequisite Status:** H-M1 (Seed Independence) PASSED ✓
- **Execution Time:** ~0 seconds (analysis only, no training)
- **Task Budget:** FULL tier (30 tasks max, 6-12 epic range)
- **Data Source:** h-m1 experiment artifacts (120 files per artifact type)

---

## Functional Requirements

### FR-1: H-M1 Artifact Loading System
**Priority:** P0 (Critical)
**Description:** Load initial weights, final weights, and loss trajectories from h-m1 experiment results.

**Requirements:**
- Load initial weights for all 30 seeds × 4 conditions from h-m1
  - Path pattern: `h-m1/results/{condition}/seed_{i}/initial_weights.pt`
  - Expected shape per file: (n_params,) flattened weight vector
- Load final weights for all 30 seeds × 4 conditions
  - Path pattern: `h-m1/results/{condition}/seed_{i}/final_weights.pt`
  - Expected shape per file: (n_params,) flattened weight vector
- Load loss trajectories for all 30 seeds × 4 conditions
  - Path pattern: `h-m1/results/{condition}/seed_{i}/loss_history.npy`
  - Expected shape per file: (10,) for 10 epochs

**Conditions:**
1. `1layer_mnist`
2. `1layer_fashion_mnist`
3. `2layer_mnist`
4. `2layer_fashion_mnist`

**Acceptance Criteria:**
- All 360 files load successfully (120 × 3 artifact types)
- Initial weights shape matches model architecture (196K for 1-layer, 400K for 2-layer)
- Final weights shape matches initial weights
- Loss trajectories contain 10 values (epochs 0-9)

**Error Handling:**
- If ANY file missing → FAIL EARLY with clear error message listing missing files
- Validate shapes match expected architecture dimensions

**Source:** Phase 2C Experiment Brief Section "Dataset" (h-m1 artifact reuse)

### FR-2: Pairwise Weight Distance Calculator
**Priority:** P0 (Critical)
**Description:** Compute all pairwise Euclidean distances between weight configurations.

**Requirements:**
- Accept weight matrix of shape (30, n_params) - 30 seed runs, flattened weights
- Compute all pairwise Euclidean distances using `scipy.spatial.distance.pdist`
- Return condensed distance array of shape (435,) = (30 choose 2) pairs

**Algorithm:**
```python
from scipy.spatial.distance import pdist, squareform
import numpy as np

def compute_pairwise_distances(weights):
    """
    weights: (30, n_params) array of flattened weight vectors
    returns: (435,) array of pairwise distances
    """
    distances = pdist(weights, metric='euclidean')
    return distances
```

**Acceptance Criteria:**
- Returns (30 choose 2) = 435 distances for 30 seeds
- Distances are non-negative
- Uses optimized scipy implementation (not manual loops)

**Source:** Scipy documentation + Phase 2C Implementation Research

### FR-3: Statistical Significance Test
**Priority:** P0 (Critical)
**Description:** One-sample t-test to verify mean pairwise distance significantly greater than 0.

**Requirements:**
- Accept pairwise distance array
- Execute one-sample t-test with null hypothesis μ = 0
- Use one-tailed test (alternative='greater')
- Return t-statistic, p-value, mean distance

**Algorithm:**
```python
from scipy.stats import ttest_1samp

def test_distance_significance(distances):
    """
    distances: (435,) array of pairwise distances
    returns: (t_stat, p_value, mean_distance)
    """
    t_stat, p_value = ttest_1samp(distances, 0, alternative='greater')
    mean_dist = np.mean(distances)
    return t_stat, p_value, mean_dist
```

**Acceptance Criteria:**
- p-value < 0.05 for significance
- t-statistic > 0 (distances greater than 0)
- Mean distance reported with at least 3 decimal places

**Source:** Phase 2C Success Criteria (Primary)

### FR-4: Loss Trajectory Divergence Analyzer
**Priority:** P1 (Important)
**Description:** Calculate coefficient of variation (CV) for final epoch losses across 30 seeds.

**Requirements:**
- Accept loss trajectory matrix of shape (30, 10) - 30 seeds, 10 epochs
- Extract final epoch losses (epoch 9, index -1)
- Calculate CV = (std / mean) × 100

**Algorithm:**
```python
def calculate_loss_cv(loss_trajectories):
    """
    loss_trajectories: (30, 10) array
    returns: cv_percent (float)
    """
    final_losses = loss_trajectories[:, -1]
    cv = (np.std(final_losses) / np.mean(final_losses)) * 100
    return cv
```

**Acceptance Criteria:**
- CV ≥ 1% for measurable divergence (SHOULD criterion)
- CV reported as percentage (not decimal)
- Uses final epoch (epoch 9) losses only

**Source:** Phase 2C Success Criteria (Secondary)

### FR-5: Per-Condition Analysis Orchestrator
**Priority:** P0 (Critical)
**Description:** Execute all analyses for all 4 experimental conditions and aggregate results.

**Requirements:**
- For each condition in [1layer_mnist, 1layer_fashion_mnist, 2layer_mnist, 2layer_fashion_mnist]:
  - Load 30 initial weights, 30 final weights, 30 loss trajectories
  - Compute initial weight pairwise distances
  - Compute final weight pairwise distances
  - Execute statistical significance test on final distances
  - Calculate loss trajectory CV
  - Store results with condition label

**Output Structure:**
```python
results = {
    'condition_name': {
        'mean_initial_distance': float,
        'mean_final_distance': float,
        'final_distance_p_value': float,
        'final_distance_t_stat': float,
        'cv_final_loss_percent': float,
        'test1_passed': bool,  # p < 0.05 and mean > 0
        'test2_passed': bool,  # CV >= 1.0
        'n_seeds': int,
        'n_params': int
    },
    ...  # for all 4 conditions
}
```

**Acceptance Criteria:**
- Results dict contains all 4 conditions
- All metrics present for each condition
- Test pass/fail flags computed correctly

**Source:** Phase 2C Experiment Design Section "Evaluation"

### FR-6: Gate Validation Logic
**Priority:** P0 (Critical)
**Description:** Determine MUST_WORK gate pass/fail based on primary and secondary criteria.

**Requirements:**
- **Primary (MUST satisfy for PASS):** All 4 conditions pass Test 1 (p < 0.05, mean distance > 0)
- **Secondary (SHOULD satisfy):** At least 2/4 conditions pass Test 2 (CV ≥ 1%)

**Algorithm:**
```python
def validate_gate(results):
    """
    results: dict with per-condition metrics
    returns: (gate_passed: bool, summary: str)
    """
    # Test 1: All 4 conditions significant
    test1_count = sum(r['test1_passed'] for r in results.values())
    primary_pass = (test1_count == 4)

    # Test 2: At least 2/4 conditions CV >= 1%
    test2_count = sum(r['test2_passed'] for r in results.values())
    secondary_pass = (test2_count >= 2)

    gate_passed = primary_pass  # MUST_WORK only requires primary

    summary = f"Primary: {test1_count}/4 conditions passed, Secondary: {test2_count}/4 conditions passed"
    return gate_passed, summary
```

**Acceptance Criteria:**
- Gate passes ONLY if all 4 conditions satisfy primary criterion
- Secondary criterion logged but not blocking
- Clear summary message generated

**Source:** Phase 2C Mechanism Verification Check

### FR-7: Visualization Generator
**Priority:** P1 (Important)
**Description:** Generate required 4-panel figure showing final weight distances and loss trajectory fans.

**Requirements:**
- **Figure Layout:** 2×2 grid (one panel per condition)
- **Panel A (top row):** Final weight distance distribution
  - Histogram of 435 pairwise distances
  - Vertical line at mean distance
  - Annotate with p-value
- **Panel B (bottom row):** Loss trajectory fan chart
  - Plot all 30 loss trajectories (10 epochs each)
  - Semi-transparent lines (alpha=0.5)
  - Annotate with CV of final epoch
- Save to `h-m2/figures/gate_metrics_comparison.png`

**Acceptance Criteria:**
- Figure saved successfully
- All 4 conditions displayed
- Clear labels and annotations
- High resolution (DPI >= 300)

**Source:** Phase 2C Visualization Requirements

---

## Non-Functional Requirements

### NFR-1: Analysis Performance
**Priority:** P1
**Description:** Analysis completes within 30 seconds
**Rationale:** No training required, pure statistical computation
**Measurement:** Total execution time for all 4 conditions < 30s

### NFR-2: Numerical Stability
**Priority:** P0
**Description:** Distance calculations use float64 precision
**Rationale:** Prevent numerical underflow in t-test for small distances
**Measurement:** All distance arrays use `dtype=np.float64`

### NFR-3: Error Reporting
**Priority:** P0
**Description:** Clear error messages for missing h-m1 artifacts
**Rationale:** Analysis cannot proceed without prerequisite data
**Measurement:** List ALL missing files in error message (not just first failure)

---

## Success Criteria

### Primary Success Criteria (MUST_WORK Gate)
1. **Test 1 - Final Weight Divergence:** Mean pairwise distance > 0 with p < 0.05 for ALL 4 conditions
   - Validates: Different initial weights → different final weights
   - Failure = MUST_WORK gate FAIL → h-m3 blocked

### Secondary Success Criteria (Quality Indicators)
1. **Test 2 - Loss Trajectory Divergence:** CV of final epoch loss ≥ 1% for ≥2/4 conditions
   - Validates: Trajectories visibly diverge during training
   - Failure = Document limitation, continue to h-m3

### Code Quality Criteria
1. All 360 h-m1 artifact files load successfully
2. Pairwise distance calculation uses scipy (not manual loops)
3. Statistical tests use scipy.stats (not manual implementation)
4. Results saved to `h-m2/results/analysis_results.json`
5. Figure saved to `h-m2/figures/gate_metrics_comparison.png`

---

## Dependencies

### Technical Dependencies
| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | ≥3.8 | Core runtime |
| PyTorch | ≥1.9 | Weight file loading (torch.load) |
| NumPy | ≥1.19 | Array operations, CV calculation |
| SciPy | ≥1.6 | pdist, ttest_1samp |
| Matplotlib | ≥3.3 | Visualization |

### Data Dependencies
| Dependency | Source | Status |
|------------|--------|--------|
| h-m1 initial weights | h-m1/results/{condition}/seed_{i}/initial_weights.pt | REQUIRED (h-m1 PASSED) |
| h-m1 final weights | h-m1/results/{condition}/seed_{i}/final_weights.pt | REQUIRED (h-m1 PASSED) |
| h-m1 loss trajectories | h-m1/results/{condition}/seed_{i}/loss_history.npy | REQUIRED (h-m1 PASSED) |

### Hypothesis Dependencies
| Hypothesis | Status | Required For |
|------------|--------|--------------|
| H-M1 (Seed Independence) | PASSED ✓ | Artifact source |

---

## Out of Scope

### Explicitly Excluded
- ❌ New model training (reuse h-m1 trained models)
- ❌ New dataset downloads (reuse h-m1 datasets)
- ❌ Kurtosis calculation (moved to separate hypothesis if needed)
- ❌ Trajectory visualization beyond required figure (optional figures delegated to LLM)
- ❌ Statistical power analysis (assume 30 seeds sufficient from h-m1)

### Future Work (Not in This Hypothesis)
- Kurtosis-based Gaussian tail validation (may become h-m2-extended)
- Trajectory clustering analysis (research direction)
- Weight space dimensionality reduction (t-SNE/PCA) - optional in Phase 4

---

## Risk Assessment

### High Priority Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| H-M1 artifacts incomplete | Low | HIGH | Early file existence check with clear error |
| Numerical precision issues | Medium | HIGH | Use float64 for all calculations |
| P-value exactly 0.05 edge case | Low | MEDIUM | Document as marginal, recommend re-run |

### Medium Priority Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| CV too low despite significant distances | Medium | MEDIUM | Secondary criterion SHOULD not MUST |
| Figure generation OOM | Low | LOW | Reduce plot DPI if needed |

---

## Data Requirements

### Input Data Specification
**Source:** h-m1 experiment artifacts (Phase 4 completion)

**File Structure:**
```
h-m1/results/
├── 1layer_mnist/
│   ├── seed_0/
│   │   ├── initial_weights.pt    # torch tensor, shape (196608,)
│   │   ├── final_weights.pt      # torch tensor, shape (196608,)
│   │   └── loss_history.npy      # numpy array, shape (10,)
│   ├── seed_1/
│   ...
│   └── seed_29/
├── 1layer_fashion_mnist/
├── 2layer_mnist/
└── 2layer_fashion_mnist/
```

**Total Files:** 360 (30 seeds × 4 conditions × 3 file types)

### Output Data Specification
**Location:** `h-m2/results/`

**Files:**
1. `analysis_results.json` - Per-condition metrics (structured as FR-5 output)
2. `gate_validation.json` - Gate pass/fail with summary
3. `figures/gate_metrics_comparison.png` - Required 4-panel figure

---

## Environment Setup

### Execution Environment
- **Runtime:** Analysis script (no training loop)
- **GPU:** Not required (CPU-only analysis)
- **Memory:** ~2GB (loading 360 weight files)
- **Disk Space:** <100MB (results + figure)

### Environment Variables
```bash
# Not required - analysis only, no CUDA
```

---

## Testing Strategy

### Unit Tests
1. **Test Artifact Loading:**
   - Mock h-m1 file structure
   - Verify all 360 files detected
   - Verify error message for missing files

2. **Test Pairwise Distance:**
   - Known weight matrix → verify distance count (435)
   - Zero matrix → verify all distances = 0
   - Identity perturbation → verify distances > 0

3. **Test Statistical Significance:**
   - Non-zero distances → p-value < 0.05
   - Zero distances → p-value = 1.0

4. **Test CV Calculation:**
   - Known loss values → verify CV formula
   - Uniform losses → CV ≈ 0

### Integration Tests
1. **End-to-End Analysis:**
   - Use h-m1 actual artifacts (if available)
   - Verify all 4 conditions analyzed
   - Verify gate validation executes

2. **Figure Generation:**
   - Verify figure file created
   - Verify 4 panels present
   - Verify annotations readable

---

## Implementation Notes

### Critical Path
1. FR-1: Load h-m1 artifacts (BLOCKING)
2. FR-2: Compute distances (BLOCKING)
3. FR-3: Statistical test (BLOCKING)
4. FR-6: Gate validation (BLOCKING)
5. FR-7: Visualization (NON-BLOCKING)

### Implementation Order
**Epic 1 - Setup:** Environment verification
**Epic 2 - Data Loading:** FR-1 (artifact loading with early failure)
**Epic 3 - Analysis Core:** FR-2, FR-3, FR-4 (distance, stats, CV)
**Epic 4 - Orchestration:** FR-5, FR-6 (per-condition loop, gate)
**Epic 5 - Visualization:** FR-7 (figures)
**Epic 6 - Validation:** Integration tests

### Key Design Decisions
1. **No Training:** Analysis-only hypothesis reduces complexity and execution time
2. **Early Failure:** File existence check before any analysis prevents wasted computation
3. **Scipy Over Manual:** Use optimized scipy implementations for correctness and speed
4. **Float64 Precision:** Prevent numerical issues in statistical tests
5. **Structured Output:** JSON results enable downstream Phase 5 baseline comparison

---

## Appendix: Reference Implementations

### Scipy Pairwise Distance
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.pdist.html
- **Purpose:** Efficient all-pairs distance computation
- **Used in:** FR-2

### Scipy One-Sample T-Test
- **URL:** https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_1samp.html
- **Purpose:** Statistical significance testing
- **Used in:** FR-3

### ArXiv - Optimization Trajectories
- **URL:** https://arxiv.org/html/2403.07379v1
- **Purpose:** Methodology for trajectory divergence analysis
- **Used in:** FR-4 (CV metric justification)

---

*Generated for Phase 3 Implementation Planning | h-m2 MECHANISM Hypothesis*
