"""
Architecture-specific tokenizers for CAWE model.
Converts architecture-specific weights to fixed-dimensional token sequences.
"""
import torch
import torch.nn as nn
from typing import Dict, List


class CNNTokenizer(nn.Module):
    """Tokenizer for CNN models - extracts and projects convolutional layer weights."""

    def __init__(self, token_dim: int = 128):
        super().__init__()
        self.token_dim = token_dim
        # Projection layers will be created dynamically based on input dimensions
        self.projections = nn.ModuleDict()

    def forward(self, state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
        """
        Extract CNN weights and project to token sequence.

        Args:
            state_dict: Model state dictionary containing weights

        Returns:
            tokens: (num_layers, token_dim) tensor
        """
        # Extract convolutional layer weights
        conv_layers = []
        for key, param in state_dict.items():
            if 'conv' in key.lower() and 'weight' in key and param.dim() == 4:
                # Flatten kernel: [out_ch, in_ch, kh, kw] -> [out_ch, in_ch*kh*kw]
                out_ch, in_ch, kh, kw = param.shape
                flattened = param.reshape(out_ch, in_ch * kh * kw)
                # Take mean over output channels to get fixed size
                layer_repr = flattened.mean(dim=0)  # [in_ch*kh*kw]
                conv_layers.append(layer_repr)

        if not conv_layers:
            # Fallback: create dummy token if no conv layers found
            return torch.zeros(1, self.token_dim)

        # Project each layer to token_dim
        tokens = []
        for i, layer_repr in enumerate(conv_layers):
            proj_key = f"proj_{i}"
            if proj_key not in self.projections:
                # Create projection layer on-the-fly
                self.projections[proj_key] = nn.Linear(layer_repr.shape[0], self.token_dim)
            # Move projection to same device as input
            self.projections[proj_key] = self.projections[proj_key].to(layer_repr.device)
            token = self.projections[proj_key](layer_repr)
            tokens.append(token)

        return torch.stack(tokens)  # (num_layers, token_dim)


class TransformerTokenizer(nn.Module):
    """Tokenizer for Transformer models - extracts and projects attention layer weights."""

    def __init__(self, token_dim: int = 128):
        super().__init__()
        self.token_dim = token_dim
        self.projections = nn.ModuleDict()

    def forward(self, state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
        """
        Extract Transformer weights and project to token sequence.

        Args:
            state_dict: Model state dictionary containing weights

        Returns:
            tokens: (num_layers, token_dim) tensor
        """
        # Extract attention layer weights (Q/K/V matrices)
        attn_layers = []
        for key, param in state_dict.items():
            if ('attn' in key.lower() or 'attention' in key.lower()) and 'weight' in key and param.dim() == 2:
                # Take mean over one dimension to get fixed size
                layer_repr = param.mean(dim=0)
                attn_layers.append(layer_repr)

        if not attn_layers:
            # Fallback: create dummy token if no attention layers found
            return torch.zeros(1, self.token_dim)

        # Project each layer to token_dim
        tokens = []
        for i, layer_repr in enumerate(attn_layers):
            proj_key = f"proj_{i}"
            if proj_key not in self.projections:
                self.projections[proj_key] = nn.Linear(layer_repr.shape[0], self.token_dim)
            self.projections[proj_key] = self.projections[proj_key].to(layer_repr.device)
            token = self.projections[proj_key](layer_repr)
            tokens.append(token)

        return torch.stack(tokens)  # (num_layers, token_dim)


class MLPTokenizer(nn.Module):
    """Tokenizer for MLP models - extracts and projects fully-connected layer weights."""

    def __init__(self, token_dim: int = 128):
        super().__init__()
        self.token_dim = token_dim
        self.projections = nn.ModuleDict()

    def forward(self, state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
        """
        Extract MLP weights and project to token sequence.

        Args:
            state_dict: Model state dictionary containing weights

        Returns:
            tokens: (num_layers, token_dim) tensor
        """
        # Extract FC layer weights
        fc_layers = []
        for key, param in state_dict.items():
            if ('fc' in key.lower() or 'linear' in key.lower()) and 'weight' in key and param.dim() == 2:
                # Take mean over one dimension to get fixed size
                layer_repr = param.mean(dim=0)
                fc_layers.append(layer_repr)

        if not fc_layers:
            # Fallback: create dummy token if no FC layers found
            return torch.zeros(1, self.token_dim)

        # Project each layer to token_dim
        tokens = []
        for i, layer_repr in enumerate(fc_layers):
            proj_key = f"proj_{i}"
            if proj_key not in self.projections:
                self.projections[proj_key] = nn.Linear(layer_repr.shape[0], self.token_dim)
            self.projections[proj_key] = self.projections[proj_key].to(layer_repr.device)
            token = self.projections[proj_key](layer_repr)
            tokens.append(token)

        return torch.stack(tokens)  # (num_layers, token_dim)
