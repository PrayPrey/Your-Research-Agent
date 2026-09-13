# Changelog: R1 Revision

**Round**: R1
**Source paper**: 06_paper.md
**Revised paper**: 06_paper_r1.md
**Date**: 2026-08-31

---

## Summary

All 8 MAJOR issues from adversarial review R1 addressed. No FATAL issues existed. 9 MINOR issues collected in human_review_notes.md (not auto-fixed).

---

## Changes by Issue

### [ACC-M1 / EXP-M3] Table 1 "FAIL (direction)" ambiguity

**Location**: Section 5.2, Table 1
**Change**: Added a "How to read Table 1" paragraph immediately before Table 1, explaining that P1's "FAIL (direction)" denotes a direction failure (τ > 0 vs. BAA prediction τ < 0), not a significance failure. Added †footnote to "FAIL (direction)" cell in Table 1 making this explicit inline.
**Text added**: ~80 words before Table 1 + one footnote line.

---

### [ACC-M2] Abstract overclaims "contrary to BAA" without causal qualification

**Location**: Abstract
**Change**: Replaced "Contrary to the BAA disengagement prediction" with "Contrary to the BAA directional prediction for prompt length in returning users — and noting that the causal chain from AI quality improvement to behavioral change is not verified in this study". Final sentence narrowed from "The BAA disengagement directional prediction is not supported" to "The BAA disengagement directional prediction for prompt length is not supported in this cohort."
**Text delta**: ~+20 words (qualification added, not padding).

---

### [ACC-M3 / EXP-M2] "First large-scale empirical test" claim unverified

**Location**: Contributions C1; Section 2.2; Conclusion Section 7
**Change**: All three instances now prefixed with "To our knowledge, based on our survey of the literature" and annotated that the claim depends on citation verification (all refs [UNVERIFIED]).
**Text delta**: ~+30 words across three locations.

---

### [ENG-M1] Section 6.2 three confounds with no discriminating evidence

**Location**: Discussion Section 6.2
**Change**: Added opening sentence explicitly stating the paper cannot discriminate among the three explanations. Added "Discriminating test:" note under each explanation specifying the concrete test needed. Retained all three explanations (not deleted — each has substantive content; cutting to two sentences would lose the specific test proposals that add value).
**Text delta**: ~+80 words.

---

### [ENG-M2] C3 framed as contribution rather than limitation

**Location**: Contributions list C3
**Change**: Reframed C3 from "Infrastructure finding" to "Documented infrastructure constraint." Language changed from "is a binding constraint" (flat assertion) to "is a binding constraint... and is reported here as a documented limitation to aid future researchers." Contribution retained in list (removing it entirely would reduce contribution count and lose the useful information for future researchers) but softened to constraint framing.
**Text delta**: ~+10 words.

---

### [EXP-M1] Causal gap not flagged in Introduction

**Location**: Introduction Section 1 (first paragraph); Limitations Section 6.3 L4; Conclusion Section 7
**Change**: 
- Introduction paragraph 1: Added "and — critically — this study contains no per-interaction measure of AI quality, so the causal chain posited by BAA (AI improves → user behavior changes) is not directly tested. The result is a directional refutation, not a causal one."
- Limitation L4: Elevated severity from MEDIUM to HIGH. Expanded to explicitly state that WildChat contains no per-interaction AI quality or model version measure, and that future work must include an AI quality covariate.
- Conclusion: Added "and — importantly — the causal chain from AI quality improvement to behavioral change has not been verified" and "it does not close the BAA empirical question."
**Text delta**: ~+100 words across three locations.

---

### [EXP-M3] FAIL/positive-finding tension — paragraph before Table 1

**Location**: Section 5.2, before Table 1
**Change**: Added explicit "How to read Table 1" paragraph resolving the apparent contradiction. This directly addresses the reviewer concern that "FAIL" and "positive finding" appear contradictory. Covered by the same fix as ACC-M1 above.
**Text delta**: Counted above in ACC-M1.

---

### Additional: 4.6× growth qualification (EXP-OC2 from expert persona)

**Location**: Section 5.3
**Change**: Qualified "4.6× growth" as "cohort-level mean growth (individual trajectories not measured)" to prevent the misreading that individual users grew 4.6×. This was listed as a major overclaim by the expert persona (EXP-OC2) even though it appeared in the MINOR list — addressed as a sentence-level qualification.
**Text delta**: ~+8 words.

---

### Additional: L5, L6 added to limitations (EXP-L2, EXP-L3)

**Location**: Section 6.3
**Change**: Added L5 (IP-hash noise: NAT/VPN) and L6 (WildChat scope: ChatGPT only) as explicit limitations. These were EXP-L2 and EXP-L3 in the review; they are substantive enough to be in the paper rather than only in human_review_notes. Date-range mismatch (EXP from ACC-M minor) also addressed in Section 3.1 with a parenthetical note.
**Text delta**: ~+60 words.

---

### Section 3.1 date range clarification

**Location**: Section 3.1 Dataset Selection
**Change**: Added parenthetical noting that the planned extraction window (Jan 2023–Dec 2024) differs from the effective analysis window (Apr 2023–Apr 2024), with a forward reference to Section 4. This addresses ACC minor issue #2 which was borderline major.
**Text delta**: ~+25 words.

