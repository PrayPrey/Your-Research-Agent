---
stepsCompleted: ['step-01', 'step-02', 'step-03', 'step-04', 'step-05', 'step-06', 'step-07', 'step-08']
completed: true
hypothesis_id: h-m1
hypothesis_type: MECHANISM
phase: Phase 3
date: 2026-03-21
---

# Product Requirements Document (PRD): H-M1 Seed Independence

**Hypothesis:** Random seed initialization creates independent training runs without cross-run contamination, validated through σ²_within/σ²_between ≤ 0.05 AND ICC_session ≤ 0.05.

**Gate Type:** MUST_WORK

---

## Executive Summary

This PRD defines the implementation requirements for validating the seed independence mechanism (H-M1) in neural network training. The experiment will verify that PyTorch's random seed initialization creates truly independent training runs by measuring pairwise weight distances across 30 different random seeds and testing for statistical significance.

**Success Criteria:** Mean pairwise weight distance > 0 with p < 0.05 for all 4 experimental conditions (2 architectures × 2 datasets).

---

## Problem Statement

### Research Question
Does PyTorch's `torch.manual_seed()` create truly independent weight initializations across different random seeds, or is there cross-run contamination that violates the i.i.d. assumptions required for Central Limit Theorem (CLT) validation?

### Context
H-M1 is a MECHANISM hypothesis that validates the first causal assumption: random seed initialization creates independent training runs. This is prerequisite for:
- H-M2 (Finite Variance)
- H-M3 (CLT-Predicted Slope)

### Constraints
- **Prerequisite Status:** H-E1 (Baseline Variance Measurability) FAILED but H-M1 can be validated independently as it tests the initialization mechanism, not variance scaling
- **Execution Time:** ~20 seconds (initialization only, no training required)
- **Task Budget:** FULL tier (30 tasks max, 6-12 epic range)

---

## Functional Requirements

### FR-1: Determinism Setup System
**Priority:** P0 (Critical)
**Description:** Implement comprehensive PyTorch determinism configuration that enables reproducible model initialization.

**Requirements:**
- Set `torch.manual_seed(seed)` for all devices (CPU + CUDA)
- Set `torch.cuda.manual_seed_all(seed)` for all CUDA devices
- Set `np.random.seed(seed)` for NumPy operations
- Set `torch.backends.cudnn.deterministic = True`
- Set `torch.backends.cudnn.benchmark = False`
- Return initialized model instance

**Acceptance Criteria:**
- Same seed produces identical initial weights (verified by checksum)
- Different seeds produce different initial weights (verified by distance > 0)

