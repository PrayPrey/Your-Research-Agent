# Limitation Record: h-e2 (Run 1)

**Date:** 2026-08-02T17:42:00+00:00
**Hypothesis:** h-e2
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

SHOULD_WORK gate failed — NLP vs CV reign length difference not supported by data.
Mann-Whitney U test (directional NLP > CV) yields p=0.9513, far from the 0.05 threshold.
No improvement path identified (medians equal at 1.0 year each, 101 NLP vs 136 CV spells).

## Failed Checks

- mann_whitney_p >= 0.05 (p=0.9513, required < 0.05)
- effect_direction: NLP <= CV (required NLP > CV)

## Partial Results

| Metric | Value |
|--------|-------|
| fuzzy_match_coverage | 69.0% (PASS ≥50%) |
| mann_whitney_p | 0.9513 (FAIL, required <0.05) |
| median_nlp_reign | 1.0 year |
| median_cv_reign | 1.0 year |
| log_rank_p | 0.0487 (significant two-sided, wrong direction) |
| Cox HR domain_nlp | 1.334 [1.001, 1.779] — NLP displaced FASTER |
| pass_rate | 0.333 (1/3 checks passed) |

## Experiment Summary

Statistical analysis of NLP vs CV domain plurality reign lengths using the h-e0 survival panel
(656 panel records, 87 tasks, 345 displacement events). Domain classification via rapidfuzz
token_sort_ratio ≥85 achieved 69% coverage (60/87 tasks: 23 NLP, 37 CV, 27 Other).
World-Snapshot domain CSVs unavailable (HTTP 404); built-in PwC-taxonomy domain lists used as fallback.

Counter-finding: Cox HR=1.334 (p=0.049) indicates NLP benchmarks are displaced FASTER than CV,
opposite to the hypothesis direction. Log-rank (two-sided) p=0.0487 confirms domain differences
exist but in the wrong direction.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded with this limitation noted. h-m1 is unaffected (SHOULD_WORK gate, no cascade).

Future research attempts should consider:
1. The NLP vs CV domain distinction does NOT explain plurality reign length variance
2. The Cox finding (NLP displaced faster) may be worth exploring as a counter-hypothesis
3. Alternative moderators (benchmark age, dataset size, citation velocity) may be more predictive — h-m1 and h-m2 target these
4. World-Snapshot CSV availability should be verified before future domain-based experiments

## Lessons Learned

- World-Snapshot CSVs (nlp_tasks_detailed.csv, cv_tasks_detailed.csv) return HTTP 404; use built-in domain lists
- Both NLP and CV communities saturate benchmarks at similar rates (median 1 year each)
- Domain-type is not a useful moderator of benchmark longevity in this dataset

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation included in paper's Limitations section

---
*Limitation recorded at: 2026-08-02T17:42:00+00:00*
*For cross-phase reference*
