# Phase 6.5 Adversarial Review — Changelog
# Paper: Can Existing RLHF Preference Corpora Reveal Human-to-AI Stylistic Adaptation?
# Generated: 2026-05-12

---

## Round 1 Changes (06_paper.md → 06_paper_r1.md)

### MAJOR-001 Fix: Incomplete Perplexity Row in Table 1

**Sections modified:** Methodology 3.3, Results 5.2 (Table 1), Experiments 4.1, 4.4

**Changes:**
- Removed "pending final run" note from Table 1
- Removed the incomplete β₃ row from Table 1 entirely
- Added explanation in Methodology 3.3: perplexity was applied as preprocessing filter, not model covariate
- Updated model equation in 3.3 to reflect actual specification (no Δperplexity term)
- Updated Experiments 4.4 model spec to match (removed β₃·Δperplexity from formula)
- Updated Experiments 4.1 RQ1 description to remove "fluency" from controls (now "length and prompt-level heterogeneity")
- Added Table 1 note explaining the perplexity design decision and referencing Figure 2 for stability

**Rationale:** A submitted paper cannot have placeholder rows in its main results table. The perplexity control was implemented as a data quality filter; the paper now accurately describes the executed experiment.

---

### MAJOR-002 Fix: BFGS Failure Cause Misattributed

**Sections modified:** Methodology 3.4, Experiments 4.5, Results 5.6, Conclusion

**Changes:**
- Methodology 3.4: Replaced "due to ill-conditioning in the Hessian matrix at this scale" with accurate explanation: "arising from the large number of small-sized cluster fixed effects: with 27,034 clusters at a median size of 2.8 pairs per cluster, each cluster contributes a near-rank-deficient block to the Hessian"
- Added "This is a structural issue inherent to the fixed-effects parameterization with many sparse groups, not a function of dataset size per se"
- Experiments 4.5: Updated optimizer description to accurately explain BFGS failure cause
- Results 5.6: Replaced "indicates that the dataset is not trivially small or underpowered" with accurate Hessian ill-conditioning explanation
- Conclusion: Updated BFGS description to reference "Hessian ill-conditioning from many small-sized cluster fixed effects"
- Related Work 2.4: Added brief reference to BFGS failure cause in context of scale challenges

**Rationale:** The original claim that BFGS failure "indicates dataset is not trivially underpowered" is a non-sequitur. BFGS fails due to many small clusters creating ill-conditioned Hessian blocks, not due to large n per se. This misattribution would be caught by reviewers familiar with mixed/fixed-effects optimization.

---

### MAJOR-003 Fix: Missing Effective Degrees of Freedom Discussion

**Sections modified:** Results 5.4, Discussion 6.3

**Changes:**
- Results 5.4: Added sentence clarifying that CI precision is derived from conditional likelihood accounting for cluster structure — "the effective precision is determined by 27,034 cluster-level strata rather than 80,342 nominally independent pairs"
- Updated the "rules out any OR ≥ 1.015" statement to the more precise "rules out any OR ≥ 1.011" (matching the actual CI upper bound of 1.0108)
- Discussion 6.3: Added new limitation paragraph "Cluster-level independence" noting that cross-cluster annotator pool overlap cannot be ruled out
- Results 5.4: Clarified that 27,034 clusters is the meaningful "sample size" for assessing power

**Rationale:** Power claims must acknowledge that pairs within the same cluster are not independent. The conditional likelihood accounts for this correctly, but the text should be explicit so readers understand the effective precision basis.

---

### MAJOR-004 Fix: Scope Overclaim on "Minimum Infrastructure"

**Sections modified:** Abstract, Introduction (Contributions), Discussion 6.4

**Changes:**
- Abstract: Changed "This falsification defines the minimum infrastructure required for bidirectional alignment research" → "This falsification illustrates a key infrastructure constraint for bidirectional alignment research"
- Introduction contributions (4th bullet): Changed "we derive minimum data requirements for an empirical bidirectional alignment research program" → "we illustrate a key data infrastructure constraint for bidirectional alignment research"
- Discussion 6.4: Changed "The null result in this paper is, in part, a consequence of working with the best available public data rather than the right data" — retained, but replaced "The null result...narrows the hypothesis space and defines the minimum data requirements" with "...narrows the hypothesis space and specifies what kind of data would be needed"
- Added nuance: "This constraint is not specific to HH-RLHF — any dataset that conflates response generation provenance with annotator behavioral metadata faces the same limitation"

**Rationale:** A single null result from one dataset using one proxy operationalization cannot "define minimum requirements" as if conducting a comprehensive survey. Softened to "illustrates a key constraint" which is accurate and defensible.

---

### Additional Fix: "To our knowledge" hedge on novelty claim

**Section modified:** Introduction (Contributions, 3rd bullet)

**Change:** "we provide the first empirical falsification" → "we provide, to our knowledge, the first empirical falsification"

**Rationale:** Standard scholarly hedging against undiscovered prior work. Collected as MINOR-003 but applied here as it is a single-word addition with no downside.

---

## Word Count Delta

