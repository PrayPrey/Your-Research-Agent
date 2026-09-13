# Results

## 5.1 H-E1: Behavioral Variance Exists

**Main Finding.** The residual variance ratio is **0.6758**, indicating that 67.6% of class-wise accuracy variance is *not* explained by overall accuracy and per-class difficulty. This exceeds our 0.05 threshold by a factor of 13.5×.

**Interpretation.** Models with identical overall accuracy exhibit substantially different class-wise performance patterns. Behavioral fingerprints—distinct per-class accuracy signatures—exist in the Small CNN Zoo.

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Residual Ratio | 0.6758 | > 0.05 | **PASS** |
| Baseline R² | 0.32 | — | — |
| Factor Above Threshold | 13.5× | — | — |

### Per-Class Variance Analysis

Class-wise residual variance reveals where behavioral differentiation is strongest:

| Class | Name | Residual Variance (σ²) | Rank |
|-------|------|------------------------|------|
| 1 | Automobile | 0.163 | 1 (highest) |
| 9 | Truck | 0.127 | 2 |
| 3 | Cat | 0.007 | 10 (lowest) |

**Pattern.** Vehicle classes (automobile, truck) show the highest behavioral variance. Models specialize differently on these semantically related categories despite similar overall accuracy. This aligns with CIFAR-10 confusion patterns where automobile/truck are commonly confused—models develop different strategies for distinguishing them.

## 5.2 H-M1: Weight Statistics Fail to Capture Behavioral Variance

**Main Finding.** Weight statistics achieve mean R² = **-0.08** compared to stratified baseline R² = **0.12**. ΔR² = **-0.20**, indicating weight features perform *worse* than simply knowing overall accuracy.

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Weight Feature R² | -0.08 | — | — |
| Baseline R² | 0.12 | — | — |
| ΔR² | -0.20 | > 0 | **FAIL** |

**Interpretation.** The mechanism hypothesis is refuted under current experimental conditions. Simple per-layer weight statistics (25 features) do not extract behavioral variance from weights.

### Per-Class R² Analysis

| Class | Name | Weight R² | Baseline R² | ΔR² |
|-------|------|-----------|-------------|-----|
| 0 | Airplane | 0.15 | 0.12 | +0.03 |
| 1 | Automobile | 0.21 | 0.08 | +0.13 |
| 4 | Deer | **-2.74** | 0.05 | -2.79 |
| 7 | Horse | 0.18 | 0.15 | +0.03 |

**Class 4 Anomaly.** Deer class shows extreme negative R² (-2.74), far worse than random prediction. This drives the overall negative result. Possible explanations:
1. **Overfitting:** With 39 test models and 25 features, Ridge may overfit to training patterns that anti-correlate with test performance on this class.
2. **Small sample artifact:** Class 4 may have unusual variance patterns in our 193-model subset.
3. **Feature-target misalignment:** Weight statistics may anti-correlate with deer-specific behavior.

Several classes (automobile, airplane, horse) show positive ΔR², suggesting weight features capture *some* signal for certain classes. The failure is not uniform.

## 5.3 Summary

| Hypothesis | Claim | Result | Evidence |
|------------|-------|--------|----------|
| H-E1 | Behavioral variance exists | **VALIDATED** | Residual ratio = 0.68 (13.5× threshold) |
| H-M1 | Weight statistics extract it | **REFUTED** | ΔR² = -0.20 (negative) |

The existence of behavioral fingerprints is established. The extraction mechanism via simple weight statistics fails. This negative result motivates learned representations and larger-scale validation.
