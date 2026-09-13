# Logic Design: h-m-integrated
## Hierarchical VAE for Cross-Architecture Model Zoo Analysis

**Hypothesis ID:** h-m-integrated  
**Type:** MECHANISM  
**Date:** 2026-08-20

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New API design - no existing code to analyze  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - new implementation

---

## Knowledge Base Patterns Applied

**Applied:** Standard PyTorch VAE + DeepSets aggregation (phi/rho) + CLIP-style contrastive learning

---

## A-1: NFN Encoder [Complexity: 3, Budget: 5 subtasks]

### API Signatures

```python
class NFNEncoder(nn.Module):
    def __init__(self, weight_dim: int, hidden_dim: int = 256, latent_dim: int = 512):
        """Permutation-equivariant encoder for neural network weights."""
        ...

    def forward(self, weights: Tensor) -> Tensor:
        """
        DeepSets aggregation: phi per-neuron, rho global.
        weights: [batch, num_neurons, neuron_dim] -> [batch, latent_dim]
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| weights | [B, N, D] | Input neuron embeddings (N varies by architecture) |
| phi_out | [B, N, H] | Per-neuron transform (H=256) |
| pooled | [B, H] | Mean over neurons (permutation-invariant) |
| out | [B, L] | Final representation (L=512) |

### Pseudo-code

```
1. phi_out = phi_network(weights)        # [B, N, D] -> [B, N, H]
2. pooled = mean(phi_out, dim=1)         # [B, N, H] -> [B, H]
3. out = rho_network(pooled)             # [B, H] -> [B, L]
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | phi_network | 2-layer MLP (weight_dim -> hidden_dim) |
| L-1-2 | rho_network | 2-layer MLP (hidden_dim -> latent_dim) |
| L-1-3 | forward | DeepSets aggregation |
| L-1-4 | variable_length_support | Handle different neuron counts (CNN vs ResNet) |
| L-1-5 | normalization | LayerNorm after phi |

---

## A-2: Hierarchical Pooling [Complexity: 2, Budget: 3 subtasks]

### API Signatures

```python
class HierarchicalPooling(nn.Module):
    def __init__(self, input_dim: int = 512, output_dim: int = 512):
        """Layer-wise mean pooling with MLP projection."""
        ...

    def forward(self, neuron_embeddings: Tensor) -> Tensor:
        """
        Aggregate per-layer summaries.
        neuron_embeddings: [B, N, D] -> [B, D]
        """
        ...
```

### Pseudo-code

