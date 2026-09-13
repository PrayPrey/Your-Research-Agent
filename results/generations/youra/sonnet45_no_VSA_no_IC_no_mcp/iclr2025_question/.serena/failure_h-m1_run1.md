# Phase 4 Failure Record: h-m1 (Run 1)

**Date:** 2026-08-25T00:00:00+00:00
**Hypothesis:** h-m1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MECHANISM_INVALID

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Mean Entropy (Hallucinated) | 2.249 | 2.295 (Factual) | -0.046 (-2.0%) |
| Statistical Significance | p=0.9333 | p<0.05 (required) | FAIL |
| Effect Direction | OPPOSITE | Expected: hallucinated > factual | INVALID |

## Root Cause Analysis

- **Hypothesis assumption violated:** Epistemic uncertainty does NOT manifest as wider next-token probability distributions in GPT-2 on wiki_bio dataset
- **Effect in opposite direction:** Factual outputs showed HIGHER entropy (2.295) than hallucinated outputs (2.249), contrary to prediction
- **Statistical insignificance:** p-value = 0.9333 >> threshold (0.05), no evidence supporting hypothesis
- **Dataset/model mismatch:** wiki_bio_gpt3_hallucination uses GPT-3 generated labels tested on GPT-2, smaller model may have different uncertainty patterns
- **Alternative explanation:** Entropy may reflect vocabulary diversity (factual bios = specific details) rather than epistemic uncertainty
- **Core mechanism broken:** Variance-based uncertainty chain breaks at Step 2 (variance → entropy correlation)

## Lessons Learned

1. **Single-token entropy ≠ epistemic uncertainty:** Per-token entropy reflects vocabulary breadth, not model confidence. H-e1 showed variance exists across passes, but h-m1 failed to link entropy to uncertainty.

2. **Model-dataset alignment critical:** Testing GPT-3-labeled data on GPT-2 introduces model mismatch. Smaller models may manifest uncertainty differently (or not at all via entropy).

3. **Mechanism assumptions need empirical validation:** Core assumption A1 ("epistemic uncertainty → wider token distributions") was untested before building h-m2/h-m3/h-m4. Empirical check at each mechanistic step prevents cascading failures.

4. **Alternative metrics required:** If entropy fails, explore:
   - Max token probability (confidence proxy)
   - Sequence perplexity
   - Cross-pass variance (h-e1 already validated)
   - Ensemble-based uncertainty (h-m4 baseline)

5. **Prompt effects matter:** Longer factual bios → more possible continuations → higher entropy (unrelated to uncertainty). Control for prompt length/complexity in future experiments.

## Feedback for Next Phase

### Suggested Modifications

- Test variance-hallucination correlation DIRECTLY (bypass entropy mechanism)
- Use larger models (GPT-2 Medium/Large) with clearer uncertainty signals
- Switch to QA datasets where uncertainty is salient (e.g., unanswerable questions)
- Explore alternative uncertainty metrics (max prob, perplexity, mutual information)

### What NOT To Do

- Do NOT rely on single-token entropy as uncertainty proxy without empirical validation
- Do NOT assume GPT-3 hallucination labels transfer to GPT-2 behaviors
- Do NOT proceed with h-m2/h-m3 (both depend on failed h-m1 mechanism)
- Do NOT ignore prompt length effects (control for context complexity)

### What Showed Promise

- Variance computation (h-e1) validated successfully — variance exists and is measurable
- End-to-end pipeline execution (dataset loading, generation, statistical tests) robust
- Unit tests for entropy formula passed (implementation correct, hypothesis wrong)
- Visualization clearly showed distribution overlap (helped identify opposite-direction effect)

---
*For cross-phase reference*
*Written at: 2026-08-25T00:00:00+00:00*
