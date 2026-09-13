# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-03-14T18:15:00Z
**Hypothesis:** h-e1
**Statement:** Under conditions where HH-RLHF's three helpfulness splits are analyzed, if RLHF alignment tier increases (helpful_base → helpful_rejection_sampling → helpful_online), then assistant turn PM-grounded features (instruction decomposition density, helpfulness-framing markers, politeness/safety framing) will differ significantly and monotonically across tiers.
**Final Status:** FAILED
**Gate Result:** FAIL (MUST_WORK)
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Results

- Gate Type: MUST_WORK
- Validation: FAIL (0/3 PM features pass; required 2/3)
- Max Cohen's d (PM features): 0.136 (threshold: 0.2)
- Spearman ρ (helpfulness_freq): 0.866 (passes ρ alone)
- Monotonic ordering: None observed
- Placebo inversion: sentence_length_mean d=0.735, hapax_ratio d=0.711 >> PM features

## Root Cause

Keyword-based PM-grounded feature proxies are insufficient. HH-RLHF alignment tiers differ primarily in response LENGTH and VOCABULARY DIVERSITY (not keyword-based alignment markers). This is a fundamental operationalization mismatch, not an implementation error.

## Lessons for Phase 0 Redesign

1. Use semantic features (embeddings, LLM scoring) not keyword counts
2. Response length and hapax_ratio are the dominant tier signals — investigate as alternative proxies
3. Human turns (H-M1 direction) may avoid the style-vs-content conflation problem
4. Full NLP pipeline infrastructure (273,617 turns, 28/28 tests pass) is reusable

---
*Per-hypothesis snapshot for Phase 2A reference*
