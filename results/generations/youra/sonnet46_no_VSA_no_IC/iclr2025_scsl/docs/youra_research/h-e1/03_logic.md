# Logic Design: H-E1 — Sharpness Anisotropy in SSL Loss Landscapes

**Hypothesis:** H-E1 (EXISTENCE)
**Phase:** 3 — Implementation Planning
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr

---

## Codebase Analysis (Serena)

Green-field project — no existing codebase to analyze. Serena MCP skipped per workflow rules for green-field hypotheses. All API designs derive from:
- davda54/sam (SAM optimizer, 60-line implementation)
- izmailovpavel/spurious_feature_learning (SSL pretraining pipeline)
- kohpangwei/group_DRO (dataset loaders, WGA evaluation)
- facebookresearch/moco, facebookresearch/dino

**Applied:** Standard DL Experiment Pattern (modular trainer → probe → measurement → analysis pipeline)

---

## Overview

This document specifies API signatures, tensor shapes, and pseudo-code for all high-complexity modules in H-E1. The core flow is:

```
SSL Pre-train (SGD) → Save Checkpoints → Load Checkpoint → Train Linear Probe
  → Compute Per-Sample Losses → Identify Spurious Direction Proxy
  → SAM Perturbation (spurious + random) → Anisotropy Ratio → Pearson r → WGA
```

---

## Subtask L-2-1: SSL Trainer Unified API

**Parent Epic:** A-2 (SSL pre-training runners, complexity 14)

### Function Signature

```python
def train_ssl(
    method: str,                          # "simclr" | "mocov2" | "dino"
    dataset_name: str,                    # "waterbirds" | "celeba" | "cmnist"
    data_root: str,                       # path to dataset root
    checkpoint_dir: str,                  # directory for checkpoint saves
    epochs: int = 200,
    checkpoint_epochs: list[int] = None,  # default: [50, 100, 150, 200]
    batch_size: int = 256,
    lr: float = 0.03,
    momentum: float = 0.9,
    weight_decay: float = 1e-4,
    seed: int = 1,
    device: str = "cuda",
    skip_if_exists: bool = True,          # skip training if all checkpoints found
) -> dict[int, str]:                      # {epoch: checkpoint_path}
    """
    Unified SSL pre-training dispatcher. Routes to method-specific trainer.
    Returns dict mapping checkpoint epoch → path.

    Raises:
        ValueError: if method not in {"simclr", "mocov2", "dino"}
        FileNotFoundError: if dataset not found at data_root
    """
```

### Dispatch Logic (Pseudo-code)

```
train_ssl(method, dataset_name, ...):
    set_seed(seed)
    dataset = load_dataset(dataset_name, data_root, split="train", ssl_augment=True)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=4)
    backbone = resnet50(pretrained=True)  # ImageNet init
    backbone = strip_classifier(backbone)  # remove fc layer → 2048-dim output

    if method == "simclr":
        model = SimCLRWrapper(backbone, proj_dim=128)
        optimizer = SGD(model.parameters(), lr=lr, momentum=momentum, weight_decay=weight_decay)
        scheduler = CosineAnnealingLR(optimizer, T_max=epochs)
        loss_fn = NTXentLoss(temperature=0.5, batch_size=batch_size)
        trainer = EpochTrainer(model, optimizer, scheduler, loss_fn)

    elif method == "mocov2":
        model = MoCoV2Wrapper(backbone, queue_size=65536, momentum=0.999, temp=0.2, proj_dim=128)
        optimizer = SGD(model.parameters(), lr=lr, momentum=momentum, weight_decay=weight_decay)
        scheduler = CosineAnnealingLR(optimizer, T_max=epochs)
        trainer = MoCoTrainer(model, optimizer, scheduler)

    elif method == "dino":
        model = DINOWrapper(backbone, teacher_momentum_schedule=(0.996, 1.0))
        optimizer = AdamW(model.parameters(), lr=1e-4, weight_decay=0.04)
        scheduler = DINOScheduler(optimizer, epochs)
        trainer = DINOTrainer(model, optimizer, scheduler)

    checkpoints = {}
    for epoch in range(1, epochs + 1):
        trainer.step(loader)
        if epoch in checkpoint_epochs:
            path = save_checkpoint(model.backbone, checkpoint_dir, method, dataset_name, epoch)
            checkpoints[epoch] = path

    return checkpoints
```

### Tensor Shapes (SimCLR example)

| Variable | Shape | dtype | Notes |
|----------|-------|-------|-------|
| `images` | `(B, 3, 224, 224)` | float32 | augmented view |
| `images2` | `(B, 3, 224, 224)` | float32 | second augmented view |
| `features` | `(B, 2048)` | float32 | ResNet-50 backbone output |
| `projections` | `(B, 128)` | float32 | after projection head, L2-normalized |
| `nt_xent_loss` | `()` | float32 | scalar NT-Xent loss |

---

## Subtask L-2-2: MoCo-v2 Momentum Encoder + Queue

**Parent Epic:** A-2 (complexity 14)

### Class Signature

