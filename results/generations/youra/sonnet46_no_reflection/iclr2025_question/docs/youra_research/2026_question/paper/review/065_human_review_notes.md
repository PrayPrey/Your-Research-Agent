# Human Review Notes

> **Purpose**: Minor issues for human review. NOT auto-fixed by AI (v2.0 policy).
> **Generated**: 2026-05-21T13:45:00
> **Rounds included**: R1

## Summary

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 1 |
| Style | 3 |
| Clarity | 3 |
| Formatting | 0 |
| **Total** | **7** |

---

## Round 1 Issues

### Typos
None identified.

### Grammar

**[MINOR-4] "89%" vs. "89.4%" inconsistency across abstract and body**
- Location: Abstract uses "89%" and "85%"; body text uses "89.4%" (derived from degenerate_fraction=0.894) and "85%" (from 0.848)
- Issue: Minor inconsistency. The abstract says "89% of TriviaQA queries and 85% of NQ queries" while the body uses "89.4%" for TriviaQA. Choose one convention and apply consistently. "89.4%" is more precise; "~89%" is acceptable shorthand for the abstract. Current mix is slightly sloppy.
- Suggested fix: Use "89.4%" and "84.8%" everywhere, or "~89%" and "~85%" in the abstract with a note that the exact values appear in Table 2.

### Style

**[MINOR-2] KLE explanation is too jargon-heavy**
- Location: Section 2 Related Work; Section 4 Key Contrasts
- Issue: "rank-1 Laplacian for 89% of queries → near-zero eigenvalue sum → systematic score inversion → AUROC well below 0.5" is technically dense. A one-sentence intuitive explanation before the technical chain would help readers not deeply familiar with spectral methods. Example: "When almost all queries produce identical samples, the similarity matrix becomes rank-1, causing KLE's von Neumann entropy to produce near-zero scores that are systematically inverted relative to uncertainty. Formally: [technical chain]."
- Suggested fix: Add 1 sentence of plain-language intuition before the technical chain.

**[MINOR-6] Oxford comma consistency**
- Location: Abstract ("token-probability and SelfCheckGPT-NLI remain valid and competitive") and various list constructions throughout
- Issue: Minor stylistic inconsistency in list formatting. Apply Oxford comma consistently per target venue style (ICML/NeurIPS typically do not mandate, but consistency within the paper matters).
- Suggested fix: Audit all list constructions and apply uniform Oxford comma policy.

**[MINOR-7] Tilde qualifier on "~2,222 lines"**
- Location: Abstract, Introduction (Section 1), and Conclusion
- Issue: The validation report (04_validation.md) confirms the exact count as 2,222 lines. Using "~" suggests approximation when the exact figure is available. Either state the exact count (2,222) or explain that the tilde reflects that line counts may vary with minor post-experiment additions.
- Suggested fix: Change "~2,222 lines" to "2,222 lines" if the count is stable, or add a brief parenthetical explanation if the tilde is intentional.

### Clarity

**[MINOR-1] "Below random chance" statistical precision**
- Location: Abstract ("below random chance on TriviaQA"); Introduction ("producing an AUROC of 0.4735: worse than random")
- Issue: SE AUROC is 0.4735 (point estimate below 0.5), which is accurate. However, the 95% CI is [0.4409, 0.5036] — the upper bound marginally exceeds 0.5. Saying "below random chance" is accurate for the point estimate but "reliably below random chance" or "statistically significantly below random" would overstate the evidence (since the CI just barely includes 0.5 from above). The anti-correlation finding is real and important — this is a nuance worth a single clarifying phrase.
- Suggested fix: Add a qualifier such as "SE AUROC point estimate 0.4735 is below random chance (0.5); the 95% CI [0.4409, 0.5036] marginally includes 0.5, consistent with a near-chance but directionally anti-correlated estimator." Do not overcorrect — the overall failure finding is unambiguous.

**[MINOR-3] Figure 3 redundancy not explained**
- Location: Section 4 Results, end of "Key Contrasts" subsection
- Issue: Figure 3 is described as "Full UQ method comparison, all six methods on both datasets." Table 1 already shows all six methods on both datasets with CIs. The paper does not explain what Figure 3 adds over Table 1 and Figure 1. A brief caption addition would reduce reviewer confusion.
- Suggested fix: Add one sentence explaining Figure 3's unique value, e.g., "Figure 3 provides a grouped bar visualization enabling direct cross-dataset comparison for each method, complementing the tabular CIs in Table 1."

