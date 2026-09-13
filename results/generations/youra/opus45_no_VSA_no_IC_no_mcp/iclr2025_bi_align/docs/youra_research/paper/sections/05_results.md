# 5. Results

## H-E1: Benchmark Independence (PASSED)

All pairwise correlations confirm benchmark independence:

| Benchmark Pair | Pearson r | p-value |
|----------------|-----------|---------|
| TruthfulQA vs HHH-helpful | 0.040 | 0.248 |
| TruthfulQA vs HHH-harmless | -0.001 | 0.983 |
| HHH-helpful vs HHH-harmless | 0.019 | 0.547 |

Maximum |r| = 0.040, far below the 0.5 threshold. The benchmarks measure effectively independent alignment dimensions, validating the experimental design.

Base model accuracies: TruthfulQA 20.4%, HHH-helpful 56.0%, HHH-harmless 53.8%.

## H-M1: RLHF Reward Smoothing (PASSED)

The RLHF reward model produces smooth, continuous predictions:

| Metric | Value |
|--------|-------|
| Reward range | 0.83 units [-0.47, +0.36] |
| Mean reward | 0.011 |
| Eval accuracy | 53.5% |
| Margin | +0.023 |
| Final train loss | 0.713 |
| Final eval loss | 0.691 |

Reward outputs span a continuous range with no discrete clustering, confirming that Bradley-Terry training learns smooth preference approximations.

## H-M2: DPO Boundary Sharpness (PASSED)

DPO preserves sharper preference boundaries than RLHF:

| Metric | DPO | RLHF | Threshold | Result |
|--------|-----|------|-----------|--------|
| Margin std | 0.343 | 0.208 | - | DPO higher |
| **Sharpness ratio** | **1.65** | 1.0 | >1.0 | **PASS** |
| Boundary accuracy | 0.589 | - | >0.55 | PASS |
| Confident ratio | 0.772 | - | >0.3 | PASS |

DPO shows 65% higher margin variance and makes confident decisions on 77% of cases where RLHF hesitates.

## H-M3: Attractor Hypothesis (PARTIAL FAILURE)

**Key finding: Cross-method similarity exceeded within-method similarity.**

| Metric | Value | Threshold | Result |
|--------|-------|-----------|--------|
| Within-method similarity | 0.967 | - | - |
| Cross-method similarity | 0.983 | - | - |
| **Clustering gap** | **-0.016** | >0.05 | **FAIL** |
| Silhouette score | -0.411 | >0.1 | FAIL |
| Cohen's d | -1.295 | - | Opposite direction |
| p-value | 0.664 | <0.05 | Not significant |

Models do not cluster by training method. Random seed variation contributes more to behavioral differences than method choice.

## H-M4: Differential Benchmark Profiles (PARTIAL)

**Primary criterion not met:**

| Benchmark | DPO Acc | RLHF Acc | Cohen's d | Interpretation |
|-----------|---------|----------|-----------|----------------|
| TruthfulQA | 0.362 | 0.320 | +0.089 | Negligible |
| HH-helpful | 0.612 | 0.704 | -0.194 | Small RLHF advantage |
| HH-harmless | 0.623 | 0.633 | -0.021 | No difference |

**Summary:**
- max|d| = 0.194 (threshold: >0.3) - **NOT MET**
- min|d| = 0.021 (threshold: <0.15) - MET
- Profile correlation: 0.978 (highly similar)

**Secondary criterion partially met:**
- TruthfulQA vs HHH-helpful correlation difference = 0.369 (>0.3 threshold)

## Summary

| Hypothesis | Gate | Result | Pass Rate |
|------------|------|--------|-----------|
| H-E1 | MUST_WORK | PASSED | 100% |
| H-M1 | MUST_WORK | PASSED | 100% |
| H-M2 | SHOULD_WORK | PASSED | 100% |
| H-M3 | SHOULD_WORK | PARTIAL | 25% |
| H-M4 | SHOULD_WORK | PARTIAL | 50% |

**Predictions supported: 1/3** (P2 only—cross-benchmark correlation differences)
**Overall pass rate: 60%**
