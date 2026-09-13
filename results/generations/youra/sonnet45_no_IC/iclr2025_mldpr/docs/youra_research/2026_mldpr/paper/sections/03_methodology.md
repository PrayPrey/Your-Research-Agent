# Methodology

Our study employs an observational meta-analysis design to quantify the relationship between documentation artifact quality and reproducibility outcomes. The methodology addresses a core measurement challenge: traditional reproducibility studies require expensive manual replication by independent teams, limiting sample sizes to tens of papers. We overcome this by treating performance variance across existing independent reproduction attempts as a scalable reproducibility proxy, enabling analysis of 108 benchmarks.

## Data Collection (Hypothesis h-e1)

We collected data from Papers with Code, a community-maintained database aggregating machine learning benchmark results from published papers. Papers with Code provides structured metadata including benchmark names, task types, datasets, evaluation metrics, and reported performance values from independent research groups. This infrastructure enables large-scale analysis that would be infeasible through manual replication studies.

**Inclusion Criteria.** We applied four filters to identify benchmarks suitable for variance analysis: (1) Task type: classification tasks only (excluding regression, generation, ranking), ensuring standardized metrics (accuracy, F1); (2) Publication period: 2019-2024, aligning with reproducibility badge adoption at major venues (NeurIPS, ICML, ICLR started badge programs circa 2018-2019); (3) Reproduction depth: ≥5 independent results per benchmark, ensuring sufficient sample size for coefficient of variation calculation; (4) Metric consistency: single metric type per benchmark (accuracy OR F1, not mixed), preventing artificial variance inflation from metric heterogeneity.

**Sample Characteristics.** The inclusion criteria yielded 108 classification benchmarks meeting all filters. Power analysis for two-sample comparison (α=0.05, power=0.80, effect size d=0.5) indicated required N=98 benchmarks; our sample exceeds this threshold. Domain distribution: 73 computer vision benchmarks (67.6%), 29 natural language processing benchmarks (26.9%), 6 multimodal benchmarks (5.5%). Reproduction depth distribution: median 7 independent results per benchmark (range: 5-47), with 83 benchmarks (76.9%) having 5-10 results and 25 benchmarks (23.1%) having >10 results.

**Data Validation.** We manually verified artifact presence for all 108 benchmarks by accessing linked repositories and dataset cards, ensuring metadata flags accurately reflected artifact availability (not broken links or empty repositories). All data collection used Papers with Code REST API (v1) with rate limiting (1 request/second) to prevent server overload.

## Artifact Quality Assessment (Hypothesis h-m1)

We developed a quantitative rubric for measuring documentation artifact quality, operationalizing completeness across four dimensions critical for reproduction: preprocessing specifications, data split protocols, evaluation procedures, and hyperparameters.

**Rubric Design.** Each dimension uses a 3-point scale (0, 5, 10) with explicit criteria:
- **Preprocessing (0-10):** 0 = no information; 5 = mentions preprocessing exists; 10 = complete code or configuration for all steps
- **Data Splits (0-10):** 0 = no split information; 5 = split ratios mentioned; 10 = exact seeds/indices or deterministic split code
- **Evaluation Protocol (0-10):** 0 = no evaluation details; 5 = metrics named; 10 = complete evaluation code with all parameters
- **Hyperparameters (0-10):** 0 = no hyperparameters listed; 5 = some parameters mentioned; 10 = complete configuration file

Benchmark-level quality score is the mean across four dimensions, yielding a continuous 0-10 scale. This design balances granularity (4 dimensions × 3 levels = 12 ordinal categories) with rater reliability (coarse 0/5/10 levels reduce subjective judgment).

**Coding Protocol.** Two independent raters assessed a stratified random sample of 20 benchmarks (10 computer vision, 10 NLP) with ≥2 artifacts present. Raters received training on the rubric using 3 pilot benchmarks, resolving scoring discrepancies before independent coding. Raters accessed GitHub repositories, dataset cards, and paper PDFs to extract information, scoring each dimension independently. We computed Cohen's kappa (κ) for inter-rater reliability, requiring κ>0.8 (excellent agreement) for measurement validation.

**Quality Threshold.** We set a minimum quality threshold at 7.0/10, representing artifacts that provide sufficient implementation detail for precise replication. This threshold is conservative—a score of 7.0 requires mean scores of 5-10 across dimensions, indicating at least partial specification of all components. Artifacts scoring below 7.0 are considered insufficient for their intended purpose (enabling reproduction).

## Variance Analysis (Hypothesis h-m3)

We operationalize reproducibility through performance variance: lower coefficient of variation (CV) across independent reproduction attempts indicates higher procedural consistency. CV normalizes variance by mean (CV = σ/μ), enabling comparison across benchmarks with different performance scales (e.g., 60% accuracy vs. 95% accuracy).

**Artifact Grouping.** We classified benchmarks into high-artifact (≥2 artifacts: GitHub repository AND dataset card AND/OR badge) and low-artifact (<2 artifacts) groups. The threshold of 2 artifacts ensures meaningful documentation presence—a single artifact (e.g., GitHub repository alone) may be incomplete. This binary classification simplifies analysis while maintaining interpretability; we also tested dose-response relationships using continuous artifact counts (0-3).

**Statistical Framework.** Our primary hypothesis test uses Mann-Whitney U test (non-parametric, two-tailed, α=0.05) comparing CV distributions between high-artifact and low-artifact groups. We selected Mann-Whitney over t-test because Shapiro-Wilk normality tests indicated non-normal CV distributions (expected for variance metrics). Effect size is measured using Cohen's d = (μ_low - μ_high) / σ_pooled, with d>0.5 (medium effect) as the substantive significance threshold. Cohen's d complements p-values by quantifying practical importance beyond statistical significance.

Secondary analyses include: (1) Spearman rank correlation (ρ) between continuous artifact count (0-3) and CV to test dose-response relationships; (2) Stratified analysis by domain (computer vision vs. NLP) to assess effect heterogeneity; (3) Propensity score weighting to correct sampling bias if Papers with Code coverage differs by artifact presence (threshold: >10% coverage difference triggers weighting).

**Power Analysis.** For Cohen's d=0.5 (medium effect), α=0.05, and power=0.80, two-sample comparison requires N=98 benchmarks (49 per group). Our sample of 108 benchmarks meets this threshold if group sizes are balanced. However, the final variance analysis (h-m3) used n=22 benchmarks due to artifact filtering and data availability constraints, achieving approximately 30% statistical power. This underpowered design increases Type II error risk (false negatives), meaning a real medium effect might not be detected. We report this limitation transparently and provide effect size estimates (d=0.464) to inform future meta-analyses and sample size planning.

**Confound Control.** We recorded benchmark age (years since publication), task domain (CV, NLP, multimodal), and metric type (accuracy vs. F1) as potential confounds. Sampling bias was assessed by comparing inclusion rates: P(included | high-artifact) vs. P(included | low-artifact). If the difference exceeded 10%, we applied propensity score weighting using logistic regression to estimate inclusion probabilities conditional on confounds, then reweighted samples using inverse probability weights before statistical testing.

## Reproducibility and Transparency

All data collection, quality coding, and statistical analysis code is available in the project repository under MIT license. The artifact quality rubric, including scoring criteria and training materials, is provided as supplementary material. Raw data includes benchmark identifiers, artifact URLs, quality scores from both raters, and performance variance calculations, enabling full verification and extension of our analysis. We report all preregistered hypotheses (h-e1, h-m1, h-m2, h-m3) with pass/fail gates defined a priori, transparently documenting null results (h-m3: p=0.418) alongside positive findings (h-m1: κ=1.0).
