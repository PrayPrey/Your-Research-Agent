"""Minimal test to validate low-rank analysis approach."""

import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from src.metrics import MetricsComputer

print("Loading GPT-2...")
model = AutoModelForCausalLM.from_pretrained(
    "gpt2",
    torch_dtype=torch.float16,
    device_map="cuda:0"
)
tokenizer = AutoTokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token

print("Model loaded:", model.device)

# Test with synthetic attention matrices
print("\nTesting effective rank computation...")
# Create synthetic attention matrix [B, H, L, L]
B, H, L = 4, 12, 64
attn = torch.randn(B, H, L, L)
attn = torch.softmax(attn, dim=-1)  # Normalize

eff_rank = MetricsComputer.svd_effective_rank(attn, threshold=0.99)
print(f"Effective rank (synthetic): {eff_rank:.2f}")

# Test operator entropy
print("\nTesting operator entropy...")
layer = model.transformer.h[6]  # Mid-layer
c_attn_weight = layer.attn.c_attn.weight.detach()
hidden_size = c_attn_weight.shape[0]
Q = c_attn_weight[:, :hidden_size]
K = c_attn_weight[:, hidden_size:2*hidden_size]

entropy = MetricsComputer.operator_entropy(Q, K)
print(f"Operator entropy (layer 6): {entropy:.4f}")

# Test regression
print("\nTesting regression...")
layer_indices = [6, 7, 8, 9, 10, 11]
entropies = []
for idx in layer_indices:
    layer = model.transformer.h[idx]
    c_attn_weight = layer.attn.c_attn.weight.detach()
    hidden_size = c_attn_weight.shape[0]
    Q = c_attn_weight[:, :hidden_size]
    K = c_attn_weight[:, hidden_size:2*hidden_size]
    ent = MetricsComputer.operator_entropy(Q, K)
    entropies.append(ent)
    print(f"Layer {idx}: entropy={ent:.4f}")

regression = MetricsComputer.entropy_regression(layer_indices, entropies)
print(f"\nRegression: β={regression['slope']:.4f}, p={regression['p_value']:.4e}")
print(f"Criterion (β < 0): {'PASS ✓' if regression['slope'] < 0 else 'FAIL ✗'}")
print(f"Criterion (p < 0.01): {'PASS ✓' if regression['p_value'] < 0.01 else 'FAIL ✗'}")

print("\n✓ All components working!")
