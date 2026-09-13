# Experimental Setup

We design experiments to validate four claims about dataset adoption dynamics: (1) that download trajectories exhibit meaningful clustering structure, (2) that trajectories contain discrete phase transitions detectable via changepoint analysis, (3) that clusters represent genuinely different trajectory shapes, and (4) that clusters map to interpretable behavioral archetypes.

## Research Questions

Our experiments address the following questions:

**RQ1 (Existence):** Do HuggingFace dataset download trajectories partition into distinct clusters? Specifically, does DTW-based clustering achieve silhouette score >0.25 with optimal k in [3,8] and bootstrap stability >0.65?

**RQ2 (Phase Detection):** Do download trajectories exhibit statistically significant changepoints indicative of discrete adoption phases? Does PELT detection rate exceed 50%?

**RQ3 (Shape Differentiation):** Do identified clusters represent genuinely different trajectory shapes, as measured by shape descriptor variance ratios?

**RQ4 (Archetype Recovery):** Do empirical clusters map to interpretable behavioral archetypes with >70% feature alignment?

## Dataset

We collect time series data from the HuggingFace Hub to validate our methodology. Our data collection follows these criteria:

| Criterion | Value | Rationale |
|-----------|-------|-----------|
| Minimum history | 12 months | Sufficient temporal depth for lifecycle analysis |
| Minimum activity | 100 downloads | Excludes noise-dominated dormant datasets |
| Data quality | <10% missing | Ensures reliable trajectory estimation |
| Sample size | 500 series | Standard for clustering validation studies |

Each time series consists of 300 temporal observations, representing monthly granularity over extended observation windows. The dataset spans diverse domains within the HuggingFace ecosystem.

**Preprocessing:** Raw time series undergo log transformation (`log(1 + x)`) to handle exponential growth patterns, followed by z-score normalization to ensure clustering reflects trajectory shape rather than absolute scale.

## Baselines

We compare our DTW-based clustering against three baseline approaches:

**Random Assignment:** Assigns datasets to clusters randomly, establishing the null baseline for clustering significance. Any meaningful clustering should substantially exceed random assignment performance.

**K-Means on Summary Statistics:** Clusters datasets based on aggregate features (mean, standard deviation, trend slope) rather than full trajectory shapes. This baseline tests whether full temporal structure is necessary or if summary statistics suffice.

**Single-Level DTW Clustering:** Applies DTW clustering without PELT phase detection, testing the value of our two-level hierarchical approach versus direct trajectory clustering.

## Implementation Details

We implement our methodology using established libraries:

- **Clustering:** tslearn v0.6.0 TimeSeriesKMeans with DTW metric
- **Changepoint Detection:** ruptures v1.1.7 PELT algorithm with BIC penalty
- **Evaluation:** scikit-learn v1.0 for silhouette scores and bootstrap validation

**Hyperparameters:**

| Parameter | Value | Source |
|-----------|-------|--------|
| k range | [3, 8] | Domain expectation for adoption archetypes |
| DTW metric | Full DTW | Shape-based similarity |
| max_iter | 10 | tslearn default |
| n_init | 2 | Multiple initialization for robustness |
| PELT penalty | BIC = 2log(n) | Data-driven penalty selection |
| Bootstrap iterations | 100 | Standard for stability assessment |
| Bootstrap sample ratio | 80% | Resampling proportion |

**Reproducibility:** All experiments use fixed random seed (42) for reproducibility. Code is available at the project repository.

## Evaluation Metrics

### Primary Metrics

**Silhouette Score:** Measures cluster cohesion and separation. Values range from -1 to 1, with >0.25 indicating meaningful structure. We compute silhouette on flattened time series representations for computational efficiency.

**Bootstrap Jaccard Stability:** Measures cluster assignment consistency across bootstrap resamples. We resample 80% of data 100 times, refit clustering, and compute Jaccard similarity between original and bootstrap assignments. Values >0.65 indicate stable clusters.

### Secondary Metrics

**Changepoint Detection Rate:** Proportion of time series exhibiting at least one PELT-detected changepoint. Rates >50% indicate that discrete phase transitions are prevalent.

**Shape Descriptor Variance Ratio:** For each descriptor (growth ratio, changepoint count, derivative variance, peak timing), we compute between-cluster variance / within-cluster variance. Ratios >2.0 indicate the descriptor successfully differentiates clusters.

**Archetype Alignment Score:** Cosine similarity between cluster centroid descriptor profiles and theoretical archetype definitions. Alignment >0.70 indicates successful archetype recovery.

## Experimental Protocol

For each research question, we follow a structured validation protocol:

1. **Data Preparation:** Load preprocessed time series (log-transformed, z-score normalized)
2. **Method Application:** Apply the relevant method (clustering, changepoint detection, descriptor analysis)
3. **Metric Computation:** Calculate primary and secondary metrics
4. **Threshold Evaluation:** Compare metrics against predefined success thresholds
5. **Visualization:** Generate diagnostic figures for qualitative assessment

Gate classification follows a hierarchical structure: RQ1 and RQ2 are MUST_WORK gates (failure blocks subsequent analysis), while RQ3 and RQ4 are SHOULD_WORK gates (failure is documented as limitation but does not block).
