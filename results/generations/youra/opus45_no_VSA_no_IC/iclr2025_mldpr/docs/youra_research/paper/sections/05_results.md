# Results

## H-E1: Fingerprint Detection

### Main Result

The linear probe achieves **99.51% accuracy** distinguishing between Flowers102 and CIFAR-100 fine-tuned models, far exceeding our 60% threshold.

| Metric | Value | 95% CI |
|--------|-------|--------|
| Test Accuracy | 99.51% | [99.38%, 99.65%] |
| Cohen's d | 698.08 | — |
| p-value | < 1e-10 | — |

The effect size (Cohen's d = 698) indicates that benchmark fingerprints are not subtle artifacts but dominant signals in representation space. For context, typical psychology studies report d < 1.

### Confusion Matrix

|  | Pred: Flowers | Pred: CIFAR-100 |
|--|---------------|-----------------|
| **Flowers** | 4,951 | 49 |
| **CIFAR-100** | 0 | 5,000 |

The asymmetric confusion reveals interesting structure: CIFAR-100 representations are never misclassified as Flowers, suggesting CIFAR-100 fine-tuning creates more distinctive fingerprints. Only 49/5,000 Flowers samples were confused.

### Baseline Validation

| Baseline | Accuracy |
|----------|----------|
| Shuffled labels | 50.43% |
| Main probe | 99.51% |

The shuffled baseline confirms that the probe relies on benchmark-specific features rather than model artifacts.

**Verdict: H-E1 PASS.** Benchmark fingerprints exist and are massively detectable.

---

## H-M1: BFS-Gap Correlation

### Model-Level Results

| Model | BFS | In-Domain | Transfer | Gap |
|-------|-----|-----------|----------|-----|
| cifar100_s0 | 0.9998 | 83.0% | 38.7% | 44.3 pp |
| cifar100_s1 | 0.9999 | 73.2% | 36.6% | 36.6 pp |
| cifar100_s2 | 1.0000 | 83.6% | 40.9% | 42.7 pp |
| flowers_s0 | 0.9998 | 89.4% | 56.0% | 33.5 pp |
| flowers_s1 | 0.9999 | 89.5% | 53.0% | 36.5 pp |
| flowers_s2 | 0.9998 | 90.2% | 54.6% | 35.7 pp |

### Correlation Analysis

- **Pearson r:** 0.022
- **p-value:** 0.967

No statistically significant correlation exists between BFS and cross-dataset gap. The scatter plot (Figure 2) shows a flat relationship.

### Interpretation

All models achieved BFS > 0.999, creating a ceiling effect that eliminates variance for correlation analysis. The classifier is so confident about benchmark identity that no meaningful BFS differences exist across models.

**Verdict: H-M1 FAIL.** BFS does not correlate with generalization gap. The proposed mechanism is not supported.

---

## H-M2: Training Regime Comparison

### Status: INCONCLUSIVE

The codebase was fully implemented (9 modules) and verified to execute end-to-end. However, the experiment ran with synthetic data (random images) rather than real fine-grained datasets.

Mock results show near-chance accuracy (~1%), as expected with random inputs. Statistical conclusions cannot be drawn without real data execution.

**Verdict: H-M2 INCONCLUSIVE.** Requires CUB-200, Stanford Dogs, Stanford Cars, FGVC Aircraft, and NABirds datasets.

---

## Summary

| Hypothesis | Type | Gate | Result |
|------------|------|------|--------|
| H-E1 | Existence | MUST_WORK | **PASS** (99.51% acc, d=698) |
| H-M1 | Mechanism | SHOULD_WORK | **FAIL** (r=0.022, p=0.967) |
| H-M2 | Mechanism | SHOULD_WORK | **INCONCLUSIVE** |

The existence of benchmark fingerprints is strongly confirmed. The proposed BFS-gap correlation mechanism is not supported. The single vs. multi-benchmark comparison remains untested.
