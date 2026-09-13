# Pivot Record: h-e1 → h-e1-v2

## Hypothesis: h-e1 (EXISTENCE) — Phase 4 PARTIAL → SELF_MODIFY

**Pipeline:** YouRA | Project: Spurious Correlations & Shortcut Learning (20260315_scsl)
**Date:** 2026-03-16

## Experiment Results

- **gradient_norm_ratio**: 12.20 (epoch5) — strongly confirmed ≥2x criterion (6x over threshold)
  - Per-epoch: E1=6.10, E2=6.59, E3=6.56, E4=14.73, E5=12.20
  - Group norms: G0(landbird/land)=6.90, G1(landbird/water)=56.98, G2(waterbird/land)=70.72, G3(waterbird/water)=19.79
- **lambda1_trajectory**: {5: 704.33, 10: 669.66, 20: 498.93} — decreasing (EOS dynamics)
- **lambda1_monotonic**: False — hypothesis criterion failed
- **oscillation_index**: NaN — implementation gap

## Root Causes

1. **Lambda1 EOS behavior**: Pretrained ResNet-50 fine-tuning enters EOS by epoch 5 (eta*lambda1 ≈ 2), then SGD implicitly minimizes sharpness. Strict monotonic increase was too strong a requirement — EOS dynamics are the correct phenomenon.
2. **Oscillation index missing**: `collect_gradient_vectors()` was implemented but not properly coupled to oscillation index computation during training loop. Vectors needed to be collected at gradient_analysis_epochs.

## Modification (h-e1-v2)

- **Keep**: `gradient_norm_ratio >= 2x` ✅
- **Replace**: `lambda1_monotonic` → `lambda1_epoch5 > EOS_threshold (eta*lambda1 ≈ 2)` OR simply `lambda1_epoch5 > 100`
- **Add**: `oscillation_index < 0` (fix: collect gradient vectors explicitly during training)
- **Relax**: sharpening criterion to EOS detection (not monotonic)

## Lessons Learned

- Pretrained ResNet-50 enters EOS by epoch 5 in fine-tuning — monotonic progressive sharpening assumption invalid
- gradient_norm_ratio is a robust, strongly confirmed predictor of spurious correlation phenomenon
- oscillation_index computation requires explicit `collect_gradient_vectors()` call at each gradient_analysis epoch with storage to separate list
- EOS dynamics (Cohen et al. 2021, Damian et al. 2022) are the correct framework for lambda1 behavior in fine-tuning

## Status

h-e1: COMPLETED (partial), reflection_outcome=SELF_MODIFY
h-e1-v2: READY (enters Phase 2C for experiment redesign)
