"""Low-rank analyzer module for attention structure analysis."""

from typing import Dict, List, Any, Optional, Tuple
import torch
from torch import Tensor, nn
from torch.utils.data import DataLoader
from transformers import AutoModelForCausalLM
from .metrics import MetricsComputer


class LowRankAnalyzer:
    """Analyze low-rank structure in Transformer attention layers."""

    def __init__(
        self,
        model: AutoModelForCausalLM,
        target_layers: range,
        variance_threshold: float = 0.99,
    ):
        """Initialize analyzer with model and configuration.

        Args:
            model: LLaMA model for analysis
            target_layers: Range of layer indices to analyze (e.g., range(20, 32))
            variance_threshold: Variance threshold for effective rank (default 0.99)
        """
        self.model = model
        self.target_layers = target_layers
        self.variance_threshold = variance_threshold
        self.attention_cache: Dict[int, List[Tensor]] = {
            i: [] for i in target_layers
        }
        self.hooks: List = []
        self.metrics_computer = MetricsComputer()

    def register_hooks(self) -> None:
        """Register forward hooks on target layers to capture attention outputs."""
        # Detect model architecture
        if hasattr(self.model, 'model') and hasattr(self.model.model, 'layers'):
            # LLaMA architecture
            layers_list = self.model.model.layers
            attn_module_name = 'self_attn'
        elif hasattr(self.model, 'transformer') and hasattr(self.model.transformer, 'h'):
            # GPT-2 architecture
            layers_list = self.model.transformer.h
            attn_module_name = 'attn'
        else:
            raise ValueError(f"Unsupported model architecture: {type(self.model)}")

        for layer_idx in self.target_layers:
            layer = layers_list[layer_idx]
            attn_module = getattr(layer, attn_module_name)

            # Create closure to capture layer_idx
            def make_hook(idx):
                def hook(module, input, output):
                    self._capture_attention(idx, module, input, output)

                return hook

            handle = attn_module.register_forward_hook(make_hook(layer_idx))
            self.hooks.append(handle)

    def clear_hooks(self) -> None:
        """Remove all registered hooks."""
        for hook in self.hooks:
            hook.remove()
        self.hooks.clear()

    def _capture_attention(
        self,
        layer_idx: int,
        module: nn.Module,
        input: Tuple[Tensor],
        output: Tensor,
    ) -> None:
        """Hook callback to cache attention outputs.

        Args:
            layer_idx: Index of the layer
            module: The attention module
            input: Input tensors
            output: Output tensor from attention (may include attention weights)
        """
        # Both LLaMA and GPT-2 attention return tuple
        # (hidden_states, attention_weights, ...) or (hidden_states, present, attention_weights)
        if isinstance(output, tuple):
            # GPT-2: output is (a, present) or (a, present, attention_weights) when output_attentions=True
            # Try to find attention weights
            attn_weights = None
            for item in output:
                if isinstance(item, torch.Tensor) and item.dim() == 4:
                    # Likely attention weights [B, H, L, L]
                    attn_weights = item
                    break

            if attn_weights is not None:
                self.attention_cache[layer_idx].append(attn_weights.detach().cpu())

    def compute_effective_rank(
        self, attention_matrix: Tensor, threshold: Optional[float] = None
    ) -> float:
        """Compute effective rank via SVD.

        Args:
            attention_matrix: Attention weights [B, H, L, L] or [B*H, L, L]
            threshold: Variance threshold (uses self.variance_threshold if None)

        Returns:
            Average effective rank across samples
        """
        if threshold is None:
            threshold = self.variance_threshold

        return self.metrics_computer.svd_effective_rank(attention_matrix, threshold)

    def compute_operator_entropy(self, layer_idx: int) -> float:
        """Compute operator entropy from Q/K projection weights.

        Args:
            layer_idx: Index of the layer

        Returns:
            Operator entropy value
        """
        # Detect model architecture
        if hasattr(self.model, 'model') and hasattr(self.model.model, 'layers'):
            # LLaMA architecture
            layer = self.model.model.layers[layer_idx]
            Q = layer.self_attn.q_proj.weight.detach()
            K = layer.self_attn.k_proj.weight.detach()
        elif hasattr(self.model, 'transformer') and hasattr(self.model.transformer, 'h'):
            # GPT-2 architecture
            layer = self.model.transformer.h[layer_idx]
            # GPT-2 uses c_attn which combines Q, K, V
            # Shape: [hidden_size, 3*hidden_size]
            c_attn_weight = layer.attn.c_attn.weight.detach()
            hidden_size = c_attn_weight.shape[0]
            # Split into Q, K, V (columns)
            Q = c_attn_weight[:, :hidden_size]  # [D, D]
            K = c_attn_weight[:, hidden_size:2*hidden_size]  # [D, D]
        else:
            raise ValueError(f"Unsupported model architecture")

        return self.metrics_computer.operator_entropy(Q, K)

    def analyze_layers(
        self, dataloader: DataLoader, num_samples: int = 100
    ) -> Dict[str, Any]:
        """Run full analysis pipeline.

        Args:
            dataloader: DataLoader yielding input batches
            num_samples: Number of batches to process

        Returns:
            Dictionary with results per layer: {layer_idx: {effective_rank, operator_entropy, singular_values}}
        """
        # Clear cache
        for layer_idx in self.target_layers:
            self.attention_cache[layer_idx].clear()

        # Register hooks
        self.register_hooks()

        # Process batches
        self.model.eval()
        with torch.no_grad():
            for batch_idx, batch in enumerate(dataloader):
                if batch_idx >= num_samples:
                    break

                # Move to device
                input_ids = batch["input_ids"].to(self.model.device)
                attention_mask = batch["attention_mask"].to(self.model.device)

                # Forward pass (hooks capture attention automatically)
                # Need output_attentions=True to get attention weights
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    output_attentions=True,
                )

                # Clear GPU cache periodically
                if batch_idx % 10 == 0:
                    torch.cuda.empty_cache()

        # Clear hooks
        self.clear_hooks()

        # Analyze each layer
        results = {}
        for layer_idx in self.target_layers:
            if len(self.attention_cache[layer_idx]) == 0:
                print(f"Warning: No attention captured for layer {layer_idx}")
                continue

            # Stack attention matrices
            attention_stack = torch.cat(self.attention_cache[layer_idx], dim=0)

            # Compute effective rank
            eff_rank = self.compute_effective_rank(attention_stack)

            # Compute operator entropy
            entropy = self.compute_operator_entropy(layer_idx)

            # Store singular values for visualization
            if attention_stack.dim() == 4:
                B, H, L, _ = attention_stack.shape
                attention_flat = attention_stack.reshape(B * H, L, L)
            else:
                attention_flat = attention_stack

            # Convert to float32 for SVD
            attention_flat = attention_flat.float()
            _, S, _ = torch.linalg.svd(attention_flat)

            results[layer_idx] = {
                "effective_rank": eff_rank,
                "operator_entropy": entropy,
                "singular_values": S.cpu(),
            }

            print(
                f"Layer {layer_idx}: rank={eff_rank:.2f}, entropy={entropy:.4f}"
            )

        return results
