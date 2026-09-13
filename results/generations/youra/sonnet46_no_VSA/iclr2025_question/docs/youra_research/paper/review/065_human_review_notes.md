# Human Review Notes — Round 1 MINOR Issues

**Paper:** Near-Orthogonal Uncertainty Signals  
**Source review:** 065_review_r1.md (Part 4: Human Review Notes)  
**Status:** Collected but NOT fixed in R1 revision (per revision rules: MINOR issues deferred to human reviewer)

---

## MINOR Issues for Human Review

### Style / Phrasing

| # | Location | Issue | Suggested Fix |
|---|----------|-------|---------------|
| S1 | Abstract, line 2 | "near-orthogonal, far below any reasonable collinearity threshold" — "any reasonable" is informal and vague | Replace with "below the pre-registered threshold of 0.70" |
| S2 | Introduction para 2 | "hallucinated outputs carry real consequences" — standard boilerplate motivation that adds no information | Consider trimming or making more specific (e.g., citing a concrete deployed-system failure) |
| S3 | Appendix A | Self-assessment "All claims supported by Results section: YES" — this was partially inaccurate in the original (abstract overclaim); now fixed in R1, so the self-assessment may be retained, but the entire self-assessment block is an unusual artifact for a research paper and may read oddly to reviewers | Consider removing or moving the self-assessment to an internal document |

### Factual / Clarification

| # | Location | Issue | Action Required |
|---|----------|-------|-----------------|
| F1 | Section 4.1 Table | Header "N samples" (original paper) referred to N=2500 prompts, which could be confused with n_samples=5 (the stochastic sampling parameter). Changed to "N prompts" in R1, but verify the table is now unambiguous given both N=2500 (prompts) and n=5 (samples per prompt) appear in the same section. | Human verify table header clarity |
| F2 | Section 5.2 Table | LR Term column: min_logprob "direction: positive" — the logistic regression is modeling correctness (h=1 presumably for hallucination). Higher min_logprob (less negative = more confident) should predict LOWER hallucination. Clarify whether the regression outcome variable is correctness=1 (judge says correct) or hallucination=1. The positive coefficient for min_logprob predicting correctness would make sense (more confident → more likely correct), but the table header says "logit(h=1)" suggesting hallucination. This directional annotation needs clarification. | Clarify outcome variable encoding in the regression table |
| F3 | References | Wang et al. (2022) Self-Consistency is listed as ICLR — the paper appeared at ICLR 2023 (as a 2022 arXiv). Verify that the venue year (2022 in citation vs ICLR 2023 publication) is correctly cited per the target venue's citation style. | Verify Wang et al. venue/year |
| F4 | References | Raghuvanshi et al. (2025) — original [UNVERIFIED] label removed in R1 revision (per MAJOR-C4 fix), but the underlying verification problem remains: this citation has no confirmed arXiv ID or venue. If a human reviewer cannot independently verify this paper before submission, the citation and the sentence in Section 2.2 referencing it should be removed. | Verify or remove Raghuvanshi et al. before submission |

### Statistical Rigor

| # | Location | Issue | Action Required |
|---|----------|-------|-----------------|
| R1 | Section 6.2 / Results 5.1 | Bootstrap 95% CIs for Pearson |r| and Spearman ρ are absent. The paper acknowledges this in Section 6.2 and flags it as planned for h-e1-v2. At N=2500, computing 10,000 bootstrap replicates takes seconds. Reviewers may ask: "if it's trivially cheap, why not include it in this paper?" Consider including before final submission. | Run bootstrap CI analysis; add to Results 5.1 and 5.3 tables |
| R2 | Throughout | The paper reports a single seed (42) result. Adding even 2-3 alternative seeds (e.g., 0, 123) to verify the near-zero |r| is seed-stable would significantly strengthen the credibility of the independence claim. | Consider adding seed robustness check |

---

---

## R2 MINOR Issues for Human Review

**Source review:** 065_review_r2.md  
**Deferred from R2 revision (per revision rules: MINOR issues not fixed by Revision Agent)**

| # | ID | Location | Issue | Suggested Fix |
|---|-----|----------|-------|---------------|
| M1 | MINOR-A1 | Section 5.3 | "same rounded magnitude" language is imprecise — both round to 0.026 only at 3 significant figures (0.02602 vs 0.02623). | Change to "both round to 0.026 at 3 significant figures" for precision. |
| M2 | MINOR-C1 | References | Gabriel (2026) arXiv:2605.05166 is a May 2026 preprint cited in an August 2026 paper. The r=0.54–0.76 value from it is load-bearing as the direct comparison point for the main finding. | Verify the preprint is accessible and the r=0.54–0.76 range is accurately transcribed before submission. |

---

## Notes on Issues Already Fixed in R1

The following items from the reviewer's Human Review Notes section were addressed in R1 (not MINOR — they were subsumed by FATAL/MAJOR fixes):

- Section 3.1 / Figure 2 vs Figure 1 inconsistency (N=2500 vs "300 data points") — **FIXED** in R1 (MAJOR-A3)
- Section 5.1 "consistent with an well-powered test" grammar error — **FIXED** in R1 (grammar fix)
- Abstract/body contradiction on "justify combining" — **FIXED** in R1 (MAJOR-E1/C2)
- The |r|=0.026 and ρ=−0.026 coincidence concern — **ADDRESSED** in R1 with explicit explanatory note in Abstract, Contributions §2, and Section 5.3
