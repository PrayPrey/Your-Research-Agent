# Limitation Record: h-c1 (Run 1)

**Date:** 2026-08-25T22:10:00+00:00
**Hypothesis:** h-c1
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

SE's superiority over TE is not domain-general. The hypothesis that NLI-based semantic clustering (SE) filters token-level noise better than token entropy (TE) — and thus generalizes across benchmarks — was refuted. On TruthfulQA adversarial misconceptions, TE=0.5110 outperformed SE=0.4449 by 6.6 AUROC points, reversing the expected SE≥TE ordering.

The noise-filtering advantage of SE over TE is task-structure-dependent: it may hold on open-domain recall (TriviaQA) but fails on adversarial misconception tasks where models generate deterministic wrong answers with low sample variance, making NLI clustering uninformative while token entropy remains a useful signal.

## Failed Checks

- Primary gate: auroc_se > auroc_te (SE=0.4449 < TE=0.5110 — FAIL)
- Tertiary gate: full ranking SE>=SCG>TE>VC (observed TE>SCG>VC>SE — FAIL)
- mechanism_activated: false (SE noise-filtering did not activate as expected)

## Partial Results

| Metric | Value |
|--------|-------|
| auroc_se | 0.4449 |
| auroc_scg | 0.4921 |
| auroc_te | 0.5110 |
| auroc_vc | 0.4617 |
| secondary_gate (VC < TE) | PASS |
| n_questions | 141 |
| parse_rate_vc | 0.7659 |

## Experiment Summary

N=141 TruthfulQA yes/no questions. Observed ranking: TE(0.511) > SCG(0.492) > VC(0.462) > SE(0.445). All AUROC values near chance (0.44–0.51); CIs overlap 0.5. VC parse rate 76.6% (above 70% threshold). EM correct rate 41.8%. Cross-benchmark comparison: both SE and TE improved from TriviaQA to TruthfulQA, but TE improved more, reversing SE's expected advantage.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded with this limitation noted.

Future research attempts should consider:
1. The specific checks that failed
2. Whether SE>TE ordering depends on task structure (open-domain recall vs adversarial misconceptions)
3. Whether larger models (13B, 70B) recover the SE > TE ordering
4. Whether SE's NLI clustering fails when samples consistently agree on a wrong answer

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-08-25T22:10:00+00:00*
*For cross-phase reference*
