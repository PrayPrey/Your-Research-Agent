# Adversarial Review Summary

**Paper:** When Adversarial Examples Improve Calibration: Construction-Method-Dependent Calibration Degradation in Open-Weight LLMs
**Review Completed:** 2026-08-25
**Rounds Completed:** 2 (R1, R2)
**Final Status:** CONVERGED
**Persuasiveness Check:** PASSED

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis (Accuracy Checker, Bored Reviewer, Skeptical Expert).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL | 0 | 0 | 0 |
| MAJOR | 6 | 6 | 0 |

**MINOR Issues:** 9 items collected in `065_human_review_notes.md` (NOT auto-fixed)

**Core research quality:** All 23+ numerical claims verified from Phase 4 source files. Zero numerical discrepancies found.

---

## Persuasiveness Assessment (Post-Revision)

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Now leads with counterintuitive finding: ANLI improved calibration (ΔECE=−0.041) vs AdvGLUE degraded it (+0.071) |
| Problem clear by paragraph 2? | PASS | §"The Problem" in Introduction is clear and well-motivated |
| Novelty clear by page 1? | PASS | Three contributions stated explicitly; gap identified precisely |
| Figure 1 self-explanatory? | UNKNOWN | External file; not verifiable from text |
| Hook avoids "X is important"? | PASS | Opens with specific finding, not generic importance claim |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review

**Accuracy Checker Findings (0 FATAL, 1 MAJOR):**
- MAJOR-ACC-001: ANLI R2 ΔΔECE framing technically correct but misleading (base ΔECE≈0; signal is chat improvement not base degradation) → RESOLVED

**Bored Reviewer Findings (0 FATAL, 1 MAJOR):**
- MAJOR-ENG-001: Abstract buried the counterintuitive hook in generic scene-setting → RESOLVED (abstract restructured to lead with ANLI paradox)

**Skeptical Expert Findings (0 FATAL, 3 MAJOR):**
- MAJOR-CRED-001: Contribution 4 (JSONL caching) presented as research contribution; actually standard engineering practice → RESOLVED (demoted to Contribution 1 implementation detail; paper now has 3 contributions)
- MAJOR-CRED-002: Abstract/Introduction overclaimed scope ("establish", "predicting") for single-model pilot study → RESOLVED ("motivate", "understanding", pilot-study qualifier added)
- MAJOR-CRED-003: H-M2 (conf_wrong < 0.70 threshold) and H-M3 (1/5 cells > 0.05 ΔECE) gate failures not disclosed → RESOLVED (new Limitation L5 added)

**Human Review Notes (R1):** 7 items (style: 2, formatting: 3, clarity: 2)

### Round 2: Numerical Verification

**Accuracy Checker Findings (0 FATAL, 1 MAJOR):**
- MAJOR-ACC-002: SST-2 excluded with claim "insufficient for ECE measurement"; Phase 4 data shows n=148 with valid ECE computed → RESOLVED (corrected to: excluded for scope/redundancy with QQP)

**Skeptical Expert Findings:** All R1 fixes verified correctly applied. No new credibility issues.

**Human Review Notes (R2):** 2 additional items

---

## Sections Modified

| Section | R1 Modifications | R2 Modifications |
|---------|-----------------|-----------------|
| Abstract | Full restructure: leading finding, scope qualifier, "motivate" language | None |
| Introduction §Contributions | 4→3 contributions; JSONL in Contribution 1; closing sentence softened | None |
| Results §5.4 | ANLI R2 ΔΔECE clarification | None |
| Discussion §Limitations | New L5 (pre-specified threshold failures) | None |
| Methodology §3.2 | None | SST-2 exclusion rationale corrected |

---

## Quality Improvements

- **Logical Consistency:** Improved (ANLI R2 ΔΔECE framing, SST-2 exclusion)
- **Numerical Accuracy:** Confirmed (23 claims verified, 0 discrepancies)
- **Novelty Claims:** Refined (scope qualified as pilot study)
- **Baseline Comparison:** N/A (measurement study)
- **Persuasiveness:** Improved (abstract restructured)
- **Transparency:** Improved (H-M2/H-M3 failures disclosed)

---

## Reviewer Preparation Notes

Potential remaining attack surfaces for real reviewers:

1. **Citation verification** — 17 citations unverified (Semantic Scholar MCP unavailable in pipeline session). High priority for Phase 6.5.1.
2. **Single-model scope** — Acknowledged in L1 and abstract (pilot study framing). Prepared response: "Multi-model evaluation feasible via H-E1 JSONL pipeline; this pilot establishes the conditional structure."
3. **Shared ANLI clean baseline** — Acknowledged in L2. Prepared response: "GLUE MNLI is methodologically correct ANLI counterpart; baseline inflation acknowledged and does not explain the direction reversal."
4. **Figure 1 quality** — Cannot verify from text; ensure external figure is clear and self-contained.
5. **SST-2 results not reported** — Now acknowledged (n=148 computed, excluded for scope). Available as supplementary if requested.

Suggested responses prepared for:
- "Why did you exclude SST-2?" → Scope; provides second binary task redundant with QQP; available on request
- "Your confidence threshold (0.616) didn't meet the 0.70 prediction" → Disclosed in L5; suggests LLM adversarial calibration degradation is smaller magnitude than vision-domain analogues
- "Your conditional framework is based on 1 model" → Pilot study framing explicit; multi-model extension is planned follow-on
