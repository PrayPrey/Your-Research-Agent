# Methodology

We test whether benchmark concentration creates epistemic lock-in through a six-hypothesis framework that traces the mechanism chain from concentration measurement through citation propagation to temporal dynamics. Our data comes from Papers With Code, covering 12,600 papers from NeurIPS, ICML, and ICLR spanning 2018-2024.

## Data Collection and Coverage

Papers With Code provides structured information linking papers to the datasets they use for evaluation. We extract all entries for papers appearing at NeurIPS, ICML, or ICLR during our study period, yielding 12,600 papers with benchmark annotations. Coverage exceeds 80% of accepted papers at these venues, with variation across years as the platform has grown.

For each paper, we record the set of datasets used for evaluation, venue, year, and citation links to other papers in the corpus. Citation data comes from Semantic Scholar, matched to Papers With Code entries through paper identifiers. This enables analysis of both aggregate concentration patterns and paper-level propagation through citation networks.

We restrict attention to the top three machine learning venues to ensure comparability across papers. Benchmark practices may differ in application-specific venues or workshops; our focus is on whether the core machine learning research community exhibits lock-in dynamics.

## Concentration Operationalization

We measure benchmark concentration using the Herfindahl-Hirschman Index (HHI). For a given venue-year, let $N$ be the number of papers and let $n_d$ be the count of papers using dataset $d$. The share for dataset $d$ is $s_d = n_d / N$. HHI is then:

$$\text{HHI} = \sum_d s_d^2$$

This metric has a natural interpretation: it equals the probability that two papers drawn uniformly at random from the venue-year evaluate on at least one common dataset. HHI ranges from $1/D$ (uniform distribution across $D$ datasets) to 1 (all papers use the same dataset). Higher values indicate greater concentration.

We validate HHI against a simpler metric: the combined share of the five most-used datasets. If HHI captures concentration appropriately, it should correlate strongly with this intuitive measure. Figure 2 displays this relationship, and we report correlation statistics in our results.

## Hypothesis Framework

Our analysis proceeds through six sub-hypotheses organized as a mechanism chain. The first two establish measurement validity; the next three test propagation mechanisms; the final hypothesis tests temporal feedback.

**H-E1 (Existence):** HHI can be computed for all venue-years in our sample. This confirms data sufficiency—if many venue-years lack enough benchmark annotations, the analysis would be unreliable.

**H-M1 (Metric Validity):** HHI correlates with simpler concentration measures. We compute Spearman correlation between HHI and top-5 dataset share across venue-years. Strong correlation validates HHI as capturing the intended construct.

**H-M2 (Prior Concentration Predicts Adoption):** Papers are more likely to adopt standard benchmarks when prior concentration is higher. We fit logistic regression predicting whether each paper uses a top-5 benchmark as a function of the prior year's HHI at the same venue, controlling for paper-level covariates.

**H-M3 (Citation Propagation):** Papers share more benchmark overlap with papers they cite than with random papers. For each paper $i$, we compute Jaccard similarity between $i$'s benchmark set and the union of benchmark sets among $i$'s references. We compare against Jaccard similarity with random non-cited papers from the same venue-year.

**H-M4 (Entropy-Variance Relationship):** If concentration constrains diversity, benchmark entropy should negatively correlate with HHI. We compute Shannon entropy of the benchmark distribution for each venue-year and correlate with HHI.

**H-M5 (Temporal Lock-In):** If lock-in exists, prior HHI should causally reduce subsequent benchmark entropy. We test this with panel regression:

$$\text{Entropy}_{v,t} = \alpha + \beta \cdot \text{HHI}_{v,t-1} + \gamma_v + \delta_t + \epsilon_{v,t}$$

where $\gamma_v$ represents venue fixed effects and $\delta_t$ represents year fixed effects. Significant negative $\beta$ would indicate lock-in; we additionally conduct Granger causality tests.

## Panel Regression Specification

The temporal lock-in test (H-M5) is our primary contribution. We construct a panel with 21 observations: 3 venues $\times$ 7 years (using lagged HHI, so effective years are 2019-2024 with 2018 providing the lag).

Venue fixed effects control for persistent differences in benchmark practices across venues—ICLR may emphasize different benchmark types than NeurIPS. Year fixed effects control for community-wide trends—overall growth in benchmark availability or methodological shifts affecting all venues. The coefficient $\beta$ on lagged HHI then identifies the within-venue, within-year relationship between prior concentration and subsequent diversity.

We report coefficient estimates, standard errors, and p-values. For robustness, we conduct Granger causality tests examining whether lagged HHI improves prediction of entropy beyond autoregressive terms. Lock-in requires both significant regression coefficients and significant Granger causality; absence of either provides evidence against the lock-in hypothesis.

## Propagation Analysis

The citation propagation test (H-M3) provides mechanism evidence complementing the temporal analysis. For each paper $i$ in our corpus with at least one citation to another corpus paper, we identify the reference set $R_i$. We compute:

$$J_{\text{cited}} = \frac{|B_i \cap B_{R_i}|}{|B_i \cup B_{R_i}|}$$

where $B_i$ is paper $i$'s benchmark set and $B_{R_i}$ is the union of benchmark sets across references. We compare against $J_{\text{random}}$ computed using random papers from the same venue-year not cited by $i$.

Effect size (Cohen's $d$) quantifies the separation between cited and random overlap distributions. Large effects confirm that benchmarks propagate through citations; this establishes the mechanism even if temporal feedback is absent.

## Visualization

Figure 1 presents a heatmap of HHI values across venues and years, illustrating variation in concentration. Figure 2 plots HHI against top-5 dataset share to validate the concentration metric. Additional figures display the Jaccard similarity distributions for cited versus random papers (H-M3) and the panel regression residuals (H-M5).

Our analysis code and data are available at [repository URL] to enable replication and extension.
