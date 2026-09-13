"""GPT-2 models with stable rank regularization."""
import torch
import torch.nn as nn
from transformers import GPT2Config, GPT2LMHeadModel
from typing import Optional, Dict, List


class BaselineGPT2(nn.Module):
    """Standard GPT-2 wrapper."""

    def __init__(self, config: GPT2Config):
        super().__init__()
        self.config = config
        self.model = GPT2LMHeadModel(config)

    def forward(self, input_ids: torch.Tensor, labels: Optional[torch.Tensor] = None) -> Dict:
        """Forward pass. input_ids: [B, L], labels: [B, L]"""
        outputs = self.model(input_ids=input_ids, labels=labels)
        return {
            'loss': outputs.loss,
            'logits': outputs.logits
        }


class StableRankRegularizer(nn.Module):
    """Residual-corrected Jacobian stable rank regularizer."""

    def __init__(self, n_power_iterations: int = 3, n_hutchinson_probes: int = 5,
                 epsilon: float = 1e-12):
        super().__init__()
        self.n_power_iter = n_power_iterations
        self.n_probes = n_hutchinson_probes
        self.eps = epsilon

    def hutchinson_trace(self, layer_output: torch.Tensor, layer_input: torch.Tensor) -> torch.Tensor:
        """Estimate ||J̃_ℓ||_F^2 via Hutchinson trace. layer_output: [B, L, H], layer_input: [B, L, H]"""
        trace_estimates = []
        B, L, H = layer_output.shape

        for probe_idx in range(self.n_probes):
            # Sample Rademacher vector
            v = torch.randint(0, 2, (B, L, H), device=layer_output.device, dtype=layer_output.dtype) * 2.0 - 1.0
            v.requires_grad = False

            # Compute Jv via autograd
            Jv = torch.autograd.grad(
                outputs=layer_output,
                inputs=layer_input,
                grad_outputs=v,
                create_graph=True,
                retain_graph=True,  # Always retain for multiple probes
                allow_unused=True
            )[0]

            if Jv is None:
                continue

            # Residual correction: J̃v = Jv - v
            Jv_res = Jv - v

            # Trace estimate: <v, J̃v>
            trace_est = torch.sum(v * Jv_res)
            trace_estimates.append(trace_est)

        if len(trace_estimates) == 0:
            return torch.tensor(0.0, device=layer_output.device)

        frobenius_norm_sq = torch.mean(torch.stack(trace_estimates))
        return frobenius_norm_sq

    def power_iteration_spectral_norm(self, layer_output: torch.Tensor,
                                     layer_input: torch.Tensor) -> torch.Tensor:
        """Estimate ||J̃_ℓ||_2 via power iteration. layer_output: [B, L, H], layer_input: [B, L, H]"""
        B, L, H = layer_output.shape

        # Initialize random vector
        v = torch.randn(B, L, H, device=layer_output.device, dtype=layer_output.dtype)
        v = v / (torch.norm(v) + self.eps)

        for iter_idx in range(self.n_power_iter):
            # Compute Jv
            Jv = torch.autograd.grad(
                outputs=layer_output,
                inputs=layer_input,
                grad_outputs=v,
                create_graph=True,
                retain_graph=True,
                allow_unused=True
            )[0]

            if Jv is None:
                break

            # Residual correction: J̃v = Jv - v
            Jv_res = Jv - v

            # Compute J̃^T J̃v
            JTJv = torch.autograd.grad(
                outputs=layer_output,
                inputs=layer_input,
                grad_outputs=Jv_res,
                create_graph=True,
                retain_graph=True,
                allow_unused=True
            )[0]

            if JTJv is None:
                break

            # Update v (detach to avoid backprop through power iteration steps)
            v = (JTJv / (torch.norm(JTJv) + self.eps)).detach()

        # Final spectral norm computation
        v_final = v.requires_grad_(False)
        Jv_final = torch.autograd.grad(
            outputs=layer_output,
            inputs=layer_input,
            grad_outputs=v_final,
            create_graph=True,
            retain_graph=True,
            allow_unused=True
        )[0]

        if Jv_final is None:
            return torch.tensor(1.0, device=layer_output.device)

        Jv_res_final = Jv_final - v_final
        spectral_norm = torch.norm(Jv_res_final)

        return spectral_norm

    def compute_stable_rank(self, layer_output: torch.Tensor, layer_input: torch.Tensor) -> torch.Tensor:
        """Compute sr_ℓ^res = ||J̃_ℓ||_F^2 / ||J̃_ℓ||_2^2. layer_output: [B, L, H], layer_input: [B, L, H]"""
        frob_sq = self.hutchinson_trace(layer_output, layer_input)
        spec_norm = self.power_iteration_spectral_norm(layer_output, layer_input)
        stable_rank = frob_sq / (spec_norm ** 2 + self.eps)
        return stable_rank


