# Per-Hypothesis Context: h-e1

**Date:** 2026-08-28
**Source:** 02b_verification_plan.md

---

## Hypothesis Information

**ID:** h-e1  
**Type:** EXISTENCE  
**Statement:** Under factual QA with frozen LLMs, if we extract token probability distributions from single forward passes, then entropy signals are measurable and correlate with prediction correctness, because output distributions encode uncertainty through their shape.

**Rationale:** Foundation hypothesis validating that entropy signal exists and is accessible. Without this, subsequent mechanism hypotheses cannot be tested. Tests P1-P3 infrastructure.

---

## Variables

**Independent:** None (infrastructure validation)  
**Dependent:** Entropy extractability, correlation with accuracy  
**Controlled:** Model family (Llama 7B/13B/70B), Datasets (TriviaQA/SQuAD/NQ)

---

## Success Criteria (PoC: Direction-based)

**Primary:**
- Entropy signal extractable for >95% of predictions
- Significant negative correlation with accuracy (p < 0.05)

**Secondary:**
- Q3 population >5%
- Entropy range spans >50% of theoretical maximum

---

## Gate

**Type:** MUST_WORK  
**Pass Condition:** Entropy extractable (>95%), significant correlation (p < 0.05)  
**Fail Action:** ABANDON (infrastructure broken, cannot proceed)

---

## Dependencies

**Prerequisites:** None (foundation hypothesis)  
**Blocks:** h-m1, h-m2, h-m3

---

## Verification Protocol

1. Run inference on TriviaQA dev set (~1000 examples), extract logits and compute softmax distributions
2. Calculate Shannon entropy per prediction, verify continuous range (0-log|V|)
3. Compute Spearman correlation between entropy and prediction correctness (binary: correct/incorrect)
4. Verify correlation is significant (p < 0.05) and negative (higher entropy → lower accuracy expected)
5. Confirm quadrant Q3 population >5% (assumption A2 check)

---

## Experimental Setup (from Phase 2B Section 1.3)

**Dataset:**
- Primary: TriviaQA (unfiltered)
- Secondary: SQuAD, Natural Questions
- Source: HuggingFace datasets
- Justification: Factual QA with single answers - fits selective prediction use case

**Model:**
- Llama-2-7B, Llama-2-13B, Llama-2-70B
- Source: Meta AI / HuggingFace
- Type: Autoregressive decoder-only transformer
- Justification: Open models with accessible logprobs, no retraining required

**Baselines (for Phase 5):**
- Max-probability thresholding
- Deep ensemble uncertainty (state-of-art but expensive)
- MC Dropout (moderate performance)

---

## Key Assumptions

**A1:** Entropy and max-prob not perfectly correlated (r < 0.95)  
**A2:** Disagreement quadrant Q3 (high max-prob, high entropy) is non-trivial (>5%)  
**A3:** Multi-modal uncertainty manifests in top-5 token distributions  
**A4:** Entropy thresholds can achieve target coverage levels  
**A5:** Single-answer factual QA is representative use case

---

**Next Phase:** Phase 2C - Experiment Design
