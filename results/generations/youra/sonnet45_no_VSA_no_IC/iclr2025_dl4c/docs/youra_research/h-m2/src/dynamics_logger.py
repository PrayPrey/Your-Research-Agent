"""Training dynamics logger for h-m2."""

import json
import logging
from typing import Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)

class DynamicsLogger:
    """Logs per-batch and per-epoch training dynamics."""

    def __init__(self, output_path: str, experiment_id: str):
        self.output_path = Path(output_path)
        self.experiment_id = experiment_id
        self.data = {
            "experiment_id": experiment_id,
            "feedback_type": None,
            "epochs": []
        }
        self.current_epoch_data = None
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def log_batch(self, metrics: dict) -> None:
        """Log per-batch metrics (step, grad_variance, grad_norm, reward_variance, kl_divergence)."""
        if self.current_epoch_data is None:
            logger.warning("log_batch called before log_epoch. Creating epoch 0.")
            self.current_epoch_data = {"epoch": 0, "batches": [], "eval_metrics": {}}

        required_fields = ["step", "grad_variance", "grad_norm"]
        for field in required_fields:
            if field not in metrics:
                raise ValueError(f"Missing required batch metric: {field}")

        self.current_epoch_data["batches"].append(metrics.copy())

    def log_epoch(self, metrics: dict) -> None:
        """Log per-epoch metrics (epoch, eval_loss, eval_reward_mean, eval_pass@1)."""
        if "epoch" not in metrics:
            raise ValueError("Missing required epoch metric: epoch")

        if self.current_epoch_data is not None:
            self.data["epochs"].append(self.current_epoch_data)

        self.current_epoch_data = {
            "epoch": metrics["epoch"],
            "batches": [],
            "eval_metrics": {k: v for k, v in metrics.items() if k != "epoch"}
        }

        if "feedback_type" in metrics and self.data["feedback_type"] is None:
            self.data["feedback_type"] = metrics["feedback_type"]

        self.save()

    def save(self) -> None:
        """Write JSON to disk (atomic write)."""
        try:
            temp_path = self.output_path.with_suffix(".tmp")
            with open(temp_path, "w") as f:
                json.dump(self.data, f, indent=2)
            temp_path.replace(self.output_path)
        except Exception as e:
            raise IOError(f"Failed to write dynamics log to {self.output_path}: {e}")

    def finalize(self) -> None:
        """Finalize logging (append current epoch if exists)."""
        if self.current_epoch_data is not None and len(self.current_epoch_data["batches"]) > 0:
            self.data["epochs"].append(self.current_epoch_data)
            self.current_epoch_data = None
        self.save()
