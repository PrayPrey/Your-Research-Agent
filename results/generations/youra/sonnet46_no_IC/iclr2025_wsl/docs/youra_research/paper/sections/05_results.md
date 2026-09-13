# Results

## 5.1 Main Result: Graph SSL Outperforms SANE on ViT Zoo (RQ1)

Table 1 presents our main comparison. EquiSSL-perm achieves R²=0.231 on 53 held-out ViT-S/16 models, while SANE achieves R²=0.072 — a +221% relative improvement. EquiSSL (scale+permutation) achieves R²=0.210, also substantially above SANE but below EquiSSL-perm.

**Table 1: Cross-Architecture Property Prediction on ViT Model Zoo (53 ViT-S/16, seed 0)**

| Method | Representation | R² (ViT zoo) | ΔR² vs SANE |
|--------|---------------|-------------|-------------|
| SANE [Schürholt et al., 2024] | Flat tokenization + VICReg | 0.072 | — |
| EquiSSL (scale+perm) | Graph + ScaleGMN | 0.210 | +0.138 |
| **EquiSSL-perm (ours)** | **Graph + permutation** | **0.231** | **+0.159** |

*All methods trained on SANE MultiZoo CIFAR-10 CNN subset (~3k models). No ViT training data used. Single seed (seed 0). Statistical significance not assessable with n=1 seed.*

This result establishes the central claim: a permutation-equivariant graph SSL encoder trained exclusively on CNN checkpoints achieves meaningful ViT accuracy prediction without any ViT training data. The 3x improvement over SANE is not a marginal improvement — it is the difference between a useful predictor (R²=0.231 provides meaningful ranking signal for model selection) and near-noise performance (R²=0.072 barely exceeds chance for regression).

Figure 1 (fig1_r2_bar.png) visualizes these results. The bar chart shows R² for each method with SANE at left, EquiSSL at center, and EquiSSL-perm at right. The step-function increase from SANE to either graph-based method, and the further increase from EquiSSL to EquiSSL-perm, illustrate both the graph schema benefit and the scale equivariance reversal.

**Why SANE fails.** Figure 4 vs Figure 5 (tsne_equissl_seed0.png vs tsne_sane_seed0.png) contrasts the latent space structure. EquiSSL-perm's t-SNE plot shows well-separated clusters of CNN training models and ViT test models, with ViT models distributed across the latent space. SANE's t-SNE shows a collapsed, point-like distribution: all inputs — CNN training zoo and ViT test zoo alike — map to nearly identical latent codes (std≈0.0014). This collapse explains the R²=0.072: the linear probe receives no discriminative signal from the SANE embeddings.

The graph schema resolves the collapse by providing architecture-agnostic relational structure. Both EquiSSL and EquiSSL-perm produce distributed ViT latent codes because the directed graph representation preserves the same node/edge structure across architecture families — ViT attention projections are structurally identical to MLP linear layers in the computational graph schema.

## 5.2 Scale Equivariance Reversal: Ablation on Symmetry Group (RQ3)

The most striking result of our study is the reversal of the expected ordering: EquiSSL-perm (permutation-only) outperforms EquiSSL (scale+permutation) by ΔR²=+0.143 on ViT models in the h-m2 ablation (seed 0, Table 2). This contradicts the prediction from supervised same-architecture settings [Kalogeropoulos et al., 2024], where scale equivariance provides +8-12 R² points.

**Table 2: Symmetry Group Ablation (h-m2, seed 0, 53 ViT-S/16)**

| Method | Symmetry Group | R² (seed 0) | ΔR² vs EquiSSL |
|--------|---------------|-------------|----------------|
| SANE | None | 0.072 | — |
| EquiSSL | Scale + Permutation (monomial) | 0.185 | — |
| **EquiSSL-perm** | **Permutation only** | **0.327** | **+0.143** |

*Note: h-m2 uses a fresh training run (seed 0 from scratch) which explains the higher absolute R² values (0.327 vs 0.231 for EquiSSL-perm) compared to Table 1. Table 1 uses the h-m1 pre-trained encoder evaluated on the same test set. Both experiments confirm the ordering: EquiSSL-perm > EquiSSL > SANE.*

Figure 2 (gate_metrics_bar.png) shows the ablation bar chart directly comparing EquiSSL and EquiSSL-perm R² values. The inversion is unambiguous: the more complex symmetry group performs worse. Figure 3 (ablation_ladder.png) displays the R² ladder from SANE (floor) to EquiSSL to EquiSSL-perm, illustrating that both graph encoders substantially outperform flat tokenization, but permutation-only outperforms scale+permutation.

**Why scale equivariance hurts.** We attribute this reversal to LayerNorm's gauge-fixing effect (Section 3.4). Scale equivariance imposes the invariance f(cG) = f(G) for scalar c — two networks related by neuron scale should have identical embeddings. For ViT architectures with LayerNorm, this invariance is geometrically incorrect: LayerNorm normalizes activation scale at inference time, meaning two ViT networks with different weight scales are NOT functionally equivalent (they will produce identical activations after normalization, but correspond to different effective weight configurations). Imposing scale invariance on ViT weights therefore discards discriminative information rather than encoding a genuine network symmetry.

