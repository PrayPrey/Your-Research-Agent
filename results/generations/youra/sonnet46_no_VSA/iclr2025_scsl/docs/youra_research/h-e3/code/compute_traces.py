import os
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from torch.func import grad, vmap, functional_call
from torch.utils.data import DataLoader
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import config


def verify_architecture(model: nn.Module) -> None:
    assert isinstance(model.fc, nn.Linear), f"model.fc must be nn.Linear, got {type(model.fc)}"
    assert model.fc.out_features == 2, f"Expected out=2, got {model.fc.out_features}"
    assert model.fc.in_features == 2048, f"Expected in=2048, got {model.fc.in_features}"


def model_backbone_forward(model: nn.Module, x: Tensor) -> Tensor:
    """x: [B,3,224,224] -> [B,2048] with no_grad on backbone."""
    backbone = nn.Sequential(*list(model.children())[:-1])
    with torch.no_grad():
        out = backbone(x)  # [B, 2048, 1, 1]
    return out.squeeze(-1).squeeze(-1)  # [B, 2048]


def extract_features(model: nn.Module, inputs: Tensor, device: str) -> Tensor:
    """Returns (N, 2048)."""
    return model_backbone_forward(model, inputs.to(device))


def _fc_loss_single(
    params: dict,
    feat: Tensor,
    target: Tensor,
    fc_module: nn.Module,
) -> Tensor:
    """Cross-entropy for single sample via functional_call. Returns scalar."""
    logit = functional_call(fc_module, params, feat.unsqueeze(0))  # [1,2]
    return F.cross_entropy(logit, target.unsqueeze(0))


def _compute_batch_hvp(
    fc_params: dict,
    features: Tensor,
    targets: Tensor,
    v: dict,
    fc_module: nn.Module,
) -> Tensor:
    """vHv per sample for one Rademacher probe. Returns [B]."""
    def hvp_single(feat: Tensor, target: Tensor) -> Tensor:
        loss_fn = lambda p: _fc_loss_single(p, feat, target, fc_module)

        def vJp(p):
            g = grad(loss_fn)(p)
            return sum((g[n] * v[n]).sum() for n in g)

        Hv_dict = grad(vJp)(fc_params)
        return sum((Hv_dict[n] * v[n]).sum() for n in Hv_dict)

    return vmap(hvp_single)(features, targets)  # [B]


def compute_per_sample_fc_trace(
    model: nn.Module,
    loader: DataLoader,
    K: int = 50,
    device: str = "cuda",
) -> Tensor:
    """K=50 Hutchinson trace over full dataset. Returns (N,). loader MUST be non-shuffled."""
    model.eval()
    verify_architecture(model)
    fc_params = {n: p.detach() for n, p in model.fc.named_parameters()}
    # Move fc_params to device
    fc_params = {n: p.to(device) for n, p in fc_params.items()}
    all_traces = []

    for batch_inputs, batch_targets, _ in loader:
        batch_inputs = batch_inputs.to(device)
        batch_targets = batch_targets.to(device)
        features = model_backbone_forward(model, batch_inputs)  # [B, 2048]

        batch_traces = torch.zeros(len(batch_inputs), device=device)
        for _ in range(K):
            v = {n: (torch.randint(0, 2, p.shape, device=device).float() * 2 - 1)
                 for n, p in fc_params.items()}
            vHv = _compute_batch_hvp(fc_params, features, batch_targets, v, model.fc)
            batch_traces += vHv / K

        all_traces.append(batch_traces.detach().cpu())

    return torch.cat(all_traces)  # [N,]


def compute_traces_for_checkpoint(
    seed: int,
    epoch: int,
    loader: DataLoader,
    K: int = 50,
    device: str = "cuda",
) -> Tensor:
    from train_erm import load_checkpoint
    model = load_checkpoint(seed, epoch, device)
    return compute_per_sample_fc_trace(model, loader, K=K, device=device)


def compute_hutchinson_cv(
    model: nn.Module,
    loader: DataLoader,
    n_resamples: int = 5,
    K: int = 50,
    device: str = "cuda",
) -> float:
    """CV = std(run_means) / mean(run_means) across n_resamples independent runs."""
    run_means = []
    for i in range(n_resamples):
        torch.manual_seed(i)
        traces = compute_per_sample_fc_trace(model, loader, K=K, device=device)
        run_means.append(traces.mean().item())
    run_means = np.array(run_means)
    cv = float(run_means.std() / (run_means.mean() + 1e-12))
    if cv > 0.10:
        print(f"WARNING: Hutchinson CV={cv:.3f} > 0.10 — K=50 may be insufficient")
    return cv
