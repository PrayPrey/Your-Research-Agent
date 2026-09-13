# Adversarial Review Summary

**Paper**: API Compatibility Is Not Gradient Compatibility: Projection-Only LoRA Fails on Mamba-130m for Classification Tasks
**Review Completed**: 2026-08-31T11:00:00Z
**Rounds Completed**: 2
**Final Status**: CONVERGED
**Persuasiveness Check**: PASSED

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis (accuracy_checker, bored_reviewer, skeptical_expert).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL    | 0     | 0        | 0         |
| MAJOR    | 9     | 9        | 0         |

**MINOR Issues**: Collected in `065_human_review_notes.md` (NOT auto-fixed)

---

## Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Strong hook with concrete experimental detail |
| Problem clear by paragraph 2? | PASS | Clear in §1.1 |
| Novelty clear by page 1? | PASS | §1.4/§1.5 contributions clear |
| Figure 1 self-explanatory? | N/A | No figures (noted as limitation; placeholders added in R1) |
| Hook avoids "X is important"? | PASS | Opens with concrete experimental narrative |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review

**Accuracy Checker Findings**:
| Category | Issues Found |
|----------|--------------|
| Claim-Evidence Mismatch | 1 ("+1.84pp within noise" lacked formal SE support) |
| Numerical Inconsistency | 0 |
| Baseline Comparison Fairness | 0 |

**Bored Reviewer Findings**:
| Category | Issues Found |
|----------|--------------|
| Engagement (no figures) | 1 MAJOR |
| Redundant section (§1.3) | 1 MAJOR |

**Skeptical Expert Findings**:
| Category | Issues Found |
|----------|--------------|
| Confidence calibration (abstract overclaims) | 1 MAJOR |
| MNLI gradient tension (partial barrier) | 1 MAJOR |
| Missing "to our knowledge" qualifier | 1 MAJOR |
| MambaPEFT hypotheses unranked | 1 MAJOR |

**Key Issues Addressed**:
1. MAJOR-ACC-1: Added binomial SE calculation (1.84pp ≈ 1.09 SE)
2. MAJOR-ENG-1: Added figure placeholders for accuracy curve and gradient path diagram
3. MAJOR-ENG-2: Condensed redundant §1.3 ("The Gap")
4. MAJOR-CRED-1: Added "partial, not total" gradient barrier paragraph in §6.1
5. MAJOR-CRED-2: Hedged "We trace" → "We attribute" + abstract confidence caveat
6. MAJOR-CRED-3: Added "to our knowledge" qualifiers
7. MAJOR-CRED-4: Ranked MambaPEFT hypotheses (checkpoint type = top candidate)

### Round 2: Numerical Verification

**Accuracy Checker Findings**:
All arithmetic verified correct (0 FATAL, 0 numerical MAJOR)

**Credibility Findings**:
| Issue | Resolution |
|-------|------------|
| "well within" SE imprecise | Changed to "within approximately one standard error" |
| Partial barrier tension with §3.4 | Added bridging sentence on symmetric noise updates |

---

## Sections Modified

| Section | Modifications |
|---------|---------------|
| Abstract | Confidence hedge on gradient barrier claim |
| Introduction §1.2 | "to our knowledge" qualifier |
| Introduction §1.3 (The Gap) | Condensed to 2-3 sentences |
| Introduction §1.4 | Hedged "We trace" → "We attribute" |
| Methodology §3 | Figure placeholder added |
| Methodology §3.4 | Figure placeholder for accuracy curves |
| Results §5.2 | Binomial SE sentence; "within approximately one SE" |
| Results §5.6 | Ranked MambaPEFT hypotheses |
| Discussion §6.1 | "Partial, not total" paragraph + bridging sentence |
| Related Work §2.5 | "to our knowledge" qualifier |

---

## Quality Improvements

- **Logical Consistency**: Improved (MNLI gradient tension resolved)
- **Numerical Accuracy**: Verified correct (all arithmetic confirmed)
- **Novelty Claims**: Refined ("first" → "to our knowledge, first")
- **Confidence Calibration**: Improved (MEDIUM confidence now explicit)
- **Persuasiveness**: Passed (strong hook, clear contributions)
- **Figure Gap**: Noted with placeholders (requires actual figure generation)

---

## Reviewer Preparation Notes

Potential remaining attack surfaces for real reviewers:

1. Zero figures in an ML venue paper
2. Single seed (seed=42 only)
3. No transformer control experiment (GPT-2 comparison missing)
4. Only 2 of 4 planned GLUE tasks completed (OOM on QNLI/QQP)
5. 40pp MambaPEFT discrepancy unresolved

Suggested responses if these are raised:
- Figures: "We plan to add architecture diagram and accuracy curve in camera-ready"
- Single seed: "Architectural failures are not seed-sensitive; identical accuracy across epochs is incompatible with any learning under any seed"
- No transformer control: "MNLI degradation below zero-shot baseline provides the cross-architecture evidence; transformer control is highest-priority follow-up experiment"
- GLUE coverage: "OOM documented; SST-2 FAIL is sufficient for MUST_WORK gate conclusion; QNLI/QQP expected to follow same pattern"
- MambaPEFT gap: "We name checkpoint type (base vs. instruction-tuned) as top candidate; exact replication with ablation is named highest-priority future work"
