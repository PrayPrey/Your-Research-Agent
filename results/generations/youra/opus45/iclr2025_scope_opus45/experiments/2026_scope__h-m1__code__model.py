"""MambaProbe and PerplexityEvaluator for H-M1.

MambaProbe: Reused from H-E1 for eigenvalue extraction.
PerplexityEvaluator: New class for measuring perplexity at varying context lengths.

This validates that eigenvalue-derived H_spec predicts actual memory behavior.
"""

import math
from typing import Dict, List, Optional

import torch
import torch.nn.functional as F
from torch import Tensor

from config import ExperimentConfig


class MambaProbe:
    """Probe for extracting eigenvalues from Mamba models (from H-E1)."""

    def __init__(self, config: ExperimentConfig) -> None:
        """Initialize probe with config; model not loaded until load_model()."""
        self.config = config
        self.model = None
        self.tokenizer = None
        self._device = torch.device(config.device)
        self._dtype = torch.float32 if config.dtype == "float32" else torch.float16

    def load_model(self, model_id: str) -> None:
        """Load Mamba model from HuggingFace; moves to device, eval mode."""
        from transformers import AutoModelForCausalLM, AutoTokenizer

        print(f"Loading model: {model_id}")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.tokenizer_id)

        # Load model via transformers (works without mamba-ssm CUDA kernels)
        self.model = AutoModelForCausalLM.from_pretrained(
            f"{model_id}-hf",  # Use HF version
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
            A_log = layer.mixer.A_log.float()
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


class PerplexityEvaluator:
    """Measures perplexity at varying context lengths on Mamba model.

    This class is used to empirically validate that eigenvalue-derived H_spec
    predicts actual perplexity degradation when context is truncated.
    """

    def __init__(
        self,
        model,
        tokenizer,
        device: str = "cuda",
        dtype: str = "float32",
    ) -> None:
        """Initialize evaluator with loaded model and tokenizer."""
        self.model = model
        self.tokenizer = tokenizer
        self.device = torch.device(device)
        self.dtype = torch.float32 if dtype == "float32" else torch.float16

    def compute_perplexity(self, input_ids: Tensor) -> float:
        """Compute perplexity for a batch of sequences.

        Args:
            input_ids: [B, L] input token ids

        Returns:
            Scalar perplexity = exp(mean cross-entropy)
        """
        input_ids = input_ids.to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids)
            logits = outputs.logits  # [B, L, V]

            # Shift for next-token prediction
            shift_logits = logits[:, :-1, :].contiguous()
            shift_labels = input_ids[:, 1:].contiguous()

            # Flatten for cross_entropy
            vocab_size = shift_logits.size(-1)
            loss = F.cross_entropy(
                shift_logits.view(-1, vocab_size),
                shift_labels.view(-1),
                reduction='mean'
            )

            ppl = torch.exp(loss).item()

        return ppl

    def evaluate_at_context_length(
        self,
        sequences: Tensor,
        context_length: int,
        batch_size: int = 4,
    ) -> float:
        """Evaluate mean perplexity with truncated context.

        Args:
            sequences: [N, max_len] full sequences
            context_length: Number of tokens to use as context
            batch_size: Batch size for evaluation

        Returns:
            Mean perplexity across all sequences
        """
        N = sequences.size(0)
        max_len = sequences.size(1)

        # Ensure context_length doesn't exceed sequence length
        context_length = min(context_length, max_len)

        # Truncate to last context_length tokens
        truncated = sequences[:, -context_length:]

        # Compute perplexity in batches
        total_ppl = 0.0
        num_batches = 0

        for i in range(0, N, batch_size):
            batch = truncated[i:i+batch_size]
            ppl = self.compute_perplexity(batch)
            total_ppl += ppl
            num_batches += 1

        mean_ppl = total_ppl / num_batches
        return mean_ppl

    def run_context_sweep(
        self,
        sequences: Tensor,
        context_lengths: List[int],
        batch_size: int = 4,
    ) -> Dict[int, float]:
        """Run perplexity evaluation at multiple context lengths.

        Args:
            sequences: [N, max_len] full sequences
            context_lengths: List of context lengths to evaluate

        Returns:
            Dict mapping context_length -> mean_perplexity
        """
        ppl_curve = {}

        print(f"Running context sweep over {len(context_lengths)} lengths...")
        for ctx_len in context_lengths:
            ppl = self.evaluate_at_context_length(sequences, ctx_len, batch_size)
            ppl_curve[ctx_len] = ppl
            print(f"  Context {ctx_len:4d}: PPL = {ppl:.2f}")

        return ppl_curve

    def compute_degradation_ratio(
        self,
        ppl_curve: Dict[int, float],
        h_spec: float,
    ) -> float:
        """Compute ratio of perplexity below H_spec vs at/above H_spec.

        ratio = mean(PPL where ctx < h_spec) / mean(PPL where ctx >= h_spec)

        If eigenvalues predict memory, this ratio should be > 1.1.

        Args:
            ppl_curve: Dict mapping context_length -> perplexity
            h_spec: Spectral memory horizon

        Returns:
            Degradation ratio (1.0 if either side is empty)
        """
        below_h_spec = [ppl for ctx, ppl in ppl_curve.items() if ctx < h_spec]
        at_or_above = [ppl for ctx, ppl in ppl_curve.items() if ctx >= h_spec]

        if not below_h_spec or not at_or_above:
            return 1.0

        mean_below = sum(below_h_spec) / len(below_h_spec)
        mean_above = sum(at_or_above) / len(at_or_above)

        ratio = mean_below / mean_above
        return ratio
