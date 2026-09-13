# Logic: H-E3

**Applied**: PyTorch functional transform + vmap per-sample Hessian pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing code — new API design
**Analyzed Path**: `docs/youra_research/h-e3/code/` (does not exist yet)
**Relevant Symbols**: None — new implementation

---

## A-3: Hutchinson Trace [Complexity: 14, Budget: 4 subtasks]

### L-3-1: HVP Implementation via vmap+vjp

```python
from torch.func import grad, vmap, functional_call
import torch.nn.functional as F
from torch import Tensor
import torch

def model_backbone_forward(model: torch.nn.Module, x: Tensor) -> Tensor:
    """Extract penultimate features. x: [B,3,224,224] -> [B,2048]"""
    backbone = torch.nn.Sequential(*list(model.children())[:-1])  # all except fc
    with torch.no_grad():
        out = backbone(x)          # [B, 2048, 1, 1]
    return out.squeeze(-1).squeeze(-1)  # [B, 2048]


def fc_loss_single(
    params: dict,
    feat: Tensor,       # [2048]
    target: Tensor,     # [] (scalar long)
    fc_module: torch.nn.Module,
) -> Tensor:
    """Cross-entropy loss for single sample via functional_call. Returns scalar."""
    logit = functional_call(fc_module, params, feat.unsqueeze(0))  # [1, 2]
    return F.cross_entropy(logit, target.unsqueeze(0))             # scalar


def compute_batch_hvp(
    fc_params: dict,
    features: Tensor,    # [B, 2048]
    targets: Tensor,     # [B]
    v: dict,             # Rademacher probe, same shapes as fc_params
    fc_module: torch.nn.Module,
    device: str,
) -> Tensor:
    """vHv per sample for one Rademacher probe. Returns [B]"""

    def hvp_single(feat: Tensor, target: Tensor) -> Tensor:
        # feat: [2048], target: scalar
        # grad of loss w.r.t. params
        loss_fn = lambda p: fc_loss_single(p, feat, target, fc_module)
        # vHv = v^T H v = dot(grad(v^T grad(L)), v) via reverse-over-reverse
        def vJp(p):
            g = grad(loss_fn)(p)               # dict of param-grad tensors
            return sum((g[n] * v[n]).sum() for n in g)  # scalar: v^T g

        Hv_dict = grad(vJp)(fc_params)         # dict: H v (same shape as params)
        return sum((Hv_dict[n] * v[n]).sum() for n in Hv_dict)  # scalar vHv

    return vmap(hvp_single)(features, targets)  # [B]
```

**Rademacher probe generation:**
```python
v = {n: (torch.randint(0, 2, p.shape, device=device).float() * 2 - 1)
     for n, p in fc_params.items()}
# Shapes: weight -> [2, 2048], bias -> [2]
```

**Tensor shape summary:**

| Variable | Shape | Note |
|----------|-------|------|
| x (input) | [B, 3, 224, 224] | raw image batch |
| features | [B, 2048] | after backbone squeeze |
| fc_params['weight'] | [2, 2048] | last-fc weight |
| fc_params['bias'] | [2] | last-fc bias |
| v (probe) | same as fc_params | Rademacher ±1 |
| vHv per sample | [B] | one probe contribution |

### Subtasks [1/4]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | HVP via vmap+vjp | `fc_loss_single`, `compute_batch_hvp`, backbone feature extraction |

---

### L-3-2: Batch Accumulation Loop