```python
class MoCoV2Wrapper(torch.nn.Module):
    def __init__(
        self,
        backbone: torch.nn.Module,   # ResNet-50 without fc
        queue_size: int = 65536,     # K in MoCo paper
        momentum: float = 0.999,     # encoder momentum m
        temperature: float = 0.2,    # InfoNCE temperature τ
        proj_dim: int = 128,         # projection head output dim
    ) -> None: ...

    def forward(
        self,
        im_q: torch.Tensor,          # (B, 3, 224, 224) query images
        im_k: torch.Tensor,          # (B, 3, 224, 224) key images
    ) -> torch.Tensor:               # () scalar InfoNCE loss

    @torch.no_grad()
    def _momentum_update_key_encoder(self) -> None:
        """θ_k ← m·θ_k + (1-m)·θ_q"""

    @torch.no_grad()
    def _dequeue_and_enqueue(self, keys: torch.Tensor) -> None:
        """Enqueue current batch keys, dequeue oldest. keys: (B, proj_dim)"""
```

### Tensor Shapes

| Variable | Shape | Notes |
|----------|-------|-------|
| `im_q` | `(B, 3, 224, 224)` | query view |
| `im_k` | `(B, 3, 224, 224)` | key view |
| `q` | `(B, 128)` | query projection, L2-normed |
| `k` | `(B, 128)` | key projection, L2-normed, no grad |
| `queue` | `(128, K)` | K=65536, circular buffer |
| `logits` | `(B, K+1)` | l_pos concat l_neg |
| `labels` | `(B,)` | all zeros (positive = index 0) |
| `infonce_loss` | `()` | scalar |

### Pseudo-code: Forward Pass

```
forward(im_q, im_k):
    q = normalize(proj_head_q(backbone_q(im_q)))        # (B, 128)
    with no_grad:
        k = normalize(proj_head_k(backbone_k(im_k)))    # (B, 128)
        _momentum_update_key_encoder()

    l_pos = bmm(q.unsqueeze(1), k.unsqueeze(2)) / τ    # (B, 1)
    l_neg = mm(q, queue.clone()) / τ                    # (B, K)
    logits = cat([l_pos, l_neg], dim=1)                 # (B, K+1)
    labels = zeros(B, dtype=long)                       # (B,)
    loss = cross_entropy(logits, labels)
    _dequeue_and_enqueue(k)
    return loss
```

---

## Subtask L-4-1: SAM Perturbation + Spurious Direction Proxy

**Parent Epic:** A-4 (SAM anisotropy measurement, complexity 13)

### Function Signatures

```python
def compute_per_sample_probe_losses(
    backbone: torch.nn.Module,           # frozen ResNet-50
    probe: torch.nn.Linear,             # trained linear probe
    dataset: torch.utils.data.Dataset,  # labeled eval dataset
    batch_size: int = 256,
    device: str = "cuda",
) -> torch.Tensor:                      # (N,) float32, one loss per sample
    """
    Compute cross-entropy loss per sample using frozen backbone + linear probe.
    No gradients tracked.
    """

def get_spurious_direction_loader(
    dataset: torch.utils.data.Dataset,
    probe_losses: torch.Tensor,          # (N,) per-sample losses
    quantile: float = 0.75,             # top-25% = above 75th percentile
    batch_size: int = 256,
) -> torch.utils.data.DataLoader:
    """
    Returns DataLoader containing only high-loss samples (spurious proxy).
    Implements Ghaznavi 2023 LFR top-25% selection.
    """

def apply_sam_perturbation(
    model: torch.nn.Module,
    loader: torch.utils.data.DataLoader,
    rho: float = 0.05,
    loss_fn: callable = None,            # default: cross_entropy on probe logits
    device: str = "cuda",
) -> torch.nn.Module:
    """
    Apply SAM first_step perturbation to model parameters.
    Returns CLONED perturbed model (original model unchanged).
    Based on davda54/sam first_step().

    e(w) = rho * grad / ||grad||_2
    w_perturbed = w + e(w)
    """

def compute_mean_loss(
    model: torch.nn.Module,
    probe: torch.nn.Linear,
    loader: torch.utils.data.DataLoader,
    device: str = "cuda",
) -> float:
    """Mean cross-entropy loss of backbone+probe on loader. No grad."""
```

### Tensor Shapes

| Variable | Shape | Notes |
|----------|-------|-------|
| `features` | `(N, 2048)` | backbone outputs, whole dataset |
| `probe_losses` | `(N,)` | per-sample CE loss |
| `spurious_mask` | `(N,)` | bool, True for top-25% high-loss |
| `grad_flat` | `(P,)` | P = total backbone parameters |
| `perturbation` | `(P,)` | `rho * grad_flat / ||grad_flat||` |

### Pseudo-code: SAM Perturbation

