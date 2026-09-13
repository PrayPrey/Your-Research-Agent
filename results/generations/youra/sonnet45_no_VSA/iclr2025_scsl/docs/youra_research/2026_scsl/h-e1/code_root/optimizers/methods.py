"""
Optimizer implementations for H-E1 SAM+SWA experiment
- SAM: Sharpness-Aware Minimization
- SWA: Stochastic Weight Averaging
- Joint SAM+SWA: Combined optimization
"""

import torch
import torch.nn as nn
from torch.optim import Optimizer
from torch.optim.swa_utils import AveragedModel, SWALR, update_bn
from typing import Optional


class SAM(Optimizer):
    """
    Sharpness-Aware Minimization optimizer.
    Based on Foret et al. 2021 (https://github.com/davda54/sam).
    """

    def __init__(
        self,
        params,
        base_optimizer: type,
        rho: float = 0.05,
        adaptive: bool = False,
        **kwargs
    ):
        """
        Initialize SAM optimizer.

        Args:
            params: Model parameters
            base_optimizer: Base optimizer class (e.g., torch.optim.SGD)
            rho: Perturbation radius for SAM
            adaptive: Use adaptive SAM (normalize by gradient norm)
            **kwargs: Arguments for base optimizer (lr, momentum, etc.)
        """
        defaults = dict(rho=rho, adaptive=adaptive, **kwargs)
        super(SAM, self).__init__(params, defaults)

        self.base_optimizer = base_optimizer(self.param_groups, **kwargs)
        self.param_groups = self.base_optimizer.param_groups
        self.rho = rho
        self.adaptive = adaptive

    @torch.no_grad()
    def first_step(self, zero_grad: bool = False):
        """
        First forward pass: compute ε-adversarial perturbation.

        Args:
            zero_grad: Zero gradients after step
        """
        grad_norm = self._grad_norm()
        for group in self.param_groups:
            scale = group["rho"] / (grad_norm + 1e-12)
            for p in group["params"]:
                if p.grad is None:
                    continue
                self.state[p]["old_p"] = p.data.clone()
                e_w = p.grad * scale
                if self.adaptive:
                    e_w = e_w * torch.abs(p.data)
                p.add_(e_w)  # Perturb: θ + ε

        if zero_grad:
            self.zero_grad()

    @torch.no_grad()
    def second_step(self, zero_grad: bool = False):
        """
        Second forward pass: update weights with perturbed gradients.

        Args:
            zero_grad: Zero gradients after step
        """
        for group in self.param_groups:
            for p in group["params"]:
                if p.grad is None:
                    continue
                p.data = self.state[p]["old_p"]  # Restore original θ

        self.base_optimizer.step()  # Apply base optimizer update

        if zero_grad:
            self.zero_grad()

    def _grad_norm(self):
        """Compute L2 norm of gradients"""
        norm = torch.norm(
            torch.stack([
                p.grad.norm(p=2)
                for group in self.param_groups
                for p in group["params"]
                if p.grad is not None
            ]),
            p=2
        )
        return norm

    def step(self, closure=None):
        """Standard step method (not used in SAM two-pass pattern)"""
        raise NotImplementedError("SAM requires first_step() and second_step()")

    def zero_grad(self):
        """Zero gradients"""
        self.base_optimizer.zero_grad()


