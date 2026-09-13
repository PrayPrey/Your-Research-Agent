# Validation Report: h-m2

**Hypothesis**: MECHANISM - Shape descriptor differentiation across cluster centroids
**Generated**: 2026-03-27T13:10:41.602995
**Gate Type**: SHOULD_WORK
**Data Source**: Reused from h-e1 (HuggingFace Hub time series)

---

## Gate Verdict

**GATE RESULT**: PASS

---

## Primary Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Passing Descriptors | 3 | >= 2 | PASS |
| Distinct Profiles | True | True | PASS |
| Min Pairwise Distance | 0.3170 | > 0 | PASS |

---

## Variance Ratios by Descriptor

| Descriptor | Inter-Cluster Var | Intra-Cluster Var | Ratio | Threshold | Status |
|------------|-------------------|-------------------|-------|-----------|--------|
| growth_ratio | 0.004636 | 0.000978 | 4.7413 | > 2.0 | PASS |
| peak_timing | 0.000041 | 0.000191 | 0.2144 | > 2.0 | FAIL |
| changepoint_count | 4.250000 | 0.383669 | 11.0773 | > 2.0 | PASS |
| derivative_variance | 0.008994 | 0.004171 | 2.1563 | > 2.0 | PASS |

---

## Descriptor Matrix (per Cluster)

| Cluster | growth_ratio | peak_timing | changepoint_count | derivative_variance |
|---------|--------|--------|--------|--------|
| Cluster 0 | 0.3467 | 0.0100 | 0.0000 | 0.1346 |
| Cluster 1 | 0.4200 | 0.0033 | 1.0000 | 0.1938 |
| Cluster 2 | 0.5367 | 0.0167 | 0.0000 | 0.3883 |
| Cluster 3 | 0.4500 | 0.0200 | 5.0000 | 0.2074 |

---

## Cluster Statistics

| Statistic | Value |
|-----------|-------|
| Number of Clusters (k) | 4 |
| Number of Series | 500 |
| Centroids Shape | (4, 300) |

---

## Mechanism Verification

| Indicator | Status |
|-----------|--------|
| descriptors_computed | PASS |
| all_clusters_analyzed | PASS |
| variance_computed | PASS |
| effect_measurable | PASS |
| hypothesis_supported | PASS |

---

## Figures Generated

- `/home/anonymous/YouRA_results_new_4_sonnet45/TEST_mldpr_opus45/docs/youra_research/20260325_mldpr/h-m2/figures/gate_metrics_bar.png`
- `/home/anonymous/YouRA_results_new_4_sonnet45/TEST_mldpr_opus45/docs/youra_research/20260325_mldpr/h-m2/figures/centroid_overlay.png`
- `/home/anonymous/YouRA_results_new_4_sonnet45/TEST_mldpr_opus45/docs/youra_research/20260325_mldpr/h-m2/figures/descriptor_radar.png`
- `/home/anonymous/YouRA_results_new_4_sonnet45/TEST_mldpr_opus45/docs/youra_research/20260325_mldpr/h-m2/figures/descriptor_scatter.png`
- `/home/anonymous/YouRA_results_new_4_sonnet45/TEST_mldpr_opus45/docs/youra_research/20260325_mldpr/h-m2/figures/distance_heatmap.png`

---

## Conclusion

The MECHANISM hypothesis is **SUPPORTED**.

Shape descriptors successfully differentiate cluster centroids with variance ratio > 2.0 on 3 descriptors.

**Passing Descriptors**: growth_ratio, changepoint_count, derivative_variance

**Key Findings**:
- 3 of 4 descriptors exceed variance ratio threshold
- Cluster profiles are distinct (min distance = 0.3170)
- Shape-based analysis reveals meaningful differentiation between adoption trajectory clusters

**Next Step**: Proceed to h-m3 (archetype recovery)
