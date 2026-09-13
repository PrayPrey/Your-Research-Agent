import torch
from torch import nn, Tensor

class GradientTracker:
    def __init__(self, model: nn.Module, majority_group: int = 0, minority_group: int = 3):
        self.majority_group = majority_group
        self.minority_group = minority_group
        self.gradient_history = []
        self.current_gradients = None
        self.epoch_group_norms = []
        self._hook_handle = model.fc.register_full_backward_hook(self._gradient_hook)

    def _gradient_hook(self, module: nn.Module, grad_input: tuple, grad_output: tuple) -> None:
        self.current_gradients = grad_output[0].detach().clone()

    def compute_group_gradient_ratio(self, batch_groups: Tensor) -> tuple:
        if self.current_gradients is None:
            return None, {}
        grad = self.current_gradients
        group_norms = {}
        for g in torch.unique(batch_groups):
            g_int = g.item()
            mask = batch_groups == g
            if mask.sum() > 0:
                group_norms[g_int] = grad[mask].norm().item()
        if self.minority_group not in group_norms or self.majority_group not in group_norms:
            return None, group_norms
        minority_norm = group_norms[self.minority_group]
        majority_norm = group_norms[self.majority_group]
        ratio = minority_norm / (majority_norm + 1e-8)
        return ratio, group_norms

    def log_epoch_gradients(self, epoch: int, ratio: float, group_norms: dict) -> None:
        self.gradient_history.append({
            'epoch': epoch,
            'gradient_ratio': ratio,
            'group_norms': group_norms
        })

    def get_ratio_history(self) -> list:
        return [h['gradient_ratio'] for h in self.gradient_history]

    def get_group_norm_history(self) -> list:
        return [h['group_norms'] for h in self.gradient_history]

    def remove(self) -> None:
        self._hook_handle.remove()
