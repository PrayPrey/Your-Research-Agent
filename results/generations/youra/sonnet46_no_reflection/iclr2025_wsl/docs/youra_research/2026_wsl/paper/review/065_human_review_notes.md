# Human Review Notes (MINOR Issues — NOT Auto-Fixed)

> These issues do not block paper acceptance but improve quality. They require human judgment
> before fixing — some involve presentation choices (precision, figure numbering) that may
> have intentional rationale. For human review before final submission.

---

## Summary by Category

| Category | Count |
|----------|-------|
| Precision / Rounding | 1 |
| Clarity (table annotation) | 1 |
| Dangling reference | 1 |
| Phrasing (residual scope) | 1 |
| Structure / Redundancy | 1 |
| Table completeness | 1 |
| **Total** | **6** |

---

## Round 1 Issues

### Precision / Rounding

**MINOR-1** (source: P1-2)
- **Location:** Table 2, §5.2 — `overhead_ratio_std`
- **Issue:** The paper reports `overhead_ratio_std = 0.061`. The ground truth value is 0.0605. This rounds differently from the mean (1.167 = 1.1671 rounded to 4 sig figs), creating a precision inconsistency within the same table.
- **Recommendation:** Report as `0.0605` (matching ground truth precision) or `0.060` (3 sig figs, consistent with 1.167). Do not report as 0.061 unless the rounding convention is intentional and documented.
- **Risk if ignored:** Low for acceptance, but an eagle-eyed reviewer may note the inconsistency.

---

### Clarity (Table Annotation)

**MINOR-2** (source: P1-3)
- **Location:** Table 1, §5.1
- **Issue:** Table 1 shows "2,000 total" and "2,500 total" for permutation run counts. The calculation (200 checkpoints × 10 seeds = 2,000) is documented in §4 but not in the table. A reader scanning only Table 1 may not immediately understand how 200 checkpoints yield 2,000 permutation runs.
- **Recommendation:** Add a table footnote or inline annotation: "10 seeds per checkpoint." E.g., "2,000 total (10 seeds/checkpoint)" in the Permutations column. This mirrors the notation in the results section source file (05_results.md).
- **Risk if ignored:** Low — the information is available in §4; this is a clarity-only issue.

---

### Dangling Reference

**MINOR-3** (source: P1-4)
- **Location:** §5.1 — "Orbit-PE computation succeeded for all layer types with a single unified codebase (Figure 10)."
- **Issue:** The paper's Figure Captions section defines only Figures 1–8. "Figure 10" is a dangling reference — Figure 9 and Figure 10 do not appear in the figure list. This reference appears to originate from the source results file (05_results.md, which references "Figure 10, orbit_pe_success_table"), but was not carried through to the figure caption list in 06_paper.md.
- **Recommendation:** Either (a) add Figure 9 and Figure 10 definitions to the Figure Captions section (likely requires generating the missing figures), or (b) replace "(Figure 10)" with a descriptive inline reference such as "(see unified codebase statistics, h-e1/code/orbit_pe.py)" or simply remove the parenthetical if no figure exists. Do NOT leave a dangling figure reference in a submission.
- **Risk if ignored:** High for submission quality — dangling figure references are immediately caught in copy-editing and can signal incomplete manuscript preparation.

---

### Phrasing (Residual Scope)

**MINOR-4** (source: P2-2)
- **Location:** Introduction, paragraph 1 (after FATAL-1 auto-fix)
- **Issue:** After the FATAL-1 fix, the Introduction now reads: "This 43-point performance gap, observed in our evaluation of permutation-equivariant methods applied cross-architecture (see Section 5), is the puzzle we resolve." The phrase "observed in our evaluation" is accurate but may still read as slightly vague. A more precise phrasing would specify the exact method and benchmark.
- **Recommendation:** Consider: "This 43-point gap — permutation-equivariant methods (τ > 0.93 within CNN Zoo, τ < 0.50 applied zero-shot cross-architecture) — is the puzzle we resolve." This makes the τ source explicit without requiring a separate citation.
- **Risk if ignored:** Low — the FATAL-1 fix already addresses the core credibility problem. This is a style refinement.

---

### Structure / Redundancy

**MINOR-5** (source: P2-3)
- **Location:** Section 7 (Conclusion)
- **Issue:** The Conclusion enumerates the three findings (H-E1, H-M1, H-M2) in nearly the same language as §5.4 Summary Table and the Introduction contribution list (§1). The final paragraph introducing "τ_retention ≥ 0.65 remains the open question" is the only structurally distinct content.
- **Recommendation:** Consider opening the Conclusion with the broader design lesson ("symmetry group selection for weight space representations should be empirically grounded per layer type, not assumed universal") rather than re-enumerating three findings already stated twice. The three contributions could be compressed to one sentence each with the balance of the conclusion devoted to future trajectory and broader significance.
- **Risk if ignored:** Low for acceptance; high for persuasiveness. A conclusion that restates the introduction is a common reviewer criticism at top venues.

---

### Table Completeness

**MINOR-6** (source: P2-4)
- **Location:** Table 4, §5.3
- **Issue:** Table 4 shows `Var_perm = 33.84` and `Var_GL = 223.52` for Linear/FC, from which readers can compute 223.52/33.84 ≈ 6.6×. This derived GL-dominance ratio is stated in the Introduction (§1) and Discussion (§6.1) but does not appear in Table 4 or its caption. A reader scanning only the tables would not see the 6.6× figure and would need to compute it manually.
- **Recommendation:** Add a "GL/Perm dominance" column or row to Table 4, or add a table caption note: "Derived GL dominance for Linear/FC: 223.52/33.84 ≈ 6.6×."
- **Risk if ignored:** Low — the ratio is derivable from the table. This is a usability improvement.

