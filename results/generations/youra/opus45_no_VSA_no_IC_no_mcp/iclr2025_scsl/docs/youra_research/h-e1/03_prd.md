# Product Requirements Document: H-E1

**Hypothesis:** Spurious features dominate earlier than core features in ERM training (GradCAM attribution ratio > 1 before epoch 10)

**Type:** EXISTENCE (PoC)
**Date:** 2026-08-28
**Phase 2C Source:** 02c_experiment_brief.md

---

## 1. Executive Summary

This experiment validates the foundational assumption that ERM-trained models learn spurious features (background) before core features (bird) on the Waterbirds dataset. Success demonstrates that spurious dominance occurs early in training, justifying subsequent intervention hypotheses.

**Key Deliverable:** Epoch-wise GradCAM attribution tracking showing spurious/core ratio > 1.0 before epoch 10.

---

## 2. Problem Statement

### 2.1 Background
Deep learning models trained with ERM exhibit simplicity bias—learning spurious correlations that are easier to fit before task-relevant features. This phenomenon underlies poor worst-group generalization.

### 2.2 Hypothesis Being Tested
Spurious feature attribution (background regions) exceeds core feature attribution (bird regions) within the first 10 training epochs.

### 2.3 Success Criteria
- **Primary:** Spurious/Core attribution ratio > 1.0 before epoch 10
- **Secondary:** Clear temporal pattern of early spurious dominance

---

## 3. Functional Requirements

### FR-1: Dataset Loading
- **Dataset:** Waterbirds v1.0
- **Source:** kohpangwei/group_DRO or WILDS
- **Splits:** Train (4,795), Test (5,794)
- **Preprocessing:** Resize 224×224, ImageNet normalization
- **Ground-truth masks:** Spurious (background) and core (bird) region masks required

### FR-2: Model Training
- **Architecture:** ResNet-50 with ImageNet pretrained weights
- **Final layer:** Linear(2048, 2) for binary classification
- **Optimizer:** SGD (momentum=0.9, weight_decay=1e-4)
- **Learning rate:** 0.01 with StepLR (step=20, gamma=0.1)
- **Batch size:** 128
- **Epochs:** 50
- **Loss:** CrossEntropyLoss
- **Seed:** 42 (single seed for PoC)

### FR-3: Attribution Tracking
- **Method:** GradCAM on layer4[-1]
- **Library:** pytorch-grad-cam
- **Measurement:** Per-epoch spurious/core attribution ratio
- **Computation:**
  ```
  spurious_attr = sum(cam * spurious_mask)
  core_attr = sum(cam * core_mask) + 1e-8
  ratio = spurious_attr / core_attr
  ```

### FR-4: Evaluation Metrics
- **Primary metric:** Spurious/Core Attribution Ratio (per epoch)
- **Derived metric:** Dominance Epoch (first epoch where ratio > 1.0)
- **Tracking:** Log ratio after each epoch on validation subset

### FR-5: Visualization
- **Required:** Gate metrics comparison bar chart
- **Additional:** Attribution ratio over epochs line plot
- **Output directory:** h-e1/figures/

---

## 4. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed (42) for all random operations
- Deterministic PyTorch settings where possible

### NFR-2: Performance
- Single GPU training (< 2 hours on standard hardware)
- Attribution computation on subset (500+ samples) for efficiency

### NFR-3: Logging
- Epoch-wise metrics saved to CSV/JSON
- Model checkpoints at key epochs (optional)

---

## 5. Data Requirements

| Item | Specification |
|------|---------------|
| Dataset | Waterbirds v1.0 |
| Train samples | 4,795 |
| Test samples | 5,794 |
| Classes | 2 (landbird, waterbird) |
| Groups | 4 (bird × background) |
| Masks | Segmentation masks for bird/background |

---

## 6. Dependencies

### External Libraries
- torch, torchvision
- pytorch-grad-cam
- numpy, matplotlib
- wilds or kohpangwei/group_DRO dataset loader

### Phase 2C Artifacts
- 02c_experiment_brief.md (experiment specification)

---

## 7. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Dominance Epoch | < 10 | First epoch with ratio > 1.0 |
| Attribution Ratio | > 1.0 | Mean ratio at dominance epoch |
| Code Execution | No errors | Training completes successfully |

---

## 8. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Mask unavailability | Use WILDS which includes segmentation |
| Noisy GradCAM | Average over 500+ samples |
| Slow attribution | Compute on subset, not full dataset |

---

## 9. Out of Scope

- Multiple seeds (PoC uses single seed)
- Alternative attribution methods (Integrated Gradients)
- Intervention mechanisms (future hypotheses)
- Worst-group accuracy optimization

---

*Generated for Phase 3 Implementation Planning*
