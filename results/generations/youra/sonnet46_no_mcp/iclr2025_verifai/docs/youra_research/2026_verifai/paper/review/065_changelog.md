# Adversarial Review Changelog
# Phase 6.5 v2.0

**Paper**: Conditional Mechanistic Complementarity of Formal Repair Strategies for LLM-Generated Python Code
**Started**: 2026-05-10T00:00:00+00:00

---

## Round 1 Changes (R1)

**Input**: `06_paper.md`
**Output**: `06_paper_r1.md`
**Issues addressed**: 4 MAJOR (all fixed), 0 FATAL

### Change 1: Table 2 Percentage Denominator Clarification (MAJOR-001)

**Section**: 5.2 Results — Failure Mode Distribution
**Type**: Accuracy / Clarity
**Change**: Replaced vague "Percentage" column header and single-line footnote in Table 2 with explicit "% of Non-Success Samples†" column header and detailed footnote explaining:
  - Denominator is non-success samples (~367)
  - 97.5% = 358/~367 non-success samples
  - Functional count (44) uses a different eligibility pool
  - Percentages are non-additive by design
  - Priority ordering (syntax > type > functional) prevents double-counting

**Before**: Single `*Multi-label; syntax and functional strata may overlap.` footnote  
**After**: Full explanation of denomination basis and non-additive counting

---

### Change 2: Abstract INCONCLUSIVE Disclaimer Added (MAJOR-002)

**Section**: Abstract
**Type**: Accuracy / Transparency
**Change**: Added explicit sentence noting that the SynCode-Z3 complementarity experiment (h-m3) was not executed and its result is INCONCLUSIVE. Prevents reviewer confusion between the paper's title (which names "complementarity") and the paper's actual scope (FMD framework + null result).

**Added**: "Note: the SynCode-Z3 complementarity experiment (h-m3) was not executed in this pipeline run; its result remains INCONCLUSIVE."

---

### Change 3: Contribution 1 Novelty Claim Reframing (MAJOR-003)

**Section**: Introduction, Contributions list
**Type**: Novelty Claims
**Change**: Removed "We are the first to confirm" language and specific version-number-dependent novelty claim. Reframed Contribution 1 as a methodological/infrastructure contribution (reproducible Docker-free integration) rather than a priority claim.

**Before**: "We are the first to confirm a Python-native (Docker-free) integration of SynCode v0.4.16, z3-solver v4.16.0.0, and mypy v1.20.2..."  
**After**: "We demonstrate a Docker-free integration of SynCode, Z3-solver, and mypy with CodeLlama-7B... This pipeline provides a reproducible infrastructure baseline for formal repair research without Docker dependencies."

---

### Change 4: Introduction Opening Restructured (MAJOR-004)

**Section**: Introduction, paragraph 1
**Type**: Engagement / Persuasiveness
**Change**: Replaced process-first introduction opening ("When we integrated...") with finding-first opening that leads with the zero-type-error result. Now mirrors the abstract's rhetorical strategy of opening with the surprise finding before providing methodology context.

**Before**: Process-first hook ("When we integrated three principled formal repair methods...")  
**After**: Finding-first hook ("Across 2,680 completions from 134 HumanEval problems, CodeLlama-7B produces zero type errors.")

---

## Sections Modified (R1)

| Section | Modifications |
|---------|---------------|
| Abstract | Added INCONCLUSIVE disclaimer for h-m3 |
| Introduction | Restructured paragraph 1 opening; reframed Contribution 1 |
| Results (5.2) | Table 2 denominator clarification with detailed footnote |

## Issues NOT Fixed (Human Review Notes)

7 minor issues collected in `065_human_review_notes.md` — NOT auto-fixed per v2.0 protocol.

---

## Round 2 Changes (R2)

**Input**: `06_paper_r1.md`
**Output**: `06_paper_r2.md`
**Issues addressed**: 1 MAJOR (MAJOR-R2-001), 0 FATAL

### Change 5: constraint_active Accuracy Fix (MAJOR-R2-001)

**Section**: 6.2 Discussion — SynCode: Direction Without Significance
**Type**: Accuracy (validation report vs. paper claim)
**Change**: Corrected the implication that `constraint_active=True` was observed for live generation. The h-e1 validation report explicitly states `constraint_active=False`. Added a dedicated paragraph in Section 6.2 disclosing:
  - The h-e1 log recorded `constraint_active=False` for SynCode's internal enforcement flag
  - Delta_ast=0.075 was still measured despite partial constraint enforcement
  - h-m1 loaded pools (not live generation) so constraint_active was N/A for h-m1

**Before**: "The SynCode mechanism is theoretically sound and confirmed operational in h-e1" (implying full constraint enforcement)
**After**: Added explicit paragraph noting constraint_active=False, explaining partial enforcement, and confirming operationality within EXISTENCE gate scope despite this

## Round 2 Human Review Notes Added

- HRN-008: Table 2 — exact denominator for 97.5% (remove ~ approximation)
- HRN-009: constraint_active=False vs. delta_ast>0 relationship (now addressed in R2 MAJOR fix; HRN-009 retains as documentation note)

## Final Summary

**Total Revisions Made**: 5 changes across 2 rounds
**Sections Modified**: Abstract, Introduction (§1), Results (§5.2), Discussion (§6.2)
**Issues Resolved**: 5 MAJOR (0 FATAL)
**Human Review Notes**: 9 total (7 from R1, 2 from R2)
**Word Count Change**: +~150 words (R1 additions) + ~120 words (R2 §6.2 addition) ≈ +270 words total