```
1. layer_summary = mean(neuron_embeddings, dim=1)  # [B, N, D] -> [B, D]
2. out = linear(layer_summary)                     # [B, D] -> [B, D]
3. out = LayerNorm(out)                            # [B, D]
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | layer_pool | Mean pooling over neurons |
| L-2-2 | mlp_projection | Linear + LayerNorm |
| L-2-3 | forward | Combined pooling pipeline |

---

## A-3: Transformer Relational Modeling [Complexity: 4, Budget: 6 subtasks]

### API Signatures

```python
class TransformerRelational(nn.Module):
    def __init__(self, latent_dim: int = 512, num_heads: int = 8, num_layers: int = 6):
        """Transformer encoder with architecture token and CLS token."""
        ...

    def forward(self, layer_summaries: Tensor) -> Tuple[Tensor, Tensor]:
        """
        Self-attention over layer summaries + arch token.
        layer_summaries: [B, L, D] -> mu [B, D], logvar [B, D]
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| layer_summaries | [B, L, D] | Input layer embeddings (L varies) |
| arch_token | [B, 1, D] | Learnable architecture-type token |
| seq | [B, L+1, D] | Concatenated sequence |
| attn_out | [B, L+1, D] | After 6-layer Transformer |
| cls_token | [B, D] | Extract first token (CLS) |
| mu | [B, D] | VAE mean |
| logvar | [B, D] | VAE log-variance |

### Pseudo-code

```
1. arch_token = learnable_param.expand(B, 1, D)
2. seq = concat([arch_token, layer_summaries], dim=1)  # [B, L+1, D]
3. attn_out = transformer_encoder(seq)                 # [B, L+1, D]
4. cls_token = attn_out[:, 0, :]                       # [B, D]
5. mu = linear_mu(cls_token)                           # [B, D]
6. logvar = linear_logvar(cls_token)                   # [B, D]
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | arch_token | Learnable parameter initialization |
| L-3-2 | transformer_encoder | 6-layer TransformerEncoder (PyTorch) |
| L-3-3 | mu_head | Linear projection to mean |
| L-3-4 | logvar_head | Linear projection to log-variance |
| L-3-5 | forward | Full pipeline with CLS token extraction |
| L-3-6 | variable_sequence | Handle variable layer counts |

---

## A-4: Hierarchical VAE [Complexity: 5, Budget: 8 subtasks]

### API Signatures

```python
class HierarchicalVAE(nn.Module):
    def __init__(self, latent_dim: int = 512):
        """3-level VAE with architecture-specific encoders."""
        ...

    def encode(self, weights: Tensor, arch_type: str) -> Tuple[Tensor, Tensor]:
        """
        Encode weights to latent distribution.
        weights: [B, N, D] -> mu [B, L], logvar [B, L]
        """
        ...

    def reparameterize(self, mu: Tensor, logvar: Tensor) -> Tensor:
        """
        Sample latent via reparameterization trick.
        mu: [B, L], logvar: [B, L] -> z: [B, L]
        """
        ...

    def decode(self, z: Tensor) -> Tensor:
        """
        Decode latent to reconstructed weights.
        z: [B, L] -> recon: [B, W]
        """
        ...
```

### Pseudo-code

```
# Encode
1. encoder = nfn_encoders[arch_type]
2. neuron_emb = encoder(weights)              # [B, N, D] -> [B, L]
3. layer_summary = pooling(neuron_emb)        # [B, L] -> [B, L]
4. mu, logvar = transformer(layer_summary)    # [B, L] -> [B, L], [B, L]

# Reparameterize
5. std = exp(0.5 * logvar)
6. eps = randn_like(std)
7. z = mu + eps * std                         # [B, L]

# Decode
8. recon = decoder_mlp(z)                     # [B, L] -> [B, W]
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | nfn_encoders | ModuleDict with 4 architecture-specific NFN encoders |
| L-4-2 | pooling | HierarchicalPooling instance |
| L-4-3 | transformer | TransformerRelational instance |
| L-4-4 | decoder | Shared MLP decoder (latent_dim -> weight_dim) |
| L-4-5 | encode | Level 1-3 pipeline |
| L-4-6 | reparameterize | Standard VAE sampling |
| L-4-7 | decode | Latent to reconstruction |
| L-4-8 | forward | Complete encode-decode cycle |

---

## A-5: Multi-Objective Loss [Complexity: 4, Budget: 7 subtasks]

### API Signatures

```python
def compute_vae_loss(
    recon: Tensor,
    target: Tensor,
    mu: Tensor,
    logvar: Tensor,
    beta: float = 1.0
) -> Tuple[Tensor, Tensor, Tensor]:
    """
    Compute reconstruction + KL loss.
    Returns: total_loss, recon_loss, kl_loss
    """
    ...

def contrastive_triplet_loss(
    anchor: Tensor,
    positive: Tensor,
    negative: Tensor,
    margin: float = 0.3
) -> Tensor:
    """
    Triplet margin loss: d(a, p) < d(a, n) - margin
    anchor: [B, D], positive: [B, D], negative: [B, D] -> loss: scalar
    """
    ...

def sample_triplet(
    batch: Dict[str, Tensor],
    task_labels: Tensor,
    arch_labels: Tensor
) -> Tuple[Tensor, Tensor, Tensor]:
    """
    Sample anchor/positive/negative from batch.
    Returns: anchor_idx, positive_idx, negative_idx
    """
    ...
```

### Pseudo-code

```
# VAE Loss
1. recon_loss = mse_loss(recon, target)
2. kl_loss = -0.5 * sum(1 + logvar - mu^2 - exp(logvar))
3. total_loss = recon_loss + beta * kl_loss

# Contrastive Loss
4. pos_dist = norm(anchor - positive, dim=1)      # [B]
5. neg_dist = norm(anchor - negative, dim=1)      # [B]
6. loss = relu(pos_dist - neg_dist + margin)      # [B]
7. loss = mean(loss)

# Triplet Sampling
8. anchor_idx = random sample from batch
9. positive_idx = same task, different architecture
10. negative_idx = different task
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | reconstruction_loss | MSE between recon and target |
| L-5-2 | kl_divergence | Standard VAE KL term |
| L-5-3 | triplet_loss | Margin-based contrastive loss |
| L-5-4 | task_classification | Cross-entropy for task labels (auxiliary) |
| L-5-5 | sample_triplet | In-batch triplet mining |
| L-5-6 | beta_annealing | Linear schedule (1.0 -> 0.1) |
| L-5-7 | total_loss | Weighted sum of all components |

---

## A-6: CKA Computation [Complexity: 3, Budget: 4 subtasks]

### API Signatures

```python
def linear_cka(X: Tensor, Y: Tensor) -> Tensor:
    """
    Centered Kernel Alignment (linear kernel).
    X: [N, F1], Y: [N, F2] -> cka: scalar [0, 1]
    """
    ...

def compute_cka_matrix(embeddings: List[Tensor]) -> Tensor:
    """
    Pairwise CKA for all embedding pairs.
    embeddings: list of [N, F] -> cka_matrix: [M, M]
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| X, Y | [N, F] | Input representations |
| K | [N, N] | Gram matrix X @ X.T |
| L | [N, N] | Gram matrix Y @ Y.T |
| H | [N, N] | Centering matrix (I - 1/N) |
| K_c | [N, N] | Centered Gram K_c = H @ K @ H |
| L_c | [N, N] | Centered Gram L_c = H @ L @ L |
| cka | scalar | Final similarity score |

