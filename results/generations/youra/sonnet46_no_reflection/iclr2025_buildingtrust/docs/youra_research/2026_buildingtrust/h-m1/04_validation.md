# Phase 4 Validation Report — H-M1

**Date:** 2026-05-12
**Generated:** 2026-05-12T14:30:00 (updated after mock fix)
**Hypothesis:** H-M1 — RI → ECE Mechanism (MUST_WORK)
**Gate Type:** MUST_WORK
**Gate Result:** PARTIAL (1/3 conditions met)
**Execution Mode:** UNATTENDED
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 5

---

## Summary

The experiment ran successfully with **real data** from the Open LLM Leaderboard v2 (arc_challenge benchmark, 1172 samples per model, 30 models). Mock data fallback was removed. ECE was computed via `uncertainty-calibration` from per-sample softmax probabilities derived from leaderboard log-likelihoods. `mean_confidence` was computed as the mean of per-sample max-choice softmax probabilities.

**Key result:** ρ(RI, ECE | PC1, mean_confidence) = **−0.535**, p = 0.0034. The correlation is statistically significant (p < 0.05) but in the **opposite direction** from the hypothesis. Higher RI (adversarial fragility) is associated with *lower* ECE (better calibration), not higher ECE.

---

## Gate Evaluation

| Condition | Threshold | Actual | Pass? |
|-----------|-----------|--------|-------|
| Spearman partial ρ(RI, ECE) | ≥ 0.4 | **−0.535** | FAIL (wrong sign) |
| Holm-corrected p-value | < 0.05 | 0.0034 | PASS |
| Family sign consistency | ≥ 2/3 positive | 1/3 (only Qwen: +0.36) | FAIL |

**Gate: PARTIAL** — p-value criterion met but ρ is negative and families show inconsistent signs.

---

## Data Sources (REAL DATA — No Mock)

| Component | Source | Notes |
|-----------|--------|-------|
| ECE scores | Open LLM Leaderboard v2, `leaderboard_arc_challenge` | n=1172 per model, softmax from log-likelihoods |
| mean_confidence | Open LLM Leaderboard v2, `leaderboard_arc_challenge` | Mean of per-sample max-choice softmax prob |
| RI scores | H-E1 validated outputs (`ri_scores.csv`) | Reused directly |
| PC1 | H-E1 model_matrix.csv | v2 leaderboard capability |
| Model set | 30 LLMs (LLaMA, Mistral, Qwen, Gemma, Falcon, etc.) | Same as H-E1 |

---

## Full Experiment Results

### Primary Analysis
- **ρ(RI, ECE | PC1, mean_confidence)** = −0.5347
- **p-value** = 0.0034
- **Bootstrap 95% CI** = [−0.782, −0.101]
- **n** = 30

### Per-Family Results (Holm-corrected)

| Family | n | ρ | p (raw) | p (Holm) | Sign |
|--------|---|---|---------|----------|------|
| LLaMA | 9 | −0.244 | 0.599 | 1.000 | Negative |
| Mistral | 6 | −0.827 | 0.173 | 0.519 | Negative |
| Qwen | 6 | +0.364 | 0.636 | 1.000 | Positive |

Consistent positive families: 1/3 (only Qwen shows positive sign, not significant).

### Secondary Statistics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Baseline ρ(PC1, ECE) | −0.511 | — | Reference |
| VIF(RI) | 1.000 | < 5.0 | PASS |
| VIF(PC1) | 1.000 | < 5.0 | PASS |
| VIF(mean_confidence) | 1.000 | < 5.0 | PASS |
| Fisher z-stat | −0.561 | — | p = 0.575 (n.s.) |
| Cook's distance outliers | 3 flagged | > 4/30 | Meta-Llama-3-70B, gemma-7b-it, stablelm-zephyr-3b |

---

## Scientific Interpretation

The hypothesis predicted ρ ≥ +0.4 (sharper decision boundaries → higher miscalibration). Instead, ρ = −0.535: models with higher adversarial fragility (RI) tend to be **better calibrated** on QA benchmarks (lower ECE on arc_challenge).

Possible explanations:
1. **Instruction-tuned models confound both axes**: Chat/instruct variants have higher RI AND higher ECE from overconfidence — but patterns may invert when controlling for PC1.
2. **Benchmark mismatch**: arc_challenge ECE measures calibration on reasoning tasks; RI measures adversarial fragility on NLI-style attacks. These tap different failure modes.
3. **Scale effect**: Larger pretrained models have both lower RI and lower ECE (better calibration), creating a negative partial correlation that survives PC1 control.

The baseline correlation ρ(PC1, ECE) = −0.511 (p = 0.0039) is nearly identical to ρ(RI, ECE | PC1) = −0.535, suggesting RI adds little unique signal beyond capability for predicting ECE.

---

## Mock Data Fix Verification

- **Previous run:** Used `_mock_ece()` Gaussian synthetic ECE ~ N(0.12, 0.04) → FAIL gate with rho=0.1612
- **This run:** Real ECE from Open LLM Leaderboard v2 arc_challenge (1172 samples/model)
- **ECE range:** 0.175 (Llama-3-70B) to 0.472 (stablelm-zephyr-3b) — realistic range for LLMs
- **mean_confidence range:** 0.789 (mpt-7b) to 0.958 (Meta-Llama-3-70B-Instruct) — typical softmax overconfidence
- Mock fallback removed from `ece_computer.py` — raises `RuntimeError` if no cache exists

---

## Figures Generated

6 figures saved to `h-m1/figures/`:
- `fig1_ri_ece_scatter.png` — RI vs ECE scatter with partial regression line
- `fig2_residuals_scatter.png` — Partial regression residuals
- `fig3_family_subplots.png` — Per-family RI vs ECE (LLaMA/Mistral/Qwen)
- `fig4_reliability_diagram.png` — Average reliability diagram by RI quartile
- `fig5_rho_comparison_bar.png` — ρ(PC1,ECE) vs ρ(RI,ECE|PC1) comparison
- `fig6_gate_summary.png` — Gate summary with threshold

---

## Test Suite

All unit tests passed:
- `test_data_loader.py` ✓
- `test_ece_computer.py` ✓
- `test_partial_corr.py` ✓
- `test_evaluate.py` ✓

---

## Conclusion

H-M1 gate: **PARTIAL FAIL**. The MUST_WORK condition requires ρ ≥ +0.4. The actual ρ = −0.535 is highly significant but inverted. This constitutes a scientific finding (RI and ECE are anticorrelated when controlling for capability) that contradicts the sharp-boundary overconfidence hypothesis. Per gate rules: MUST_WORK failure routes to Phase 2A for hypothesis revision.