class RegularizedGPT2(nn.Module):
    """GPT-2 with stable rank regularization."""

    def __init__(self, config: GPT2Config, lambda_reg: float = 0.01,
                 n_power_iter: int = 5, n_hutchinson: int = 10):
        super().__init__()
        self.config = config
        # Disable flash attention to allow second-order derivatives
        config._attn_implementation = "eager"
        self.model = GPT2LMHeadModel(config)
        self.regularizer = StableRankRegularizer(n_power_iter, n_hutchinson)
        self.lambda_reg = lambda_reg

        # Storage for layer I/O
        self.layer_outputs = []
        self.layer_inputs = []
        self.hooks = []

    def _register_hooks(self):
        """Register forward hooks on transformer layers."""
        self.layer_outputs.clear()
        self.layer_inputs.clear()
        self.hooks.clear()

        def make_hook(layer_idx):
            def hook(module, input, output):
                # input is tuple, output is tuple or tensor
                layer_input = input[0] if isinstance(input, tuple) else input
                layer_output = output[0] if isinstance(output, tuple) else output

                # Store and ensure requires_grad
                if layer_input.requires_grad:
                    self.layer_inputs.append(layer_input)
                    self.layer_outputs.append(layer_output)

            return hook

        # Register hooks on all transformer blocks
        for idx, block in enumerate(self.model.transformer.h):
            hook = block.register_forward_hook(make_hook(idx))
            self.hooks.append(hook)

    def _remove_hooks(self):
        """Remove all registered hooks."""
        for hook in self.hooks:
            hook.remove()
        self.hooks.clear()

    def forward(self, input_ids: torch.Tensor, labels: Optional[torch.Tensor] = None) -> Dict:
        """Forward pass with regularization. input_ids: [B, L], labels: [B, L]"""
        # Register hooks
        self._register_hooks()

        # Forward pass
        outputs = self.model(input_ids=input_ids, labels=labels)
        loss_clm = outputs.loss

        # Compute regularization loss
        reg_loss = self.compute_regularization_loss()

        # Total loss
        loss_total = loss_clm + self.lambda_reg * reg_loss

        # Clean up
        self._remove_hooks()
        self.layer_outputs.clear()
        self.layer_inputs.clear()

        return {
            'loss': loss_total,
            'logits': outputs.logits,
            'reg_loss': reg_loss,
            'clm_loss': loss_clm
        }

    def compute_regularization_loss(self) -> torch.Tensor:
        """Compute mean stable rank across layers (sample every 4th layer to save memory)."""
        if len(self.layer_outputs) == 0:
            return torch.tensor(0.0, device=next(self.parameters()).device)

        stable_ranks = []
        # Sample every 4th layer to reduce memory (layers 0, 4, 8)
        for idx, (layer_output, layer_input) in enumerate(zip(self.layer_outputs, self.layer_inputs)):
            if idx % 4 == 0:  # Only compute for 1/4 of layers
                sr = self.regularizer.compute_stable_rank(layer_output, layer_input)
                stable_ranks.append(sr)

        if len(stable_ranks) == 0:
            return torch.tensor(0.0, device=next(self.parameters()).device)

        reg_loss = torch.mean(torch.stack(stable_ranks))
        return reg_loss

    def adaptive_lambda_update(self, current_ppl: float, baseline_ppl: float,
                               tolerance: float = 0.01) -> None:
        """Adjust lambda to maintain perplexity within tolerance."""
        ppl_ratio = current_ppl / baseline_ppl

        if ppl_ratio > (1 + tolerance):
            # Exceeds threshold, reduce regularization
            self.lambda_reg *= 0.95
        elif ppl_ratio < (1 - tolerance):
            # Below threshold, increase regularization
            self.lambda_reg *= 1.05

        # Safety bounds
        self.lambda_reg = max(1e-4, min(1.0, self.lambda_reg))