### Pseudo-code

```
1. K = X @ X.T                                # [N, N]
2. L = Y @ Y.T                                # [N, N]
3. H = eye(N) - ones(N, N) / N                # [N, N]
4. K_c = H @ K @ H                            # [N, N]
5. L_c = H @ L @ H                            # [N, N]
6. hsic_kl = trace(K_c @ L_c) / (N - 1)^2
7. hsic_kk = trace(K_c @ K_c) / (N - 1)^2
8. hsic_ll = trace(L_c @ L_c) / (N - 1)^2
9. cka = hsic_kl / sqrt(hsic_kk * hsic_ll)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | gram_matrix | K = X @ X.T |
| L-6-2 | centering | H @ K @ H operation |
| L-6-3 | hsic | Hilbert-Schmidt Independence Criterion |
| L-6-4 | cka | Final CKA computation |

---

## A-7: WCSS Bootstrap Test [Complexity: 3, Budget: 5 subtasks]

### API Signatures

```python
def compute_wcss(embeddings: Tensor, labels: Tensor) -> Tensor:
    """
    Within-cluster sum of squares.
    embeddings: [N, D], labels: [N] -> wcss: scalar
    """
    ...

def wcss_bootstrap(
    embeddings: Tensor,
    labels: Tensor,
    n_resamples: int = 100
) -> Dict[str, float]:
    """
    Bootstrap resampling for WCSS significance test.
    Returns: {mean_same_task, mean_diff_task, p_value, cohen_d}
    """
    ...
```

### Pseudo-code

```
# WCSS Computation
1. wcss = 0
2. for each unique label k:
3.     cluster_mask = (labels == k)
4.     cluster_emb = embeddings[cluster_mask]     # [N_k, D]
5.     centroid = mean(cluster_emb, dim=0)        # [D]
6.     wcss += sum((cluster_emb - centroid)^2)
7. return wcss

