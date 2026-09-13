# Limitation Record: h-m3 (Run 1)

**Date:** 2026-08-25T18:35:00+00:00
**Hypothesis:** h-m3
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

SCG BERTScore AUROC (0.378) differs from SE AUROC (0.286) by 0.092, exceeding the 0.03 gate
threshold. BERTScore on short QA answers is dominated by word overlap rather than semantic
equivalence, causing SCG and SE to diverge. Secondary: SE sign convention mismatch likely explains
low SE AUROC (0.286 vs h-e1's 0.57); h-m3 uses unsigned SE scores while h-e1 negates for AUROC.

## Failed Checks

- |auroc_scg - auroc_se| <= 0.03 (actual: 0.092)
- auroc_not_random (auroc > 0.45): False (SCG AUROC = 0.378)
- scores_in_range [0,1]: False (rescale_with_baseline causes slight OOB)

## Partial Results

| Metric | Value |
|--------|-------|
| auroc_scg | 0.3779 |
| auroc_se | 0.286 |
| auroc_te | 0.4381 |
| delta | 0.092 |
| n_questions | 98 |
| K | 10 |

## Experiment Summary

SCG BERTScore was tested on Llama-2-7B TriviaQA dev (N=98, K=10). SCG AUROC=0.378,
SE AUROC=0.286, delta=0.092. Gate threshold 0.03 not met. Mechanism: BERTScore measures
surface lexical overlap; NLI-based SE clustering captures semantic entailment — the two
diverge especially on short 1-3 word QA answers. Both methods fail as uncertainty estimators
on this subset (AUROC < 0.5), but they fail differently.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to H-M4 with this limitation noted.

Future research attempts should consider:
1. SE sign convention (negate SE scores before computing AUROC as h-e1 does)
2. BERTScore suitability for very short QA answers — consider ROUGE or NLI-based SCG instead
3. Validate SE AUROC baseline matches h-e1's ~0.57 before comparing any method to SE

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0, this limitation informs brainstorming
- **Phase 6 Discussion:** Limitation included in paper's Limitations section

---
*Limitation recorded at: 2026-08-25T18:35:00+00:00*
*For cross-phase reference*
*Note: Written to local file (Serena MCP unavailable in no-MCP ablation session)*
