import json
import os
from collections import deque
from typing import Any, Dict, List

import torch
from torch import Tensor


class StabilityError(Exception):
    """Raised when NaN detected in loss; halts current seed training."""
    pass


class StabilityMonitor:
    def __init__(
        self,
        seed: int,
        moving_avg_window: int = 100,
        divergence_factor: float = 2.0,
    ) -> None:
        self.seed = seed
        self.moving_avg_window = moving_avg_window
        self.divergence_factor = divergence_factor
        self._loss_deque: deque = deque(maxlen=moving_avg_window)
        self.loss_history: List[float] = []
        self.grad_norm_history: List[Dict] = []
        self.nan_events: int = 0
        self.divergence_events: int = 0

    def update(self, loss: float, step: int) -> None:
        self._loss_deque.append(loss)
        self.loss_history.append(loss)

    def check_nan(self, loss: Tensor) -> bool:
        if torch.isnan(loss):
            self.nan_events += 1
            return True
        return False

    def check_divergence(self, loss: float) -> bool:
        if len(self._loss_deque) < 2:
            return False
        avg = self.get_moving_average()
        if avg > 0 and loss > self.divergence_factor * avg:
            self.divergence_events += 1
            return True
        return False

    def record_grad_norms(self, step: int, lora_norm: float, locret_norm: float) -> None:
        self.grad_norm_history.append({
            "step": step,
            "lora_norm": lora_norm,
            "locret_norm": locret_norm,
        })

    def get_moving_average(self) -> float:
        if not self._loss_deque:
            return 0.0
        return sum(self._loss_deque) / len(self._loss_deque)

    def is_stable(self) -> bool:
        return self.nan_events == 0 and self.divergence_events == 0

    def get_report(self) -> Dict[str, Any]:
        return {
            "seed": self.seed,
            "nan_events": self.nan_events,
            "divergence_events": self.divergence_events,
            "final_loss": self.loss_history[-1] if self.loss_history else None,
            "loss_history": self.loss_history,
            "grad_norm_history": self.grad_norm_history,
        }

    def save_report(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.get_report(), f, indent=2)