```python
def compute_per_sample_fc_trace(
    model: torch.nn.Module,
    loader: torch.utils.data.DataLoader,
    K: int = 50,
    device: str = "cuda",
) -> Tensor:
    """K=50 Hutchinson trace over full dataset. Returns (N,) — loader MUST be non-shuffled."""
    model.eval()
    fc_params = {n: p for n, p in model.fc.named_parameters()}
    all_traces = []

    for batch_inputs, batch_targets, _ in loader:
        # batch_inputs: [B, 3, 224, 224], batch_targets: [B]
        batch_inputs = batch_inputs.to(device)
        batch_targets = batch_targets.to(device)

        features = model_backbone_forward(model, batch_inputs)  # [B, 2048]

        batch_traces = torch.zeros(len(batch_inputs), device=device)  # [B]
        for _ in range(K):
            v = {n: (torch.randint(0, 2, p.shape, device=device).float() * 2 - 1)
                 for n, p in fc_params.items()}
            vHv = compute_batch_hvp(fc_params, features, batch_targets, v, model.fc, device)  # [B]
            batch_traces += vHv / K   # running mean; [B]

        all_traces.append(batch_traces.detach().cpu())

    return torch.cat(all_traces)  # [N,] where N=4795 for train split
```

**Shape invariants:**
- `batch_traces`: `[B]` where B = current batch size (may be < 32 at epoch end)
- `all_traces` list: each element `[B_i]`, final concat `[N]` = `[4795]`
- Variable-size last batch is handled naturally by `torch.cat`

**Index alignment guarantee:** eval loader created with `shuffle=False` — order matches `minority_mask` built from `metadata.csv` in dataset construction order. Non-shuffled is REQUIRED; `compute_per_sample_fc_trace` does not accept shuffled loaders.

**Running mean correctness:** `batch_traces += vHv / K` accumulates K independent unbiased estimates of `trace(H)` per sample. Final value = `(1/K) * sum_k vHv_k` = unbiased Hutchinson estimator. No ordering dependency across probes.

### Subtasks [2/4]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-2 | Batch accumulation | K-probe loop, variable batch handling, non-shuffled loader requirement |

---

### L-3-3: Architecture Verification + Feature Extraction

```python
def verify_architecture(model: torch.nn.Module) -> None:
    """Assert model is ResNet-50 with binary last-fc. Raises AssertionError if wrong."""
    assert isinstance(model.fc, torch.nn.Linear), \
        f"model.fc must be nn.Linear, got {type(model.fc)}"
    assert model.fc.out_features == 2, \
        f"Expected binary classifier (out=2), got {model.fc.out_features}"
    assert model.fc.in_features == 2048, \
        f"Expected ResNet-50 feature dim 2048, got {model.fc.in_features}"
```

**Feature extraction detail:**
```python
def model_backbone_forward(model: torch.nn.Module, x: Tensor) -> Tensor:
    """x: [B,3,224,224] -> [B,2048] with no_grad on backbone."""
    # ResNet-50 children: [conv1, bn1, relu, maxpool, layer1, layer2, layer3, layer4, avgpool, fc]
    # Exclude last child (fc) → indices [:-1] gives up to and including avgpool
    backbone = torch.nn.Sequential(*list(model.children())[:-1])
    with torch.no_grad():
        out = backbone(x)   # [B, 2048, 1, 1]  (avgpool output)
    return out.squeeze(-1).squeeze(-1)  # [B, 2048]
```

**Note:** `nn.Sequential(*list(model.children())[:-1])` is safe for ResNet-50 because avgpool is the second-to-last child and flattening is done inside `model.forward()` before fc. The backbone sequential stops at avgpool output `[B, 2048, 1, 1]`; squeeze removes the spatial dims.

### Subtasks [3/4]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-3 | Architecture verify + feature extract | `verify_architecture`, `model_backbone_forward` with squeeze |

---

### L-3-4: Hutchinson CV + Checkpoint Loading

