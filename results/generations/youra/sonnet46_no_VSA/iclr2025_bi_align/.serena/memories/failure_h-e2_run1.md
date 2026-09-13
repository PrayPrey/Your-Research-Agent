# Phase 4 Failure Record: h-e2 (Run 1)

**Date:** 2026-07-29T21:30:00
**Hypothesis:** h-e2
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MATCH_RATE_BELOW_THRESHOLD

## Gate Evaluation

| Criterion | Threshold | Actual | Pass? |
|-----------|-----------|--------|-------|
| N (complete rows) | ≥ 30 | 30 | ✓ PASS |
| match_rate | ≥ 0.70 | 0.5172 | ✗ FAIL |
| **Overall gate** | **BOTH required** | — | **FAIL** |

## Performance Gap

| Metric | Actual | Target | Gap |
|--------|--------|--------|-----|
| match_rate | 0.5172 | 0.70 | -0.1828 (-26.1%) |
| N matched | 30 | ≥ 30 | PASS |

## Root Cause Analysis

- ~20 of 58 AlpacaEval-LC models are structurally absent from Open LLM Leaderboard v1 by design: proprietary API models (GPT-4, Claude, Gemini Pro, etc.) cannot be evaluated on open harnesses
- Best-of-N variants (e.g., PairRM+Tulu 2+DPO 70B best-of-16) have no independent leaderboard entry
- Open-source models not yet indexed in this leaderboard snapshot (DEITA, LMCocktail, Evo, PlatoLM, etc.)
- Effective open-source coverage is 30/38 = 78.9% — exceeds 70% threshold when denominator restricted to open-source models
- No fuzzy matching threshold (70–85) achieves 70% overall match rate; constraint is structural absence, not matching quality

## Threshold Sensitivity

| Threshold | N matched | match_rate |
|-----------|-----------|------------|
| 70 | 33 | 56.90% |
| 75 | 32 | 55.17% |
| 80 | 30 | 51.72% |
| 85 | 30 | 51.72% |

## Lessons Learned

1. AlpacaEval-LC includes proprietary models (GPT-4, Claude, Gemini) that are structurally absent from any open evaluation harness — any join with Open LLM Leaderboard will structurally exclude ~35% of AlpacaEval-LC entries.
2. The 70% threshold was too aggressive for a cross-leaderboard join involving proprietary models; 55–60% is a more realistic expectation for this dataset pair.
3. MT-Bench integration via hardcoded published scores is feasible: 35 models from Zheng et al. 2023, 26 overlap with the 30-model matched subset.
4. The 30-model matched dataset is sufficient for correlation analysis (h-m1, h-m2) but introduces range restriction bias — absent proprietary models tend to have higher AlpacaEval-LC scores.
5. Per 02c failure mode spec ("match_rate<0.70 but N≥30: Proceed with caveat"), the pipeline was allowed to continue to h-m1/h-m2 despite FAIL — but the formal gate is FAIL.

## Routing Decision

**Gate:** MUST_WORK → FAIL → ROUTED_TO_PHASE_0

However, note: the experiment brief explicitly defined a failure-mode caveat for this exact scenario (N≥30 but match_rate<0.70 → proceed with selection bias note). If re-running Phase 0, consider:
- Relaxing the match_rate threshold to ≥0.55 (achievable with current datasets)
- OR restricting the denominator to open-source models only (effective rate = 78.9%)
- OR replacing Open LLM Leaderboard v1 with a leaderboard that includes proprietary models (e.g., LMSYS Chatbot Arena ELO)

## Feedback for Phase 0 Brainstorming

### Suggested Modifications
- Change gate criterion to match_rate ≥ 0.55 (open + proprietary) OR ≥ 0.70 (open-source only)
- Consider using LMSYS Chatbot Arena ELO scores as the third dataset (covers proprietary models)
- Keep N ≥ 30 criterion (achieved)

### What NOT To Do
- Do not use Open LLM Leaderboard v1 as sole benchmark source when AlpacaEval-LC is the alignment metric — structural absence of proprietary models guarantees sub-70% join rate
- Do not set match_rate ≥ 0.70 as hard gate without accounting for structural absence

### What Showed Promise
- Fuzzy join via rapidfuzz token_set_ratio is effective for open-source model name normalization
- MT-Bench hardcoded scores provide reliable coverage for the 30 matched models
- The 30-model matched subset is usable for correlation analysis with appropriate caveats

---
*For cross-phase reference*
*Written at: 2026-07-29T21:30:00*
