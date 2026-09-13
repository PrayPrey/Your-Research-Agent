# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-07-30T06:30:00Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** STRUCTURAL_DATA_UNAVAILABILITY

## Hypothesis Statement

N_joint ≥ 25 complete rows (TruthfulQA MC2, BBQ accuracy, HarmBench refusal rate, MMLU) exist after fuzzy join of HarmBench × lighteval/bbq_helm × Open LLM LB v1 leaderboards

## Performance Gap

| Metric | Result | Target | Gap |
|--------|--------|--------|-----|
| N_joint (complete rows) | 18 | 25 | -7 rows |
| HarmBench model coverage | 7/21 | 21/21 | -14 models |
| Match rate (fuzzy join) | 0.857 | - | N/A |

## Root Cause Analysis

- Only 7/21 HarmBench target models have complete TruthfulQA+MMLU in Open LLM Leaderboard v1 — structural temporal mismatch (HarmBench models released after LLM LB v1 snapshot)
- BBQ dimension not present in LLM LB v1 standard harness — no model-aggregated public source exists
- HarmBench infrastructure (website, GitHub, Zenodo) inaccessible at time of execution — paper ASR fallback viable for only 21 published models
- BeaverTails fallback (PKU-SafeRLHF) is preference data, not model evaluation data — incompatible

## Lessons Learned

1. Open LLM Leaderboard v1 has a hard cutoff that excludes many models evaluated in safety benchmarks (2023-2024 era models)
2. BBQ is not included in LLM LB v1 standard harness — need alternative aggregated source or per-model inference
3. Fuzzy join algorithm is correct (score_cutoff=75, match_rate=0.857) — the bottleneck is data availability, not join logic
4. HarmBench website/API unreliability requires robust fallback strategy in hypothesis design
5. Safety benchmark data (HarmBench ASR) is sparse in public leaderboard aggregators

## Reflection Outcome

ROUTED_TO_PHASE_0 — structural temporal mismatch between HarmBench target models and LLM LB v1 coverage is not fixable by code changes. Hypothesis needs fundamental redesign.

## Feedback for Phase 0 Redesign

### What NOT To Do
- Do not rely on Open LLM Leaderboard v1 for models released after mid-2023
- Do not assume BBQ is available in standard leaderboard harnesses
- Do not assume HarmBench website/infrastructure is reliably accessible

### Suggested Alternatives
- Use Open LLM Leaderboard v2 (broader model coverage, more recent)
- Use direct HarmBench paper ASR scores (Table 2) for the 21 published models only — redesign around N=21 target
- Consider using AlpacaEval or MT-Bench as alignment proxies instead of BBQ
- Consider self-computing BBQ accuracy via inference on a smaller model subset

### What Showed Promise
- Fuzzy join algorithm works correctly (0.857 match rate)
- HarmBench paper ASR data (21 models) is usable as fallback
- The core bi-alignment analysis concept is sound — data sourcing strategy needs revision

---
*For cross-phase reference*
*Written at: 2026-07-30T06:30:00Z*
