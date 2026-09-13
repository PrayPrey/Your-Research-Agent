# Adversarial Review Summary (v2.0)

**Paper:** Orbit-PE: Empirical Variance Stratification in Weight Space Symmetries Across Layer Types
**Review Completed:** 2026-05-21T07:45:00Z
**Rounds Completed:** 2 (R1 + R2)
**Final Status:** CONVERGED
**Persuasiveness Check:** PASSED

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis
(accuracy_checker, bored_reviewer, skeptical_expert) in R1, and two-persona
verification (accuracy_checker, skeptical_expert) in R2.

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL    | 2     | 2        | 0         |
| MAJOR    | 6     | 6        | 0         |

**MINOR Issues:** 11 collected in `065_human_review_notes.md` (NOT auto-fixed)

---

## Persuasiveness Assessment (v2.0)

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Opens with concrete puzzle (43-pt gap) and specific result |
| Problem clear by paragraph 2? | PASS | Cross-architecture transfer failure clearly framed in §1 para 2 |
| Novelty clear by page 1? | PASS | Three empirical contributions listed clearly in §1 |
| Figure 1 self-explanatory? | PASS | Caption states Conv2d=0.637 vs Linear=0.133 explicitly |
| Hook avoids "X is important"? | PASS | Opens with specific performance numbers, not generic claim |

**Engagement cliff identified:** Section 4 (Experimental Setup) was a redundant restatement of §3 — collapsed to one focused section in R1.

---

## Round-by-Round Summary

### Round 1: Three-Persona Review (Accuracy + Engagement + Skeptical Expert)

**Accuracy Checker Findings:**
| Category | Issues Found |
|----------|--------------|
| Causal overclaim (H-M3 never ran) | FATAL-2 |
| Unsupported universal claim | FATAL-1 |
| Phase 5 baseline not disclosed | MAJOR-1 |
| GL claim scope too broad | MAJOR-2 |

**Bored Reviewer Findings:**
| Category | Issues Found |
|----------|--------------|
| Section 4 redundancy / engagement cliff | MAJOR-4 |

**Skeptical Expert Findings:**
| Category | Issues Found |
|----------|--------------|
| Citation ambiguity (2410.04207 vs 2410.04209) | MAJOR-3 |

**Key Issues Addressed (R1):**
1. **FATAL-2** — "explains why" → "is consistent with" throughout (Abstract, §6.2). Removes causal claim H-M3 would have needed to support.
2. **FATAL-1** — "43-point gap, persistent across all current methods" scoped to "observed in our evaluation of permutation-equivariant methods."
3. **MAJOR-1** — Added "Note on baseline τ comparison" in §4 disclosing Phase 5 was not conducted.
4. **MAJOR-2** — All "Linear/attention" GL dominance claims scoped to "Linear (FC) layers in CNN Zoo."
5. **MAJOR-3** — arXiv:2410.04207 removed; only 2410.04209 retained throughout.
6. **MAJOR-4** — §4 collapsed from ~400 to ~200 words; Q1/Q2/Q3 narrative restatement removed.

### Round 2: Numerical Verification and Credibility

**Accuracy Checker Findings:**
| Category | Issues Found |
|----------|--------------|
| MHA overhead discrepancy (validation file vs ground truth) | MAJOR-R2-1 |

**Skeptical Expert Findings:**
| Category | Issues Found |
|----------|--------------|
| §6.3 Linear/attention qualifier missing | MAJOR-R2-2 |

**All R1 fixes verified as correctly applied:**
- FATAL-1, FATAL-2: ✅ Fixed
- MAJOR-1, MAJOR-3: ✅ Fixed
- Forbidden claims: ✅ None present
- H-M2 FAIL: ✅ Consistently stated everywhere

**Key Issues Addressed (R2):**
1. **MAJOR-R2-1** — MHA overhead corrected from 1.147× → 1.126× (from h-m1/04_validation.md primary source). ground_truth.yaml value identified as transcription error.
2. **MAJOR-R2-2** — §6.3 hybrid encoding proposal now includes parenthetical: "(attention layers follow by inference from Linear layer GL dominance; direct Transformer Zoo measurement not conducted — see L3)".

---

## Sections Modified

| Section | R1 Modifications | R2 Modifications |
|---------|-----------------|-----------------|
| Abstract | "explains why" → "is consistent with" | — |
| §1 Introduction | Scoped 43-pt gap claim | — |
| §2.3 GL Orbit Symmetry | Consolidated arXiv citation | — |
| §4 Experimental Setup | Collapsed to ~200 words; added baseline disclosure | — |
| §5.2 H-M1 Results (Table 3) | — | MHA 1.147× → 1.126× |
| §5.3 H-M2 Results | "Linear/attention" → "Linear (FC) in CNN Zoo" for GL claims | — |
| §6.1 Discussion | Same scoping fix | — |
| §6.2 Literature Alignment | "directly explained" → "consistent with" | — |
| §6.3 Cross-Arch Implications | — | Added attention inference qualifier |
| §7 Conclusion | "explains" → "is consistent with" | MHA value updated |
| Figure 7 Caption | — | MHA 1.147× → 1.126× |

---

## Quality Improvements

- **Logical Consistency:** Improved — causal overclaims removed
- **Numerical Accuracy:** Improved — MHA overhead corrected from ground truth mismatch
- **Novelty Claims:** Refined — scoped from universal to evaluation-specific
- **Baseline Comparison:** Contextualized — Phase 5 skip disclosed explicitly
- **Persuasiveness:** Maintained — strong hook preserved, engagement cliff removed
- **Citation Integrity:** Improved — ambiguous arXiv alias resolved

---

## Reviewer Preparation Notes

Potential remaining attack surfaces for real reviewers:

1. **MHA overhead correction (1.126× vs 1.147×)**: The ground truth file had a transcription error; the validation file is the primary source. Be ready to point to h-m1/04_validation.md as evidence.
2. **H-M2 CNN-only scope**: Transformer Zoo variance decomposition not measured (L3). Ready response: "Measuring CNN Zoo provides the core stratification finding; Transformer Zoo measurement is future work enabled by the infrastructure released here."
3. **No τ_retention result**: H-M3 was blocked by H-M2's MUST_WORK failure per pre-specified design. Ready response: "The pre-registered pivot prevents expending compute when the causal precondition (permutation variance dominance) is refuted — this is methodological discipline, not scope limitation."
4. **Literature NFN τ values**: These are from the original papers (Zhou et al. 2023, Tran-Viet et al. 2024) and are verified in ground truth. No comparison table with our method exists because H-M3 never ran.

---

## Human Review Notes

11 MINOR issues collected across 2 rounds in `065_human_review_notes.md`. None block acceptance.
Categories: typo (2), grammar (3), style (3), clarity (2), formatting (1).

---

## Final Recommendation: CONDITIONAL_ACCEPT

All FATAL and MAJOR issues resolved. Paper is persuasive, numerically accurate, and appropriately scoped. The key negative result (H-M2 FAIL) is presented prominently and honestly. Limitations are comprehensive. Ready for submission pending human review of MINOR notes.
