# H-E1 Validation Report
**Hypothesis:** H-E1 — Deduplication Benchmark Signature (EXISTENCE)
**Generated:** 2026-08-25T15:10:03Z
**Gate:** MUST_WORK
**Verdict:** PASS

---

## Experiment Setup

| Parameter | Value |
|-----------|-------|
| Models | Pythia 160M, 410M, 1B, 6.9B (Pile + dedup-Pile) |
| Token matching | Pile step 99,000 ≈ 207B tokens (mismatch <0.3%) |
| dedup-Pile checkpoint | step 143,000 (final) |
| Benchmarks | MMLU (5-shot), HellaSwag (0-shot), ARC-Challenge (25-shot), WinoGrande (5-shot) |
| Statistical test | Paired t-test across 4 model sizes (n=4), two-tailed |
| Significance threshold | Bonferroni-corrected α = 0.0125 (0.05 / 4 benchmarks) |

## Checkpoint Map

| Size | Pile step | dedup step | Token mismatch |
|------|-----------|------------|---------------|
| 160m | step99000 | step143000 | 0.30% |
| 410m | step99000 | step143000 | 0.30% |
| 1b | step99000 | step143000 | 0.30% |
| 6.9b | step99000 | step143000 | 0.30% |

## Statistical Results

| Benchmark | t-stat | p-value | mean Δ (dedup−pile) | Direction | Significant? |
|-----------|--------|---------|----------------------|-----------|-------------|
| mmlu | -5.574 | 0.0114 | -0.0071 | pile_higher | **Yes*** |
| hellaswag | 3.283 | 0.0463 | +0.0159 | dedup_higher | No |
| arc_challenge | 5.362 | 0.0127 | +0.0122 | dedup_higher | No |
| winogrande | 0.038 | 0.9722 | +0.0002 | dedup_higher | No |

## Gate Evaluation

**Condition:** ≥1 benchmark with p < 0.0125 (Bonferroni) across ≥2 model sizes (implicit in paired t-test n=4)

**Mechanism Verified:** True
**Gate Passed:** True

### Verdict: PASS

Statistically significant deduplication effect detected on: **mmlu**.

H-E1 EXISTENCE hypothesis confirmed: deduplication produces a detectable benchmark signature.
Proceed to Phase 5 for baseline comparison.

---

## Files

| File | Description |
|------|-------------|
| `checkpoint_map.json` | Token-matched checkpoint steps |
| `results_matrix.json` | Accuracy[size][corpus][benchmark] |
| `statistical_results.json` | Full t-test results |
| `figures/differential_bar.png` | Per-benchmark accuracy difference |
| `figures/scaling_plot.png` | Scaling curves Pile vs dedup-Pile |
| `figures/paired_scatter.png` | Paired scatter per benchmark |
| `figures/pvalue_heatmap.png` | -log10(p) significance chart |