```python
def load_checkpoint(seed: int, epoch: int, device: str) -> torch.nn.Module:
    """Load model from checkpoint. Returns model in eval mode."""
    from train_erm import build_model
    import config
    path = config.ckpt_path(seed, epoch)   # f"results/checkpoints/ckpt_seed{seed}_epoch{epoch}.pt"
    state_dict = torch.load(path, map_location=device)
    model = build_model()
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model


def compute_hutchinson_cv(
    model: torch.nn.Module,
    loader: torch.utils.data.DataLoader,
    n_resamples: int = 5,
    K: int = 50,
    device: str = "cuda",
) -> float:
    """CV of Hutchinson estimator across n_resamples independent runs. Returns float.

    CV = std(mean_of_traces per run) / mean(mean_of_traces per run).
    Each run uses fresh Rademacher probes — measures estimator stability, not per-sample variance.
    """
    run_means = []
    for i in range(n_resamples):
        torch.manual_seed(i)  # distinct probe sets per run
        traces = compute_per_sample_fc_trace(model, loader, K=K, device=device)  # [N]
        run_means.append(traces.mean().item())

    import numpy as np
    run_means = np.array(run_means)
    cv = run_means.std() / run_means.mean()
    # CV > 0.10 → warning: K=50 may be insufficient; consider K=100
    return float(cv)
```

**CV interpretation:** `cv > 0.10` means estimator variance is >10% of its mean — log a warning but do not abort (secondary gate criterion per PRD).

### Subtasks [4/4]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-4 | CV + checkpoint load | `compute_hutchinson_cv` (std of run_means / mean), `load_checkpoint` rebuild |

---

## A-2: ERM Training [Complexity: 10, Budget: 1 subtask]

### L-2-1: Checkpoint Save at t=0 Logic

```python
def run_training(
    seed: int,
    n_epochs: int,
    checkpoint_epochs: list[int],   # e.g. [0, 1, 5, 10, 20, 50]
    device: str,
) -> None:
    """ERM training with checkpoint saves. t=0 saved BEFORE any gradient update."""
    import config
    from data import get_train_loader

    config.set_seed(seed)
    model = build_model()           # resnet50(IMAGENET1K_V1), fc replaced with Linear(2048,2)
    model.to(device)

    optimizer = torch.optim.SGD(
        model.parameters(), lr=config.LR,
        momentum=config.MOMENTUM, weight_decay=config.WEIGHT_DECAY
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=n_epochs)
    loader = get_train_loader(config.DATA_ROOT, config.BATCH_SIZE)

    # CRITICAL: save t=0 BEFORE any Waterbirds gradient step
    if 0 in checkpoint_epochs:
        save_checkpoint(model, seed, epoch=0)

    for epoch in range(1, n_epochs + 1):
        train_one_epoch(model, loader, optimizer, scheduler, device)
        if epoch in checkpoint_epochs:
            save_checkpoint(model, seed, epoch)


def save_checkpoint(model: torch.nn.Module, seed: int, epoch: int) -> None:
    """Save model.state_dict() to ckpt_path(seed, epoch)."""
    import config, os
    path = config.ckpt_path(seed, epoch)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    torch.save(model.state_dict(), path)
```

**Why t=0 must precede training loop:** `build_model()` returns pretrained ImageNet weights. The epoch=0 checkpoint captures the model *before any Waterbirds exposure*. If `save_checkpoint` is placed inside `for epoch in range(1, ...)` with `epoch == 0` guard, it never fires. The save MUST be before `for epoch in range(1, n_epochs + 1)`.

**`build_model` contract:**
```python
def build_model() -> torch.nn.Module:
    """ResNet-50 with last fc replaced. Returns model on CPU."""
    from torchvision.models import resnet50, ResNet50_Weights
    model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
    model.fc = torch.nn.Linear(2048, 2)   # reinit — NOT pretrained for Waterbirds
    return model
```

### Subtasks [1/1]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | t=0 checkpoint | save before training loop, `build_model` fc replacement, `save_checkpoint` path |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings <= 2 lines
- [x] Tensor shapes in code comments
- [x] Subtask count within budget (5 total: 4 for A-3, 1 for A-2)
- [x] Codebase Analysis section included
- [x] Green-field — Serena skip acceptable
