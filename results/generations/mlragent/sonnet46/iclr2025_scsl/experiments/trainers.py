"""
Training methods: ERM, GroupDRO, JTT, and CAGR (proposed).
"""
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import defaultdict
from gradient_analysis import (
    identify_gradient_subspaces, decompose_gradient,
    compute_spurious_dominance_ratio, estimate_hessian_curvature
)


class ERMTrainer:
    """Standard Empirical Risk Minimization."""
    def __init__(self, model, lr=1e-3, weight_decay=1e-4, device='cuda'):
        self.model = model
        self.device = device
        self.optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
        self.loss_fn = nn.CrossEntropyLoss()
        self.name = 'ERM'

    def train_epoch(self, dataloader):
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0

        for batch in dataloader:
            if len(batch) == 3:
                inputs, targets, _ = batch
            else:
                inputs, targets = batch

            inputs, targets = inputs.to(self.device), targets.to(self.device)

            self.optimizer.zero_grad()
            logits = self.model(inputs)
            loss = self.loss_fn(logits, targets)
            loss.backward()
            self.optimizer.step()

            total_loss += loss.item() * len(targets)
            correct += (logits.argmax(1) == targets).sum().item()
            total += len(targets)

        return total_loss / total, correct / total

    def get_extra_metrics(self):
        return {}


class GroupDROTrainer:
    """
    Group Distributionally Robust Optimization.
    Requires group labels. Maintains per-group weights and upweights worst group.
    """
    def __init__(self, model, n_groups=4, lr=1e-3, weight_decay=1e-4,
                 eta=0.1, device='cuda'):
        self.model = model
        self.n_groups = n_groups
        self.device = device
        self.optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
        self.loss_fn = nn.CrossEntropyLoss(reduction='none')
        self.eta = eta  # step size for group weights
        self.q = torch.ones(n_groups, device=device) / n_groups
        self.name = 'GroupDRO'

    def train_epoch(self, dataloader):
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0

        for batch in dataloader:
            if len(batch) == 3:
                inputs, targets, groups = batch
            else:
                inputs, targets = batch
                groups = torch.zeros(len(targets), dtype=torch.long)

            inputs = inputs.to(self.device)
            targets = targets.to(self.device)
            groups = groups.to(self.device)

            self.optimizer.zero_grad()
            logits = self.model(inputs)
            per_sample_loss = self.loss_fn(logits, targets)

            # Compute per-group losses
            group_losses = torch.zeros(self.n_groups, device=self.device)
            for g in range(self.n_groups):
                mask = (groups == g)
                if mask.sum() > 0:
                    group_losses[g] = per_sample_loss[mask].mean()

            # Update group weights: q_g <- q_g * exp(eta * loss_g)
            self.q = self.q * torch.exp(self.eta * group_losses.detach())
            self.q = self.q / self.q.sum()

            # Weighted loss
            loss = (self.q * group_losses).sum()
            loss.backward()
            self.optimizer.step()

            total_loss += loss.item() * len(targets)
            correct += (logits.argmax(1) == targets).sum().item()
            total += len(targets)

        return total_loss / total, correct / total

    def get_extra_metrics(self):
        return {'group_weights': self.q.cpu().numpy().tolist()}


