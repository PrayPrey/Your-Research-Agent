# Human Review Notes — Phase 6.5 Adversarial Review
# Minor issues collected for human reviewer (NOT auto-fixed)

Generated: 2026-03-15T13:30:00

---

## MINOR Issues for Human Review

### m1 — Statistical notation informality
**Location:** Abstract, line 1; Introduction Section 1 (C1 contributions)
**Issue:** The paper uses "p≈0" as shorthand in several places instead of citing the exact p-value.
**Recommendation:** Replace "p≈0" with "p=1.4×10⁻²⁴" in the abstract and introduction for the H-E1 and H-M1 results. This is the exact value from the validation report and verification_state.yaml.
**Example:** Abstract says "Spearman ρ=1.0, p≈0" — should be "Spearman ρ=1.0, p=1.4×10⁻²⁴"

### m2 — H-M2 negative control labeling inconsistency
**Location:** h-m2/04_validation.md labels the negative control result "FAIL (threshold: 0.01)" when the value 0.4953 clearly exceeds the threshold 0.01.
**Issue:** This is a labeling error in the validation report. The paper correctly classifies it as a PASS, but a reviewer who reads the raw validation file may challenge this.
**Recommendation:** Add a brief parenthetical clarification in Section 5.4 noting that the validation report's "FAIL" label is a threshold direction error — the value 0.4953 greatly exceeds the minimum threshold of 0.01.

### m3 — "seven corpus configurations" phrasing
**Location:** Abstract ("These effects hold robustly across seven corpus configurations"); Introduction.
**Issue:** H-E1 processed 7 configs (C0-C6). The Spearman rho is computed across C1-C5 (5 configs). C0 and C6 are included in the entropy table but not in the Spearman computation.
**Recommendation:** Clarify phrasing to "seven corpus configurations, with monotonic trend confirmed across C1-C5 (Spearman ρ=−1.0)" or similar. This is minor precision, not a factual error.

### m4 — DoReMi reference phrasing
**Location:** Introduction, Section 2.1 (Related Work)
**Issue:** Related Work cites DoReMi as showing "+6.5% few-shot accuracy improvement." This value should be verified against Xie et al. 2023 — the paper does not cite a specific source for this number.
**Recommendation:** Verify this number against the DoReMi paper (arXiv:2305.10429) before submission.

### m5 — "[Bender et al., 2021; Dolma, 2024]" citation style
**Location:** Introduction, first sentence of "The gap this creates" paragraph
**Issue:** The citation appears as "[Bender et al., 2021; Dolma, 2024]" in 01_introduction.md but as "[Bender et al., 2021; Soldaini et al., 2024]" in the main 06_paper.md Introduction. There is inconsistency between section files.
**Recommendation:** Standardize to "[Bender et al., 2021; Soldaini et al., 2024]" — Soldaini is the first author of Dolma and this matches the reference list.

---

## Notes on Auto-Fixed Issues

The following MAJOR issues were auto-fixed by the adversarial review agent:

1. **M1 (MAJOR, FIXED):** Table 2 entropy values corrected to match h-e1/04_validation.md actual experimental output. Values for C0, C2, C3, C4, C6 were wrong; C1 and C5 were correct. Relative percentages updated accordingly.

2. **M2 (MAJOR, FIXED):** DoReMi relative change claim corrected from −6.61% to −1.51%, consistent with corrected C6 entropy value.

3. **Explanatory text (REVISED):** Results section and main paper updated to contextualize the nonlinear entropy reduction pattern (modest reductions C1-C4, dramatic drop C4→C5).
