# Human Review Notes
# Phase 6.5 Adversarial Review — Minor Issues for Human Review
# Paper: Can Existing RLHF Preference Corpora Reveal Human-to-AI Stylistic Adaptation?
# Generated: 2026-05-12

> **Purpose:** Minor issues collected during adversarial review for human review.
> **v2.0:** These issues are NOT auto-fixed by AI. Fix at author's discretion before submission.

**Generated:** 2026-05-12T12:30:00Z
**Updated:** 2026-05-12T13:30:00Z
**Rounds Completed:** R1, R2

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 1 |
| Clarity | 2 |
| Formatting | 0 |
| Precision | 2 |
| Citation | 1 |
| **Total** | **6** |

---

## Round 1 Issues

### Style

1. **Section 2.4 (Conditional Logit Methods in Preference Modeling)**
   - Issue: This section reads more like a textbook introduction to conditional logit than a related-work positioning statement. For an ICML audience, it may slow engagement for ML readers unfamiliar with econometrics.
   - Suggestion: Consider condensing to 2–3 sentences covering (a) what conditional logit is, (b) how prior NLP work has used it, and (c) what is novel in this application (semantic cluster FE at scale). The methodological detail belongs in Section 3.
   - Impact: Low — does not affect scientific validity, but may reduce reader engagement in Related Work.

### Clarity

1. **Abstract — CI notation precision**
   - Location: Abstract, sentence "...precisely null (β₄ ≈ 0, OR = 0.998, 95% CI [0.986, 1.011])"
   - Issue: Abstract uses 3-decimal CI bounds [0.986, 1.011] while Results section uses 4-decimal [0.9861, 1.0108]. Inconsistent precision across sections.
   - Suggestion: Use 4-decimal bounds throughout, or add note "values rounded in abstract." Either is acceptable; consistency is the goal.
   - Impact: Cosmetic — a careful reviewer may notice but it does not affect interpretation.

---

## Round 2 Issues

### Precision

1. **OR rounding in Abstract**
   - Location: Abstract, "OR = 0.998"
   - Issue: Abstract uses 3-decimal OR (0.998); Introduction and Results use 4-decimal (0.9984). Actual value: 0.9983705.
   - Suggestion: Use "OR = 0.9984" consistently throughout.
   - Impact: Cosmetic.

2. **Runtime phrasing**
   - Location: Section 4.5, "~34 minutes"
   - Issue: Tilde notation ("~34 minutes") is informal for academic writing.
   - Suggestion: Replace with "approximately 34 minutes".
   - Impact: Cosmetic.

### Clarity

1. **CI notation in Abstract (carried from R1)**
   - Already listed in Round 1 Clarity note above. Still unresolved.

### Citation — ACTION REQUIRED

1. **Five [UNVERIFIED] citation tags must be removed before submission**
   - Location: References section
   - Citations: Bai et al. 2022, Ji et al. 2023, McFadden 1974, Shen et al. 2024, Vishwarupe et al. 2026
   - Risk levels:
     - Bai et al. 2022, Ji et al. 2023, McFadden 1974: LOW (widely cited; verify links only)
     - Shen et al. 2024: MEDIUM (cited as "most comprehensive review"; confirm existence and claim)
     - **Vishwarupe et al. 2026: HIGH** — 2026 date matches paper date; substantive claim ("16 alignment benchmarks audited") depends on this. Verify it exists and is accessible. If forthcoming/preprint, mark accordingly.

---

## Recommended Priority

1. **Fix First:** Clarity issue (CI precision) — single-word fix, high visibility in abstract
2. **Consider:** Style issue (Section 2.4 density) — requires judgment call on audience

---

*Note: These issues do not block paper acceptance but improve overall quality.*
*MINOR-003 ("to our knowledge" hedge) was applied directly in R1 revision as a trivial addition.*