class JTTTrainer:
    """
    Just Train Twice (JTT).
    Phase 1: Train ERM model to identify misclassified (hard) samples.
    Phase 2: Train with upweighted hard samples.
    """
    def __init__(self, model, model_factory, lr=1e-3, weight_decay=1e-4,
                 upweight=20, device='cuda'):
        self.model = model
        self.model_factory = model_factory
        self.device = device
        self.lr = lr
        self.weight_decay = weight_decay
        self.upweight = upweight
        self.loss_fn = nn.CrossEntropyLoss(reduction='none')
        self.phase = 1
        self.error_set = None
        self.optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
        self.name = 'JTT'

    def identify_errors(self, dataloader):
        """Phase 1: identify ERM misclassified samples."""
        self.model.eval()
        error_indices = []
        idx_offset = 0
        with torch.no_grad():
            for batch in dataloader:
                if len(batch) == 3:
                    inputs, targets, _ = batch
                else:
                    inputs, targets = batch
                inputs, targets = inputs.to(self.device), targets.to(self.device)
                logits = self.model(inputs)
                preds = logits.argmax(1)
                wrong = (preds != targets).cpu().numpy()
                error_indices.extend(np.where(wrong)[0] + idx_offset)
                idx_offset += len(targets)
        self.error_set = set(error_indices)
        return len(error_indices)

    def train_epoch(self, dataloader):
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0

        idx_offset = 0
        for batch in dataloader:
            if len(batch) == 3:
                inputs, targets, _ = batch
            else:
                inputs, targets = batch

            inputs = inputs.to(self.device)
            targets = targets.to(self.device)

            self.optimizer.zero_grad()
            logits = self.model(inputs)
            per_sample_loss = self.loss_fn(logits, targets)

            # Create weights based on error set
            if self.error_set is not None and self.phase == 2:
                weights = torch.ones(len(targets), device=self.device)
                for j in range(len(targets)):
                    if (idx_offset + j) in self.error_set:
                        weights[j] = self.upweight
                loss = (weights * per_sample_loss).mean()
            else:
                loss = per_sample_loss.mean()

            loss.backward()
            self.optimizer.step()

            total_loss += loss.item() * len(targets)
            correct += (logits.argmax(1) == targets).sum().item()
            total += len(targets)
            idx_offset += len(targets)

        return total_loss / total, correct / total

    def get_extra_metrics(self):
        return {'phase': self.phase, 'error_set_size': len(self.error_set) if self.error_set else 0}


class CAGRTrainer:
    """
    Curvature-Aware Gradient Reweighting (CAGR) - Proposed Method.

    Decomposes gradients into causal and spurious components and
    penalizes updates along low-curvature spurious directions.
    """
    def __init__(self, model, causal_idx, spurious_idx, lr=1e-3, weight_decay=1e-4,
                 beta=1.0, hessian_update_freq=50, device='cuda'):
        self.model = model
        self.causal_idx = causal_idx
        self.spurious_idx = spurious_idx
        self.device = device
        self.beta = beta
        self.hessian_update_freq = hessian_update_freq
        self.loss_fn = nn.CrossEntropyLoss()
        self.lr = lr
        self.weight_decay = weight_decay

        # Initialize optimizer
        self.optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)

        # Subspace bases (initialized as None, estimated during training)
        self.V_c = None
        self.V_s = None

        # Curvature estimates
        self.lambda_c = 1.0
        self.lambda_s = 1.0
        self.alpha = 1.0  # penalty factor

        # Tracking
        self.step_count = 0
        self.rho_history = []  # spurious dominance ratio
        self.alpha_history = []

        self.name = 'CAGR'

    def _compute_alpha(self):
        """Curvature-adaptive penalty: alpha = exp(-beta * lambda_c / (lambda_s + eps))"""
        ratio = self.lambda_c / (self.lambda_s + 1e-8)
        alpha = np.exp(-self.beta * ratio)
        # Clip to reasonable range
        alpha = max(0.0, min(1.0, alpha))
        return alpha

    def update_subspaces(self, dataloader):
        """Update gradient subspace estimates."""
        V_c, V_s = identify_gradient_subspaces(
            self.model, self.loss_fn, dataloader,
            self.causal_idx, self.spurious_idx,
            self.device, n_batches=3
        )
        if V_c is not None:
            self.V_c = V_c
        if V_s is not None:
            self.V_s = V_s

    def update_curvature(self, dataloader):
        """Update Hessian curvature estimates."""
        lam_c = estimate_hessian_curvature(
            self.model, self.loss_fn, dataloader, self.V_c, self.device,
            n_batches=2, n_power_iter=5
        )
        lam_s = estimate_hessian_curvature(
            self.model, self.loss_fn, dataloader, self.V_s, self.device,
            n_batches=2, n_power_iter=5
        )
        self.lambda_c = max(lam_c, 1e-6)
        self.lambda_s = max(lam_s, 1e-6)
        self.alpha = self._compute_alpha()

    def train_epoch(self, dataloader):
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0
        rho_sum = 0.0
        n_batches = 0

        # Update subspaces at start of epoch if not initialized
        if self.V_c is None:
            self.update_subspaces(dataloader)
            self.update_curvature(dataloader)

        for batch in dataloader:
            if len(batch) == 3:
                inputs, targets, _ = batch
            else:
                inputs, targets = batch

            inputs = inputs.to(self.device)
            targets = targets.to(self.device)

            self.optimizer.zero_grad()
            logits = self.model(inputs)
            loss = self.loss_fn(logits, targets)
            loss.backward()

            # Get current gradient
            flat_grad = []
            params_with_grad = []
            for param in self.model.parameters():
                if param.requires_grad and param.grad is not None:
                    flat_grad.append(param.grad.detach().flatten())
                    params_with_grad.append(param)

            if flat_grad and self.V_c is not None and self.V_s is not None:
                flat_grad = torch.cat(flat_grad)

                # Decompose gradient
                g_c, g_s, g_perp = decompose_gradient(flat_grad, self.V_c, self.V_s)

                # Compute spurious dominance ratio
                rho = compute_spurious_dominance_ratio(g_c, g_s)
                rho_sum += rho

                # Modified gradient: penalize spurious component
                alpha = self.alpha
                modified_grad = g_c + alpha * g_s + g_perp

                # Write back modified gradient
                offset = 0
                for param in params_with_grad:
                    n = param.numel()
                    param.grad.data = modified_grad[offset:offset+n].view_as(param)
                    offset += n

            self.optimizer.step()

            # Periodic curvature update
            self.step_count += 1
            if self.step_count % self.hessian_update_freq == 0:
                self.update_curvature(dataloader)
                self.alpha_history.append(self.alpha)

            total_loss += loss.item() * len(targets)
            correct += (logits.argmax(1) == targets).sum().item()
            total += len(targets)
            n_batches += 1

        avg_rho = rho_sum / max(n_batches, 1)
        self.rho_history.append(avg_rho)

        return total_loss / total, correct / total

    def get_extra_metrics(self):
        return {
            'rho': self.rho_history[-1] if self.rho_history else None,
            'alpha': self.alpha,
            'lambda_c': self.lambda_c,
            'lambda_s': self.lambda_s,
        }


