"""Model classes for H-M2: Projection-Only LoRA Eigenvalue Preservation.

MambaProbe: Ported from H-M1 with added get_model()/get_tokenizer() accessors.
LoRAAdapter: Wraps model with projection-only LoRA via PEFT.
EigenvaluePreservationValidator: Validates that eigenvalues are preserved after training.
"""

import math
from typing import Dict, List, Optional, Tuple

import torch
from scipy.stats import pearsonr
from torch import Tensor

from config import ExperimentConfig


class MambaProbe:
    """Probe for extracting eigenvalues from Mamba models.

    Ported from H-M1 with added get_model()/get_tokenizer() accessors for LoRA wrapping.
    """

    def __init__(self, config: ExperimentConfig) -> None:
        """Initialize probe with config; model not loaded until load_model()."""
        self.config = config
        self.model = None
        self.tokenizer = None
        self._device = torch.device(config.device)
        self._dtype = torch.float32 if config.dtype == "float32" else torch.float16

    def load_model(self) -> None:
        """Load Mamba model from HuggingFace; moves to device, eval mode."""
        from transformers import AutoModelForCausalLM, AutoTokenizer

        model_id = self.config.model_id
        print(f"Loading model: {model_id}")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.tokenizer_id)

        # Add pad token if missing
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load model via transformers
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=self._dtype,
            device_map="auto",
        )
        self.model.eval()

        # Count layers
        num_layers = len(self.model.backbone.layers)
        print(f"Model loaded with {num_layers} layers")

    def extract_layer_A_log(self) -> List[Tensor]:
        """Return list of A_log tensors, one per layer.

        Returns: list of length num_layers, each tensor shape [d_inner, d_state]
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        a_logs = []
        # Both raw model and PEFT-wrapped model expose backbone.layers directly
        for layer in self.model.backbone.layers:
            A_log = layer.mixer.A_log.detach().float()
            a_logs.append(A_log)

        return a_logs

    def compute_h_spec(self, input_ids: Optional[Tensor] = None) -> float:
        """Compute H_spec from static A weights.

        H_spec = 1/min(exp(A_log)) - time constant of slowest decay mode.

        Args:
            input_ids: unused (A is input-independent)

        Returns:
            H_spec as Python float (in tokens/timesteps)
        """
        a_logs = self.extract_layer_A_log()

        # Find global minimum A_log (slowest decay mode)
        all_a_logs = torch.cat([a.flatten() for a in a_logs])
        min_a_log = all_a_logs.min().item()

        # H_spec = 1 / min(exp(A_log))
        min_exp_a_log = math.exp(min_a_log)
        h_spec = 1.0 / min_exp_a_log

        return h_spec

    def get_per_layer_h_spec(self) -> List[float]:
        """Get H_spec for each layer (based on slowest mode in that layer)."""
        a_logs = self.extract_layer_A_log()
        h_specs = []
        for a_log in a_logs:
            min_exp = math.exp(a_log.min().item())
            h_specs.append(1.0 / min_exp)
        return h_specs

    def get_per_layer_lambda_max(self) -> List[float]:
        """Get the slowest discrete eigenvalue for each layer."""
        a_logs = self.extract_layer_A_log()
        lambdas = []
        for a_log in a_logs:
            min_exp_a = math.exp(a_log.min().item())
            lambda_max = math.exp(-min_exp_a)
            lambdas.append(lambda_max)
        return lambdas

    def get_model(self):
        """Return loaded model reference for LoRA wrapping.

        H-M2 Addition: Required for LoRAAdapter.apply() to wrap model.
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        return self.model

    def get_tokenizer(self):
        """Return tokenizer reference.

        H-M2 Addition: Required for data preprocessing.
        """
        if self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        return self.tokenizer

    def unload(self) -> None:
        """Delete model reference and free GPU memory."""
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        torch.cuda.empty_cache()
        print("Model unloaded and GPU memory cleared")


