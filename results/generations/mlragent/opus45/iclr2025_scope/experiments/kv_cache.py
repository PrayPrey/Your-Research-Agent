"""
KV Cache compression implementations including QARP and baselines.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple, List, Dict
import math


class RelevancePredictorNetwork(nn.Module):
    """
    Relevance Predictor Network (RPN) that scores KV entries based on
    learned query prototypes.
    """
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 128,
        num_layers: int = 2,
        num_query_prototypes: int = 16,
        recency_bias_alpha: float = 1.0,
    ):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_query_prototypes = num_query_prototypes
        self.recency_bias_alpha = nn.Parameter(torch.tensor(recency_bias_alpha))

        # Input projection
        self.input_proj = nn.Linear(input_dim, hidden_dim)

        # Transformer layers for RPN
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim,
            nhead=4,
            dim_feedforward=hidden_dim * 4,
            dropout=0.1,
            activation='gelu',
            batch_first=True,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        # Query prototypes - learned representations of canonical query patterns
        self.query_prototypes = nn.Parameter(torch.randn(num_query_prototypes, hidden_dim))

        # Output projection for relevance scores
        self.output_proj = nn.Linear(hidden_dim, 1)

    def forward(
        self,
        kv_representations: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Compute relevance scores for KV entries.

        Args:
            kv_representations: (batch, seq_len, input_dim) - pooled KV representations
            attention_mask: (batch, seq_len) - mask for valid positions

        Returns:
            relevance_scores: (batch, seq_len) - importance scores for each position
        """
        batch_size, seq_len, _ = kv_representations.shape

        # Project to hidden dimension
        h = self.input_proj(kv_representations)  # (batch, seq_len, hidden_dim)

        # Apply transformer
        if attention_mask is not None:
            # Ensure attention_mask matches seq_len
            mask_seq_len = attention_mask.shape[-1]
            if mask_seq_len != seq_len:
                # Resize mask to match seq_len
                if mask_seq_len > seq_len:
                    attention_mask = attention_mask[:, :seq_len]
                else:
                    # Pad mask with ones (valid positions)
                    padding = torch.ones(batch_size, seq_len - mask_seq_len, device=attention_mask.device, dtype=attention_mask.dtype)
                    attention_mask = torch.cat([attention_mask, padding], dim=1)

            # Convert to key padding mask (True = masked)
            key_padding_mask = ~attention_mask.bool()
        else:
            key_padding_mask = None

        h = self.transformer(h, src_key_padding_mask=key_padding_mask)

        # Compute relevance against query prototypes
        # Normalize for cosine similarity
        h_norm = F.normalize(h, dim=-1)  # (batch, seq_len, hidden_dim)
        q_norm = F.normalize(self.query_prototypes, dim=-1)  # (num_prototypes, hidden_dim)

        # Compute similarity to all prototypes and take max
        similarities = torch.einsum('bsh,ph->bsp', h_norm, q_norm)  # (batch, seq_len, num_prototypes)
        prototype_scores = similarities.max(dim=-1).values  # (batch, seq_len)

        # Add recency bias
        positions = torch.arange(seq_len, device=kv_representations.device).float()
        recency_bias = torch.exp(-self.recency_bias_alpha * (seq_len - 1 - positions) / seq_len)
        recency_bias = recency_bias.unsqueeze(0).expand(batch_size, -1)

        # Combine prototype scores with recency bias
        relevance_scores = prototype_scores + 0.1 * recency_bias

        if attention_mask is not None:
            relevance_scores = relevance_scores.masked_fill(~attention_mask.bool(), float('-inf'))

        return relevance_scores


