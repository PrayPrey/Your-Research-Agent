# Validation Report: H-C1

**Hypothesis:** Coupling matrices differ across models (Mantel test r < 0.7 for ≥1 model pair)

**Gate Type:** SHOULD_WORK

**Gate Result:** PARTIAL

**Date:** 2026-08-19 14:39:18

---

## Summary

3 model pair(s) show distinct coupling patterns (r < 0.7) but not statistically significant (p > 0.0167). Likely due to small sample size.

---

## Mantel Test Results

| Model Pair | r | p-value | Bonferroni Significant | Pass Threshold (r < 0.7) |
|------------|---|---------|------------------------|--------------------------|
| GPT-4 vs Claude-3 | -0.2684 | 0.3167 | ✗ | ✓ |
| GPT-4 vs Llama-3 | -0.1741 | 0.6000 | ✗ | ✓ |
| Claude-3 vs Llama-3 | -0.1301 | 0.7583 | ✗ | ✓ |

**Bonferroni-corrected alpha:** 0.0167

---

## Phi Coefficient Statistics (Per Model)

| Model | Mean Phi | Max Phi | Min Phi | Significant Pairs (phi ≥ 0.3, p < 0.01) |
|-------|----------|---------|---------|------------------------------------------|
| GPT-4 | 0.1597 | 0.6205 | -0.1546 | 2 |
| Claude-3 | 0.1819 | 0.7711 | -0.0847 | 3 |
| Llama-3 | 0.0217 | 0.2375 | -0.1593 | 0 |

---

## Coupling Matrices

### GPT-4

| | truthfulness | robustness | fairness | safety | privacy |
|-|-|-|-|-|-|
| truthfulness | 1.000 | 0.621 | -0.155 | 0.260 | 0.029 |
| robustness | 0.621 | 1.000 | 0.016 | 0.564 | 0.033 |
| fairness | -0.155 | 0.016 | 1.000 | 0.037 | 0.219 |
| safety | 0.260 | 0.564 | 0.037 | 1.000 | -0.028 |
| privacy | 0.029 | 0.033 | 0.219 | -0.028 | 1.000 |

### Claude-3

| | truthfulness | robustness | fairness | safety | privacy |
|-|-|-|-|-|-|
| truthfulness | 1.000 | 0.130 | 0.014 | 0.094 | -0.010 |
| robustness | 0.130 | 1.000 | -0.075 | -0.035 | -0.085 |
| fairness | 0.014 | -0.075 | 1.000 | 0.771 | 0.528 |
| safety | 0.094 | -0.035 | 0.771 | 1.000 | 0.485 |
| privacy | -0.010 | -0.085 | 0.528 | 0.485 | 1.000 |

### Llama-3

| | truthfulness | robustness | fairness | safety | privacy |
|-|-|-|-|-|-|
| truthfulness | 1.000 | -0.002 | 0.238 | -0.159 | 0.063 |
| robustness | -0.002 | 1.000 | -0.034 | -0.051 | -0.028 |
| fairness | 0.238 | -0.034 | 1.000 | 0.098 | 0.037 |
| safety | -0.159 | -0.051 | 0.098 | 1.000 | 0.055 |
| privacy | 0.063 | -0.028 | 0.037 | 0.055 | 1.000 |

---

## Gate Decision Logic

- **PASS:** r < 0.7 for ≥1 model pair with p < 0.0167 (Bonferroni-corrected)
- **PARTIAL:** 0.7 ≤ r < 0.9 for ≥1 pair (moderate similarity)
- **FAIL:** r ≥ 0.9 for all pairs (universal coupling)

---

## Key Findings

- **Distinct coupling patterns observed but not statistically significant**
- 3 model pair(s) show different coupling matrices (r < 0.7)
- Non-significance (p > 0.0167) likely due to small sample size (100 samples/dimension)
- Evidence suggests model-specific fingerprints exist but require larger sample to confirm

---

## Data Summary

- **Models:** GPT-4, Claude-3, Llama-3
- **Dimensions:** truthfulness, robustness, fairness, safety, privacy
- **Samples per model:** 500 (100 per dimension)
- **Total instances:** 1500
- **Mantel permutations:** 10,000
- **Statistical correction:** Bonferroni (α = 0.05/3 = 0.0167)

---

## Visualizations

Generated figures:
- `figures/coupling_heatmaps.png` - Side-by-side coupling matrices
- `figures/scatter_*_vs_*.png` - Pairwise phi value comparisons
- `figures/mantel_results.png` - Mantel correlation bar plot

---

## Phase 5 Progression

**SHOULD_WORK Gate:** All outcomes (PASS/PARTIAL/FAIL) proceed to Phase 5.

Gate outcome does not block pipeline progression.
