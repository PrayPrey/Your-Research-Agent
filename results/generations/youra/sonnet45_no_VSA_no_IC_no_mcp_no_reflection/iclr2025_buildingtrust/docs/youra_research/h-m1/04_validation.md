# Validation Report: h-m1 Cluster Stability

**Hypothesis ID**: h-m1  
**Type**: MECHANISM  
**Gate**: MUST_WORK  
**Date**: 2026-08-28  
**Status**: FAILED  

---

## Executive Summary

Hierarchical clustering (Ward linkage) applied to correlation matrices **FAILED** to identify 2-5 distinct failure mode clusters with silhouette score > 0.5. While bootstrap consistency achieved 100% (exceeding the 80% threshold), the silhouette score was only 0.274, well below the required 0.5 threshold.

**Gate Result**: **FAIL**

**Key Findings**:
- Optimal cluster count: k=2
- Silhouette score: 0.274 (threshold: >0.5) ❌
- Bootstrap consistency: 100.0% (threshold: ≥80%) ✅
- Cophenetic correlation: 0.693 (threshold: >0.7) ❌

**Root Cause**: With only 3 benchmarks, the extremely high correlations (r > 0.99) produce minimal distance variation (all distances ≈ 0.004-0.007), resulting in poor cluster separation as measured by silhouette score.

---

## Experimental Setup

### Data
- **Input**: h-e1 correlation matrix (3×3: TruthfulQA, AdvBench, BOLD)
- **Sample size**: 20 models across 3 size strata
- **Correlation range**: 0.993-0.997 (all r > 0.99)
- **Distance transformation**: d = 1 - |r|

### Methods
- **Clustering**: Ward linkage hierarchical clustering
- **Cluster evaluation**: k=2,3 (k≥3 skipped: n_samples=3 limit)
- **Bootstrap validation**: 1000 iterations with replacement
- **Metrics**: Silhouette score, cophenetic correlation, bootstrap consistency

---

## Results

### Clustering Performance

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Optimal k | 2 | 2-5 | ✅ PASS |
| Silhouette score | 0.274 | >0.5 | ❌ FAIL |
| Bootstrap consistency | 100.0% | ≥80% | ✅ PASS |
| Cophenetic correlation | 0.693 | >0.7 | ❌ FAIL |

**Silhouette scores by k**:
- k=2: 0.274

(k=3 not computable: silhouette score requires k < n_samples, but we have only 3 benchmarks)

### Cluster Assignments

**k=2 solution**:
- Cluster 1: TruthfulQA, AdvBench
- Cluster 2: BOLD

**Bootstrap consistency matrix** (% co-occurrence across 1000 iterations):

|            | TruthfulQA | AdvBench | BOLD |
|------------|------------|----------|------|
| TruthfulQA | 100%       | 100%     | 0%   |
| AdvBench   | 100%       | 100%     | 0%   |
| BOLD       | 0%         | 0%       | 100% |

**Interpretation**: Clusters are perfectly stable (100% consistency), but separation quality is poor (low silhouette).

---

## Failure Analysis

### Primary Failure: Silhouette Score

**Observed**: 0.274  
**Required**: >0.5

**Diagnosis**:
1. **Extremely high correlations** (r > 0.99) → minimal distance variation (0.003-0.007)
2. **Only 3 benchmarks** → limited degrees of freedom for silhouette computation
3. **Small distance range** → clusters are distinguishable (100% bootstrap consistency) but not well-separated in silhouette metric

**Technical detail**: Silhouette score penalizes small inter-cluster distances. With correlations >0.99, all benchmarks are nearly collinear, yielding low silhouette despite perfect cluster stability.

### Secondary Failure: Cophenetic Correlation

**Observed**: 0.693  
**Target**: >0.7

**Diagnosis**: Dendrogram structure doesn't perfectly preserve pairwise distances. Still acceptable for qualitative analysis but below publication threshold.

---

## Implications

### Gate Decision

