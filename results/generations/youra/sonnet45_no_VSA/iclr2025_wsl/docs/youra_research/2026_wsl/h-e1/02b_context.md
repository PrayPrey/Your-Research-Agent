# H-E1 Context: Statistical Features Sufficiency

**Generated:** 2026-07-11  
**Type:** EXISTENCE  
**Gate:** MUST_WORK

---

## 1. Hypothesis Information

### 1.1 Statement
Under TIMM model zoo evaluation, if normalization layer counts and parameter-mass ratio are extracted from checkpoints, then >80% 3-way classification accuracy (CNN/Transformer/Hybrid) can be achieved because these features capture fundamental architectural constraints (BatchNorm for spatial data, LayerNorm for sequential, conv vs linear parameter allocation).

### 1.2 Rationale
This hypothesis validates that simple statistical features are sufficient for architecture family classification, challenging the assumption that complex GNN architectures (Kofinas 2024) are necessary. Success proves the phenomenon exists and justifies investigating the underlying mechanism. Failure would indicate that weight-space structure requires deeper analysis than surface statistics.

### 1.3 Variables
- **Independent:** Architecture family (CNN / Transformer / Hybrid)
- **Dependent:** Classification accuracy (macro-averaged)
- **Controlled:** Model size (multi-scale), Family diversity (stratified split), Ground truth (TIMM naming)

---

## 2. Experimental Setup

### 2.1 Dataset Specification
| Component | Value |
|-----------|-------|
| **Name** | TIMM Model Zoo |
| **Type** | Standard |
| **Source** | timm.create_model() + load checkpoints |
| **Size** | 50 models (20 CNN, 20 Transformer, 10 Hybrid) |
| **Split** | 70% train (35 models), 30% validation (15 models) |
| **Preprocessing** | Stratified split by architecture family |

### 2.2 Model Specification
| Component | Value |
|-----------|-------|
| **Type** | Linear classifier |
| **Architecture** | Logistic Regression |
| **Source** | sklearn.linear_model.LogisticRegression |
| **Purpose** | Tests feature sufficiency—no MLP rescue allowed |

---

## 3. Verification Protocol

### 3.1 Steps
1. Extract normalization counts (BN, LN, GN, No_norm_flag) and parameter-mass ratio R from 50 TIMM model checkpoints
2. Train logistic regression classifier on 70% (35 models), validate on 30% (15 models) with stratified split
3. Measure macro-averaged accuracy on validation set and per-class accuracy breakdown
4. Validate scale invariance: intra-family CV <0.15 across ResNet-{18,34,50,101,152}
5. Document confusion matrix and failure cases

### 3.2 Success Criteria (PoC: Direction-based)
- **Primary:** Validation accuracy >80% (macro-averaged across 3 classes)
- **Secondary:** Per-class accuracy ≥75% (no single class collapse)

---

## 4. Gate Conditions

### 4.1 Gate Type
**MUST_WORK** - This hypothesis must succeed for dependent hypotheses to proceed.

### 4.2 Failure Consequence
**ABANDON** - Features insufficient → need complex representations (GNN/MLP)

### 4.3 Prerequisites
None (foundation hypothesis)

---

## 5. Baseline & Comparison

### 5.1 Baseline Methods
| Method | Performance | Dataset |
|--------|-------------|---------|
| Kofinas et al. 2024 GNN | High accuracy with GNN | Various NN architectures |
| Zhang & Abdulla 2023 | BatchNorm statistics | Performance prediction |

### 5.2 Research Gap & Novelty
**Core Contribution:** First interpretable, checkpoint-only classifier requiring no forward pass, GNN processing, or model instantiation.

**vs Kofinas et al. (2024):** Complex GNN processing (50+ hours) vs simple statistical features (6 hours, <15 tasks)

**vs Zhang & Abdulla (2023):** Requires forward passes for BatchNorm runtime statistics vs checkpoint-only analysis

---

## 6. Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | TIMM naming aligns with structure | Expected >90% alignment on 10-model sample | Mislabeled training data → wrong features |
| A2 | Normalization reflects paradigm, not training | Violation rate must be ≤15% per class | Features lose discriminative power |
| A3 | Parameter-mass ratio is scale-invariant | Intra-family CV <0.15 across ResNet-{18,34,50,101,152} | Scale confounds structure signal |
| A4 | Linear classifier sufficient | Logistic regression test passes | Features are not linearly separable |

---

## 7. Risk Assessment

| Risk ID | Description | Severity | Mitigation |
|---------|-------------|----------|------------|
| R1 | TIMM naming misalignment >10% | Medium | Validate 10-model sample via structural inspection |
| R2 | Normalization convention risk (violation >15%) | High | Test violation rate, add GroupNorm patterns as backup |
| R3 | Scale invariance failure (CV ≥0.15) | High | Validate CV pre-experiment, normalize by model size |
| R4 | Linear classifier insufficient | Critical | Pre-test with 2D visualization, ABANDON if fails |

---

## 8. Previous Context

**Status:** First hypothesis (no prerequisites)

**Previous Validation Results:** N/A

**Lessons Learned:** N/A

---
