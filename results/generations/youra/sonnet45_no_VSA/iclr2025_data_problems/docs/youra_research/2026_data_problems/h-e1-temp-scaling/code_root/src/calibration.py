"""Temperature scaling calibration for neural network confidence."""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from typing import List, Tuple


class ModelWithTemperature(nn.Module):
    """Wraps model with learnable temperature parameter for calibration."""

    def __init__(self, model: nn.Module = None, init_temperature: float = 1.5):
        """
        Args:
            model: Base Code Llama model (optional, can be None)
            init_temperature: Initial T value (default 1.5)
        """
        super().__init__()
        self.model = model
        self.temperature = nn.Parameter(torch.ones(1) * init_temperature)

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor = None
    ) -> torch.Tensor:
        """
        Forward pass with temperature scaling.

        Args:
            input_ids: [B, L] tokenized input
            attention_mask: [B, L] attention mask

        Returns:
            scaled_logits: [B, L, V] temperature-scaled logits
        """
        if self.model is None:
            raise ValueError("Model not set. Use this wrapper only for logit scaling.")

        logits = self.model(input_ids, attention_mask=attention_mask).logits
        return self.temperature_scale(logits)

    def temperature_scale(self, logits: torch.Tensor) -> torch.Tensor:
        """
        Apply temperature scaling: logits / T

        Args:
            logits: [..., V] raw logits

        Returns:
            scaled: [..., V] scaled logits
        """
        # Broadcasting: temperature is a scalar, divide all logits
        return logits / self.temperature

    def set_temperature(
        self,
        logits_list: List[torch.Tensor],
        labels_list: List[int],
        lr: float = 0.01,
        max_iter: int = 200
    ) -> Tuple[float, List[float]]:
        """
        Optimize temperature using LBFGS.

        Args:
            logits_list: List of [V] logits from calibration set
            labels_list: Binary labels (0/1 correctness)
            lr: LBFGS learning rate
            max_iter: Maximum iterations

        Returns:
            optimal_temperature: Learned T value
            loss_history: NLL loss per iteration
        """
        # Stack all calibration data
        # For binary classification, we need to create 2-class logits
        # logits_list contains final token logits [V], but we need [2] for binary
        # We'll use a simple mapping: take max logit as "correct" score
        logits_2d = []
        for logits in logits_list:
            # Get max logit value as confidence score
            max_logit = logits.max().item()
            # Create binary logits: [incorrect, correct]
            binary_logits = torch.tensor([-max_logit, max_logit])
            logits_2d.append(binary_logits)

        logits = torch.stack(logits_2d)  # [N, 2]
        labels = torch.tensor(labels_list, dtype=torch.long)  # [N]

        # LBFGS optimizer
        optimizer = optim.LBFGS(
            [self.temperature],
            lr=lr,
            max_iter=max_iter,
            line_search_fn='strong_wolfe'
        )

        criterion = nn.CrossEntropyLoss()
        loss_history = []

        # LBFGS closure
        def closure():
            optimizer.zero_grad()
            scaled_logits = self.temperature_scale(logits)
            loss = criterion(scaled_logits, labels)
            loss.backward()
            loss_history.append(loss.item())
            return loss

        # Run optimization
        optimizer.step(closure)

        optimal_temperature = self.temperature.item()
        return optimal_temperature, loss_history

    def get_temperature(self) -> float:
        """Return current temperature value."""
        return self.temperature.item()


class TemperatureScaler:
    """Simplified temperature scaler without nn.Module dependency."""

    def __init__(self, init_temp: float = 1.5):
        """Initialize with temperature parameter."""
        self.temperature = nn.Parameter(torch.ones(1) * init_temp)

    def fit(
        self,
        logits: List[torch.Tensor],
        labels: List[int],
        max_iter: int = 200,
        lr: float = 0.01
    ) -> float:
        """
        Optimize temperature on calibration data.

        Args:
            logits: List of [V] logit tensors
            labels: List of binary labels (0/1)
            max_iter: LBFGS iterations
            lr: Learning rate

        Returns:
            optimal_temp: Learned temperature
        """
        # Convert to binary classification problem
        logits_2d = []
        for logit_vec in logits:
            max_logit = logit_vec.max().item()
            binary_logits = torch.tensor([-max_logit, max_logit])
            logits_2d.append(binary_logits)

        logits_tensor = torch.stack(logits_2d)  # [N, 2]
        labels_tensor = torch.tensor(labels, dtype=torch.long)  # [N]

        # LBFGS optimizer
        optimizer = optim.LBFGS(
            [self.temperature],
            lr=lr,
            max_iter=max_iter,
            line_search_fn='strong_wolfe'
        )

        criterion = nn.CrossEntropyLoss()

        def closure():
            optimizer.zero_grad()
            scaled = logits_tensor / self.temperature
            loss = criterion(scaled, labels_tensor)
            loss.backward()
            return loss

        optimizer.step(closure)
        return self.temperature.item()

    def scale(self, logits: torch.Tensor) -> torch.Tensor:
        """Apply learned temperature to logits."""
        return logits / self.temperature

    def get_temperature(self) -> float:
        """Return current temperature value."""
        return self.temperature.item()