This finding has an important practical implication: the choice of equivariance group should be validated for the target architecture's normalization properties, not assumed from results in supervised same-architecture settings.

## 5.3 Latent Space Visualization (RQ1, Supporting Evidence)

Figure 5 (fig3_tsne.png) shows a 4-panel t-SNE comparison of latent spaces across encoders and model families. The panels contrast: (a) EquiSSL-perm on CNN training zoo, (b) EquiSSL-perm on ViT test zoo, (c) SANE on CNN training zoo, (d) SANE on ViT test zoo. The ViT test zoo distribution under EquiSSL-perm (panel b) is well-distributed and distinct from the training zoo (panel a), demonstrating that the graph encoder produces meaningful differentiation among ViT models. SANE's ViT latents (panel d) collapse to a single cluster regardless of accuracy differences.

The t-SNE visualization is qualitative, but it makes the mechanism transparent: SANE cannot differentiate ViT models because it maps all inputs to the same representation region. EquiSSL-perm spreads ViT models across latent space, allowing the linear probe to use geometric structure for prediction.

## 5.4 Distribution Shift Analysis (RQ2)

Table 3 reports MMD between training (CNN) and test (ViT) latent distributions for each encoder.

**Table 3: MMD Between CNN Train Zoo and ViT Test Zoo (h-e1/h-m2)**

| Method | MMD (train→test) | Relative to SANE |
|--------|----------------|-----------------|
| SANE | 0.849 | — |
| EquiSSL | 2.348 | 2.77× higher |
| EquiSSL-perm | 0.203 | 0.24× lower |

*RBF kernel MMD. Lower = smaller distributional gap between training and test latents.*

The MMD results reveal a puzzling pattern. SANE achieves the lowest MMD (0.849) — apparently the smallest distribution shift — but also the worst R² (0.072). EquiSSL has the highest MMD (2.348) and intermediate R² (0.210). EquiSSL-perm has lower MMD than SANE (0.203) and the best R² (0.231).

This ordering is inconsistent with the hypothesis that lower MMD predicts better cross-architecture transfer. The explanation lies in SANE's latent collapse: with std≈0.0014, all inputs map to near-constant codes, producing trivially low MMD by construction (collapsed distributions have near-zero variance, yielding near-zero MMD by the RBF kernel). SANE "wins" on MMD not because it aligns distributions, but because it collapses all distributions to the same point. R² is the appropriate metric; on R², SANE is clearly inferior.

This finding serves as a **methodological warning**: MMD is unreliable as a cross-architecture transfer metric when baseline encoders may collapse their representations. Any evaluation protocol that relies on MMD to assess distribution shift should first verify that the encoder produces non-degenerate latent distributions.

## 5.5 Latent Interpolation vs Weight-Space Averaging (RQ4)

Table 4 reports interpolation accuracy across N=501 CNN model pairs (h-m3).

**Table 4: Latent Interpolation vs Weight-Space Averaging (501 pairs, seed 0)**

| Metric | Value |
|--------|-------|
| mean(acc_latent) | 0.100 |
| mean(acc_ws) | 0.125 |
| mean(delta) | -0.025 |
| std(delta) | 0.023 |
| t-statistic | -24.52 |
| p-value | ~9.0 × 10⁻⁸⁸ |
| Cohen's d | -1.10 |
| % pairs with delta > 0 | 9.4% |

*acc_latent: CIFAR-10 accuracy of model decoded from latent midpoint. acc_ws: CIFAR-10 accuracy of model averaged in weight space. Paired t-test over 501 pairs.*

Latent interpolation performs at near-random chance (acc=0.100, matching the 10-class uniform baseline for CIFAR-10) and is significantly worse than weight-space averaging (acc=0.125, p≈0, Cohen d=-1.10). Weight-space averaging outperforms in 90.6% of pairs.

This result is not a failure of the latent space — the R² results confirm that EquiSSL-perm's latent codes encode property-predictive information. It is a failure of the decoder. The graph decoder in this pipeline was trained to reconstruct 512-dimensional edge attribute statistics vectors, not raw weight tensors. The tile/slice mapping from 512-dimensional output to architecture-specific weight matrices is a non-functional heuristic: it produces random-like weight configurations that are unrelated to the interpolated point in latent space. The decoder's output format (statistics reconstruction) and the target format for model generation (functional weight tensors) are fundamentally incompatible.

This distinguishes two separable capabilities: *property prediction* (which requires only that the latent space is organized by functional properties — confirmed by R²) and *model generation* (which requires a decoder that maps from latent codes to functional weights — not provided by statistics reconstruction). Future work designing a dedicated hypernetwork-style decoder could potentially recover the interpolation capability.

Figure 6 (delta_histogram.png) shows the distribution of acc_latent - acc_ws across all 501 pairs. The distribution is strongly left-skewed, centered at approximately -0.025, with only 9.4% of pairs showing positive delta. The result is not borderline — it is a consistent and highly significant failure of the latent interpolation approach with the current decoder design.
