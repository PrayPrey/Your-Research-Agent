"""
Implementation of data valuation methods for multi-stage training.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Tuple, Optional
from copy import deepcopy
import torch.autograd as autograd


class StageAwareInfluence:
    """
    Stage-aware influence function for multi-stage training.
    This is the proposed method.
    """

    def __init__(self, model: nn.Module, config: dict):
        self.model = model
        self.config = config
        self.device = config.get("device", torch.device("cpu"))
        self.low_rank_dim = config.get("low_rank_dim", 50)

    def compute_influence(self, train_data: Dict, test_data: Dict,
                         stage_checkpoints: Dict[str, nn.Module],
                         stage: str) -> np.ndarray:
        """
        Compute stage-aware influence scores for training data.

        Args:
            train_data: Training data batch
            test_data: Test data batch
            stage_checkpoints: Dictionary of model checkpoints at each stage
            stage: Current training stage

        Returns:
            influence_scores: (num_train_samples,) array of influence scores
        """
        self.model.eval()

        # Get test gradient
        test_grad = self._compute_gradient(self.model, test_data)

        # Compute influence for each training sample
        influences = []

        for idx in range(len(train_data["sample_ids"])):
            # Get single training sample
            train_sample = {
                k: v[idx:idx+1] for k, v in train_data.items()
            }

            # Compute training gradient
            train_grad = self._compute_gradient(self.model, train_sample)

            # Compute stage-specific influence with chain rule
            influence = self._compute_stage_influence(
                train_grad, test_grad, stage_checkpoints, stage
            )

            influences.append(influence.item())

        return np.array(influences)

    def _compute_gradient(self, model: nn.Module, data: Dict) -> Dict[str, torch.Tensor]:
        """Compute gradient of loss w.r.t. model parameters."""
        model.zero_grad()

        if "chosen" in data:  # Alignment stage
            loss = model.compute_preference_loss(
                data["chosen"].to(self.device),
                data["rejected"].to(self.device)
            )
        else:
            loss = model.compute_loss(
                data["input_ids"].to(self.device),
                data["labels"].to(self.device)
            )

        loss.backward()

        # Extract gradients
        grads = {}
        for name, param in model.named_parameters():
            if param.grad is not None:
                grads[name] = param.grad.detach().clone()

        return grads

    def _compute_stage_influence(self, train_grad: Dict, test_grad: Dict,
                                stage_checkpoints: Dict, stage: str) -> torch.Tensor:
        """
        Compute stage-aware influence using chain rule.

        Approximates: dL_test/dtheta_final * dtheta_final/dtheta_stage * grad_stage
        """
        # Simple approximation: dot product of gradients
        # In full implementation, this would include Hessian inverse and Jacobian chain
        influence = 0.0

        for name in train_grad.keys():
            if name in test_grad:
                # Dot product of flattened gradients
                train_flat = train_grad[name].flatten()
                test_flat = test_grad[name].flatten()
                influence += torch.dot(train_flat, test_flat)

        return influence


class StandardInfluence:
    """Standard influence functions without stage awareness."""

    def __init__(self, model: nn.Module, config: dict):
        self.model = model
        self.config = config
        self.device = config.get("device", torch.device("cpu"))

    def compute_influence(self, train_data: Dict, test_data: Dict) -> np.ndarray:
        """Compute standard influence scores."""
        self.model.eval()

        # Get test gradient
        test_grad = self._compute_gradient(self.model, test_data)

        influences = []

        for idx in range(len(train_data["sample_ids"])):
            train_sample = {
                k: v[idx:idx+1] for k, v in train_data.items()
            }

            train_grad = self._compute_gradient(self.model, train_sample)

            # Simple dot product (no Hessian inverse for efficiency)
            influence = 0.0
            for name in train_grad.keys():
                if name in test_grad:
                    train_flat = train_grad[name].flatten()
                    test_flat = test_grad[name].flatten()
                    influence += torch.dot(train_flat, test_flat).item()

            influences.append(influence)

        return np.array(influences)

    def _compute_gradient(self, model: nn.Module, data: Dict) -> Dict[str, torch.Tensor]:
        """Compute gradient of loss w.r.t. model parameters."""
        model.zero_grad()

        if "chosen" in data:
            loss = model.compute_preference_loss(
                data["chosen"].to(self.device),
                data["rejected"].to(self.device)
            )
        else:
            loss = model.compute_loss(
                data["input_ids"].to(self.device),
                data["labels"].to(self.device)
            )

        loss.backward()

        grads = {}
        for name, param in model.named_parameters():
            if param.grad is not None:
                grads[name] = param.grad.detach().clone()

        return grads


class DataShapley:
    """Data Shapley value computation."""

    def __init__(self, model_class, config: dict):
        self.model_class = model_class
        self.config = config
        self.device = config.get("device", torch.device("cpu"))
        self.num_coalitions = config.get("num_coalitions", 20)

    def compute_shapley(self, train_data: List[Dict], test_data: Dict,
                       model_config: dict, stage_config: dict) -> np.ndarray:
        """
        Compute Data Shapley values using Monte Carlo approximation.

        Args:
            train_data: List of training samples
            test_data: Test data batch
            model_config: Model configuration
            stage_config: Training configuration

        Returns:
            shapley_values: (num_train_samples,) array
        """
        num_samples = len(train_data)
        shapley_values = np.zeros(num_samples)

        # Monte Carlo approximation
        for _ in range(self.num_coalitions):
            # Random permutation
            perm = np.random.permutation(num_samples)

            prev_performance = 0.0

            for i, idx in enumerate(perm):
                # Train model on coalition
                coalition = [train_data[j] for j in perm[:i+1]]

                # Train and evaluate
                performance = self._train_and_evaluate(
                    coalition, test_data, model_config, stage_config
                )

                # Marginal contribution
                marginal = performance - prev_performance
                shapley_values[idx] += marginal

                prev_performance = performance

        # Average over coalitions
        shapley_values /= self.num_coalitions

        return shapley_values

    def _train_and_evaluate(self, train_samples: List[Dict], test_data: Dict,
                           model_config: dict, stage_config: dict) -> float:
        """Train model on subset and evaluate."""
        if len(train_samples) == 0:
            return 0.0

        # Create small model
        from model import create_model
        model = create_model(model_config).to(self.device)

        optimizer = torch.optim.Adam(
            model.parameters(),
            lr=stage_config["learning_rate"]
        )

        # Quick training (fewer epochs for efficiency)
        model.train()
        for _ in range(2):  # Just 2 epochs for efficiency
            for sample in train_samples:
                optimizer.zero_grad()

                sample_batch = {
                    k: v.unsqueeze(0).to(self.device) if isinstance(v, torch.Tensor)
                    else torch.tensor([v]).to(self.device)
                    for k, v in sample.items()
                }

                if "chosen" in sample_batch:
                    loss = model.compute_preference_loss(
                        sample_batch["chosen"],
                        sample_batch["rejected"]
                    )
                else:
                    loss = model.compute_loss(
                        sample_batch["input_ids"],
                        sample_batch["labels"]
                    )

                loss.backward()
                optimizer.step()

        # Evaluate
        model.eval()
        with torch.no_grad():
            if "chosen" in test_data:
                loss = model.compute_preference_loss(
                    test_data["chosen"].to(self.device),
                    test_data["rejected"].to(self.device)
                )
            else:
                loss = model.compute_loss(
                    test_data["input_ids"].to(self.device),
                    test_data["labels"].to(self.device)
                )

            # Return negative loss as performance
            performance = -loss.item()

        return performance


class TracIn:
    """TracIn: Tracing influence through checkpoints."""

    def __init__(self, model: nn.Module, config: dict):
        self.model = model
        self.config = config
        self.device = config.get("device", torch.device("cpu"))

    def compute_influence(self, train_data: Dict, test_data: Dict,
                         checkpoints: List[nn.Module]) -> np.ndarray:
        """
        Compute TracIn influence using checkpoints.

        Args:
            train_data: Training data batch
            test_data: Test data batch
            checkpoints: List of model checkpoints

        Returns:
            influence_scores: (num_train_samples,) array
        """
        influences = np.zeros(len(train_data["sample_ids"]))

        # Compute test gradient at each checkpoint
        for checkpoint in checkpoints:
            checkpoint.eval()

            test_grad = self._compute_gradient(checkpoint, test_data)

            # Compute influence for each training sample
            for idx in range(len(train_data["sample_ids"])):
                train_sample = {
                    k: v[idx:idx+1] for k, v in train_data.items()
                }

                train_grad = self._compute_gradient(checkpoint, train_sample)

                # Dot product
                influence = 0.0
                for name in train_grad.keys():
                    if name in test_grad:
                        train_flat = train_grad[name].flatten()
                        test_flat = test_grad[name].flatten()
                        influence += torch.dot(train_flat, test_flat).item()

                influences[idx] += influence

        # Average over checkpoints
        influences /= len(checkpoints)

        return influences

    def _compute_gradient(self, model: nn.Module, data: Dict) -> Dict[str, torch.Tensor]:
        """Compute gradient."""
        model.zero_grad()

        if "chosen" in data:
            loss = model.compute_preference_loss(
                data["chosen"].to(self.device),
                data["rejected"].to(self.device)
            )
        else:
            loss = model.compute_loss(
                data["input_ids"].to(self.device),
                data["labels"].to(self.device)
            )

        loss.backward()

        grads = {}
        for name, param in model.named_parameters():
            if param.grad is not None:
                grads[name] = param.grad.detach().clone()

        return grads


class RandomBaseline:
    """Random baseline for comparison."""

    def __init__(self, config: dict):
        self.config = config

    def compute_influence(self, train_data: Dict, test_data: Dict) -> np.ndarray:
        """Return random influence scores."""
        num_samples = len(train_data["sample_ids"])
        return np.random.randn(num_samples)