class AdaptiveRetentionPolicy:
    """
    Implements budget-constrained optimization over compression operations.
    """
    def __init__(
        self,
        compression_ratio: float = 4.0,
        quant_bits: int = 4,
        merge_window: int = 4,
    ):
        self.compression_ratio = compression_ratio
        self.quant_bits = quant_bits
        self.merge_window = merge_window

        # Compression operation costs (relative to full retention)
        self.costs = {
            'full': 1.0,
            'quant': quant_bits / 16,  # Relative to FP16
            'merge': 1 / merge_window,
            'evict': 0.0,
        }

        # Fidelity scores (information preservation)
        self.fidelity = {
            'full': 1.0,
            'quant': 0.9,
            'merge': 0.7,
            'evict': 0.0,
        }

    def compute_policy(
        self,
        relevance_scores: torch.Tensor,
        budget_ratio: float = None,
    ) -> Dict[str, torch.Tensor]:
        """
        Compute compression policy assignments based on relevance scores.

        Args:
            relevance_scores: (batch, seq_len) - importance scores
            budget_ratio: Memory budget as fraction of original (default: 1/compression_ratio)

        Returns:
            Dictionary with policy assignments and masks
        """
        if budget_ratio is None:
            budget_ratio = 1.0 / self.compression_ratio

        batch_size, seq_len = relevance_scores.shape
        device = relevance_scores.device

        # Initialize policy assignments
        policy = torch.zeros(batch_size, seq_len, dtype=torch.long, device=device)
        # 0=evict, 1=merge, 2=quant, 3=full

        # Compute budget
        budget = int(seq_len * budget_ratio)

        for b in range(batch_size):
            scores = relevance_scores[b]
            valid_mask = scores != float('-inf')
            valid_indices = torch.where(valid_mask)[0]

            if len(valid_indices) == 0:
                continue

            valid_scores = scores[valid_indices]

            # Sort by score (descending)
            sorted_indices = torch.argsort(valid_scores, descending=True)

            # Greedy assignment based on budget
            current_cost = 0.0
            num_full = max(1, int(budget * 0.3))  # 30% full retention
            num_quant = max(1, int(budget * 0.4))  # 40% quantized
            num_merge = max(1, int(budget * 0.2))  # 20% merged

            for i, idx in enumerate(sorted_indices):
                original_idx = valid_indices[idx]
                if i < num_full:
                    policy[b, original_idx] = 3  # full
                elif i < num_full + num_quant:
                    policy[b, original_idx] = 2  # quant
                elif i < num_full + num_quant + num_merge:
                    policy[b, original_idx] = 1  # merge
                # else: evict (default 0)

        # Create masks for each operation
        masks = {
            'full': policy == 3,
            'quant': policy == 2,
            'merge': policy == 1,
            'evict': policy == 0,
            'retain': policy > 0,  # All non-evicted
        }

        return {'policy': policy, 'masks': masks}


