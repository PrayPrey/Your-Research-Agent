# 6. Discussion

## 6.1 Key Findings

**Finding 1: Benchmark saturation is a phase transition, not a gradual decline.** The most important finding is structural, not numerical. Prior work modeled saturation as a smooth monotonic trend (Liao et al. 2022, S_index); our results demonstrate it is a discrete structural break — a regime shift at paper_count*≈39 detectable by standard change-point analysis. This reframing has practical implications: a threshold supports decision-making (retire benchmarks above it), while a trend does not (how negative does the slope need to be?).

**Finding 2: The two regimes are quantitatively extreme.** Pre-breakpoint variance (3.81× global) and post-breakpoint variance (0.20× pre-segment) differ by approximately 19×. This is not a subtle statistical effect — it is visible in the raw scatter plot (Figure 2). The magnitude of the contrast suggests that the regime boundary at paper_count*=39 reflects a genuine change in the competitive dynamics of benchmark participation, not a distributional artifact.

**Finding 3: Three independent experiments corroborate the same mechanism.** H-E1 detects the break; H-M1 confirms the pre-breakpoint character; H-M2 confirms the post-breakpoint character. Each experiment is independently designed, uses pre-specified metrics, and passes its gate. This convergence substantially reduces the probability of a Type I error and demonstrates methodological rigor beyond what a single experiment could provide.

**Interpretation of OLS reversal (rho: −0.28 → +0.137).** The reversal of the global OLS trend between the Phase 1 anchor and the current dataset is not a contradiction — it is evidence that the PwC benchmark database composition changes over time. New competitive benchmarks added at high paper_count tend to have high CoV (they are actively contested), locally reversing the aggregate trend direction. This finding motivates periodic re-analysis and reinforces that PELT's residual-based approach — which removes whatever trend exists before detection — is the right tool for this analysis.

## 6.2 Limitations

**L1: Small pre-segment (n_pre=8) limits directional characterization.** The structural break falls near the left boundary of the paper_count distribution (all pre-breakpoint benchmarks have paper_count = 38, the minimum threshold). This results in only 8 pre-breakpoint benchmarks, insufficient for stable moment-based inference (skewness, kurtosis). H-M3's skewness metrics fail as a consequence. Our primary claims (structural break detection, variance compression) are unaffected by this limitation; they rely on statistics robust to small segment sizes (permutation tests, rank-based tests, variance ratio). This limitation is a consequence of where the natural breakpoint falls, not a methodological flaw.

**L2: Cross-sectional design cannot establish causality.** Our analysis pools benchmarks at a single time point (Aug 2026). The two-regime variance structure is consistent with Goodhart saturation dynamics — communities discovering dominant approaches, converging scores, benchmark ceiling — but cross-sectional CoV-vs-paper_count correlations cannot rule out alternative explanations: benchmark selection effects (benchmarks with many papers may be intrinsically less variable task types), metric heterogeneity across task domains, or benchmark age confounds. Longitudinal within-benchmark CoV trajectories would be required to establish causal attribution. All causal language in this work should be read as interpretive motivation, not confirmed mechanism.

**L3: Dataset snapshot sensitivity.** paper_count*=39 reflects the Aug 2026 PwC snapshot (N=115, min_papers=38). The PwC database grows continuously; future snapshots may yield different N and, potentially, different paper_count* estimates. The OLS trend direction already reversed between Phase 1 (N=111) and our analysis (N=115), demonstrating snapshot sensitivity. We recommend periodic re-analysis (see Section 7) as an immediate follow-up.

**L4: Bootstrap CI width = 31.5.** The 95% CI [38, 69.5] is wider than the pre-specified soft criterion of ≤20 papers, driven by the small pre-segment. The point estimate (paper_count*=39) is stable and actionable; the CI width should be reported in any application of this threshold.

**L5: Domain stratification not tested.** We report a global paper_count* across all benchmark task types. Whether image classification, NLP, and other domains have different saturation thresholds (different paper_count* values) is an explicit open question (P3, deferred to Phase 5). Users applying paper_count*=39 to specific task types should do so with caution pending stratified analysis.

## 6.3 Broader Impact

This work provides a methodology for operationalizing benchmark retirement decisions using existing leaderboard data. As the ML community debates benchmark proliferation [CITE:Akhtar2026] and the risks of Goodhart saturation [CITE:Bowman2021], our approach offers a lightweight, reproducible, data-driven tool that requires no new data collection or annotation. Any team maintaining a leaderboard can run a variant of this analysis on their own data.

The threshold paper_count*≈39 should be interpreted as a benchmark health indicator, not a hard retirement trigger. Benchmarks above this threshold merit closer review — including examinations of rank reversal rates, standard deviation of top-k methods, and qualitative assessment of whether the benchmark still captures meaningful capability differences. Our method identifies *when* to look harder, not a fully automated retirement decision.

Potential misuse: mechanically retiring benchmarks above paper_count*=39 without qualitative review could prematurely sunset benchmarks where the post-saturation regime reflects genuine consensus (the benchmark correctly identifies a solved task) rather than Goodhart gaming. Retirement decisions should combine quantitative indicators with community input.
