# Product Requirements Document (PRD)

**Project:** H-M4 Geometry-Phenotype Coupling Verification
**Date:** 2026-04-24
**Author:** Anonymous
**Hypothesis Type:** MECHANISM
**Gate:** SHOULD_WORK

---

## 1. Executive Summary

### 1.1 Purpose

Implement experiment to test functional coupling between loss landscape geometry (curvature alignment A(w)) and distribution shift robustness (worst-group accuracy) along mode-connected paths. This is the final mechanism hypothesis validating whether geometric regions determine robustness outcomes.

### 1.2 Success Criteria

**Primary (PoC - Direction-based):**
- FGE path shows Spearman ρ(A(w), WGA) < -0.6, p < 0.01
- Validates strong negative coupling (low alignment → high robustness)

**Secondary:**
- Linear interpolation shows ρ(A(w), WGA) < -0.7
- Confirms coupling is not artifact of FGE optimization

### 1.3 Scope

**In Scope:**
- Fast Geometric Ensembling (FGE) path sampling (M=20 checkpoints)
- Linear interpolation validation path
- A(w) computation for each checkpoint (reuse from H-M2)
- Worst-group accuracy evaluation
- Spearman correlation analysis

**Out of Scope:**
- New training (reuse H-E1 ERM and DRO endpoints)
- Additional datasets beyond Waterbirds
- Novel curvature metrics

---

## 2. Problem Statement

### 2.1 Research Question

At convergence, if solutions have lower minority-gradient alignment A(w) (from H-M3 SGD flow), do they exhibit better worst-group accuracy?

### 2.2 Hypothesis

Functional coupling between geometry and phenotype within mode-connected manifolds means geometric regions determine robustness outcomes.

### 2.3 Dependencies on Prior Work

**From H-E1:**
- ERM endpoint checkpoint (A(w) ≈ 0.72, WGA ≈ 60-75%)
- DRO endpoint checkpoint (A(w) ≈ 0.32, WGA ≈ 75-80%)

**From H-M1:**
- Marchenko-Pastur outlier detection (23 vs 15 outliers validated)

**From H-M2:**
- A(w) computation: A(w) = ||P_S_out g_minority||² / ||g_minority||²
- Minority gradient extraction

**From H-M3:**
- SGD directional bias confirmation (bulk vs outlier alignment)

---

## 3. Functional Requirements

### FR-1: Path Sampling

**Priority:** CRITICAL
**Description:** Sample M=20 checkpoints along mode-connected path between ERM and DRO endpoints

**Acceptance Criteria:**
- FGE path: Linear interpolation α ∈ [0, 1]
- M=20 checkpoints with valid parameter states
- Each checkpoint loadable into ResNet-50

**Dependencies:** ERM and DRO endpoint checkpoints from H-E1

### FR-2: Curvature Alignment Computation

**Priority:** CRITICAL
**Description:** Compute A(w) for each of M=20 checkpoints using H-M2 implementation

**Acceptance Criteria:**
- Reuse Marchenko-Pastur outlier detection from H-M1
- Compute alignment A(w) = ||P_S_out g_minority||² / ||g_minority||²
- Array of M=20 alignment values

**Dependencies:** H-M1 curvature code, H-M2 alignment code

### FR-3: Worst-Group Accuracy Evaluation

**Priority:** CRITICAL
**Description:** Evaluate WGA for each of M=20 checkpoints on Waterbirds test set

**Acceptance Criteria:**
- Standard 4-group evaluation (landbird-land, landbird-water, waterbird-land, waterbird-water)
- WGA = min(group accuracies)
- Array of M=20 WGA values

**Dependencies:** Waterbirds dataset, group labels

### FR-4: Correlation Analysis

**Priority:** CRITICAL
**Description:** Compute Spearman correlation ρ(A(w), WGA) to test monotonic coupling

**Acceptance Criteria:**
- Spearman ρ with p-value
- Visualization: scatter plot with regression line
- Statistical significance test (p < 0.01)

**Dependencies:** scipy.stats.spearmanr

### FR-5: Linear Interpolation Validation

**Priority:** HIGH
**Description:** Validate FGE results with simpler linear interpolation path

**Acceptance Criteria:**
- Same M=20 sampling along linear path
- Compute A(w) and WGA for each checkpoint
- Compare ρ_linear vs ρ_fge

**Dependencies:** FR-1, FR-2, FR-3

### FR-6: Visualization Generation

**Priority:** HIGH
**Description:** Generate required figures for validation report

**Acceptance Criteria:**
- Coupling scatter plot (A(w) vs WGA)
- Path trajectory plot (α vs A(w), WGA dual axes)
- FGE vs Linear comparison
- Group-specific accuracy along path

**Dependencies:** matplotlib, seaborn

---

## 4. Data Specification

### 4.1 Datasets

**Primary Dataset: Waterbirds**
- **Type:** Standard (ground-truth spurious labels)
- **Source:** group_DRO repository
- **Loading:** Via WILDS or group_DRO data scripts
- **Splits:** Train (4,795), Val (1,199), Test (5,794)
- **Classes:** 2 (landbird, waterbird)
- **Groups:** 4 (landbird-land, landbird-water, waterbird-land, waterbird-water)
- **Download:** Automatic via `wilds.get_dataset("waterbirds", download=True)`

