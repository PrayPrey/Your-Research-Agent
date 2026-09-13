# Limitation Record: h-m2 (Run 1)

**Date:** 2026-08-09T14:00:00+00:00
**Hypothesis:** h-m2
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

Routing robustness hypothesis falsified: MiniLM embeddings rely on surface-level lexical features rather than deep semantic task structure. Paraphrase variations and keyword removal both cause routing failures.

## Failed Checks

- Cosine Mean 0.782 < 0.90 threshold (FAIL)
- Max Accuracy Drop 44.4% > 10% threshold (FAIL)
- Routing Consistency 76.1% < 85% threshold (FAIL)

## Partial Results

| Metric | Value |
|--------|-------|
| cosine_mean | 0.7818 |
| routing_consistency | 76.1% |
| wordnet_cosine | 0.720 |
| embedding_cosine | 0.843 |

## Experiment Summary

H-M2 tested whether linear probe routing (validated in H-E1) maintains stability under input perturbations. WordNet synonym substitutions cause embedding drift (cosine ~0.72). Even 20% keyword masking causes 26% accuracy drop. Task families with distinctive vocabulary show higher robustness; open-domain NLI tasks are fragile.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded with this limitation noted.

Future research attempts should consider:
1. Use more robust encoder (larger models, contrastive fine-tuning)
2. Add paraphrase augmentation during probe training
3. Combine embedding routing with keyword-based fallback

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0, this informs brainstorming about encoder robustness needs
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-08-09T14:00:00+00:00*
*For cross-phase reference*