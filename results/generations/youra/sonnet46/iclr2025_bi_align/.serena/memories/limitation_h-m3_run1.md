# Limitation Record: h-m3 (Run 1)

**Date:** 2026-03-15T14:11:00
**Hypothesis:** h-m3
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

h-m3: SHOULD_WORK gate failed - within-prompt Δ-cosine quality probe mechanism does not hold in HH-RLHF. All Δ = cos(H_next, A_chosen) - cos(H_next, A_rejected) < 0 for 25/27 tier×op combinations. The hypothesis was empirically falsified: H_next is systematically MORE similar to rejected responses than chosen ones. No improvement path identified via self-recovery.

## Failed Checks

- models_passing=0 (threshold: >=2)
- delta_positive=False (all deltas negative across 25/27 tier x op combinations)
- ci_lower_positive=False

## Partial Results

| Metric | Value |
|--------|-------|
| models_passing | 0 |
| ops_passing (minilm) | 0 |
| ops_passing (paraphrase) | 0 |
| ops_passing (mpnet) | 0 |
| partial_exception | OP3 prompt_projected passes for helpful-base (minilm: +0.014) |
| n_pairs_sufficient | True (14,426-35,665 per tier) |

## Experiment Summary

Within-prompt Δ = cos(H_next, A_chosen) - cos(H_next, A_rejected) was tested across 3 models × 3 tiers × 3 operationalizations (raw, length-matched, prompt-projected). Result: negative Δ in 25/27 combinations, highly significant (p≈0), large effect (Cohen d up to -0.74 for helpful-online). Reverse finding: H_next more similar to rejected than chosen in cosine space. n=31,013-35,665 pairs per tier. 31/31 unit tests pass.

Key finding: The direction of cosine similarity is REVERSED from hypothesis prediction. RLHF preference labels do NOT translate to within-prompt cosine similarity ordering of H_next embeddings. This may reflect that rejected responses are topically closer to H_next (they failed due to tone/safety, not topic relevance).

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to Phase 5 with this limitation noted.

Future research attempts should consider:
1. The specific checks that failed
2. Whether the limitation is fundamental or circumstantial - likely fundamental for this cosine-space probe approach
3. Alternative approaches: token-level or attention-based quality probes vs. sentence-embedding Δ

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL), this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-03-15T14:11:00*
*For cross-phase reference*
