# H-M2 Validation Report
## NLI Clustering Aggregation Behavior Analysis

**Generated:** 2026-05-11T11:17:26.522106
**Hypothesis ID:** h-m2
**Gate Type:** SHOULD_WORK
**Gate Result:** PIVOT
**Cluster Count Source:** hm1_summary

---

## Gate Decision: PIVOT

| Criterion | Threshold | Value | Status |
|-----------|-----------|-------|--------|
| Aggregation Rate | ≥ 0.50 | 0.2720 | ❌ FAIL |
| CI Lower Bound | ≥ 0.30 | 0.2530 | ❌ FAIL |
| Gate Pass | Both | False | ❌ |

**Bootstrap 95% CI:** [0.2530, 0.2915]

---

## Primary Metrics

| Metric | Value |
|--------|-------|
| Aggregation Rate | 0.2720 |
| Bootstrap CI Lower | 0.2530 |
| Bootstrap CI Upper | 0.2915 |
| Gate Pass | False |
| Gate Result | **PIVOT** |
| Collapse Rate | 0.0020 |
| Mean Cluster Count | 4.6440 |
| Std Cluster Count | 0.6567 |
| Median Cluster Count | 5.0000 |
| Point-Biserial r | nan |
| p-value | nan |
| N Examples | 2000 |

---

## Cluster Count Distribution

| Cluster Count | Frequency | Fraction |
|---------------|-----------|----------|
| 1 | 4 | 0.002 |
| 2 | 22 | 0.011 |
| 3 | 112 | 0.056 |
| 4 | 406 | 0.203 |
| 5 | 1456 | 0.728 |

---

## Figures

- `figures/aggregation_rate.png` — Aggregation rate bar chart with 95% CI vs gate threshold
- `figures/cluster_count_dist.png` — Histogram of cluster count values (1–5)
- `figures/cluster_count_by_label.png` — Box plot: cluster count by hallucination label
- `figures/cluster_count_cdf.png` — CDF of cluster counts with threshold line at x=4

## ⚠️ PIVOT Condition (A2 Violation)

The aggregation rate is below the 0.30 threshold, indicating that deberta-large-mnli NLI clustering
does NOT produce meaningful semantic aggregation on HaluEval-QA responses.

**Interpretation:** This is an A2 violation — the NLI model does not generalize to HaluEval-QA
response style. Short factual QA answers are treated as semantically distinct by deberta-large-mnli
even when they convey equivalent meaning.

**Pipeline Action:** PIVOT to alternative NLI thresholds or models. Pipeline continues to H-M3.

---

## Summary

H-M2 analyzed the NLI clustering aggregation behavior on 2,000 HaluEval-QA examples using
deberta-large-mnli (lorenzkuhn/semantic_uncertainty). Cluster counts were loaded from hm1_summary.

**Key finding:** aggregation_rate = 0.2720 (95% CI: [0.2530, 0.2915]).
Mean cluster count = 4.6440 (expected ~4.644 from H-M1).

**Gate:** PIVOT (SHOULD_WORK — failure does not halt pipeline).
