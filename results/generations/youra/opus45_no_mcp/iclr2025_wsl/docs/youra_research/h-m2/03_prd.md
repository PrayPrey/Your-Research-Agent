# Product Requirements Document: H-M2

**Hypothesis:** Alignment Preprocessing Benefit
**Date:** 2026-08-19
**Author:** Anonymous
**Type:** MECHANISM
**Base Hypothesis:** H-M1 (Layer-wise Structure Advantage)

---

## 1. Executive Summary

Implement and evaluate Git Re-Basin alignment preprocessing combined with Layer-wise encoding vs Layer-wise encoding alone (H-M1 baseline) for accuracy prediction on CIFAR-10 Model Zoo. This MECHANISM hypothesis tests whether alignment removes permutation-induced variance to reveal functional equivalence and improve correlation.

**Gate Condition:** Δr > 0.05 with p < 0.05 (paired t-test across 5 seeds)
**Gate Type:** SHOULD_WORK (failure documented as limitation, verification continues)

---

## 2. Problem Statement

Neural networks with identical functionality can have different weight configurations due to permutation symmetries. H-M1's Layer-wise encoding achieves r≈0.547 but may be limited by permutation-induced variance. Git Re-Basin alignment preprocesses weights to a canonical form, potentially revealing functional equivalence and improving prediction accuracy.

---

## 3. Goals and Non-Goals

### Goals
- Implement Git Re-Basin weight alignment preprocessing
- Apply alignment to all Model Zoo weights (reference: first model)
- Train accuracy prediction regressor on aligned + Layer-wise encoded weights
- Compare Pearson correlation: Layer-wise+GRB vs Layer-wise alone
- Statistical validation with paired t-test across 5 seeds

### Non-Goals
- Full Git Re-Basin implementation (use simplified weight matching)
- Hungarian algorithm optimization (greedy matching sufficient for PoC)
- Cross-architecture alignment (same CNN family only)
- Hyperparameter tuning beyond H-M1 defaults

---

## 4. Data Specification

### 4.1 Primary Dataset

| Property | Value |
|----------|-------|
| Name | CIFAR-10 Model Zoo (Small) |
| Source | Schurholt et al. 2022 (NeurIPS) |
| DOI | 10.5281/zenodo.6620869 |
| Format | PyTorch .pt file |
| Train | 42,650 models |
| Val | 9,340 models |
| Test | 9,345 models |
| Total | 61,335 models |

### 4.2 Data Loading

Reuse H-M1 data loading infrastructure:
```python
from h_m1.data import load_model_zoo, make_dataloaders
```

### 4.3 Preprocessing Pipeline

1. Load model checkpoints (reuse H-M1)
2. **NEW: Apply Git Re-Basin alignment to reference model (first train sample)**
3. Apply Layer-wise statistics extraction (reuse H-M1)

---

## 5. Functional Requirements

### FR-1: Git Re-Basin Alignment Module
- FR-1.1: Implement `detect_permutable_layers()` to identify conv/fc layers
- FR-1.2: Implement `align_to_reference()` with greedy correlation matching
- FR-1.3: Implement `compute_alignment_batch()` for zoo-wide alignment
- FR-1.4: Track alignment convergence rate (target: >95%)

### FR-2: Data Pipeline Extension
- FR-2.1: Reuse H-M1 data loading (download, split extraction)
- FR-2.2: Add alignment preprocessing step before encoding
- FR-2.3: Cache aligned weights to avoid re-computation

### FR-3: Baseline Model (H-M1 Layer-wise)
- FR-3.1: Import Layer-wise encoder from H-M1
- FR-3.2: Train on raw (unaligned) weights
- FR-3.3: Expected baseline r ≈ 0.547 (from H-M1 validation)

### FR-4: Proposed Model (Layer-wise + GRB)
- FR-4.1: Apply GRB alignment to all model weights
- FR-4.2: Apply Layer-wise encoding to aligned weights
- FR-4.3: Train identical regressor architecture

### FR-5: Training Loop
- FR-5.1: Reuse H-M1 training infrastructure
- FR-5.2: AdamW optimizer, lr=1e-3, weight_decay=1e-4
- FR-5.3: ReduceLROnPlateau, early stopping (patience=10)
- FR-5.4: Max 50 epochs per seed

### FR-6: Evaluation
- FR-6.1: Compute Pearson r on test set for both methods
- FR-6.2: Run 5 seeds (0, 1, 2, 3, 4)
- FR-6.3: Paired t-test: Layer-wise+GRB vs Layer-wise
- FR-6.4: Report Δr = mean(GRB r) - mean(baseline r)
- FR-6.5: Report GRB convergence rate

### FR-7: Visualization
- FR-7.1: Gate metrics bar chart (baseline r vs GRB r with error bars)
- FR-7.2: Scatter plot (predicted vs actual accuracy, both methods)
- FR-7.3: Per-seed comparison line plot
- FR-7.4: Alignment diagnostic histogram (pre/post alignment distances)

### FR-8: Ablations
- FR-8.1: Reference model selection (random, median-accuracy, highest-accuracy)
- FR-8.2: Alignment algorithm (greedy vs Hungarian)
- FR-8.3: Partial alignment (conv only vs all layers)

---

## 6. Non-Functional Requirements

### NFR-1: Performance
- Alignment preprocessing: < 2 hours for full zoo (one-time, cached)
- Training time: < 30 minutes per seed (same as H-M1)

### NFR-2: Reproducibility
- Fixed random seeds
- Deterministic alignment order (sorted model indices)
- Cached aligned weights for reproducibility

### NFR-3: Code Reuse
- Import data loading from H-M1
- Import Layer-wise encoder from H-M1
- Import training loop from H-M1
- Only new code: alignment module

---

## 7. Dependencies

### 7.1 Internal Dependencies (from H-M1)

```
h-m1/code/
├── data.py (reuse: load_model_zoo, make_dataloaders)
├── models.py (reuse: LayerWiseEncoder, AccuracyPredictor, FullModel)
├── train.py (reuse: set_seed, train_model, save_checkpoint)
├── evaluate.py (reuse: predict, compute_pearson, compare_methods, plotting)
└── config.py (extend: add alignment-specific fields)
```

### 7.2 Python Packages

```
torch>=2.0
numpy
scipy
matplotlib
tqdm
```

No new packages required (GRB implemented from scratch using torch).

---

## 8. Success Criteria

| Metric | Threshold | Type |
|--------|-----------|------|
| Δr | > 0.05 | PRIMARY |
| p-value | < 0.05 | PRIMARY |
| GRB convergence | > 95% | SECONDARY |
| Consistent improvement | ≥3/5 seeds | SECONDARY |

**Gate Decision (SHOULD_WORK):**
- PASS: Δr > 0.05 AND p < 0.05
- PARTIAL: Δr > 0 but below threshold → Document as limitation, continue
- FAIL: Δr ≤ 0 → Document limitation, explore alignment variants

---

## 9. Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| GRB convergence issues | Medium | Greedy matching fallback, subset testing |
| No improvement from alignment | Medium | SHOULD_WORK gate allows documented failure |
| Alignment overhead | Low | Pre-compute and cache aligned weights |
| Reference model sensitivity | Low | Ablation study on reference selection |

---

## 10. Timeline

| Phase | Duration |
|-------|----------|
| Alignment module implementation | 1-2 hours |
| Alignment preprocessing (full zoo) | 1-2 hours |
| Training (10 runs: 5 seeds × 2 methods) | 5-10 hours |
| Ablation studies | 2-3 hours |
| Analysis | 1 hour |
| Total | < 1 day |
