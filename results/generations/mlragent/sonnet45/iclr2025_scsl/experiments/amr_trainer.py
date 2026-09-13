"""
Adaptive Margin Regularization (AMR) Trainer
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from collections import defaultdict
import copy


class AMRTrainer:
    """Trainer implementing Adaptive Margin Regularization"""

    def __init__(self, model, config, total_steps):
        self.model = model
        self.config = config
        self.total_steps = total_steps
        self.device = config.device

        # Initialize tracking variables
        self.gradient_history = defaultdict(list)
        self.confidence_history = defaultdict(list)
        self.margin_history = defaultdict(list)
        self.step = 0

    def compute_margin(self, logits, targets):
        """Compute classification margin"""
        batch_size = logits.size(0)
        margins = torch.zeros(batch_size, device=self.device)

        for i in range(batch_size):
            correct_logit = logits[i, targets[i]]
            # Get max logit from other classes
            mask = torch.ones(logits.size(1), dtype=torch.bool, device=self.device)
            mask[targets[i]] = False
            other_logits = logits[i, mask]
            max_other = other_logits.max()
            margins[i] = correct_logit - max_other

        return margins

    def compute_gradient_magnitude(self):
        """Compute gradient magnitude for the model"""
        total_norm = 0.0
        for p in self.model.parameters():
            if p.grad is not None:
                param_norm = p.grad.data.norm(2)
                total_norm += param_norm.item() ** 2
        total_norm = total_norm ** 0.5
        return total_norm

    def compute_spurious_scores(self, confidences, margins, step):
        """Compute spurious feature scores for samples"""
        batch_size = len(confidences)
        scores = torch.zeros(batch_size, device=self.device)

        # Confidence indicator
        conf_indicator = (confidences > self.config.gamma_c).float()

        # For gradient acceleration, we need history
        # Simplified: use high confidence + large margin as proxy
        for i in range(batch_size):
            # Acceleration indicator (simplified)
            accel_indicator = 1.0 if step < self.config.tau else 0.5

            # Combine signals
            scores[i] = (
                self.config.alpha * conf_indicator[i] * accel_indicator +
                self.config.beta * torch.sigmoid(margins[i])
            )

        return scores

    def compute_amr_regularization(self, margins, spurious_scores):
        """Compute AMR regularization term"""
        # Sample weights based on spurious scores
        weights = torch.sigmoid(
            self.config.eta * (spurious_scores - self.config.delta)
        )

        # Margin penalty
        penalties = torch.zeros_like(margins)

        for i in range(len(margins)):
            m = margins[i]
            # Clamp margin to avoid numerical issues
            m_clamped = torch.clamp(m, min=-10.0, max=10.0)

            if m_clamped > self.config.m_target:
                # Quadratic penalty for excessive margins
                penalties[i] = (m_clamped - self.config.m_target) ** 2
            else:
                # Logarithmic penalty to prevent collapse
                # Use softplus to ensure positive input to log
                penalties[i] = -self.config.lambda_log * torch.log(
                    torch.nn.functional.softplus(m_clamped) + self.config.epsilon
                )

        # Weighted average with clamping to avoid NaN
        reg_loss = torch.clamp((weights * penalties).mean(), min=-100.0, max=100.0)
        return reg_loss, weights.mean()

    def compute_mu(self, step):
        """Compute adaptive regularization strength"""
        # Cosine schedule
        mu = self.config.mu_0 * (
            1 + np.cos(np.pi * step / self.total_steps)
        )
        return mu

    def train_step(self, inputs, targets, groups, optimizer):
        """Single training step with AMR"""
        self.model.train()
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)

        # Forward pass
        logits = self.model(inputs)

        # Standard cross-entropy loss
        ce_loss = F.cross_entropy(logits, targets)

        # Compute margins and confidence
        margins = self.compute_margin(logits, targets)
        probs = F.softmax(logits, dim=1)
        confidences = probs.max(dim=1)[0]

        # Compute spurious scores
        spurious_scores = self.compute_spurious_scores(
            confidences, margins, self.step
        )

        # Compute AMR regularization
        amr_loss, mean_weight = self.compute_amr_regularization(
            margins, spurious_scores
        )

        # Adaptive regularization strength
        mu = self.compute_mu(self.step)

        # Total loss
        total_loss = ce_loss + mu * amr_loss

        # Backward pass
        optimizer.zero_grad()
        total_loss.backward()

        # Gradient clipping based on spurious scores
        batch_spurious_score = spurious_scores.mean()
        if batch_spurious_score > self.config.tau_s:
            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(),
                self.config.clip_spurious
            )
        else:
            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(),
                self.config.clip_grad_norm
            )

        optimizer.step()

        self.step += 1

        # Return metrics
        return {
            'loss': total_loss.item(),
            'ce_loss': ce_loss.item(),
            'amr_loss': amr_loss.item(),
            'mu': mu,
            'mean_spurious_score': spurious_scores.mean().item(),
            'mean_margin': margins.mean().item(),
            'mean_weight': mean_weight.item()
        }


class BaselineTrainer:
    """Baseline trainer (ERM)"""

    def __init__(self, model, config):
        self.model = model
        self.config = config
        self.device = config.device

    def train_step(self, inputs, targets, groups, optimizer):
        """Standard ERM training step"""
        self.model.train()
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)

        # Forward pass
        logits = self.model(inputs)
        loss = F.cross_entropy(logits, targets)

        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(
            self.model.parameters(),
            self.config.clip_grad_norm
        )
        optimizer.step()

        return {'loss': loss.item()}


class GroupDROTrainer:
    """Group DRO trainer (requires group labels)"""

    def __init__(self, model, config, n_groups):
        self.model = model
        self.config = config
        self.device = config.device
        self.n_groups = n_groups

        # Initialize group weights
        self.group_weights = torch.ones(n_groups, device=self.device) / n_groups
        self.group_losses = torch.zeros(n_groups, device=self.device)
        self.eta = 0.1  # Step size for group weight updates

    def train_step(self, inputs, targets, groups, optimizer):
        """Group DRO training step"""
        self.model.train()
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)
        groups = groups.to(self.device)

        # Forward pass
        logits = self.model(inputs)

        # Compute per-sample losses
        losses = F.cross_entropy(logits, targets, reduction='none')

        # Compute group losses
        group_losses = torch.zeros(self.n_groups, device=self.device)
        group_counts = torch.zeros(self.n_groups, device=self.device)

        for g in range(self.n_groups):
            mask = (groups == g)
            if mask.sum() > 0:
                group_losses[g] = losses[mask].mean()
                group_counts[g] = mask.sum()

        # Update group weights (exponentiated gradient) - detach to avoid backprop issues
        with torch.no_grad():
            self.group_weights = self.group_weights * torch.exp(self.eta * group_losses.detach())
            self.group_weights = self.group_weights / self.group_weights.sum()

        # Compute weighted loss
        loss = (self.group_weights.detach() * group_losses).sum()

        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(
            self.model.parameters(),
            self.config.clip_grad_norm
        )
        optimizer.step()

        return {
            'loss': loss.item(),
            'worst_group_loss': group_losses.max().item()
        }


class JTTTrainer:
    """Just Train Twice (JTT) trainer"""

    def __init__(self, model, config):
        self.model = model
        self.config = config
        self.device = config.device
        self.phase = 1  # Phase 1: identify hard examples, Phase 2: upweight them

        self.misclassified_indices = set()

    def identify_misclassified(self, data_loader):
        """Identify misclassified samples in phase 1"""
        self.model.eval()
        misclassified = []

        with torch.no_grad():
            for batch_idx, (inputs, targets, groups) in enumerate(data_loader):
                inputs = inputs.to(self.device)
                targets = targets.to(self.device)

                logits = self.model(inputs)
                preds = logits.argmax(dim=1)

                # Find misclassified samples
                wrong = (preds != targets)
                for i in range(len(wrong)):
                    if wrong[i]:
                        global_idx = batch_idx * self.config.batch_size + i
                        misclassified.append(global_idx)

        self.misclassified_indices = set(misclassified)
        print(f"Identified {len(self.misclassified_indices)} misclassified samples")

    def train_step(self, inputs, targets, groups, optimizer, indices=None):
        """JTT training step with upweighting"""
        self.model.train()
        inputs = inputs.to(self.device)
        targets = targets.to(self.device)

        # Forward pass
        logits = self.model(inputs)

        # Compute per-sample losses
        losses = F.cross_entropy(logits, targets, reduction='none')

        # In phase 2, upweight misclassified samples
        if self.phase == 2 and indices is not None:
            weights = torch.ones_like(losses)
            for i, idx in enumerate(indices):
                if idx in self.misclassified_indices:
                    weights[i] = 10.0  # Upweight factor

            loss = (weights * losses).mean()
        else:
            loss = losses.mean()

        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(
            self.model.parameters(),
            self.config.clip_grad_norm
        )
        optimizer.step()

        return {'loss': loss.item()}