**Source:** PyTorch Reproducibility Documentation (https://pytorch.org/docs/stable/notes/randomness.html)

### FR-2: Model Architecture Implementation
**Priority:** P0 (Critical)
**Description:** Implement two MLP architectures for robustness testing.

**Architecture 1 - 1-Layer MLP:**
- Input: 784 (28×28 flattened images)
- Hidden: 128 units (ReLU activation)
- Output: 10 units (log softmax)
- Parameters: ~196K

**Architecture 2 - 2-Layer MLP:**
- Input: 784 (28×28 flattened images)
- Hidden 1: 256 units (ReLU activation)
- Hidden 2: 128 units (ReLU activation)
- Output: 10 units (log softmax)
- Parameters: ~400K

**Acceptance Criteria:**
- Models initialize with PyTorch default (Kaiming uniform)
- Forward pass processes 28×28 images correctly
- Both architectures support batch processing

**Source:** Phase 2C Experiment Brief Section "Models"

### FR-3: Dataset Loading System
**Priority:** P0 (Critical)
**Description:** Load MNIST and Fashion-MNIST datasets with standard preprocessing.

**Requirements:**
- Download MNIST via `torchvision.datasets.MNIST`
- Download Fashion-MNIST via `torchvision.datasets.FashionMNIST`
- Apply normalization: mean=0.1307, std=0.3081
- Convert to tensor format [0, 1]
- No data augmentation (testing initialization, not generalization)

**Acceptance Criteria:**
- Both datasets load successfully
- Images are 28×28 grayscale
- Train/test splits: 60K/10K each
- 10 classes per dataset

**Source:** Phase 2C Experiment Brief Section "Dataset"

### FR-4: Pairwise Distance Computation
**Priority:** P0 (Critical)
**Description:** Compute Euclidean distances between all weight configuration pairs.

**Requirements:**
- For each seed pair (i, j):
  - Flatten all model parameters into single vector
  - Compute L2 distance: `||params_i - params_j||_2`
- Generate distance matrix (30 seeds → 435 pairs via combinations)
- Return list of all pairwise distances

**Acceptance Criteria:**
- Distance computation handles all parameter shapes (Linear layers)
- Output is list of 435 scalar distance values
- Distances are non-negative floats

**Source:** Jordan et al. 2024 (ICLR), Phase 2C Pseudo-code

### FR-5: Statistical Independence Testing
**Priority:** P0 (Critical)
**Description:** Test hypothesis that mean pairwise distance > 0 (seeds create different initializations).

**Requirements:**
- Perform one-sample t-test: `scipy.stats.ttest_1samp(distances, 0, alternative='greater')`
- Compute: mean distance, std distance, t-statistic, p-value
- Test at α = 0.05 significance level
- Report number of pairs tested

**Acceptance Criteria:**
- p-value < 0.05 indicates seed independence
- Test rejects null hypothesis H0: distance = 0
- All 4 conditions (2 architectures × 2 datasets) pass

**Source:** Phase 2C Experiment Brief Section "Evaluation"

### FR-6: Multi-Condition Experiment Runner
**Priority:** P0 (Critical)
**Description:** Execute seed independence test across 4 experimental conditions.

**Conditions:**
1. MLP1Layer + MNIST
2. MLP1Layer + Fashion-MNIST
3. MLP2Layer + MNIST
4. MLP2Layer + Fashion-MNIST

**Per Condition:**
- Initialize 30 models with seeds 0-29
- Compute 435 pairwise distances
- Run statistical test
- Save results

**Acceptance Criteria:**
- All 4 conditions execute without error
- Results saved per condition
- Summary report shows pass/fail for each condition

**Source:** Phase 2C Experiment Brief Section "Training Protocol"

### FR-7: Visualization System
**Priority:** P1 (High)
**Description:** Generate figures for seed independence analysis.

**Required Figure:**
- Gate Metrics Comparison: Target vs actual bar chart

**Recommended Figures:**
1. Distance Distribution Histogram (per condition)
2. Distance Heatmap (30×30 matrix, per condition)
3. Condition Comparison Boxplot (4 conditions side-by-side)

**Acceptance Criteria:**
- All figures saved to `{hypothesis_folder}/figures/`
- Figures use clear labels and legends
- Matplotlib or Seaborn rendering

**Source:** Phase 2C Experiment Brief Section "Visualization Requirements"

### FR-8: Results Logging and Reporting
**Priority:** P0 (Critical)
**Description:** Log all experimental results and generate validation report.

**Requirements:**
- Save per-condition statistics (mean, std, t-stat, p-value)
- Save gate validation result (PASS/FAIL per condition)
- Generate `04_validation.md` report with:
  - Hypothesis statement
  - Success criteria
  - Results per condition
  - Gate decision (PASS if all 4 conditions pass)
  - Figures embedded

**Acceptance Criteria:**
- All results saved to JSON/YAML format
- Validation report follows Phase 4 template
- Report includes interpretation and next steps

**Source:** Phase 4 Validation Requirements

---

## Non-Functional Requirements

### NFR-1: Execution Performance
- Total runtime: < 60 seconds (initialization only, no training)
- Memory usage: < 2GB (small models, no large datasets in memory)

### NFR-2: Reproducibility
- Same seed produces identical results across runs
- Determinism flags prevent any GPU non-determinism

### NFR-3: Code Quality
- Type hints for all functions
- Docstrings with parameter descriptions
- Unit tests for distance computation
- Integration test for full pipeline

### NFR-4: GPU Compatibility
- Support single GPU execution (CUDA_VISIBLE_DEVICES)
- Graceful fallback to CPU if no GPU available

---

## Data Requirements

### DR-1: MNIST Dataset
- **Type:** Standard torchvision dataset
- **Size:** 60K train + 10K test images
- **Format:** 28×28 grayscale, 10 classes
- **Loading:** Auto-download via `datasets.MNIST(root='./data', download=True)`

### DR-2: Fashion-MNIST Dataset
- **Type:** Standard torchvision dataset
- **Size:** 60K train + 10K test images
- **Format:** 28×28 grayscale, 10 classes (clothing items)
- **Loading:** Auto-download via `datasets.FashionMNIST(root='./data', download=True)`

### DR-3: Random Seed Range
- **Seeds:** 0-29 (30 independent seeds)
- **Rationale:** Rajput 2023's N≥30 criterion for stable variance estimation
- **Storage:** No storage required (seeds are just integers)

---

## Dependencies

### Python Libraries
- `torch` >= 2.0.0 (PyTorch framework)
- `torchvision` >= 0.15.0 (datasets, transforms)
- `numpy` >= 1.24.0 (numerical operations)
- `scipy` >= 1.10.0 (statistical tests)
- `matplotlib` >= 3.7.0 (visualization)
- `pyyaml` >= 6.0 (YAML parsing for config)

### External Services
- **Archon MCP:** Task management, document storage
- **Serena MCP:** (Optional) Code analysis if base hypothesis exists

### Hardware
- **GPU:** Optional (CUDA-capable, single GPU)
- **RAM:** 2GB minimum
- **Storage:** 200MB (datasets auto-download)

---

## Success Criteria

### Primary Success Criteria
1. **Seed Independence Validated:** Mean pairwise distance > 0 with p < 0.05 for all 4 conditions
2. **No Clustering:** Distance distribution shows no systematic patterns (confirms independence)

### Secondary Success Criteria
3. **Code Quality:** All unit tests pass, type hints complete
4. **Documentation:** Validation report complete with figures
5. **Reproducibility:** Re-running with same seeds produces identical results

### Gate Validation
- **Gate Type:** MUST_WORK
- **Pass Condition:** All 4 experimental conditions show p < 0.05
- **Fail Consequence:** PIVOT - investigate PyTorch determinism failures, check seed control implementation

---

## Out of Scope

- Training neural networks (initialization-only experiment)
- Variance scaling analysis (covered in H-E1, H-M3)
- Alternative distance metrics (e.g., HSIC, α-trimming)
- Multi-GPU distributed training
- Model performance evaluation (accuracy, loss)

---

## Risks and Mitigations

### R1: PyTorch Non-Determinism
**Risk:** GPU operations may introduce non-determinism despite flags
**Mitigation:** Set `CUBLAS_WORKSPACE_CONFIG`, verify determinism with checksums

### R2: Insufficient Statistical Power
**Risk:** 30 seeds may not provide enough pairs for robust p-value
**Mitigation:** 30 choose 2 = 435 pairs provides strong statistical power

### R3: Prerequisite Failure Impact
**Risk:** H-E1 failure may suggest fundamental CLT issues
**Mitigation:** H-M1 tests initialization mechanism independently, can proceed

---

## Timeline and Milestones

**Total Estimated Duration:** 20 seconds (experiment runtime)

### Phase 4 Implementation
- Environment setup: Task 1
- Data preparation: Task 2
- Model implementation: Tasks 3-4
- Distance computation: Task 5
- Statistical testing: Task 6
- Visualization: Task 7
- Validation report: Task 8

**Implementation Budget:** 6-12 epic tasks (FULL tier)

---

## Appendix: Research References

### A. PyTorch Reproducibility
- **Source:** PyTorch Official Documentation
- **URL:** https://pytorch.org/docs/stable/notes/randomness.html
- **Applied:** Determinism setup protocol (FR-1)

### B. Variance Analysis Framework
- **Source:** Jordan et al. 2024 (ICLR) - "On the Variance of Neural Network Training with respect to Test Sets"
- **URL:** https://arxiv.org/abs/2304.01910
- **Applied:** Pairwise distance methodology (FR-4)

### C. Sample Size Validation
- **Source:** Rajput 2023 - "Decided sample size validation"
- **Applied:** N≥30 criterion for seed count (DR-3)

---

*Generated by Phase 3 Implementation Planning - PRD Workflow*
*Hypothesis: h-m1 (MECHANISM) | Gate: MUST_WORK*
*Next: Architecture Design (03_architecture.md)*
