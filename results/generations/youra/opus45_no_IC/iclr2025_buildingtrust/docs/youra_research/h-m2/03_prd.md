# Product Requirements Document: H-M2

**Hypothesis:** Different confidence distributions require different temperature parameters for optimal calibration
**Type:** MECHANISM
**Date:** 2026-08-10
**Author:** YouRA Research Pipeline

---

## 1. Executive Summary

This PRD specifies implementation requirements for hypothesis H-M2, which tests whether optimal temperature scaling parameters vary significantly across semantic clusters in LLM calibration on TruthfulQA. Building on H-M1's confirmation that category-specific confidence distributions exist (17/21 cluster pairs significantly different), this experiment determines if these distribution differences necessitate different calibration temperatures.

**Success Criteria:** Coefficient of variation (CV) of optimal temperatures > 0.1, Range of optimal temperatures > 0.3

---

## 2. Problem Statement

### Background
H-M1 established that LLMs produce category-specific confidence distributions on TruthfulQA (KS test: 17/21 pairs p<0.05). If distributions differ, optimal calibration parameters should also differ. Global temperature scaling applies one T to all clusters, potentially leaving some clusters poorly calibrated.

### Core Question
Do optimal temperature parameters vary meaningfully across semantic clusters?

### Business Impact
- Validates theoretical foundation for cluster-specific calibration
- Determines if per-cluster temperature optimization is necessary
- Gate for H-M3 (cluster-specific vs global comparison)

---

## 3. Scope

### In Scope
- Per-cluster temperature optimization using L-BFGS-B
- 5-fold cross-validation per cluster
- Coefficient of variation and range calculation
- Statistical bootstrap confidence intervals
- Visualization of temperature variation

### Out of Scope
- Comparison with global temperature (H-M3)
- Multi-model evaluation (single model: Llama-2-7B)
- Production deployment

---

## 4. Data Specification

### 4.1 Primary Dataset

| Attribute | Value |
|-----------|-------|
| **Name** | TruthfulQA |
| **Source** | HuggingFace: `truthful_qa` |
| **Size** | 817 questions |
| **Clusters** | 7 semantic clusters |
| **Split** | 5-fold CV (80/20 per cluster) |

**Loading Code:**
```python
from datasets import load_dataset
dataset = load_dataset("truthful_qa", "generation")
```

### 4.2 Pre-computed Data Dependencies

| Data | Source | Description |
|------|--------|-------------|
| Cluster assignments | H-M1 output | 7 semantic clusters from 38 categories |
| Logits | H-M1 output | Pre-computed model logits for all 817 questions |

---

## 5. Model Specification

### 5.1 Base Model

| Attribute | Value |
|-----------|-------|
| **Architecture** | Llama-2-7B |
| **Source** | HuggingFace: `meta-llama/Llama-2-7b-hf` |
| **Purpose** | Extract logits for temperature scaling |

### 5.2 Proposed Method

**Per-cluster Temperature Optimization:**
- Independent T optimization for each of 7 clusters
- Optimizer: L-BFGS-B (scipy.optimize.minimize)
- Loss: Negative Log Likelihood
- Bounds: T ∈ [0.1, 10.0]
- Initial: T = 1.0

---

## 6. Functional Requirements

### FR-1: Data Loading
- Load TruthfulQA dataset from HuggingFace
- Load cluster assignments from H-M1 output
- Load pre-computed logits from H-M1 output

### FR-2: Cross-Validation Setup
- Implement 5-fold CV with stratified splits per cluster
- Ensure minimum 80 samples per fold per cluster

### FR-3: Per-Cluster Temperature Optimization
- Optimize temperature T for each cluster independently
- Use L-BFGS-B with NLL loss
- Apply bounds [0.1, 10.0] to prevent degenerate solutions

### FR-4: Variation Metrics Computation
- Compute coefficient of variation: CV = std(T) / mean(T)
- Compute range: max(T) - min(T)
- Bootstrap 95% confidence intervals (n=1000)

### FR-5: Gate Evaluation
- Primary gate: CV > 0.1
- Secondary gate: Range > 0.3
- Report PASS/FAIL with metrics

### FR-6: Visualization
- Bar chart: Optimal T per cluster with error bars
- Box plot: T distribution across CV folds
- Save to `figures/` directory

### FR-7: Ablation Studies
- **A1: Optimization bounds sensitivity** - Test [0.5, 5.0] vs [0.1, 10.0]
- **A2: Initialization sensitivity** - Test T_init ∈ {0.5, 1.0, 2.0}

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.30.0
datasets>=2.14.0
scipy>=1.10.0
numpy>=1.24.0
matplotlib>=3.7.0
pyyaml>=6.0
```

### 7.2 External References

| Reference | URL | Purpose |
|-----------|-----|---------|
| gpleiss/temperature_scaling | https://github.com/gpleiss/temperature_scaling | Canonical T-scaling implementation |
| TorchUncertainty | https://torch-uncertainty.github.io/ | VectorScaler reference |

---

## 8. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seeds for all CV splits
- Deterministic optimization (same initial conditions)

### NFR-2: Efficiency
- Optimization should complete in <5 minutes per cluster
- Total runtime <1 hour for full experiment

### NFR-3: Logging
- Log optimal T for each cluster and fold
- Save intermediate results for debugging

---

## 9. Success Criteria

| Metric | Threshold | Priority |
|--------|-----------|----------|
| CV(optimal T) | > 0.1 | Primary Gate |
| Range(optimal T) | > 0.3 | Secondary Gate |
| Bootstrap CI width | Report | Informational |

---

## 10. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Small cluster sizes | Verify min 80 samples/cluster from H-M1 |
| Optimization convergence | Use bounded L-BFGS-B with multiple restarts |
| Numerical instability | Add epsilon (1e-10) to log probabilities |

---

*Generated by Phase 3 Implementation Planning*
*Source: 02c_experiment_brief.md*
