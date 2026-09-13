"""Metrics evaluator for hypothesis validation."""
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict
import numpy as np


class MetricsEvaluator:
    """Comprehensive metrics computation."""

    def __init__(self, model: nn.Module, val_loader: DataLoader, device: str = "cuda"):
        self.model = model
        self.val_loader = val_loader
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def compute_perplexity(self, n_samples: int = 1000) -> float:
        """Compute perplexity on validation set."""
        self.model.eval()
        total_loss = 0.0
        num_batches = 0

        with torch.no_grad():
            for batch in self.val_loader:
                input_ids = batch['input_ids'].to(self.device)
                labels = batch['labels'].to(self.device)

                outputs = self.model(input_ids=input_ids, labels=labels)
                total_loss += outputs['loss'].item()
                num_batches += 1

                if num_batches * input_ids.size(0) >= n_samples:
                    break

        avg_loss = total_loss / max(num_batches, 1)
        perplexity = torch.exp(torch.tensor(avg_loss)).item()

        return perplexity

    def compute_stable_rank_per_layer(self, n_samples: int = 100) -> Dict[str, float]:
        """Compute stable rank per layer. Returns dict with layer-wise stable ranks."""
        if not hasattr(self.model, 'regularizer'):
            return {}

        self.model.eval()
        layer_stable_ranks = {f"layer_{i}": [] for i in range(12)}  # GPT-2 has 12 layers

        num_batches = 0
        batch_iter = iter(self.val_loader)

        while num_batches < (n_samples // 32):  # Assuming batch_size=32
            try:
                batch = next(batch_iter)
            except StopIteration:
                break

            input_ids = batch['input_ids'].to(self.device)
            labels = batch['labels'].to(self.device)

            # Forward pass with hooks to capture layer I/O
            self.model._register_hooks() if hasattr(self.model, '_register_hooks') else None

            with torch.no_grad():
                _ = self.model(input_ids=input_ids, labels=labels)

            # Compute stable rank for each layer
            if hasattr(self.model, 'layer_outputs') and hasattr(self.model, 'layer_inputs'):
                for idx, (layer_out, layer_in) in enumerate(zip(self.model.layer_outputs, self.model.layer_inputs)):
                    if idx < 12:
                        # Compute stable rank with gradient context for autograd
                        layer_in_copy = layer_in.detach().requires_grad_(True)
                        layer_out_copy = layer_out.detach().requires_grad_(True)

                        sr = self.model.regularizer.compute_stable_rank(layer_out_copy, layer_in_copy)
                        layer_stable_ranks[f"layer_{idx}"].append(sr.item())

            if hasattr(self.model, '_remove_hooks'):
                self.model._remove_hooks()

            num_batches += 1

        # Average across samples
        result = {}
        for layer_name, ranks in layer_stable_ranks.items():
            if len(ranks) > 0:
                result[layer_name] = float(np.mean(ranks))
            else:
                result[layer_name] = 0.0

        return result

    def compute_layer_variance(self, stable_ranks: Dict[str, float]) -> float:
        """Compute coefficient of variation across layers."""
        if not stable_ranks:
            return 0.0

        ranks = list(stable_ranks.values())
        mean_rank = np.mean(ranks)
        std_rank = np.std(ranks)

        if mean_rank > 0:
            cv = std_rank / mean_rank
        else:
            cv = 0.0

        return float(cv)

    def compute_measurement_cv(self, stable_ranks: Dict[str, float], n_repeats: int = 5) -> float:
        """Compute CV for spectral norm estimation (measurement precision)."""
        if not stable_ranks or not hasattr(self.model, 'regularizer'):
            return 0.0

        # Sample one batch and repeat spectral norm estimation
        batch = next(iter(self.val_loader))
        input_ids = batch['input_ids'].to(self.device)
        labels = batch['labels'].to(self.device)

        # Get layer outputs
        if hasattr(self.model, '_register_hooks'):
            self.model._register_hooks()

        with torch.no_grad():
            _ = self.model(input_ids=input_ids, labels=labels)

        spectral_norm_estimates = []

        if hasattr(self.model, 'layer_outputs') and len(self.model.layer_outputs) > 0:
            # Use first layer for CV estimation
            layer_out = self.model.layer_outputs[0].detach().requires_grad_(True)
            layer_in = self.model.layer_inputs[0].detach().requires_grad_(True)

            for _ in range(n_repeats):
                spec_norm = self.model.regularizer.power_iteration_spectral_norm(layer_out, layer_in)
                spectral_norm_estimates.append(spec_norm.item())

        if hasattr(self.model, '_remove_hooks'):
            self.model._remove_hooks()

        if len(spectral_norm_estimates) > 1:
            mean_spec = np.mean(spectral_norm_estimates)
            std_spec = np.std(spectral_norm_estimates)
            cv = std_spec / mean_spec if mean_spec > 0 else 0.0
        else:
            cv = 0.0

        return float(cv)

    def evaluate_all(self) -> Dict:
        """Full evaluation suite."""
        print("Computing perplexity...")
        perplexity = self.compute_perplexity()

        print("Computing stable rank per layer...")
        stable_ranks = self.compute_stable_rank_per_layer()

        print("Computing layer variance...")
        layer_variance = self.compute_layer_variance(stable_ranks)

        print("Computing measurement CV...")
        measurement_cv = self.compute_measurement_cv(stable_ranks)

        # Compute mean stable rank
        mean_stable_rank = np.mean(list(stable_ranks.values())) if stable_ranks else 0.0

        results = {
            'perplexity': perplexity,
            'stable_ranks': stable_ranks,
            'mean_stable_rank': float(mean_stable_rank),
            'layer_variance': layer_variance,
            'measurement_cv': measurement_cv
        }

        return results