| Section | Before | After | Delta |
|---------|--------|-------|-------|
| Abstract | ~148 | ~150 | +2 |
| Introduction | ~820 | ~830 | +10 |
| Related Work | ~720 | ~730 | +10 |
| Methodology | ~900 | ~950 | +50 |
| Experiments | ~680 | ~680 | 0 |
| Results | ~750 | ~760 | +10 |
| Discussion | ~600 | ~650 | +50 |
| Conclusion | ~380 | ~390 | +10 |
| **Total** | **~5998** | **~6140** | **+142** |

---

## Issues Addressed

| Issue ID | Severity | Status | Action |
|----------|----------|--------|--------|
| MAJOR-001 | MAJOR | RESOLVED | Table 1 perplexity row removed; methodology updated |
| MAJOR-002 | MAJOR | RESOLVED | BFGS cause corrected throughout |
| MAJOR-003 | MAJOR | RESOLVED | Effective DoF clarified; CI interpretation updated |
| MAJOR-004 | MAJOR | RESOLVED | Scope claims softened to "illustrates constraint" |
| MINOR-001 | MINOR | COLLECTED | CI precision inconsistency — in human_review_notes |
| MINOR-002 | MINOR | COLLECTED | Section 2.4 density — in human_review_notes |
| MINOR-003 | MINOR | APPLIED | "To our knowledge" hedge — applied (trivial addition) |

---

*Round 1 complete. Paper advanced to 06_paper_r1.md for Round 2 numerical verification.*

---

## Round 2 Changes (06_paper_r1.md → 06_paper_r2.md)

### MAJOR-R2-001 Fix: "Rules Out OR ≥ 1.011" Precision

**Sections modified:** Results 5.4, Discussion 6.4

**Changes:**
- Results 5.4: "rules out any OR ≥ 1.011" → "rules out OR ≥ 1.0108 at the 95% confidence level; effects as large as OR = 1.10, the minimum practical threshold set a priori, lie far outside the CI."
- Discussion 6.4: Same correction applied where same stale "OR ≥ 1.011" language appeared.

**Rationale:** The CI upper bound is 1.0108; stating "rules out ≥ 1.011" is technically correct but numerically inconsistent — 1.011 ≠ 1.0108. The corrected statement matches the reported CI upper bound exactly and adds the practical-magnitude comparison (OR = 1.10) as a separate interpretive statement.

---

### MAJOR-R2-002 Fix: β₁ Rounding Standardized to 0.0246

**Sections modified:** Abstract, Introduction (findings paragraph), Conclusion

**Changes:**
- Abstract: "β₁ = 0.025, p < 0.001" → "β₁ = 0.0246, p < 0.001"
- Introduction (findings): "β₁ = +0.025 (p < 0.001)" → "β₁ = +0.0246 (p < 0.001)"
- Conclusion: "β₁ = +0.025 (p < 0.001)" → "β₁ = +0.0246 (p < 0.001)"

**Rationale:** The actual value is 0.0246 (from ground truth and Table 1). Mixed reporting of 0.025 and 0.0246 in the same paper creates ambiguity; the two values look identical to the casual reader but differ in a way a careful reviewer will flag. Standardized to 0.0246 everywhere for consistency with Table 1.

---

## Final Status

**Total rounds:** 2 (R1 + R2)
**Total MAJOR issues:** 6 (4 from R1, 2 from R2) — all resolved
**Total FATAL issues:** 0
**Total MINOR issues:** 6 — collected in 065_human_review_notes.md
**Convergence:** MET after R2
**Recommendation:** CONDITIONAL_ACCEPT

**Final paper:** 06_paper_final.md (copy of 06_paper_r2.md)

---

## Issues Addressed — Complete Record

| Issue ID | Round | Severity | Status | Action |
|----------|-------|----------|--------|--------|
| MAJOR-001 | R1 | MAJOR | RESOLVED | Table 1 perplexity row removed; methodology updated |
| MAJOR-002 | R1 | MAJOR | RESOLVED | BFGS cause corrected throughout |
| MAJOR-003 | R1 | MAJOR | RESOLVED | Effective DoF clarified; CI interpretation updated |
| MAJOR-004 | R1 | MAJOR | RESOLVED | Scope claims softened to "illustrates constraint" |
| MINOR-001 | R1 | MINOR | COLLECTED | CI precision inconsistency — in human_review_notes |
| MINOR-002 | R1 | MINOR | COLLECTED | Section 2.4 density — in human_review_notes |
| MINOR-003 | R1 | MINOR | APPLIED | "To our knowledge" hedge — applied (trivial) |
| MAJOR-R2-001 | R2 | MAJOR | RESOLVED | OR threshold corrected to 1.0108 |
| MAJOR-R2-002 | R2 | MAJOR | RESOLVED | β₁ standardized to 0.0246 throughout |
| MINOR-R2-001 | R2 | MINOR | COLLECTED | OR precision in abstract |
| MINOR-R2-002 | R2 | MINOR | COLLECTED | CI precision in abstract (carried from R1) |
| MINOR-R2-003 | R2 | MINOR | COLLECTED | Runtime phrasing |
| MINOR-R2-004 | R2 | MINOR | COLLECTED | [UNVERIFIED] citation tags — human action required |
