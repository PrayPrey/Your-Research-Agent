# PRD: H-M1 — DPO Bias-Avoidance Signal Detection

**Date:** 2026-08-31
**Author:** yoon303@ust.ac.kr
**Hypothesis:** H-M1 (MECHANISM)
**Phase:** 3 — Implementation Planning

---

## 1. Objective

Verify that DPO-trained 7B models score higher than matched SFT-trained models on BBQ and WinoGender benchmarks, providing mechanistic evidence that DPO preference signal encodes bias-avoidance.

**Gate:** k_BBQ ≥ 4/6 pairs show DPO > SFT AND one-sided binomial sign test p ≤ 0.125.

---

## 2. Background

H-E1 validated that DPO/SFT 7B model 4D benchmark vectors are separable (LOO k-NN accuracy=83.3%, p=0.031). H-M1 asks *why*: specifically, whether BBQ and WinoGender — the bias-sensitive dimensions — are the primary drivers. This is a post-hoc statistical analysis of H-E1 results; **no new model inference required**.

---

## 3. Scope

### In Scope
- Load H-E1 benchmark scores (BBQ, WinoGender, TruthfulQA MC2, WinoGrande) from existing results files
- Compute per-pair deltas (DPO − SFT) for BBQ and WinoGender
- Run one-sided binomial sign test on BBQ (primary gate) and WinoGender (secondary)
- Compute Fisher's criterion for all 4 benchmark dimensions
- Generate 4 required figures
- Produce gate verdict and 04_validation.md report

### Out of Scope
- New model inference (H-E1 scores reused)
- Model training
- New benchmark evaluation
- Hyperparameter search

---

## 4. Data Requirements

**Source:** H-E1 lm-evaluation-harness results JSON files at `docs/youra_research/h-e1/results/` (or equivalent H-E1 output directory).

**Required scores per model:**
- `bbq` — accuracy (disambiguation, across all 9 categories; aggregate)
- `winogender_mc_female` + `winogender_mc_male` — accuracy (averaged to single WinoGender score)
- `truthfulqa_mc2` — MC2 accuracy (control)
- `winogrande` — accuracy (control)

**Model pairs (6 matched DPO/SFT):**
- Pair 1: zephyr-7b-sft-full vs zephyr-7b-beta (Mistral-7B base)
- Pairs 2–6: as established in H-E1 execution (exact names from H-E1 results)

---

## 5. Implementation Requirements

### Core Analysis Script (`h-m1/run_hm1.py`)
- Load scores from H-E1 results (JSON parsing or manual dict if results not persisted)
- Compute signed deltas per pair for BBQ and WinoGender
- `scipy.stats.binomtest` for one-sided p-values (n=6, H1: DPO>SFT)
- Fisher's criterion for all 4 dimensions
- Print gate verdict: PASS/FAIL

### Figures (saved to `h-m1/figures/`)
1. **fig1_bbq_winogender_paired_bar.png** — paired DPO vs SFT bar chart for BBQ and WinoGender (group means + per-pair)
2. **fig2_bbq_delta_signed_bar.png** — per-pair signed delta BBQ_DPO − BBQ_SFT; positive=green, negative=red; dashed zero line
3. **fig3_fisher_criterion_bar.png** — Fisher's criterion for all 4 benchmark dimensions (BBQ, WinoGender, TruthfulQA, WinoGrande)
4. **fig4_winogender_delta_signed_bar.png** — same as fig2 but for WinoGender

### Validation Report (`h-m1/04_validation.md`)
- Gate result (PASS/FAIL)
- k_BBQ, p_BBQ, k_WG, p_WG
- Per-pair delta table
- Fisher's criterion table
- Figure references

---

## 6. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| k_BBQ | ≥ 4/6 pairs DPO > SFT | Primary gate |
| p_BBQ | ≤ 0.125 (one-sided binomial) | Primary gate |
| k_WG | ≥ 4/6 (soft) | Exploratory |
| Code runs without error | — | Required |
| All 4 figures generated | — | Required |

---

## 7. Dependencies

- Python 3.10+
- scipy ≥ 1.7
- numpy ≥ 1.21
- matplotlib
- H-E1 results files (pre-computed benchmark scores)

---

## 8. Timeline

**Estimated compute time:** < 1 minute (CPU only, pure statistical analysis)
**Implementation effort:** LIGHT — single analysis script + 4 figures + report