```
apply_sam_perturbation(model, loader, rho):
    perturbed = deepcopy(model)
    perturbed.train()

    # Accumulate gradients over loader
    total_loss = 0
    for x, y in loader:
        logits = probe(perturbed(x))
        loss = cross_entropy(logits, y)
        loss.backward()
        total_loss += loss.item()

    # Compute gradient norm across all parameters
    grad_norm = sqrt(sum(p.grad.norm()**2 for p in perturbed.parameters() if p.grad is not None))

    # Apply perturbation: w += rho * grad / ||grad||
    with no_grad:
        for p in perturbed.parameters():
            if p.grad is not None:
                e_w = p.grad * (rho / (grad_norm + 1e-12))
                p.add_(e_w)

    perturbed.zero_grad()
    return perturbed
```

---

## Subtask L-4-2: Random Direction Baseline + Anisotropy Ratio

**Parent Epic:** A-4 (complexity 13)

### Function Signature

```python
def measure_sharpness_anisotropy(
    backbone: torch.nn.Module,           # frozen SSL-pretrained ResNet-50
    probe: torch.nn.Linear,             # linear probe trained on backbone features
    dataset: torch.utils.data.Dataset,  # labeled eval dataset (group annotations available)
    rho: float = 0.05,
    n_random: int = 100,
    spurious_quantile: float = 0.75,
    batch_size: int = 256,
    device: str = "cuda",
) -> dict:
    """
    Returns:
        {
            "anisotropy_ratio": float,           # spurious_increase / mean(random_increases)
            "spurious_loss_increase": float,     # loss(w_perturbed, spurious) - loss(w, spurious)
            "mean_random_loss_increase": float,
            "std_random_loss_increase": float,
            "spurious_mask_size": int,           # |S| = |top-25% high-loss samples|
            "n_random": int,
        }
    """
```

### Pseudo-code: Full Anisotropy Measurement

```
measure_sharpness_anisotropy(backbone, probe, dataset, rho, n_random, ...):
    # Step 1: Compute per-sample probe losses (no group labels)
    probe_losses = compute_per_sample_probe_losses(backbone, probe, dataset)  # (N,)

    # Step 2: Build spurious direction loader (top-25% high-loss)
    spurious_loader = get_spurious_direction_loader(dataset, probe_losses, quantile=0.75)

    # Step 3: Base loss on spurious samples
    base_loss_spurious = compute_mean_loss(backbone, probe, spurious_loader)

    # Step 4: Perturb along spurious direction
    perturbed_spurious = apply_sam_perturbation(backbone, spurious_loader, rho)
    perturbed_loss_spurious = compute_mean_loss(perturbed_spurious, probe, spurious_loader)
    spurious_increase = perturbed_loss_spurious - base_loss_spurious

    # Step 5: 100 random direction baselines (same sample count as spurious proxy)
    n_spurious = len(spurious_loader.dataset)
    random_increases = []
    for i in range(n_random):
        # Random subset of same size from full dataset (reproducible via index seed)
        random_idx = randperm(len(dataset))[:n_spurious]
        random_subset_loader = DataLoader(Subset(dataset, random_idx), batch_size=batch_size)

        base_loss_random = compute_mean_loss(backbone, probe, random_subset_loader)
        perturbed_random = apply_sam_perturbation(backbone, random_subset_loader, rho)
        perturbed_loss_random = compute_mean_loss(perturbed_random, probe, random_subset_loader)
        random_increases.append(perturbed_loss_random - base_loss_random)

    # Step 6: Anisotropy ratio
    mean_random = mean(random_increases)
    anisotropy_ratio = spurious_increase / (mean_random + 1e-12)

    return {
        "anisotropy_ratio": anisotropy_ratio,
        "spurious_loss_increase": spurious_increase,
        "mean_random_loss_increase": mean_random,
        "std_random_loss_increase": std(random_increases),
        "spurious_mask_size": n_spurious,
        "n_random": n_random,
    }
```

### Statistical Analysis API

```python
def compute_pearson_correlation(
    anisotropy_ratios: list[float],  # one per checkpoint epoch [50, 100, 150, 200]
    worst_group_accs: list[float],   # WGA at same checkpoints
) -> dict:
    """
    Returns {"r": float, "p_value": float, "n": int}
    Uses scipy.stats.pearsonr.
    Gate condition: |r| > 0.5 and p_value < 0.05
    """

def compute_worst_group_accuracy(
    model: torch.nn.Module,
    probe: torch.nn.Linear,
    dataset: torch.utils.data.Dataset,  # must have group_array attribute
    n_groups: int,
    device: str = "cuda",
) -> float:
    """
    WGA = min(per_group_accuracy) over all groups.
    group_array: (N,) int tensor with group index per sample.
    """
```

---

## Module File Map

| File | Subtasks Covered |
|------|-----------------|
| `src/h_e1/ssl_trainer.py` | L-2-1, L-2-2 |
| `src/h_e1/anisotropy.py` | L-4-1, L-4-2 |
| `src/h_e1/probe.py` | Linear probe trainer (A-3, no subtask needed) |
| `src/h_e1/stats.py` | Pearson r, results aggregation (A-5) |
| `src/h_e1/data.py` | Dataset loaders (A-1) |
| `src/h_e1/visualize.py` | Figures (A-6) |
| `src/h_e1/run.py` | CLI orchestration (A-7) |