class LoRAAdapter:
    """Wraps base model with projection-only LoRA via PEFT.

    Key requirement: LoRA targets ONLY in_proj and out_proj (projection matrices).
    A_log parameters MUST remain frozen (not trainable).
    """

    def __init__(self, model, config: ExperimentConfig) -> None:
        """Initialize adapter with base model and config.

        Args:
            model: Raw AutoModelForCausalLM from MambaProbe.get_model()
            config: Experiment configuration with LoRA parameters
        """
        self.base_model = model
        self.config = config
        self.peft_model = None

    def apply(self):
        """Apply LoraConfig to in_proj/out_proj only; return PEFT model.

        Uses PEFT library to wrap model with LoRA adapters on projection matrices.
        A_log and other SSM core parameters remain frozen.

        Returns:
            PEFT-wrapped model ready for training
        """
        from peft import LoraConfig, get_peft_model, TaskType

        lora_config = LoraConfig(
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            target_modules=self.config.lora_target_modules,
            lora_dropout=self.config.lora_dropout,
            bias=self.config.lora_bias,
            task_type=TaskType.CAUSAL_LM,
        )

        self.peft_model = get_peft_model(self.base_model, lora_config)

        print(f"LoRA applied with r={self.config.lora_r}, alpha={self.config.lora_alpha}")
        print(f"Target modules: {self.config.lora_target_modules}")
        self.peft_model.print_trainable_parameters()

        return self.peft_model

    def verify_mechanism(self) -> bool:
        """Assert A_log NOT in trainable params; assert proj+lora ARE trainable.

        This is the core verification for H-M2: projection-only LoRA should NOT
        modify A_log parameters, which control eigenvalues.

        Raises:
            AssertionError: If A_log is trainable or projections are not

        Returns:
            True if verification passes
        """
        if self.peft_model is None:
            raise RuntimeError("LoRA not applied. Call apply() first.")

        trainable_params = [
            name for name, param in self.peft_model.named_parameters()
            if param.requires_grad
        ]

        # Check 1: A_log should NOT be trainable
        a_log_trainable = any('A_log' in name for name in trainable_params)
        if a_log_trainable:
            raise AssertionError(
                "MECHANISM VIOLATION: A_log is trainable! "
                "Projection-only LoRA should NOT modify A_log."
            )

        # Check 2: Projection LoRA adapters SHOULD be trainable
        proj_lora_trainable = any(
            'proj' in name and 'lora' in name
            for name in trainable_params
        )
        if not proj_lora_trainable:
            raise AssertionError(
                "MECHANISM VIOLATION: No projection LoRA adapters found in trainable params. "
                f"Trainable params: {trainable_params[:10]}..."
            )

        print("Mechanism verification PASSED:")
        print("  - A_log parameters: FROZEN (not trainable)")
        print("  - Projection LoRA adapters: TRAINABLE")

        return True

    def get_trainable_param_count(self) -> int:
        """Count of parameters with requires_grad=True."""
        if self.peft_model is None:
            return 0
        return sum(p.numel() for p in self.peft_model.parameters() if p.requires_grad)


