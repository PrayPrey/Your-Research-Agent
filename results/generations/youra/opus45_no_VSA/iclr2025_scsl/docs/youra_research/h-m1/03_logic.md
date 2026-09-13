# Logic: H-M1

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing code — new API design from scratch
**Analyzed Path**: N/A
**Relevant Symbols**: None

---

## A-3: Per-sample gradients [Complexity: 15, Budget: 15]

**Applied**: Standard PyTorch (torch.func.vmap + grad, no KB match — functorch functional_call pattern)

### API Signatures

```python
from torch.func import functional_call, vmap, grad
import torch
from torch import nn, Tensor
from typing import Callable

def compute_per_sample_grad_norms(
    model: nn.Module,
    data: Tensor,          # [B, 3, 224, 224]
    targets: Tensor,       # [B]
    loss_fn: Callable[[Tensor, Tensor], Tensor],  # (logits, target) -> scalar
) -> Tensor:                # [B] per-sample L2 grad norm
    """Per-sample gradient norms via vmap(grad(...)) over stateless functional_call."""
    ...

def _compute_loss_stateless(params: dict, buffers: dict, model: nn.Module,
                             x: Tensor, y: Tensor) -> Tensor:
    """x: [1, 3, 224, 224] (single sample), returns scalar loss."""
    ...

def compute_gradient_ratio(
    grad_norms: Tensor,        # [B]
    group_labels: Tensor,      # [B], values in {0,1,2,3}
    majority_groups: tuple[int, ...] = (0, 3),
) -> float:
    """r = mean(grad_norms[majority]) / mean(grad_norms[minority])."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| params (dict) | {name: [*param_shape]} | from `dict(model.named_parameters())` |
| data (unbatched, per vmap slice) | [1, 3, 224, 224] | add batch dim via `.unsqueeze(0)` inside stateless fn |
| per_sample_grads | dict of {name: [B, *param_shape]} | output of `vmap(grad(...))` |
| grad_norms | [B] | L2 norm flattened across all param grads, per sample |

### Pseudo-code

```
1. params = dict(model.named_parameters()); buffers = dict(model.named_buffers())
2. def compute_loss(params, buffers, x, y):
     logits = functional_call(model, (params, buffers), (x.unsqueeze(0),))  # [1, C]
     return loss_fn(logits, y.unsqueeze(0))
3. grad_fn = grad(compute_loss)   # grads wrt params, single sample
4. batched_grad_fn = vmap(grad_fn, in_dims=(None, None, 0, 0))
5. per_sample_grads = batched_grad_fn(params, buffers, data, targets)  # dict[name] -> [B, *shape]
6. flat = cat([g.reshape(B, -1) for g in per_sample_grads.values()], dim=1)  # [B, P]
7. grad_norms = flat.norm(p=2, dim=1)  # [B]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Stateless loss fn | `_compute_loss_stateless` wrapping `functional_call` |
| L-3-2 | vmap+grad wiring | `grad` over single sample, `vmap` batching with `in_dims=(None,None,0,0)` |
| L-3-3 | Flatten + norm | Concatenate per-param grads, compute L2 norm per sample |
| L-3-4 | Gradient ratio | Group-masked mean ratio (majority vs minority) |

---

## A-4: Sharpness ratio (Hessian) [Complexity: 17, Budget: 17]

**Applied**: Standard PyTorch (torch.autograd.functional.vhp, power iteration — no KB match)

### API Signatures

```python
from torch.autograd.functional import vhp
from torch.utils.data import DataLoader

def hvp_top_eigenvalue(
    model: nn.Module,
    data_loader: DataLoader,      # yields (image, label, group_id) batches
    loss_fn: Callable[[Tensor, Tensor], Tensor],
    num_iters: int = 20,
) -> float:
    """Top Hessian eigenvalue via power iteration using vhp (Hessian-vector product)."""
    ...

def _loss_over_loader(model: nn.Module, params: tuple[Tensor, ...],
                       data_loader: DataLoader, loss_fn: Callable) -> Tensor:
    """Full-batch (or accumulated) scalar loss for given param tuple, avg over loader."""
    ...

def compute_sharpness_ratio(
    model: nn.Module,
    minority_loader: DataLoader,
    majority_loader: DataLoader,
    loss_fn: Callable,
) -> float:
    """SR = top_eig(H_minority) / top_eig(H_majority)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| params (tuple) | (p1, p2, ...) each [*shape] | `tuple(model.parameters())` |
| v (random vector) | same structure as params, each [*shape] | initialized random, normalized |
| Hv | same structure as v | output of `vhp` |

### Pseudo-code (power iteration)

```
1. params = tuple(model.parameters())
2. v = [torch.randn_like(p) for p in params]; v = normalize(v)  # unit L2 norm over flattened v
3. loss_closure = lambda *p: _loss_over_loader(model, p, data_loader, loss_fn)
4. for i in range(num_iters):
5.     _, Hv = vhp(loss_closure, params, tuple(v))
6.     eigenvalue = dot(flatten(v), flatten(Hv))   # Rayleigh quotient
7.     v = normalize(Hv)                            # next iterate
8. return eigenvalue  # top eigenvalue estimate (float)
```

**Normalize helper**: `flat = cat([t.reshape(-1) for t in tensors]); norm = flat.norm(); return [t/norm for t in tensors]`

**Group split for SR**: build `minority_loader`/`majority_loader` by filtering dataset on `group_id in {1,2}` / `{0,3}` respectively (same Dataset, `Subset` + custom sampler or filtered index list), constructed in `train.py` before calling `compute_sharpness_ratio`.

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Loss closure | `_loss_over_loader`: full-loader avg loss as function of param tuple, for `vhp` |
| L-4-2 | Power iteration core | `hvp_top_eigenvalue`: init random v, iterate `vhp` + Rayleigh quotient + renormalize |
| L-4-3 | Group-filtered loaders | Build minority/majority `DataLoader`s from group_id (used by train.py + this module) |
| L-4-4 | Sharpness ratio | `compute_sharpness_ratio`: call `hvp_top_eigenvalue` on each loader, take ratio |

---

## External Dependencies (Base Hypothesis)

Not applicable — green-field, no base hypothesis code to call.
