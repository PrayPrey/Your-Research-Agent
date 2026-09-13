"""Sample script with softmax for metamorphic testing."""

import torch
import torch.nn.functional as F


def attention_mechanism(query, key, value):
    """Simple attention with softmax."""
    d_k = query.size(-1)
    scores = torch.matmul(query, key.transpose(-2, -1)) / (d_k ** 0.5)
    weights = F.softmax(scores, dim=-1)
    output = torch.matmul(weights, value)
    return output


if __name__ == "__main__":
    batch_size = 2
    seq_len = 10
    d_model = 64

    query = torch.randn(batch_size, seq_len, d_model)
    key = torch.randn(batch_size, seq_len, d_model)
    value = torch.randn(batch_size, seq_len, d_model)

    output = attention_mechanism(query, key, value)
    print(f"Output shape: {output.shape}")
    print("Script executed successfully")