# Bootstrap Test
8. same_task_wcss = []
9. diff_task_wcss = []
10. for i in range(n_resamples):
11.     idx = randint(0, N, size=N)               # resample with replacement
12.     emb_sample = embeddings[idx]
13.     label_sample = labels[idx]
14.     same_wcss = compute_wcss(emb_sample, label_sample)
15.     random_labels = randperm(label_sample)
16.     diff_wcss = compute_wcss(emb_sample, random_labels)
17.     same_task_wcss.append(same_wcss)
18.     diff_task_wcss.append(diff_wcss)
19. p_value = ttest_ind(same_task_wcss, diff_task_wcss)
20. cohen_d = (mean(same) - mean(diff)) / pooled_std
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | compute_wcss | Per-cluster sum of squares |
| L-7-2 | bootstrap_resample | Random sampling with replacement |
| L-7-3 | statistical_test | t-test + Cohen's d |
| L-7-4 | wcss_bootstrap | Full bootstrap pipeline |
| L-7-5 | random_baseline | Different-task WCSS via label permutation |

---

## Edge Cases and Validation

### Variable Neuron Counts

**Problem:** CNN-small (10K neurons) vs ResNet-34 (200K neurons)  
**Solution:** DeepSets aggregation (mean pooling) handles variable N  
**Implementation:** No padding required, pooling operates on dim=1

### Missing Architecture Types

**Problem:** Encoder called with unknown arch_type  
**Solution:** 
```python
if arch_type not in self.nfn_encoders:
    raise ValueError(f"Unknown architecture: {arch_type}")
```

### Variable Layer Counts

**Problem:** ResNet-18 (18 layers) vs ResNet-34 (34 layers)  
**Solution:** Transformer handles variable sequence length (L varies)  
**Implementation:** No positional encoding required for layer-agnostic attention

### CKA Numerical Stability

**Problem:** Small eigenvalues in Gram matrices  
**Solution:** Add regularization to diagonal
```python
K = K + eps * eye(N)  # eps = 1e-6
```

### WCSS Bootstrap Sample Size

**Problem:** Small clusters (N_k < 10) unstable  
**Solution:** Filter out clusters with N_k < 30 (PRD coverage threshold)

### Gradient Clipping

**Problem:** Exploding gradients in Transformer  
**Solution:** `clip_grad_norm_(parameters, max_norm=1.0)` in training loop

---

## Complexity Analysis

### NFN Encoder
- **Time:** O(N * D * H) for phi, O(H * L) for rho  
- **Space:** O(N * H) intermediate activations  
- **Dominant:** phi network (per-neuron MLP)

### Hierarchical Pooling
- **Time:** O(N * D) for mean, O(D * D) for MLP  
- **Space:** O(B * D)  
- **Dominant:** Mean reduction over N neurons

### Transformer
- **Time:** O(L^2 * D) per layer (6 layers)  
- **Space:** O(L^2) attention maps  
- **Dominant:** Self-attention computation

### CKA
- **Time:** O(N^2 * F) for Gram matrices, O(N^3) for centering  
- **Space:** O(N^2) for K, L matrices  
- **Dominant:** Matrix multiplication

### WCSS Bootstrap
- **Time:** O(R * K * N * D) where R=100 resamples, K=9 tasks  
- **Space:** O(R) for WCSS values  
- **Dominant:** Centroid computation (R * K iterations)

---

## Implementation Notes

1. **NFN Reference:** Use DeepSets phi/rho pattern, skip permutation-specific layers from full NFN paper
2. **Transformer:** Use `nn.TransformerEncoder` directly, no custom attention needed
3. **CKA:** Follow pytorch-cka reference for centering matrix computation
4. **Triplet Sampling:** In-batch hard negative mining (largest d(a, n) among negatives)
5. **Beta Annealing:** Linear schedule `beta = 1.0 - 0.9 * (epoch / 200)`

---

**Document Version:** 1.0  
**Last Updated:** 2026-08-20  
**Total Subtasks:** 38/38 allocated
