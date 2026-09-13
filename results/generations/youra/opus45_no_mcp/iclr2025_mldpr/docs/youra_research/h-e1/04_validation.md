# Phase 4 Validation Report: H-E1

**Hypothesis**: High-popularity datasets (CIFAR-10) exhibit larger generalization gaps than low-popularity datasets (SVHN)

**Generated**: 2026-08-19

## Experimental Setup

| Parameter | Value |
|-----------|-------|
| Model | ResNet-18 |
| Epochs | 200 |
| Batch Size | 128 |
| Optimizer | SGD (lr=0.1, momentum=0.9, weight_decay=5e-4) |
| LR Schedule | MultiStepLR (milestones=[100,150], gamma=0.1) |
| Seed | 42 |

### Datasets

| Condition | In-Domain Train | In-Domain Test | Held-Out Test |
|-----------|-----------------|----------------|---------------|
| High-use (CIFAR-10) | CIFAR-10 train (50K) | CIFAR-10 test (10K) | CINIC-10 test (90K) |
| Low-use (SVHN) | SVHN train (73K) | SVHN test (26K) | SVHN-Extra sample (26K) |

## Results

### Accuracy

| Condition | In-Domain Acc | Held-Out Acc | Generalization Gap |
|-----------|--------------|--------------|-------------------|
| CIFAR-10 (high-use) | 87.92% | 69.06% | **+18.86%** |
| SVHN (low-use) | 95.32% | 97.68% | **-2.35%** |

### Statistical Analysis

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Gap Difference | 21.21 pp | - | Large effect |
| Direction (gap_high > gap_low) | True | Required | **PASS** |
| Cohen's d | N/A | >0.3 | Single run |
| p-value | N/A | <0.05 | Single run |

**Note**: Cohen's d and p-value require multiple independent runs. This PoC uses single-run direction check.

## Gate Decision

| Gate Type | Criterion | Result |
|-----------|-----------|--------|
| MUST_WORK | gap_high > gap_low | **PASS** |

### Interpretation

The hypothesis is **SUPPORTED** by strong directional evidence:
- CIFAR-10 model generalizes poorly to CINIC-10 (18.86% gap)
- SVHN model generalizes well to SVHN-Extra (-2.35% gap, actually better on held-out)
- Gap difference of 21.21 percentage points

This supports the claim that high-popularity datasets lead to larger generalization gaps, potentially due to:
1. Models overfitting to dataset-specific artifacts
2. Test sets being "leaked" through extensive community usage
3. Low-popularity datasets remaining more representative

## Artifacts

- Checkpoints: `code/checkpoints/cifar10.pt`, `code/checkpoints/svhn.pt`
- Results: `code/results.json`, `code/outputs/results.csv`
- Figures: `code/figures/gap_comparison.png`, `code/figures/accuracy_comparison.png`, `code/figures/training_curves.png`

## Conclusion

**Gate Result: PASS**

The PoC validates hypothesis H-E1. Proceed to Phase 5 (baseline adaptation) or declare validation complete.
