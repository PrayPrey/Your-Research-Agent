"""Baseline data mixing strategies for DynaMix comparison.

Implements:
1. Static Uniform Mixing - equal weights for all domains
2. Static Tuned Mixing - manually tuned weights (Llama-2 style)
3. DoReMi-style - upweight domains with higher reference model loss
"""

import logging
import numpy as np
import torch
import torch.nn.functional as F
from config import (DOMAINS, NUM_DOMAINS, STATIC_UNIFORM, STATIC_TUNED,
                    DOREMI_WARMUP_STEPS, DEVICE)

logger = logging.getLogger(__name__)


class BaselineMixer:
    """Base class for data mixing strategies."""

    def __init__(self, name):
        self.name = name
        self.step = 0
        self.mixture_history = []

    def get_weights(self, **kwargs):
        raise NotImplementedError

    def update(self, losses, **kwargs):
        """Update mixer state based on losses (optional)."""
        pass

    def record_mixture(self, weights):
        self.mixture_history.append(weights.copy() if hasattr(weights, 'copy') else list(weights))
        self.step += 1


class UniformMixer(BaselineMixer):
    """Static uniform mixing - equal weights for all domains."""

    def __init__(self):
        super().__init__("Static Uniform")
        self.weights = np.array(STATIC_UNIFORM, dtype=np.float32)

    def get_weights(self, **kwargs):
        self.record_mixture(self.weights)
        return self.weights.copy()


class StaticTunedMixer(BaselineMixer):
    """Static manually-tuned mixing (Llama-2 style proportions)."""

    def __init__(self):
        super().__init__("Static Tuned")
        self.weights = np.array(STATIC_TUNED, dtype=np.float32)

    def get_weights(self, **kwargs):
        self.record_mixture(self.weights)
        return self.weights.copy()


class DoReMiStyleMixer(BaselineMixer):
    """DoReMi-inspired mixing strategy.

    Trains a reference model with uniform weights, then upweights domains
    where the reference model has higher loss (indicating more to learn).
    Reference: Xie et al. 2023 "DoReMi: Optimizing Data Mixtures Speeds Up Language Model Pretraining"

    Simplified version: maintains per-domain exponential moving average of losses
    and adjusts weights proportionally.
    """

    def __init__(self, warmup_steps=DOREMI_WARMUP_STEPS, eta=0.1):
        super().__init__("DoReMi-style")
        self.warmup_steps = warmup_steps
        self.eta = eta  # Learning rate for weight update

        # Initialize with uniform weights
        self.weights = np.ones(NUM_DOMAINS) / NUM_DOMAINS
        self.ref_losses = np.ones(NUM_DOMAINS)  # Reference model losses (EMA)
        self.ema_alpha = 0.1
        self.is_warmed_up = False

    def update_reference_losses(self, domain_losses):
        """Update EMA of per-domain losses."""
        for i, loss in enumerate(domain_losses):
            if loss is not None:
                self.ref_losses[i] = (1 - self.ema_alpha) * self.ref_losses[i] + self.ema_alpha * loss

    def update_weights(self):
        """Update mixture weights based on reference losses.

        DoReMi principle: higher loss domains should get more data.
        """
        # Convert losses to weights: higher loss -> higher weight
        # Use softmax with temperature for smooth weights
        temperature = 0.5
        logits = self.ref_losses / temperature
        self.weights = np.exp(logits - logits.max())
        self.weights /= self.weights.sum()

        # Ensure minimum weight for each domain (0.05)
        min_weight = 0.05
        self.weights = np.maximum(self.weights, min_weight)
        self.weights /= self.weights.sum()

    def get_weights(self, domain_losses=None, **kwargs):
        if domain_losses is not None:
            self.update_reference_losses(domain_losses)
            if self.step >= self.warmup_steps:
                self.update_weights()
                self.is_warmed_up = True

        self.record_mixture(self.weights)
        return self.weights.copy()

    def update(self, losses, **kwargs):
        self.update_reference_losses(losses)
        if self.step >= self.warmup_steps:
            self.update_weights()


class PiKEStyleMixer(BaselineMixer):
    """PiKE-inspired mixing strategy.

    Adapts domain weights based on gradient conflict minimization.
    Simplified: reduces weights for domains with conflicting gradients
    (high variance in gradient directions).

    Reference: Li et al. 2025 "PiKE: Adaptive Data Mixing for Multi-Task Learning"
    """

    def __init__(self, warmup_steps=200, lr=0.05):
        super().__init__("PiKE-style")
        self.warmup_steps = warmup_steps
        self.lr = lr

        # Initialize with uniform weights
        self.log_weights = np.zeros(NUM_DOMAINS)  # Softmax parameterization
        self.weights = np.ones(NUM_DOMAINS) / NUM_DOMAINS
        self.gradient_conflicts = np.zeros(NUM_DOMAINS)
        self.loss_ema = np.ones(NUM_DOMAINS)
        self.ema_alpha = 0.2

    def update_gradient_signals(self, domain_losses, domain_snrs=None):
        """Update gradient conflict estimates from per-domain loss signals."""
        for i, loss in enumerate(domain_losses):
            if loss is not None:
                self.loss_ema[i] = (1 - self.ema_alpha) * self.loss_ema[i] + self.ema_alpha * loss

        if domain_snrs is not None:
            # Higher SNR = less conflict
            for i, snr in enumerate(domain_snrs):
                if snr is not None:
                    self.gradient_conflicts[i] = 1.0 / (snr + 1e-6)

    def update_weights_pike(self):
        """Update weights to reduce gradient conflicts.

        Domains with high gradient conflicts (low SNR) get reduced weight.
        """
        # Score each domain: high loss AND low conflict -> high weight
        loss_score = self.loss_ema / (self.loss_ema.sum() + 1e-8)
        conflict_penalty = self.gradient_conflicts / (self.gradient_conflicts.sum() + 1e-8)

        scores = loss_score - 0.3 * conflict_penalty

        # Gradient ascent on log_weights
        self.log_weights += self.lr * scores

        # Project to simplex via softmax
        log_w = self.log_weights - self.log_weights.max()
        self.weights = np.exp(log_w)
        self.weights /= self.weights.sum()

        # Minimum weight constraint
        min_weight = 0.05
        self.weights = np.maximum(self.weights, min_weight)
        self.weights /= self.weights.sum()

    def get_weights(self, domain_losses=None, domain_snrs=None, **kwargs):
        if domain_losses is not None:
            self.update_gradient_signals(domain_losses, domain_snrs)
            if self.step >= self.warmup_steps:
                self.update_weights_pike()

        self.record_mixture(self.weights)
        return self.weights.copy()

    def update(self, losses, snrs=None, **kwargs):
        self.update_gradient_signals(losses, snrs)
        if self.step >= self.warmup_steps:
            self.update_weights_pike()


def evaluate_model(model, eval_data, device=DEVICE):
    """Evaluate model perplexity on each domain."""
    model.eval()
    domain_losses = {}

    with torch.no_grad():
        for domain, data in eval_data.items():
            data = data.to(device)
            x = data[:, :-1]
            y = data[:, 1:]
            _, loss = model(x, y)
            domain_losses[domain] = loss.item()

    model.train()
    return domain_losses


def compute_perplexity(loss):
    """Convert cross-entropy loss to perplexity."""
    return np.exp(min(loss, 20))  # Cap at exp(20) to avoid inf
