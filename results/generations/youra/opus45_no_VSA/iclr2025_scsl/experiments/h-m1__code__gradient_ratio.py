import torch
from torch import nn, Tensor
from torch.func import functional_call, vmap, grad
from typing import Callable, Dict, Tuple

def compute_per_sample_grad_norms(
    model: nn.Module,
    params: Dict[str, Tensor],
    buffers: Dict[str, Tensor],
    data: Tensor,
    targets: Tensor,
    loss_fn: Callable[[Tensor, Tensor], Tensor],
) -> Tensor:
    def compute_loss(params, buffers, sample, target):
        pred = functional_call(model, (params, buffers), (sample.unsqueeze(0),))
        return loss_fn(pred, target.unsqueeze(0))
    ft_grad = grad(compute_loss)
    ft_sample_grad = vmap(ft_grad, in_dims=(None, None, 0, 0))
    grads = ft_sample_grad(params, buffers, data, targets)
    flat_grads = []
    for name in grads:
        g = grads[name]
        flat_grads.append(g.reshape(g.shape[0], -1))
    all_grads = torch.cat(flat_grads, dim=1)
    norms = all_grads.norm(p=2, dim=1)
    return norms

def compute_gradient_ratio(
    grad_norms: Tensor,
    group_labels: Tensor,
    majority_groups: Tuple[int, ...] = (0, 3),
) -> float:
    majority_mask = torch.zeros_like(group_labels, dtype=torch.bool)
    for g in majority_groups:
        majority_mask |= (group_labels == g)
    minority_mask = ~majority_mask
    if majority_mask.sum() == 0 or minority_mask.sum() == 0:
        return 1.0
    r = grad_norms[majority_mask].mean() / grad_norms[minority_mask].mean()
    return r.item()