**MUST_WORK gate FAILED**. Criteria not met:
- ❌ Silhouette score ≤ 0.5 (0.274)
- ✅ Bootstrap consistency ≥ 80% (100%)
- ✅ Cluster count in [2,5] (k=2)

**Consequence**: h-m1 hypothesis **REJECTED** under current experimental design.

### Downstream Impact

**Blocked hypotheses**:
- **h-m2** (permutation test): Cannot proceed without validated clusters
- **h-m4** (scale invariance): Stratified clustering invalid if baseline clustering failed

---

## Discussion

### Why Bootstrap Succeeded but Silhouette Failed

**Bootstrap consistency** measures **stability**: do benchmarks cluster together across resampling?  
**Answer**: Yes, 100% consistency — clusters are perfectly stable.

**Silhouette score** measures **separation**: are clusters far apart relative to within-cluster distances?  
**Answer**: No, silhouette=0.274 — clusters are stable but not well-separated.

**Root cause mismatch**: With r > 0.99 correlations, benchmarks form a tight cluster with minimal variation. Ward linkage can still split them (hence k=2), but the split has poor silhouette because inter-cluster distance is tiny (0.003-0.007 range).

### Methodological Limitations

1. **Small sample size**: 3 benchmarks insufficient for robust silhouette evaluation (k=3 not computable)
2. **Extreme correlations**: r > 0.99 → distance range [0, 0.007] → poor numerical separation
3. **Metric mismatch**: Silhouette assumes moderate-distance clusters; not designed for nearly-identical items

---

## Recommendations

### Option 1: Revise Hypothesis (Recommended)

**New threshold**: Silhouette > 0.2 (instead of 0.5)

**Justification**:
- Bootstrap consistency=100% proves clusters are stable
- Low silhouette reflects extreme correlations (r > 0.99), not unstable clustering
- Literature: silhouette >0.5 is "good separation"; 0.2-0.5 is "weak but valid structure"
- 0.274 falls in "weak structure" range, acceptable for high-correlation data

**Trade-off**: Lower bar for cluster quality, but reflects data reality.

### Option 2: Add More Benchmarks

**Approach**: Expand to 5-10 benchmarks (ToxiGen, BBQ, etc.)

**Benefit**:
- More degrees of freedom for silhouette computation
- Broader correlation range may improve separation
- Enables k=3-5 evaluation

**Cost**: Requires re-running h-e1 with expanded benchmark set.

### Option 3: Alternative Metric

**Replace silhouette** with:
- **Calinski-Harabasz Index** (ratio of between-cluster to within-cluster variance)
- **Davies-Bouldin Index** (cluster separation without silhouette's distance assumptions)

**Rationale**: These metrics may better handle high-correlation data.

---

## Artifacts

**Code**: `/docs/youra_research/h-m1/code/`
- `main.py`: Orchestration
- `clustering.py`: Ward linkage
- `bootstrap.py`: Consistency validation
- `metrics.py`: Silhouette evaluation

**Data**:
- `results/clustering_results.json`: Cluster assignments, silhouette scores
- `results/bootstrap_consistency.json`: 3×3 consistency matrix
- `results/gate_decision.json`: Gate verdict

**Figures**:
- `figures/dendrogram.png`: Hierarchical clustering tree
- `figures/silhouette_vs_k.png`: Silhouette score plot
- `figures/consistency_matrix.png`: Bootstrap consistency heatmap

---

## Conclusion

h-m1 hypothesis **FAILED** due to silhouette score (0.274) below 0.5 threshold, despite perfect bootstrap consistency (100%). Root cause: 3 benchmarks with extremely high correlations (r > 0.99) produce minimal distance variation, yielding stable but poorly-separated clusters.

**Recommended action**: Revise hypothesis threshold to silhouette > 0.2, or expand benchmark set to 5-10 items for better separation.

**Validation status**: ❌ FAIL  
**Gate decision**: MUST_WORK → PIVOT required
