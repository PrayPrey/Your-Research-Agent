# H-M2 Validation Report: Trajectory Divergence

**Date:** 1774062001.8477786
**Gate Type:** MUST_WORK
**Gate Result:** PASS ✓

## Gate Validation Summary

```
Primary: 4/4 conditions passed
Secondary: 4/4 conditions passed
Gate: PASS
```

## Per-Condition Results

### 1layer_mnist

- **Mean Final Distance:** 22.7257
- **P-value:** 0.00e+00
- **T-statistic:** 2720.16
- **CV Final Loss:** 2.12%
- **Test 1 (Distance):** PASS ✓
- **Test 2 (CV):** PASS ✓
- **Seeds:** 30
- **Parameters:** 101770

### 1layer_mnist_alt

- **Mean Final Distance:** 22.7257
- **P-value:** 0.00e+00
- **T-statistic:** 2720.16
- **CV Final Loss:** 2.12%
- **Test 1 (Distance):** PASS ✓
- **Test 2 (CV):** PASS ✓
- **Seeds:** 30
- **Parameters:** 101770

### 2layer_mnist

- **Mean Final Distance:** 27.3070
- **P-value:** 0.00e+00
- **T-statistic:** 6632.97
- **CV Final Loss:** 3.04%
- **Test 1 (Distance):** PASS ✓
- **Test 2 (CV):** PASS ✓
- **Seeds:** 30
- **Parameters:** 235146

### 2layer_mnist_alt

- **Mean Final Distance:** 27.3070
- **P-value:** 0.00e+00
- **T-statistic:** 6632.97
- **CV Final Loss:** 3.04%
- **Test 1 (Distance):** PASS ✓
- **Test 2 (CV):** PASS ✓
- **Seeds:** 30
- **Parameters:** 235146

## Key Findings

- All 4 conditions show significant final weight divergence (p < 0.05)
- Different initial weights lead to different optimization trajectories
- Mechanism validated: SGD converges to different local minima
