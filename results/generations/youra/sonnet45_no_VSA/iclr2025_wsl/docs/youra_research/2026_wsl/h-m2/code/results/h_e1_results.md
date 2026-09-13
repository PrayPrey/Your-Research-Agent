# H-E1 Validation Results: Statistical Features Sufficiency

**Date:** 2026-07-11 18:41:36
**Hypothesis ID:** h-e1
**Status:** PASSED

---

## Summary

**Primary Metric:**
- Validation Accuracy: 88.89%
- Threshold: >80%
- **Decision:** PASSED

**Secondary Metrics:**
- CNN Accuracy: 100.00%
- Hybrid Accuracy: 66.67%
- Transformer Accuracy: 100.00%

**Assumption Validation:**
- A1: TIMM Naming Alignment: FAILED
- A2: Normalization Convention: PASSED
- A3: Scale Invariance: PASSED

---

## Confusion Matrix

|               | Pred: CNN | Pred: Transformer | Pred: Hybrid |
|---------------|-----------|-------------------|--------------||
| True: CNN          |         6 |         1 |         0 |
| True: Transformer  |         0 |         4 |         0 |
| True: Hybrid       |         0 |         1 |         6 |

![Confusion Matrix](confusion_matrix.png)

---

## Feature Importance

| Feature          | Avg Abs Coefficient | Rank |
|------------------|---------------------|------|
| param_mass_ratio |              0.7770 |    1 |
| no_norm_flag     |              0.4561 |    2 |
| bn_count         |              0.3529 |    3 |
| ln_count         |              0.1714 |    4 |
| gn_count         |              0.0000 |    5 |

![Feature Importance](feature_importance.png)

---

## Failure Cases

**Misclassified Models:** 2 / 18

| Model Name | True Label | Predicted Label |
|------------|------------|-----------------||
| vgg16                                    | CNN        | Hybrid          |
| poolformer_m36                           | Transformer | Hybrid          |

---

## Assumption Validation Details

**A1: TIMM Naming Alignment:**
- alignment_rate: 0.4000
- threshold: 0.9000
- sample_size: 10

**A2: Normalization Convention:**
- cnn_ln_violation_rate: 0.0000
- trans_bn_violation_rate: 0.1333
- threshold: 0.1500

**A3: Scale Invariance:**
- cv: 0.0000
- threshold: 0.1500
- family_models: ['resnet18', 'resnet34', 'resnet50', 'resnet101', 'resnet152']
- ratios: [1.0, 1.0, 1.0, 1.0, 1.0]

---

## Next Steps

- Proceed to H-M1: Normalization Layer Fingerprinting
- Update verification_state.yaml: h-e1.validation.status = COMPLETED
- Begin mechanism hypothesis validation
