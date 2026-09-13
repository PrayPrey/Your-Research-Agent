# Product Requirements Document: h-e1

**Date:** 2026-08-24
**Hypothesis:** Attribution methods (TRAK, TracIn, Kronfluence) compute influence via mathematically distinct operations
**Type:** EXISTENCE (PoC)
**Gate:** MUST_WORK

---

## 1. Objective

Verify that TRAK, TracIn, and Kronfluence compute training data influence using mathematically distinct operations by computing influence scores on identical model/data and measuring inter-method correlation.

## 2. Success Criteria

| Criterion | Threshold | Metric |
|-----------|-----------|--------|
| All methods run | 0 errors | Execution success |
| Valid outputs | No NaN/Inf | Score validation |
| Mathematical distinctness | r < 0.9 | Pearson correlation between method pairs |

## 3. Scope

### In Scope
- Install and run TRAK (MadryLab/trak)
- Install and run TracIn (pytorch/captum)
- Install and run Kronfluence (pomonam/kronfluence)
- Train or load ResNet model on CIFAR-10
- Compute pairwise influence scores for test samples
- Measure inter-method correlations
- Generate comparison figures

### Out of Scope
- Hyperparameter optimization
- Multiple seeds
- Downstream application evaluation
- Method modification

## 4. Technical Requirements

### 4.1 Dependencies
- Python 3.9+
- PyTorch 2.1+
- traker (TRAK)
- captum (TracIn)
- kronfluence
- torchvision
- scipy, numpy, matplotlib

### 4.2 Hardware
- GPU recommended (CUDA)
- RAM: 16GB minimum
- Storage: 5GB for model/data

### 4.3 Data
- CIFAR-10: 50,000 train, 10,000 test
- Standard torchvision loading

### 4.4 Model
- ResNet-9 or ResNet-18 adapted for CIFAR-10
- Pretrained or trained from scratch (200 epochs)

## 5. Deliverables

| Deliverable | Format | Location |
|-------------|--------|----------|
| Experiment code | Python | h-e1/code/ |
| Influence scores | .pt files | h-e1/outputs/ |
| Correlation results | JSON | h-e1/outputs/correlations.json |
| Figures | PNG | h-e1/figures/ |
| Validation report | Markdown | h-e1/04_validation.md |

## 6. Acceptance Criteria

- [ ] All three methods execute without error
- [ ] Influence scores computed for ≥1000 test samples against full training set
- [ ] All pairwise correlations < 0.9
- [ ] Correlation heatmap generated
- [ ] Results documented in validation report

---

*Phase 3 PRD - Ready for architecture/logic/config generation*
