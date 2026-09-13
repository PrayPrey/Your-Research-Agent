# Phase 6.5 Adversarial Review — Changelog
# Generated: 2026-05-03T14:20:00Z

---

## Round 1 (R1) Revisions — 2026-05-03T14:20:00Z

**Source paper:** `06_paper.md`
**Revised paper:** `06_paper_r1.md`
**Issues addressed:** MAJOR-001, MAJOR-002, MAJOR-003, MAJOR-004

---

### MAJOR-001: Figure Captions Added; Figure Numbering Resolved

**Problem:** Paper referenced 5 figures by filename path only (e.g., "figures/fig1_coefficient_comparison.png") with no formal captions. Figure numbering was inconsistent — "Figure 3" was used for two different figures (feature stability and discriminant validity).

**Fix applied:**
- Added formal caption blocks for all 5 figures (Figure 1–5) immediately after each figure reference in §5.1, §5.2, §5.3
- Resolved numbering: Figure 1 = coefficient comparison, Figure 2 = dose_response, Figure 3 = feature stability, Figure 4 = discriminant validity, Figure 5 = topic balance
- Captions include content description, dataset/n info, and source file reference

**Sections modified:** §5.1, §5.2, §5.3

---

### MAJOR-002: Near-Chance AUC Reported and Explained

**Problem:** Model AUC values (early_auc=0.4952, late_auc=0.5111) were present in verification_state.yaml but not reported in the paper. A skeptical reviewer would challenge the validity of coefficient estimates from near-chance classifiers.

**Fix applied:**
- Added AUC column to Table 1 (showing overall early=0.495, late=0.511)
- Added "Note on model AUC" paragraph in §5.1 explaining:
  - Near-chance AUC is expected for noisy individual preference labels
  - Does not undermine coefficient-level inference under large-n logistic regression
  - Coefficient estimates and bootstrap CIs remain valid even when marginal discrimination is weak

**Sections modified:** §5.1, Table 1

---

### MAJOR-003: Multiple Comparisons Note Added

**Problem:** Three hypothesis tests (H-E1, H-M1, H-M2) conducted without explicit acknowledgment of family-wise error rate. Reviewers would note absence of cross-test correction.

**Fix applied:**
- Added "Multiple comparisons" paragraph to §4.3 noting:
  - Family-wise Bonferroni threshold: α = 0.05/3 ≈ 0.017
  - Primary positive result (H-M1 p=2.05×10⁻⁵) well below corrected threshold
  - H-M2 CI non-overlap criterion does not require p-value correction

**Sections modified:** §4.3

---

### MAJOR-004: AAI Incompleteness Explicitly Flagged in Abstract and Contributions

**Problem:** Abstract described AAI as "a composite instrument that measures directional stylistic adaptation" without noting that component 3 (behavioral divergence, H-M3/H-M4) was not yet executed. Introduction contributions did not flag this incompleteness.

**Fix applied:**
- Abstract: After "We validate the first two components on HH-RLHF and WebGPT," added "(components 1–2 validated in this paper; the reward-model behavioral divergence component is specified but not yet executed — see §6.2)"
- Introduction §1 "Our approach": Added explicit "(3) behavioral divergence... We validate the first two components... component (3) is fully specified for future work (see §6.2)"
- Contribution 2: Added note "these results validate AAI components 1 and 2; the behavioral divergence component (H-M3/H-M4) is specified but not yet executed"
- Conclusion: Updated to "validating AAI components 1–2"

**Sections modified:** Abstract, §1 (Our approach, Contributions), §7

---

### Word Count Delta

| Version | Approx. Words |
|---------|--------------|
| 06_paper.md (original) | ~4,850 |
| 06_paper_r1.md (revised) | ~6,100 |
| Delta | +~1,250 |

**Note:** Increase primarily from added figure captions (~5 × ~80 words) and explanatory paragraphs for MAJOR-002/003/004.

---

### Sections Modified

