"""Model classes for H-M3: Eigenmode Energy Redistribution via Projection-Only LoRA.

MambaProbe: Ported from H-M2 with added get_model()/get_tokenizer() accessors.
LoRAAdapter: Wraps model with projection-only LoRA via PEFT.
EigenmodeEnergyAnalyzer: NEW - Measures energy distribution across SSM eigenmodes.
"""

import math
from typing import Dict, List, Optional, Tuple

import torch
from torch import Tensor

from config import ExperimentConfig


class MambaProbe:
    """Probe for extracting eigenvalues from Mamba models.

    Ported from H-M2 with added get_model()/get_tokenizer() accessors for LoRA wrapping.
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
        for layer in self.model.backbone.layers:
            A_log = layer.mixer.A_log.detach().float()
            a_logs.append(A_log)

        return a_logs

    def get_model(self):
        """Return loaded model reference for LoRA wrapping."""
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        return self.model

    def get_tokenizer(self):
        """Return tokenizer reference."""
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

    Key requirement: LoRA targets ONLY in_proj and x_proj (projection matrices).
    A_log parameters MUST remain frozen (not trainable).
    """

    def __init__(self, model, config: ExperimentConfig) -> None:
        """Initialize adapter with base model and config."""
        self.base_model = model
        self.config = config
        self.peft_model = None

    def apply(self):
        """Apply LoraConfig to in_proj/x_proj only; return PEFT model."""
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
        """Assert A_log NOT in trainable params; assert proj+lora ARE trainable."""
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
                "MECHANISM VIOLATION: No projection LoRA adapters found."
            )

        print("Mechanism verification PASSED:")
        print("  - A_log parameters: FROZEN (not trainable)")
        print("  - Projection LoRA adapters: TRAINABLE")

        return True


