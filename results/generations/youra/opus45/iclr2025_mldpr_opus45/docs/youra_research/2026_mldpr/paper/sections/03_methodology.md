# Methodology

Building on our observation that adoption dynamics reflect recurring mechanisms that generate trajectory shapes, we design a two-level hierarchical analysis framework. Level 1 identifies discrete adoption phases within individual trajectories using changepoint detection. Level 2 clusters trajectories by shape similarity using Dynamic Time Warping, enabling phase-independent taxonomy discovery. This separation addresses the fundamental challenge that a young dataset's current state does not reveal its trajectory type.

## Overview

Our methodology consists of four components: (1) data collection and preprocessing, (2) Level 1 phase detection via PELT changepoint analysis, (3) Level 2 trajectory clustering via DTW-based TimeSeriesKMeans, and (4) stability validation through bootstrap resampling. Figure 1 illustrates representative time series with detected changepoints.

## Data Collection and Preprocessing

We collect download time series from the HuggingFace Hub API, which provides access to dataset metadata and download statistics. Our inclusion criteria ensure sufficient temporal depth for trajectory analysis:

- **Temporal coverage:** Minimum 12 months of download history
- **Activity threshold:** Minimum 100 total downloads
- **Data quality:** Less than 10% missing monthly values
- **Target population:** 500 qualifying datasets

**Rationale:** The 12-month minimum ensures trajectories capture meaningful lifecycle evolution rather than transient fluctuations. The 100-download threshold excludes dormant datasets where noise dominates signal.

### Preprocessing Pipeline

Raw download counts undergo two transformations:

1. **Log transformation:** We apply `log(1 + downloads)` to handle the exponential growth patterns common in adoption dynamics. This compresses the range of values and makes multiplicative changes (e.g., doubling) comparable across scales.

2. **Z-score normalization:** Using TimeSeriesScalerMeanVariance from tslearn, we standardize each series to zero mean and unit variance. This ensures clustering reflects trajectory *shape* rather than absolute download volume—a dataset with 1,000 downloads following a sustained-growth pattern should cluster with a dataset showing 100,000 downloads following the same pattern.

## Level 1: PELT Changepoint Detection

Adoption dynamics include discrete phase transitions—launch, growth, maturity, decline—that segment trajectories into distinct regimes. We detect these transitions using the Pruned Exact Linear Time (PELT) algorithm [Killick et al., 2012].

**Rationale:** PELT provides optimal changepoint detection with O(n) computational cost, making it practical for analyzing hundreds of trajectories. The algorithm identifies points where statistical properties (mean, variance) shift significantly.

### Penalty Selection

Changepoint detection requires a penalty parameter controlling sensitivity—too low yields spurious changepoints from noise, too high misses genuine transitions. We use the Bayesian Information Criterion (BIC) penalty:

$$\text{penalty} = 2 \cdot \log(n)$$

where $n$ is the series length.

**Rationale:** BIC provides a data-driven balance appropriate for count data. Empirically, this yields meaningful phase segmentation: most datasets exhibit 0-2 changepoints, consistent with the launch-growth-maturity lifecycle model.

### Phase Detection Output

For each trajectory, PELT outputs:
- Number of detected changepoints
- Changepoint locations (time indices)
- Segment boundaries defining distinct phases

This enables subsequent analysis to condition on lifecycle phase or normalize trajectories relative to phase boundaries.

## Level 2: DTW-Based Trajectory Clustering

With phases identified, we cluster trajectories by shape similarity using Dynamic Time Warping (DTW) as the distance metric within TimeSeriesKMeans.

**Rationale:** DTW captures shape similarity while accommodating temporal warping—two trajectories following similar adoption patterns at different speeds are recognized as similar. This is essential because some datasets reach maturity faster than others, and we aim to cluster by *pattern* not *timing*.

### Clustering Algorithm

We employ TimeSeriesKMeans from tslearn with the following configuration:

```
metric: "dtw"
k_range: [3, 8]
max_iter: 10
n_init: 2
random_state: 42
```

**Rationale:**
- **k range [3,8]:** Based on domain expectation that adoption patterns partition into 3-8 archetypes (sustained growth, flash-in-the-pan, plateau, slow burn, revival, and variants). Values below 3 indicate trivial structure; above 8 suggests fragmentation.
- **DTW metric:** Shape-based clustering preserving temporal structure.
- **n_init=2:** Multiple initializations improve robustness to local optima.

### Optimal k Selection

We select optimal k by maximizing silhouette score across the candidate range:

$$\text{silhouette}(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$

where $a(i)$ is mean intra-cluster distance and $b(i)$ is mean nearest-cluster distance. Higher silhouette indicates better-separated, cohesive clusters.

**Success threshold:** Silhouette > 0.25 indicates meaningful clustering structure. Values below this suggest trajectories do not partition into distinct groups.

## Stability Validation

Cluster stability is assessed via bootstrap resampling with Jaccard similarity measurement.

### Bootstrap Protocol

1. Sample 80% of trajectories with replacement
2. Refit DTW clustering with same k
3. Compute Jaccard similarity between original and bootstrap cluster assignments
4. Repeat 100 times

$$\text{Jaccard}(A, B) = \frac{|A \cap B|}{|A \cup B|}$$

**Success threshold:** Mean Jaccard > 0.65 indicates stable clusters that are robust to sampling variation. Lower values suggest clusters are artifacts of specific data points.

**Rationale:** Bootstrap stability distinguishes genuine structure from overfitting. A taxonomy that changes substantially with minor data perturbations lacks reliability for practical use.

## Shape Descriptor Analysis

To validate that clusters represent genuinely different trajectory types, we compute shape descriptors for cluster centroids:

1. **Growth ratio:** Final value / initial value (captures overall trend)
2. **Changepoint count:** Number of PELT-detected phase transitions
3. **Derivative variance:** Variance of first differences (captures volatility)
4. **Peak timing:** Relative position of maximum value

For each descriptor, we compute variance ratio (between-cluster variance / within-cluster variance). Ratios exceeding 2.0 indicate the descriptor successfully differentiates clusters.

## Summary

Our two-level methodology addresses the phase-trajectory conflation in single-level approaches:

| Component | Purpose | Success Criterion |
|-----------|---------|-------------------|
| PELT (Level 1) | Identify adoption phases | >50% datasets show changepoints |
| DTW Clustering (Level 2) | Group by trajectory shape | Silhouette > 0.25, k in [3,8] |
| Bootstrap Validation | Verify stability | Jaccard > 0.65 |
| Shape Descriptors | Validate differentiation | 3+ descriptors with ratio > 2.0 |

This framework enables discovery of stable, interpretable trajectory archetypes that characterize ML dataset adoption dynamics.
