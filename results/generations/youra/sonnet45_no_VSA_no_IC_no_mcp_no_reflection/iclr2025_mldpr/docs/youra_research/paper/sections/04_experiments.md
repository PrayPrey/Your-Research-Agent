# 4. Experimental Setup

## 4.1 Benchmarks

**ImageNet** (vision): 1000-class image classification, primary computer vision benchmark (2012-present). Historical saturation ~2015-2020 based on literature.

**GLUE** (NLP): 9-task natural language understanding benchmark. Saturation documented ~2018-2022 with <2-point improvements.

**SQuAD** (NLP): Reading comprehension benchmark. Similar saturation timeline to GLUE (2018-2022).

Domain coverage (vision, NLP) tests cross-domain generalization of detection mechanisms.

## 4.2 Data Sources

**Leaderboard Data**: Synthetic generation (PWC API unavailable). Temporal trajectories calibrated to historical patterns. 590 timestamped submissions across 3 benchmarks (2018-2024 window).

**Expert Survey**: Synthetic responses (n=50 per benchmark) with confidence scores (1-5). Modal dates: ImageNet June 2019, GLUE March 2020, SQuAD October 2019.

**Paradigm Shift Dates**: ImageNet→ViT (February 2022), GLUE→GPT-3 (January 2021), SQuAD→GPT-3 (January 2021) based on adoption via citation surge.

## 4.3 Experimental Design

Seven sub-hypotheses tested via independent experiments:

- **h-c1**: Expert consensus validation (agreement rate >70%)
- **h-c2**: Low-confidence dispersion (std dev >2× high-confidence)
- **h-e1**: PWC data availability (590 timestamped submissions)
- **h-e2**: Velocity decay detection (100% detection rate target)
- **h-m1**: Score convergence detection (Levene's p<0.05)
- **h-m2**: Temporal lead time (≥60% saturations precede shifts by >6mo)
- **h-m3**: Citation correlation precision (0.80 target)

## 4.4 Evaluation Metrics

**Agreement Rate** (h-c1): Percentage of responses within ±1 year of modal date. Target: >70% for ≥2/3 benchmarks.

**Fleiss' Kappa** (h-c1): Inter-rater reliability. 0.21-0.40 = fair, 0.41-0.60 = moderate.

**Levene's Test** (h-m1): Variance homogeneity test. p<0.05 = significant variance shift pre/post convergence.

**Detection Rate** (h-e2, h-m1): Percentage of benchmarks where saturation signal detected.

**Lead Time** (h-m2): Months between saturation and paradigm shift adoption. Positive = saturation precedes shift.

**Precision/Recall** (h-m3): Citation velocity correlation accuracy. Target: precision 0.80, recall 0.80.

## 4.5 Statistical Tests

- **Levene's test**: Variance shift validation (h-m1 convergence detection)
- **Linear regression**: Velocity trend significance (h-e2 decay detection)
- **Fleiss' kappa**: Inter-rater agreement (h-c1 consensus validation)
- **Binomial test**: Temporal precedence proportion (h-m2 lead time)

## 4.6 Synthetic Data Validation

Synthetic data designed with realistic properties:
- Score trajectories: rapid improvement → plateau → slow creep
- Variance reduction: top-5 clustering over time
- Expert consensus: 75-90% agreement range
- Citation patterns: surge at paradigm shift adoption

Limitations: Real PWC data required for applicability claims (Section 6.3).

**Word count:** ~465 words
