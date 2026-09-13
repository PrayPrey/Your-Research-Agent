# H-M2 Phase 4 Validation Report
**Hypothesis:** h-m2 — NFN Equivariant Encoder Permutation Sensitivity Probing
**Gate Type:** SHOULD_WORK
**Gate Result:** PASS
**Date:** 2026-05-05T15:00:00Z

---

## 1. Executive Summary

H-M2 validates that a Navon et al. permutation-equivariant NFN encoder trained on accuracy prediction exhibits **near-zero permutation sensitivity** — i.e., it produces virtually identical embeddings for permutation-equivalent weight configurations.

The SHOULD_WORK gate passes with:
- `sensitivity_score = 7.34e-07` (≈ 0.000, dual threshold: abs < 0.1 AND rel < 0.3245)
- `spearman_rho = 0.6806` (well above target 0.1041 from h-m1)
- `param_count = 521,953` (in range [475K, 525K])
- `n_pairs = 500` (sufficient, ≥ 50)

The NFN encoder achieves permutation sensitivity **885,000× lower** than the flat MLP baseline (h-m1: 0.6490 vs h-m2: 7.34e-07), confirming the equivariance property by construction.

---

## 2. Hypothesis Statement

> Under conditions of matched encoder capacity (~500K parameters ±5%) on the Schurholt MNIST-CNN zoo, if we train a Navon et al. permutation-equivariant NFN encoder on accuracy prediction, then its learned embeddings will exhibit near-zero permutation sensitivity (similar embeddings for permutation-equivalent weight configurations), because NFN encoders are equivariant by construction and map all permutation-equivalent weight vectors to identical embeddings before the final prediction head.

---

## 3. Experiment Configuration

| Parameter | Value |
|-----------|-------|
| Dataset | Schurholt ModelZooDataset MNIST-CNN (hyp_rand) |
| Architecture | Conv(8)-Conv(6)-Conv(4)-FC(20)-FC(10), 10 weight tensors |
| NFN channel_dim | 112 |
| NFN n_layers | 3 |
| NFN param_count | 521,953 |
| embed_dim | 128 |
| Epochs | 150 |
| Batch size | 32 |
| LR | 1e-3 (AdamW + CosineAnnealing) |
| Seed | 42 |
| n_pairs | 500 (50 per decile) |
| GPU | CUDA (single GPU) |

---

## 4. Gate Check Results

### SHOULD_WORK Gate Criteria
The gate passes if **both** conditions hold:
1. `sensitivity_score < 0.1` (absolute threshold)
2. `sensitivity_score < 0.3245` (relative threshold = 0.5 × flat_MLP_score)

### Results

| Check | Threshold | Value | Pass? |
|-------|-----------|-------|-------|
| Absolute gate | < 0.1 | 7.34e-07 | ✓ PASS |
| Relative gate | < 0.3245 | 7.34e-07 | ✓ PASS |
| **Overall gate** | both pass | — | **✓ PASS** |
| param_count in range | [475K, 525K] | 521,953 | ✓ |
| n_pairs sufficient | ≥ 50 | 500 | ✓ |

### Sensitivity Score Breakdown

| Metric | Value |
|--------|-------|
| sensitivity_score | 7.343696e-07 |
| mean_equiv_L2 | 2.679e-08 |
| mean_random_L2 | 3.648e-02 |
| flat_MLP_sensitivity_score (ref) | 0.6490 |
| NFN vs MLP ratio | 885,000× lower |

---

## 5. Spearman Correlation Results

| Metric | Value |
|--------|-------|
| spearman_rho (test set) | 0.6806 |
| spearman_target (from h-m1) | 0.1041 |
| Exceeds target? | Yes (6.5× higher) |

The NFN encoder achieves substantially higher Spearman correlation (0.6806) than the flat MLP (0.1041), supporting the main hypothesis that equivariant encoders better utilize capacity for accuracy-predictive features.

---

## 6. Per-Decile Sensitivity Analysis

| Decile | NFN Sensitivity Score |
|--------|----------------------|
| D0 (lowest acc) | 3.81e-07 |
| D1 | 3.01e-07 |
| D2 | 7.07e-07 |
| D3 | 8.72e-07 |
| D4 | 1.10e-06 |
| D5 | 2.06e-06 |
| D6 | 6.64e-07 |
| D7 | 1.16e-06 |
| D8 | 4.13e-07 |
| D9 (highest acc) | 1.26e-06 |

All deciles show near-zero sensitivity (order 1e-6 to 1e-7), confirming equivariance holds uniformly across the accuracy spectrum.

