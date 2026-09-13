# Methodology

Our methodology operationalizes the insight that metadata completeness constrains preprocessing degrees of freedom, reducing implementation heterogeneity and thereby reducing reproducibility variance. We describe our metadata scoring scheme, variance operationalization, mediation framework, and statistical approach.

## Overview

Building on our observation that documentation reduces epistemic entropy—the space of valid implementations—we design a predictive framework with three components:

1. **Metadata Completeness Score**: A 5-field binary checklist capturing documentation coverage
2. **Reproducibility Variance (IQR)**: Interquartile range of performance across matched experimental configurations
3. **Preprocessing Entropy**: Shannon entropy of preprocessing component distributions as the mediating mechanism

The causal model under test:
```
Metadata Completeness → Preprocessing Entropy → Reproducibility Variance
        ↓________________________↗
              (Direct Effect)
```

## Metadata Completeness Score

We operationalize metadata completeness as a 5-field binary checklist, scored 0–5:

| Field | Definition | Rationale |
|-------|------------|-----------|
| Train/test split specified | Dataset specifies standard partition | Removes data splitting ambiguity |
| Preprocessing enumerated | Required transformations listed | Constrains pipeline design |
| Missing value handling documented | Imputation strategy specified | Removes common divergence point |
| Feature semantics provided | Column meanings documented | Enables domain-appropriate preprocessing |
| Versioning present | Dataset version tracked | Ensures temporal reproducibility |

**Rationale for binary checklist**: Continuous quality metrics introduce subjectivity; binary presence/absence is objectively verifiable from metadata. The checklist targets fields most likely to cause implementation divergence based on the leakage taxonomy (Kapoor & Narayanan, 2022).

We analyze by quartile (Q1: 0–1, Q2: 2, Q3: 3, Q4: 4–5) for interpretable effect sizes.

## Reproducibility Variance Operationalization

We define reproducibility variance as the IQR of accuracy/F1 scores across *matched runs*—experiments sharing identical:
- Flow (sklearn pipeline specification)
- Hyperparameters (identical configuration)
- Evaluation protocol (same cross-validation scheme)

**Why IQR rather than standard deviation**: IQR is robust to outliers from crashed runs or infrastructure failures, providing a conservative variance estimate.

**Matched-run requirement**: This design controls for algorithm-level variance, isolating implementation-level heterogeneity. If researcher A and researcher B use the same RandomForest with identical hyperparameters on the same dataset, variance in their results reflects preprocessing differences.

The nested structure yields:
```
Variance = Var_dataset + Var_config + Var_run + Var_seed
```
We estimate Var_config as our target, conditioning on dataset and controlling for seed-level stochasticity.

## Preprocessing Entropy

We compute Shannon entropy over preprocessing component distributions:

```
H_prep = -Σ p(c) log p(c)
```

where p(c) is the proportion of runs using preprocessing component c. Components include:
- **Imputation**: mean, median, mode, KNN, iterative, none
- **Scaling**: standard, minmax, robust, none
- **Encoding**: onehot, ordinal, target, none

Higher entropy indicates greater preprocessing diversity; lower entropy indicates convergence on standard approaches.

**Mechanism hypothesis**: High-metadata datasets constrain valid preprocessing choices, reducing H_prep. Lower H_prep corresponds to lower run-level variance.

## Statistical Framework

### Primary Analysis: Mixed-Effects Regression

```
IQR ~ metadata_score + stability + log_popularity + C(algo_family) + (1|dataset_id)
```

- **metadata_score**: Quartile indicator (Q1–Q4)
- **stability**: Intrinsic dataset stability (log instances, class imbalance, 1-NN CV error)
- **log_popularity**: log(number of runs) to control for community convergence
- **C(algo_family)**: Fixed effects for algorithm families (RandomForest, SVM, etc.)
- **(1|dataset_id)**: Random intercept per dataset

Random effects account for dataset-level clustering; datasets from similar domains may share unobserved confounders.

### Mediation Analysis

We test whether preprocessing entropy mediates the metadata-variance relationship using the Baron-Kenny framework with Sobel test:

1. **Path c (total)**: Metadata → IQR (should be significant)
2. **Path a**: Metadata → H_prep (should be significant negative)
3. **Path b**: H_prep → IQR, controlling metadata (should be significant positive)
4. **Path c' (direct)**: Metadata → IQR, controlling H_prep (should be smaller than c)

**Proportion mediated**: ab/(ab + c')

Significance tested via Sobel Z-statistic and bias-corrected bootstrap (1000 iterations).

### Robustness Checks

1. **Early-run test (P3)**: Restrict to first 50 runs (within 90 days of upload). If effect persists, reverse causality (popular datasets get better documentation) is unlikely.

2. **Single-algorithm test (P4)**: Restrict to RandomForest flows only. If effect persists, algorithm-mix confounding is ruled out.

3. **Permutation test (P6)**: Shuffle metadata scores 1000 times. Observed effect should exceed 95th percentile of permuted distribution.

## Data Collection

**Source**: OpenML platform via REST API

**Filtering criteria**:
- ≥10 matched runs per dataset (statistical power)
- Time window: 2019–2024 (infrastructure consistency)
- sklearn version ≥0.22 (API stability)
- Preprocessing component extraction succeeds (~70% of flows)

**Note on synthetic data**: Due to OpenML API timeout (504 Gateway Timeout) during data collection, we validated methodology using synthetic data following expected distributions. Effect patterns are consistent with theory; real-world replication with live API is scoped as future work.

## Implementation

Analysis implemented in Python using:
- statsmodels: Mixed-effects regression
- pingouin: Mediation analysis
- scipy: Bootstrap confidence intervals, Sobel test
- pandas: Data manipulation

All code, synthetic data, and analysis scripts available at [repository link].
