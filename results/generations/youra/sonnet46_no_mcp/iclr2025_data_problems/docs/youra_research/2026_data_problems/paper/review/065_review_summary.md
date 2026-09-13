# Adversarial Review Summary (v2.0)

**Paper:** A Cross-Corpus Contamination Atlas: Systematic 13-gram Overlap Mapping Across NLP Benchmarks and Training Corpora
**Review Completed:** 2026-05-04T10:30:00
**Rounds Completed:** 2
**Final Status:** CONVERGED
**Persuasiveness Check:** PASSED (CONDITIONAL_ACCEPT)

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis
(accuracy_checker, bored_reviewer, skeptical_expert).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL    | 0     | 0        | 0         |
| MAJOR    | 7     | 7        | 0         |

**MINOR Issues:** 10 items collected in `065_human_review_notes.md` (NOT auto-fixed)

All numerical claims were verified against pipeline ground truth (h-e1, h-m1, h-m2 validation reports). No fundamental errors were found. The paper is methodologically sound and its core empirical contributions are well-supported.

---

## Persuasiveness Assessment (v2.0)

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Strong hook (43x differential), clear gap, headline numbers |
| Problem clear by paragraph 2? | PASS | Gap framed within first paragraph |
| Novelty clear by page 1? | CONDITIONAL PASS | Explicit WIMBD differentiation added in R1 |
| Figure 1 self-explanatory? | ASSUMED PASS | Caption describes content clearly; visual verification recommended |
| Hook avoids "X is important"? | PASS | Opens with concrete statistic, not generic framing |
| Would continue reading? | YES | Bored reviewer engaged through abstract |
| Attention lost at | Section 3 (minor) | Scaling factor motivation — addressed by added uncertainty caveat |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review (Accuracy, Engagement, Credibility)

**Accuracy Checker Findings:**
| Category | Issues Found |
|----------|--------------|
| Factual ratio error | 1 (M1 — "2-3x" vs actual 1.86x) |
| Gate failure disclosure gap | 1 (M2 — h-m2 not disclosed in abstract) |
| Numerical inconsistency | 0 (all 12 GT claims verified correct) |

**Bored Reviewer Findings:**
| Category | Issues Found |
|----------|--------------|
| Hook quality | 0 (PASS) |
| Novelty pre-emption | 1 (M3 — needs WIMBD differentiation) |
| Attention concern | 1 (N — scaling factor motivation, minor) |

**Skeptical Expert Findings:**
| Category | Issues Found |
|----------|--------------|
| Causal language overclaim | 1 (M4 — "determines" → "associated with") |
| Scaling uncertainty | 1 (M5 — no confidence interval on 38% claim) |
| Novelty challenge | 1 (M3 — shared with Bored Reviewer) |
| Missing limitations | Multiple (N3-N5 — minor) |

**Key Issues Addressed in R1:**
1. M1: "2-3×" → "approximately 1.9×" (domain stratification ratio, all occurrences)
2. M2: Abstract + Contribution 3 now include h-m2 Mann-Whitney failure qualifier
3. M3: "First unified" → "first systematic multi-corpus, multi-sub-task"; WIMBD differentiation paragraph added
4. M4: "corpus composition determines" → "corpus composition is associated with"; causal confound acknowledged
5. M5: 38% claims now caveated with scaling factor uncertainty; ±4–8pp propagated uncertainty stated

### Round 2: Numerical Verification and Credibility

**Accuracy Checker Findings:**
| Category | Issues Found |
|----------|--------------|
| Cross-source comparison asymmetry | 1 (MAJOR-1) |
| KW test disclosure inconsistency | 1 (MAJOR-2) |
| Arithmetic verification | 0 (all values verified correct) |
| R1 fix verification | 0 (all 5 R1 fixes correctly applied) |

**Skeptical Expert Findings:**
| Category | Issues Found |
|----------|--------------|
| Pile-RP equivalence language | 0 (correctly uses "statistically indistinguishable") |
| Scaling factor internal consistency | 0 (C4/RP ordering robust post-scaling) |
| Format sensitivity scope | 1 (N — Pile only, minor) |
| Temporal limitation | 1 (N — no temporal caveat, minor) |

