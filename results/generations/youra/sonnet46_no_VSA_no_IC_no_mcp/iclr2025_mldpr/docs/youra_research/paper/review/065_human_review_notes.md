# Human Review Notes

> **Purpose**: Minor issues collected during adversarial review for human review. These issues do NOT block paper acceptance and were NOT auto-fixed. They improve overall quality when addressed by the human author.

**Date**: 2026-08-25T20:30:00+00:00  
**Rounds Completed**: 2 (R1, R2)  
**Status**: MINOR only — all FATAL and MAJOR issues resolved in automated revision.

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 2 |
| Clarity | 4 |
| Formatting | 2 |
| **Total** | **8** |

---

## Round 1 Issues

### Style

**MIN-004** — Introduction paragraph 1, mild redundancy  
*Location*: Introduction, first two paragraphs  
*Issue*: The phrase "no automated system" or equivalent appears in both the first sentence ("no automated system detects when this saturation occurs") and implicitly again in paragraph 2 ("the field lacks a principled, automated signal"). Consider whether one occurrence can be removed or the phrasing varied.  
*Suggested revision*: Keep the first paragraph's concrete mention; rephrase paragraph 2 to focus on the positive framing of what's needed rather than repeating the absence.

**MIN-007** — Abstract, final sentence overclaiming tone  
*Location*: Abstract, final sentence  
*Current text*: "transforming what has been a community judgment call into a principled, data-driven measurement"  
*Issue*: Strong language for a two-benchmark retrospective study. The paper does transform the qualitative concept into a quantitative one, but "transforming" may read as claiming more than two-benchmark evidence can support.  
*Suggested revision*: "establishing a principled, data-driven foundation for automated benchmark saturation monitoring"

---

### Clarity

**MIN-001** — Section 5.2, multiplier range  
*Location*: Section 5.2, sentence "The ΔAIC values versus linear (−250.50 and −194.37) are 19–25× larger than the decisive evidence threshold"  
*Issue*: After R1 fix, the multiplier ranges are now correctly separated (19–25× vs linear, 11–36× vs power-law). Verify that both multiplier ranges appear in the text and that neither is used to describe the other type of comparison. Cross-check: does Discussion Section 6.1 ("19–25 times larger than the decisive evidence threshold") correctly scope to vs-linear? It should, since the discussion focuses on the linear comparison as the primary null.

**MIN-002** — Section 5.3, human parity citation  
*Location*: Section 5.3, sentence "K ≈ 0.89 aligns with human parity on these tasks (consistent with the ~89.8% human performance reported for GLUE \citep{wang2018glue})"  
*Issue*: The original GLUE paper (Wang et al. 2018) reports average human performance of 87.1%, not 89.8%. The 89.8% figure may be from a different source or a different task subset. Verify the exact figure and citation before submission. If 89.8% is from a different paper, cite that paper; if the number cannot be precisely sourced, write "consistent with ~89% human parity on GLUE" without citing a specific percentage.

**MIN-006** — Section 5.2 / Discussion, SuperGLUE power-law asymmetry  
*Location*: Section 5.2 (Table 2 commentary) or Discussion  
*Issue*: For SuperGLUE, the power-law AIC (−372.71) is better than the linear AIC (−291.06), meaning the power-law better fits SuperGLUE than the linear model — more so than for GLUE (where logistic beats both by larger margins vs power-law). The paper doesn't discuss this asymmetry. Reviewers may ask: "Why does power-law describe SuperGLUE better than GLUE relative to linear?"  
*Suggested addition* (1–2 sentences in Results 5.2 or Discussion): "The power-law model fits SuperGLUE relatively better than GLUE (ΔAIC_pl = −112.72 vs −357.09), suggesting SuperGLUE's trajectory may retain more visible growth-phase data than GLUE's — consistent with the larger |t₀| for GLUE (−6.77m vs −2.85m), which implies more of GLUE's growth phase predated the leaderboard."

**MIN-008** (from R2) — Section 3.3, fitting bounds vs plausibility criteria  
*Location*: Section 3.3 parameter table and Table 3 (Section 5.3)  
*Issue*: After R2 fix (MAJ-005), Section 3.3 now correctly states K_lower=0.5 for fitting bounds, with a note that the post-hoc plausibility criterion is K∈[0.8, 1.0]. Table 3 in Section 5.3 uses "Plausibility Criterion: K ∈ [0.8, 1.0] ✓" — this is correct but readers seeing both [0.5, 1.05] (fitting) and [0.8, 1.0] (plausibility) without context may be confused.  
*Suggested addition*: A footnote to Table 3: "Plausibility criterion checked post-hoc; fitting bounds are K∈[0.5, 1.05] — see Section 3.3 and Appendix B." This makes explicit that both numbers refer to K but serve distinct roles.

---

### Formatting

**MIN-003** — Appendix B, H-C1 bounds comment  
*Location*: Appendix B, `bounds_lower_c1` section  
*Issue*: After R2, Appendix B now has a comment explaining H-C1-specific bounds. Verify the comment is clear and that it explicitly cross-references the main pipeline bounds for comparison.  
*Current comment added*: `# H-C1 specific: t₀ ≥ 6 months (post-launch)` — consider also noting: `# Compare: main pipeline uses t0_lower=-24 to allow pre-launch inflection`

**MIN-005** — Section 5.5, K-boundary hit rate detail  
*Location*: Section 5.5 (RQ5/H-C1), final paragraph  
*Issue*: "removing bounds increases the K-boundary hit rate from 25% to 50%, indicating that unconstrained fitting diverges for approximately half of small benchmarks" — this is a mechanistically important ablation detail but is embedded in the main results. For page economy (paper is over ICML page limit), consider moving this sentence and the ablation discussion to Appendix C, with a forward pointer in the main text.  
*Suggested revision in main*: "Bounded fitting is necessary: removing bounds doubles the K-boundary hit rate (see Appendix C for ablation details)."

---

## Recommended Priority

1. **Fix First**: MIN-002 (human parity citation verification — factual accuracy risk before submission)
2. **Fix Second**: MIN-006 (SuperGLUE/power-law asymmetry — proactively answers a foreseeable reviewer question)
3. **Fix Third**: MIN-001 (verify multiplier range scoping consistency in Discussion)
4. **Consider**: MIN-004, MIN-007 (style/tone — subjective)
5. **Optional**: MIN-003, MIN-005, MIN-008 (formatting/organization — mainly for page economy)

---

*Note: These issues do not block paper acceptance but improve overall quality and reviewer experience. Priority items 1–2 involve potential factual inaccuracies and should be addressed before submission.*
