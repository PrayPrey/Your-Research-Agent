"""
NFT-inspired encoder (Zhou 2023).
Weight rows/cols as tokens → transformer → CLS → scalar.
batch_size=32 required (memory constraint).
"""
import torch
import torch.nn as nn


class NFT(nn.Module):
    def __init__(self, weight_shapes: list, d_model: int = 128, n_heads: int = 4,
                 n_layers: int = 2, max_tokens: int = 512, **kwargs):
        """
        weight_shapes: list of (fan_in, fan_out) for 2D weight matrices.
        Rows and cols of each matrix become tokens.
        """
        super().__init__()
        self.weight_shapes = weight_shapes
        self.d_model = d_model
        self.max_tokens = max_tokens

        # Input projections per layer (row and col separately)
        self.row_projs = nn.ModuleList([nn.Linear(fan_in, d_model) for fan_in, fan_out in weight_shapes])
        self.col_projs = nn.ModuleList([nn.Linear(fan_out, d_model) for fan_in, fan_out in weight_shapes])

        self.cls_token = nn.Parameter(torch.randn(1, 1, d_model) * 0.02)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=n_heads, dim_feedforward=d_model * 2,
            dropout=0.0, batch_first=True, norm_first=True,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        self.head = nn.Linear(d_model, 1)

    def forward(self, weights_flat: torch.Tensor) -> torch.Tensor:
        """weights_flat: [B, D] -> [B]"""
        B = weights_flat.shape[0]
        tokens = [self.cls_token.expand(B, -1, -1)]  # [B, 1, d]

        offset = 0
        total_tokens = 1
        for i, (fan_in, fan_out) in enumerate(self.weight_shapes):
            size = fan_in * fan_out
            w = weights_flat[:, offset:offset + size].reshape(B, fan_in, fan_out)
            # rows: [B, fan_out, fan_in] -> project -> [B, fan_out, d_model]
            row_tok = self.row_projs[i](w.transpose(1, 2))   # [B, fan_out, d]
            # cols: [B, fan_in, fan_out] -> project -> [B, fan_in, d_model]
            col_tok = self.col_projs[i](w)                    # [B, fan_in, d]

            # Subsample if too many tokens
            if total_tokens + fan_out + fan_in > self.max_tokens:
                keep = max(1, (self.max_tokens - total_tokens) // 2)
                row_tok = row_tok[:, :keep, :]
                col_tok = col_tok[:, :keep, :]
                tokens.append(row_tok)
                tokens.append(col_tok)
                total_tokens += 2 * keep
                break
            tokens.append(row_tok)
            tokens.append(col_tok)
            total_tokens += fan_out + fan_in
            offset += size + fan_out  # skip bias

        seq = torch.cat(tokens, dim=1)  # [B, T, d]
        out = self.transformer(seq)     # [B, T, d]
        cls_out = out[:, 0, :]          # [B, d]
        return self.head(cls_out).squeeze(-1)  # [B]
