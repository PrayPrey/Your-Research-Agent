# Product Requirements Document: H-M2

**Date:** 2026-08-09
**Hypothesis:** Update-norm parity intervention attenuates SR divergence (SR ≤ 1.1 vs baseline SR > 1.2)
**Type:** MECHANISM
**Phase 2C Source:** 02c_experiment_brief.md

---

## Executive Summary

Implement and validate update-norm parity intervention that equalizes gradient update norms across majority/minority groups during training. The intervention should prevent Sharpness Ratio (SR) divergence, keeping SR ≤ 1.1 compared to baseline ERM where SR > 1.2.

---

## Problem Statement

Standard ERM training on datasets with spurious correlations (like Waterbirds) leads to differential sharpness between majority and minority groups. H-E1 established SR ≈ 1.0 at initialization. This experiment tests whether enforcing update-norm parity during training can prevent SR divergence.

---

## Functional Requirements

### FR-1: Data Pipeline
- **FR-1.1:** Load Waterbirds dataset from kohpangwei/group_DRO repository
- **FR-1.2:** Implement 4-group data loader (landbird/waterbird × land/water background)
- **FR-1.3:** Apply ImageNet normalization and standard augmentation (RandomResizedCrop, RandomHorizontalFlip)
- **FR-1.4:** Support group-aware batch sampling for per-group gradient computation

### FR-2: Baseline Model (ERM)
- **FR-2.1:** ResNet-50 pretrained on ImageNet
- **FR-2.2:** Replace final FC layer: Linear(2048, 2) for binary classification
- **FR-2.3:** SGD optimizer (lr=0.001, momentum=0.9, weight_decay=0.0001)
- **FR-2.4:** CrossEntropyLoss
- **FR-2.5:** 100 epochs with early stopping on worst-group validation accuracy

### FR-3: Proposed Model (Update-Norm Parity)
- **FR-3.1:** Same architecture as baseline (ResNet-50)
- **FR-3.2:** Insert parity intervention between loss.backward() and optimizer.step()
- **FR-3.3:** Compute per-group gradient norms
- **FR-3.4:** Scale gradients to equalize update norms across groups
- **FR-3.5:** Log parity metrics per epoch

### FR-4: Ablation Variants
- **FR-4.1:** Baseline (no intervention) - control
- **FR-4.2:** Full Parity (100% scaling toward equal norms)
- **FR-4.3:** Partial Parity (50% scaling toward equal norms)

### FR-5: Evaluation Metrics
- **FR-5.1:** Sharpness Ratio (SR) - Hessian trace ratio minority/majority
- **FR-5.2:** Worst-Group Accuracy (WGA) - min accuracy across 4 groups
- **FR-5.3:** Per-group accuracy tracking
- **FR-5.4:** Update norm distribution per group

### FR-6: Visualization
- **FR-6.1:** SR trajectory comparison (baseline vs parity) over epochs
- **FR-6.2:** Per-group accuracy trajectories
- **FR-6.3:** Update norm distribution boxplots
- **FR-6.4:** Final WGA comparison bar chart

### FR-7: Statistical Validation
- **FR-7.1:** Run 5 seeds per condition
- **FR-7.2:** Report mean ± std for all metrics
- **FR-7.3:** Statistical significance test for SR difference

---

## Non-Functional Requirements

### NFR-1: Performance
- Training should complete within 4 hours per seed on single GPU
- SR computation should add < 10% overhead

### NFR-2: Reproducibility
- Fixed random seeds
- Deterministic operations where possible
- Config files for all hyperparameters

### NFR-3: Logging
- TensorBoard or WandB integration
- Per-epoch metric logging
- Parity intervention activation logs

---

## Success Criteria

| Metric | Baseline (ERM) | Proposed (Parity) | Threshold |
|--------|----------------|-------------------|-----------|
| SR @ epoch 50 | > 1.2 | ≤ 1.1 | PASS if proposed < baseline |
| WGA | ~21% | ≥ 21% | No regression |
| Statistical | - | p < 0.05 | SR difference significant |

---

## Dependencies

- PyTorch >= 1.10
- torchvision (ResNet-50 pretrained)
- kohpangwei/group_DRO (dataset + baseline)
- numpy, scipy (statistics)
- matplotlib (visualization)

---

## Constraints

- Must use Waterbirds dataset (standard benchmark)
- Must use ResNet-50 architecture (consistency with prior work)
- Must follow kohpangwei/group_DRO evaluation protocol

---

## Out of Scope

- Other datasets (CelebA, MultiNLI) - future work
- Other architectures - future work
- Group DRO comparison - separate hypothesis
