# Product Requirements Document: H-M3

**Hypothesis:** H-M3 - FLAN Taxonomy Correlation with Grassmann Distances
**Date:** 2026-04-13
**Author:** Anonymous
**Version:** 1.0
**Status:** Draft
**Type:** MECHANISM (MUST_WORK Gate)

---

## 1. Executive Summary

This PRD defines the requirements for validating hypothesis H-M3: Under identical training conditions, if two tasks are semantically similar (same FLAN category), then their LoRA adapters will have similar B matrix column spaces (Spearman ρ > 0.3 with FLAN taxonomy distances), because similar tasks require similar functional transformations in the output dimension.

**Scope:** MECHANISM validation building on H-E1's existence proof. Tests whether the geometric clustering observed in H-E1 correlates systematically with semantic similarity defined by FLAN taxonomy.

**Key Deliverables:**
1. FLAN taxonomy distance matrix construction
2. Spearman correlation analysis pipeline
3. P3 control condition validation (within-task variance baseline)
4. Statistical significance analysis with bootstrap confidence intervals

**Continuation Context:**
- **Prerequisite:** H-E1 VALIDATED (p=8.63e-28, Cohen's d=0.7652)
- **Reused Components:** 40 trained adapters (8 tasks × 5 seeds), Grassmann distance computation
- **No New Training Required:** Analysis-only experiment using existing adapters

---

## 2. Problem Statement

### 2.1 Background
H-E1 established that within-cluster Grassmann distances are significantly smaller than between-cluster distances. H-M3 now tests whether this pattern reflects a systematic relationship: does geometric similarity (Grassmann distance) correlate with semantic similarity (FLAN taxonomy)?

### 2.2 Objective
Validate that Spearman rank correlation between Grassmann distances and FLAN taxonomy distances is significant (ρ > 0.3, p < 0.05), establishing a mechanism linking task semantics to adapter geometry.

### 2.3 Success Criteria (MUST_WORK Gate)
- **Primary:** Spearman ρ > 0.3 AND p < 0.05
- **Secondary (P3 Control):** within_task_distance < 0.5 × within_cluster_distance
- **Interpretation:** Positive correlation means similar tasks → similar adapter geometry

---

## 3. Functional Requirements

### FR-1: Load Pre-trained Adapters from H-E1
**Priority:** P0 (Critical)
**Description:** Load existing LoRA adapters from H-E1 validation

| Requirement | Specification |
|-------------|---------------|
| FR-1.1 | Load 40 adapters from `../h-e1/adapters/` directory |
| FR-1.2 | Verify adapter integrity (8 tasks × 5 seeds) |
| FR-1.3 | Extract task labels and seed information from folder names |
| FR-1.4 | Validate adapter configuration matches H-E1 specs (r=32, alpha=64) |

### FR-2: Compute/Load Grassmann Distance Matrix
**Priority:** P0 (Critical)
**Description:** Obtain pairwise Grassmann distances between adapter B matrices

| Requirement | Specification |
|-------------|---------------|
| FR-2.1 | Option A: Load precomputed distances from `../h-e1/results/pairwise_distances.npy` |
| FR-2.2 | Option B: Recompute from adapters using H-E1 analysis code |
| FR-2.3 | Verify matrix shape: (40, 40) for 40 adapters |
| FR-2.4 | Validate symmetry and zero diagonal |

### FR-3: Construct FLAN Taxonomy Distance Matrix
**Priority:** P0 (Critical)
**Description:** Build semantic similarity ground truth from FLAN categories

| Requirement | Specification |
|-------------|---------------|
| FR-3.1 | Define FLAN category mapping for 8 tasks |
| FR-3.2 | Compute binary taxonomy distance: 0=same category, 1=different category |
| FR-3.3 | Generate (40, 40) taxonomy distance matrix |
| FR-3.4 | Support hierarchical distance if binary insufficient |

**FLAN Category Mapping:**
| Task | Category |
|------|----------|
| gsm8k | Reasoning |
| arc | Reasoning |
| logiqa | Reasoning |
| strategyqa | Reasoning |
| mnli | NLU |
| qqp | NLU |
| sst2 | NLU |
| mrpc | NLU |

### FR-4: Spearman Correlation Analysis
**Priority:** P0 (Critical)
**Description:** Compute rank correlation between Grassmann and taxonomy distances

| Requirement | Specification |
|-------------|---------------|
| FR-4.1 | Flatten upper triangle of both distance matrices (exclude diagonal) |
| FR-4.2 | Compute Spearman ρ using scipy.stats.spearmanr |
| FR-4.3 | Compute bootstrap 95% confidence interval (n=1000 iterations) |
| FR-4.4 | Report correlation coefficient, p-value, and CI bounds |

### FR-5: P3 Control Condition Validation
**Priority:** P0 (Critical)
**Description:** Verify training stochasticity does not dominate signal

| Requirement | Specification |
|-------------|---------------|
| FR-5.1 | Extract within-task distances (same task, different seeds) |
| FR-5.2 | Extract within-cluster distances (same category, different tasks) |
| FR-5.3 | Validate: within_task_mean < 0.5 × within_cluster_mean |
| FR-5.4 | Report control condition pass/fail status |

### FR-6: Visualization
**Priority:** P1 (High)
**Description:** Generate figures for result interpretation

| Requirement | Specification |
|-------------|---------------|
| FR-6.1 | **Gate Metrics Bar Chart**: Spearman ρ vs threshold (0.3) with significance annotation |
| FR-6.2 | **Scatter Plot**: Grassmann distance vs taxonomy distance with regression line |
| FR-6.3 | **Correlation Heatmap**: Task-level correlation matrix |
| FR-6.4 | **P3 Control Plot**: Within-task vs within-cluster distance distributions |
| FR-6.5 | Save all figures to `{hypothesis_folder}/figures/` |

---

## 4. Data Specification

### 4.1 Input Data

#### 4.1.1 Pre-trained Adapters (from H-E1)
- **Source:** `../h-e1/adapters/`
- **Count:** 40 adapters (8 tasks × 5 seeds)
- **Format:** PEFT adapter format (adapter_model.safetensors + adapter_config.json)
- **No download required:** Already generated in H-E1

#### 4.1.2 Grassmann Distances (from H-E1)
- **Source:** `../h-e1/results/pairwise_distances.npy` (if exists)
- **Alternative:** Recompute from adapters
- **Format:** NumPy (40, 40) float array

### 4.2 Generated Data

#### 4.2.1 Taxonomy Distance Matrix
- **Location:** `{hypothesis_folder}/results/`
- **File:** `taxonomy_distances.npy`
- **Format:** NumPy (40, 40) binary array

#### 4.2.2 Correlation Results
- **Location:** `{hypothesis_folder}/results/`
- **File:** `correlation_results.json`
- **Content:**
```json
{
  "spearman_rho": float,
  "p_value": float,
  "ci_low": float,
  "ci_high": float,
  "p3_control_passed": bool,
  "within_task_mean": float,
  "within_cluster_mean": float
}
```

---

## 5. Non-Functional Requirements

### NFR-1: Reproducibility
- Use identical random seed (42) for bootstrap sampling
- Document all library versions in requirements.txt
- Results must be reproducible from H-E1 adapters

### NFR-2: Performance
- Total execution time: < 5 minutes (analysis only, no training)
- Memory: < 8GB RAM (no GPU required for analysis)

### NFR-3: Compatibility
- Must work with H-E1 adapter format
- Scipy >= 1.11.0 for spearmanr

---

## 6. Success Criteria

### 6.1 Gate Conditions (MUST_WORK)

| Metric | Threshold | Status |
|--------|-----------|--------|
| Spearman ρ | > 0.3 | Required |
| p-value | < 0.05 | Required |
| P3 Control | within_task < 0.5 × within_cluster | Required |

### 6.2 Expected Performance
Based on H-E1 results:
- H-E1 showed Cohen's d = 0.7652 for within vs between cluster
- This suggests positive correlation expected (similar tasks → smaller distances)
- Expected Spearman ρ: 0.3-0.6 range

### 6.3 Interpretation Guide
| Spearman ρ | Interpretation |
|------------|----------------|
| ρ > 0.5 | Strong correlation - semantic similarity strongly predicts geometric similarity |
| 0.3 < ρ < 0.5 | Moderate correlation - mechanism confirmed with room for other factors |
| ρ < 0.3 | Weak/no correlation - mechanism not supported, explore alternatives |

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
transformers>=4.36.0
peft>=0.7.0
scipy>=1.11.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
pandas>=2.0.0
tqdm>=4.65.0
```

### 7.2 External Dependencies
- H-E1 validated adapters (40 adapters in `../h-e1/adapters/`)
- H-E1 analysis code (optional, for Grassmann distance recomputation)

### 7.3 Reference Implementations
- scipy.stats.spearmanr: Standard Spearman correlation implementation
- FLAN v2 taxonomy: https://github.com/google-research/FLAN/blob/main/flan/v2/flan_collection_info.csv

---

## 8. Constraints

### 8.1 Technical Constraints
- Analysis-only (no training)
- Must use H-E1 adapters exactly (no retraining)
- Binary taxonomy distance (same/different category)

### 8.2 Scope Constraints
- Tests correlation only, not causation
- Limited to 8 tasks across 2 categories
- FLAN taxonomy as ground truth (external validation)

---

## 9. Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| H-E1 adapter corruption | High | Low | Verify adapter integrity before analysis |
| Insufficient variance | Medium | Low | 40 adapters with 5 seeds provides sufficient variance |
| P3 control failure | High | Medium | If within-task > 0.5 × within-cluster, investigate training instability |
| Binary taxonomy too coarse | Medium | Medium | Fallback: hierarchical taxonomy or task embedding similarity |

---

## 10. Implementation Notes

### 10.1 Continuation from H-E1
This experiment builds directly on H-E1:
- **Reused:** Adapters, Grassmann distance computation code
- **New:** FLAN taxonomy matrix, Spearman correlation, P3 control analysis
- **Changed:** Only analysis component, no training

### 10.2 Failure Mitigation (R1)
If FLAN taxonomy fails (ρ < 0.3):
- Alternative metric: Task embedding cosine similarity (using sentence-transformers)
- This provides continuous similarity rather than binary

---

*Generated by Phase 3 PRD Workflow | Anonymous Research Pipeline*
*Source: 02c_experiment_brief.md (Phase 2C)*
*Continuation Experiment: Builds on H-E1 validated infrastructure*
