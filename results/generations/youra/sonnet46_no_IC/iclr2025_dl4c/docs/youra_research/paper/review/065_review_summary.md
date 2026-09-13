# Adversarial Review Summary

**Paper**: Measuring Doctest Executability in Python Corpora: Feasibility of Execution-Filtered SFT Data Curation
**Review Completed**: 2026-08-04T20:20:00Z
**Rounds Completed**: 2 (R1, R2)
**Final Status**: CONVERGED
**Persuasiveness Check**: PASSED

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis
(Accuracy Checker, Bored Reviewer, Skeptical Expert).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL    | 0     | 0        | 0         |
| MAJOR    | 5     | 5        | 0         |

**MINOR Issues**: 9 collected in `065_human_review_notes.md` (NOT auto-fixed)

---

## Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | "1 in 1,000" framing is concrete and memorable |
| Problem clear by paragraph 2? | PASS | Section 1.2 frames the untested assumption clearly |
| Novelty clear by page 1? | PASS | Contributions list in Section 1.4 is crisp |
| Figure 1 self-explanatory? | PASS (description) | Adequately described; actual figure not embedded in markdown |
| Would continue reading? | YES | Bored Reviewer: attention held through results |
| Attention lost at | Section 5.2 (pre-fix) | Fixed by removing speculative 2-5pp range |
| False novelty claims found | 1 (fixed) | "First empirical characterization" scoped more precisely |
| Unfair baseline comparisons | 0 | All prior work comparisons correctly contextualized |
| Overclaims found | 2 (fixed) | "production-ready" and "recommendation is clear" recalibrated |
| Missing limitations | 0 | L1, L2, L3 all present and adequate |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review

**Accuracy Checker Findings**:
| Category | Issues Found |
|----------|--------------|
| Numerical inconsistency | 1 (30× vs 31×) |
| Dataset attribution | 0 (correctly disclosed) |

**Bored Reviewer Findings**:
| Category | Issues Found |
|----------|--------------|
| Scope (SFT pending) | 1 MAJOR |
| Hook quality | 0 |

**Skeptical Expert Findings**:
| Category | Issues Found |
|----------|--------------|
| Fragile "first" claim | 1 MAJOR |
| Compile-only benefit overclaim | 1 MAJOR |

**Key Issues Addressed in R1**:
1. MAJOR-A1: Fixed "30×" → "31×" in Section 5.1
2. MAJOR-E1: Removed speculative 2-5pp HumanEval prediction; framed H-E1 purely as future work
3. MAJOR-C1: Scoped novelty claim: "First systematic measurement of the gap between `>>>` pattern prevalence and subprocess executability in a curated Python code corpus used for LLM training"
4. MAJOR-C2: Replaced "The practical recommendation is clear" / "production-ready" with feasibility framing and H-E1 caveat

### Round 2: Numerical Verification

**Verified Against Source Files** (results.json, 04_validation.md, code/):
- All 15 quantitative claims (QC1-QC15) confirmed correct
- Phase A/B/C rates: ✓
- Gap multiplier 31×: ✓
- Token pool 0.004M / 125,000× gap: ✓
- Scan duration 129.8s: ✓
- 28/28 unit tests: ✓
- n_workers=4: ✓ (code/config.py, scanner.py)

**One MAJOR issue found and fixed:**
- MAJOR-N1: Figure 2 breakdown arithmetic — "2.1% have patterns but fail AST parsing" was wrong. Math: (310-204)/10,000 = 1.06% ≈ **1.1%**. Fixed to "1.1%". Four-category sum now verified: 96.9% + 1.1% + 1.9% + 0.1% = 100.0% ✓

---

## Sections Modified

| Section | Modifications |
|---------|---------------|
| Section 1.4 (Contribution 1) | "First systematic measurement..." (narrowed from "First empirical characterization") |
| Section 5.1 (Results table text) | "31×" corrected (from "30×"); "1.1%" corrected (from "2.1%") |
| Section 5.2 (H-E1 Pending) | Removed speculative 2-5pp range; added explicit future-work framing + heuristic-filter caveat |
| Section 6.1 (Discussion) | "feasible as a quality gate" replacing "The practical recommendation is clear" |
| Section 6.3 (Broader Impact) | "pipeline-ready" + SFT benefit caveat replacing "production-ready" |

---

## Quality Improvements

- **Logical Consistency**: Improved — 31×/1.1% arithmetic now consistent throughout
- **Numerical Accuracy**: Improved — all calculations verified against source files
- **Novelty Claims**: Refined — "first to" scoped precisely, avoids reviewer attack surface
- **Scope Framing**: Improved — H-C1 vs H-E1 boundary is now explicit and honest
- **Persuasiveness**: Improved — speculative content removed, evidence-scope match tightened

---

## Reviewer Preparation Notes

Potential remaining attack surfaces for real reviewers:

1. **H-E1 not executed** — Most likely rejection reason at main venue. Paper explicitly designates it as future work; this is the honest position. Consider (a) workshop submission while H-E1 runs, or (b) H-E1 results for camera-ready.

2. **Dataset proxy validity** — codeparrot-clean-valid vs. the-stack-dedup. Defended in Limitations L1; robust to 5× rate difference argument is present.

3. **~95% import error figure unsourced** — Currently listed in human_review_notes. If reviewers request sourcing, derive the exact percentage from error_type_distribution.png figure data before submission.

4. **n=10 executable files** — Very small sample for error analysis. Section 5.3 "ruling out file size" language should be softened (in human_review_notes) before submission.

Suggested responses:
- On H-E1: "H-E1 is provided as a complete experimental design for reproducibility; the primary contribution of this work is the corpus characterization, which demonstrates the structural infeasibility of the doctest-passing condition and motivates the compile-only comparison."
- On dataset: "We demonstrate robustness: even at 5× the observed rate (0.5%), the token pool (0.02M) remains 25,000× below the 500M target. The PIVOT conclusion holds across any reasonable dataset composition variation."
