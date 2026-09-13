"""Temperature scaling calibration (Guo et al. 2017)."""
import torch
import torch.nn as nn
import torch.nn.functional as F


class TemperatureScaler:
    """Post-hoc temperature scaling for model calibration."""

    def __init__(self, temperature_bounds=(0.1, 10.0)):
        self.temperature = nn.Parameter(torch.ones(1) * 1.5)
        self.bounds = temperature_bounds

    def fit(self, logits, labels, max_iter=100, lr=0.01):
        """
        Optimize temperature on validation set using LBFGS.

        Args:
            logits: [N, C] uncalibrated logits
            labels: [N] ground truth labels
            max_iter: maximum iterations
            lr: learning rate

        Returns:
            optimized temperature (float)
        """
        logits = logits.detach()
        labels = labels.detach()

        # NLL loss for temperature optimization
        criterion = nn.CrossEntropyLoss()

        # LBFGS optimizer
        optimizer = torch.optim.LBFGS(
            [self.temperature],
            lr=lr,
            max_iter=max_iter
        )

        def closure():
            optimizer.zero_grad()
            scaled_logits = logits / self.temperature
            loss = criterion(scaled_logits, labels)
            loss.backward()

            # Constrain temperature to bounds
            with torch.no_grad():
                self.temperature.data.clamp_(*self.bounds)

            return loss

        # Optimize
        optimizer.step(closure)

        # Constrain final temperature
        with torch.no_grad():
            self.temperature.data.clamp_(*self.bounds)

        return self.temperature.item()

    def calibrate(self, logits, temperature=None):
        """
        Apply temperature scaling to logits.

        Args:
            logits: [N, C] uncalibrated logits
            temperature: scalar T (uses self.temperature if None)

        Returns:
            calibrated_probs: [N, C] = softmax(logits / T)
        """
        if temperature is None:
            temperature = self.temperature.item()

        scaled_logits = logits / temperature
        calibrated_probs = F.softmax(scaled_logits, dim=1)
        return calibrated_probs
