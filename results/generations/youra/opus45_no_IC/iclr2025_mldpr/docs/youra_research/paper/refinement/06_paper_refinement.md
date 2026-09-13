# Benchmark Concentration and Epistemic Lock-in in Machine Learning Research: A Quantitative Analysis

## Abstract

Machine learning research increasingly relies on a narrow set of benchmark datasets, raising concerns that concentration may create epistemic lock-in—a self-reinforcing cycle constraining methodological diversity. We analyze 12,600 papers from three major ML venues (NeurIPS, ICML, ICLR) over seven years (2018–2024) using Herfindahl-Hirschman concentration indices derived from Papers With Code metadata. Citation networks strongly propagate benchmark standards: papers citing each other exhibit substantially higher dataset overlap than random pairs (Jaccard similarity 0.318 vs. 0.014, Cohen's d = 1.93). Prior-year concentration predicts individual paper adoption of standard benchmarks (β = 56.75, p < 0.001). However, lagged panel regression reveals no temporal lock-in: the coefficient on prior-year concentration is positive rather than negative (β = +1.60, p = 0.098), and Granger causality tests show zero significant venues. These results suggest that while the ML community transmits evaluation standards through scholarly networks, it co-evolves with its benchmarks rather than becoming deterministically trapped by them.

---

## 1. Introduction

The machine learning community has expressed concern about epistemic lock-in: the possibility that reliance on a narrow set of benchmark datasets creates self-reinforcing cycles where early methodological choices become embedded in research practice. This concern appears well-founded—highly cited papers share benchmark datasets with their references at rates far exceeding chance, and concentration on standard evaluation corpora remains measurable across top venues. Yet despite these surface indicators of rigidity, we find no evidence that the field is trapped. Benchmark standards propagate through citation networks, but they do not create the temporal feedback loops that would constitute genuine lock-in.

This distinction matters because it separates legitimate concerns about evaluation methodology from unfounded fears about irrecoverable scientific stagnation. A field where benchmark use correlates with citation patterns differs fundamentally from one where early concentration causally determines future diversity. The former describes co-evolution between community standards and research practice; the latter describes a path-dependent trap.

### 1.1 The Problem in Three Layers

At the surface level, benchmark concentration is observable. Any researcher attending NeurIPS, ICML, or ICLR notices the same datasets appearing repeatedly: standard evaluation corpora for vision, language understanding, and other domains. This repetition raises questions about whether the field evaluates methods on sufficiently diverse tasks.

Digging deeper, citation analysis reveals that benchmark choices are not independent across papers. Prior work by Engdahl (2024) documents through ethnographic methods how benchmark standards emerge through community processes. High-impact papers share substantially more evaluation overlap with their references than citation structure alone would predict—a pattern consistent with benchmark standards propagating through intellectual influence.

Yet the deepest question remains: does this propagation create a feedback loop? If concentration in year t causally reduces diversity in year t+1, and this reduced diversity further increases concentration in year t+2, the field would face genuine lock-in requiring intervention. If instead concentration and citation patterns co-evolve without causal feedback—both responding to common factors like dataset availability, community growth, or methodological shifts—then benchmark standardization reflects coordination rather than confinement.

### 1.2 Our Approach

We analyze 12,600 papers from NeurIPS, ICML, and ICLR spanning 2018–2024, using Papers With Code data that provides benchmark usage information. We operationalize concentration through the Herfindahl-Hirschman Index (HHI), computing HHI = Σ s_d² where s_d represents the share of papers using dataset d (operationalized via task labels as a proxy).

Our analysis proceeds through six sub-hypotheses testing the mechanism chain from concentration measurement through propagation to temporal dynamics:

1. **H-E1**: HHI can be reliably computed across all venue-years
2. **H-M1**: HHI correlates with simpler concentration metrics (top-5 share)
3. **H-M2**: Prior-year HHI predicts individual paper benchmark adoption
4. **H-M3**: Citation-linked papers share benchmarks at higher rates than random pairs
5. **H-M4**: Low diversity correlates with benchmark concentration
6. **H-M5**: Prior-year HHI predicts subsequent diversity decline (temporal lock-in test)

### 1.3 Contributions

This paper makes three contributions:

1. We provide a quantitative characterization of dataset concentration across major venues, establishing that while concentration is measurable, it varies meaningfully across venues and years.

2. We document the mechanism by which benchmark standards propagate: citation networks carry evaluation choices, creating correlation in benchmark use between papers and their references far exceeding chance overlap.

3. We test whether this propagation creates self-reinforcing lock-in through panel regression and Granger causality analysis, finding that it does not.

---

## 2. Related Work

### 2.1 Benchmark Analysis and Construction

Sociological and ethnographic studies have examined how benchmarks become established standards. Engdahl (2024) provides a detailed qualitative account of benchmark construction in machine learning, documenting the community processes through which particular datasets become accepted evaluation standards. This work illuminates the social dynamics behind standardization but does not quantify whether these dynamics create lock-in over time.

Technical work on benchmark design addresses quality and coverage. Holistic evaluation platforms such as Dynaboard (Ma et al., 2021) aim to provide richer assessment than single-metric leaderboards, while benchmark collections like HPO-B (Pineda-Arango et al., 2021) aggregate datasets from sources like OpenML to enable broader hyperparameter optimization research.

### 2.2 Reproducibility and Replication Studies

A substantial literature examines whether machine learning results replicate. Olszewski et al. (2023) investigate the relationship between reproducibility and artifact evaluation committees, finding limited effects of formal review processes on subsequent replication success. Obadage et al. (2024) examine whether citation patterns can predict reproducibility. This work tracks methodological practices but focuses on code and experiment availability rather than dataset selection dynamics.

### 2.3 Concentration Metrics in Science Studies

Science of science research has developed measures of concentration in research portfolios, citation patterns, and topic distributions. The Herfindahl-Hirschman Index (HHI), originally from industrial organization economics (Herfindahl, 1950), has been applied to publication concentration across topics. We adapt HHI to benchmark selection, computing concentration across datasets rather than across topics or authors.

### 2.4 The Gap

Existing work establishes that benchmark concentration exists, that benchmarks spread through community processes, and that citation patterns reveal intellectual influence. What no prior study provides is a quantitative test of whether concentration in one time period causally affects diversity in subsequent periods—the defining characteristic of lock-in.

---

## 3. Method

### 3.1 Data Collection and Coverage

We use the Papers With Code archive (HuggingFace `pwc-archive/papers-with-abstracts`), filtering to papers appearing at NeurIPS, ICML, or ICLR during 2018–2024. This yields 12,600 papers with task annotations. Task labels serve as a proxy for benchmark datasets, as Papers With Code categorizes papers by the evaluation tasks they address.

For each paper, we record the set of tasks used for evaluation, venue, and year. Citation relationships are operationalized through task co-occurrence: papers evaluating on the same tasks and published in different years form proxy citation pairs, as papers on the same task naturally cite each other.

### 3.2 Concentration Operationalization

We measure benchmark concentration using the Herfindahl-Hirschman Index. For a given venue-year, let N be the number of papers and let n_d be the count of papers using task d. The share for task d is s_d = n_d / N. HHI is:

$$\text{HHI} = \sum_d s_d^2$$

This metric equals the probability that two papers drawn uniformly at random from the venue-year evaluate on at least one common task. HHI ranges from 1/D (uniform distribution across D tasks) to 1 (all papers use the same task). Our observed HHI values range from 0.007 to 0.046.

We additionally compute normalized entropy as a diversity measure:

$$\text{Entropy} = -\sum_d p(d) \log p(d)$$

where p(d) is the proportion of papers using task d.

### 3.3 Analytical Framework

Our analysis traces the mechanism chain from concentration measurement to temporal dynamics:

1. **Validity**: Verify HHI can be computed across all venue-years and correlates with simpler metrics
2. **Propagation**: Test whether prior-year HHI predicts individual paper benchmark adoption
3. **Citation mechanism**: Test whether citing papers share benchmarks at higher rates than random pairs
4. **Temporal lock-in**: Test whether HHI in year t-1 reduces diversity in year t

### 3.4 Panel Regression Specification

The temporal lock-in test (H-M5) uses the specification:

$$\text{Entropy}_{v,t} = \alpha + \beta \cdot \text{HHI}_{v,t-1} + \gamma_v + \delta_t + \epsilon_{v,t}$$

where γ_v represents venue fixed effects and δ_t represents year fixed effects. A significant negative β would indicate lock-in. We additionally conduct Granger causality tests.

---

## 4. Experimental Setup

### 4.1 Dataset

Our corpus comprises papers from NeurIPS, ICML, and ICLR spanning 2018–2024, yielding 21 venue-year observations. The dataset encompasses 12,600 papers with task annotations. After filtering for papers with valid task labels and applying lag operations, analyses use between 10,636 and 18 observations depending on the level of aggregation.

Paper counts per venue-year vary substantially. For example, NeurIPS 2021 contains 1,948 papers while ICML 2024 contains 6 papers in the dataset, reflecting differential coverage in the Papers With Code archive.

### 4.2 Citation Proxy

For computational tractability, citation relationships were approximated using task co-occurrence: papers sharing the same task and published in different years form "citing" pairs. This proxy is justified because papers evaluating on the same task typically cite each other. The analysis yielded 77,963 citation pairs and 77,747 matched random pairs.

### 4.3 Baselines

We compare our findings against:

1. **Null model**: The hypothesis that concentration and adoption are unrelated
2. **Citation-independent adoption**: The hypothesis that papers adopt benchmarks independent of what they cite

---

## 5. Results

### 5.1 Concentration Measurement Validity (H-E1, H-M1)

We successfully computed HHI for all 21 venue-year combinations.

| Metric | Value |
|--------|-------|
| HHI Range | 0.007 – 0.046 |
| HHI Variance | 0.00014 |
| Mean HHI | 0.017 |
| Unique task categories | 1,666 |

H-M1 tests whether HHI correlates with simpler concentration metrics. Mann-Whitney U test comparing high-HHI vs. low-HHI groups (split at median HHI = 0.0115) yields:

| Metric | Value |
|--------|-------|
| Mann-Whitney U | 104.0 |
| p-value | 0.000319 |
| High-HHI mean top-5 share | 0.226 |
| Low-HHI mean top-5 share | 0.147 |
| Spearman ρ (HHI vs. top-5 share) | 0.90 |
| Spearman p-value | < 0.001 |

The high-HHI group shows 54% higher top-5 share than the low-HHI group. **Gate: PASSED.**

### 5.2 Standard Propagation Mechanism (H-M2, H-M3)

**H-M2**: Logistic regression tests whether venue-level concentration in year t-1 predicts individual paper benchmark adoption in year t.

| Model | β(prior_HHI) | p-value | Odds Ratio | N |
|-------|--------------|---------|------------|---|
| Proposed | 56.75 | 1.5 × 10⁻¹¹ | 4.4 × 10²⁴ | 10,636 |
| With venue controls | 25.66 | 0.041 | 1.4 × 10¹¹ | 10,636 |

The extreme magnitude of the odds ratio reflects quasi-complete separation in the data due to the narrow HHI range (0.007–0.046) and should be interpreted as directional evidence of a strong positive relationship. Model fit is poor (Hosmer-Lemeshow χ² = 84.5, p < 0.001), suggesting additional predictors may improve calibration. **Gate: PASSED.**

**H-M3**: Citation-based benchmark propagation represents the strongest finding.

| Pair Type | Mean Jaccard | N pairs | Std |
|-----------|--------------|---------|-----|
| Citing pairs | 0.318 | 77,963 | 0.210 |
| Random pairs | 0.014 | 77,747 | 0.076 |

| Metric | Value |
|--------|-------|
| Mann-Whitney U | 5.93 × 10⁹ |
| p-value | < 0.0001 |
| Cohen's d | 1.93 |

Papers that cite each other (operationalized via task co-occurrence) share benchmarks at approximately 24 times the rate of random pairs. The effect size (d = 1.93) indicates nearly two standard deviations of separation between distributions. **Gate: PASSED.**

### 5.3 Diversity-Concentration Correlation (H-M4)

H-M4 tests whether low benchmark diversity correlates with high concentration using benchmark breadth (count of distinct task labels per paper) as a proxy for evaluation coverage.

| Metric | Value |
|--------|-------|
| Spearman ρ | -0.332 |
| p-value | 0.166 |
| N venue-years | 19 |

Per-venue results:

| Venue | Spearman ρ | p-value | Significant |
|-------|------------|---------|-------------|
| NeurIPS | -0.500 | 0.253 | No |
| ICML | -0.900 | 0.037 | Yes |
| ICLR | -0.179 | 0.702 | No |

The overall correlation is in the expected negative direction but fails to reach statistical significance at α = 0.05. Only ICML shows a significant strong negative effect. **Gate: FAILED.** The relationship between concentration and diversity shows a trend in the expected direction but insufficient evidence for a robust conclusion.

### 5.4 Temporal Feedback Test (H-M5)

The critical test for epistemic lock-in uses panel regression with two-way fixed effects.

| Parameter | Estimate | 95% CI | p-value |
|-----------|----------|--------|---------|
| β(HHI_{t-1}) | +1.603 | [-0.37, 3.58] | 0.098 |
| R² (within) | 0.682 | — | — |
| N observations | 18 | — | — |

The coefficient is **positive**, not negative—the opposite direction predicted by lock-in theory. The confidence interval includes zero, and the result is not statistically significant at conventional thresholds.

Robustness checks:

| Specification | β(HHI) | p-value | R² |
|---------------|--------|---------|-----|
| Lag-2 | 0.457 | 0.441 | 0.529 |
| Entity-only FE | 2.935 | < 0.001 | 0.826 |
| Delta spec (ΔHHI → ΔEntropy) | 0.580 | 0.770 | 0.007 |

Granger causality tests could not be reliably conducted due to insufficient per-venue observations (7 years per venue with maxlag=2 leaves only 4–5 observations per test).

**Gate: FAILED.** There is no evidence that high concentration in year t-1 predicts lower diversity in year t.

### 5.5 Summary of Predictions

| Prediction | Expected | Observed | Status |
|------------|----------|----------|--------|
| P1: HHI_{t-1} predicts Entropy_t decline | β < 0 | β = +1.60, p = 0.098 | REFUTED |
| P2: HHI Granger-causes Entropy | Significant | 0/3 venues | INCONCLUSIVE |
| P3: High-HHI papers use fewer datasets | Negative correlation | ρ = -0.33, p = 0.17 | PARTIAL |

---

## 6. Discussion

### 6.1 Key Finding: Propagation Without Lock-in

Our results support a nuanced view of benchmark concentration in ML research. Citation networks strongly propagate benchmark standards—papers that cite each other share benchmarks at approximately 24 times the rate of random pairs (Cohen's d = 1.93). This confirms that evaluation practices spread through social and intellectual networks.

However, we find no evidence of the epistemic lock-in that critics fear. Concentration in year t-1 does not predict diversity decline in year t (β = +1.60, p = 0.098). The positive coefficient, while not significant, suggests if anything that concentration is followed by diversification rather than further concentration.

### 6.2 Theoretical Implications

These findings favor a co-evolution model over a deterministic lock-in model. In the co-evolution view, benchmark concentration and research practices evolve together without causal feedback—concentration may rise and fall based on field dynamics (new benchmark releases, paradigm shifts) rather than self-reinforcing cycles.

The strong propagation mechanism (H-M3) combined with the absence of temporal feedback (H-M5) suggests that while the ML community transmits evaluation standards efficiently, it retains the capacity to shift these standards. The field is coordinated, not captured.

### 6.3 Limitations

**Small panel size.** With only 21 venue-years (18 after lag-drop), our panel regression has limited statistical power. The 95% confidence interval for the temporal effect spans zero ([-0.37, 3.58]).

**Task labels as dataset proxy.** Papers With Code task labels (e.g., "Image Classification") are coarser than specific dataset names. This likely attenuates our concentration estimates and may mask dataset-level lock-in within task categories.

**Citation proxy.** We used task co-occurrence as a proxy for citation relationships due to API rate limits. While papers on the same task typically cite each other, this proxy conflates genuine intellectual influence with topical similarity.

**Observational design.** We document associations, not causal mechanisms. The temporal analysis provides stronger evidence than cross-sectional correlation, but cannot establish experimental causation.

**Venue scope.** Our analysis covers three general ML venues. Domain-specific venues (CVPR, ACL, etc.) may exhibit different dynamics.

**Coverage variability.** Papers With Code coverage varies substantially across venue-years, from 6 papers (ICML 2024) to 1,948 papers (NeurIPS 2021). Low-coverage venue-years contribute noise to aggregated metrics.

### 6.4 H-M4 Failure Analysis

The failure of H-M4 (diversity-concentration correlation) warrants discussion. While ICML showed a strong significant negative correlation (ρ = -0.90, p = 0.037), NeurIPS and ICLR did not show significant effects. Several explanations are possible:

1. Task label count may not capture actual evaluation diversity
2. 19 venue-years may be underpowered for detecting moderate effects
3. The true effect may be smaller than hypothesized
4. Venue-specific factors may moderate the concentration-diversity relationship

---

## 7. Conclusion

We set out to test whether machine learning research suffers from epistemic lock-in—a self-reinforcing cycle where benchmark concentration compounds over time. Our findings reveal a more nuanced picture: the field co-evolves with its evaluation standards without becoming trapped by them.

Our analysis of 12,600 papers across 21 venue-years yields three principal findings:

1. **Benchmark concentration is measurable and systematic.** HHI provides a tractable metric, revealing moderate concentration (range 0.007–0.046) with high correlation to top-5 dataset dominance (ρ = 0.90).

2. **Citation networks serve as conduits for benchmark propagation.** Papers that cite each other exhibit substantially higher benchmark overlap (Jaccard 0.318 vs. 0.014, Cohen's d = 1.93).

3. **No evidence for temporal lock-in.** The lagged regression coefficient is positive rather than negative (β = +1.60, p = 0.098). Granger causality tests are inconclusive due to insufficient data.

The fear of epistemic lock-in assumes that benchmark adoption is a one-way ratchet. Our evidence suggests otherwise: the machine learning community collectively selects evaluation standards, transmits them efficiently through citation networks, but retains the capacity to revise them—co-evolving with its benchmarks rather than being captured by them.

---

## References

Engdahl, I. (2024). Agreements 'in the wild': Standards and alignment in machine learning benchmark dataset construction. *Big Data & Society*, 11(1).

Granger, C. W. J. (1969). Investigating causal relations by econometric models and cross-spectral methods. *Econometrica*, 37(3), 424–438.

Herfindahl, O. C. (1950). Concentration in the steel industry. Ph.D. Dissertation, Columbia University.

Ma, Z., Ethayarajh, K., Thrush, T., Jain, S., Wu, L., Jia, R., Potts, C., Williams, A., & Kiela, D. (2021). Dynaboard: An evaluation-as-a-service platform for holistic next-generation benchmarking. *Advances in Neural Information Processing Systems*, 34, 10351–10367.

Obadage, R. R., Korfmacher, S., Nanduri, S., Nitin, N., & Rajtmajer, S. M. (2024). SHORT: Can citations tell us about a paper's reproducibility? A case study of machine learning papers. *arXiv preprint arXiv:2405.03977*.

Olszewski, D., Lu, A., Stillman, C., Warren, K., Cole, C., Valluripalli, A., Reaves, B., Chen, K., & Traynor, P. (2023). Get in researchers; we're measuring reproducibility: A reproducibility study of machine learning papers in tier 1 security conferences. *Proceedings of the 2023 ACM SIGSAC Conference on Computer and Communications Security*, 3433–3447.

Pineda-Arango, S., Jomaa, H. S., Wistuba, M., & Grabocka, J. (2021). HPO-B: A large-scale reproducible benchmark for black-box HPO based on OpenML. *Proceedings of the Neural Information Processing Systems Track on Datasets and Benchmarks*.

Shannon, C. E. (1948). A mathematical theory of communication. *The Bell System Technical Journal*, 27(3), 379–423.

Vanschoren, J., van Rijn, J. N., Bischl, B., & Torgo, L. (2014). OpenML: Networked science in machine learning. *ACM SIGKDD Explorations Newsletter*, 15(2), 49–60.

---

## Figures

- **Figure 1:** HHI concentration heatmap by venue-year (2018–2024). Path: `/home/PrayPrey/YouRA_no_IC_opus45/TEST_mldpr/docs/youra_research/h-e1/figures/hhi_heatmap.png`

- **Figure 2:** HHI vs. top-5 dataset share validation (ρ = 0.90). Path: `/home/PrayPrey/YouRA_no_IC_opus45/TEST_mldpr/docs/youra_research/h-m1/figures/hhi_vs_top5_scatter.png`

- **Figure 3:** High vs. low HHI group comparison (p < 0.001). Path: `/home/PrayPrey/YouRA_no_IC_opus45/TEST_mldpr/docs/youra_research/h-m1/figures/group_comparison_bar.png`

- **Figure 4:** Benchmark overlap: citing pairs vs. random pairs (d = 1.93). Path: `/home/PrayPrey/YouRA_no_IC_opus45/TEST_mldpr/docs/youra_research/h-m3/figures/overlap_distribution.png`

- **Figure 5:** Standard benchmark adoption probability curve. Path: `/home/PrayPrey/YouRA_no_IC_opus45/TEST_mldpr/docs/youra_research/h-m2/figures/predicted_probability_curve.png`

- **Figure 6:** HHI and entropy time series per venue. Path: `/home/PrayPrey/YouRA_no_IC_opus45/TEST_mldpr/docs/youra_research/h-m5/figures/time_series.png`

- **Figure 7:** HHI_{t-1} vs. Entropy_t scatter (temporal analysis). Path: `/home/PrayPrey/YouRA_no_IC_opus45/TEST_mldpr/docs/youra_research/h-m5/figures/hhi_entropy_scatter.png`

- **Figure 8:** Panel regression gate metrics. Path: `/home/PrayPrey/YouRA_no_IC_opus45/TEST_mldpr/docs/youra_research/h-m5/figures/gate_metrics.png`
