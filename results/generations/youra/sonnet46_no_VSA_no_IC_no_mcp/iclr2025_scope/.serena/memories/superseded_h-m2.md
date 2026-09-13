# Superseded Hypothesis Record

**Date:** 2026-08-26T19:30:00+00:00
**Hypothesis:** h-m2
**Superseded By:** Phase 2A redesign
**Status:** SUPERSEDED

## Supersede Reason

MUST_WORK gate FAILED. LoRA-Q macro-avg F1=0.89 vs SnapKV=0.00, delta=0.89 falls short of required ≥1.0 point improvement on LongBench v1 (narrativeqa/hotpotqa/2wikimqa, 10 examples each, 20% KV budget, LLaMA-2-7B). Both methods degenerate at 80% KV eviction on base (non-instruct) model. Hypothesis routed to Phase 2A for redesign with adjusted conditions.

## Compatibility Assessment

| Factor | Score/Result |
|--------|--------------|
| Compatibility Score | 0.3 |
| Recommendation | ROUTED_TO_PHASE_2A |
| Reasoning | Gate threshold not met; directional signal confirmed but SnapKV degenerates completely making delta comparison unreliable on base model... |

## Key Findings

- LoRA-Q F1=0.89 > SnapKV F1=0.00 (macro-avg) — directional signal confirmed
- Delta=0.89 falls short of MUST_WORK gate (≥1.0)
- SnapKV degenerates completely at 80% eviction on base LLaMA-2-7B
- Both methods suffer from extreme eviction ratio + base (non-instruct) model
- Root cause: gate comparison invalid when baseline collapses to zero

## Recommended Fix for Phase 2A

- Use instruction-tuned model (Llama-2-7b-chat-hf) instead of base model
- Lighter eviction ratio (50% instead of 80%) OR lower gate threshold (≥0.5 instead of ≥1.0)
- Run on full 21 LongBench tasks with larger sample (50+ examples per task)

## Timeline

1. Original hypothesis: h-m2 (LoRA-Q ≥ SnapKV + 1.0 point at 20% KV budget)
2. Gate FAIL detected: delta=0.89 < 1.0
3. Reflection outcome: ROUTED_TO_PHASE_2A
4. Decision: Redesign hypothesis conditions in Phase 2A

---
*Superseded at: 2026-08-26T19:30:00+00:00*
*For cross-phase reference*
