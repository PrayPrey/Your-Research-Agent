# Phase 6.5 Revision Changelog
**Generated:** 2026-03-15

## Round 1 Revisions

### Issues Addressed

| Issue ID | Severity | Description | Action |
|----------|----------|-------------|--------|
| AC-1 | FATAL | Afterburner attributed to "Liao et al." in section draft files | Corrected to "Du et al., 2025" in sections/05_results.md (2 instances) and sections/06_discussion.md (1 instance) |
| AC-2 | MAJOR | Overall Gate Table 2 Pass/Fail showed "PARTIAL" | Corrected to "FAIL" — ground truth: overall_gate_decision=FAIL |
| BR-1 | MAJOR | "independently replicates and extends" overclaims a null result | Replaced with "is consistent with and independently corroborates" in Abstract, Introduction, and Conclusion |
| BR-2 | MAJOR | Section 5.5 Projected outcomes lacked justification for inclusion | Added framing sentence explaining epistemic value for community |
| SE-2 | MAJOR | Binomial derivation presented without acknowledging elementary nature | Added sentence positioning novelty as framing application, not derivation |

### Sections Modified
- Abstract
- Section 1 Introduction
- Section 3.1 Binomial Variance Analysis
- Section 5.2 Gate Metric Results (Table 2)
- Section 5.5 Theoretical Projections
- Section 7 Conclusion
- sections/05_results.md (draft file — Liao→Du)
- sections/06_discussion.md (draft file — Liao→Du)

### Issues Deferred to Human Review
8 issues collected in 065_human_review_notes.md (categories: clarity ×3, style ×2, formatting ×3)

### Word Count Change
+~80 words (added framing sentence in 5.5 and positioning sentence in 3.1)

## Round 2 Revisions

### Issues Addressed

| Issue ID | Severity | Description | Action |
|----------|----------|-------------|--------|
| R2-FATAL-1 | MAJOR (reclassified) | Var(r_ratio) formula dropped /T factor; ρ formula missing T in denominator | Corrected to q(1-q)/T and ρ=q(1-q)/[T·q^T(1-q^T)]; recalculated example values; updated Introduction and Conclusion |
| R2-MAJOR-1 | MAJOR | "independently discover" in Sec 2.2 not updated in R1 | Replaced with "independently corroborate" |

### Sections Modified
- Section 3.1 Binomial Variance Analysis (formulas and example values)
- Section 1 Introduction (Var formula mention)
- Section 7 Conclusion (formula in Contribution 2)
- Section 2.2 Related Work (overclaiming language)

### Word Count Change
~+20 words (formula corrections and expanded example)
