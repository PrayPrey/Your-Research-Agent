# H-M3 Context (Phase 2B Extract)

**Generated:** 2026-05-11
**Source:** 02b_verification_plan.md Section 2.2

---

## Hypothesis Information

**ID:** h-m3
**Type:** MECHANISM
**Statement:** Under representation changes from targeted interventions, if internal states affect multiple downstream capabilities, then performance on non-targeted dimensions D₂/D₃ shifts in correlated fashion, because prior multi-task learning work shows task interference from shared representations.

**Rationale:** Validates causal chain Step 3—representation changes must translate to measurable performance effects. If correlations are random (ρ≈0), propagation mechanism fails.

---

## Variables

**Independent Variables:**
- Target Dimension (D₁): {truthfulness, fairness, robustness}
- Non-Target Dimension Pair: {D₂, D₃}

**Dependent Variables:**
- Non-Target Dimension Score Changes: Δ(D₂), Δ(D₃)

**Controlled Variables:**
- Evaluation Protocol
- Perturbation Methodology

---

## Experimental Setup

**Dataset:** TruthfulQA (target), BBQ + AdvGLUE (non-target dimensions)
- Source: HuggingFace datasets (sylinrl/TruthfulQA, nyu-mll/BBQ, adversarial_glue)
- Path: datasets/{truthfulqa,bbq,advglue}

**Model:** Multi-family LLM suite
- Type: Pre-trained LLMs (1B-70B parameters)
- Source: HuggingFace Hub (e.g., Llama-3-8B, Mistral-7B, Qwen-1.8B, Mamba-1.4B, Falcon-40B)

---

## Verification Protocol

1. From H-E1 results, extract Δscores for non-targeted dimensions
2. Test whether Δ(D₂) and Δ(D₃) correlate with representation changes from H-M2
3. Classify correlation direction (positive/negative) and magnitude
4. Compare against random perturbation control (null hypothesis baseline)

---

## Success Criteria

**Primary:** Non-random correlation structure (differs from control baseline at p<0.05)
**Secondary:** Correlation magnitudes |ρ| > 0.2 (small-to-medium effects)

---

## Gate Conditions

**Gate Type:** SHOULD_WORK
**Threshold:** Non-random correlation structure (differs from control at p<0.05)
**Fail Action:** Narrow scope

---

## Prerequisites

**Depends on:** h-m2 (COMPLETED)

**h-m2 Results Summary:**
- ✅ All 24 layers showed representation changes (100%)
- Mean change magnitude: 0.143
- Attention layers changed more than residual streams (2.0× magnitude)
- Correlation with performance: r=0.150 (p=0.28, non-significant)
- Gate verdict: PASS (SHOULD_WORK allows continuation)

**Key Findings from h-m2:**
- Parameter updates cause uniform representation changes across all layers
- LoRA targeting of c_attn affects attention mechanisms most strongly
- TransformerLens + CKA pipeline validated and functional

**Inherited Components:**
- `transformer_lens_wrapper.py` - activation extraction
- `representation_analyzer.py` - pre/post comparison
- `similarity.py` - CKA computation
- Need extension: cross-dimension correlation analysis

---

## h-m3 Extensions Beyond h-m2

**Multi-dimensional Performance Tracking:**
- h-m2: Single aggregated performance delta
- h-m3: Track multiple dimensions separately (TruthfulQA, BBQ, AdvGLUE)

**Correlation Structure Analysis:**
- h-m2: Layer changes vs. aggregate performance
- h-m3: Which layers correlate with which dimensions

**Statistical Comparison:**
- h-m2: Simple correlation test
- h-m3: Compare to random baseline (permutation test)

---

## Recommendations from h-m2

1. **Per-dimension correlation:** Analyze correlation with each trustworthiness dimension separately (not aggregated)
2. **Larger sample:** Increase to 500+ samples for better representation coverage
3. **Layer-wise performance:** Track which layers most influence which dimensions
4. **Fix known bug:** Device mismatch in `transformer_lens_wrapper.py:convert_peft_to_hooked()`

---

*Context extracted from Phase 2B verification_plan.md for targeted experiment design*
