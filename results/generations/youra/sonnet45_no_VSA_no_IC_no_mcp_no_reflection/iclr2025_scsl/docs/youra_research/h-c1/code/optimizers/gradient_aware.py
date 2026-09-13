"""Gradient-aware optimizer wrapper with per-parameter LR modulation."""

import torch
from torch.optim import Optimizer, SGD
from typing import Dict, Type, Iterable


class GradientAwareOptimizer:
    """Wrapper applying lr_j = base_lr * (1 - ρ_j) per parameter."""

    def __init__(
        self,
        params: Iterable,
        base_optimizer_class: Type[Optimizer],
        rho_j_dict: Dict[str, float],
        base_lr: float = 1e-3,
        lr_floor: float = 1e-5,
        **optimizer_kwargs
    ):
        """
        Args:
            params: Model named_parameters()
            base_optimizer_class: SGD or Adam
            rho_j_dict: {param_name: rho_value}
            base_lr: Base learning rate
            lr_floor: Minimum lr for stability
            optimizer_kwargs: momentum, weight_decay, etc.
        """
        self.rho_j_dict = rho_j_dict
        self.base_lr = base_lr
        self.lr_floor = lr_floor

        # Create per-parameter groups with modulated lr
        param_groups = []
        for name, param in params:
            rho = rho_j_dict.get(name, 0.0)
            modulated_lr = max(base_lr * (1 - rho), lr_floor)

            param_groups.append({
                'params': [param],
                'lr': modulated_lr,
                'name': name
            })

        self.optimizer = base_optimizer_class(param_groups, **optimizer_kwargs)
        print(f"GradientAwareOptimizer: {len(param_groups)} param groups")

    def step(self, closure=None):
        """Forward to base optimizer."""
        return self.optimizer.step(closure)

    def zero_grad(self):
        """Forward to base optimizer."""
        self.optimizer.zero_grad()

    def state_dict(self) -> dict:
        """Save optimizer state + rho_j_dict."""
        return {
            'optimizer_state': self.optimizer.state_dict(),
            'rho_j_dict': self.rho_j_dict,
            'base_lr': self.base_lr
        }

    def load_state_dict(self, state_dict: dict):
        """Load optimizer state."""
        self.optimizer.load_state_dict(state_dict['optimizer_state'])
        self.rho_j_dict = state_dict['rho_j_dict']
        self.base_lr = state_dict['base_lr']