class QARPKVCache:
    """
    Query-Aware Retention Policy KV Cache.
    Implements adaptive compression based on predicted relevance.
    """
    def __init__(
        self,
        rpn: RelevancePredictorNetwork,
        compression_ratio: float = 4.0,
        calibration_momentum: float = 0.9,
        calibration_lr: float = 0.1,
    ):
        self.rpn = rpn
        self.compression_ratio = compression_ratio
        self.policy = AdaptiveRetentionPolicy(compression_ratio=compression_ratio)

        # Continual calibration parameters
        self.calibration_momentum = calibration_momentum
        self.calibration_lr = calibration_lr
        self.prediction_errors = None

    def compress(
        self,
        keys: torch.Tensor,
        values: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor, Dict]:
        """
        Compress KV cache using QARP.

        Args:
            keys: (num_layers, batch, num_heads, seq_len, head_dim) OR (batch, num_heads, seq_len, head_dim)
            values: same shape as keys
            attention_mask: (batch, seq_len)

        Returns:
            compressed_keys, compressed_values, metadata
        """
        # Handle both shapes: (num_layers, batch, num_heads, seq_len, head_dim) and (batch, num_heads, seq_len, head_dim)
        if keys.dim() == 5:
            # Stack format: (num_layers, batch, num_heads, seq_len, head_dim)
            num_layers, batch_size, num_heads, seq_len, head_dim = keys.shape
            # Average across layers for pooling
            keys_pooled = keys.mean(dim=0)  # (batch, num_heads, seq_len, head_dim)
            values_pooled = values.mean(dim=0)
        else:
            # Single layer format: (batch, num_heads, seq_len, head_dim)
            batch_size, num_heads, seq_len, head_dim = keys.shape
            keys_pooled = keys
            values_pooled = values

        # Pool KV representations across heads for RPN input
        # Average keys and values, then concatenate
        kv_pooled = torch.cat([
            keys_pooled.mean(dim=1),  # (batch, seq_len, head_dim)
            values_pooled.mean(dim=1),
        ], dim=-1).float()  # (batch, seq_len, 2*head_dim), convert to float32

        # Ensure RPN input dimension matches
        expected_dim = self.rpn.input_proj.in_features
        actual_dim = kv_pooled.shape[-1]

        if actual_dim != expected_dim:
            # Project to expected dimension or pad/truncate
            if actual_dim < expected_dim:
                # Pad with zeros
                padding = torch.zeros(batch_size, seq_len, expected_dim - actual_dim, device=kv_pooled.device)
                kv_pooled = torch.cat([kv_pooled, padding], dim=-1)
            else:
                # Truncate
                kv_pooled = kv_pooled[:, :, :expected_dim]

        # Get relevance scores from RPN
        if attention_mask is not None:
            attention_mask_float = attention_mask.float()
        else:
            attention_mask_float = None

        with torch.no_grad():
            relevance_scores = self.rpn(kv_pooled, attention_mask_float)

        # Compute policy
        policy_result = self.policy.compute_policy(relevance_scores)
        retain_mask = policy_result['masks']['retain']

        # Apply compression by selecting retained positions
        max_retained = 0
        for b in range(batch_size):
            retained_idx = torch.where(retain_mask[b])[0]
            max_retained = max(max_retained, len(retained_idx))

        # Ensure we have at least one position
        max_retained = max(max_retained, 1)

        if keys.dim() == 5:
            # Handle (num_layers, batch, num_heads, seq_len, head_dim) format
            num_layers = keys.shape[0]
            compressed_keys_list = []
            compressed_values_list = []

            for layer_idx in range(num_layers):
                layer_k_list = []
                layer_v_list = []

                for b in range(batch_size):
                    retained_idx = torch.where(retain_mask[b])[0]
                    if len(retained_idx) == 0:
                        retained_idx = torch.tensor([0], device=keys.device)  # Keep at least one

                    k_compressed = keys[layer_idx, b, :, retained_idx, :]
                    v_compressed = values[layer_idx, b, :, retained_idx, :]

                    # Pad if necessary
                    pad_len = max_retained - len(retained_idx)
                    if pad_len > 0:
                        k_pad = torch.zeros(num_heads, pad_len, head_dim, device=keys.device, dtype=keys.dtype)
                        v_pad = torch.zeros(num_heads, pad_len, head_dim, device=values.device, dtype=values.dtype)
                        k_compressed = torch.cat([k_compressed, k_pad], dim=1)
                        v_compressed = torch.cat([v_compressed, v_pad], dim=1)

                    layer_k_list.append(k_compressed)
                    layer_v_list.append(v_compressed)

                compressed_keys_list.append(torch.stack(layer_k_list, dim=0))
                compressed_values_list.append(torch.stack(layer_v_list, dim=0))

            compressed_keys = torch.stack(compressed_keys_list, dim=0)
            compressed_values = torch.stack(compressed_values_list, dim=0)
        else:
            # Handle (batch, num_heads, seq_len, head_dim) format
            compressed_keys_list = []
            compressed_values_list = []

            for b in range(batch_size):
                retained_idx = torch.where(retain_mask[b])[0]
                if len(retained_idx) == 0:
                    retained_idx = torch.tensor([0], device=keys.device)

                k_compressed = keys[b, :, retained_idx, :]
                v_compressed = values[b, :, retained_idx, :]

                pad_len = max_retained - len(retained_idx)
                if pad_len > 0:
                    k_pad = torch.zeros(num_heads, pad_len, head_dim, device=keys.device, dtype=keys.dtype)
                    v_pad = torch.zeros(num_heads, pad_len, head_dim, device=values.device, dtype=values.dtype)
                    k_compressed = torch.cat([k_compressed, k_pad], dim=1)
                    v_compressed = torch.cat([v_compressed, v_pad], dim=1)

                compressed_keys_list.append(k_compressed)
                compressed_values_list.append(v_compressed)

            compressed_keys = torch.stack(compressed_keys_list, dim=0)
            compressed_values = torch.stack(compressed_values_list, dim=0)

        metadata = {
            'relevance_scores': relevance_scores,
            'policy': policy_result['policy'],
            'compression_ratio': seq_len / max_retained if max_retained > 0 else float('inf'),
            'retained_positions': max_retained,
            'original_positions': seq_len,
        }

        return compressed_keys, compressed_values, metadata

    def calibrate(
        self,
        actual_attention: torch.Tensor,
        predicted_relevance: torch.Tensor,
    ):
        """
        Update relevance predictions based on actual attention patterns.
        Implements continual calibration.
        """
        # Compute prediction error
        actual_importance = actual_attention.mean(dim=1)  # Average across heads
        error = actual_importance - F.softmax(predicted_relevance, dim=-1)

        if self.prediction_errors is None:
            self.prediction_errors = error
        else:
            # Exponential moving average
            self.prediction_errors = (
                self.calibration_momentum * self.prediction_errors +
                (1 - self.calibration_momentum) * error
            )


