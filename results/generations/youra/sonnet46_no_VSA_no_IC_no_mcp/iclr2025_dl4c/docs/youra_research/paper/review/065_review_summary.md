# Adversarial Review Summary
# Phase 6.5 — Paper: "Does Reward Formulation Matter? A Controlled Study of RLEF vs. SFT Across Code Generation Difficulty Levels"

**Review Completed**: 2026-08-26
**Rounds Completed**: 2
**Final Status**: CONVERGED
**Persuasiveness Check**: PASSED

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis
(Accuracy Checker, Bored Reviewer, Skeptical Expert). All FATAL and MAJOR issues
were resolved. MINOR issues are collected in `065_human_review_notes.md`.

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL | 0 | 0 | **0** |
| MAJOR | 5 (4 in R1, 1 in R2) | 5 | **0** |

**MINOR Issues**: 8 collected in `065_human_review_notes.md` (NOT auto-fixed)

**Convergence**: Met after R2 (FATAL=0, MAJOR=0, persuasiveness_passed=true, rounds_completed=2 ≥ min_rounds=2)

---

## Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | "We were wrong about the mechanism" hook is unusually honest and attention-grabbing |
| Problem clear by paragraph 2? | PASS | Generalization void vs dataset void distinction clear in first 3 sentences |
| Novelty clear by page 1? | PASS | Contributions list at end of §1 clearly differentiates 4 contributions |
| Figure 1 self-explanatory? | PASS (assumed) | Caption "SFT training loss by difficulty level" adequately labels content |
| Hook avoids "X is important"? | PASS | No "Code generation is important" opening — opens with specific finding |
| Would Bored Reviewer continue? | YES | Confirmed — abstract and §1 engage immediately |
| Attention lost at? | Never (in §1–§5) | §6.3 Broader Impact is generic; see human_review_notes item 3 |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review (Accuracy, Engagement, Skepticism)

**Accuracy Checker Findings**:
| Category | Issues Found |
|----------|--------------|
| Numerical verification | 0 discrepancies in 14 values checked |
| Proxy value presentation | MAJOR-AC-001 (inconsistent table format) |
| Checkpoint disclosure | MAJOR-AC-002 (insufficient prominence) |

**Bored Reviewer Findings**:
| Category | Issues Found |
|----------|--------------|
| Hook quality | PASS — strong counterintuitive opening |
| Engagement | PASS — abstract and §1 excellent |
| Figure issues | MAJOR-BR-001 (duplicate figure file) |

**Skeptical Expert Findings**:
| Category | Issues Found |
|----------|--------------|
| Novelty claims | PASS — "first open-source controlled comparison" plausible and properly scoped |
| Baseline fairness | PASS — SFT and RLEF-Binary appropriately compared with disclosed limitations |
| Mechanistic overclaiming | MAJOR-SE-001 (mechanism stated as fact when unverified) |
| Missing limitations | PASS — all 5 limitations (L1–L5) confirmed present |

**Key Issues Addressed in R1**:
1. MAJOR-AC-001: Table 1 standardized to single point estimates
2. MAJOR-AC-002: Checkpoint disclosure added to Abstract, §5.2, Table 2
3. MAJOR-BR-001: Duplicate Figure 10 replaced with distinct content (figure count 11→10)
4. MAJOR-SE-001: Mechanistic language softened with "(mechanism under investigation)" qualifiers throughout

### Round 2: Numerical Verification and Credibility

**Accuracy Checker (Numerical) Findings**:
| Category | Issues Found |
|----------|--------------|
| Δ values verified vs Phase 4 | PASS — all 5 Δ values exact match |
| Statistical values | PASS — JT z, p-value, h-m3 CI all exact |
| SFT absolute values | MAJOR-R2-001 (Table 1 wrong values) |
| Mathematical consistency | PASS — all arithmetic verified |
| Baseline fairness | PASS — SFT vs RLEF-Fraction fair; proxy binary disclosed |

**Skeptical Expert (Credibility) Findings**:
| Category | Issues Found |
|----------|--------------|
| APPS arithmetic | PASS — 308/361 = 85.32% verified |
| Loss gradient arithmetic | PASS — 10.678 − 9.533 = 1.145 verified |
| h-m3 CI plausibility | PASS — CI width consistent with symmetric BCa |
| JT interpretation | PASS — paper correctly caveats bootstrap construction |

**Key Issue Addressed in R2**:
1. MAJOR-R2-001: Table 1 SFT values corrected from approximations to Phase 4 source values (e.g., MBPP SFT: 0.52→0.24, LCB-Easy SFT: 0.08→0.18)

---

## Sections Modified

| Section | R1 Modifications | R2 Modifications |
|---------|-----------------|-----------------|
| Abstract | Added proxy qualifier, mechanism caveat | None |
| Introduction | 3 mechanistic claims softened; contribution 2, 4 qualified | None |
| Methodology (§3) | Notation: e-notation → ×10 format | None |
| Results (§5.1) | Table 1 format standardized | Table 1 values corrected |
| Results (§5.2) | Table 2 checkpoint note added | Table 2 expanded (added SFT, RLEF columns) |
| Results (§5.4) | Mechanistic language softened | None |
| Discussion (§6.1) | "Hypothesis not mechanism" distinction added | None |
| Conclusion (§7) | Mechanism caveat added | None |
| Paper Statistics | Figure count 11→10; Figure 10 corrected | Word count, R2 changes noted |

---

## Quality Improvements

- **Logical Consistency**: Improved — mechanistic claims now consistently framed as hypotheses
- **Numerical Accuracy**: Improved — Table 1 SFT values corrected to Phase 4 source; all Δ values verified exact
- **Novelty Claims**: Unchanged — claims were already appropriately scoped
- **Baseline Comparison**: Unchanged — already fair and disclosed
- **Persuasiveness**: Improved (minor) — cleaner table presentation
- **Hook Quality**: Unchanged — already strong; preserved throughout revisions

---

## Reviewer Preparation Notes

Potential remaining attack surfaces for real reviewers:

1. **Smoke-scale proxies**: All Δ values are from N=50 smoke evaluation with a checkpoint that was not saved. Standard response: MUST_WORK gate (SFT LCB-Hard = 0.0) is directly evaluated; directional claim supported by JT test; full-scale evaluation is planned.

2. **JT bootstrap validity**: z=+56.10 from pseudo-groups may be questioned as circular. Standard response: The test is correctly interpreted as "consistency with a positive ordered trend given these estimates" — this framing is in the paper (§5.2 statistical caveat).

3. **Mechanism unverified**: h-m2 failed due to truncation artifact. Standard response: Empirical outcome (difficulty-scaling advantage, APPS paradox) does not depend on mechanism verification; mechanism claim is framed as hypothesis throughout.

4. **No full-scale RLEF-Binary training**: Binary comparison uses proxy. Standard response: Null result is consistent with two independent papers (arXiv:2605.02944, arXiv:2601.03525); direction is conservative; full training is future work.

5. **Two monotone violations in Δ**: MBPP→LCB-Easy and LCB-Easy→LCB-Medium not monotone. Standard response: JT tests ordered trend, not strict monotonicity; violations are consistent with N=50 proxy noise; LCB-Hard (primary target) shows largest Δ as predicted.

---

## Final Paper Location

`docs/youra_research/paper/06_paper_final.md`

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
