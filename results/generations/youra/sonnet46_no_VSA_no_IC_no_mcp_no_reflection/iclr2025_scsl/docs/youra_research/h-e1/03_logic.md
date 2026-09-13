---
hypothesis_id: h-e1
phase: 3
document_type: logic
generated: 2026-08-31
---

# Logic Design: H-E1
## Gradient Alignment Signal Existence Verification

Applied: per-sample-vmap-grad-pattern (vmap(grad(loss_fn)) scoped to last layer for memory efficiency)
Applied: batch-cosine-similarity-alignment (per-sample gradient cosine similarity with batch mean as spurious signal)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing codebase to analyze with Serena
**Analyzed Path**: N/A
**Findings**: All implementation primitives are external well-documented APIs: `torch.func.vmap`, `torch.func.grad`, `torch.func.functional_call`, `torch.nn.functional.cosine_similarity`, `sklearn.metrics.roc_auc_score`. No custom layers or complex inheritance to trace.

---

## System Overview

Four subtasks decompose Epic E3 (per-sample gradient probe, complexity 14). The core challenge is computing per-sample gradients over the full training set (N up to 162,770 for CelebA) without OOM — solved by scoping vmap to the last layer only (4,098 params vs ~25M for full ResNet-50). Alignment score is negated cosine similarity so that high score predicts spurious-minority membership (consistent with ROC-AUC convention where higher = more positive).

---

## Subtask L-E3-1: FC Parameter Extraction

### API Signature

```python
def _extract_fc_params(
    model: nn.Module
) -> tuple[dict[str, torch.Tensor], dict[str, torch.Tensor]]:
    """Extract last-layer (fc) parameters and all model buffers for vmap scope.

    Args:
        model: ResNet-50 with replaced fc layer (Linear(2048, n_classes)).

    Returns:
        fc_params: dict of fc parameter tensors keyed by full parameter name.
                   Example keys: {'fc.weight': Tensor(2, 2048), 'fc.bias': Tensor(2,)}
        all_buffers: dict of all model buffers (BatchNorm running stats etc.)
                     Required by functional_call even if not differentiating through them.

    Critical constraint:
        Only fc params are returned — passing all ~25M ResNet-50 params to vmap
        would require storing (batch_size × 25M) gradient tensors simultaneously → OOM.
        With fc only: 32 × 4098 × 4 bytes ≈ 512 KB — fits in 8GB GPU.
    """
```

### Implementation

```python
def _extract_fc_params(model):
    fc_params = {
        name: param.detach()
        for name, param in model.named_parameters()
        if name.startswith('fc.')
    }
    all_buffers = dict(model.named_buffers())
    return fc_params, all_buffers
```

### Notes
- Key pattern `'fc.'` matches ResNet-50 default last layer name. Verify with `[n for n,_ in model.named_parameters()]` if using custom model.
- `param.detach()` needed — vmap requires leaf tensors not attached to existing autograd graph.
- `all_buffers` passed to `functional_call` for BatchNorm correctness (running mean/var).

---

## Subtask L-E3-2: Per-Sample Loss Function

### API Signature

```python
def _per_sample_loss(
    fc_params: dict[str, torch.Tensor],
    all_buffers: dict[str, torch.Tensor],
    model: nn.Module,
    x: torch.Tensor,   # shape: (C, H, W) = (3, 224, 224) — single sample, NO batch dim
    y: torch.Tensor,   # shape: () — scalar long tensor
) -> torch.Tensor:     # shape: () — scalar loss
    """Cross-entropy loss for a single sample using functional_call to inject fc_params.

    Designed to be differentiated via grad() and vectorized via vmap().
    The backbone (all params except fc) remains frozen — functional_call merges
    fc_params into the model's parameter dict, overriding only fc.weight and fc.bias.

    Tensor shapes through forward pass:
        x:          (3, 224, 224)
        x_batch:    (1, 3, 224, 224)  ← unsqueeze for model forward
        logits:     (1, n_classes)
        y_batch:    (1,)              ← unsqueeze for cross_entropy
        loss:       ()                ← scalar
    """
```

### Implementation

```python
def _per_sample_loss(fc_params, all_buffers, model, x, y):
    x_batch = x.unsqueeze(0)          # (1, 3, 224, 224)
    y_batch = y.unsqueeze(0)          # (1,)

    # Merge fc_params into model's full parameter dict
    # functional_call creates a stateless forward pass — no in-place modification
    merged_params = {**dict(model.named_parameters()), **fc_params}
    logits = functional_call(model, (merged_params, all_buffers), (x_batch,))
    # logits: (1, n_classes)

    return F.cross_entropy(logits, y_batch)  # scalar
```