class DFRTrainer:
    """
    Deep Feature Reweighting (DFR).
    Phase 1: Train ERM on full data.
    Phase 2: Retrain only the last layer on balanced subset.
    """
    def __init__(self, model, lr=1e-3, weight_decay=1e-4, device='cuda'):
        self.model = model
        self.device = device
        self.lr = lr
        self.weight_decay = weight_decay
        self.loss_fn = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
        self.phase = 1
        self.name = 'DFR'

    def freeze_features(self):
        """Freeze all layers except the last one."""
        # Freeze all parameters
        for param in self.model.parameters():
            param.requires_grad = False

        # Unfreeze last layer
        if hasattr(self.model, 'net'):
            # LinearClassifier
            for param in self.model.net[-1].parameters():
                param.requires_grad = True
        elif hasattr(self.model, 'classifier'):
            # CNN
            for param in self.model.classifier[-1].parameters():
                param.requires_grad = True

        # Update optimizer with only trainable parameters
        trainable = [p for p in self.model.parameters() if p.requires_grad]
        self.optimizer = optim.Adam(trainable, lr=self.lr, weight_decay=self.weight_decay)

    def train_epoch(self, dataloader):
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0

        for batch in dataloader:
            if len(batch) == 3:
                inputs, targets, _ = batch
            else:
                inputs, targets = batch

            inputs = inputs.to(self.device)
            targets = targets.to(self.device)

            self.optimizer.zero_grad()
            logits = self.model(inputs)
            loss = self.loss_fn(logits, targets)
            loss.backward()
            self.optimizer.step()

            total_loss += loss.item() * len(targets)
            correct += (logits.argmax(1) == targets).sum().item()
            total += len(targets)

        return total_loss / total, correct / total

    def get_extra_metrics(self):
        return {'phase': self.phase}