---

## Issues NOT Fixed (MINOR — in human_review_notes.md)

See 065_human_review_notes.md for the 9 MINOR issues deferred to human review.

---

## Word Count Delta

Approximate: +400 words (6301 → ~6700). All additions are substantive qualifications or explanatory notes, not padding.

---

---

# Changelog: R2 Revision

**Round**: R2
**Source paper**: 06_paper_r1.md
**Revised paper**: 06_paper_r2.md
**Date**: 2026-08-31

---

## Summary

All 4 MAJOR issues from adversarial review R2 addressed. No FATAL issues existed. 5 MINOR issues collected in human_review_notes.md (not auto-fixed).

---

## Changes by Issue

### [R2-MAJOR-1] Cohort size discrepancy h-e1 vs h-e1-v2 unexplained

**Location**: Section 5.6 Internal Replication; Appendix A.1
**Change**: Section 5.6 now explicitly states both cohort sizes (h-e1: 6,769; h-e1-v2: 27,902) and explains the methodological difference: h-e1 used words × 1.3 approximation; h-e1-v2 used tiktoken cl100k_base. A sentence explains that tiktoken's subword tokenization affects per-user token counts and therefore which users satisfy the ≥3 monthly bin criterion — accounting for the larger cohort in h-e1-v2. Section 5.6 explicitly uses "methodological variants" framing. Appendix A.1 received a dedicated "Note on h-e1 vs. h-e1-v2 methodology" paragraph with the same explanation.
**Text delta**: ~+120 words across Section 5.6 and Appendix A.1.

---

### [R2-MAJOR-2] BAA directional prediction not verified against source

**Location**: Section 1 Introduction (paragraph 3, after Dell'Acqua reference)
**Change**: Added explicit hedge: "We operationalize the BAA disengagement prediction as a negative monotonic trend in prompt token count (τ < 0); this operationalization follows from BAA's core mechanism (Shen et al., 2024 [UNVERIFIED]) but the specific proxy mapping — that declining engagement manifests as shorter prompts — is our own extension of the framework and is not directly quoted from the source." This preserves the BAA framing while clearly marking where the authors' operationalization extends beyond the cited source.
**Text delta**: ~+50 words.

---

### [R2-MAJOR-3] GPT-3.5 → GPT-4 transition confound not named

**Location**: Section 6.3 Limitations (new L7)
**Change**: Added L7: "Model transition confound (severity: MEDIUM)." Named the specific confound: GPT-4 API launched March 2023 — immediately before the observation window (April 2023). Users switching from GPT-3.5-turbo to GPT-4 may have composed longer prompts for technical reasons (GPT-4's larger context window incentivizes longer, more detailed inputs). Notes that disentangling model capability effects from behavioral adaptation requires holding the AI model constant, which is impossible in WildChat-1M. Distinguished from L4 (general "no AI quality covariate") by naming the specific discrete event.
**Text delta**: ~+100 words.

---

### [R2-MAJOR-4] p-value precision inconsistency

**Location**: Table 1 caption; Abstract; Conclusion Section 7; Introduction Section 1
**Change**: Standardized to a two-tier system: Table 1 and Section 5.3 use "p = 0.0005" (precise, 4 decimal places). Abstract and Conclusion use "p < 0.001" (standard threshold notation for summary contexts). Added explanatory note to Table 1 caption: "p-values reported to 4 decimal places where available; Abstract and Conclusion use standard threshold notation (p < 0.001) for conciseness." This is consistent with common practice in ML papers (exact values in tables, threshold notation in summaries).
**Text delta**: ~+25 words (caption note).

---

## Issues NOT Fixed (MINOR — in human_review_notes.md)

See 065_human_review_notes.md for the 5 new R2 MINOR issues deferred to human review (R2-MINOR-1 through R2-MINOR-5).

---

## Word Count Delta

Approximate: +295 words (R1: ~6700 → R2: ~6995). All additions are substantive explanations of methodological differences, a named confound, and a precision note.

---

## Final Summary

**Total Revisions Made**: 12 MAJOR issues across 2 rounds
**Sections Modified**: Abstract, Introduction, Related Work 2.2, Methodology 3.1, Results 5.2, 5.3, 5.6, Discussion 6.2, 6.3, Contributions C1/C3, Conclusion, Appendix A.1
**Word Count Change**: ~6301 (original) → ~6995 (final, +694 words)

**Review Process**:
- Started: 2026-08-31T06:00:00+00:00
- Completed: 2026-08-31T07:00:00+00:00
- Rounds: 2 (R1, R2)
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert (R1); accuracy_checker, skeptical_expert (R2)

**Files Generated**:
- 06_paper_r1.md (R1 revised paper)
- 06_paper_r2.md (R2 revised paper)
- 06_paper_final.md (final paper = copy of r2 + review metadata)
- 065_review_r1.md (R1 adversary report)
- 065_review_r2.md (R2 adversary report)
- 065_review_summary.md (consolidated review report)
- 065_human_review_notes.md (14 MINOR issues for human review)
- 065_changelog.md (this file)
- 065_review_checkpoint.yaml (state tracking)

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
