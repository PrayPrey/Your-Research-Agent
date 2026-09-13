# Methodology

Our methodology combines time-series analysis with hypothesis-driven mechanism verification. We describe the data source, concentration metrics, change-point detection approach, and mechanism verification design.

## Data Source

We use Papers With Code (PWC) as our primary data source, covering 2018-2024 with monthly resolution. PWC provides task-dataset-metric triplets for ML benchmark evaluations, enabling precise measurement of benchmark usage beyond simple paper-dataset pairs.

**Rationale:** PWC is the most comprehensive public database of benchmark usage, was used by Koch et al. (2021) establishing methodological continuity, and provides sufficient temporal coverage (84 months) for time-series analysis. We acknowledge PWC may not capture industry or proprietary benchmark usage.

## Concentration Metrics

We measure benchmark concentration using the Gini coefficient, following Koch et al. (2021). For a distribution of benchmark usage counts $x_1, \ldots, x_n$:

$$G = \frac{\sum_{i=1}^{n}\sum_{j=1}^{n}|x_i - x_j|}{2n\sum_{i=1}^{n}x_i}$$

Gini ranges from 0 (perfect equality—all benchmarks equally used) to 1 (perfect concentration—all usage on one benchmark). We compute monthly aggregate Gini across all task-dataset-metric triplets.

**Rationale:** Gini is a standard economics metric for measuring concentration, validated for benchmark analysis by Koch et al., and interpretable (0.7 means high concentration).

## Change-Point Detection

To detect structural breaks in the Gini time series, we apply the Pruned Exact Linear Time (PELT) algorithm [Killick et al., 2012]. PELT identifies an unknown number of change points by minimizing:

$$\sum_{i=1}^{m+1} C(y_{(\tau_{i-1}+1):\tau_i}) + \beta m$$

where $C$ is a cost function (we use RBF kernel), $m$ is the number of change points, and $\beta$ is a penalty term preventing overfitting.

**Key parameters:**
- Model: RBF kernel (robust to non-linear trends)
- Minimum segment size: 3 months
- Penalty: BIC-derived ($\beta = 1.87$ for 84 observations)

**Rationale:** PELT is designed for time series with an unknown number of change points, which matches our hypothesis that foundation models caused structural breaks without specifying exactly when or how many. The alternative (pre-specifying break locations) would beg the question.

## Model Comparison

We compare two models:
1. **Null (Monotonic):** Single monotonic trend over 2018-2024
2. **Alternative (Segmented):** Multiple segments with different trends, separated by PELT-detected change points

Model selection uses Bayesian Information Criterion (BIC):

$$\text{BIC} = k \ln(n) - 2\ln(\hat{L})$$

where $k$ is the number of parameters, $n$ is the number of observations, and $\hat{L}$ is maximum likelihood. Lower BIC indicates better fit-complexity tradeoff.

**Success criterion:** Segmented model has lower BIC than monotonic model, with change points detected within the 2019-2022 window (aligning with foundation model emergence).

## Mechanism Verification Design

Beyond detecting that a phase transition occurred, we verify the causal mechanism through a chain of five sub-hypotheses:

| Step | Mechanism | Sub-Hypothesis | Test |
|------|-----------|----------------|------|
| 1 | Foundation models emerge | h-m1 | Citation z-scores >2σ for GPT-3/ViT/BERT |
| 2 | Emergent benchmarks created | h-m2 | >80% of emergent benchmarks post-2020 |
| 3 | Attention shifts | h-m3 | Emergent share increases significantly |
| 4 | Traditional persists | h-m4 | Traditional share <50%, papers >10k |
| 5 | Modalities diverge | h-m5 | CV-NLP correlation drops from >0.6 to <0.4 |

**Gate structure:** h-e1 (phase transition signal) and h-m1 (foundation emergence) are MUST_WORK gates—their failure would invalidate the entire hypothesis. h-m2 through h-m5 are SHOULD_WORK gates—their failure weakens but does not invalidate the core claim.

**Falsification:** Each sub-hypothesis has pre-specified falsification criteria. If the data contradicts predictions, the hypothesis fails. This design enables definitive conclusions rather than post-hoc rationalization.

## Statistical Tests

We use the following statistical tests:

- **Change-point significance:** BIC comparison between models
- **Citation impact:** Z-score relative to field distribution
- **Share comparison:** Chi-square test for pre/post proportion differences
- **Correlation comparison:** Fisher z-test for correlation difference significance

All tests use α=0.05 significance level. We report exact p-values where computationally feasible.

## Implementation

Experiments were implemented in Python using:
- `ruptures` library for PELT change-point detection
- `scipy.stats` for statistical tests
- Custom pipelines for PWC data processing

All code will be released upon publication.
