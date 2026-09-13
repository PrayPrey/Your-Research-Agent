"""
Simplified architecture-specific tokenizers for CAWE model.
Fixed projection layers to avoid dynamic creation and device issues.
"""
import torch
import torch.nn as nn
from typing import Dict


class CNNTokenizer(nn.Module):
    """Tokenizer for CNN models - simplified version with fixed projections."""

    def __init__(self, token_dim: int = 128):
        super().__init__()
        self.token_dim = token_dim
        # Use a single fixed-size projection for all layers
        self.projection = nn.Linear(512, token_dim)  # Fixed input size

    def forward(self, state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Extract CNN weights and project to token sequence."""
        # Extract convolutional layer weights
        conv_layers = []
        for key, param in state_dict.items():
            if 'conv' in key.lower() and 'weight' in key and param.dim() == 4:
                # Flatten kernel and pool to fixed size
                flattened = param.flatten()
                # Adaptive pooling to fixed size
                if flattened.shape[0] >= 512:
                    layer_repr = flattened[:512]
                else:
                    # Pad if smaller
                    layer_repr = torch.nn.functional.pad(flattened, (0, 512 - flattened.shape[0]))
                conv_layers.append(layer_repr)

        if not conv_layers:
            return torch.zeros(1, self.token_dim, device=next(self.parameters()).device)

        # Stack and project
        stacked = torch.stack(conv_layers)  # (num_layers, 512)
        tokens = self.projection(stacked)  # (num_layers, token_dim)
        return tokens


class TransformerTokenizer(nn.Module):
    """Tokenizer for Transformer models - simplified version."""

    def __init__(self, token_dim: int = 128):
        super().__init__()
        self.token_dim = token_dim
        self.projection = nn.Linear(512, token_dim)

    def forward(self, state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Extract Transformer weights and project to token sequence."""
        attn_layers = []
        for key, param in state_dict.items():
            if ('attn' in key.lower() or 'attention' in key.lower()) and 'weight' in key and param.dim() == 2:
                flattened = param.flatten()
                if flattened.shape[0] >= 512:
                    layer_repr = flattened[:512]
                else:
                    layer_repr = torch.nn.functional.pad(flattened, (0, 512 - flattened.shape[0]))
                attn_layers.append(layer_repr)

        if not attn_layers:
            return torch.zeros(1, self.token_dim, device=next(self.parameters()).device)

        stacked = torch.stack(attn_layers)
        tokens = self.projection(stacked)
        return tokens


class MLPTokenizer(nn.Module):
    """Tokenizer for MLP models - simplified version."""

    def __init__(self, token_dim: int = 128):
        super().__init__()
        self.token_dim = token_dim
        self.projection = nn.Linear(512, token_dim)

    def forward(self, state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Extract MLP weights and project to token sequence."""
        fc_layers = []
        for key, param in state_dict.items():
            if ('fc' in key.lower() or 'linear' in key.lower() or 'weight' in key) and param.dim() == 2:
                flattened = param.flatten()
                if flattened.shape[0] >= 512:
                    layer_repr = flattened[:512]
                else:
                    layer_repr = torch.nn.functional.pad(flattened, (0, 512 - flattened.shape[0]))
                fc_layers.append(layer_repr)

        if not fc_layers:
            return torch.zeros(1, self.token_dim, device=next(self.parameters()).device)

        stacked = torch.stack(fc_layers)
        tokens = self.projection(stacked)
        return tokens
