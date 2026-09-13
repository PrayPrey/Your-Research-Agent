# Validation Report: h-m1

**Date:** 2026-08-31
**Hypothesis:** Under convergence-regime conditions, if generalization gap is predicted from weight tensors, then the prediction error is lower when the encoder computes globally distributed statistics compared to locally position-indexed statistics, because overfitting signal is spread across the full weight tensor — no single neuron or layer localizes it.
**Gate Type:** MUST_WORK
**Gate Result:** PASS

---

## Gate Condition

**Condition:** ≥1 equivariant encoder (DWSNet/NFT/GNN) achieves Spearman(gap) > FlatMLP Spearman(gap)

**Outcome:** ✅ PASS — NFT Spearman(gap) = 0.5752 > FlatMLP = 0.5330

---

## Key Results

| Encoder | Type | Spearman r | 95% CI | vs FlatMLP |
|---------|------|-----------|--------|------------|
| FlatMLP | position-indexed | 0.5330 | [0.4850, 0.5801] | baseline |
| DWSNet | equivariant | 0.4881 | [0.4377, 0.5325] | −0.0449 |
| **NFT** | **equivariant** | **0.5752** | **[0.5339, 0.6158]** | **+0.0422 ✅** |
| GNN | equivariant | 0.3747 | [0.3180, 0.4265] | −0.1583 |

- **Best equivariant encoder:** NFT (r=0.5752)
- **Δ_gap (mean equivariant − FlatMLP):** −0.0773 (mean is pulled down by GNN)
- **Gate-satisfying comparison:** NFT vs FlatMLP, Δ = +0.0422

---

## Experiment Details

- **Dataset:** Unterthiner CIFAR-10 CNN zoo, N=10,000, D=33,890
- **Split:** 80/10/10 (train/val/test), seed=42 — same as H-E1
- **Test set:** N=1,000 models
- **Training protocol:** 3-trial random search per encoder, best by val Spearman
- **Bootstrap CI:** N=1,000 resamples, 95% percentile CI

---

## Findings

1. **NFT (Neural Functional Transformer) exceeds FlatMLP** on gap prediction: r=0.5752 vs 0.5330. The cross-layer attention mechanism generalizes better than position-indexed features on this target.

2. **DWSNet underperforms FlatMLP** (r=0.4881 < 0.5330). Row+column equivariance alone is insufficient for gap prediction; within-layer permutation invariance does not help when the signal is cross-layer.

3. **GNN substantially underperforms** (r=0.3747). The graph structure may impose too strong an inductive bias, reducing capacity for the regression task.

4. **Mean equivariant Δ_gap = −0.0773** — negative overall, but gate criterion requires only ≥1 encoder to beat FlatMLP, which NFT satisfies.

5. **FlatMLP re-run val_r=0.5400 vs H-E1 val_r=0.5436**: small variance between runs (different trial seeds) — within expected noise. Test_r=0.5330 in this run vs 0.5567 in H-E1 reflects run-to-run variance with 3-trial search.

---

## Mechanism Interpretation

NFT's cross-layer attention architecture captures inter-layer co-variation signals that are distributed across the full weight tensor. This supports the hypothesis that overfitting signal is globally distributed — at least partially. However, the result is not universal across equivariant architectures (DWSNet and GNN do not benefit), suggesting the specific form of equivariance matters.

---

## Figures

- `figures/fig1_bar.png` — Spearman r per encoder vs FlatMLP baseline
- `figures/fig2_scatter.png` — Predicted vs true gap (2×2 scatter grid)
- `figures/fig3_delta.png` — Δ_gap per equivariant encoder
- `figures/fig4_gap_dist.png` — Test split gap distribution

---

## Conclusion

**Gate: PASS.** NFT achieves Spearman(gap)=0.5752 > FlatMLP=0.5330, satisfying the MUST_WORK criterion. The hypothesis receives directional support: at least one equivariant encoder (NFT with cross-layer attention) outperforms the position-indexed baseline on gap prediction, consistent with the mechanism claim that gap signal is globally distributed across weight tensors.
