# Phase 4 Failure Record: H-E1 (Run 1)

**Hypothesis ID:** H-E1  
**Type:** EXISTENCE  
**Phase:** 4 (PoC Implementation & Validation)  
**Gate Type:** MUST_WORK  
**Gate Result:** FAIL  
**Reflection Outcome:** ROUTED_TO_PHASE_0  
**Date:** 2026-08-04

---

## Failure Summary

No qualifying proxy pair found satisfying both gate conditions:
- **P1:** N_intersection ≥ 50
- **P2:** Pearson r < 0.5

**Qualifying pairs: 0 / 6**

---

## Experimental Results

| Pair | N | r | P1 | P2 | Result |
|------|---|---|----|----|--------|
| MT-Bench × Arena ELO | 55 | 0.9708 | PASS | FAIL | Not qualifying |
| MT-Bench × RewardBench-Chat | 10 | -0.1143 | FAIL | PASS | Not qualifying |
| WildBench × Arena ELO | 36 | 0.9350 | FAIL | FAIL | Not qualifying |
| WildBench × RewardBench-Chat | 16 | 0.4830 | FAIL | PASS | Not qualifying |
| AlpacaEval 2.0 × Arena ELO | 14 | 0.6737 | FAIL | FAIL | Not qualifying |
| AlpacaEval 2.0 × RewardBench-Chat | 5 | 0.7658 | FAIL | FAIL | Not qualifying |

---

## Root Cause Analysis

### RC-1: Arena ELO is an H→AI Proxy (Architectural Flaw)
Arena ELO measures human preference for AI capability in conversation — structurally the same dimension as MT-Bench, WildBench, AlpacaEval. All three H→AI proxies show r > 0.93 against Arena ELO. P2 will always fail for this AI proxy.

### RC-2: RewardBench-Chat Has Insufficient Model Overlap
RewardBench-Chat evaluates reward models on preference alignment tasks. Its model universe (~188 reward models) has very limited naming overlap with chat LLM leaderboards. Even with fuzzy matching and name normalization, max intersection was N=10 (MT-Bench × RewardBench-Chat).

### RC-3: Hypothesis Design Assumed Arena ELO = AI→H Proxy
The original hypothesis classified Arena ELO as an AI→H proxy, but Arena ELO is determined by human preference in side-by-side comparisons of task capability — it is fundamentally an H→AI signal, not an AI→H signal.

### RC-4: Data Source Incompatibilities
- LMSYS combined CSV (MT-Bench + Arena ELO in one file) only exists in 2023 snapshots
- AlpacaEval uses informal display names incompatible with formal model identifiers
- RewardBench-Chat names are HTML-wrapped HF model paths

---

## Lessons Learned

1. **Proxy classification matters**: Arena ELO is an H→AI proxy, not AI→H. Only reward model benchmarks (RewardBench, preference learning leaderboards) are genuine AI→H proxies.
2. **Model name normalization is critical**: Multi-leaderboard intersection requires canonical model name mapping, not just fuzzy matching.
3. **RewardBench coverage is the binding constraint**: With only ~10-16 overlapping models per H→AI leaderboard, P1 (N≥50) is unachievable with current RewardBench-Chat data.
4. **Hypothesis needs redesign**: BAI computation requires finding or constructing an AI→H proxy dataset with ≥50 model overlap with H→AI leaderboards.

---

## Recommended Redesign Direction (for Phase 0)

1. **Replace Arena ELO as AI→H proxy** — use reward model score leaderboards with broader model coverage
2. **Find/construct augmented AI→H dataset** — combine multiple reward model evaluations to reach N≥50
3. **Or reframe hypothesis** — use within-dataset comparisons instead of cross-leaderboard intersection
4. **Canonical name mapping** — build explicit model name alias table across leaderboards

---

## Files

- Validation report: `h-e1/04_validation.md`
- Results: `h-e1/results/pair_results.json`
- Figures: `h-e1/figures/`
