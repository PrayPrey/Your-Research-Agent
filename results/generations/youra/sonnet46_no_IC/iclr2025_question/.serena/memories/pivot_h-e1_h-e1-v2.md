# Hypothesis Pivot Record

**Date:** 2026-08-05T08:10:00+00:00
**From:** h-e1
**To:** h-e1-v2

## Pivot Reason

PARTIAL result (MUST_WORK gate, satisfied=false) — mechanism functional but A2 anchor pre-gate is unsatisfiable as specified. The A2 anchor halt gate (FR-4.1) fired on the first cell (llama2/triviaqa): selection-split final-layer entropy AUROC 0.5928 vs reference 0.5186 (delta +0.0742 > 0.03 tolerance). Root cause is a spec provenance flaw, NOT a code bug: H_E1_REFERENCES came from a v1 archive run (_archive/20260804T140137_routing_recovery) that used a materially different protocol, so no correct implementation of the current protocol can reproduce those reference numbers. The donor episode crashed before its anchor check ever executed, so the mismatch was never previously detected. Remaining 5 cells intentionally not run per halt semantics.

## What Changed

- Anchor reference provenance must be regenerated under the CURRENT protocol (or the A2 anchor criterion redefined) in Phase 2C for h-e1-v2
- Protocol differences that invalidated the old references:
  - sample: random 1000-of-7993 TriviaQA (random.seed(42)) vs validation[:1000] first-slice
  - prompt: bare example['question'] vs 'Q: {q}\nA:' template
  - labels: bidirectional substring vs normalized-alias exact match
  - signal: generation-time entropy of generate() scores vs teacher-forced logit-lens L32 entropy
  - dtype: bfloat16 vs float16
  - evaluation set: full n=1000 vs selection split n=500

## What Was Preserved

- Core existence claim is SUPPORTED on the completed cell: best intermediate (L31, adj_kl) corrected AUROC 0.6522 >= 0.55, depth_beats_final=True, 20 layers retained (>= 5)
- Entire validated codebase: data pipeline, logit-lens mechanism, donor cache reuse, resume logic, anchor halt gate, degeneracy screen, AUROC grid, gate evaluation (15/15 tasks SDD-passed)
- Real-data verification: donor cache labels verified 10/10 against fresh GPU regenerations; REAL_MODEL verdict
- Direction of final-layer signal (inverted/anti-correlated) matches the v1 record

## Partial Results Preserved

| Metric | Value | Notes |
|--------|-------|-------|
| best_intermediate_auroc (L31, adj_kl, selection) | 0.6522 | From h-e1 llama2/triviaqa |
| final_layer_entropy_auroc_selection | 0.5928 | From h-e1 |
| final_layer_entropy_auroc_full | 0.5739 | From h-e1 |
| retained_layers | 20 | Degeneracy screen, llama2/triviaqa |
| cells_completed | 1/6 | Remaining 5 blocked by A2 halt gate (by design) |
| pass_rate | 0.667 | failed: a2_anchor_reproduction, existence_all_models_unmeasured |

## Feedback for Phase 2C (h-e1-v2)

- Do NOT reuse H_E1_REFERENCES numbers as anchors; regenerate references with the current protocol or drop the cross-provenance anchor
- Existence criterion itself passes where measured — modification_attempt=1, route_to=phase2c
- Dependents affected: h-m1 (direct), h-m3 (direct), h-c1 (direct), h-m2 (transitive)

## Lineage

```
h-e1
    └── (PIVOT: A2 anchor provenance flaw (spec), mechanism functional)
        └── h-e1-v2
```

---
*Pivot recorded at: 2026-08-05T08:10:00+00:00*