**Preprocessing:**
```python
transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225])
])
```

### 4.2 Model Checkpoints (Static Baselines)

**ERM Endpoint:** From H-E1 validation
- Path: `h-e1/checkpoints/erm_final.pt`
- Expected A(w): ~0.72
- Expected WGA: 60-75%

**DRO Endpoint:** From H-E1 validation
- Path: `h-e1/checkpoints/dro_final.pt`
- Expected A(w): ~0.32
- Expected WGA: 75-80%

---

## 5. Non-Functional Requirements

### NFR-1: Performance

- Path sampling: < 1 minute (no training required)
- A(w) computation per checkpoint: < 30 seconds
- WGA evaluation per checkpoint: < 10 seconds
- Total experiment runtime: < 15 minutes

### NFR-2: Reproducibility

- Fixed seed: 42 (consistent with H-E1)
- Deterministic interpolation
- All hyperparameters logged

### NFR-3: Code Quality

- Reuse H-M1, H-M2 validated code
- Clear module separation (path_sampling, metrics, analysis)
- Type hints for all functions
- Docstrings for public APIs

---

## 6. Evaluation Metrics

### Primary Metrics

1. **Spearman Correlation ρ(A(w), WGA)**
   - Expected: ρ < -0.6 (strong negative coupling)
   - Statistical test: p < 0.01

2. **Linear Path Correlation ρ_linear**
   - Expected: ρ < -0.7 (validation)

### Secondary Metrics

3. **A(w) Range**
   - Min: ~0.32 (DRO endpoint)
   - Max: ~0.72 (ERM endpoint)

4. **WGA Range**
   - Min: ~60% (ERM endpoint)
   - Max: ~80% (DRO endpoint)

---

## 7. Dependencies

### 7.1 Python Packages

**Core:**
- torch >= 1.12.0
- torchvision >= 0.13.0
- numpy >= 1.21.0
- scipy >= 1.7.0

**Data:**
- wilds >= 2.0.0

**Visualization:**
- matplotlib >= 3.5.0
- seaborn >= 0.11.0

**Utilities:**
- PyYAML >= 6.0
- tqdm >= 4.62.0

### 7.2 External Code (Reused from Prior Hypotheses)

- H-M1: `curvature/marchenko_pastur.py` (outlier detection)
- H-M2: `metrics/alignment.py` (A(w) computation)
- H-M2: `data/minority_gradients.py` (gradient extraction)

---

## 8. Testing Strategy

### Unit Tests
- Path sampling correctness (α interpolation)
- A(w) computation (reuse H-M2 tests)
- WGA computation (4-group accuracy)

### Integration Tests
- End-to-end pipeline (checkpoints → correlation)
- Visualization generation

### Validation Checks
- A(w) values within [0, 1]
- WGA values within [0, 1]
- Correlation statistical significance

---

## 9. Implementation Plan

**Phase 3 Output:** This PRD + Architecture + Logic + Config
**Phase 4 Implementation:** 30 tasks (FULL tier)

**Epic Tasks (Architecture):**
1. Path sampling module (FGE + linear)
2. Metrics computation (A(w), WGA)
3. Correlation analysis
4. Visualization generation
5. Validation reporting

**Data Tasks:**
- Task D-1: Verify Waterbirds dataset (auto-download)

**Environment Tasks:**
- Task E-1: Setup dependencies (torch, wilds, scipy)

---

## 10. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| ERM/DRO checkpoints missing from H-E1 | Fallback: Retrain with H-E1 optimal hyperparameters |
| Weak correlation (ρ > -0.3) | Document as PARTIAL (geometry exists but weak coupling) |
| Statistical insignificance (p > 0.01) | Increase M to 50 checkpoints |

---

## 11. Acceptance Criteria

**MUST_WORK (N/A - SHOULD_WORK gate):**
- N/A

**SHOULD_WORK:**
- ✅ FGE path shows ρ(A(w), WGA) < -0.6, p < 0.01
- ✅ Linear path validates coupling (ρ < -0.7)
- ✅ A(w) and WGA values within expected ranges

**PARTIAL:**
- ρ between -0.3 and -0.6 (weak coupling)
- Statistical significance marginal (p < 0.05 but > 0.01)

**FAIL:**
- ρ > -0.3 (no coupling)
- p > 0.05 (not significant)

---

## Appendix A: Reference Implementations

**GitHub Repositories (from Phase 2C):**
1. kohpangwei/group_DRO - Waterbirds, WGA evaluation
2. timgaripov/dnn-mode-connectivity - FGE sampling
3. facebookresearch/loss-landscape - Linear interpolation

**Prior Hypotheses:**
- H-E1: ERM/DRO training, endpoint checkpoints
- H-M1: Marchenko-Pastur outlier detection
- H-M2: Alignment metric A(w)
- H-M3: SGD directional bias validation

---

*PRD v1.0 | Generated for Phase 3 Implementation Planning*
