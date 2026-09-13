# H-M2 Validation Report

**Hypothesis**: Corpus Entropy → Model Logit Margin Internalization
**Gate Type**: SHOULD_WORK
**Gate Result**: FAIL (EXPLORE)
**Generated**: 2026-03-15 02:39:30 UTC

---

## Executive Summary

H-M2 tests whether training corpus occupational-demographic entropy (H(occ|demo))
is internalized by Pythia-1B as a logit margin for gender-stereotyped occupations.

**Primary Gate (Spearman ρ > 0, p < 0.01):**
- Spearman ρ = 0.3571
- p-value = 0.431611
- 95% CI: [-0.6471, 0.9608]
- **Verdict: FAIL_EXPLORE**
- Reason: p=0.4316 >= 0.01 (not significant)

---

## Probe Results

| Config | Mean Logit Margin | N Samples |
|--------|-------------------|-----------|
| C0 | -0.0108 | 2160 |
| C1 | -0.3225 | 2160 |
| C2 | -0.4192 | 2160 |
| C3 | -0.5540 | 2160 |
| C4 | -0.4921 | 2160 |
| C5 | -0.3921 | 2160 |
| C6 | -0.2762 | 2160 |
| C7 | -0.5062 | 2160 |

Configs used for main analysis: ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6']

---

## Statistical Tests

### 1. Spearman Rank Correlation (Primary Gate)

- ρ = 0.3571
- p = 0.431611
- 95% CI = [-0.6471, 0.9608]
- N bootstrap = 1000
- Gate threshold: ρ > 0, p < 0.01
- **Gate: FAIL**

### 2. Log-Linear OLS (logit_margin ~ log(H_entropy))

- Coefficient: 0.3629
- Intercept: -0.7648
- R²: 0.0354
- p-value: 0.6863
- Meets R²>0.3 criterion: False

### 3. Negative Control (C7 vs C0)

**|C7-C0| = 0.4953** — FAIL (threshold: 0.01)

---

## Figures Generated

1. `figures/01_entropy_vs_margin.png` — Scatter: H(occ|demo) vs. mean logit margin
2. `figures/02_logit_margin_heatmap.png` — Heatmap: occupation × config
3. `figures/03_training_curves.png` — Training loss curves per config
4. `figures/04_negative_control.png` — C0 vs C7 comparison
5. `figures/05_config_comparison.png` — Logit margins sorted by entropy

---

## Gate Decision

**Gate Type**: SHOULD_WORK
**Result**: FAIL_EXPLORE

✗ Gate FAILED: Gate conditions not met. Action: EXPLORE — investigate training depth, probe design, or corpus quality.

---

## Notes

- Quick run (50B tokens, 95368 steps) used for PoC gating
- Architecture: Pythia-1B (GPT-NeoX), hidden_size=2048, 16 layers
- Probe: WinoBias 20 occupation pairs × 50+ templates
- Corpus configs: C0 (unfiltered) through C6 (filtered) + C7 (negative control)
- H-M2 builds on H-M1 (occupational entropy) and H-E1 (corpus construction)
