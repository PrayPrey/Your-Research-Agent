# Methodology

Our study design follows directly from the threshold-plus-amplification hypothesis: we need an observational design that can isolate keyword tagging as the FAIR F1 operand, while controlling for the primary confounds — dataset size, age, and platform era. Each design choice is a deliberate response to the problem structure.

## 3.1 Dataset: OpenML Corpus

We analyze the OpenML dataset corpus, a cross-sectional snapshot of N=5,217 datasets with at least one registered ML task (N_tasks≥1) as of the collection date. OpenML [Vanschoren et al., 2014] is a publicly accessible ML experimentation platform where researchers register datasets, define ML tasks (target variable, task type), and execute experimental flows. The corpus includes all datasets for which we can observe both tag status and task count simultaneously.

**Sample restriction (N_tasks≥1):** We study conditional adoption intensity — how tagging affects engagement among datasets that have been minimally engaged. Datasets with zero tasks are structurally different (never engaged with the platform's ML task infrastructure) and would require a hurdle component for joint modeling; we defer this to future work and explicitly scope our claims to the engaged dataset population.

**Key variables:**

| Variable | Role | Definition |
|----------|------|------------|
| N_tasks | DV | Count of distinct ML task registrations (integer ≥ 1) |
| has_tags | IV (P1) | Binary: 1 if dataset has ≥1 keyword tag, 0 otherwise |
| log_tag_count_p1 | IV (P2) | log(tag_count + 1); restricted to has_tags=1 subset |
| tag_count_cat | IV (P3) | Categorical bins: 0, 1-2, 3-5, 6+ (reference: 0) |
| log_n_instances | Control | log(number of instances); dataset size proxy |
| log_n_features | Control | log(number of features); dataset complexity proxy |
| age_years | Control | Dataset age in years at corpus collection date |
| age_sq | Control | age_years²; quadratic age term for non-linearity |
| C(decade) | Control | Decade-of-upload fixed effects (2010s, 2020s, etc.) |

## 3.2 Model: Negative Binomial Type 2

Building on the observation that tag-indexed search membership creates a binary gatekeeping function, we design the regression to isolate this binary effect while accounting for the overdispersed count outcome structure of N_tasks.

**Why NB-2 (not Poisson):** The Cameron-Trivedi Lagrange multiplier test (CT LR=7,356.36, χ²(1)=3.84 critical value) confirms strong overdispersion — variance far exceeds mean in the N_tasks distribution. Poisson regression would underestimate standard errors and inflate significance. NB-2 accommodates overdispersion via the quadratic variance function Var(Y) = μ + αμ², where α is the estimated dispersion parameter.

**Why binary has_tags (not composite score):** A prior episode on the same corpus tested a composite metadata completeness score (0-5, aggregating description, tags, license, creator, version). That composite score yielded IRR=1.076 (95% CI [1.0595, 1.0922]) under decade fixed effects, falling to IRR=1.014 (p=0.19) — effectively no effect. The has_tags binary isolates the FAIR F1 signal without averaging it against non-F1 metadata fields (description richness, licensing) that may not drive search-indexed discoverability. RC-2a from that episode (binary description presence: IRR=1.102) confirmed that binary presence outperforms the composite; binary has_tags is the natural extension to the tagging-specific operand.

**Why decade fixed effects (not age alone):** The OpenML platform underwent substantial character shifts across decades: 2010s datasets were predominantly curated with tags (85.4% have tags), while 2020s datasets are predominantly untagged (2.1% have tags), reflecting shifts in community norms and platform growth patterns. Including C(decade) as fixed effects controls for this between-era confounding. Without this control, any tagging effect would be partially attributed to era differences, not tag-indexed discoverability per se. The extreme collinearity (Cramér's V=0.823) between decade and has_tags was the primary robustness risk — Section 5 demonstrates it is non-fatal.

## 3.3 Four-Prediction Test Design

The threshold-plus-amplification hypothesis generates four falsifiable predictions, each tested with a separate regression specification:

**P1 (Binary Threshold — MUST_WORK):**
```
Formula: N_tasks ~ has_tags + log_n_instances + log_n_features + age_years + age_sq + C(decade)
Sample: Full corpus (N=5,217; N_tasks ≥ 1)
Gate: IRR ≥ 1.1 AND CI_lower ≥ 1.1 AND p < 0.05
```

**P2 (Log-Linear Dose-Response — SHOULD_WORK):**
```
Formula: N_tasks ~ log_tag_count_p1 + log_n_instances + log_n_features + age_years + age_sq + C(decade)
Sample: Tagged subset only (has_tags=1; N=2,625)
Gate: IRR_P2 CI_lower ≥ 1.05 AND p < 0.05
```

**P3 (Categorical Dose-Response — SHOULD_WORK):**
```
Formula: N_tasks ~ C(tag_count_cat) + log_n_instances + log_n_features + age_years + age_sq + C(decade)
Sample: Full corpus (N=5,217)
Bins: 0, 1-2, 3-5, 6+ (reference: 0)
Gate: Monotonic IRR ordering AND ≥2/3 adjacent contrasts p < 0.0167 (Bonferroni)
```

**Mechanism Verification (MUST_WORK, via H-M1):** We test whether the P1 has_tags effect survives decade fixed effects — operationalized as the attenuation ratio (IRR_with_FE / IRR_without_FE) and the post-FE p-value. The gate requires the post-FE p-value to remain below 0.05 with IRR ≥ 1.1.

## 3.4 Implementation

All models are fit using `statsmodels.formula.api.negativebinomial` with `loglike_method='nb2'` and BFGS optimization (`method='bfgs'`, `maxiter=100`). BFGS convergence was confirmed for all 7 model variants tested (H-E1 through H-M3 specifications). The BFGS optimizer was selected over L-BFGS-B based on convergence stability in the prior episode on this corpus.

Incidence rate ratios are computed as `IRR = exp(coefficient)` and confidence intervals as `exp(coefficient ± 1.96 * standard_error)`. Statistical significance is evaluated at α=0.05; adjacent categorical contrasts use Bonferroni correction (α=0.0167 for 3 contrasts). The Cameron-Trivedi LR test is computed at the end of each fit to confirm NB-2 appropriateness.

The mechanism flow from FAIR F1 principle to ML task adoption operates as illustrated in Figure 3:

> **Figure 3** (h-m1_fig4_mechanism_flow.png): FAIR F1 threshold-plus-amplification mechanism. Dataset tags → search index membership → multiple search pathways → researcher discovery events → ML task registration.

**Robustness checks:** We report three pre-specified robustness checks: RC-4 (winsorization of N_tasks at the 99th percentile), RC-7 (age_years-only control vs. decade FE), and the mechanism test (with vs. without decade FE for P1). These are reported in the Results section.
