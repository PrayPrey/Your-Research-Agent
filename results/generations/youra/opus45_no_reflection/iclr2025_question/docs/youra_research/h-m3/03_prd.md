# Product Requirements Document: H-M3

**Hypothesis:** Linear probe learns hidden state to correctness mapping with AUROC >= 0.70
**Type:** MECHANISM
**Date:** 2026-08-18
**Phase 2C Source:** 02c_experiment_brief.md

---

## Executive Summary

Validate that a linear probe (logistic regression) can learn to predict answer correctness from middle-layer hidden states extracted at the optimal layer (L15, 50% depth) identified in H-M2. Success demonstrates linear separability of correctness signal in hidden state space.

---

## Problem Statement

Hidden states from transformer middle layers encode correctness-predictive information (validated in H-E1, H-M1, H-M2). This hypothesis tests whether a simple linear classifier can leverage this signal to predict correctness with AUROC >= 0.70.

---

## Functional Requirements

### FR-1: Data Preparation
- **FR-1.1:** Load pre-extracted hidden states from H-M2 (L15, shape: N×4096)
- **FR-1.2:** Load correctness labels from H-M2 (binary: 0=incorrect, 1=correct)
- **FR-1.3:** Apply StandardScaler normalization (mean=0, std=1)
- **FR-1.4:** Maintain train/val split: 9,500 train, 1,700 validation samples

### FR-2: Baseline Model
- **FR-2.1:** Implement random direction baseline
- **FR-2.2:** Generate random unit vector in d_model=4096 dimensional space
- **FR-2.3:** Score samples as dot product: scores = activations @ random_direction
- **FR-2.4:** Expected AUROC ≈ 0.50 ± 0.02

### FR-3: Linear Probe Training
- **FR-3.1:** Implement LinearCorrectnessProbe class using sklearn LogisticRegression
- **FR-3.2:** Configure: C=1e-3, max_iter=2000, class_weight='balanced', solver='lbfgs'
- **FR-3.3:** Train on scaled training hidden states
- **FR-3.4:** Track convergence (solver iterations)

### FR-4: Evaluation
- **FR-4.1:** Compute validation AUROC using sklearn.metrics.roc_auc_score
- **FR-4.2:** Compute accuracy at optimal threshold
- **FR-4.3:** Compare probe AUROC vs random baseline AUROC
- **FR-4.4:** Success gate: AUROC >= 0.70

### FR-5: Mechanism Verification
- **FR-5.1:** Verify probe weights non-trivial (weight_norm > 1e-6)
- **FR-5.2:** Verify predictions not constant (std > 0.01)
- **FR-5.3:** Verify AUROC significantly above random (> 0.55)

### FR-6: Visualization
- **FR-6.1:** Generate gate metrics comparison bar chart (threshold vs achieved)
- **FR-6.2:** Generate ROC curve with AUC annotation
- **FR-6.3:** Save figures to {hypothesis_folder}/figures/

### FR-7: Fallback Protocol (Conditional)
- **FR-7.1:** If linear AUROC < 0.70, test 2-layer MLP variant
- **FR-7.2:** MLP config: hidden_layer_sizes=(256,), max_iter=500, early_stopping=True
- **FR-7.3:** Report MLP AUROC for comparison

---

## Non-Functional Requirements

### NFR-1: Performance
- Training completes in < 60 seconds on CPU
- Inference: < 1ms per sample

### NFR-2: Reproducibility
- Fixed random seed: 42
- All hyperparameters documented

### NFR-3: Dependencies
- sklearn >= 1.0
- numpy
- torch (for loading .pt files)
- matplotlib (for figures)

---

## Success Criteria

| Metric | Threshold | Expected |
|--------|-----------|----------|
| AUROC | >= 0.70 | ~0.85 (based on H-M2 peak) |
| AUROC vs Random | > baseline + 0.20 | 0.35+ delta |
| Probe Convergence | Solver converges | Yes |

---

## Data Specifications

### Input Data
- **Source:** Pre-computed from H-M2
- **Hidden States:** `h-m2/hidden_states_l15.pt` (shape: 11200×4096)
- **Labels:** `h-m2/correctness_labels.pt` (shape: 11200)
- **Train Split:** 9,500 samples
- **Val Split:** 1,700 samples

### Output Artifacts
- `03_prd.md` (this file)
- `03_architecture.md`
- `03_logic.md`
- `03_config.md`
- `04_validation.md` (Phase 4)
- `figures/gate_comparison.png`
- `figures/roc_curve.png`

---

## Dependencies

### Prerequisite Hypotheses
- **H-M2:** Provides optimal layer (L15) and pre-extracted hidden states
- **H-M1:** Validated hook extraction pipeline
- **H-E1:** Validated correctness signal exists in hidden states

### External Dependencies
- sklearn LogisticRegression (L-BFGS solver)
- Pre-computed hidden states from H-M2 folder

---

## References

1. Kossen et al. (2024) - Semantic Entropy Probes
2. Aiersilan (2026) - Hallucination Is Linearly Decodable
3. concept-probes PyPI package
4. OpenInterpretability probes.py

---

*Generated for Phase 3 Implementation Planning*
