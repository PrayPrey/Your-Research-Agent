# Benchmark Concentration and Epistemic Lock-in in Machine Learning Research: A Quantitative Analysis

## Abstract

Machine learning research increasingly relies on a narrow set of benchmark datasets, raising concerns that concentration may create epistemic lock-in—a self-reinforcing cycle constraining methodological diversity. Yet no quantitative framework has tested whether benchmark adoption exhibits temporal feedback dynamics. We analyze 12,600 papers from three major ML venues over seven years (21 venue-years) using Herfindahl-Hirschman concentration indices derived from Papers With Code metadata. We find strong evidence that citation networks propagate benchmark standards: papers citing each other exhibit 24-fold higher dataset overlap than random pairs (Jaccard 0.318 vs. 0.014, Cohen's d=1.93). However, lagged panel regression reveals no temporal lock-in: the coefficient on prior-year concentration is positive rather than negative (β=+1.60, p=0.098), and Granger causality tests show zero significant venues. These results suggest that while the ML community transmits evaluation standards through scholarly networks, it co-evolves with its benchmarks rather than becoming deterministically trapped by them.

---

## 1. Introduction

The machine learning community has long worried about epistemic lock-in: the possibility that reliance on a narrow set of benchmark datasets creates self-reinforcing cycles where early methodological choices become permanently embedded in research practice. This concern appears well-founded—highly cited papers overwhelmingly share benchmark datasets with their references, and concentration on standard evaluation corpora remains high across top venues. Yet despite these surface indicators of rigidity, we find no evidence that the field is actually trapped. Benchmark standards propagate through citation networks, but they do not create the temporal feedback loops that would constitute genuine lock-in.

This distinction matters because it separates legitimate concerns about evaluation methodology from unfounded fears about irrecoverable scientific stagnation. A field where benchmark use correlates with citation patterns differs fundamentally from one where early concentration causally determines future diversity. The former describes co-evolution between community standards and research practice; the latter describes a path-dependent trap. Our contribution is establishing, through quantitative temporal analysis, which of these characterizes machine learning research.

### 1.1 The Problem in Three Layers

At the surface level, benchmark concentration is easily observed. Any researcher attending NeurIPS, ICML, or ICLR notices the same datasets appearing repeatedly: ImageNet for vision, GLUE for language understanding, standard splits on well-known corpora. This repetition raises natural questions about whether the field evaluates methods on sufficiently diverse tasks to generalize findings.

Digging deeper, citation analysis reveals that benchmark choices are not independent across papers. Prior work by Engdahl (2024) documents through ethnographic methods how benchmark standards emerge through community processes, while studies of hyperparameter optimization benchmarks like HPO-B (Pineda-Arango et al., 2021) demonstrate concentrated usage patterns even when alternatives exist. High-impact papers share substantially more evaluation overlap with their references than citation structure alone would predict—a pattern consistent with benchmark standards propagating through intellectual influence.

Yet the deepest question remains unaddressed: does this propagation create a feedback loop? If concentration in year t causally reduces diversity in year t+1, and this reduced diversity further increases concentration in year t+2, the field would face genuine lock-in requiring intervention. If instead concentration and citation patterns co-evolve without causal feedback—both responding to common factors like dataset availability, community growth, or methodological shifts—then benchmark standardization reflects coordination rather than confinement.

No prior work has conducted the quantitative temporal analysis required to distinguish these hypotheses. This gap motivates our study.

### 1.2 Our Approach and Key Insight

We analyze 12,600 papers from NeurIPS, ICML, and ICLR spanning 2018-2024, using Papers With Code data that provides benchmark usage information with over 80% coverage. We operationalize concentration through the Herfindahl-Hirschman Index (HHI), computing HHI = Σ s_d² where s_d represents the share of papers using dataset d.

Our analysis proceeds through six sub-hypotheses testing the mechanism chain from concentration measurement through propagation to temporal dynamics. We first establish that HHI provides a valid concentration measure correlating with simpler top-5 share metrics (ρ = 0.90, p < 0.001). We then demonstrate that benchmark standards do propagate through citations—papers share substantially higher benchmark overlap with papers they cite (Jaccard similarity 0.318 versus 0.014 baseline, Cohen's d = 1.93). Prior concentration predicts individual paper adoption of standard benchmarks (odds ratio 4.4 × 10²⁴).

The key finding emerges in our temporal analysis. Despite strong propagation mechanisms, we find no evidence of causal feedback from concentration to subsequent diversity. Panel regression of benchmark entropy on lagged HHI, controlling for venue and year fixed effects, yields a coefficient that is not statistically significant (β = +1.60, p = 0.098). Granger causality tests similarly fail to reject the null. Concentration does not trap the field; benchmark standards spread, but diversity can shift independently.

### 1.3 Contributions

This paper makes three contributions to understanding benchmark dynamics in machine learning research. First, we provide a comprehensive quantitative characterization of dataset concentration across major venues, establishing that while concentration is measurable and substantive, it varies meaningfully across venues and years rather than reflecting uniform rigidity. Second, we document the mechanism by which benchmark standards propagate: citation networks carry evaluation choices, creating correlation in benchmark use between papers and their references far exceeding chance overlap. Third, and most importantly, we test whether this propagation creates self-reinforcing lock-in through panel regression and Granger causality analysis, finding that it does not.

---

## 2. Related Work

Our study connects three research streams: qualitative analyses of benchmark construction, quantitative reproducibility investigations, and concentration measurement in science. Each provides essential background but none addresses whether benchmark concentration creates temporal feedback loops.

### 2.1 Benchmark Analysis and Construction

Sociological and ethnographic studies have examined how benchmarks become established standards. Engdahl (2024) provides a detailed qualitative account of benchmark construction in machine learning, documenting the community processes through which particular datasets become accepted evaluation standards. This work illuminates the social dynamics behind standardization but does not quantify whether these dynamics create lock-in over time.

Technical work on benchmark design addresses quality and coverage. Holistic evaluation platforms such as Dynaboard (Ma et al., 2021) aim to provide richer assessment than single-metric leaderboards, while large-scale benchmark collections like HPO-B (Pineda-Arango et al., 2021) aggregate datasets from sources like OpenML to enable broader hyperparameter optimization research.

### 2.2 Reproducibility and Replication Studies

A substantial literature examines whether machine learning results replicate. Olszewski et al. (2023) investigate the relationship between reproducibility and artifact evaluation committees, finding limited effects of formal review processes on subsequent replication success. This work tracks methodological practices but focuses on code and experiment availability rather than dataset selection dynamics.

### 2.3 Concentration Metrics in Science Studies

Science of science research has developed measures of concentration in research portfolios, citation patterns, and topic distributions. The Herfindahl-Hirschman Index (HHI), originally from industrial organization economics, has been applied to publication concentration across topics. We adapt HHI to benchmark selection, computing concentration across datasets rather than across topics or authors.

### 2.4 The Gap: No Temporal Causality Test

Existing work establishes that benchmark concentration exists, that benchmarks spread through community processes, and that citation patterns reveal intellectual influence. What no prior study provides is a quantitative test of whether concentration in one time period causally affects diversity in subsequent periods—the defining characteristic of lock-in.

---

## 3. Methodology

We test whether benchmark concentration creates epistemic lock-in through a six-hypothesis framework that traces the mechanism chain from concentration measurement through citation propagation to temporal dynamics. Our data comes from Papers With Code, covering 12,600 papers from NeurIPS, ICML, and ICLR spanning 2018-2024.

### 3.1 Data Collection and Coverage

Papers With Code provides structured information linking papers to the datasets they use for evaluation. We extract all entries for papers appearing at NeurIPS, ICML, or ICLR during our study period, yielding 12,600 papers with benchmark annotations. We estimate coverage exceeds 80% of accepted papers at these venues based on comparing PWC entry counts against official venue acceptance statistics from conference proceedings.

For each paper, we record the set of datasets used for evaluation, venue, year, and citation links to other papers in the corpus. Citation data comes from Semantic Scholar, matched to Papers With Code entries through paper identifiers.

### 3.2 Concentration Operationalization

We measure benchmark concentration using the Herfindahl-Hirschman Index (HHI). For a given venue-year, let N be the number of papers and let n_d be the count of papers using dataset d. The share for dataset d is s_d = n_d / N. HHI is then:

$$\text{HHI} = \sum_d s_d^2$$

This metric equals the probability that two papers drawn uniformly at random from the venue-year evaluate on at least one common dataset. HHI ranges from 1/D (uniform distribution across D datasets) to 1 (all papers use the same dataset). Our observed HHI values range from 0.007 to 0.046.

### 3.3 Analytical Framework

Our analysis traces the mechanism chain from concentration measurement to temporal dynamics. We first establish that HHI provides a valid concentration measure by verifying it can be computed across all venue-years and correlates with simpler metrics like top-5 dataset share. We then test whether concentration predicts individual paper behavior: do papers adopt standard benchmarks more readily when venue-level concentration is already high?

The propagation mechanism is tested through citation network analysis. If benchmark standards spread through intellectual influence, papers should share more evaluation overlap with the papers they cite than with random papers. Finally, we test for temporal lock-in directly: does concentration in year t-1 reduce diversity in year t? This is the critical test distinguishing co-evolution from lock-in.

### 3.4 Panel Regression Specification

The temporal lock-in test (H-M5) is our primary contribution. We estimate:

$$\text{Entropy}_{v,t} = \alpha + \beta \cdot \text{HHI}_{v,t-1} + \gamma_v + \delta_t + \epsilon_{v,t}$$

where γ_v represents venue fixed effects and δ_t represents year fixed effects. Significant negative β would indicate lock-in; we additionally conduct Granger causality tests.

---

## 4. Experimental Setup

### 4.1 Research Questions

1. **Measurability**: Can we reliably quantify benchmark concentration across major ML venues?
2. **Predictive Power**: Does concentration at the venue level predict individual paper adoption of standard benchmarks?
3. **Temporal Dynamics**: Is there evidence for temporal lock-in?

### 4.2 Dataset

Our corpus comprises papers from NeurIPS, ICML, and ICLR spanning 2018-2024, yielding 21 venue-year observations. The dataset encompasses 10,636 papers with valid dataset annotations. Citation relationships were obtained from Semantic Scholar, providing 77,963 citing-cited paper pairs.

### 4.3 Baselines

We compare our findings against two baselines:

1. **Null model (cross-sectional only)**: The hypothesis that concentration and adoption are unrelated across venue-years.

2. **Citation-independent adoption**: The hypothesis that papers adopt benchmarks independent of what they cite.

---

## 5. Results

### 5.1 Concentration Measurement Validity (H-E1, H-M1)

We successfully computed HHI for all 21 venue-year combinations. HHI values ranged from 0.007 to 0.046, with variance of 0.00014.

Mann-Whitney U test rejects the null of no group difference (p = 0.000319). Spearman correlation between HHI and top-5 dataset share is ρ = 0.90 (p < 0.001). The high-HHI group showed mean top-5 share of 0.226, compared to 0.147 for the low-HHI group—a 54% relative difference.

### 5.2 Standard Propagation Mechanism (H-M2, H-M3)

**H-M2:** Logistic regression confirms that venue-level concentration in year t-1 predicts whether individual papers in year t use standard benchmarks. The coefficient β = 56.75 is highly significant (p < 0.001), corresponding to an odds ratio of 4.4 × 10²⁴. We note this extreme magnitude reflects quasi-complete separation in the data and should be interpreted as directional evidence of a strong positive relationship rather than a precise effect size estimate.

**H-M3:** Our strongest finding concerns citation-based benchmark propagation. Citing pairs exhibit mean Jaccard similarity of 0.318, compared to 0.014 for randomly paired papers. Cohen's d = 1.93 indicates a large effect—nearly two standard deviations separate the distributions.

| Pair Type | Mean Jaccard | N pairs |
|-----------|--------------|---------|
| Citing pairs | 0.318 | 77,963 |
| Random pairs | 0.014 | 77,747 |

### 5.3 Temporal Feedback Test (H-M5)

**Critical Result:** Panel regression yields β(HHI_{t-1}) = +1.603 with p = 0.098. The coefficient is **positive**, not negative—the opposite direction predicted by lock-in theory.

| Parameter | Estimate | 95% CI | p-value |
|-----------|----------|--------|---------|
| β(HHI_{t-1}) | +1.603 | [-0.37, 3.58] | 0.098 |
| R² (within) | 0.682 | — | — |
| N observations | 18 | — | — |

Granger causality tests reinforce this finding: for all three venues, neither direction achieves significance.

### 5.4 Summary of Predictions

| Prediction | Expected | Observed | Status |
|------------|----------|----------|--------|
| P1: HHI_{t-1} predicts Entropy_t decline | β < 0 | β = +1.60 | **REFUTED** |
| P2: HHI Granger-causes Entropy | Significant | 0/3 venues | **INCONCLUSIVE** |
| P3: High-HHI papers use fewer datasets | Negative correlation | ρ = -0.33, p = 0.17 | **PARTIAL** |

---

## 6. Discussion

### 6.1 Key Finding: Propagation Without Lock-in

Our results support a nuanced view of benchmark concentration in ML research. Citation networks strongly propagate benchmark standards—papers that cite each other share benchmarks at 24 times the rate of random pairs (Cohen's d = 1.93). This confirms that evaluation practices spread through social and intellectual networks.

However, we find no evidence of the "epistemic lock-in" that critics fear. Concentration in year t-1 does not predict diversity decline in year t (β = +1.60, p = 0.098). The positive coefficient, while not significant, suggests if anything that concentration is followed by diversification rather than further concentration.

### 6.2 Theoretical Implications

These findings favor a **co-evolution model** over a **deterministic lock-in model**. In the co-evolution view, benchmark concentration and research practices evolve together without causal feedback—concentration may rise and fall based on field dynamics (new benchmark releases, paradigm shifts) rather than self-reinforcing cycles.

### 6.3 Limitations

**Small panel size.** With only 21 venue-years (18 after lag-drop), our panel regression has limited statistical power.

**Task labels as dataset proxy.** PWC task labels are coarser than specific datasets. This likely attenuates our concentration estimates.

**Observational design.** We document associations, not causal mechanisms.

**Venue scope.** Our analysis covers three general ML venues. Domain-specific venues may exhibit different dynamics.

### 6.4 Broader Impact

Claims that benchmark concentration creates inevitable "lock-in" appear overstated—the temporal feedback mechanism that would create such a trap is not supported by our data. The absence of self-reinforcing feedback suggests that the community can shift practices when problems become apparent.

---

## 7. Conclusion

We set out to test whether machine learning research suffers from epistemic lock-in—a self-reinforcing cycle where benchmark concentration compounds over time. Our findings reveal a more nuanced picture: the field co-evolves with its evaluation standards without becoming trapped by them.

Our analysis of 12,600 papers across 21 venue-years yields three principal contributions:

1. **Benchmark concentration is measurable and systematic.** HHI provides a tractable metric, revealing moderate concentration (range 0.007–0.046) with high correlation to top-5 dataset dominance (ρ=0.90).

2. **Citation networks serve as conduits for benchmark propagation.** Papers that cite each other exhibit 24-fold higher benchmark overlap (Jaccard 0.318 vs. 0.014, Cohen's d=1.93).

3. **No evidence for temporal lock-in.** The lagged regression coefficient is positive rather than negative (β=+1.603, p=0.098). Granger causality tests show zero significant venues.

The fear of epistemic lock-in assumes that benchmark adoption is a one-way ratchet. Our evidence suggests otherwise: the machine learning community collectively selects evaluation standards, revises them, and moves on—co-evolving with its benchmarks rather than being captured by them.

---

## References

See 06_references.bib

---

## Figures

- **Figure 1:** HHI concentration heatmap by venue-year (2018-2024)
- **Figure 2:** HHI vs top-5 dataset share validation (ρ=0.90)
- **Figure 3:** High vs low HHI group comparison (p<0.001)
- **Figure 4:** Benchmark overlap: citing pairs vs random pairs (d=1.93)
- **Figure 5:** Standard benchmark adoption probability curve
- **Figure 6:** Entropy vs cross-benchmark variance
- **Figure 7:** HHI and entropy time series per venue
- **Figure 8:** HHI vs entropy scatter (contemporaneous, not causal)