---

## Recommended Priority

1. **Fix First (High Risk):** MINOR-3 — Dangling "Figure 10" reference. This is a submission blocker; dangling figure references indicate incomplete manuscript preparation and are caught at submission.

2. **Fix Second (Moderate):** MINOR-1 — Rounding inconsistency in Table 2 std value. Easy one-character fix; removes potential reviewer distraction.

3. **Consider (Low):** MINOR-2 — Add "10 seeds/checkpoint" annotation to Table 1. Small clarity improvement for readers who scan tables directly.

4. **Consider (Low):** MINOR-6 — Add GL/Perm dominance column to Table 4. Improves table self-sufficiency.

5. **Optional / Stylistic:** MINOR-4 — Refine "observed in our evaluation" phrasing in Introduction.

6. **Optional / Stylistic:** MINOR-5 — Differentiate Conclusion from Introduction contribution list.

---

*Notes generated by Anonymous Pipeline — Phase 6.5 (Adversarial Review)*
*Round: R1 | Date: 2026-05-21*

---

## Round 2 Issues

> These 5 issues were identified in R2 adversarial review and are deferred for human judgment.
> They do not block acceptance but improve numerical precision and presentation clarity.

### MINOR-R2-1: overhead_ratio_std rounding inconsistency (inherited from R1 MINOR-1)

- **Location:** Table 2, §5.2 — `overhead_ratio_std`
- **Issue:** The paper reports `overhead_ratio_std = 0.061`. The validation file shows 0.0605. The mean is rounded to 4 significant figures (1.167), but the std is rounded to only 3 (0.061 ≈ 0.0605). This inconsistency within the same table row was flagged in R1 as MINOR-1 and was not auto-fixed in either R1 or R2.
- **Recommendation:** Change `overhead_ratio_std` to `0.0605` (matching validation file precision) or `0.060` (3 sig figs, symmetric with 1.167). Either is acceptable; pick one and apply consistently.
- **Risk if ignored:** Low — but an eagle-eyed reviewer will note the inconsistency.

---

### MINOR-R2-2: Conv2d and Linear overhead rounded to 1.168× but validation shows 1.1671

- **Location:** Table 3 (§5.2), §7 Conclusion, Figure 7 caption
- **Issue:** The paper reports "Conv2d: 1.168×" and "Linear (FC): 1.168×". The h-m1/04_validation.md shows both values as 1.1671. The value 1.1671 rounds to 1.167 (4 sig figs), not 1.168. The discrepancy is < 0.1% but technically incorrect rounding. Note: MHA was corrected from 1.147× to 1.126× in R2, making Conv2d/Linear rounding inconsistency more noticeable by contrast.
- **Recommendation:** Change Conv2d and Linear (FC) overhead to 1.167× throughout (Table 3, §7, Figure 7 caption). Consistent with standard 4-sig-fig rounding of 1.1671.
- **Risk if ignored:** Low for scientific conclusions; moderate for numerical credibility in a precision-sensitive venue.

---

### MINOR-R2-3: "(see Section 5)" forward reference for 43-point gap is misleading

- **Location:** §1 Introduction, paragraph 1: "...observed in our evaluation of permutation-equivariant methods applied cross-architecture (see Section 5)"
- **Issue:** Section 5 covers H-E1, H-M1, and H-M2 results. None of these subsections contain a cross-architecture τ evaluation table. H-M3 (which would have generated cross-architecture τ comparisons) was blocked. A reader following the "(see Section 5)" pointer will not find a cross-architecture τ result there.
- **Recommendation:** Replace "(see Section 5)" with literature citations: "[Zhou et al., 2023; Tran-Viet et al., 2024]" or similar. Alternatively, reframe the sentence to make clear the 43-point gap is implicit from the literature rather than from this paper's Section 5.
- **Risk if ignored:** Moderate — a reviewer who follows the cross-reference will notice the referenced section does not contain the claimed evidence.

---

### MINOR-R2-4: Section 4 (Experimental Setup) engagement cliff still partially present

- **Location:** Section 4
- **Issue:** After R1 restructuring, Section 4 is improved but retains some narrative overlap with Section 3 (methodology). The multi-paragraph structure still has mild redundancy vs. the Introduction and Section 3. Not blocking, but noted as a presentation concern that was flagged as MAJOR-4 in R1 (partially addressed) and MINOR-R2-4 in R2.
- **Recommendation:** Consider further condensing Section 4 to a single short paragraph + the metrics table + the baseline disclosure note. The dataset bullets and implementation details are informative but could be merged.
- **Risk if ignored:** Low for acceptance. A tight, focused Section 4 improves reviewer experience at top venues.

---

### MINOR-R2-5: Table 4 does not display GL/Perm dominance ratio (6.6×)

- **Location:** Table 4, §5.3
- **Issue:** Table 4 shows Var_perm = 33.84 and Var_GL = 223.52 for Linear/FC, from which readers can derive 223.52/33.84 ≈ 6.6×. This derived ratio is stated prominently in §1, §6.1, and §7 but does not appear in Table 4 or its caption. A reader scanning only the tables must compute it manually. (Inherited from R1 MINOR-6.)
- **Recommendation:** Add a "GL/Perm ratio" column to Table 4 showing Conv2d: 0.57×, Linear: 6.6×. Alternatively, add a table caption note: "Derived GL dominance for Linear/FC: 223.52/33.84 ≈ 6.6×."
- **Risk if ignored:** Low — the ratio is derivable. This is a usability improvement.

---

*Notes appended by Anonymous Pipeline — Phase 6.5 (Adversarial Review)*
*Round: R2 | Date: 2026-05-21*
