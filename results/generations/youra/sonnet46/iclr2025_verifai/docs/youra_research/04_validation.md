# h-e1_v4 Validation Report

**Hypothesis:** H-E1_v4 — Passing Cluster Dominance (PCD) Null Exceedance Test
**Gate Type:** MUST_WORK
**Gate Criterion:** exceedance_fraction >= 0.5 for >= 3/5 model-benchmark pairs
**Generated:** 2026-03-19T16:52:46.125642

## Gate Result: FAIL

**Overall Pass:** False
**n_pairs_passing:** 0/5 (threshold: 3)

### Per-Pair Gate Results

| Pair | N_mid_θ | Exceedance | CI 95% | Pass |
|------|---------|-----------|--------|------|
| codellama_7b_mbpp | 179 | 0.0000 | [0.0000, 0.0000] | ❌ FAIL |
| deepseek_coder_6.7b_humaneval | 91 | 0.0000 | [0.0000, 0.0000] | ❌ FAIL |
| deepseek_coder_6.7b_mbpp | 228 | 0.0000 | [0.0000, 0.0000] | ❌ FAIL |
| llama3_8b_humaneval | 76 | 0.0000 | [0.0000, 0.0000] | ❌ FAIL |
| llama3_8b_mbpp | 210 | 0.0000 | [0.0000, 0.0000] | ❌ FAIL |

**Summary:** 0/5 pairs pass exceedance >= 0.5

### FCD Negative Control (Specificity Check)

**FCD specificity:** 0/5 pairs have FCD exceedance < PCD exceedance -> ⚠️ FAILS

| Pair | PCD exceedance | FCD exceedance | FCD < PCD |
|------|---------------|---------------|-----------|
| codellama_7b_mbpp | 0.0000 | 0.4302 | ❌ |
| deepseek_coder_6.7b_humaneval | 0.0000 | 0.1209 | ❌ |
| deepseek_coder_6.7b_mbpp | 0.0000 | 0.1096 | ❌ |
| llama3_8b_humaneval | 0.0000 | 0.0000 | ❌ |
| llama3_8b_mbpp | 0.0000 | 0.0952 | ❌ |

### D_p Diagnostic

| Pair | mean_D_p | n_mid_θ | Status |
|------|----------|---------|--------|
| codellama_7b_mbpp | 0.2799 | 179 | ✅ OK |
| deepseek_coder_6.7b_humaneval | 0.3927 | 91 | ✅ OK |
| deepseek_coder_6.7b_mbpp | 0.3614 | 228 | ✅ OK |
| llama3_8b_humaneval | 0.3606 | 76 | ✅ OK |
| llama3_8b_mbpp | 0.3642 | 210 | ✅ OK |

## Mechanism Activation Indicators

| Indicator | Status |
|-----------|--------|
| PCD computed for all 5 pairs | ✅ |
| MC null simulation (n_sim=100000) | ✅ |
| Gate evaluated | ✅ |
| FCD negative control evaluated | ✅ |

## Conclusion

**GATE FAIL**: Only 0/5 pairs pass (needed >= 3).
Failing pairs: codellama_7b_mbpp, deepseek_coder_6.7b_humaneval, deepseek_coder_6.7b_mbpp, llama3_8b_humaneval, llama3_8b_mbpp.

**Routing:** ROUTE_TO_PHASE_0 — PCD does not exceed sampling noise; hypothesis redesign needed.