| Section | Change |
|---------|--------|
| Abstract | MAJOR-004: AAI incompleteness note added |
| §1 Introduction | MAJOR-004: "Our approach" and Contributions updated |
| §4.3 Evaluation Metrics | MAJOR-003: Multiple comparisons paragraph added |
| §5.1 Results H-M2 | MAJOR-001: Figure 1 caption added; MAJOR-002: AUC added to Table 1 + explanatory note |
| §5.2 Results H-M1 | MAJOR-001: Figure 2, Figure 4 captions added; design reminder added |
| §5.3 Results H-E1 | MAJOR-001: Figure reference clarified |
| Table 1 | MAJOR-002: AUC column added |
| §7 Conclusion | MAJOR-004: "AAI components 1–2" language |

---

### MINOR Issues (NOT fixed — see 065_human_review_notes.md)

- MINOR-001: §5.2 clarity — "between-group tercile proxy" not restated
- MINOR-002: §5.2 formatting — informal figure path in body text
- MINOR-003: Abstract style — opens with generic framing

*Note: MINOR-001 was partially addressed in R1 (added "(between-group tercile design; worker IDs absent from public release)" reminder in §5.2 result sentence).*

---

## Round 2 (R2) Revisions — 2026-05-03T14:45:00Z

**Source paper:** `06_paper_r1.md`
**Revised paper:** `06_paper_r2.md`
**Issues addressed:** MAJOR-005, MINOR-004

---

### MAJOR-005: H-M1 Provenance Note Added

**Problem:** `h-m1/04_validation.md` report table shows β_exposure=0.0000 and tercile F=33.226 (pre-fix run), while the paper cites β_exposure=0.041 and F=82.92 from `h-m1/04_checkpoint.yaml` (post-fix run). This documentation gap creates a reproducibility concern — the cited numbers cannot be traced to the validation report without checkpoint access.

**Fix applied:** Added *Provenance note* paragraph in §5.2 immediately after the β_exposure equation, explaining that:
- Values are from the post-mock-data-fix run in `h-m1/04_checkpoint.yaml`
- The `04_validation.md` table reflects the pre-fix run
- Synthetic worker ID generation was removed before the final run

**Sections modified:** §5.2

---

### MINOR-004: CI Half-Width Multiplier Corrected

**Problem:** §5.1 stated "approximately 2.6× the early-round CI half-width" — actual calculation gives ≈4× (CI half-width ≈0.019; Δβ_L=0.080; ratio≈4.3).

**Fix applied:** Changed "approximately 2.6×" to "approximately 4× the early-round CI half-width of ≈0.019."

**Sections modified:** §5.1 observation 1

---

### Word Count Delta (R2)

| Version | Approx. Words |
|---------|--------------|
| 06_paper_r1.md | ~6,100 |
| 06_paper_r2.md | ~6,150 |
| Delta | +~50 |

---

## Final Summary

**Total Revisions Made:** 6 issues addressed (4 MAJOR in R1, 1 MAJOR + 1 MINOR in R2)
**Sections Modified:** Abstract, §1, §4.3, §5.1, §5.2, Table 1
**Word Count Change:** ~4,850 → ~6,150 (+~1,300)

**Review Process:**
- Started: 2026-05-03T14:00:00Z
- R1 completed: 2026-05-03T14:20:00Z
- R2 completed: 2026-05-03T14:45:00Z
- Rounds: 2
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated:**
- 06_paper_r1.md (R1 revised paper)
- 06_paper_r2.md (R2 revised paper — final)
- 06_paper_final.md (copy of R2 — see Step 7)
- 065_review_r1.md (R1 adversarial review)
- 065_review_r2.md (R2 adversarial review)
- 065_review_summary.md (consolidated summary)
- 065_human_review_notes.md (MINOR issues for human review)
- 065_changelog.md (this file)

**Next Phase:** Phase 6.5.1 (Overleaf LaTeX/PDF generation)
