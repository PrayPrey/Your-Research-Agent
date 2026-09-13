import torch
from torch import nn, Tensor
from torch.autograd.functional import vhp
from torch.utils.data import DataLoader
from typing import Callable, Tuple, List

def _flatten(tensors: Tuple[Tensor, ...]) -> Tensor:
    return torch.cat([t.reshape(-1) for t in tensors])

def _unflatten(flat: Tensor, shapes: List[torch.Size]) -> Tuple[Tensor, ...]:
    tensors = []
    offset = 0
    for shape in shapes:
        numel = torch.prod(torch.tensor(shape)).item()
        tensors.append(flat[offset:offset+numel].reshape(shape))
        offset += numel
    return tuple(tensors)

def _normalize(tensors: Tuple[Tensor, ...]) -> Tuple[Tensor, ...]:
    flat = _flatten(tensors)
    norm = flat.norm()
    if norm == 0:
        return tensors
    return tuple(t / norm for t in tensors)

def hvp_top_eigenvalue(
    model: nn.Module,
    data_loader: DataLoader,
    loss_fn: Callable[[Tensor, Tensor], Tensor],
    num_iters: int = 20,
    device: str = "cuda",
) -> float:
    params = tuple(p for p in model.parameters() if p.requires_grad)
    shapes = [p.shape for p in params]
    v = tuple(torch.randn_like(p) for p in params)
    v = _normalize(v)

    def loss_closure(*param_vals):
        param_dict = {}
        idx = 0
        for name, p in model.named_parameters():
            if p.requires_grad:
                param_dict[name] = param_vals[idx]
                idx += 1
            else:
                param_dict[name] = p
        buf_dict = dict(model.named_buffers())
        total_loss = 0.0
        count = 0
        for batch in data_loader:
            images, labels = batch[0].to(device), batch[1].to(device)
            from torch.func import functional_call
            pred = functional_call(model, (param_dict, buf_dict), (images,))
            total_loss = total_loss + loss_fn(pred, labels) * images.size(0)
            count += images.size(0)
        return total_loss / count

    eigenvalue = 0.0
    for _ in range(num_iters):
        _, Hv = vhp(loss_closure, params, v)
        flat_v = _flatten(v)
        flat_Hv = _flatten(Hv)
        eigenvalue = torch.dot(flat_v, flat_Hv).item()
        v = _normalize(Hv)
    return eigenvalue

def compute_sharpness_ratio(
    model: nn.Module,
    minority_loader: DataLoader,
    majority_loader: DataLoader,
    loss_fn: Callable,
    device: str = "cuda",
) -> float:
    eig_minority = hvp_top_eigenvalue(model, minority_loader, loss_fn, device=device)
    eig_majority = hvp_top_eigenvalue(model, majority_loader, loss_fn, device=device)
    if eig_majority == 0:
        return 1.0
    return eig_minority / eig_majority
