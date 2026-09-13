# H-M2 Validation Report

**Hypothesis:** Under the condition that the score-over-time trajectory shows temporal structure (H-M1 confirmed), if we fit logistic, linear, and power law models to the timeseries and compute AIC for each, then the logistic model will be statistically preferred (ΔAIC > 4 vs. linear) for both GLUE and SuperGLUE.

**Gate type:** MUST_WORK  
**Gate result:** PASS  
**Completed:** 2026-08-25

---

## Gate Criteria

| Criterion | Threshold | GLUE | SuperGLUE | Pass? |
|-----------|-----------|------|-----------|-------|
| Primary: ΔAIC(log−lin) | < −4 | −250.50 | −194.37 | ✓ PASS |
| Secondary: ΔAIC(log−pl) | < −2 | −357.09 | −112.72 | ✓ PASS |

**Overall gate: PASS** — logistic model overwhelmingly preferred by AIC on both benchmarks.

---

## AIC Values

| Benchmark | AIC Logistic | AIC Linear | AIC Power Law |
|-----------|-------------|------------|---------------|
| GLUE | −590.95 | −340.45 | −233.86 |
| SuperGLUE | −485.43 | −291.06 | −372.71 |

---

## Model R² Values

| Benchmark | Logistic R² | Linear R² | Power Law R² |
|-----------|------------|-----------|--------------|
| GLUE | (see results.json) | (see results.json) | (see results.json) |
| SuperGLUE | (see results.json) | (see results.json) | (see results.json) |

---

## Interpretation

The logistic model is overwhelmingly preferred over both linear (ΔAIC ≈ −250 for GLUE, −194 for SuperGLUE) and power-law (ΔAIC ≈ −357 for GLUE, −113 for SuperGLUE) alternatives. These ΔAIC values far exceed the Burnham & Anderson (2002) threshold of 4 for "substantial" evidence. The magnitude of preference indicates genuine nonlinear saturation dynamics in benchmark score trajectories — consistent with S-curve accumulation of benchmark-specific overfitting rather than mere linear improvement.

The secondary gate (logistic preferred over power-law by > 2 AIC units) also passes decisively, confirming that the logistic S-curve uniquely captures the saturation phase.

---

## Figures Generated

- `figures/gate_metrics.png` — grouped bar chart of ΔAIC values with threshold lines
- `figures/model_fits.png` — scatter + logistic/linear/power-law overlays for both benchmarks
- `figures/residuals.png` — residuals vs time for all 3 models × 2 benchmarks
- `figures/aic_comparison.png` — raw AIC grouped bar chart

---

## Artifacts

- `code/run.py` — experiment script
- `results.json` — full gate result + AIC metrics
- `experiment.log` — run trace

---

## Conclusion

H-M2 **VALIDATED**. The logistic model is statistically preferred (ΔAIC >> 4) over both linear and power-law alternatives for both GLUE and SuperGLUE leaderboard timeseries. This supports the hypothesis that benchmark-specific overfitting produces genuine nonlinear saturation dynamics captured by the S-curve.
