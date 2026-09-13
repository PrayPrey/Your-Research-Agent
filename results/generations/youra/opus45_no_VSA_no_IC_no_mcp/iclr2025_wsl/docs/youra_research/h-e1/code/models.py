from typing import List, Tuple

import torch
import torch.nn as nn
from torch import Tensor


class FlattenedMLP(nn.Module):
    def __init__(self, input_dim: int, hidden_dims: List[int] = None, num_classes: int = 10, dropout: float = 0.1):
        super().__init__()
        hidden_dims = hidden_dims or [512, 256, 128]

        layers = []
        prev_dim = input_dim
        for h in hidden_dims:
            layers.append(nn.Linear(prev_dim, h))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            prev_dim = h
        layers.append(nn.Linear(prev_dim, num_classes))

        self.net = nn.Sequential(*layers)

    def forward(self, weight_list: List[Tensor]) -> Tensor:
        flat = torch.cat([w.flatten(1) for w in weight_list], dim=1)
        return self.net(flat)


class DWSLayer(nn.Module):
    def __init__(self, weight_shapes: List[Tuple[int, int]], out_channels: int):
        super().__init__()
        self.per_layer_linear = nn.ModuleList([
            nn.Linear(in_c * out_c, out_channels)
            for (in_c, out_c) in weight_shapes
        ])

    def forward(self, weight_list: List[Tensor]) -> Tuple[Tensor, List[Tensor]]:
        feats = []
        for i, w in enumerate(weight_list):
            flat = w.flatten(1)
            f = self.per_layer_linear[i](flat)
            feats.append(f)
        stacked = torch.stack(feats, dim=1)
        agg = stacked.mean(dim=1)
        return agg, feats


class DWSModel(nn.Module):
    def __init__(self, weight_shapes: List[Tuple[int, int]], hidden: int = 128, num_classes: int = 10):
        super().__init__()
        self.dws_layer = DWSLayer(weight_shapes, hidden)
        self.fc1 = nn.Linear(hidden, hidden)
        self.fc2 = nn.Linear(hidden, num_classes)
        self.relu = nn.ReLU()

    def forward(self, weight_list: List[Tensor]) -> Tensor:
        agg, _ = self.dws_layer(weight_list)
        h = self.relu(self.fc1(agg))
        return self.fc2(h)

    def get_layer_activations(self, weight_list: List[Tensor]) -> List[Tensor]:
        with torch.no_grad():
            _, feats = self.dws_layer(weight_list)
        return feats


class WeightTokenizer(nn.Module):
    def __init__(self, weight_shapes: List[Tuple[int, int]], d_model: int):
        super().__init__()
        self.per_layer_linear = nn.ModuleList([
            nn.Linear(in_c * out_c, d_model)
            for (in_c, out_c) in weight_shapes
        ])

    def forward(self, weight_list: List[Tensor]) -> Tensor:
        tokens = []
        for i, w in enumerate(weight_list):
            flat = w.flatten(1)
            t = self.per_layer_linear[i](flat)
            tokens.append(t)
        return torch.stack(tokens, dim=1)


class NFTModel(nn.Module):
    def __init__(
        self,
        weight_shapes: List[Tuple[int, int]],
        d_model: int = 128,
        nhead: int = 4,
        num_layers: int = 2,
        num_classes: int = 10,
    ):
        super().__init__()
        self.tokenizer = WeightTokenizer(weight_shapes, d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            batch_first=True,
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.classifier = nn.Linear(d_model, num_classes)
        self._last_attn_weights = None

    def forward(self, weight_list: List[Tensor]) -> Tensor:
        tokens = self.tokenizer(weight_list)
        enc = self.transformer_encoder(tokens)
        pooled = enc.mean(dim=1)
        return self.classifier(pooled)

    def get_attention_weights(self, weight_list: List[Tensor]) -> Tensor:
        tokens = self.tokenizer(weight_list)
        with torch.no_grad():
            last_layer = self.transformer_encoder.layers[-1]
            _, attn = last_layer.self_attn(
                tokens, tokens, tokens,
                need_weights=True,
                average_attn_weights=False
            )
        return attn
