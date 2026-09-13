# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.
> **v2.0:** These issues are NOT auto-fixed by the AI revision agent.

**Generated:** 2026-05-12T17:45:00
**Rounds Completed:** 2 (R1 + R2)
**Paper:** Adversarial Fragility and Calibration Are Anticorrelated After Capability Control

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 2 |
| Clarity | 2 |
| Formatting | 1 |
| **Total** | **5** |

---

## Round 1 Issues

### Style
1. **Section 5.4:** "visually confirms the statistical result" — passive/weak phrasing; consider "provides visual confirmation of the statistical result" (already softened in r1 revision)

### Clarity
1. **Section 3.1:** Lists "SOLAR, MPT, StableLM, Phi" as named families alongside major ones (LLaMA, Mistral, Qwen). With n=1–2 these are unusual to list at the same level. Consider grouping small-n families as "other families (SOLAR, MPT, StableLM, Phi; n=1–2 each)" in the model set description.

### Formatting
1. **Abstract:** `**Residual Instability (RI)**` uses bold markdown — confirm this renders correctly in ICML LaTeX format. May need `\textbf{Residual Instability (RI)}` in the final LaTeX version.

---

## Round 2 Issues

### Formatting
1. **Section 3.3 and throughout:** "ARC-Challenge" capitalization is inconsistent — sometimes written as "arc_challenge" (code style), sometimes "ARC-Challenge" (proper noun). Standardize to "ARC-Challenge" in prose and "arc_challenge" only in code/variable references.

### Clarity
1. **Section 5.2:** Notation for partial correlation is inconsistent — sometimes written as "ρ(RI, ECE | PC1)" and sometimes as "ρ(RI, ECE | PC1, mean_confidence)". The full conditioning set (PC1 + mean_confidence) should be stated consistently throughout, or a shorthand defined at first use: "ρ(RI, ECE | **Z**) where **Z** = {PC1, mean_confidence}".

---

## Recommended Priority

1. **Fix First:** ARC-Challenge capitalization consistency (affects all sections, easy search-and-replace)
2. **Fix Second:** Partial correlation notation standardization (affects Sections 3.6, 5.2, 6.1, 7)
3. **Consider:** Model family grouping in Section 3.1 (subjective, depends on author preference)
4. **LaTeX:** Bold formatting in abstract (handled automatically when converting to LaTeX)
5. **Optional:** "visually confirms" phrasing (very minor)

---

*Note: These issues do not block paper acceptance but improve overall quality and consistency.*
*All FATAL and MAJOR issues were resolved during the adversarial review rounds.*
