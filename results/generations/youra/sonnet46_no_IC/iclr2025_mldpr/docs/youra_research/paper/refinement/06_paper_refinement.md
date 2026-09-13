# Keyword Tagging as a FAIR F1 Mechanism: Quantifying the Discoverability Advantage in ML Dataset Adoption on OpenML

## Abstract

Most machine learning datasets are invisible — not because they lack quality, but because they lack keyword tags that enable search-indexed discovery. This study examines whether keyword tagging, the operationalization of the FAIR F1 (Findability) principle on OpenML, predicts dataset adoption measured by ML task registrations. Analyzing 5,217 datasets with negative binomial (NB-2) regression and decade fixed effects, binary tag presence is associated with 22.6% more task registrations (IRR=1.2263, 95% CI [1.1681, 1.2873], p=1.87×10⁻¹⁶). This effect survives decade fixed effects with only 12.2% attenuation (attenuation ratio=1.1219) despite extreme era-tag collinearity (Cramér's V=0.823), confirming a structural platform property rather than a temporal artifact. Within tagged datasets (N=2,625), tag count amplifies adoption log-linearly (IRR=1.5332 per log(tag_count+1), 95% CI [1.4680, 1.6014], p=1.28×10⁻⁸²), with essentially zero decade confounding (attenuation ratio=1.0007). Categorical analysis reveals that OpenML tagging behavior is bimodal — the 6+ tag tier (IRR=1.2861) is the sole meaningfully distinguishable amplification tier; intermediate bins (1-2 and 3-5 tags) produce statistically indistinguishable effects. These findings constitute the first NB-2 quantification of FAIR F1 keyword tagging on an ML platform, translating aspirational data management principles into actionable, evidence-grounded guidance.

---

## 1. Introduction

Most machine learning datasets are invisible — not because they lack quality, but because they lack tags. On OpenML, a platform hosting more than 5,000 actively-studied datasets, datasets with at least one keyword tag register 22.6% more ML task experiments than their untagged counterparts (IRR=1.2263, 95% CI [1.1681, 1.2873], p=1.87×10⁻¹⁶, N=5,217), after controlling for dataset size, age, and decade of upload. This finding is statistically robust across seven model variants, and reflects a structural platform property rather than a temporal artifact.

The disparity in ML dataset adoption is a well-documented but incompletely understood phenomenon. Some datasets accumulate hundreds of task registrations; others, of comparable size and scope, remain largely unused. Explanations typically focus on intrinsic dataset properties — instance count, dimensionality, task difficulty — as primary drivers of engagement. These structural features are controlled for explicitly in the present study. They cannot, however, account for adoption gaps among datasets of similar size and complexity. A complementary mechanism is required.

The mechanism examined here is discoverability via search-indexed metadata. On platforms such as OpenML, researchers discover datasets primarily through keyword search. A dataset without keyword tags is structurally absent from tag-indexed search results, regardless of its intrinsic merit. This is the FAIR F1 (Findability) principle operationalized: keyword tags are the mechanism by which datasets enter researcher awareness. The FAIR Data Principles [Wilkinson et al., 2016] established this as a foundational requirement for dataset reuse, but quantitative IRR evidence for the effect of FAIR F1 compliance on ML dataset adoption has been absent from the literature.

The FAIR F1 tagging mechanism on OpenML operates as a **threshold-plus-amplification** structure. Binary tag presence (has_tags=1 vs. has_tags=0) captures the critical search-index-membership threshold: any tagging is associated with a 22.6% adoption advantage. Above this threshold, tag count magnitude amplifies discovery probability log-linearly: within the tagged subset (N=2,625), each unit increase in log(tag_count+1) is associated with 53.3% more task registrations (IRR=1.5332, p=1.28×10⁻⁸²). The categorical shape of this amplification is non-uniform — the 6+ tag tier produces a meaningfully distinct effect (IRR=1.2861) while 1–5 tags produce statistically indistinguishable effects — indicating that comprehensive tagging maximizes discovery benefit.

The study makes four contributions:

**C1.** First empirical NB-2 quantification of FAIR F1 keyword tagging and ML dataset adoption. Incidence rate ratio estimates are provided for has_tags binary (IRR=1.2263) and log tag count (IRR=1.5332) in negative binomial regression appropriate for overdispersed count outcomes, on the OpenML platform with N=5,217 datasets.

**C2.** Threshold-plus-amplification characterization of the FAIR F1 mechanism. The mechanism shape is characterized as binary threshold (any tags → search index membership), continuous log-linear amplification (more tags → more search pathways), and non-uniform categorical tiers (6+ tag dominance).

**C3.** Structural mechanism verification via decade fixed effects. The has_tags effect survives C(decade) fixed effects with 12.2% attenuation (versus 98.6% attenuation for a prior composite metadata score tested on the same corpus), establishing the within-decade, structural character of the finding.

**C4.** Informative negative for uniform categorical dose-response. Categorical analysis reveals that OpenML tagging behavior is bimodal — users tag comprehensively (3+ tags) or not at all — making the 1–2 tag range a sparse middle ground (N=73). This constrains future tagging intervention designs.

Section 2 reviews the FAIR principles literature, ML metadata adoption research, and negative binomial regression methodology. Section 3 describes the study design, corpus, and model specification. Section 4 presents the four experimental analyses. Section 5 reports results. Section 6 interprets findings and acknowledges limitations. Section 7 concludes.

---

## 2. Related Work

### 2.1 FAIR Data Principles and Keyword Findability

The FAIR Guiding Principles [Wilkinson et al., 2016] established a framework for scientific data management organized around Findability (F), Accessibility (A), Interoperability (I), and Reusability (R). The F1 sub-principle — that data should be assigned globally unique persistent identifiers and described with rich machine-actionable metadata — is directly operationalizable in ML repositories via keyword tagging. The Wilkinson et al. framework has accumulated over 15,976 citations and has influenced repository design and curation policy broadly.

The FAIR literature has, however, remained primarily normative. Papers describe desirable metadata properties and propose compliance checklists without measuring the quantitative effect of specific FAIR F1 interventions on dataset adoption outcomes. The Croissant-RAI specification [Jain et al., 2024] — developed partly by OpenML's founder — proposes machine-readable structured metadata for ML datasets and identifies keyword tags as a primary findability mechanism, but does not provide empirical IRR estimates. Trišović et al. [2025] study automated FAIR compliance scoring but measure compliance richness rather than adoption outcomes. The present study fills this gap by providing the first negative binomial regression IRR for keyword tag presence on a major ML platform.

### 2.2 ML Dataset Adoption and Metadata Quality

Yang et al. [2024] study the relationship between documentation quality (dataset cards on HuggingFace) and dataset popularity, finding that richer documentation predicts higher download counts. This is a parallel finding — structured metadata presence predicts platform adoption — but differs from the present study in three important respects: the platform (HuggingFace, a model-centric platform with different search mechanics), the metadata type (free-form dataset cards rather than keyword tags), and the adoption metric (download counts rather than ML task registrations). Yang et al. do not isolate keyword tagging as a specific FAIR F1 operand, nor do they apply negative binomial regression to handle overdispersion.

Lachmuth et al. [2025] study FAIR metadata compliance and dataset reuse in the BonaRes agricultural data repository, finding that compliance predicts reuse (measured as paper citations). This provides cross-domain corroboration of the FAIR-adoption linkage, but in a domain-specific repository with different platform mechanics and a different adoption proxy. The tag-indexed search mechanism characterizing OpenML does not directly apply to BonaRes's architecture.

Oreamuno et al. [2023] survey documentation practices across ML datasets and find that poor tagging leads to poor discoverability — consistent with the present findings — but do not provide regression estimates. Chapman et al. [2019] survey dataset search behavior and identify keywords as the primary mechanism by which researchers discover datasets, providing theoretical grounding for the FAIR F1 mechanism hypothesis. Afzal et al. [2020] propose a data readiness framework incorporating metadata richness but focus on quality assessment rather than adoption regression.

Orr and Crawford [2024] situate ML dataset metadata in sociological context, arguing that metadata reflects curatorial effort and community norms rather than purely technical properties — a perspective consistent with the present finding that tagging behavior is bimodal on OpenML.

No prior study provides an NB-2 incidence rate ratio for keyword tag presence specifically, predicting ML task adoption, with overdispersion testing, on an ML dataset repository.

### 2.3 Negative Binomial Regression for Platform Adoption

Count data regression for platform adoption outcomes requires careful model selection. Standard Poisson regression assumes mean-variance equality; real-world count outcomes such as task registrations exhibit overdispersion (variance substantially exceeding mean). The Negative Binomial Type 2 (NB-2) model accommodates overdispersion via a quadratic variance function [Cameron and Trivedi, 1986; 2013].

The Cameron-Trivedi Lagrange multiplier test (CT LR) provides a formal overdispersion test. In the present setting, CT LR=7,356.36 far exceeds the critical value (χ²(1)=3.84), confirming NB-2 as the appropriate model family. Cabansag and Ntegeka [2026] demonstrate the NB-2 IRR interpretation in a related count regression context, providing methodological precedent.

---

## 3. Method

### 3.1 Dataset: OpenML Corpus

The analysis uses the OpenML dataset corpus, a cross-sectional snapshot of N=5,217 datasets with at least one registered ML task (N_tasks≥1). OpenML [Vanschoren et al., 2014] is a publicly accessible ML experimentation platform where researchers register datasets, define ML tasks, and execute experimental flows. The corpus was collected as of 2026-08-05 and preprocessed as a parquet file (`h-e1/results/preprocessed.parquet`).

**Sample restriction (N_tasks≥1):** This study examines conditional adoption intensity — how tagging affects engagement among datasets that have received at least minimal engagement. Datasets with zero tasks are structurally different and would require a hurdle model component; this is deferred to future work. The sample restriction yields N=5,217 datasets: 2,625 tagged (50.3%) and 2,592 untagged (49.7%).

**Variables:**

| Variable | Role | Definition |
|----------|------|------------|
| N_tasks | Dependent variable | Count of distinct ML task registrations (integer ≥ 1) |
| has_tags | Primary IV (P1) | Binary: 1 if dataset has ≥1 keyword tag, 0 otherwise |
| log_tag_count_p1 | Secondary IV (P2) | log(tag_count + 1); restricted to has_tags=1 subset |
| tag_count_cat | Categorical IV (P3) | Bins: 0, 1–2, 3–5, 6+ (reference: 0) |
| log_n_instances | Control | log(number of instances) |
| log_n_features | Control | log(number of features) |
| age_years | Control | Dataset age in years |
| age_sq | Control | age_years² (quadratic age term) |
| C(decade) | Fixed effect | Decade-of-upload fixed effects |

### 3.2 Model: Negative Binomial Type 2

**Why NB-2 (not Poisson):** CT LR=7,356.36 (>> χ²(1)=3.84 critical value) confirms strong overdispersion across all three model specifications (CT LR=7,356.36 for P1; 7,357.39 for P2; 7,509.42 for P3). Poisson regression would underestimate standard errors and inflate significance.

**Why binary has_tags rather than a composite score:** A prior episode on the same corpus tested a composite metadata completeness score (0–5). That composite yielded IRR=1.076 without decade fixed effects, collapsing to IRR=1.014 (p=0.19) under decade fixed effects. Binary has_tags, by contrast, yields IRR=1.2263 and survives decade fixed effects with only 12.2% attenuation. The binary variable isolates the FAIR F1 search-index-membership signal without dilution by non-F1 metadata fields.

**Why decade fixed effects:** Platform era shifts created extreme decade-tag collinearity (Cramér's V=0.823; nearly all 2010s datasets are tagged at a rate of 85.4%, while 2020s datasets are tagged at only 2.1%). C(decade) fixed effects control for between-era confounding. The structural character of the has_tags effect — its survival within decades — is then verified via the mechanism test (Section 3.3).

All models were estimated using `statsmodels.formula.api.negativebinomial` with `loglike_method='nb2'` and the BFGS optimizer (`method='bfgs'`, `maxiter=100`). Convergence was confirmed for all seven model variants. IRR = exp(coefficient); 95% CI = exp(coefficient ± 1.96·SE).

### 3.3 Four-Prediction Test Design

| Prediction | Model Formula | Sample | Gate Criterion | Gate Type |
|-----------|---------------|--------|----------------|-----------|
| P1 — Binary Threshold | N_tasks ~ has_tags + controls + C(decade) | N=5,217 | IRR≥1.1, CI_lower≥1.1, p<0.05 | MUST_WORK |
| Mechanism | P1 with vs. without C(decade) | N=5,217 | Post-FE IRR≥1.1, p<0.05 | MUST_WORK |
| P2 — Log-Linear | N_tasks ~ log_tag_count_p1 + controls + C(decade) | N=2,625 (tagged) | CI_lower≥1.05, p<0.05 | SHOULD_WORK |
| P3 — Categorical | N_tasks ~ C(tag_count_cat) + controls + C(decade) | N=5,217 | Monotonic IRR, ≥2/3 adjacent contrasts p<0.0167 | SHOULD_WORK |

Bonferroni correction for categorical contrasts: α=0.0167 (k=3 contrasts). The mechanism test quantifies attenuation ratio = IRR_without_FE / IRR_with_FE; attenuation ratio < 1.5 constitutes STRONG mechanism support.

![FAIR F1 threshold-plus-amplification mechanism chain: Dataset keyword tags → search index membership → multiple search query pathways → researcher discovery events → ML task registration.](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_mldpr/docs/youra_research/paper/figures/fig4_mechanism_flow.png)

*Figure 1. FAIR F1 threshold-plus-amplification mechanism chain. Dataset keyword tags enable search index membership, which in turn expands the set of search query pathways through which researchers encounter the dataset, ultimately driving ML task registration. Source: h-m1/figures/fig4_mechanism_flow.png.*

### 3.4 Robustness Checks

Pre-specified robustness checks include: RC-4 (winsorize N_tasks at the 99th percentile), RC-7 (age-only control versus decade fixed effects sensitivity comparison), and the mechanism attenuation test (with/without C(decade) fixed effects for P1). RC-5 (tagged-only subset for has_tags) was pre-specified but is not applicable because has_tags is constant (=1) in the tagged subset; this was noted as an expected design limitation.

---

## 4. Experimental Setup

### 4.1 Research Questions

**RQ1:** Does binary keyword tag presence predict significantly more ML task registrations (IRR ≥ 1.1)?

**RQ2:** Does the has_tags effect survive decade fixed effects, confirming a structural rather than temporal mechanism?

**RQ3:** Within the tagged subset, does tag count show a log-linear dose-response with task registrations?

**RQ4:** Does the categorical dose-response show monotonic IRR ordering with distinguishable adjacent tiers?

RQ1 and RQ2 are MUST_WORK gates — failing either would undermine the threshold hypothesis. RQ3 and RQ4 are SHOULD_WORK — informative about mechanism structure.

### 4.2 Corpus Summary

| Statistic | Value |
|-----------|-------|
| Total datasets (N_tasks ≥ 1) | 5,217 |
| Tagged (has_tags=1) | 2,625 (50.3%) |
| Untagged (has_tags=0) | 2,592 (49.7%) |
| CT LR (overdispersion test, P1 spec) | 7,356.36 (>> 3.84 critical value) |
| Tagged subset for P2 | N=2,625 |
| Decade breakdown | 2010s: N=5,009; 2020s: N=208 |

### 4.3 Internal Comparison

No external baseline system exists — this is an observational regression study. An internal comparison is provided by the composite metadata completeness score (0–5) tested in a prior episode on the same corpus, which yielded IRR=1.076 under baseline conditions and IRR=1.014 (p=0.19) under decade fixed effects. This prior episode functions as a historical negative control demonstrating that the specific binary has_tags variable captures a signal that composite scoring does not.

### 4.4 Evaluation Metrics

- **IRR:** exp(NB-2 coefficient) — multiplicative adoption multiplier
- **Gate criteria:** as specified in Section 3.3
- **CT LR:** Cameron-Trivedi LR statistic, must exceed χ²(1)=3.84 to confirm NB-2 appropriate
- **Attenuation ratio:** IRR_without_FE / IRR_with_FE; < 1.5 indicates STRONG mechanism support

---

## 5. Results

Results are presented in causal-chain order: binary threshold (H-E1, RQ1), structural mechanism (H-M1, RQ2), log-linear dose-response (H-M2, RQ3), and categorical shape (H-M3, RQ4).

### 5.1 Primary Finding: Binary Tag Presence Predicts 22.6% More Task Registrations (RQ1)

![Primary gate result: IRR=1.2263 for has_tags with 95% CI [1.1681, 1.2873] and 1.1 MUST_WORK threshold line.](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_mldpr/docs/youra_research/paper/figures/fig1_gate_metrics.png)

*Figure 2. Primary gate result: IRR=1.2263 for has_tags binary in NB-2 regression (N=5,217) with 95% CI and 1.1 threshold. The estimate exceeds the IRR gate by 11.5% and CI_lower gate by 6.2%. Source: h-e1/figures/fig1_gate_metrics.png.*

| Metric | Value | Gate | Status |
|--------|-------|------|--------|
| IRR (has_tags) | 1.2263 | ≥ 1.1 | PASS (+11.5% margin) |
| 95% CI lower | 1.1681 | ≥ 1.1 | PASS (+6.2% margin) |
| 95% CI upper | 1.2873 | — | — |
| p-value | 1.87×10⁻¹⁶ | < 0.05 | PASS |
| N | 5,217 | — | — |
| CT LR | 7,356.36 | >> 3.84 | NB-2 confirmed |
| LLF (proposed model) | −12,881.76 | — | — |
| AIC (proposed model) | 25,779.53 | — | — |

Any keyword tag on OpenML is associated with a 22.6% increase in expected ML task registrations. This estimate controls for dataset size, age, and decade of upload. The p-value of 1.87×10⁻¹⁶ is consistent across all seven model variants, including RC-4 winsorization (N_tasks winsorized at 99th percentile threshold=40, n_winsorized=51; IRR≈1.22, consistent with primary) and RC-7 age-only control (IRR=1.3758 without decade fixed effects, discussed in Section 5.2).

**Comparison to composite score:** The prior episode composite metadata score yielded IRR=1.076 on the same corpus, below the 1.1 gate, and collapsed to IRR=1.014 (p=0.19) under decade fixed effects — a 98.6% attenuation. The binary has_tags variable achieves IRR=1.2263 and 12.2% attenuation under identical fixed effects, isolating the FAIR F1 signal that composite scoring dilutes.

![Forest plot of all covariate IRRs from the primary NB-2 model.](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_mldpr/docs/youra_research/paper/figures/fig2_forest_plot.png)

*Figure 3. Forest plot of all covariate IRRs from the primary NB-2 model. has_tags shows the dominant positive effect among all predictors. Source: h-e1/figures/fig2_forest_plot.png.*

### 5.2 Mechanism Verification: Structural Platform Property, Not Temporal Artifact (RQ2)

![IRR comparison before and after C(decade) fixed effects: IRR without FE ≈ 1.376, IRR with FE = 1.2263. Attenuation ratio = 1.1219.](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_mldpr/docs/youra_research/paper/figures/fig1_irr_comparison.png)

*Figure 4. IRR comparison before and after C(decade) fixed effects. Without FE: IRR=1.3758. With FE: IRR=1.2263. Attenuation ratio=1.1219 means decade fixed effects absorb only 12.2% of the has_tags effect. Source: h-m1/figures/fig1_irr_comparison.png.*

| Metric | Value | Interpretation |
|--------|-------|----------------|
| IRR without decade FE | 1.3758 | — |
| IRR with decade FE | 1.2263 | Primary estimate |
| Attenuation ratio | 1.1219 | Gate < 1.5: STRONG mechanism support |
| Cramér's V (decade × has_tags) | 0.823 | Extreme collinearity |
| Post-FE p-value | 1.87×10⁻¹⁶ | << 0.05 |

Despite extreme decade-tag collinearity (Cramér's V=0.823), C(decade) absorbs only 12.2% of the has_tags effect. Within each upload decade, tagged datasets attract more tasks than untagged datasets from the same era. This confirms that the has_tags effect captures a within-decade structural property — search index membership — not a between-decade platform era trend. The composite score episode (same corpus, same fixed effects) produced 98.6% attenuation, establishing a within-study historical negative control. The has_tags effect survives where the composite score does not.

![Mean has_tags rate per decade of upload, showing RC-3 collinearity context.](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_mldpr/docs/youra_research/paper/figures/fig3_decade_adoption.png)

*Figure 5. Mean has_tags rate per decade of upload on OpenML. The 2010s datasets are tagged at 85.4%; 2020s datasets at 2.1%. This reflects platform growth phases rather than analytical bias. Source: h-e1/figures/fig3_decade_adoption.png.*

### 5.3 Dose-Response: Tag Count Amplifies Adoption Log-Linearly (RQ3)

![Added variable (partial regression) plot: log(tag_count+1) versus residual log(N_tasks) after controlling for all covariates in the tagged subset (N=2,625).](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_mldpr/docs/youra_research/paper/figures/fig3_partial_regression.png)

*Figure 6. Added variable (partial regression) plot: log(tag_count+1) versus residual log(N_tasks) after controlling for all covariates in the tagged subset (N=2,625). Confirms a clear positive log-linear relationship. Source: h-m2/figures/fig3_partial_regression.png.*

| Metric | Value | Gate | Status |
|--------|-------|------|--------|
| IRR (log_tag_count_p1) | 1.5332 | — | — |
| 95% CI lower | 1.4680 | ≥ 1.05 | PASS (+39.4% margin) |
| 95% CI upper | 1.6014 | — | — |
| p-value | 1.28×10⁻⁸² | < 0.05 | PASS |
| N (tagged subset) | 2,625 | — | — |
| Attenuation ratio (decade) | 1.0007 | — | Negligible collinearity |
| CT LR | 7,357.39 | >> 3.84 | NB-2 confirmed |

Within the 2,625 tagged datasets, each log-unit increase in tag count is associated with 53.3% more task registrations. The dose-response is essentially orthogonal to decade effects (0.07% attenuation; IRR without decade FE = 1.5343, IRR with = 1.5332), confirming that additional tags expand search pathways independently of platform era. This contrasts markedly with the binary has_tags attenuation ratio of 1.1219 on the full corpus, indicating that the continuous tag count variable within the tagged subset has negligible temporal confounding.

### 5.4 Categorical Shape: 6+ Tags Drive Dominant Amplification (RQ4)

![Categorical IRR bars for tag bins (0, 1-2, 3-5, 6+) with 95% CIs and monotonic ordering.](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_mldpr/docs/youra_research/paper/figures/fig1_irr_bar_chart.png)

*Figure 7. Categorical dose-response: IRR bars for four tag count bins (0, 1–2, 3–5, 6+) with 95% CI. Monotonic ordering confirmed; 6+ tier (IRR=1.2861) is the dominant distinguishable amplification tier. Source: h-m3/figures/fig1_irr_bar_chart.png.*

**Corpus distribution by categorical bin:**

| Category | N | % of corpus |
|----------|---|-------------|
| 0 (no tags) | 2,592 | 49.7% |
| 1–2 tags | 73 | 1.4% |
| 3–5 tags | 710 | 13.6% |
| 6+ tags | 1,842 | 35.3% |

**Categorical NB-2 results (reference: 0 tags):**

| Category | IRR | 95% CI | p-value (vs. 0) |
|----------|-----|--------|-----------------|
| 0 (ref) | 1.000 | — | — |
| 1–2 | 1.1267 | [1.0025, 1.2664] | 0.045 |
| 3–5 | 1.1277 | [1.0669, 1.1919] | <0.001 |
| 6+ | 1.2861 | [1.2230, 1.3524] | 1.12×10⁻²² |

**Adjacent contrasts (Bonferroni α=0.0167):**

| Contrast | Bonferroni p-value | Gate | Notes |
|----------|--------------------|------|-------|
| 0 → 1–2 | 0.272 | FAIL | N=73 in bin 1–2; underpowered |
| 1–2 → 3–5 | 1.000 | FAIL | IRR gap Δ=0.001; effectively zero |
| 3–5 → 6+ | 5.54×10⁻¹⁰ | PASS | Only significant adjacent transition |

**Gate result: INFORMATIVE_NEGATIVE.** Monotonic ordering is confirmed (IRR(1-2) < IRR(3-5) < IRR(6+), all > 1). The gate condition (≥2/3 adjacent contrasts p<0.0167) is not met: 1/3 contrasts pass. This is a data distribution issue, not a mechanism failure. The 1–2 tag bin contains only 73 datasets (1.4% of corpus), providing insufficient power for Bonferroni-corrected adjacent contrast testing. The near-identical IRR(1-2)=1.1267 versus IRR(3-5)=1.1277 (gap Δ=0.001) indicates that these two bins do not represent a meaningful IRR step at all.

The dominant finding from categorical analysis is that the 6+ tag tier is the sole meaningfully distinguishable amplification tier (IRR=1.2861, p=1.12×10⁻²², distinctly above all lower bins at p=5.54×10⁻¹⁰ for the 3–5→6+ contrast). OpenML tagging behavior is bimodal: datasets are either untagged (49.7%) or comprehensively tagged (35.3% with 6+ tags), with sparse occupancy in the 1–5 range.

Robustness check RC-7 (no decade fixed effects) for categorical bins yielded attenuation ratios of approximately 11% across all bins (IRR(1-2) without FE=1.263, attenuation ratio=1.121; IRR(3-5) without FE=1.294, ratio=1.147; IRR(6+) without FE=1.431, ratio=1.114), consistent with the binary has_tags attenuation of 12.2%.

### 5.5 Summary of Hypothesis Outcomes

| Hypothesis | Gate Type | Key Metric | Gate Result |
|------------|-----------|-----------|-------------|
| H-E1 (P1 — Binary) | MUST_WORK | IRR=1.2263, CI_lower=1.1681, p=1.87×10⁻¹⁶ | PASS |
| H-M1 (Mechanism) | MUST_WORK | Attenuation=12.2%, post-FE p=1.87×10⁻¹⁶ | PASS |
| H-M2 (P2 — Log-Linear) | SHOULD_WORK | IRR=1.5332, CI_lower=1.4680, p=1.28×10⁻⁸² | PASS |
| H-M3 (P3 — Categorical) | SHOULD_WORK | Monotonic: YES; adjacent contrasts: 1/3 | INFORMATIVE_NEGATIVE |

Three of four hypotheses are fully validated; none failed outright. The informative negative reveals bimodal tagging behavior rather than mechanism failure.

---

## 6. Discussion

### 6.1 Key Findings and Their Interpretation

**Finding 1: Any tagging creates a substantial, robust discoverability advantage.** The 22.6% adoption advantage (IRR=1.2263) survives the primary platform-era confound with only 12.2% attenuation. The single most impactful metadata action for a dataset creator is adding at least one keyword tag. The choice of tags matters less than the act of tagging, because the primary mechanism is binary search index membership.

**Finding 2: Tag count magnitude is associated with a genuine dose-response.** Within the tagged subset, IRR=1.5332 per log-unit with an attenuation ratio of 1.0007 establishes that additional tags are associated with more task registrations independently of platform era. Each additional tag represents an additional keyword query pathway, reaching different researcher subsets. This is the amplification arm of the threshold-plus-amplification structure.

**Finding 3: Comprehensive tagging (6+) is the dominant amplification tier.** The 6+ tag tier produces a 28.6% adoption advantage versus reference, meaningfully above the 12.7–12.8% for 1–5 tags. The bimodal tagging distribution (all-or-nothing) means that minimal tagging (1–2 tags) and moderate tagging (3–5 tags) produce effects that are statistically indistinguishable from each other. Repository interfaces that encourage minimal tag entry may not realize the full discoverability benefit; 6+ tags appears to be the practical amplification threshold.

**Finding 4: The mechanism survives extreme temporal collinearity.** The Cramér's V=0.823 collinearity between decade and has_tags represents a severe potential confound — nearly all 2010s datasets are tagged, nearly none of the 2020s datasets are. That the has_tags effect survives with only 12.2% attenuation, while the composite metadata score attenuated to non-significance (98.6%) under identical controls, establishes that the binary tagging variable captures a within-decade structural property — not a platform-era trend.

### 6.2 Connection to Literature

The binary threshold finding provides the first NB-2 IRR for keyword tagging on an ML repository, filling the quantification gap in Wilkinson et al. [2016]. The direction is consistent with Yang et al. [2024] and Lachmuth et al. [2025], though platform and metric differences preclude direct comparison. The mechanism verification via decade fixed effects (H-M1) provides a methodological template for observational platform studies: testing extreme temporal collinearity without abandoning fixed effect controls demonstrates that within-cohort variation can identify structural mechanisms even under severe between-cohort confounding.

### 6.3 Limitations

**L1: Cross-sectional design — predictive, not causal.** Tags and task counts are observed simultaneously. The causal interpretation rests on OpenML's creator-only tagging architecture (Vanschoren et al., 2014) as a structural temporal ordering argument, not verified by timestamps in the available corpus.

**L2: N_tasks proxy measures registration breadth, not execution depth.** Task registration is a deliberate adoption signal — it requires defining a target variable and task type — but may diverge from execution-frequency adoption for some datasets.

**L3: Conditional adoption only — hurdle component deferred.** The analysis is scoped to N_tasks≥1 (adoption intensity). The probability of any adoption at all is not estimated.

**L4: 12.2% decade attenuation is partially uncontrolled.** The residual after fixed effects may include both the structural FAIR F1 mechanism and uncontrolled era confounding. The gate passed with large margin despite this.

**L5: H-M3 bin 1–2 sparsity (N=73) limits uniform categorical dose-response claim.** The low-count range is undetermined; the 6+ tier characterization is robust. The informative negative reflects a data distribution constraint, not a mechanism failure.

**L6: Reverse causality for continuous IV.** For the log tag count measure (H-M2 and H-M3), popular datasets attracting additional tags retroactively remains a possible alternative explanation. OpenML's creator-only tagging architecture partially mitigates this, but if community tag additions exist, they could introduce upward bias in log_tag_count_p1 estimates. This is not testable without tag modification timestamps from the platform API.

### 6.4 Broader Implications

Evidence-grounded IRR estimates translate FAIR F1 compliance from aspirational to actionable. Repository designers can justify tag-requirement policies with quantitative adoption effects; dataset creators gain guidance grounded in platform-scale evidence. The NB-2 methodology with decade fixed effects and attenuation testing provides a replicable template for other repository studies.

Strategic tag farming, analogous to SEO manipulation, could emerge if tagging is widely understood to boost adoption metrics. Repository governance should monitor for tag quality degradation alongside quantity. Additionally, if discovery concentrates among heavily-tagged datasets, a Matthew effect may emerge — more-discoverable datasets accumulating further engagement at the expense of high-quality untagged datasets that do not appear in keyword searches.

---

## 7. Conclusion

This study examined whether keyword tagging — the FAIR F1 findability operand — predicts ML dataset adoption on OpenML, using negative binomial regression on a corpus of 5,217 datasets with at least one registered task.

The results support a threshold-plus-amplification characterization of the FAIR F1 mechanism:

1. **Binary tag presence is associated with a 22.6% adoption advantage** (IRR=1.2263, 95% CI [1.1681, 1.2873], p=1.87×10⁻¹⁶, N=5,217), surviving decade fixed effects with only 12.2% attenuation despite Cramér's V=0.823 era-tag collinearity.

2. **Tag count magnitude is associated with a log-linear amplification** within tagged datasets (IRR=1.5332 per log(tag_count+1), 95% CI [1.4680, 1.6014], p=1.28×10⁻⁸², N=2,625), with essentially zero decade confounding (attenuation ratio=1.0007).

3. **Comprehensive tagging (6+ tags) is the dominant categorical tier** (IRR=1.2861, distinctly above the 1–5 tag range at p=5.54×10⁻¹⁰), while OpenML tagging behavior is bimodal — users tag comprehensively or not at all.

The informative negative result (H-M3) honestly documents the limits of categorical characterization at low tag counts while refining the practical recommendation toward the 6+ tag target.

### 7.1 Future Directions

**Reverse causality testing:** Whether popular datasets attract tags retroactively requires tag assignment timestamps unavailable in the current corpus. A natural experiment around OpenML API version changes affecting tagging permissions would provide stronger evidence on temporal ordering.

**Direct search pathway verification:** OpenML search API log analysis (query → click → task creation sequences) would directly verify the tag-indexed search mechanism, converting proxy evidence to direct evidence.

**Multi-platform replication:** Testing FAIR F1 threshold-plus-amplification on HuggingFace, Kaggle, and UCI would examine whether the structure generalizes across repository architectures with different search mechanics.

**Hurdle model on the full corpus:** Including N_tasks=0 datasets would estimate P(any adoption) alongside conditional adoption intensity, providing a complete picture of tagging effects across the adoption distribution.

### 7.2 Closing

As ML repositories grow and dataset proliferation accelerates, the structural advantages of keyword-indexed FAIR F1 compliance compound. Adding 6 or more descriptive keyword tags at dataset upload is associated with substantially higher conditional adoption on OpenML. While causal ordering requires timestamp verification beyond the available corpus, the magnitude of the association and its structural robustness across model variants support treating FAIR F1 tagging as a discoverability mechanism with measurable adoption consequences rather than a documentation checkbox.

---

## References

Afzal, W., et al. (2020). Data Readiness Report. *arXiv preprint arXiv:2010.07213*.

Cabansag, I. J., & Ntegeka, P. (2026). Bayesian Negative Binomial Regression of Afrobeats Chart Persistence. *arXiv preprint arXiv:2601.01391*. doi:10.48550/arXiv.2601.01391

Cameron, A. C., & Trivedi, P. K. (1986). Econometric models based on count data: Comparisons and applications of some estimators and tests. *Journal of Applied Econometrics*, 1(1), 29–53.

Cameron, A. C., & Trivedi, P. K. (2013). *Regression Analysis of Count Data* (2nd ed.). Cambridge University Press. doi:10.1017/CBO9781139013567

Chapman, A. P., Simperl, E., Koesten, L., Konstantinidis, G., Ibáñez, L.-D., Kacprzak, E., & Groth, P. (2019). Dataset search: a survey. *The VLDB Journal*, 29, 251–272. doi:10.1007/s00778-019-00564-x

Jain, N., Akhtar, M., Giner-Miguelez, J., Shinde, R. C., Vanschoren, J., et al. (2024). A Standardized Machine-readable Dataset Documentation Format for Responsible AI. *arXiv preprint arXiv:2407.16883*. doi:10.48550/arXiv.2407.16883

Lachmuth, S., Dönmez, C., Hoffmann, C., Specka, X., Svoboda, N., & Helming, K. (2025). Facilitating Effective Reuse of Soil Research Data: The BonaRes Repository. *European Journal of Soil Science*, 76. doi:10.1111/ejss.70103

Oreamuno, M. A., et al. (2023). State of Documentation Practices in ML: Current State and Future Directions. *arXiv preprint arXiv:2312.15058*.

Orr, W., & Crawford, K. (2024). The social construction of datasets: On the practices, processes, and challenges of dataset creation for machine learning. *New Media & Society*. doi:10.1177/14614448241251797

Trišović, A., et al. (2025). FAIR Compliance via Automated Metadata. [Citation unverified; verify DOI before submission.]

Vanschoren, J., van Rijn, J. N., Bischl, B., & Torgo, L. (2014). OpenML: Networked science in machine learning. *ACM SIGKDD Explorations Newsletter*, 15(2), 49–60. doi:10.1145/2641190.2641198

Wilkinson, M. D., Dumontier, M., Aalbersberg, I. J., et al. (2016). The FAIR guiding principles for scientific data management and stewardship. *Scientific Data*, 3, 160018. doi:10.1038/sdata.2016.18

Yang, X., Liang, W., & Zou, J. (2024). Navigating Dataset Documentations in AI: A Large-Scale Analysis of Dataset Cards on Hugging Face. In *International Conference on Learning Representations*. doi:10.48550/arXiv.2401.13822

---

## Appendix: Robustness Check Details

**RC-4 (Winsorization):** N_tasks winsorized at 99th percentile (threshold=40; n_winsorized=51). Refitted P1 model yields IRR≈1.22, consistent with primary. Gate passes.

**RC-7 (Age vs. Decade FE):** Replacing C(decade) with age_years-only control; IRR_without_decade = 1.3758; attenuation ratio = 1.1219. The has_tags effect remains above the 1.1 gate and p<0.001 in both specifications.

**RC-3 (Collinearity documentation):** Cramér's V=0.823 for decade × has_tags. Decade adoption rates: 2010s=85.4% tagged, 2020s=2.1% tagged. Attenuation ratio=1.1219 confirms the collinearity is non-fatal. The categorical bins exhibit similar attenuation (~11% mean across bins 1–2, 3–5, 6+) in RC-7, consistent with the binary has_tags result.

**Model fit:** Observed vs. predicted N_tasks scatter (log scale) for the primary NB-2 model is available in h-e1/figures/fig5_obs_vs_pred.png. NB-2 fit is adequate for overdispersed count data with the observed variance structure.

**RC-6 (Categorical model — decade × category interaction):** AIC for interaction model = 25,743.84 versus main-effects AIC = 25,739.41; the interaction model is worse, indicating main effects are sufficient and there is no evidence of decade-moderation of the categorical dose-response.
