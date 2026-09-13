# rci.py - h-m3: RCI Flip Pattern Detector
import torch
from config import CONFIG


class RCIFlipDetector:
    """Detects representational competition via top-token flips across layers."""

    def __init__(self, unembedding_weight, layer_range=None):
        """
        Args:
            unembedding_weight: model.lm_head.weight [vocab_size, hidden_dim]
            layer_range: (start, end) inclusive, default (24, 32)
        """
        self.W = unembedding_weight  # [V, 4096]
        self.layer_range = layer_range or CONFIG["layer_range"]

    def extract_layer_predictions(self, hidden_states, position=-1):
        """
        Project each layer's hidden state to vocabulary space.

        Args:
            hidden_states: tuple of 33 tensors [B, seq, hidden_dim]
            position: token position to analyze (-1 = last token)

        Returns:
            layer_logits: [num_layers, B, vocab_size]
        """
        layer_start, layer_end = self.layer_range
        layer_logits = []

        for layer_idx in range(layer_start, layer_end + 1):
            h = hidden_states[layer_idx][:, position, :]  # [B, hidden_dim]
            # Move to same device as unembedding weight
            h = h.to(self.W.device)
            logits = h @ self.W.T  # [B, vocab_size]
            layer_logits.append(logits)

        return torch.stack(layer_logits)  # [num_layers, B, vocab_size]

    def detect_flip_pattern(self, layer_logits):
        """
        Detect if top-1 token changes between consecutive layers.

        Args:
            layer_logits: [num_layers, B, vocab_size]

        Returns:
            num_flips: [B] count of flips
            flip_positions: [num_layers-1, B] bool tensor
        """
        top_tokens = layer_logits.argmax(dim=-1)  # [num_layers, B]
        flip_positions = top_tokens[:-1] != top_tokens[1:]  # [num_layers-1, B]
        num_flips = flip_positions.sum(dim=0)  # [B]
        return num_flips, flip_positions

    def compute_sample(self, hidden_states, position=-1):
        """
        Compute RCI flip info for a single sample.

        Returns:
            dict with num_flips, has_flip, flip_positions
        """
        layer_logits = self.extract_layer_predictions(hidden_states, position)
        num_flips, flip_positions = self.detect_flip_pattern(layer_logits)

        # Convert to python types (batch_size=1 assumed)
        num_flips_int = num_flips[0].item()
        has_flip = num_flips_int > 0

        # Get flip layer indices (offset by layer_range[0])
        flip_indices = []
        if has_flip:
            flip_mask = flip_positions[:, 0]  # [num_layers-1]
            for i, is_flip in enumerate(flip_mask):
                if is_flip:
                    flip_indices.append(self.layer_range[0] + i)

        return {
            "num_flips": num_flips_int,
            "has_flip": has_flip,
            "flip_positions": flip_indices,
        }
