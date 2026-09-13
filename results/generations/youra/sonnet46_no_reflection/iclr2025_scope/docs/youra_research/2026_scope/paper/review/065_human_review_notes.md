# Human Review Notes — Phase 6.5

> Minor issues collected during adversarial review. NOT auto-fixed by AI.
> These are for human review before final submission.

Generated: 2026-05-21
Rounds contributing: R1, R2

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 2 |
| Clarity | 6 |
| Formatting | 2 |
| **Total** | **10** |

---

## Round 1 Minor Issues

**[MINOR-001] Clarity — σ rounding inconsistency**
- Location: Abstract ("σ=0.076"), Section 1 Introduction contribution bullet ("σ=0.076"), Appendix A ("Standard deviation: 0.0759")
- Description: The standard deviation of Spearman ρ is reported as "0.076" (2 decimal places) in the abstract and introduction, but as "0.0759" (4 decimal places) in Appendix A. These are the same number rounded differently. Ground truth from h-e1/04_validation.md is 0.0759.
- Recommended fix: Standardize to 0.0759 throughout for consistency with the validation report.

**[MINOR-002] Clarity — GLUE citation year**
- Location: Section 4.1 (in-text citation) and References section
- Description: The references list "Wang et al., 2018" for the GLUE paper with "EMNLP 2018" as venue. Verify there is no in-text "2019" citation. The GLUE paper (arXiv:1804.07461) was presented at ICLR 2019 Workshop and the EMNLP 2018 BlackboxNLP workshop; the standard citation year varies by source.
- Recommended fix: Verify the exact year used consistently across all in-text citations and the reference entry.

**[MINOR-003] Clarity — Temperature parameter discrepancy**
- Location: Section 3.2 (methodology: τ=0.1), h-m1/04_validation.md (config: soft_temperature=10.0)
- Description: The methodology section describes the soft KV budget mask with "τ=0.1 controls sharpness" (sigmoid relaxation). The H-M1 Phase 4 validation config shows `soft_temperature: 10.0` under `kv_budget`. These may refer to different parameters (10.0 for softmax in STE vs 0.1 for sigmoid relaxation), but this is not explicitly clarified in the paper.
- Recommended fix: Clarify in Section 3.2 or a footnote whether these are distinct hyperparameters (sigmoid temperature vs softmax temperature in STE) or if one value supersedes the other.

**[MINOR-004] Clarity — Table 2 missing data notation**
- Location: Section 5.3, Table 2 — Seeds 123 and 456 show "—" for LongBench Mean F1
- Description: The "—" entries for seeds 123 and 456 could be read as "data not collected" rather than "not evaluated at these seeds." The FATAL-001 fix adds a table footnote, but the underlying presentation issue remains: readers may still wonder if there was an execution problem for seeds 123/456.
- Recommended fix: Consider adding a column header note or brief parenthetical clarifying that LongBench F1 was evaluated only for the representative seed (42) and "—" indicates not evaluated (by design, not missing data).

**[MINOR-005] Formatting — Figure placeholder format**
- Location: Sections 5.1, 5.2, 5.3 — all figure references
- Description: Figures are referenced as `[Figure N: filename.png — Description]` in square brackets as inline text. This is a placeholder format, not standard ICML figure reference format. For a camera-ready submission, these should be proper LaTeX \figure environments.
- Recommended fix: Before submission, replace all `[Figure N: ...]` placeholder references with proper \begin{figure}...\end{figure} LaTeX environments with \caption and \label.

**[MINOR-006] Style — Repetitive phrasing**
- Location: Abstract ("consistent across every example tested") and Section 1 Introduction ("consistent across every single example we tested")
- Description: Nearly identical phrasing appears in both the abstract and introduction. While some repetition between abstract and body is acceptable, the wording is close enough to feel unintentional.
- Recommended fix: Vary the phrasing in one location, e.g., "with zero exceptions across all 100 examples" or "uniformly below the alignment threshold."

**[MINOR-007] Formatting — Figure numbering discrepancy between sections/ files and 06_paper.md**
- Location: `sections/05_results.md` vs `06_paper.md`
- Description: The sections/ intermediate files use different figure numbering than the final paper (06_paper.md). In sections/05_results.md, §5.2 refers to "Figure 4" and §5.3 refers to "Figure 5," while in 06_paper.md §5.2 uses "Figure 3" and §5.3 uses "Figure 4." This is an internal consistency issue between working files and the final paper.
- Recommended fix: Verify all section intermediate files match the final paper's figure numbering before archiving. The authoritative version is 06_paper.md (now 06_paper_r1.md).

---

## Round 2 Minor Issues

**[MINOR-R2-001] Clarity — σ rounding inconsistency (re-flagged from R2)**
- Location: Abstract/Introduction ("σ=0.076") vs Appendix A ("Standard deviation: 0.0759")
- Description: Same issue as MINOR-001 from R1. The R2 adversary review re-identified this inconsistency. Ground truth from h-e1/04_validation.md is 0.0759.
- Recommended fix: Standardize to 0.0759 throughout for consistency with the validation report.

**[MINOR-R2-002] Clarity — ρ rounding in Conclusion**
- Location: Section 7 (Conclusion), first sentence: "ρ = 0.37"
- Description: The conclusion uses the rounded value ρ=0.37, while the precise empirical value reported throughout the paper is ρ=0.3662. This inconsistency could create minor confusion. The precise value was already corrected elsewhere in R1 but the conclusion retained the rounded form.
- Recommended fix: Change "ρ = 0.37" to "ρ = 0.3662" in Section 7 (Conclusion) first sentence for consistency with other sections.

**[MINOR-R2-003] Clarity — Table 2 Seeds 123/456 LongBench "—" explanation (re-flagged from R2)**
- Location: Section 5.3, Table 2 — Seeds 123 and 456 show "—" for LongBench Mean F1
- Description: Same issue as MINOR-004 from R1. R2 adversary review re-flagged this. The "—" entries could still be interpreted as missing data rather than deliberately not evaluated. The existing table footnote addresses this partially but the table cell notation remains potentially ambiguous.
- Recommended fix: Consider changing "—" to "N/E" (not evaluated) with a legend note, or add explicit column header clarification that LongBench F1 was measured only for the representative seed (42).
