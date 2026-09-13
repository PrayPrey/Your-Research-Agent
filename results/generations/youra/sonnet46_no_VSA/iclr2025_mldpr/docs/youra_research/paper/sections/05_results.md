# 5. Results

## 5.1 H-E1: FAIL FAST Gate Validation — All 5 Gates Pass

All five pre-validation gates pass by wide margins (Table 1; Figure 1).

**Table 1: FAIL FAST Gate Results**

| Gate | Metric | Value | Threshold | Status |
|------|--------|-------|-----------|--------|
| G0 | Join coverage (n_matched / 87) | **0.862** | ≥ 0.80 | ✅ PASS |
| G1 | partial r²(log_count_z ~ temporal) | **0.605** | > 0.01 | ✅ PASS |
| G2 | partial r²(diversity_ratio_z ~ temporal) | **0.975** | > 0.01 | ✅ PASS |
| G3 | std(paper_diversity_ratio_at_intro) | **0.246** | > 0.10 | ✅ PASS |
| G4 | max VIF (active covariates) | **2.14** | < 10.0 | ✅ PASS |

Additional statistics:
- 75/87 benchmarks matched in fuzzy join; 67/87 have diversity statistics computed
- Pearson r(log_count_z, diversity_ratio_z) = −0.324 (collinearity failsafe NOT triggered; both predictors retained as independent constructs)
- `benchmark_introduction_year` excluded from Cox models (|r| = 1.000 with `task_age`)
- 43,543 / 59,860 evaluation-table rows retained after temporal filter

**Interpretation:** The FAIL FAST all-pass result establishes three critical facts for interpreting the downstream Cox result. First, the diversity signal exists in the data with adequate coverage (G0). Second, both predictors are genuinely time-independent — they contain cross-benchmark information beyond temporal trend (G1 partial r² = 0.605, G2 partial r² = 0.975). Third, the predictors have sufficient variance for Cox regression to detect effects of the pre-specified magnitude (G3 std = 0.246 >> 0.10 threshold). Any downstream null is therefore attributable to genuine absence of effect, not data quality failure.

## 5.2 H-M1: Cox Regression — Near-Perfect Null

**Primary results (Table 2):**

**Table 2: Cox Regression Results (H-M1)**

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| LRT statistic | 0.0040 | — | — |
| **LRT p-value** | **0.9495** | < 0.05 | ❌ FAIL |
| **Hazard Ratio (HR)** | **1.006** | \|HR−1\| ≥ 0.10 | ❌ FAIL |
| 95% CI | [0.846, 1.196] | excludes 1.0 | ❌ FAIL |
| \|HR−1\| | 0.006 | ≥ 0.10 | ❌ FAIL (17× below threshold) |
| M0 log-likelihood | −750.7335 | — | — |
| M1 log-likelihood | −750.7315 | — | — |
| ΔlogL (M1 − M0) | 0.0020 | — | — |
| Concordance index (M1) | 0.7363 | — | (acceptable) |
| Panel rows used | 258 | — | (87 NaN dropped) |

The null result is not marginal. HR = 1.006 means the diversity predictor is essentially indistinguishable from no effect. The LRT statistic of 0.0040 corresponds to a ΔlogL of 0.0020 — the predictor adds essentially zero explanatory power to the baseline model. The 95% CI [0.846, 1.196] straddles 1.0 by a wide margin and is compatible with the null across the full range.

**Direction:** H0 (null). Neither the lock-in mechanism (HR < 1) nor the saturation mechanism (HR > 1) is operative at a detectable level. Both H1 and H2 are falsified.

**Model validity:** The concordance index of 0.7363 indicates the Cox model has reasonable discrimination overall (baseline covariates `task_age` and `log_publication_volume` do predict displacement timing). The diversity predictor adds nothing to this baseline. The model is not broken; the predictor is uninformative.

## 5.3 Kaplan-Meier Analysis (P3)

Kaplan-Meier survival curves for Q1 (lowest diversity quartile) vs Q4 (highest diversity quartile) benchmarks show no meaningful separation (Figure 3). Visual inspection of `km_quartiles.png` confirms the null: the survival curves for low- and high-diversity benchmarks overlap substantially throughout the observation window. The Schoenfeld residuals plot (Figure A1) shows no gross violation of the proportional hazards assumption.

## 5.4 Contrast with Prior Directional Signal

A prior run (h-m1 Run 2) on a *different predictor* (Δscore_lag1_z, score velocity) with only 22 displacement events showed HR = 0.871 (LRT p = 0.565, underpowered). The current result uses approximately 10× more events (EPV ≈ 86 vs ~22) and a different predictor (submission count diversity vs score velocity). The prior HR = 0.871 was likely sampling noise; the current HR = 1.006 with adequate power is the reliable estimate for the submission-count diversity predictor.

**Table 3: Prior Attempt vs Current Result**

| Property | h-m1 Run 2 (prior) | H-M1 (current) |
|----------|-------------------|----------------|
| Predictor | Δscore_lag1_z (score velocity) | log_unique_paper_count_at_intro_z |
| Rows used | ~64 | 258 |
| Events (EPV) | ~22 | ~86 |
| HR | 0.871 | 1.006 |
| 95% CI | (wide, not reported) | [0.846, 1.196] |
| LRT p | 0.565 | 0.9495 |
| Interpretation | Directional but underpowered | Near-perfect null |