class EigenmodeEnergyAnalyzer:
    """Measures energy distribution across SSM eigenmodes.

    ΔE > 0.1 nats indicates significant redistribution toward slow modes.

    Key insight: While eigenvalues remain fixed (H-M2 proved), the energy
    distribution across eigenmodes can change via projection matrices.
    """

    def __init__(self, model, config: ExperimentConfig) -> None:
        """Initialize analyzer with model and config.

        Args:
            model: PEFT-wrapped or raw Mamba model
            config: Experiment configuration
        """
        self.model = model
        self.config = config
        self.hooks: List = []
        self.hidden_states: List[Tensor] = []

    def register_hooks(self) -> None:
        """Register forward hooks on all layer.mixer modules to capture SSM outputs."""
        self.clear_hooks()  # Clear any existing hooks

        # Access backbone.layers whether raw or PEFT-wrapped
        layers = self.model.backbone.layers

        for layer in layers:
            hook = layer.mixer.register_forward_hook(self._capture_state)
            self.hooks.append(hook)

        print(f"Registered hooks on {len(self.hooks)} layers")

    def clear_hooks(self) -> None:
        """Remove all registered hooks and clear captured hidden_states."""
        for hook in self.hooks:
            hook.remove()
        self.hooks.clear()
        self.hidden_states.clear()
        # Free GPU memory
        torch.cuda.empty_cache()

    def _capture_state(self, module, input, output) -> None:
        """Hook callback: appends output tensor detached to self.hidden_states.

        output shape from layer.mixer: [B, L, d_model] = [B, L, 2048]
        """
        self.hidden_states.append(output.detach().float())

    def get_eigenvalues_per_layer(self) -> List[Tensor]:
        """Compute λ = exp(-exp(A_log)) per layer from frozen A_log.

        Returns: List[Tensor[d_inner, d_state]], len=48
        """
        eigenvalues_list = []
        layers = self.model.backbone.layers

        for layer in layers:
            a_log = layer.mixer.A_log.detach().float()  # [d_inner, d_state]
            eigenvalues = torch.exp(-torch.exp(a_log))  # [d_inner, d_state]
            eigenvalues_list.append(eigenvalues)

        return eigenvalues_list

    def measure_energy(self, model, input_ids: Tensor) -> dict:
        """Run forward pass with hooks; return energy dict.

        Args:
            model: same as self.model (passed for interface clarity)
            input_ids: [B, L] token ids

        Returns:
            {
              'per_layer': List[float],       # slow_fraction per layer (48 values)
              'slow_fraction': float,         # global average slow mode fraction
              'per_layer_total_energy': List[float],
            }
        """
        device = next(model.parameters()).device
        input_ids = input_ids.to(device)

        # Ensure hooks are registered
        if not self.hooks:
            self.register_hooks()

        # Clear previous hidden states
        self.hidden_states.clear()

        # Forward pass to trigger hooks
        with torch.no_grad():
            model(input_ids)

        # Now self.hidden_states has 48 tensors [B, L, d_model]
        layers = self.model.backbone.layers
        per_layer = []
        per_layer_total = []

        for i, layer in enumerate(layers):
            a_log = layer.mixer.A_log.detach().float()  # [d_inner, d_state]
            eigenvalues = torch.exp(-torch.exp(a_log))  # [d_inner, d_state]

            # Identify slow modes: |λ| > threshold
            slow_mask = eigenvalues.abs() > self.config.slow_mode_threshold  # [d_inner, d_state]

            if i < len(self.hidden_states):
                h = self.hidden_states[i]  # [B, L, d_model]
                d_model = h.shape[-1]
                d_inner = a_log.shape[0]  # 4096 for Mamba-1.4B

                # Project hidden to d_inner dim if needed
                # For Mamba-1.4B: d_model=2048, d_inner=4096
                # The mixer output is d_model, but we need to relate to d_inner
                # Use d_model channels as proxy (each channel relates to eigenmodes)
                h_energy = h[..., :min(d_model, d_inner)]  # [B, L, min(d_model, d_inner)]

                # Energy per channel: sum over B and L
                ch_energy = (h_energy ** 2).sum(dim=(0, 1))  # [min(d_model, d_inner)]

                # Map slow_mask to channel dimension
                # slow_mask is [d_inner, d_state], collapse to per-channel
                slow_ch = slow_mask.any(dim=1)[:len(ch_energy)]  # [min(d_model, d_inner)] bool

                slow_energy = ch_energy[slow_ch].sum().item()
                total_energy = ch_energy.sum().item()

                slow_frac = slow_energy / (total_energy + 1e-8)
            else:
                # Fallback: use eigenvalue statistics
                slow_frac = slow_mask.float().mean().item()
                total_energy = 1.0

            per_layer.append(slow_frac)
            per_layer_total.append(total_energy)

        # Clear hidden states to free memory
        self.hidden_states.clear()

        return {
            'per_layer': per_layer,
            'slow_fraction': sum(per_layer) / len(per_layer) if per_layer else 0.0,
            'per_layer_total_energy': per_layer_total,
        }

    def compute_delta_e(self, pre_energy: dict, post_energy: dict) -> dict:
        """Compute ΔE metrics between pre- and post-training energy dicts.

        Args:
            pre_energy: output of measure_energy() before training
            post_energy: output of measure_energy() after training

        Returns:
            {
              'delta_slow_fraction': float,   # post - pre global slow_fraction
              'delta_e_nats': float,          # -log(1 - min(|delta|, 0.99))
              'gate_pass': bool,              # delta_e_nats > threshold
              'per_layer_delta': List[float], # per-layer post - pre slow_fraction
            }
        """
        # Per-layer delta
        per_layer_delta = [
            post_energy['per_layer'][i] - pre_energy['per_layer'][i]
            for i in range(len(pre_energy['per_layer']))
        ]

        # Global delta
        delta_slow_fraction = post_energy['slow_fraction'] - pre_energy['slow_fraction']

        # Convert to nats: -log(1 - min(|delta|, 0.99))
        # This gives higher values for larger energy shifts
        abs_delta = abs(delta_slow_fraction)
        clamped_delta = min(abs_delta, 0.99)
        delta_e_nats = -math.log(1 - clamped_delta) if clamped_delta < 1.0 else float('inf')

        # Gate evaluation
        gate_pass = delta_e_nats > self.config.delta_e_gate_threshold

        return {
            'delta_slow_fraction': delta_slow_fraction,
            'delta_e_nats': delta_e_nats,
            'gate_pass': gate_pass,
            'per_layer_delta': per_layer_delta,
        }