class EigenvaluePreservationValidator:
    """Compare pre/post A_log tensors; compute preservation metrics.

    H-M2 Hypothesis: |ΔH_spec| < 10% after projection-only LoRA fine-tuning.
    """

    def __init__(
        self,
        baseline_a_logs: List[Tensor],
        post_a_logs: List[Tensor],
        config: ExperimentConfig,
    ) -> None:
        """Initialize validator with baseline and post-training A_log tensors.

        Args:
            baseline_a_logs: List of A_log tensors before training (len=48)
            post_a_logs: List of A_log tensors after training (len=48)
            config: Experiment configuration with thresholds
        """
        self.baseline_a_logs = baseline_a_logs
        self.post_a_logs = post_a_logs
        self.config = config

        # Pre-compute H_spec values
        self._baseline_h_spec = self._compute_h_spec(baseline_a_logs)
        self._post_h_spec = self._compute_h_spec(post_a_logs)

    def _compute_h_spec(self, a_logs: List[Tensor]) -> float:
        """Compute H_spec from A_log tensors (same formula as H-M1)."""
        all_a = torch.cat([a.float().flatten() for a in a_logs])
        min_a_log = all_a.min().item()
        return 1.0 / math.exp(min_a_log)

    def compute_delta_h_spec(self) -> float:
        """Return |ΔH_spec| as percentage.

        H_spec = 1/min(exp(A_log)) - same formula as H-M1.
        delta = |post - baseline| / baseline * 100

        Returns:
            Percentage change in H_spec
        """
        delta = abs(self._post_h_spec - self._baseline_h_spec) / self._baseline_h_spec * 100
        return delta

    def compute_eigenvalue_correlation(self) -> float:
        """Compute Pearson correlation between flattened pre/post discrete eigenvalues.

        eigenvalue = exp(-exp(A_log)) per element; concatenate all layers.

        Returns:
            Pearson correlation coefficient (should be ~1.0 if preserved)
        """
        # Compute discrete eigenvalues: λ = exp(-exp(A_log))
        baseline_eigenvalues = torch.cat([
            torch.exp(-torch.exp(a.float())).flatten()
            for a in self.baseline_a_logs
        ])
        post_eigenvalues = torch.cat([
            torch.exp(-torch.exp(a.float())).flatten()
            for a in self.post_a_logs
        ])

        # Compute Pearson correlation
        corr, _ = pearsonr(
            baseline_eigenvalues.cpu().numpy(),
            post_eigenvalues.cpu().numpy()
        )
        return float(corr)

    def compute_a_log_max_diff(self) -> float:
        """Return max|A_log_post - A_log_pre| across all layers.

        Expected ~0.0 if A_log is truly frozen.

        Returns:
            Maximum absolute difference
        """
        max_diff = 0.0
        for baseline, post in zip(self.baseline_a_logs, self.post_a_logs):
            diff = torch.abs(post.float() - baseline.float()).max().item()
            max_diff = max(max_diff, diff)
        return max_diff

    def validate(self) -> Dict:
        """Return full metrics dict with hypothesis_pass bool.

        Returns:
            Dictionary with all preservation metrics and pass/fail result
        """
        delta_h_spec = self.compute_delta_h_spec()
        eigenvalue_corr = self.compute_eigenvalue_correlation()
        a_log_max_diff = self.compute_a_log_max_diff()

        # Gate evaluation
        delta_pass = delta_h_spec < self.config.delta_h_spec_threshold
        corr_pass = eigenvalue_corr > self.config.eigenvalue_corr_threshold
        a_log_frozen = a_log_max_diff < 1e-6  # Should be essentially 0

        hypothesis_pass = delta_pass and corr_pass

        return {
            # H_spec metrics
            'baseline_h_spec': self._baseline_h_spec,
            'post_h_spec': self._post_h_spec,
            'delta_h_spec_percent': delta_h_spec,
            # Eigenvalue metrics
            'eigenvalue_correlation': eigenvalue_corr,
            'a_log_max_diff': a_log_max_diff,
            'a_log_frozen': a_log_frozen,
            # Gate results
            'delta_h_spec_pass': delta_pass,
            'eigenvalue_corr_pass': corr_pass,
            'hypothesis_pass': hypothesis_pass,
            # Interpretation
            'interpretation': (
                f"H_spec: {self._baseline_h_spec:.2f} -> {self._post_h_spec:.2f} "
                f"(Δ={delta_h_spec:.4f}%). "
                f"{'PASS' if hypothesis_pass else 'FAIL'}: "
                f"{'Eigenvalues preserved' if hypothesis_pass else 'Eigenvalues modified'}"
            ),
        }
