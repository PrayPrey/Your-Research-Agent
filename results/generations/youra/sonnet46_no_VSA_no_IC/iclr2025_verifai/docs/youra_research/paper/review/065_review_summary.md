# Adversarial Review Summary

**Paper**: Specification-Aligned Repair for EvalPlus Semantic Failures: Data Infrastructure and Pre-Registered Design  
**Review Completed**: 2026-08-22T21:00:00+00:00  
**Rounds Completed**: 2 (R1, R2)  
**Final Status**: CONVERGED  
**Persuasiveness Check**: PASSED (post-R1 fixes)

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis
(Accuracy Checker, Bored Reviewer, Skeptical Expert).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL | 1 | 1 | 0 |
| MAJOR | 5 | 5 | 0 |

**MINOR Issues**: 10 total collected in `065_human_review_notes.md` (NOT auto-fixed)

---

## Persuasiveness Assessment

| Check | R1 Result | R2 Result (post-fix) | Notes |
|-------|-----------|----------------------|-------|
| Abstract compelling? | FAIL | PASS | Stage 1 framing + Nosek 2018 citation made contribution category clear |
| Problem clear by paragraph 2? | PASS | PASS | SA oracle failure hook is effective |
| Novelty clear in 2 minutes? | FAIL | PASS | Narrowed contribution claims are now appropriately scoped |
| Figure 1 self-explanatory? | FAIL | FAIL | Figures are described but not embedded; minor issue collected |
| Would continue reading? | FAIL | PASS | Pre-registration tradition framing gives reviewers a category |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review (Accuracy + Engagement)

**Accuracy Checker Findings:**
| Category | Issues Found |
|----------|--------------|
| Numerical rounding (68% vs 67.6%) | 1 MAJOR |
| CEGIS citation missing from References | 1 MAJOR |
| All other numerical claims | VERIFIED (0 issues) |

**Bored Reviewer Findings:**
| Category | Issues Found |
|----------|--------------|
| Venue mismatch / no executed results | 1 FATAL |
| Abstract not compelling | Persuasiveness FAIL |
| Novelty unclear in 2 min | Persuasiveness FAIL |

**Skeptical Expert Findings:**
| Category | Issues Found |
|----------|--------------|
| "Minimal sufficient oracle" unproven | 1 MAJOR |
| "First explicit verification" overclaim | 1 MAJOR |

**Key Issues Addressed in R1:**
1. F1 (FATAL): Paper reframed as Stage 1 infrastructure + pre-registration report; Nosek 2018 cited; conclusion expanded.
2. M1: "68-84%" corrected to "67-84%" consistent with Table 2's exact value (23/34 = 67.6%).
3. M2: "Minimal sufficient oracle" → "structured, jointly motivated oracle" throughout.
4. M3: CEGIS attribution removed; counterexample concept retained without unverified citation.
5. M4: "First explicit verification" narrowed to "an explicit verification"; reframed as reusable template.

### Round 2: Numerical Verification and Credibility

**Accuracy Checker:**
All numerical values verified against ground truth — full match table:

| Claim | Paper | Ground Truth | Match |
|-------|-------|--------------|-------|
| HE+ SA fire rate | 32.4% | 0.324 | YES |
| MBPP+ SA fire rate | 16.0% | 0.160 | YES |
| HE+ failures | 34 | 34 | YES |
| MBPP+ failures | 100 | 100 | YES |
| Working set | 128 | 128 | YES |
| Recovery rate | 95.5% | 128/134=95.52% | YES |
| Solutions cache | 134/134 | 134/134 | YES |
| EvalPlus API | 34/34 + 100/100 | 34/34 + 100/100 | YES |
| Test selection | 780 | 780 | YES |
| Pytest | 5/5, 2.32s | 5/5, 2.32s | YES |
| ContrastRepair | 143/337 vs 124 | 143/337 vs 124 | YES |
| Haeri +38pp | +38pp | +38pp | YES |
| Iscan +18pp p=0.00042 | +18pp, p=0.00042 | verified | YES |
| FeedbackEval 63.6% vs 53.1% | 63.6% vs 53.1% | verified | YES |
| "67-84%" (post-fix) | 67.6% HE+, 84.0% MBPP+ | 23/34, 84/100 | YES |

**Skeptical Expert (R2):**
| Category | Issues Found |
|----------|--------------|
| Condition B mischaracterized as "Self-Refine style" | 1 MAJOR |
| All R1 fixes verified correctly applied | 0 new issues |

**Key Issue Addressed in R2:**
- R2-M1: Condition B description corrected — "Fixed reprompt (Self-Refine [Madaan 2023] motivation)" replacing "Self-Refine style"; clarifying sentence added in Section 2.1.

---

## Sections Modified

| Section | Modifications |
|---------|---------------|
| Abstract | Stage 1 framing added; "structured information" replaces "minimum information" |
| Introduction | Pre-registration tradition paragraph + Nosek 2018 citation; CEGIS attribution removed; "structured oracle" replaces "minimal sufficient oracle" |
| Section 2.1 | Condition B clarified as simplified (not full) Self-Refine |
| Section 2.4 | "First explicit" → "an explicit" |
| Section 3.1 | "68-84%" → "67-84%"; "minimum information" → "structured information" |
| Section 3.2 | CEGIS attribution removed |
| Section 4.2 | Condition B baseline label corrected |
| Section 6.1 | "minimal sufficient oracle" → "structured oracle" |
| Section 6.2 | "single random seed" added to limitations |
| Section 6.3 | Pre-registration scholarly value expanded |
| Section 7 | Conclusion expanded to name infrastructure + pre-registration as independent contributions |
| References | Clarke 2003 removed; Nosek 2018 added |

---

## Quality Improvements

- **Logical Consistency**: Improved — "minimal sufficient oracle" overclaim removed
- **Numerical Accuracy**: Improved — 67.6% rounding fixed; CEGIS citation removed
- **Novelty Claims**: Refined — scoped appropriately; no "first" claims
- **Baseline Comparison**: Contextualized — Condition B correctly distinguished from Self-Refine
- **Persuasiveness**: Improved — Stage 1 framing makes contribution category clear
- **Hook Quality**: Unchanged (already effective)

---

## Reviewer Preparation Notes

Potential remaining attack surfaces for real reviewers:

1. **No executed P1/P2 results**: Paper honestly labels all predictions INCONCLUSIVE. Prepared response: "This is a pre-registered infrastructure paper; the mechanism experiments are the companion contribution. The infrastructure and pre-registration are independently valuable (Nosek 2018)."

2. **Single seed limitation**: Acknowledged in Section 6.2. Prepared response: "seed=42 is pre-registered; reproducibility is guaranteed. Seed sensitivity is future work."

3. **Power analysis derivation (Section 5.5)**: ~24 discordant pairs not derived explicitly. Collected as minor issue. Prepared response: "Estimate assumes ~50% overlap in fixed tasks; exact value depends on correlation between B and C outcomes, which is not known pre-experiment."

4. **No OSF/AsPredicted registration**: Pre-registration is within the paper, not a third-party registry. Collected as minor issue. Prepared response: "Timestamped submission constitutes pre-registration; pipeline logs provide additional provenance."