### Notes
- `functional_call` requires `model.eval()` before the probe pass (BatchNorm uses running stats, not batch stats in eval mode).
- The merge `{**dict(model.named_parameters()), **fc_params}` ensures backbone params are present but only fc params are differentiated (grad scope is set by what's passed to grad()).
- This function signature is designed for `grad(_per_sample_loss, argnums=0)` — differentiates w.r.t. `fc_params` (argnums=0).

---

## Subtask L-E3-3: Batched Probe Loop

### API Signature

```python
def compute_probe(
    model: nn.Module,
    loader: DataLoader,   # yields (x_batch, y_batch, group_id_batch)
    device: torch.device,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute per-sample alignment and loss scores over the full training set.

    Args:
        model: ResNet-50 in eval mode, at a checkpoint epoch.
        loader: DataLoader with batch_size=32, shuffle=False (eval order).
        device: cuda or cpu.

    Returns:
        alignment_scores: shape (N,), dtype float32
                          = -cosine_similarity(g_i, g_mean)
                          Negated: high score → low alignment → likely spurious-minority.
        loss_scores:      shape (N,), dtype float32
                          = per-sample cross-entropy loss (not negated).
        group_ids:        shape (N,), dtype int64
                          = group membership labels from DataLoader.

    Memory analysis (CelebA, N=162,770, B=32):
        Per batch: (32, 4098) floats × 4 bytes = 512 KB gradient tensor
        Batch-wise: safe. Full-N storage: 162,770 × 4098 × 4 bytes ≈ 2.5 GB → use lists.
    """
```

### Pseudo-code

```python
def compute_probe(model, loader, device):
    model.eval()
    fc_params, all_buffers = _extract_fc_params(model)

    # Move to device
    fc_params = {k: v.to(device) for k, v in fc_params.items()}
    all_buffers = {k: v.to(device) for k, v in all_buffers.items()}

    # Bind static args — vmap only vectorizes over x, y
    _loss_fn = partial(_per_sample_loss, all_buffers=all_buffers, model=model)
    _grad_fn = grad(_loss_fn, argnums=0)        # grad w.r.t. fc_params
    _vmap_grad = vmap(_grad_fn, in_dims=(None, 0, 0))  # vectorize over (x_batch, y_batch)

    all_alignments, all_losses, all_groups = [], [], []

    for x_batch, y_batch, group_batch in loader:
        # Tensor shapes:
        # x_batch:   (B, 3, 224, 224)
        # y_batch:   (B,) long
        # group_batch: (B,) long
        x_batch = x_batch.to(device)
        y_batch = y_batch.to(device)

        # Per-sample last-layer gradients
        # per_sample_grads: dict with same keys as fc_params
        #   'fc.weight': (B, n_classes, 2048)   ← grad of (n_classes, 2048) weight per sample
        #   'fc.bias':   (B, n_classes)
        per_sample_grads = _vmap_grad(fc_params, x_batch, y_batch)

        # Flatten to (B, D) where D = n_classes*2048 + n_classes = 4098 (for n_classes=2)
        g_flat = torch.cat([
            v.flatten(start_dim=1) for v in per_sample_grads.values()
        ], dim=1)   # (B, 4098)

        # Per-batch mean gradient
        # ponytail: per-batch mean approximates global mean; upgrade to two-pass
        # (accumulate all g_flat then mean) if alignment signal is noisy.
        g_mean = g_flat.mean(dim=0, keepdim=True)   # (1, 4098)

        # Cosine similarity: (B,)
        cos_sim = F.cosine_similarity(g_flat, g_mean.expand_as(g_flat), dim=1)

        # Negate: low alignment → high predictor score (spurious-minority convention)
        alignment = -cos_sim   # (B,)

        # Per-sample loss (no grad needed)
        with torch.no_grad():
            logits = model(x_batch)   # (B, n_classes)
            loss = F.cross_entropy(logits, y_batch, reduction='none')   # (B,)

        all_alignments.append(alignment.detach().cpu().numpy())
        all_losses.append(loss.cpu().numpy())
        all_groups.append(group_batch.numpy())

    return (
        np.concatenate(all_alignments),   # (N,)
        np.concatenate(all_losses),       # (N,)
        np.concatenate(all_groups),       # (N,)
    )
```

### Tensor Shape Summary

| Variable | Shape | Dtype | Notes |
|---|---|---|---|
| `x_batch` | (B, 3, 224, 224) | float32 | B=32 |
| `y_batch` | (B,) | int64 | class labels |
| `group_batch` | (B,) | int64 | group_DRO group id |
| `per_sample_grads['fc.weight']` | (B, 2, 2048) | float32 | n_classes=2 |
| `per_sample_grads['fc.bias']` | (B, 2) | float32 | |
| `g_flat` | (B, 4098) | float32 | 2×2048 + 2 = 4098 |
| `g_mean` | (1, 4098) | float32 | per-batch mean |
| `cos_sim` | (B,) | float32 | cosine similarity |
| `alignment` | (B,) | float32 | negated cos_sim |
| `loss` | (B,) | float32 | per-sample CE loss |

---

## Subtask L-E3-4: ROC-AUC Evaluation

### API Signature

```python
def evaluate_roc_auc(
    scores: np.ndarray,                    # shape (N,), predictor scores
    group_ids: np.ndarray,                 # shape (N,), int — group_DRO group index
    minority_group_ids: frozenset[int],    # {1, 2} for Waterbirds; {1} for CelebA
) -> float:
    """Compute binary ROC-AUC for spurious-minority prediction.

    Binary label construction:
        y_binary[i] = 1 if group_ids[i] in minority_group_ids else 0

    Args:
        scores: predictor scores (alignment_scores or loss_scores).
                Higher score should predict spurious-minority=1.
        group_ids: integer group labels from group_DRO ConfounderDataset.
        minority_group_ids: set of group indices considered spurious-minority.

    Returns:
        float: ROC-AUC score in [0, 1].

    Raises:
        ValueError: if minority count is 0 or equals N (degenerate case).

    Group encoding (group_DRO):
        Waterbirds:
            group_id = y * n_confounders + confounder_id
            y=0 (landbird), y=1 (waterbird); confounder: 0=land, 1=water
            → group 0: landbird+land (majority), group 1: landbird+water (minority)
            → group 2: waterbird+land (minority), group 3: waterbird+water (majority)
            minority_group_ids = frozenset({1, 2})

        CelebA:
            y=0 (non-blond), y=1 (blond); confounder: 0=female, 1=male
            → group 0: non-blond+female, group 1: non-blond+male
            → group 2: blond+female (majority blond), group 3: blond+male (minority)
            minority_group_ids = frozenset({3})   ← blond+male is the spurious-minority

    Note: CelebA minority is group 3 (blond+male), NOT group 1.
    Verify against group_DRO source before running.
    """
```

### Implementation

```python
def evaluate_roc_auc(scores, group_ids, minority_group_ids):
    y_binary = np.isin(group_ids, list(minority_group_ids)).astype(int)

    minority_count = y_binary.sum()
    if minority_count == 0 or minority_count == len(y_binary):
        raise ValueError(
            f"Degenerate binary labels: minority_count={minority_count}, N={len(y_binary)}. "
            f"Check minority_group_ids={minority_group_ids} against actual group_ids."
        )

    return roc_auc_score(y_binary, scores)
```

### Notes
- CelebA minority encoding: `blond_male = group 3` (y=1, confounder=1 → 1×2+1=3). Double-check with `group_dro/data/confounder_utils.py:get_group_idx()`.
- Waterbirds minority: `{1, 2}` — both cross-group classes (landbird+water, waterbird+land).
- `alignment_scores` passed directly (already negated in `compute_probe`) — higher alignment_score → more likely spurious-minority.
- `loss_scores` passed as-is — higher loss → more likely spurious-minority per JTT convention.

---

## Complete Tensor Shape Reference

| Stage | Tensor | Shape | Source |
|---|---|---|---|
| Input | x | (3, 224, 224) | DataLoader single sample |
| Input batch | x_batch | (B, 3, 224, 224) | DataLoader B=32 |
| FC weight grad | per_sample_grads['fc.weight'] | (B, 2, 2048) | vmap(grad()) output |
| FC bias grad | per_sample_grads['fc.bias'] | (B, 2) | vmap(grad()) output |
| Flattened grad | g_flat | (B, 4098) | flatten + cat |
| Batch mean grad | g_mean | (1, 4098) | g_flat.mean(0) |
| Cosine similarity | cos_sim | (B,) | F.cosine_similarity |
| Alignment score | alignment | (B,) | -cos_sim |
| Loss score | loss | (B,) | F.cross_entropy(..., reduction='none') |
| Full-dataset alignment | alignment_scores | (N,) | np.concatenate |
| Binary label | y_binary | (N,) | np.isin(group_ids, minority_ids) |
