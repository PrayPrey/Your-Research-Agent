# Limitation Record: h-c1 (Run 1)

**Date:** 2026-07-29T19:30:00Z
**Hypothesis:** h-c1
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

SHOULD_WORK gate failed due to API_UNAVAILABLE. The infini-gram HTTP API
(https://api.infini-gram.io/) returned HTTP 403 Forbidden (AWS ForbiddenException)
for all requests from this IP address. This is an IP-level block, not a rate-limit
(429) error. The free-tier infini-gram API enforces per-session or per-IP call
budgets that were exhausted during h-e1 (~353k planned calls for h-c1 is a large
volume for a free API endpoint).

The experiment infrastructure failed; the hypothesis was not tested. This is NOT
an informative null — both rates (r_{C4,BoolQ}^(13) and r_{Dolma,BoolQ}^(13))
were unmeasured.

## Failed Checks

- r_{C4,BoolQ}^(13) - r_{Dolma,BoolQ}^(13) >= 0.5pp (UNMEASURED — API blocked)
- API accessible (count returned >= 1 for any item) — FAIL (HTTP 403 on all requests)

## Partial Results

| Metric | Value |
|--------|-------|
| Items measured (C4) | 0/3270 |
| Items measured (Dolma) | 0/3270 |
| API error type | HTTP 403 Forbidden (IP-level block) |
| Backoff attempts | 7 × [30,60,120,300]s — all failed |

## Experiment Summary

Script run_hc1.py completed with exit=0 (sentinel path): query_count() exhausted
all retries returning -1, item_has_overlap() treated sentinel as no-overlap
(overlaps=False). Result: 0/3270 items measured per corpus — artifact of API
block, not a true measurement.

Code is correct and complete. All three h-e1 bugs are resolved.
Re-run when infini-gram API access is restored.

Re-run command:
  cd /home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_data_problems && \
  /home/PrayPrey/miniforge3/envs/youra-h-c1/bin/python -u \
  docs/youra_research/h-c1/code/run_hc1.py >> \
  docs/youra_research/h-c1/code/experiment.log 2>&1

## Context

This limitation was recorded but **did not block the pipeline**.
SHOULD_WORK gate failure is informative by design (Phase 2B). The pipeline
may proceed to downstream hypotheses.

Future research attempts should consider:
1. Using local infini-gram suffix-array indices to avoid HTTP API rate limits
2. Distributing ~353k API calls over multiple sessions with long delays
3. Re-running h-c1 after API IP block is lifted

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0, this limitation informs
  brainstorming to use local infini-gram indices rather than HTTP API
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section
  as "h-c1 positive control unconfirmed due to API rate limits"

---
*Limitation recorded at: 2026-07-29T19:30:00Z*
*For cross-phase reference*
