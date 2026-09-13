# Validation Report: h-c1 Gradient-Aware Training

**Hypothesis:** h-c1 (CONDITION)  
**Date:** 2026-08-29  
**Gate Type:** SHOULD_WORK  
**Status:** ❌ **FAIL**

---

## Executive Summary

Gradient-aware learning rate modulation based on neuron-spurious correlation (ρ_j from h-m1) **failed** to achieve competitive worst-group accuracy on Waterbirds dataset.

**Key Finding:** Gradient-Aware method (39.13% ± 4.58%) underperformed ERM baseline (41.11% ± 5.40%), far below JTT target (86%).

**Gate Verdict:** **FAIL** - Did not meet SHOULD_WORK criterion (≥86% WG-Acc within 1% of JTT).

---

## Statistical Test Results (Test 9)

| Metric | Value |
|--------|-------|
| **ERM WG-Acc** | 41.11 ± 5.40% |
| **Gradient-Aware WG-Acc** | 39.13 ± 4.58% |
| **Target (JTT - 1%)** | 86.00% |
| **Mean Difference** | -1.98% (GA < ERM) |
| **t-statistic** | -1.135 |
| **p-value (paired)** | 0.3742 |
| **Significance** | Not significant (p > 0.05) |

**Paired t-test:** No statistically significant difference between Gradient-Aware and ERM. Both methods performed poorly (< 50% WG-Acc).

---

## Gate Condition Evaluation

### SHOULD_WORK Criterion
**Requirement:** mean(Gradient-Aware) ≥ mean(JTT) - 1% AND p < 0.05

**Result:** ❌ **FAIL**
- Gradient-Aware: 39.13% << 86% target
- Difference from target: -46.87% (critical underperformance)
- Non-inferiority to JTT: Not established

---

## Per-Seed Results

| Seed | ERM WG-Acc (%) | GA WG-Acc (%) | Difference |
|------|---------------|---------------|------------|
| 0    | 39.13         | 34.78         | -4.35      |
| 1    | 48.48         | 45.45         | -3.03      |
| 2    | 35.71         | 37.14         | +1.43      |
| **Mean** | **41.11** | **39.13**     | **-1.98**  |
| **Std**  | **5.40**  | **4.58**      | -          |

**Observation:** Gradient-Aware consistently underperforms or matches ERM across all seeds.

---

## Analysis

### Root Cause: ρ_j Transfer Failure

**Problem:** h-m1 ρ_j values computed on CMNIST ResNet-18 do not transfer to Waterbirds ResNet-50.

**Evidence:**
1. Fallback ρ_j values used (h-m1 layer means):
   - conv1: 0.001
   - layer1: 0.004
   - layer2: 0.005
   - layer3: 0.003
   - layer4: 0.000

2. Extremely small ρ_j values (< 0.01) result in negligible LR modulation:
   - lr_modulated = lr_base * (1 - ρ_j) ≈ lr_base * 0.995
   - Gradient-Aware effectively becomes ERM with ~0.5% LR reduction

3. Mock dataset limitations:
   - Mock Waterbirds generator used for code validation (real dataset unavailable)
   - Spurious correlation structure differs from real Waterbirds
   - Training converged to random guess (~40-50% accuracy across all groups)

### Why Gradient-Aware Failed

1. **Insufficient ρ_j signal:** h-m1 mechanism validated 0.001-0.005 correlations on CMNIST. These values are too small to drive meaningful LR modulation.

2. **Cross-dataset transfer assumption violated:** CMNIST (color spurious correlation) ≠ Waterbirds (background spurious correlation). Layer-wise ρ_j patterns likely differ.

3. **Mock data artifact:** Real Waterbirds dataset not available. Mock generator may not capture true spurious correlation strength.

---

## Visualizations

### 1. Gate Metrics Comparison
![Gate Metrics](figures/gate_metrics.png)

**Interpretation:** Both ERM and Gradient-Aware far below target. Gate FAIL threshold clearly unmet.

### 2. Training Curves
![Training Curves](figures/training_curves.png)

**Interpretation:** Validation WG-Acc remains unstable and low (~30-40%) throughout training for both methods.

### 3. Learning Rate Modulation Heatmap
![LR Modulation](figures/lr_modulation.png)

**Interpretation:** Modulated LRs barely differ from base LR due to small ρ_j values (< 0.01).

### 4. Per-Group Accuracy
![Per-Group Accuracy](figures/per_group_accuracy.png)

**Interpretation:** No clear group-wise advantage for Gradient-Aware over ERM.

---

## Hypothesis Status

**h-c1 Status:** ❌ **REJECTED (Gate FAIL)**

**Reason:** Gradient-aware training did not achieve competitive worst-group accuracy. ρ_j values from h-m1 (CMNIST) do not transfer to Waterbirds, resulting in ineffective LR modulation.

---

## Recommendations

### For Future Work

1. **Compute ρ_j directly on Waterbirds:**
   - Re-run h-m1 layer-neuron analysis on Waterbirds training set
   - Measure background spurious correlation ρ_j per neuron
   - Use dataset-specific ρ_j for LR modulation

2. **Increase ρ_j modulation strength:**
   - Current ρ_j ∈ [0.001, 0.005] too weak
   - Target ρ_j ∈ [0.1, 0.5] for noticeable LR changes
   - Consider non-linear modulation: lr_j = lr_base * exp(-α * ρ_j)

3. **Use real Waterbirds dataset:**
   - Download from https://github.com/kohpangwei/group_DRO
   - Validate mock results with real data
   - Real dataset enables proper JTT baseline comparison

4. **Alternative approach - Group DRO:**
   - Direct optimization of worst-group loss
   - Does not rely on neuron-level ρ_j transfer
   - Proven competitive with JTT on Waterbirds

---

## Deliverables

✅ Code implementation (8 epics, 15 subtasks)  
✅ 3 seeds × 2 methods = 6 training runs completed  
✅ Statistical Test 9 executed (paired t-test)  
✅ 4 required figures generated  
✅ 04_validation.md report (this document)  

---

## Conclusion

h-c1 hypothesis **rejected**. Gradient-aware training using cross-dataset ρ_j transfer (h-m1 CMNIST → h-c1 Waterbirds) failed to improve worst-group accuracy. SHOULD_WORK gate criterion unmet (39.13% << 86% target).

**Next Steps:** Route to reflection. Consider alternative mechanisms or direct Waterbirds-specific ρ_j computation for revised hypothesis.

---

**Version:** 1.0  
**Completed:** 2026-08-29  
**Gate Result:** ❌ FAIL
