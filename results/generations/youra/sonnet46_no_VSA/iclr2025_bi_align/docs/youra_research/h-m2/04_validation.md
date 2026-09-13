# H-M2 Phase 4 Validation Report

**Hypothesis:** H-M2 — Partial Spearman + Fisher Z Difference Test  
**Date:** 2026-07-30  
**Gate Type:** MUST_WORK  
**Gate Result:** PASS  

---

## 1. Environment

- Conda env: `youra-h-m2` (Python 3.11.15)
- pingouin: 0.6.1
- Data: `h-e1/code/data/llm_leaderboard_v1/llm.csv` (N=500) merged with `h-e1/code/data/bbq_scores/bbq_per_model.csv` (N=300) → N=299 inner join → N=296 after dropna

---

## 2. Test Results

**pytest:** 12/12 passed  

| Test | Result |
|------|--------|
| test_fisher_z_known_values | PASS |
| test_fisher_z_identical_rhos_gives_zero_diff | PASS |
| test_fisher_z_significant_outcome | PASS |
| test_fisher_z_null_outcome | PASS |
| test_bbq_normalization_in_load_data | PASS |
| test_gate_pass_significant | PASS |
| test_gate_pass_null | PASS |
| test_gate_fail_nan_pvalue | PASS |
| test_gate_fail_none_pvalue | PASS |
| test_compute_raw_spearman_returns_keys | PASS |
| test_compute_partial_spearman_returns_keys | PASS |
| test_mechanism_activation_check | PASS |

---

## 3. Experiment Results

| Metric | Value |
|--------|-------|
| N | 296 |
| Families | 51 (30 with ≥3 models) |
| raw_rho (TruthfulQA MC2 × BBQ) | 0.7322 |
| raw_p | 5.83e-51 |
| raw CI 95% (BCa) | (0.670, 0.780) |
| partial_rho (controlling MMLU) | 0.3432 |
| partial_p | 1.40e-09 |
| partial CI 95% (BCa) | (0.180, 0.492) |
| CI overlap | non-overlapping |
| z_diff | 6.9679 |
| Fisher Z p-value | < 0.0001 |
| Outcome | SIGNIFICANT |

---

## 4. Gate Evaluation

**Gate type:** MUST_WORK — p_value computed without error, in [0, 1]

- p_value = ~3.2e-12 (computed successfully, not NaN, in valid range)
- **Gate: PASS**

---

## 5. Bugs Fixed During Coder-Validator Loop

1. **pingouin column name mismatch** — `p-val` vs `p_val`: pingouin 0.6.1 uses `p_val`; fixed with dynamic detection.
2. **`evaluate_gate` None-safety**: `results.get("p_value", 1.0)` returned `None` when key present with None value; fixed with explicit None check.
3. **Log format None error**: `f"{p_value:.4f}"` crashed when p_value is None; fixed with conditional formatting.
4. **Missing BBQ column**: main CSV lacks `BBQ_accuracy`; added `bbq_path` config field and inner-join merge in `load_data`.

---

## 6. Output Artifacts

- `code/results/h_m2_results.json` — full results dict (arrays serialized as lists)
- `code/results/h_m2_summary.txt` — human-readable summary
- `figures/fig1_rho_comparison.png` — raw vs partial rho bar chart
- `figures/fig2_scatter_mmlu_gradient.png` — scatter with MMLU gradient
- `figures/fig3_bootstrap_distributions.png` — bootstrap distributions
- `figures/fig4_family_rho_bar.png` — per-family rho bar chart
- `figures/fig5_fisher_z_numberline.png` — Fisher Z number line

---

## 7. Interpretation

MMLU (general capability) explains a substantial portion of the TruthfulQA–BBQ correlation. Controlling for MMLU reduces rho from 0.73 to 0.34 — a statistically significant reduction (Fisher Z diff test: z=6.97, p<0.0001, CIs non-overlapping). The residual partial correlation (0.34, p=1.4e-9) remains significant, indicating alignment-specific co-movement beyond what general capability accounts for.
