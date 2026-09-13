# Limitation Record: h-e2-v3 (Run 1)

**Date:** 2026-07-29T20:30:00Z
**Hypothesis:** h-e2-v3
**Run:** 1
**Gate Type:** MUST_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

Pile-full measurement blocked by infini-gram API HTTP 403 ForbiddenException (AWS API Gateway IP-level block). This is not a hypothesis design failure — the Pile-dedup measurement succeeded completely (0.328%, 95% CI [0.242%, 0.427%], n=14,042 MMLU items). The gate comparison `r_{Pile-full} > r_{Pile-dedup}` cannot be evaluated because Pile-full API is inaccessible from this IP.

## Failed Checks

- infini-gram API accessible from current IP
- Pile-full 13-gram contamination rate measurable
- Direction check: r_pile_full > r_pile_dedup (INDETERMINATE)
- CI non-overlap check (INDETERMINATE)

## Partial Results

| Metric | Value |
|--------|-------|
| pile_dedup_contamination_rate | 0.328% (46/14,042) |
| pile_dedup_ci_lower | 0.242% |
| pile_dedup_ci_upper | 0.427% |
| pile_full_contamination_rate | N/A (API blocked) |
| n_items_measured | 14,042 |
| bootstrap_resamples | 1000 |
| gate_status | INCONCLUSIVE_API_BLOCKED |

## Experiment Summary

Full experiment executed. Pile-dedup streaming approach (200,000 docs, 167.4M unique 13-grams) worked correctly. All MMLU items measured against Pile-dedup. Pile-full infini-gram API blocked at first request with HTTP 403 ForbiddenException (x-amzn-ErrorType header). Block persists across all paths/methods — confirmed IP-level AWS WAF block, not rate limiting. Predecessor h-e2 used same endpoint successfully, suggesting IP was blocked due to query volume during h-e2 attempts.

## Mitigation Options for Future Attempts

1. Request API token from infini-gram team (https://infini-gram.io) — token holders may bypass IP blocks
2. Use different compute node with different public IP
3. Build local infini-gram index (~370 GB disk, multi-hour build) for offline measurement
4. Use h-e2 cached result (rate_pile_full=0.0107 from 93 items) as proxy — low n but directionally consistent with h-e2-v3 Pile-dedup rate of 0.328%

## Context

This limitation was recorded but **did not block the pipeline**.
The Pile-dedup measurement (0.328%) is valid and reusable — cached in `.cache/h_e2_v3/pile_dedup/`.
The hypothesis that Pile-full > Pile-dedup is directionally supported by h-e2 data but unconfirmed at full scale.

Future research attempts should consider:
1. Infrastructure access to infini-gram API must be verified before scheduling full runs
2. Pile-dedup streaming approach (HuggingFace) is reliable and scales to full test set
3. h-e2 partial result (0.0107 from 93 items) provides prior for expected Pile-full rate

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0, note that Pile-full measurement requires API access
- **Phase 6 Discussion:** Limitation included in paper's Limitations section — report Pile-dedup rate as confirmed, Pile-full as directionally supported but blocked

---
*Limitation recorded at: 2026-07-29T20:30:00Z*
*For cross-phase reference*
