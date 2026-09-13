# Phase 4 Failure Record: h-e1 (Run 3)

**Date:** 2026-03-16T13:45:00+00:00
**Hypothesis:** h-e1
**Run:** 3
**Final Status:** FAIL
**Failure Type:** MECHANISM_NOT_ACTIVATED

## Hypothesis Statement

SelfCheckGPT-NLI (deberta-v3-large-mnli, N=5, temperature=0.7, utterance-level for dialogue) achieves AUROC >= 0.65 on both HaluEval-Dialogue AND HaluEval-QA using LLaMA-3-8B-Instruct, demonstrating that cross-sample NLI contradiction signal exists and discriminates hallucinated from factual responses.

## Performance Gap

| Metric | Ours | Gate Target | Gap |
|--------|------|-------------|-----|
| Dialogue AUROC | 0.4832 | >= 0.65 | -0.1668 |
| Dialogue CI lower | 0.4714 | >= 0.60 | -0.1286 |
| QA AUROC | 0.5326 | >= 0.65 | -0.1174 |
| QA CI lower | 0.5228 | >= 0.60 | -0.0772 |

**Gate:** MUST_WORK (4/4 criteria FAILED)

## Root Cause Analysis

- Llama-3.1-8B base model (NOT instruct variant) generates insufficient semantic diversity across N=5 stochastic samples — the intended gated access model Meta-Llama-3-8B-Instruct was unavailable
- Dialogue AUROC=0.4832 is below chance (0.52 threshold), indicating NLI mechanism NOT activated for dialogue
- Base LLM produces near-identical outputs across samples at temperature=0.7, yielding near-zero NLI contradiction variance
- Score std=0.175 (dialogue), 0.213 (QA) — variance exists in scores but no discriminative signal between hallucinated/factual classes
- SelfCheckGPT-NLI cross-task transfer (WikiBio → HaluEval) may require instruction-tuned model to generate semantically diverse responses

## Lessons Learned

1. SelfCheckGPT-NLI requires an instruction-tuned model to generate semantically diverse stochastic samples; base models collapse to near-identical outputs
2. Model access gating (HuggingFace) is a practical blocker — always identify fallback models during Phase 2C experiment design
3. Utterance-level segmentation for dialogue may be too coarse — sentence-level could improve NLI discrimination
4. Temperature=0.7 alone is insufficient for diversity when using base (non-instruct) models; top-p or higher temperature may help
5. Dialogue AUROC < chance is a strong signal that the mechanism fundamentally failed, not just underperformed

## Feedback for Next Phase (Phase 0 Redesign)

### Suggested Modifications
- Use an instruction-tuned model (e.g., Llama-3.1-8B-Instruct, Mistral-Instruct) to ensure stochastic sample diversity
- Verify model access/availability before finalizing hypothesis
- Consider alternative hallucination detection approaches that don't require instruction following (e.g., contrastive decoding, logit-based uncertainty)
- Explore sentence-level segmentation for both dialogue and QA tasks

### What NOT To Do
- Do NOT use base (non-instruct) LLMs for SelfCheckGPT-NLI — they lack the semantic diversity needed
- Do NOT assume cross-task transfer from WikiBio to HaluEval without empirical validation on the same model family
- Do NOT set AUROC >= 0.65 as gate without verifying the model can produce discriminative signals first

### What Showed Promise
- QA AUROC=0.5326 (above chance) suggests the NLI mechanism has weak signal on QA — with instruct model may reach gate
- Code infrastructure (generate.py, score.py, evaluate.py) works correctly and is reusable for next hypothesis
- Dataset loading (HaluEval via HuggingFace) is verified and working

## Cascade Effects

This failure caused cascade failure to: h-m1, h-m2, h-m3, h-m4 (all blocked)

## Routing Decision

**ROUTED_TO_PHASE_0** — PoC shows methodology doesn't work with current model setup.
Fundamental issue: wrong model variant used. Requires hypothesis redesign.

---
*For cross-phase reference*
*Written at: 2026-03-16T13:45:00+00:00*
