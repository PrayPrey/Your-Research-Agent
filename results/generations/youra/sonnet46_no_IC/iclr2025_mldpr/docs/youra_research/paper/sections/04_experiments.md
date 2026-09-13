# Experimental Setup

We design four experiments to test the threshold-plus-amplification hypothesis systematically, progressing from the binary threshold (existence) through the structural mechanism, the dose-response magnitude, and the categorical shape. Each experiment maps directly to a prediction from the Introduction.

## 4.1 Research Questions

Our experiments are organized around four research questions:

**RQ1:** Does binary keyword tag presence predict significantly more ML task registrations on OpenML (IRR ≥ 1.1)? *(Tests P1 — the binary threshold)*

**RQ2:** Does the has_tags effect survive decade fixed effects, confirming that it is a structural platform property rather than a temporal artifact? *(Tests mechanism survival — rules out era confounding)*

**RQ3:** Within the tagged dataset subset, does tag count magnitude show a log-linear dose-response relationship with ML task registrations? *(Tests P2 — the amplification mechanism)*

**RQ4:** Does the categorical dose-response show monotonic IRR ordering across tag count bins, with statistically distinguishable adjacent tiers at Bonferroni threshold? *(Tests P3 — categorical shape)*

Each RQ corresponds to a specific hypothesis gate. RQ1 and RQ2 are MUST_WORK gates — failing either would fundamentally undermine the threshold hypothesis. RQ3 and RQ4 are SHOULD_WORK gates — informative about the mechanism structure but not critical for the primary claim.

## 4.2 Dataset

**OpenML Dataset Corpus (N=5,217):** The corpus covers publicly accessible datasets on OpenML with at least one registered ML task (N_tasks ≥ 1). Datasets were collected via the OpenML API and preprocessed to compute all derived features (log transforms, age calculations, decade binning). The corpus includes datasets uploaded across decades of platform activity.

| Statistic | Value |
|-----------|-------|
| Total datasets (N_tasks ≥ 1) | 5,217 |
| Tagged datasets (has_tags=1) | 2,625 (50.3%) |
| Untagged datasets (has_tags=0) | 2,592 (49.7%) |
| Median N_tasks | [overdispersed count; NB-2 appropriate] |
| Cameron-Trivedi LR (confirms overdispersion) | 7,356.36 (>> χ²(1)=3.84 critical value) |

**Tagged subset (RQ3):** For the log-linear dose-response test (P2, H-M2), we restrict to datasets with has_tags=1 (N=2,625) and use log(tag_count+1) as the continuous independent variable.

**Why this dataset:** The OpenML corpus is the only openly available ML dataset repository with simultaneous access to (a) keyword tag metadata, (b) task registration counts as an adoption signal, and (c) structural metadata controls (n_instances, n_features, upload date). The corpus was collected for prior episodes on the same research question, eliminating data collection risk.

## 4.3 Baselines

This is an observational regression study — we compare the tagged (has_tags=1) versus untagged (has_tags=0) subpopulations within the same corpus, controlling for confounders. There is no external baseline system.

**Internal comparison:** Our primary IV (has_tags binary) is compared against the composite metadata completeness score (0-5, averaged across multiple metadata fields) from the prior episode, which yielded IRR=1.076 — below the 1.1 gate threshold — and collapsed to IRR=1.014 under decade fixed effects. This prior episode result serves as a negative control: an IV that captures broader metadata quality without isolating the FAIR F1 tagging mechanism specifically.

**Why this comparison is informative:** The contrast between composite score (IRR=1.014 under decade FE) and binary has_tags (IRR=1.2263 under decade FE, same corpus) isolates the FAIR F1 mechanism — binary tag presence captures within-decade search discoverability that the composite score dilutes.

## 4.4 Evaluation Metrics

**Primary metric:** Incidence Rate Ratio (IRR) — exp(NB-2 regression coefficient). IRR represents the multiplicative change in expected N_tasks for a unit increase in the independent variable.

**Gate criteria:**
- P1 (MUST_WORK): IRR ≥ 1.1 AND CI_lower ≥ 1.1 AND p < 0.05
- Mechanism (MUST_WORK): Post-FE p < 0.05 AND post-FE IRR ≥ 1.1
- P2 (SHOULD_WORK): IRR CI_lower ≥ 1.05 AND p < 0.05
- P3 (SHOULD_WORK): Monotonic IRR ordering AND ≥2/3 adjacent contrasts p < 0.0167 (Bonferroni)

**Structural validity metric:** Cameron-Trivedi Lagrange Multiplier test (CT LR) — must exceed χ²(1)=3.84 to confirm NB-2 appropriate over Poisson.

**Mechanism check:** Attenuation ratio = IRR_without_FE / IRR_with_FE. Values near 1.0 indicate the effect is decade-robust. The acceptable range is < 1.5 for STRONG mechanism support.

Statistical significance throughout uses two-tailed tests with α=0.05 for primary models and Bonferroni correction (α=0.0167 for k=3 adjacent contrasts) for the categorical comparison.

## 4.5 Implementation Details

All NB-2 models are implemented in Python using `statsmodels.formula.api.negativebinomial` with `loglike_method='nb2'`. BFGS optimizer (`method='bfgs'`, `maxiter=100`) is used throughout, confirmed convergent across all specifications.

**Primary model formula (P1):**
```
N_tasks ~ has_tags + log_n_instances + log_n_features + age_years + age_sq + C(decade)
```

**Dose-response formula (P2, tagged subset only):**
```
N_tasks ~ log_tag_count_p1 + log_n_instances + log_n_features + age_years + age_sq + C(decade)
```

**Categorical formula (P3):**
```
N_tasks ~ C(tag_count_cat) + log_n_instances + log_n_features + age_years + age_sq + C(decade)
```
Tag bins: [0], [1-2], [3-5], [6+]; reference category: 0 (no tags).

**Robustness checks (pre-specified):**
- RC-4: Winsorize N_tasks at 99th percentile; refit P1 model
- RC-7: Replace C(decade) with age_years-only; test age vs. decade FE sensitivity
- Mechanism test: Fit P1 model without C(decade) FE; compute attenuation ratio

All code uses the preprocessed dataset cached from the prior H-E1 episode (`h-e1/results/preprocessed.parquet`), ensuring reproducible data preparation.
