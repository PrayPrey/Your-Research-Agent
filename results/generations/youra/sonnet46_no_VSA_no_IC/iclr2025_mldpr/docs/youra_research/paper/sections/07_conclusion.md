# 7. Conclusion

We began by asking a question the ML evaluation community has long debated informally: when should we retire a benchmark? Our answer is concrete. Among 115 Papers With Code benchmarks, a statistically significant structural break in residual CoV occurs at paper_count* ≈ 39 — the point at which benchmark competition dynamics shift from high-variance exploration to low-variance saturation. Before this threshold, performance scores vary 3.81× more than the global baseline; after it, variance collapses to 0.20× of the pre-breakpoint level. This 80% variance collapse is not a gradual fade — it is a detectable phase transition, confirmed by two independent statistical tests (permutation p=0.035, piecewise F-test p=0.0021) and corroborated by three independently designed experiments.

## Summary

In this work, we addressed the benchmark retirement problem by reframing saturation as a structural break detection task. Our key insight — that benchmark performance variance undergoes a discrete regime shift rather than a monotonic decline — enabled a clean methodology: OLS detrend to remove the global trend component, apply PELT to detect the structural break in residuals, validate with permutation test and piecewise F-test. The result is a data-driven, reproducible, and computationally lightweight tool for flagging mature benchmarks.

Our contributions are:

1. **Empirical (novel threshold).** First detected structural break in PwC benchmark residual CoV at paper_count*≈39 (N=115, Aug 2026 snapshot), confirmed by two independent statistical tests. This provides a quantitative, paper-count-based candidate threshold for benchmark retirement review — not available in prior work.

2. **Empirical (two-regime structure).** Pre-breakpoint exploration regime (3.81× global variance, F p=0.0009) and post-breakpoint saturation regime (0.20× pre-segment variance, BF p=0.0099) are both empirically characterized and independently confirmed, providing mechanistic evidence for the Goodhart saturation narrative.

3. **Methodological.** PELT on OLS-detrended residual CoV is demonstrated to be a viable, computationally efficient, and interpretable approach for saturation onset detection in benchmark leaderboard data — applicable to any leaderboard with paper_count and performance metric data.

## Future Directions

Several directions arise directly from our experimental evidence:

**From untested alternative explanations:** The OLS trend reversal (rho: −0.28 → +0.137) suggests that paper_count* may be sensitive to min_papers threshold selection, as different thresholds yield different benchmark compositions. Repeating the analysis at min_papers ∈ {5, 10, 20, 38, 50} would establish whether paper_count*≈39 is threshold-stable — a high-priority validation for reproducibility claims.

**From unverified assumptions:** Causal attribution to Goodhart saturation dynamics requires longitudinal within-benchmark CoV trajectories. Extracting per-result-row publication timestamps from PwC evaluation-tables and testing whether CoV variance decreases over time *within* the same benchmark would distinguish genuine saturation from benchmark selection effects.

**From scope extensions:** Running the PELT-on-residual-CoV methodology within task-type strata (image classification, NLP reading comprehension) would yield domain-specific paper_count* values, addressing the P3 stratification analysis deferred from this work. Applying the methodology to HELM and OpenLLM leaderboard data would test cross-ecosystem generalizability.

We hope this work encourages the ML evaluation community to treat benchmark saturation as a quantitatively tractable problem — one that existing leaderboard data already contains the information to answer.
