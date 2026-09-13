# Product Requirements Document: H-M4

**Hypothesis:** Layer-wise Grassmann Distance Analysis for Task-Similarity Clustering
**Type:** MECHANISM (Exploratory)
**Date:** 2026-04-13
**Author:** Phase 3 Implementation Planning

---

## 1. Executive Summary

This PRD specifies the implementation requirements for H-M4, a mechanism hypothesis that analyzes whether different layer types (attention vs MLP) in LoRA adapters show varying strengths of task-similarity clustering. The experiment disaggregates the aggregate Grassmann distance analysis from H-E1 to identify which specific layer types carry the strongest task-similarity signal.

**Key Deliverable:** Analysis pipeline that computes Cohen's d per layer type for within-cluster vs between-cluster Grassmann distances, identifying layers with d > 0.8.

---

## 2. Problem Statement

### 2.1 Background
H-E1 validated that LoRA adapter geometric signatures cluster by task category (aggregate Cohen's d = 0.7652). H-M3 confirmed the mechanism linking semantic similarity to geometric similarity (Spearman ρ = 0.389). H-M4 investigates whether this clustering signal is uniformly distributed across layer types or concentrated in specific layers.

### 2.2 Research Question
Do different layer types (attention: q/k/v/o_proj vs MLP: up/down/gate_proj) show different strengths of task-similarity clustering in their LoRA adapter B matrix column spaces?

### 2.3 Success Criteria
- **Primary:** At least one layer type shows Cohen's d > 0.8
- **Secondary:** Systematic difference identified between attention and MLP layer groups

---

## 3. Functional Requirements

### FR-1: Adapter Loading Module
**Description:** Load the 40 validated LoRA adapters from H-E1 results
**Input:** H-E1 adapter directory (`h-e1/results/adapters/`)
**Output:** Dictionary of adapter weights organized by task and seed
**Acceptance Criteria:**
- Load all 40 adapters (8 tasks × 5 seeds)
- Extract B matrices for all 7 layer types across 22 transformer layers
- Validate adapter structure matches TinyLlama architecture

### FR-2: Layer-Type Distance Computation
**Description:** Compute pairwise Grassmann distances for each layer type
**Input:** Loaded adapter B matrices
**Output:** 7 distance matrices (one per layer type), each 40×40
**Acceptance Criteria:**
- Compute Grassmann geodesic distance using QR decomposition + SVD
- Average distances across layers of same type (e.g., all q_proj layers)
- Handle numerical stability with clamping for arccos

### FR-3: Within/Between Cluster Splitting
**Description:** Split distance matrices into within-cluster and between-cluster pairs
**Input:** Distance matrix, task category mapping
**Output:** Two arrays: within-cluster distances, between-cluster distances
**Acceptance Criteria:**
- Use FLAN taxonomy categories: Reasoning (gsm8k, arc, logiqa, strategyqa), NLU (mnli, qqp, sst2, mrpc)
- Exclude self-distances (diagonal)
- Correct pair counting for each category

### FR-4: Cohen's d Computation with Bootstrap CI
**Description:** Compute effect size with confidence intervals for each layer type
**Input:** Within and between distance arrays
**Output:** Cohen's d value with 95% CI (low, high)
**Acceptance Criteria:**
- Use pooled standard deviation formula
- Compute bootstrap CI with 2000 iterations
- Report both point estimate and interval

### FR-5: Layer Type Ranking and Analysis
**Description:** Rank layer types by Cohen's d and analyze attention vs MLP groups
**Input:** Cohen's d results for all 7 layer types
**Output:** Ranked list, group statistics, gate evaluation
**Acceptance Criteria:**
- Sort by Cohen's d descending
- Compute mean d for attention group (4 types) vs MLP group (3 types)
- Statistical test for group difference (if appropriate)

### FR-6: Visualization Generation
**Description:** Generate required figures for analysis
**Input:** Analysis results
**Output:** Figures saved to `h-m4/figures/`
**Acceptance Criteria:**
- Bar chart: Cohen's d per layer type with 0.8 threshold line and CI error bars
- Horizontal ranking chart: All 7 layer types by Cohen's d
- Attention vs MLP comparison: Box/violin plot
- Heatmap: 8×8 task-level mean distance for best layer type

### FR-7: Gate Evaluation and Report Generation
**Description:** Evaluate SHOULD_WORK gate and generate validation report
**Input:** Analysis results
**Output:** Gate result, 04_validation.md report
**Acceptance Criteria:**
- PASS if any layer type has Cohen's d > 0.8
- Record all layer-type results regardless of gate outcome
- Include figures in report

---

## 4. Data Specification

### 4.1 Input Data

#### H-E1 Adapter Dataset
- **Source:** H-E1 validation results
- **Location:** `h-e1/results/adapters/`
- **Format:** SafeTensors adapter files
- **Structure:**
  ```
  adapters/
  ├── gsm8k/
  │   ├── seed_42/adapter_model.safetensors
  │   ├── seed_43/...
  │   └── seed_46/
  ├── arc/
  ├── logiqa/
  ├── strategyqa/
  ├── mnli/
  ├── qqp/
  ├── sst2/
  └── mrpc/
  ```
- **Statistics:** 40 adapters (8 tasks × 5 seeds)
- **Download Required:** NO (local data from H-E1)

#### Task Category Mapping
- **Reasoning:** gsm8k, arc, logiqa, strategyqa
- **NLU:** mnli, qqp, sst2, mrpc

### 4.2 Output Data

#### Analysis Results
- **Location:** `h-m4/results/`
- **Files:**
  - `layer_distances.npz`: Distance matrices per layer type
  - `cohens_d_results.json`: Effect sizes with CIs
  - `analysis_summary.json`: Complete analysis output

#### Figures
- **Location:** `h-m4/figures/`
- **Files:**
  - `cohens_d_by_layer_type.png`
  - `layer_type_ranking.png`
  - `attention_vs_mlp.png`
  - `best_layer_heatmap.png`

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Analysis should complete in < 5 minutes on CPU
- Memory usage < 4GB RAM
- No GPU required

### NFR-2: Reproducibility
- Fixed random seed for bootstrap (seed=42)
- Deterministic distance computation
- All results logged with timestamps

### NFR-3: Code Quality
- Type hints for all functions
- Docstrings with parameter descriptions
- Unit tests for core functions

---

## 6. Success Criteria

### 6.1 Primary Gate (SHOULD_WORK)
- **Metric:** Maximum Cohen's d across layer types
- **Threshold:** d > 0.8 for at least one layer type
- **Consequence if Fails:** EXPLORE (informative null result, no mechanism block)

### 6.2 Secondary Criteria
- Clear ranking of layer types by effect size
- Identifiable pattern in attention vs MLP comparison
- Statistical significance (p < 0.05) for best layer type

### 6.3 Expected Outcomes
- **Optimistic:** Multiple layer types exceed d > 0.8, clear attention/MLP separation
- **Expected:** 1-2 layer types exceed d > 0.8, moderate group difference
- **Pessimistic:** No layer exceeds d > 0.8, uniform distribution (informative null)

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
safetensors>=0.3.0
pyyaml>=6.0
pingouin>=0.5.0  # For bootstrap CI
tqdm>=4.65.0
```

### 7.2 Internal Dependencies
- H-E1 results: 40 trained adapters with validated geometric signatures
- H-M3 results: Task category mapping, FLAN taxonomy distances

### 7.3 External Repositories
- None required (analysis-only experiment)

---

## 8. Assumptions and Constraints

### 8.1 Assumptions
- H-E1 adapters are correctly formatted and loadable
- TinyLlama architecture has 22 transformer layers with 7 layer types each
- B matrix column spaces are suitable for Grassmann distance computation

### 8.2 Constraints
- Analysis only - no model training or inference
- Must use same task categories as H-E1/H-M3
- Bootstrap CI must use same seed for reproducibility

---

## 9. Out of Scope

- Training new adapters
- Model inference or evaluation
- Cross-model comparison
- Layer pruning or selection optimization
- Real-time analysis pipeline

---

## 10. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| No layer exceeds d > 0.8 | Low (SHOULD_WORK gate) | Document as informative null result |
| Numerical instability in Grassmann distance | Medium | Use clamping for arccos, validate with known distances |
| Memory issues with 40×40×7 matrices | Low | Process layer types sequentially if needed |

---

*Generated by Phase 3 Implementation Planning*
*Input: h-m4/02c_experiment_brief.md*
*Next: 03_architecture.md*
