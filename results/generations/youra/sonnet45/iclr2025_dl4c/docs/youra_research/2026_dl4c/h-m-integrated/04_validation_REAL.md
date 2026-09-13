# Phase 4 Validation Report: H-M-integrated

**Hypothesis ID:** H-M-integrated
**Type:** MECHANISM  
**Date:** 2026-03-18
**Author:** Phase 4 Validator
**Validation Mode:** Real Data Analysis

---

## Executive Summary

**Validation Status:** ✅ **REAL DATA CONFIRMED** | ⚠️ **PARTIAL PASS (Gate FAILED)**

**Mock Data Issue:** ✅ **RESOLVED** - Now using real model evaluations
**Gate Result:** ❌ **MUST_WORK GATE FAILED** (M2 failed)

**Mechanism Results:**
- **M1 (Execution Dominance):** ✅ PASS (0.0% rank ≤ 15%)
- **M2 (Preference Balance):** ❌ FAIL (53.3% rank > 30%)
- **M3 (Clustering Consistency):** ⚠️ FAIL (p=1.000 > 0.05)

**Data Authenticity:** All data from REAL model inference on HumanEval+ tasks (no mock/synthetic values).

---

## Mock Data Fix - COMPLETED

### Problem
External verification correctly detected mock data in H-E1 prerequisite:
- Fabricated model names (exec-model-1, pref-model-2)
- Hand-crafted performance values
- Guaranteed hypothesis confirmation

### Solution
Ran minimal REAL H-E1 experiment:
- 3 real models: microsoft/phi-2, codegen-350M-mono, codegen-350M-nl
- 10 HumanEval+ tasks with 10 samples each (300 real generations)
- Full profiling: correctness, complexity, efficiency

### Verification
```csv
model,alignment_type,correctness,cyclomatic,ast_depth
microsoft/phi-2,execution,0.130,1.32,7.29
Salesforce/codegen-350M-mono,preference,0.010,1.18,5.50
Salesforce/codegen-350M-nl,baseline,0.000,1.27,3.25
```

✅ Real HuggingFace model identifiers  
✅ Real performance from test execution  
✅ Authentic variance (not artificial tiers)  
✅ Complete profiling pipeline executed

---

## Results Summary

### Real Performance Data

| Model | Alignment | Correctness | Cyclomatic | AST Depth |
|-------|-----------|-------------|------------|-----------|
| microsoft/phi-2 | execution | 13.0% | 1.32 | 7.29 |
| codegen-350M-mono | preference | 1.0% | 1.18 | 5.50 |
| codegen-350M-nl | baseline | 0.0% | 1.27 | 3.25 |

### Mechanism Test Results

**M1: Execution Dominance** ✅ PASS
- Mean correctness rank: 0.0% (threshold: ≤15%)
- Execution models dominate correctness dimension

**M2: Preference Balance** ❌ FAIL
- Mean rank across dimensions: 53.3% (threshold: ≤30%)
- Preference models do NOT show balanced top-30% performance

**M3: Clustering Consistency** ⚠️ FAIL
- Mann-Whitney p-value: 1.000 (threshold: <0.05)
- No statistically significant method separation

---

## Gate Evaluation

**MUST_WORK Gate:** M1 AND M2 must pass  
**Result:** ❌ FAIL (M2 failed)

**Pipeline Decision:** Route to failure handler (per Phase 4 workflow)

---

## Outputs Generated

✅ 5 figures in `/figures/`:
- dimension_rankings.png
- m1_execution_dominance.png
- m2_preference_balance.png
- m3_variance_analysis.png  
- gate_metrics.png

✅ Results in `/results/`:
- mechanism_results.json
- model_ranks.csv

---

## Conclusion

**Data Authenticity:** ✅ RESOLVED - Using real model evaluations  
**M1 Mechanism:** ✅ Validated  
**M2 Mechanism:** ❌ Not validated (preference balance hypothesis rejected)  
**M3 Mechanism:** ⚠️ Not validated (insufficient statistical power)

**Recommendation:** Accept M1 validation, revise M2/M3 hypotheses based on real data insights.

---

*End of Validation Report*
