# Failure Analysis: h-m1 Layer-wise Bottleneck Detection

**Hypothesis ID:** h-m1  
**Type:** MECHANISM  
**Gate:** MUST_WORK  
**Result:** FAIL  
**Date:** 2026-08-19

---

## Hypothesis Statement

During pretraining, if models develop shared representational bottlenecks that encode both semantic content and behavioral meta-patterns, then layer-wise embedding analysis will show specific layers where coupled dimensions exhibit minimal distance, because these layers encode the shared features.

---

## What Failed

### Gate Criteria Not Met

**MUST_WORK gate required:**
1. ✓ Clear peaks detected (ratio > 1.2) — **PASSED** (36 peaks total)
2. ✗ Peaks consistent across all 3 coupled pairs — **FAILED** (peaks vary across pairs)
3. ✗ Cross-model stability (±10% tolerance) — **FAILED** (0/3 pairs aligned)
4. ✗ Uniform distance baseline rejected — **FAILED** (ANOVA p=nan)

### Specific Failures

1. **Cross-Model Alignment: 0/3 pairs aligned**
   - truthfulness-robustness: Not aligned across gpt2/gpt2-medium/gpt2-large
   - reliability-error_detection: Not aligned across models
   - fairness-explainability: Not aligned across models
   - Threshold: ≥2/3 pairs needed, got 0/3

2. **Uniform Distance Baseline: Not rejected**
   - ANOVA test produced p=nan for all models
   - Implementation error: single-element groups in ANOVA
   - Could not confirm layer-specific coupling vs uniform distance

3. **Peak Consistency: Failed within models**
   - Different coupled pairs showed peaks at different layers
   - Example (gpt2): truthfulness-robustness [1,7], reliability-error_detection [4,10], fairness-explainability [3,9]
   - Inconsistency suggests no shared bottleneck layers

---

## Root Cause Analysis

### Primary Issue: PoC Methodology Limitation

**Synthetic data does not inject layer-specific coupling patterns:**
- Hidden states extracted from real models (gpt2, gpt2-medium, gpt2-large)
- BUT failure samples are synthetic text without real trustworthiness failures
- No actual coupled dimension failures in the data
- Cannot validate layer-specific bottleneck hypothesis without real h-e1 outputs

### Technical Issues

1. **ANOVA Implementation Error**
   - Treating each layer's single ratio value as a group
   - scipy.stats.f_oneway requires groups with length > 1
   - Produces DegenerateDataWarning and p=nan
   - Fix: Reshape data or use different statistical test

2. **Model Family Mismatch**
   - Used GPT-2 family (12-36 layers) instead of target models
   - Target: GPT-4 (~96 layers), Claude 3 Sonnet (~64 layers), Llama 3 70B (80 layers)
   - Architectural differences may prevent coupling pattern transfer

---

## What Worked

### Methodology Successfully Demonstrated

1. **Hidden State Extraction:** ✓
   - Successfully extracted layer-wise embeddings from all 3 models
   - Cache system worked (600 samples × 3 models)
   - Runtime ~15 minutes

2. **Distance Computation:** ✓
   - Layer-wise cosine distance computed correctly
   - Distance ratio calculation functional
   - Visualization pipeline complete

3. **Peak Detection:** ✓
   - Detected 36 peaks across models and coupled pairs
   - Algorithm correctly identifies layers where ratio > threshold

4. **Code Structure:** ✓
   - Modular implementation (data, model, distance, baselines, viz)
   - Reusable for real data when available

---

## Lessons Learned

### Hypothesis Refinement Needed

**Possible alternative explanations:**

1. **Distributed Coupling (not layer-specific)**
   - Coupling may exist across ALL layers, not concentrated at bottlenecks
   - Shared features spread throughout the network
   - Would explain why no clear layer-specific peaks align

2. **Architecture-Dependent Coupling**
   - Different model architectures may have bottlenecks at different relative depths
   - GPT-4, Claude, Llama may not share aligned bottleneck structure
   - Coupling exists but manifests differently per architecture

3. **Alternative Mechanisms**
   - Attention pattern coupling (not hidden state coupling)
   - Token-level interactions instead of dimension-level
   - Coupling at semantic level, not representational bottleneck

4. **Data Quality Requirements**
   - Real h-e1 evaluation outputs required to validate
   - Synthetic data cannot capture true coupling structure
   - Need actual model outputs with trustworthiness dimension scores

---

## Recommended Next Steps

### Route to Phase 2A (Dialogue-based Refinement)

**Refinement questions:**
1. Is coupling layer-specific or distributed across all layers?
2. Should we test architecture-agnostic coupling vs architecture-specific?
3. Are there alternative mechanistic explanations (attention, token-level)?
4. Can we reframe as: "coupling exists BUT not via layer-specific bottlenecks"?

### Alternative Hypotheses to Explore

**h-m1-v2 (Distributed Coupling):**
- Statement: Coupling is distributed across all layers, not concentrated at bottlenecks
- Test: Mean distance across ALL layers (coupled vs uncoupled), no peak detection

**h-m1-v3 (Architecture-Dependent Bottlenecks):**
- Statement: Each architecture has its own bottleneck layers (not aligned)
- Test: Detect peaks per model independently, no cross-model alignment requirement

**h-m2-alt (Attention Coupling):**
- Statement: Coupling mediated by attention patterns, not hidden states
- Test: Analyze attention weights instead of hidden state distances

---

## Implementation Notes for Future Attempts

### If Re-attempting h-m1 with Real Data

**Required changes:**
1. Use actual h-e1 evaluation outputs (not synthetic)
2. Extract hidden states from target models (GPT-4, Claude, Llama 3 70B)
3. Fix ANOVA test (aggregate ratio values across sample pairs, not single ratio per layer)
4. Increase sample size for statistical power (current: 100 pairs per group, consider 500+)

### Code Preservation

**Working code location:** `/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_buildingtrust/h-m1_code/`

**Reusable components:**
- `src/model_wrapper.py` — Hidden state extraction (works)
- `src/distance_metrics.py` — Layer-wise distance computation (works)
- `src/visualization.py` — Plots (works)

**Needs fixing:**
- `src/baselines.py` — ANOVA test (reshape data or use alternative test)
- `src/data_generator.py` — Replace with real h-e1 loader

---

## Related Hypotheses

- **h-e1** (VALIDATED) — Established coupled pairs exist
- **h-m2** (NOT_STARTED) — Intervention hypothesis (depends on h-m1 mechanism)
- **h-m3** (NOT_STARTED) — Transfer learning hypothesis (depends on h-m1 mechanism)

**Impact of h-m1 FAIL:**
- h-m2 and h-m3 may need alternative mechanistic grounding
- Cannot test intervention on layer-specific bottlenecks if they don't exist
- May need to pivot to distributed coupling or attention mechanisms
