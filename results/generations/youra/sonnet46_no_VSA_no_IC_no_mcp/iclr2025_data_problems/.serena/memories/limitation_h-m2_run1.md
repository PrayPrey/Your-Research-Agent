# Limitation Record: h-m2 (Run 1)

**Date:** 2026-08-25T17:30:00+00:00
**Hypothesis:** h-m2
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

SHOULD_WORK gate PARTIAL — effect direction opposite to hypothesis on all 4 benchmarks.
Pythia-1B PoC shows dedup-Pile models have HIGHER min-k% scores than Pile models
(negative differential on all benchmarks, p_corrected=1.0 one-tailed).
No self-recovery possible — fundamental direction reversal, not a parameter issue.

Root cause hypothesis: Deduplication removes repeated n-grams including common
linguistic patterns shared with benchmarks. Pile models, having seen more repetition
of these patterns, may produce lower logprob scores (more "bored"/diffuse distribution)
rather than higher scores, contrary to the near-memorization prediction.

## Failed Checks

- n_significant=0/4 (need >=2 at p<0.0125 Bonferroni-corrected)
- n_pile_higher=0/4 (direction opposite: dedup > Pile on all benchmarks)
- Effect direction wrong: Pile mean lower than dedup mean on all 4 benchmarks

## Partial Results

| Metric | Value |
|--------|-------|
| mmlu differential (Pile - Dedup) | -0.1039 |
| hellaswag differential | -0.0921 |
| arc_challenge differential | -0.0766 |
| winogrande differential | -0.1596 |
| n_significant | 0/4 |
| n_pile_higher | 0/4 |
| tests_passed | 22/22 |

## Experiment Summary

Pythia-1B PoC (500 items per benchmark, GPU 4, CUDA_VISIBLE_DEVICES=4).
Models: EleutherAI/pythia-1b (Pile) vs EleutherAI/pythia-1b-deduped.
Metric: min-k% probability score (k=20, Shi et al. 2023).
Statistical test: one-tailed paired t-test + Wilcoxon, Bonferroni α=0.0125.
Full experiment v4 (1B+6.9B, full test sets) also ran; direction consistent.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to Phase 5 with this limitation noted.

Future research attempts should consider:
1. Direction of deduplication effect on min-k% is opposite to naive prediction
2. Repeated n-grams may not translate to higher logprob for specific benchmark items
3. Consider measuring memorization via perplexity difference rather than min-k% scores
4. Alternative: measure verbatim reproduction rate rather than token probability

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-08-25T17:30:00+00:00*
*For cross-phase reference*