class StreamingLLMCache:
    """
    Baseline: StreamingLLM approach.
    Keeps attention sinks (initial tokens) + recent window.
    """
    def __init__(self, sink_size: int = 4, window_size: int = 256):
        self.sink_size = sink_size
        self.window_size = window_size

    def compress(
        self,
        keys: torch.Tensor,
        values: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor, Dict]:
        # Handle both 4D (batch, heads, seq_len, head_dim) and 5D (layers, batch, heads, seq_len, head_dim)
        if keys.dim() == 5:
            num_layers, batch_size, num_heads, seq_len, head_dim = keys.shape
            is_5d = True
        else:
            batch_size, num_heads, seq_len, head_dim = keys.shape
            is_5d = False

        if seq_len <= self.sink_size + self.window_size:
            return keys, values, {'compression_ratio': 1.0}

        if is_5d:
            # Keep sink tokens and recent window across all layers
            sink_keys = keys[:, :, :, :self.sink_size, :]
            sink_values = values[:, :, :, :self.sink_size, :]
            recent_keys = keys[:, :, :, -self.window_size:, :]
            recent_values = values[:, :, :, -self.window_size:, :]

            compressed_keys = torch.cat([sink_keys, recent_keys], dim=3)
            compressed_values = torch.cat([sink_values, recent_values], dim=3)
        else:
            # Keep sink tokens and recent window
            sink_keys = keys[:, :, :self.sink_size, :]
            sink_values = values[:, :, :self.sink_size, :]
            recent_keys = keys[:, :, -self.window_size:, :]
            recent_values = values[:, :, -self.window_size:, :]

            compressed_keys = torch.cat([sink_keys, recent_keys], dim=2)
            compressed_values = torch.cat([sink_values, recent_values], dim=2)

        retained = self.sink_size + self.window_size
        metadata = {
            'compression_ratio': seq_len / retained,
            'retained_positions': retained,
            'original_positions': seq_len,
        }

        return compressed_keys, compressed_values, metadata


class H2OCache:
    """
    Baseline: Heavy Hitter Oracle (H2O).
    Retains tokens with highest cumulative attention scores.
    """
    def __init__(self, retention_ratio: float = 0.25):
        self.retention_ratio = retention_ratio

    def compress(
        self,
        keys: torch.Tensor,
        values: torch.Tensor,
        cumulative_attention: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor, Dict]:
        # Handle both 4D (batch, heads, seq_len, head_dim) and 5D (layers, batch, heads, seq_len, head_dim)
        if keys.dim() == 5:
            num_layers, batch_size, num_heads, seq_len, head_dim = keys.shape
            is_5d = True
        else:
            batch_size, num_heads, seq_len, head_dim = keys.shape
            is_5d = False

        # Average attention across heads
        importance = cumulative_attention.mean(dim=1)  # (batch, seq_len)

        # Select top-k positions
        k = max(1, int(seq_len * self.retention_ratio))

        if is_5d:
            compressed_keys_layers = []
            compressed_values_layers = []

            for layer_idx in range(num_layers):
                compressed_keys_list = []
                compressed_values_list = []

                for b in range(batch_size):
                    top_indices = torch.topk(importance[b], k=k).indices
                    top_indices = top_indices.sort().values

                    compressed_keys_list.append(keys[layer_idx, b, :, top_indices, :])
                    compressed_values_list.append(values[layer_idx, b, :, top_indices, :])

                compressed_keys_layers.append(torch.stack(compressed_keys_list, dim=0))
                compressed_values_layers.append(torch.stack(compressed_values_list, dim=0))

            compressed_keys = torch.stack(compressed_keys_layers, dim=0)
            compressed_values = torch.stack(compressed_values_layers, dim=0)
        else:
            compressed_keys_list = []
            compressed_values_list = []

            for b in range(batch_size):
                top_indices = torch.topk(importance[b], k=k).indices
                top_indices = top_indices.sort().values  # Maintain order

                compressed_keys_list.append(keys[b, :, top_indices, :])
                compressed_values_list.append(values[b, :, top_indices, :])

            compressed_keys = torch.stack(compressed_keys_list, dim=0)
            compressed_values = torch.stack(compressed_values_list, dim=0)

        metadata = {
            'compression_ratio': seq_len / k,
            'retained_positions': k,
            'original_positions': seq_len,
        }

        return compressed_keys, compressed_values, metadata


class UniformQuantizationCache:
    """
    Baseline: Uniform quantization of KV cache.
    """
    def __init__(self, bits: int = 4):
        self.bits = bits
        self.scale = 2 ** (bits - 1) - 1

    def compress(
        self,
        keys: torch.Tensor,
        values: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor, Dict]:
        """Simulates quantization effect."""
        # Compute scale factors
        k_max = keys.abs().max(dim=-1, keepdim=True).values.clamp(min=1e-8)
        v_max = values.abs().max(dim=-1, keepdim=True).values.clamp(min=1e-8)

        # Quantize and dequantize
        k_quant = torch.round(keys / k_max * self.scale).clamp(-self.scale, self.scale)
        v_quant = torch.round(values / v_max * self.scale).clamp(-self.scale, self.scale)

        compressed_keys = k_quant / self.scale * k_max
        compressed_values = v_quant / self.scale * v_max

        metadata = {
            'compression_ratio': 16 / self.bits,  # FP16 to N-bit
            'bits': self.bits,
            'quantization_error_keys': (keys - compressed_keys).abs().mean().item(),
            'quantization_error_values': (values - compressed_values).abs().mean().item(),
        }

        return compressed_keys, compressed_values, metadata