---

## 7. Model Architecture

### NFNEncoder (~522K params)
- `NPLinear` layers: permutation-equivariant via diag + bias_terms paths
- In-projection: maps each weight tensor to channel_dim=112 channels
- 2 hidden `NPLinear` layers with invariant context (mean pooling)
- Global mean pool over all weight tensors → readout Linear → 128-dim embedding

### NFNWithHead
- NFNEncoder + Linear(128, 1) head for accuracy regression
- Returns (embedding [B,128], prediction [B,1])

---

## 8. Generated Figures

All 6 required figures saved to `h-m2/code/figures/`:

| Figure | File | Description |
|--------|------|-------------|
| FR-7.1 | `gate_metrics_comparison.png` | Bar chart: NFN score vs thresholds vs flat MLP |
| FR-7.2 | `l2_distribution_comparison.png` | Histograms: equiv vs random L2 for NFN (and MLP placeholder) |
| FR-7.3 | `embedding_pca.png` | PCA 2D scatter colored by accuracy |
| FR-7.4 | `training_curves.png` | Loss + Spearman ρ over 150 epochs (train/val) |
| FR-7.5 | `sensitivity_by_decile.png` | NFN per-decile sensitivity bar chart |
| FR-7.6 | `nfn_vs_mlp_decile_comparison.png` | Grouped bar: NFN vs flat MLP per decile |

---

## 9. Key Findings

1. **Near-zero equivariance achieved**: `sensitivity_score = 7.34e-07 ≈ 0`, confirming NFN maps permutation-equivalent weights to virtually identical embeddings.

2. **885,000× improvement over flat MLP**: The NFN's equivariant inductive bias completely eliminates permutation sensitivity that flat MLP encoders exhibit (h-m1: 0.6490).

3. **Strong accuracy prediction**: `spearman_rho = 0.6806`, far exceeding the flat MLP baseline (0.1041) and confirming the encoder has learned meaningful accuracy-predictive features.

4. **Capacity budget respected**: `param_count = 521,953` within ±5% of 500K target (521,953 / 500,000 = 4.4% over budget, within [475K, 525K]).

5. **Robust across all deciles**: All 10 accuracy deciles show sensitivity scores in [1e-7, 2e-6], confirming equivariance holds uniformly regardless of model quality.

6. **Equivariance theoretical confirmation**: The near-zero `mean_equiv_L2 = 2.68e-08` vs `mean_random_L2 = 3.65e-02` demonstrates the encoder distinguishes different models while treating equivalent ones identically.

---

## 10. Comparison: H-M1 vs H-M2

| Metric | H-M1 (Flat MLP) | H-M2 (NFN) | Ratio |
|--------|-----------------|-------------|-------|
| sensitivity_score | 0.6490 | 7.34e-07 | 885,000× |
| spearman_rho | 0.1041 | 0.6806 | 6.5× |
| param_count | 500,577 | 521,953 | matched |
| Gate type | MUST_WORK | SHOULD_WORK | — |
| Gate result | PASS | PASS | — |

---

## 11. Conclusion

**H-M2 SHOULD_WORK gate: PASS**

The NFN equivariant encoder successfully demonstrates:
- Near-zero permutation sensitivity (equivariance by construction)
- Superior accuracy prediction (Spearman ρ = 0.6806 vs 0.1041 for flat MLP)
- Capacity-matched architecture (521,953 ≈ 500K params)

This validates the mechanism hypothesis: NFN encoders, by operating on the permutation-quotient weight space, achieve equivariance that flat MLPs cannot, freeing encoder capacity for accuracy-predictive features rather than navigating permutation orbits.

**Next step:** H-M3 — Controlled Δρ benchmark comparing NFN vs flat MLP Spearman correlation on MNIST-CNN and CIFAR-10 zoos.

---

## 12. Artifacts

| Artifact | Path |
|----------|------|
| Results JSON | `h-m2/code/results/h-m2_results.json` |
| Best encoder checkpoint | `h-m2/code/results/best_nfn_encoder.pt` |
| Figures | `h-m2/code/figures/` (6 PNG files) |
| Experiment log | `h-m2/code/experiment.log` |
| Config | `h-m2/code/config.py` |
| Models | `h-m2/code/models.py` |
| Data loader | `h-m2/code/data_loader.py` |
| Train | `h-m2/code/train.py` |
| Probe | `h-m2/code/probe.py` |
| Evaluate | `h-m2/code/evaluate.py` |
| Visualize | `h-m2/code/visualize.py` |
| Run experiment | `h-m2/code/run_experiment.py` |
