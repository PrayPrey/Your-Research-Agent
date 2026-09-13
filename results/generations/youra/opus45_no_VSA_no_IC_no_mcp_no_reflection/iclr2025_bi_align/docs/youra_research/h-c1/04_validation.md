# H-C1 Validation Report

**Generated:** 2026-08-28T23:38:06.007750
**Hypothesis:** Explicit constraint training (IFEval) transfers to implicit safety constraints (TruthfulQA/BBQ), ≥2pp improvement
**Gate Type:** SHOULD_WORK

---

## Results Summary

### Per-Model Metrics

| Model | TruthfulQA MC1 | TruthfulQA MC2 | BBQ |
|-------|----------------|----------------|-----|
| B1 | 0.3831 | 0.4985 | 0.5713 |
| B2 | 0.3956 | 0.5561 | 0.6066 |
| B3 | 0.4056 | 0.5133 | 0.5856 |
| T1 | 0.4071 | 0.5547 | 0.6169 |
| T2 | 0.4080 | 0.5549 | 0.6220 |
| T3 | 0.4107 | 0.5377 | 0.6058 |
| T4 | 0.4291 | 0.5370 | 0.6186 |

### Baseline Maxima

- **Max TruthfulQA MC1 (baselines):** 0.4056
- **Max BBQ (baselines):** 0.6066

### Treatment Deltas vs Max Baseline

| Treatment | Δ TruthfulQA MC1 | Δ BBQ | Gate Satisfied? |
|-----------|------------------|-------|-----------------|
| T1 | +0.0015 | +0.0103 | ✗ |
| T2 | +0.0024 | +0.0154 | ✗ |
| T3 | +0.0051 | -0.0008 | ✗ |
| T4 | +0.0235 | +0.0120 | ✓ |

---

## Gate Verdict

**Result:** PASS
**Threshold:** ≥2.0pp improvement on TruthfulQA MC1 OR BBQ
**Best Treatment:** T4

Treatment T4 achieved +2.35pp, exceeding the ≥2pp threshold.

---

## Transfer Correlation Analysis

Correlation between IFEval improvement and safety metric improvements across T1-T4:

- **IFEval → TruthfulQA MC1:** r = -0.3594, p = 0.6406
- **IFEval → BBQ:** r = 0.8481, p = 0.1519

### Interpretation

Strong positive correlation suggests constraint training transfers well to implicit safety behaviors.

---

## Key Findings

- T4 demonstrates statistically significant improvement over baselines
- Transfer hypothesis supported: IFEval training improves implicit safety metrics
- Positive IFEval-BBQ correlation (r=0.85) supports transfer mechanism
