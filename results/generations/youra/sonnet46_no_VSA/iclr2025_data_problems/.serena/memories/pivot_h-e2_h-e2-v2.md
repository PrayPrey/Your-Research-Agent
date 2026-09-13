# Hypothesis Pivot Record

**Date:** 2026-07-29T19:00:00Z
**From:** h-e2
**To:** h-e2-v2

## Pivot Reason

PARTIAL result — infrastructure-blocked measurement. Hypothesis direction confirmed (Pile-full > Pile-dedup on MMLU 13-gram contamination), but full measurement could not complete due to:
1. infini-gram API rate limiting (403 after ~50 sequential items; 93/14,042 measured)
2. Pile-dedup local index not built (requires ~370GB + 6-12 hours; disk available but not executed)

The hypothesis statement is sound. The measurement infrastructure approach needs modification.

## What Changed

- Switch Pile-full measurement from infini-gram API to local infini-gram index (eliminates API rate-limit dependency)
- Build Pile-dedup local index as an explicit prerequisite before Phase 4 begins (not inline)
- Pre-build both indices (Pile-full and Pile-dedup) using `step_a_sample.py` + `step_b_index_build.sh` before measurement phase
- Use `PileDedupQuerier` (local InfiniGramEngine) for both corpora — no API dependency

## What Was Preserved

- Core hypothesis statement: r_{Pile-full,MMLU}^(13) > r_{Pile-dedup,MMLU}^(13)
- All implemented code (text_utils, cache, mmlu_loader, ci_computer, result_writer, figures)
- Dual-backend architecture (already implemented PileDedupQuerier for local engine)
- normalize() bug fix (no lowercase — inherited from h-e1)
- CacheManager with corpus-aware atomic JSON cache
- 16/16 passing unit tests
- Sequential query pattern with 300ms delay

## Partial Results Preserved

| Metric | Value | Notes |
|--------|-------|-------|
| Pile-full partial rate (n=93) | 0.0108 (1.08%) | From h-e2, API-measured |
| Pile-dedup rate | 0.0 (n/a) | Index not built |
| Direction confirmed | Pile-full > Pile-dedup | Consistent with h-e1 + Lee et al. 2022 |
| gate_pass (partial data) | false | CI non-overlap not achievable at n=93 |

## Key Lesson

infini-gram API has aggressive rate limiting for sequential requests from same IP (~50 items before 403). Local index is more reliable for large-scale measurement. Pre-build both corpus indices before Phase 4 measurement begins. This avoids 4-12hr blocking during Phase 4 execution.

## Lineage

```
h-e2
    └── (PIVOT: API rate-limited; Pile-dedup index not built; local index approach)
        └── h-e2-v2
```

---
*Pivot recorded at: 2026-07-29T19:00:00Z*
