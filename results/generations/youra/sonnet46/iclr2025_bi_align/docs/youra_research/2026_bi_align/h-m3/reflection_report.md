# Reflection Report: h-m3

**Generated:** 2026-03-15T14:11:00
**Hypothesis:** h-m3
**Gate Type:** SHOULD_WORK
**Gate Result:** FAIL
**Reflection Outcome:** LIMITATION_RECORDED
**Reflection Mode:** CASE 3 (unknown reflection_type → fallback)

---

## Executive Summary

H-M3 tested whether within-prompt Δ-cosine similarity (cos(H_next, A_chosen) − cos(H_next, A_rejected)) is positive, serving as a quality probe for RLHF alignment. The SHOULD_WORK gate FAILED: 0/3 models passed. Reflection outcome is **LIMITATION_RECORDED** — the pipeline continues to Phase 5 with this limitation noted.

---

## Experiment Findings

| Dimension | Result |
|-----------|--------|
| Models passing gate | 0/3 (threshold: ≥2) |
| Tier×op combos with Δ < 0 | 25/27 |
| Direction of finding | REVERSED from hypothesis |
| Effect size | Cohen d up to -0.74 (helpful-online) |
| Statistical significance | p≈0 (all 3 models) |
| n_pairs_sufficient | True (14,426–35,665 per tier) |
| Unit tests | 31/31 passed |

### Partial Exception
- OP3 (prompt_projected) passes for helpful-base only (MiniLM: +0.014 Δ)

---

## Root Cause Analysis

**Primary Finding:** H_next is systematically MORE similar to rejected responses than chosen ones in cosine space.

**Likely Explanation:** Rejected responses likely share more topical surface content with H_next (they failed RLHF preference due to tone, safety, or helpfulness quality, not topic relevance). Chosen responses may be more semantically "elevated" — using different vocabulary, more abstract or specialized language — which makes them LESS cosine-similar to H_next in raw embedding space.

**Implication:** RLHF preference labels do NOT translate to within-prompt cosine similarity ordering. The cosine-based Δ probe is fundamentally misaligned with the preference mechanism.

---

## Decision: LIMITATION_RECORDED

- **Gate type:** SHOULD_WORK → pipeline does NOT route to Phase 0 or Phase 2A
- **Reflection type:** null (fallback to CASE 3)
- **Action:** Record limitation, continue to Phase 5
- **Modification attempts exhausted:** N/A (gate_type=SHOULD_WORK, no retries attempted)

This limitation does not block the pipeline. H-M4 (which builds on H-M3) will proceed if prerequisites allow.

---

## Lessons Learned

1. **Cosine Δ ≠ Quality Δ**: Sentence-embedding cosine similarity does not faithfully capture RLHF preference quality differences within the same prompt.
2. **Topical overlap confound**: Rejected responses may systematically share more surface vocabulary with H_next than chosen responses, creating a reverse signal.
3. **Alternative probes needed**: Token-level, attention-weighted, or classifier-based quality probes may be more appropriate than raw cosine similarity.
4. **H-M1/H-M2 not affected**: The between-conversation tier comparison (H-M1) and directional asymmetry (H-M2) findings remain valid — they use a different experimental design.

---

## Impact on Dependent Hypotheses

- **h-m4** has h-m3 as a prerequisite. h-m4 tests PM-score as predictor of C_sem^H←A. Since h-m3 is FAILED but gate_type=SHOULD_WORK (not MUST_WORK), h-m4 can still proceed — its design does not depend on h-m3's within-prompt mechanism being confirmed.

---

## Serena Memory Files Written

- `limitation_h-m3_run1.md` — Full limitation record for cross-phase learning
- `snapshot_h-m3_20260315T141100.md` — Completion snapshot for Phase 2A reference

---

## Next Action

**Proceed to Phase 5** (baseline comparison) with h-m3 LIMITATION_RECORDED.
The pipeline continues with remaining hypotheses (h-m4).

---
*Reflection completed: 2026-03-15T14:11:00*
*Step 06b → GOTO Section_7 → Section_8 → Section_9*
