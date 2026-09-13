# 2. Related Work

## 2.1 Benchmark Saturation Studies

The saturation of ML benchmarks — the progressive compression of performance variance as the community exhausts high-payoff approaches — has attracted growing attention. Bowman and Dahl [CITE:Bowman2021] argue that standard NLU benchmarks have largely saturated, with top models differing by fractions of a percent, and call for principled retirement criteria. However, their analysis is qualitative; they identify the *need* for retirement criteria without providing a quantitative threshold.

Liao et al. [CITE:Liao2022UNVERIFIED] conduct the largest systematic study of benchmark saturation to date, analyzing near-saturation trends across 3,765 benchmarks using time-based metrics and coefficient of variation. Their analysis confirms that saturation is a systemic, cross-domain phenomenon — but their metric is time-based (years to saturation), not paper_count-based, and their methodology targets aggregate trends rather than discrete structural breaks. The global aggregate CoV trends they observe cannot answer when, in terms of publication count, a *specific* benchmark crosses from exploration to saturation.

Akhtar et al. [CITE:Akhtar2026] introduce the S_index, a composite saturation metric applied to 60 LLM benchmarks. S_index characterizes saturation as a continuous property and is designed for LLM evaluation platforms; it does not apply change-point detection to PwC-internal CoV-vs-paper_count data, and does not produce a paper_count threshold. Vasudevan et al. [CITE:Vasudevan2022] analyze ImageNet saturation in depth, documenting that top-1 accuracy above 90% no longer discriminates between models — providing independent evidence for the exploration-phase variance that characterizes pre-saturation benchmarks. Cao and Zhao [CITE:Cao2025] demonstrate that LLM benchmark scores are increasingly inflated by test-set pretraining, further motivating the need for quantitative saturation detection.

**The gap:** No prior work applies change-point detection to PwC-internal CoV-vs-paper_count data to produce a discrete, paper-count-based retirement threshold. Our work addresses this gap directly.

## 2.2 Change-Point Detection Methods

Change-point detection has a rich statistical literature. Pruned Exact Linear Time (PELT) [CITE:Killick2012UNVERIFIED] is an exact dynamic programming algorithm for detecting an unknown number of change-points in 1D signals with a penalized cost function. Wang, Lin and Willett [CITE:Wang2019] establish the VPWBS (Variable-Penalty WBBS) algorithm's O_p(1/n) localization rate for regression change-points under mild conditions, providing theoretical grounding for PELT's performance at small sample sizes (our N=115). The `ruptures` Python library [CITE:Truong2020UNVERIFIED] provides a well-maintained, audited PELT implementation (2,000+ GitHub stars) that we use directly.

Existing benchmark analysis methods — piecewise regression (Liao et al.), composite indices (S_index), threshold-based analysis (Bowman et al.) — treat saturation as a continuous property or apply domain-specific heuristics. We instead treat the CoV-vs-paper_count series as a signal in which a structural break should be detected and statistically validated, directly borrowing methods from the change-point literature.

## 2.3 Benchmark Evaluation and Leaderboard Dynamics

Papers With Code (PwC) [CITE:PwC2019UNVERIFIED] maintains a comprehensive leaderboard database with evaluation results across thousands of benchmarks, making it a uniquely rich source for benchmark lifecycle analysis. Prior work using PwC data has examined research dynamics and performance trends [CITE:Pinto2022UNVERIFIED], but not structural breaks in performance variability organized by publication count. The coefficient of variation (CoV = σ/μ per benchmark) captures score diversity in a scale-invariant manner, making it suitable for pooling across benchmarks with heterogeneous metric scales — a standard approach in benchmark evaluation research [CITE:Liao2022UNVERIFIED].

Our work is the first to apply PELT to PwC-internal residual CoV data, producing a quantitative paper_count* threshold grounded in change-point theory rather than aggregate trend analysis. This reframes benchmark saturation from a continuous property to a discrete, detectable phase transition.