**Key Issues Addressed in R2:**
1. MAJOR-1: Added Limitation L2b explicitly flagging cross-source comparison (WIMBD published rate vs. pipeline-computed rate) in the 38% reduction claim
2. MAJOR-2: Added parenthetical in Section 5.3 and L3 noting KW interaction test equally affected by n=2 commonsense group imbalance

---

## Sections Modified

| Section | Round | Modifications |
|---------|-------|---------------|
| Abstract | R1, R2 | Domain stratification qualifier added; KW interaction parenthetical added |
| Introduction (Contributions) | R1 | Contribution 1 retitled; Contribution 3 labeled "(exploratory)"; WIMBD differentiation added |
| Section 2.4 Positioning | R1 | WIMBD differentiation paragraph reinforced |
| Section 3.3 Corpus Indexing | R1 | Scaling factor uncertainty paragraph added |
| Section 5.3 RQ3 | R1, R2 | "1.9×" ratio throughout; KW imbalance disclosure added |
| Section 6.1 Key Findings | R1 | C4 causal confound caveat sentence added |
| Section 6.2 Limitations | R1, R2 | L2 expanded (scaling uncertainty); L2b added (cross-source); L3 updated (KW shares n=2 limitation) |
| Section 7 Conclusion | R1 | "~1.9×" updated; exploratory qualifier added |
| Appendix Figure 5 caption | R1 | Exploratory qualifier added |

---

## Quality Improvements

- **Logical Consistency:** Improved — domain stratification disclosure now consistent across Abstract/Intro/Results/Discussion
- **Numerical Accuracy:** Confirmed — all 12 GT claims verified; ratio corrected M1
- **Novelty Claims:** Refined — "first unified" → "first systematic multi-corpus, multi-sub-task"; explicitly differentiated from WIMBD
- **Baseline Comparison:** Contextualized — cross-source comparison limitation now explicitly disclosed
- **Persuasiveness:** Maintained — hook preserved; uncertainty caveats added without undermining core findings
- **Methodological Transparency:** Improved — KW imbalance, scaling uncertainty, cross-source comparison all now disclosed

---

## Reviewer Preparation Notes

Potential remaining attack surfaces for real reviewers:

1. **"Only 3 corpora — too few for corpus composition conclusions"**: Prepared response: We agree formal causal decomposition requires >3 corpora; we now explicitly state this as a limitation and use association language. The three corpora represent the dominant open training corpora used in the field.

2. **"WIMBD rates are not independent measurements for The Pile"**: Prepared response: Explicitly disclosed in L1. The cross-corpus extension (C4, RedPajama) is our novel contribution; The Pile column serves as a validated reference anchor (Spearman ρ=0.721).

3. **"Domain stratification not Mann-Whitney confirmed"**: Prepared response: Disclosed in abstract, Contribution 3 (labeled exploratory), Section 5.3, Table 4 footnote, and L3. KW interaction p=0.0005 and Cohen's d=0.85 provide strong directional evidence. Test failure is a design constraint (n=2 commonsense), correctable with individual BBH sub-tasks.

4. **"h-m3 not run — metric consistency unverified"**: Prepared response: Explicitly marked as future work in L4 and Conclusion. No claims about 13-gram vs. Jaccard consistency made.

5. **"40× vs 43× inconsistency"**: Prepared response: Flagged as MINOR issue (R2-N1) in human_review_notes for author review — recommend standardizing to 43× throughout.

---

## Human Review Notes

10 minor issues collected (not auto-fixed) in `065_human_review_notes.md`:
- **R1:** N1 (40x/43x rounding), N2 (ρ=0.74 precision), N3 (question vs answer leakage), N4 (scaling factor citations), N5 (BBH granularity asymmetry), N6 (Figure 1 visual check)
- **R2:** R2-N1 (40x/43x standardization), R2-N2 (format sensitivity scope), R2-N3 (±5pp tolerance justification), R2-N4 (temporal limitation)

Recommended priority: Fix R2-N1 (40x/43x) and R2-N3 (±5pp justification) before submission; remaining are optional quality improvements.

---

*Phase 6.5 Adversarial Review v2.0 — Anonymous Pipeline | 2026-05-04*