**[MINOR-5] "Diversity precondition" used before defined**
- Location: Introduction paragraph 3 ("this diversity precondition is systematically violated"), before formal methodology in Section 3
- Issue: The paper uses "diversity precondition" in the Introduction before formally defining it. The R1 revised paper (06_paper_r1.md) added a parenthetical definition earlier: "(the requirement that N samples produce K>1 semantic clusters)" — but this definition appears in paragraph 3 of the Introduction. Confirm this is early enough for the reader, as the phrase "diversity precondition" first appears in the same paragraph where it is now defined.
- Suggested fix: The parenthetical in paragraph 3 of Introduction is adequate. Verify consistency if any other uses appear before this definition.

---

---

## Round 2 Issues

> **Generated**: 2026-05-21T14:15:00
> **Source Review**: paper/review/065_review_r2.md
> **Note**: These MINOR issues were identified in R2 but NOT auto-fixed. For human review only.

### [MINOR-R2-1] Style: mean_K notation inconsistency (Table 2 header vs. prose)
- **Location**: Table 2 header uses "mean_K" (uppercase K); paper prose uses "mean_k" (lowercase k) elsewhere.
- **Issue**: Minor notation inconsistency. The UQ/clustering literature uses K for number of clusters; the table header should match the prose convention and ideally clarify which convention is intended.
- **Suggested fix**: Harmonize to either "mean_K" or "mean_k" throughout. If "mean_K" is kept, add clarification that K here refers to cluster size (dominant cluster count), not number of clusters.

### [MINOR-R2-2] Clarity: Table 2 definition note verbosity
- **Location**: Section 4, Table 2 note (added in R2-FIX-001)
- **Issue**: The added note is explicit and unambiguous but somewhat long for a table footnote in an ICML-style paper. A more concise footnote style may be preferred at final submission.
- **Suggested fix**: Shorten to: "*`degenerate_fraction`: fraction of queries with K=1 (all N=10 samples in one cluster). `mean_K`: mean dominant-cluster size per query (in samples, out of N=10); mean_K=9.884 means 98.84% of samples per query fall into the largest cluster on average. Not to be confused with mean number of clusters.*"

### [MINOR-R2-3] Carry-forward [MINOR-1]: "below random chance" statistical precision
- **Location**: Abstract ("below random chance on TriviaQA"); Introduction ("worse than random")
- **Issue**: SE TriviaQA CI = [0.4409, 0.5036] marginally includes 0.5. "Below random chance" is accurate for point estimate but the CI's upper bound is 0.5036 > 0.5. Consider qualifying as "point estimate below chance" or retaining the R1 fix's "anti-correlated with correctness" language as the primary framing.
- **Suggested fix**: Already partially addressed by R1 Introduction fix. Confirm abstract phrasing is consistent with statistical precision.

### [MINOR-R2-4] Carry-forward [MINOR-4]: "89%" vs. "89.4%" inconsistency
- **Location**: Abstract uses "89%"; Section 4 and Section 6 use "89.4%"
- **Issue**: Minor inconsistency. Choose "89.4%" everywhere or "~89%" in abstract with a note.
- **Suggested fix**: Use "89.4%" in all locations for consistency, or add "~" before "89%" in abstract.

### [MINOR-R2-5] Carry-forward [MINOR-7]: tilde in "~2,222 lines"
- **Location**: Abstract, Introduction (Section 1), Conclusion
- **Issue**: Exact count 2,222 is known from 04_validation.md; tilde suggests approximation unnecessarily.
- **Suggested fix**: Remove tilde and state "2,222 lines" if count is stable, or explain tilde if intentional.

### [MINOR-R2-6] Style: NQ CI for token_prob absent from abstract
- **Location**: Abstract
- **Issue**: Abstract now states exact AUROC values for token_prob (0.6835 and 0.6551) but CIs are not mentioned. Standard practice, but the Introduction could briefly note NQ CI to strengthen robustness claim.
- **Suggested fix**: Optional — add "(95% CI: [0.5960, 0.7063])" after NQ value in Introduction or Discussion. Low priority.

**ROUND 2 HUMAN REVIEW COUNT: 6**

---

## Recommended Priority

1. **Fix First**: Grammar/consistency issues affecting precision (MINOR-4: 89% vs 89.4%)
2. **Fix Second**: Clarity issues affecting statistical interpretation (MINOR-1: "below random chance" precision)
3. **Consider**: Style improvements — KLE intuition (MINOR-2) and Figure 3 explanation (MINOR-3) improve reader experience
4. **Optional**: Minor formatting tweaks — Oxford comma (MINOR-6), tilde removal (MINOR-7), diversity precondition definition check (MINOR-5)
