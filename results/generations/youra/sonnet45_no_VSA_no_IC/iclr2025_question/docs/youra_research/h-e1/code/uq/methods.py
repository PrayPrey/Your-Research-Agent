"""Uncertainty quantification methods for selective prediction."""
from typing import List
import torch
import torch.nn.functional as F
from scipy.stats import entropy
import numpy as np


class TemperatureScaling:
    """Temperature scaling for logit calibration."""

    def __init__(self):
        """Initialize with default temperature."""
        self.temperature = 1.0

    def calibrate(
        self,
        logits: List[torch.Tensor],
        labels: List[int],
        max_iter: int = 50
    ) -> float:
        """
        Fit temperature parameter via LBFGS.

        Args:
            logits: List of [V] vocabulary logits
            labels: List of binary labels (0=correct, 1=incorrect)
            max_iter: Maximum LBFGS iterations

        Returns:
            Optimal temperature value
        """
        # Stack logits
        logits_tensor = torch.stack(logits)  # [N, V]
        labels_tensor = torch.tensor(labels, dtype=torch.long)

        # Initialize temperature
        temperature = torch.nn.Parameter(torch.ones(1))

        # Optimizer
        optimizer = torch.optim.LBFGS([temperature], lr=0.01, max_iter=max_iter)

        def closure():
            optimizer.zero_grad()
            scaled_logits = logits_tensor / temperature.clamp(min=1e-3)
            loss = F.cross_entropy(scaled_logits, labels_tensor)
            loss.backward()
            return loss

        optimizer.step(closure)

        self.temperature = temperature.item()
        return self.temperature

    def compute_uncertainty(self, logits: torch.Tensor, T: float = None) -> float:
        """
        Compute uncertainty score.

        Args:
            logits: [V] vocabulary logits
            T: Temperature (uses calibrated value if None)

        Returns:
            Uncertainty score (1 - max_prob)
        """
        if T is None:
            T = self.temperature

        probs = F.softmax(logits / T, dim=0)
        uncertainty = 1.0 - probs.max().item()
        return uncertainty


class ConformalPrediction:
    """Conformal prediction via nonconformity scores."""

    def __init__(self, alpha: float = 0.1):
        """
        Initialize conformal prediction.

        Args:
            alpha: Miscoverage rate (default 0.1 for 90% coverage)
        """
        self.alpha = alpha
        self.threshold = 0.0

    def calibrate(
        self,
        logits: List[torch.Tensor],
        labels: List[int]
    ) -> float:
        """
        Compute nonconformity threshold.

        Args:
            logits: List of [V] vocabulary logits
            labels: List of binary labels (unused for threshold computation)

        Returns:
            (1-alpha) quantile of scores
        """
        # Compute nonconformity scores
        scores = []
        for logit in logits:
            probs = F.softmax(logit, dim=0)
            score = 1.0 - probs.max().item()
            scores.append(score)

        # Compute quantile
        self.threshold = float(np.quantile(scores, 1 - self.alpha))
        return self.threshold

    def compute_uncertainty(self, logits: torch.Tensor) -> float:
        """
        Compute uncertainty score.

        Args:
            logits: [V] vocabulary logits

        Returns:
            Nonconformity score (1 - max_prob)
        """
        probs = F.softmax(logits, dim=0)
        uncertainty = 1.0 - probs.max().item()
        return uncertainty


class MCDropout:
    """Monte Carlo dropout for epistemic uncertainty."""

    def __init__(self, k: int = 5, dropout_rate: float = 0.1):
        """
        Initialize MC dropout.

        Args:
            k: Number of forward passes
            dropout_rate: Dropout rate
        """
        self.k = k
        self.dropout_rate = dropout_rate

    def enable_dropout(self, model):
        """
        Enable dropout layers during inference.

        Args:
            model: Model with dropout layers
        """
        model.train()
        for module in model.modules():
            if isinstance(module, torch.nn.Dropout):
                module.p = self.dropout_rate

    def compute_uncertainty(
        self,
        questions: List[str],
        model,
        tokenizer
    ) -> List[float]:
        """
        Compute epistemic uncertainty via MC dropout.

        Args:
            questions: List of question strings
            model: LLM model
            tokenizer: Model tokenizer

        Returns:
            List of uncertainty scores (entropy)
        """
        self.enable_dropout(model)
        uncertainties = []

        for question in questions:
            # Run k forward passes
            predictions = []

            for _ in range(self.k):
                inputs = tokenizer(question, return_tensors="pt").to(model.device)

                with torch.no_grad():
                    outputs = model.generate(
                        **inputs,
                        max_new_tokens=100,
                        return_dict_in_generate=True,
                        output_scores=True
                    )

                # Extract first token logits
                logits = outputs.scores[0][0]  # [V]
                probs = F.softmax(logits, dim=0).cpu().numpy()
                predictions.append(probs)

            # Compute mean prediction
            mean_probs = np.mean(predictions, axis=0)

            # Compute entropy
            uncertainty = entropy(mean_probs)
            uncertainties.append(uncertainty)

        return uncertainties
