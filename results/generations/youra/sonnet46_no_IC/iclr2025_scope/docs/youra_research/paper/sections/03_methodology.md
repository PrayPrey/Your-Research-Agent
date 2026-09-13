# 3. Methodology

Our approach rests on three components: (1) erank computation from pretrained weights, (2) the PARA oracle that defines ground-truth optimal rank per layer, and (3) the statistical test linking them.

## 3.1 Effective Rank of Pretrained Weight Matrices

Building on our key insight that pretrained weight geometry encodes layer-complexity structure, we use the effective rank of Roy and Vetterli [2007] as the structural predictor.

**Definition.** For a weight matrix $W_0 \in \mathbb{R}^{d_{\text{out}} \times d_{\text{in}}}$ with singular values $\sigma_1 \geq \sigma_2 \geq \cdots \geq \sigma_k > 0$ (where $k = \min(d_{\text{out}}, d_{\text{in}})$), the effective rank is:
$$\text{erank}(W_0) = \exp\!\left(-\sum_{i=1}^{k} p_i \log p_i\right), \quad p_i = \frac{\sigma_i}{\sum_j \sigma_j}$$

This is the exponential of the Shannon entropy of the normalized singular value distribution.

**Why erank, not spectral entropy or stable rank?** Spectral entropy $H(\sigma/\|\sigma\|_1)$ is the log of erank, lacking the natural scale $[1, \text{rank}(W_0)]$. Stable rank $\|W\|_F^2 / \|W\|_2^2$ is dominated by the largest singular value and insensitive to the distribution of smaller values. erank is normalized (depending only on ratios $\sigma_i/\sigma_j$), bounded between 1 (rank-1 matrix) and $\text{rank}(W_0)$ (identity), and captures the full distributional shape of the singular spectrum. In our preliminary experiments with the prior spectral entropy metric, we observed a ceiling effect (low CV across layers); erank's exponential transformation amplifies differences between layers, providing the dynamic range necessary for correlation analysis.

**Implementation.** We compute erank in fp32 precision for all weight matrices with $\geq 2$ dimensions and at most $d_{\text{out}} \times d_{\text{in}} < 50\text{M}$ entries (to exclude embedding tables). The computation uses full SVD (not truncated), since erank requires the complete singular value distribution:

```python
def compute_erank(W: torch.Tensor, eps: float = 1e-10) -> float:
    S = torch.linalg.svdvals(W.float())  # fp32 cast
    S = S[S > eps]                        # numerical stability
    p = S / S.sum()
    entropy = -(p * torch.log(p)).sum()
    return entropy.exp().item()
```

Figure 2 shows the erank heatmap for BERT-base-uncased. FFN intermediate/output matrices (erank $\sim 705$–$726$) consistently exceed attention Q/K/V/O matrices (erank $\sim 530$–$610$), reflecting the richer representational diversity these layers develop during pretraining.

## 3.2 PARA Oracle: Ground-Truth Per-Layer Rank

To define what the optimal LoRA rank is for each layer, we use the Per-layer Adaptive Rank Allocation (PARA) oracle — a marginal search protocol that isolates each layer's rank contribution.

**Protocol.** For each target layer $l$ in model $\mathcal{M}$:
1. Freeze all LoRA adapters at baseline rank $r_{\text{base}} = 8$.
2. Sweep layer $l$'s rank over $\mathcal{R} = \{4, 8, 16, 32, 64\}$, training each configuration independently from the same initialization.
3. Evaluate validation accuracy for each rank.
4. Assign oracle rank $r_l^* = \arg\max_{r \in \mathcal{R}} \text{val\_acc}(r)$.

**Why marginal, not joint?** Jointly optimizing all layer ranks simultaneously is computationally infeasible ($|\mathcal{R}|^{n_{\text{layers}}}$ combinations). The marginal oracle is a well-established proxy [Zhang et al., 2023; Tripathi et al., 2026] and is the appropriate experimental target for testing whether erank predicts per-layer rank need independently.

**Implementation.** We use the HuggingFace PEFT library [Mangrulkar et al., 2022] with `LoraConfig` per-rank instantiation. Each oracle sweep trains a separate adapter with the target layer's rank varied while all other layers remain at $r=8$. Training follows standard GLUE fine-tuning protocols (Section 4.2).

## 3.3 Statistical Test Design

**Primary test (P1).** Pearson correlation $r(\text{erank}(W_0), r_l^*)$ over all layers $l$ in a model family. We use a one-tailed test ($H_1: r > 0$) at $\alpha = 0.05$, pre-registered threshold $r \geq 0.65$. Bootstrap 95% confidence intervals are computed via 1000 resamples with replacement over layers.

**Metric agreement test (P5).** Pearson correlation between $\text{erank}(W_0)$ and participation ratio $\text{PR}(W_0) = (\sum \sigma_i)^2 / \sum \sigma_i^2$ in layer ranking. Pre-registered threshold: Pearson $\rho \geq 0.8$.

**Gate criterion.** The primary hypothesis (H-E1) passes if $r \geq 0.65$ with $p < 0.05$ in $\geq 2/3$ evaluated model families.

## 3.4 Models and Target Layers

We evaluate three pretrained transformer families:

| Model | Architecture | Adapted Layers | $n_{\text{layers}}$ |
|-------|-------------|----------------|---------------------|
| BERT-base-uncased | Encoder, 12 layers | Q, K, V, O, FFN-int, FFN-out | 72 |
| DeBERTa-v3-base | Encoder, 12 layers (disentangled attn) | Q-proj, K-proj, V-proj, O, FFN-int, FFN-out | 72 |
| ViT-base-patch16-224 | Vision encoder, 12 layers | Q, K, V, O, FFN-int, FFN-out | 73 |

For each family, erank is computed for all target weight matrices. Oracle rank sweeps were completed for 5 of 72 BERT-base-uncased layers in the current experimental run (see Section 5 for details and discussion of compute constraints).
