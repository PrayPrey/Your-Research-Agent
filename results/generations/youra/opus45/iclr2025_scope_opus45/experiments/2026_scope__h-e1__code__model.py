"""MambaProbe: Model loader and eigenvalue extractor for H-E1.

Mamba SSM Eigenvalue Analysis:
- A_log stores log of CONTINUOUS-TIME eigenvalue magnitudes: A_log = log(|a_continuous|)
- The continuous-time SSM: dx/dt = A*x, where A = -exp(A_log) (negative for stability)
- The discrete-time eigenvalue: λ_discrete = exp(Δ * A) = exp(-Δ * exp(A_log))
- For memory horizon, we want the SLOWEST decay mode (largest discrete eigenvalue)
- This corresponds to the SMALLEST continuous eigenvalue magnitude: min(exp(A_log))
- H_spec = -1/log(λ_max_discrete) where λ_max_discrete = exp(-Δ * min(exp(A_log)))
- With Δ=1 as reference: H_spec ≈ 1/min(exp(A_log))
"""

import math
from typing import Optional

import torch
from torch import Tensor

from config import ExperimentConfig


class MambaProbe:
    """Probe for extracting eigenvalues from Mamba models."""

    def __init__(self, config: ExperimentConfig) -> None:
        """Initialize probe with config; model not loaded until load_model()."""
        self.config = config
        self.model = None
        self._device = torch.device(config.device)
        self._dtype = torch.float32 if config.dtype == "float32" else torch.float64

    def load_model(self, model_id: str) -> None:
        """Load MambaLMHeadModel from HuggingFace; moves to device, eval mode."""
        from mamba_ssm.models.mixer_seq_simple import MambaLMHeadModel

        print(f"Loading model: {model_id}")
        self.model = MambaLMHeadModel.from_pretrained(
            model_id,
            dtype=self._dtype,
            device=self._device,
        )
        self.model.eval()
        print(f"Model loaded with {len(self.model.backbone.layers)} layers")

    def extract_layer_A_log(self) -> list[Tensor]:
        """Return list of A_log tensors, one per layer.

        A_log stores log of continuous-time eigenvalue magnitudes.
        Returns: list of length num_layers, each tensor shape [d_inner, d_state]
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        a_logs = []
        for layer in self.model.backbone.layers:
            # A_log shape: [d_inner, d_state] for Mamba-1.4B (e.g., [4096, 16])
            A_log = layer.mixer.A_log.float()
            a_logs.append(A_log)

        return a_logs

    def compute_h_spec(self, input_ids: Optional[Tensor] = None) -> float:
        """Compute H_spec from static A weights.

        The spectral memory horizon H_spec measures how many timesteps information
        can persist in the SSM state. For Mamba:
        - Continuous eigenvalue: a = -exp(A_log) (negative for stability)
        - Discrete eigenvalue (with Δ=1): λ = exp(-exp(A_log))
        - The slowest decay mode has the smallest exp(A_log)
        - H_spec = -1/log(λ_max) = 1/min(exp(A_log))

        Args:
            input_ids: unused (A is input-independent); kept for interface consistency

        Returns:
            H_spec as Python float (in tokens/timesteps)
        """
        a_logs = self.extract_layer_A_log()

        # Find global minimum A_log (slowest decay mode)
        all_a_logs = torch.cat([a.flatten() for a in a_logs])
        min_a_log = all_a_logs.min().item()

        # Smallest continuous eigenvalue magnitude
        min_exp_a_log = math.exp(min_a_log)

        # H_spec = 1 / min(exp(A_log)) = time constant of slowest mode
        # This equals -1/log(λ_max_discrete) when Δ=1
        h_spec = 1.0 / min_exp_a_log

        return h_spec

    def get_per_layer_h_spec(self) -> list[float]:
        """Get H_spec for each layer (based on slowest mode in that layer)."""
        a_logs = self.extract_layer_A_log()
        h_specs = []
        for a_log in a_logs:
            min_exp = math.exp(a_log.min().item())
            h_specs.append(1.0 / min_exp)
        return h_specs

    def get_per_layer_lambda_max(self) -> list[float]:
        """Get the slowest discrete eigenvalue for each layer.

        Returns values closest to 1.0 (slowest decay).
        """
        a_logs = self.extract_layer_A_log()
        lambdas = []
        for a_log in a_logs:
            # λ_max = exp(-min(exp(A_log))) - closest to 1 (slowest decay)
            min_exp_a = math.exp(a_log.min().item())
            lambda_max = math.exp(-min_exp_a)
            lambdas.append(lambda_max)
        return lambdas

    def unload(self) -> None:
        """Delete model reference and free GPU memory."""
        if self.model is not None:
            del self.model
            self.model = None
        torch.cuda.empty_cache()
        print("Model unloaded and GPU memory cleared")

    def unload(self) -> None:
        """Delete model reference and free GPU memory."""
        if self.model is not None:
            del self.model
            self.model = None
        torch.cuda.empty_cache()
        print("Model unloaded and GPU memory cleared")
