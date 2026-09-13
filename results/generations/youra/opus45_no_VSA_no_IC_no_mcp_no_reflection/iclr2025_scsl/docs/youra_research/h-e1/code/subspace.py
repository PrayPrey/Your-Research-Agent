"""Gradient subspace accumulation and alignment measurement."""
import torch
import torch.nn as nn
from model import get_flat_grad


class GradientSubspaceAccumulator:
    def __init__(self, num_params: int, rank_k: int = 50, accumulation_epochs: int = 10):
        self.rank_k = rank_k
        self.accumulation_epochs = accumulation_epochs
        self.buffer = []
        self.subspace_S = None
        self.singular_values = None

    def accumulate(self, model: nn.Module, epoch: int) -> None:
        if epoch <= self.accumulation_epochs:
            grad_vec = get_flat_grad(model).detach().cpu()
            self.buffer.append(grad_vec)

    def compute_subspace(self) -> torch.Tensor:
        G = torch.stack(self.buffer)
        U, S_vals, Vt = torch.linalg.svd(G, full_matrices=False)
        k = min(self.rank_k, Vt.shape[0])
        self.subspace_S = Vt[:k].T
        self.singular_values = S_vals[:k]
        return self.subspace_S

    def measure_alignment(self, direction_vec: torch.Tensor) -> float:
        if self.subspace_S is None:
            return 0.0
        d = direction_vec / (direction_vec.norm() + 1e-8)
        S = self.subspace_S.to(d.device)
        proj_coeffs = S.T @ d
        proj_energy = (proj_coeffs ** 2).sum()
        return proj_energy.item()


def compute_direction(model: nn.Module, dataset, pairs: list, device) -> torch.Tensor:
    """Compute average gradient direction from sample pairs."""
    model.eval()
    grads = []
    criterion = nn.CrossEntropyLoss()
    for i, j, label in pairs[:50]:
        img_i, _, _ = dataset[i]
        img_j, _, _ = dataset[j]
        model.zero_grad()
        out_i = model(img_i.unsqueeze(0).to(device))
        loss_i = criterion(out_i, torch.tensor([label], device=device))
        loss_i.backward()
        grad_i = get_flat_grad(model).detach().cpu()
        model.zero_grad()
        out_j = model(img_j.unsqueeze(0).to(device))
        loss_j = criterion(out_j, torch.tensor([label], device=device))
        loss_j.backward()
        grad_j = get_flat_grad(model).detach().cpu()
        grads.append(grad_i - grad_j)
    if not grads:
        return torch.zeros(sum(p.numel() for p in model.parameters()))
    direction = torch.stack(grads).mean(dim=0)
    return direction / (direction.norm() + 1e-8)
