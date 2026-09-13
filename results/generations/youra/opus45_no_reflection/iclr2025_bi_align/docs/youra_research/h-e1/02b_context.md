# Phase 2B Context: H-E1

**Generated:** 2026-08-18
**Source:** 02b_verification_plan.md (JIT extraction)

## Hypothesis Information

- **ID:** H-E1
- **Type:** EXISTENCE
- **Statement:** Collaboration score extracts agency signals orthogonal to preference labels (correlation < 0.7)
- **Gate:** MUST_WORK
- **Prerequisites:** None (foundation hypothesis)

## Rationale

Validates that collaboration score extracts genuinely novel signal not already captured by preference labels. If correlation >= 0.7, the signal is redundant and BiDPO reduces to weighted DPO.

## Variables

- **Independent:** Response text (chosen vs rejected from HH-RLHF)
- **Dependent:** Pearson correlation between collab_score and preference labels
- **Controlled:** Length normalization applied, same HH-RLHF split

## Verification Protocol

1. Sample 1000 random HH-RLHF pairs
2. Compute collab_score_v2 on both chosen and rejected responses
3. Calculate Pearson correlation with preference labels (chosen=1, rejected=0)
4. Pass if r < 0.7

## Success Criteria (PoC: Direction-based)

- **Primary:** Correlation < 0.7 (signal is orthogonal)
- **Secondary:** Score distribution shows meaningful variance

## Experimental Setup

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HH-RLHF (standard) | Contains preference pairs with full response text |
| **Model** | N/A (statistical analysis only) | No model training for existence check |

## Dataset Details

- **Source:** Anthropic via HuggingFace
- **Path:** Anthropic/hh-rlhf
- **Subset:** helpful-base (primary), harmless-base (secondary)

## Failure Response

- IF fails: PIVOT to orthogonalized score or revise heuristics

## Dependencies

None (foundation hypothesis)