class JointSAMSWA:
    """
    Joint SAM+SWA optimizer wrapper.
    Combines SAM optimization with SWA weight averaging.
    """

    def __init__(
        self,
        model: nn.Module,
        base_optimizer: type,
        lr: float,
        momentum: float = 0.9,
        weight_decay: float = 0.0001,
        rho: float = 0.05,
        swa_start: int = 75,
        swa_lr: float = 0.05,
        epochs: int = 100
    ):
        """
        Initialize Joint SAM+SWA.

        Args:
            model: Model to optimize
            base_optimizer: Base optimizer (torch.optim.SGD)
            lr: Base learning rate
            momentum: SGD momentum
            weight_decay: L2 regularization
            rho: SAM perturbation radius
            swa_start: Epoch to start SWA averaging
            swa_lr: Learning rate for SWA phase
            epochs: Total training epochs
        """
        self.model = model
        self.sam = SAM(
            model.parameters(),
            base_optimizer,
            lr=lr,
            momentum=momentum,
            weight_decay=weight_decay,
            rho=rho
        )
        self.swa_model = AveragedModel(model)
        self.swa_scheduler = SWALR(self.sam.base_optimizer, swa_lr=swa_lr)
        self.swa_start = swa_start
        self.current_epoch = 0
        self.epochs = epochs

    def step(
        self,
        loss_fn: callable,
        inputs: torch.Tensor,
        targets: torch.Tensor,
        model: nn.Module
    ) -> float:
        """
        Single optimization step (SAM two-pass + optional SWA update).

        Args:
            loss_fn: Loss function (e.g., BCEWithLogitsLoss)
            inputs: Batch inputs [B, 3, H, W]
            targets: Batch targets [B]
            model: Model being trained

        Returns:
            loss: Scalar loss value
        """
        # First forward pass: enable BN stats
        enable_running_stats(model)
        outputs = model(inputs)
        loss = loss_fn(outputs, targets)
        loss.backward()
        self.sam.first_step(zero_grad=True)

        # Second forward pass: disable BN stats
        disable_running_stats(model)
        outputs_perturbed = model(inputs)
        loss_perturbed = loss_fn(outputs_perturbed, targets)
        loss_perturbed.backward()
        self.sam.second_step(zero_grad=True)

        return loss.item()

    def on_epoch_end(self, epoch: int):
        """
        End-of-epoch hook for SWA averaging.

        Args:
            epoch: Current epoch number
        """
        self.current_epoch = epoch
        if epoch >= self.swa_start:
            self.swa_model.update_parameters(self.model)
            self.swa_scheduler.step()

    def get_model(self) -> nn.Module:
        """Get current model (SWA if after swa_start, else regular)"""
        if self.current_epoch >= self.swa_start:
            return self.swa_model
        return self.model

    def finalize(self, train_loader, device='cuda'):
        """
        Mandatory post-training BN statistics update.

        Args:
            train_loader: Training data loader for BN update
            device: Device to move data to
        """
        # Custom update_bn that handles device transfer
        self.swa_model.eval()
        with torch.no_grad():
            for batch_data in train_loader:
                # Handle both ColoredMNIST and CelebA data formats
                if len(batch_data) == 3:
                    inputs = batch_data[0]
                else:
                    inputs = batch_data[0]
                inputs = inputs.to(device)
                self.swa_model(inputs)


def enable_running_stats(model: nn.Module):
    """Enable BN running stats tracking (for SAM first pass)"""
    def _enable(module):
        if isinstance(module, (nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d)):
            module.track_running_stats = True
    model.apply(_enable)


def disable_running_stats(model: nn.Module):
    """Disable BN running stats tracking (for SAM second pass)"""
    def _disable(module):
        if isinstance(module, (nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d)):
            module.track_running_stats = False
    model.apply(_disable)


def get_optimizer(
    method: str,
    model: nn.Module,
    lr: float,
    momentum: float = 0.9,
    weight_decay: float = 0.0001,
    rho: float = 0.05,
    swa_start: int = 75,
    swa_lr: float = 0.05,
    epochs: int = 100
):
    """
    Factory function to create optimizer for each method.

    Args:
        method: Training method (ERM, SAM, SWA, Joint, Sequential)
        model: Model to optimize
        lr: Base learning rate
        momentum: SGD momentum
        weight_decay: L2 regularization
        rho: SAM perturbation radius
        swa_start: Epoch to start SWA
        swa_lr: SWA learning rate
        epochs: Total training epochs

    Returns:
        optimizer: Configured optimizer or wrapper
    """
    if method == "ERM":
        return torch.optim.SGD(
            model.parameters(),
            lr=lr,
            momentum=momentum,
            weight_decay=weight_decay
        )
    elif method == "SAM":
        return SAM(
            model.parameters(),
            torch.optim.SGD,
            lr=lr,
            momentum=momentum,
            weight_decay=weight_decay,
            rho=rho
        )
    elif method == "SWA":
        base_opt = torch.optim.SGD(
            model.parameters(),
            lr=lr,
            momentum=momentum,
            weight_decay=weight_decay
        )
        swa_model = AveragedModel(model)
        swa_scheduler = SWALR(base_opt, swa_lr=swa_lr)
        return {
            "optimizer": base_opt,
            "swa_model": swa_model,
            "swa_scheduler": swa_scheduler,
            "swa_start": swa_start
        }
    elif method == "Joint":
        return JointSAMSWA(
            model,
            torch.optim.SGD,
            lr,
            momentum,
            weight_decay,
            rho,
            swa_start,
            swa_lr,
            epochs
        )
    elif method == "Sequential":
        sam = SAM(
            model.parameters(),
            torch.optim.SGD,
            lr=lr,
            momentum=momentum,
            weight_decay=weight_decay,
            rho=rho
        )
        sgd = torch.optim.SGD(
            model.parameters(),
            lr=lr,
            momentum=momentum,
            weight_decay=weight_decay
        )
        swa_model = AveragedModel(model)
        swa_scheduler = SWALR(sgd, swa_lr=swa_lr)
        return {
            "sam": sam,
            "sgd": sgd,
            "swa_model": swa_model,
            "swa_scheduler": swa_scheduler,
            "swa_start": swa_start
        }
    else:
        raise ValueError(f"Unknown method: {method}")
