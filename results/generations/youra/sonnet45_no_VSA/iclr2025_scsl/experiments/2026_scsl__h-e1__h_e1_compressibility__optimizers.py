"""Optimizer factory and SAM implementation."""

from typing import Type
import torch
import torch.nn as nn


BASE_OPTIMIZER_CONFIG = {
    "type": "SGD",
    "lr": 0.01,
    "momentum": 0.9,
    "weight_decay": 0.0001,
    "nesterov": False
}

METHOD_CONFIGS = {
    "ERM": {},
    "SAM": {
        "rho": 0.05,
        "adaptive": False
    },
    "SWA": {
        "swa_start_epoch": 10,
        "swa_lr": 0.005,
        "swa_anneal_epochs": 10
    },
    "Dropout": {},
    "SpectralNorm": {}
}


class SAM(torch.optim.Optimizer):
    """Sharpness-Aware Minimization optimizer."""

    def __init__(
        self,
        params,
        base_optimizer: Type[torch.optim.Optimizer],
        rho: float = 0.05,
        adaptive: bool = False,
        **kwargs
    ):
        assert rho >= 0.0, f"Invalid rho: {rho}"

        defaults = dict(rho=rho, adaptive=adaptive, **kwargs)
        super(SAM, self).__init__(params, defaults)

        self.base_optimizer = base_optimizer(self.param_groups, **kwargs)
        self.param_groups = self.base_optimizer.param_groups

    @torch.no_grad()
    def first_step(self, zero_grad: bool = False):
        """Compute gradient and perturb weights."""
        grad_norm = self._grad_norm()
        for group in self.param_groups:
            scale = group["rho"] / (grad_norm + 1e-12)

            for p in group["params"]:
                if p.grad is None:
                    continue
                self.state[p]["old_p"] = p.data.clone()
                e_w = (torch.pow(p, 2) if group["adaptive"] else 1.0) * p.grad * scale.to(p)
                p.add_(e_w)

        if zero_grad:
            self.zero_grad()

    @torch.no_grad()
    def second_step(self, zero_grad: bool = False):
        """Update with perturbed gradient and restore original weights."""
        for group in self.param_groups:
            for p in group["params"]:
                if p.grad is None:
                    continue
                p.data = self.state[p]["old_p"]

        self.base_optimizer.step()

        if zero_grad:
            self.zero_grad()

    def _grad_norm(self):
        """Compute gradient norm."""
        shared_device = self.param_groups[0]["params"][0].device
        norm = torch.norm(
            torch.stack([
                ((torch.abs(p) if group["adaptive"] else 1.0) * p.grad).norm(p=2).to(shared_device)
                for group in self.param_groups for p in group["params"]
                if p.grad is not None
            ]),
            p=2
        )
        return norm

    def step(self, closure=None):
        """Not used - call first_step() and second_step() explicitly."""
        raise NotImplementedError("SAM requires explicit first_step() and second_step() calls")


def get_optimizer(
    model: nn.Module,
    method: str,
    lr: float = 0.01,
    momentum: float = 0.9,
    weight_decay: float = 1e-4
) -> torch.optim.Optimizer:
    """Optimizer factory for all methods."""
    if method == "SAM":
        return SAM(
            model.parameters(),
            base_optimizer=torch.optim.SGD,
            rho=METHOD_CONFIGS["SAM"]["rho"],
            lr=lr,
            momentum=momentum,
            weight_decay=weight_decay
        )
    else:
        return torch.optim.SGD(
            model.parameters(),
            lr=lr,
            momentum=momentum,
            weight_decay=weight_decay
        )
