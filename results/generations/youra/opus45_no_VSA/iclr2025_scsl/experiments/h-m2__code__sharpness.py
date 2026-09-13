import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from config import CONFIG
from data import WaterbirdDataset, get_group_loader


def compute_loss(model: nn.Module, loader: DataLoader) -> torch.Tensor:
    device = next(model.parameters()).device
    total_loss = torch.tensor(0.0, dtype=torch.float64, device=device)
    total_samples = 0
    criterion = nn.CrossEntropyLoss(reduction='sum')

    for x, y, _ in loader:
        x = x.double().to(device)
        y = y.to(device)
        logits = model(x)
        total_loss = total_loss + criterion(logits, y)
        total_samples += x.size(0)

    return total_loss / total_samples


def hessian_vector_product(model: nn.Module, loader: DataLoader, v: torch.Tensor) -> torch.Tensor:
    loss = compute_loss(model, loader)
    grads = torch.autograd.grad(loss, model.parameters(), create_graph=True)
    flat_grads = torch.cat([g.reshape(-1) for g in grads])
    grad_dot_v = torch.dot(flat_grads, v)
    hvp = torch.autograd.grad(grad_dot_v, model.parameters())
    return torch.cat([h.reshape(-1) for h in hvp]).detach()


def compute_group_sharpness(model: nn.Module, loader: DataLoader, num_iterations: int = 20) -> float:
    device = next(model.parameters()).device
    P = sum(p.numel() for p in model.parameters())
    v = torch.randn(P, dtype=torch.float64, device=device)
    v = v / torch.norm(v)

    lambda_max = torch.tensor(0.0, device=device)
    for _ in range(num_iterations):
        Hv = hessian_vector_product(model, loader, v)
        lambda_max = torch.dot(v, Hv)
        norm_Hv = torch.norm(Hv)
        if norm_Hv < 1e-12:
            break
        v = Hv / norm_Hv

    return abs(lambda_max.item())


def compute_sharpness_ratio(model: nn.Module, dataset: WaterbirdDataset) -> float:
    minority_sharpness = []
    for g in CONFIG.minority_groups:
        loader = get_group_loader(dataset, g, CONFIG.batch_size)
        s = compute_group_sharpness(model, loader, CONFIG.num_power_iter)
        minority_sharpness.append(s)
        print(f"  Group {g} (minority) sharpness: {s:.6f}")

    majority_sharpness = []
    for g in CONFIG.majority_groups:
        loader = get_group_loader(dataset, g, CONFIG.batch_size)
        s = compute_group_sharpness(model, loader, CONFIG.num_power_iter)
        majority_sharpness.append(s)
        print(f"  Group {g} (majority) sharpness: {s:.6f}")

    mean_minority = sum(minority_sharpness) / len(minority_sharpness)
    mean_majority = sum(majority_sharpness) / len(majority_sharpness)

    if mean_majority < 1e-12:
        return 1.0

    return mean_minority / mean_majority
