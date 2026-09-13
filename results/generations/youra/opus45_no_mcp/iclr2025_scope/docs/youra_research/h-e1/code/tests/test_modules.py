"""Basic tests for H-E1 modules"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
from config import BENCHMARKS, LORA_CONFIG_TRANSFORMER, LORA_CONFIG_MAMBA
from model import MambaWithLoRA, verify_mechanism_active
from evaluate import compute_deltas, spearman_correlation, check_gate_conditions


def test_mamba_forward():
    model = MambaWithLoRA(d_model=64, d_state=8, n_layers=2, vocab_size=100)
    x = torch.randint(0, 100, (2, 16))
    out = model(x)
    assert out.logits.shape == (2, 16, 100), f"Expected (2,16,100), got {out.logits.shape}"
    print("✓ MambaWithLoRA forward pass")


def test_mechanism_verification():
    model = MambaWithLoRA(d_model=64, d_state=8, n_layers=2, vocab_size=100)
    x = torch.randint(0, 100, (1, 8))
    assert verify_mechanism_active(model, x) == True
    print("✓ Mechanism verification")


def test_delta_computation():
    t_scores = {"gsm8k": 0.5, "nq": 0.3}
    m_scores = {"gsm8k": 0.48, "nq": 0.1}
    deltas = compute_deltas(t_scores, m_scores)
    assert abs(deltas["gsm8k"] - (-0.02)) < 0.001
    assert abs(deltas["nq"] - (-0.2)) < 0.001
    print("✓ Delta computation")


def test_gate_conditions():
    deltas = {"gsm8k": -0.02, "nq": -0.2, "mmlu": -0.1, "hotpotqa": -0.15}
    gate = check_gate_conditions(deltas, 0.8)
    assert gate["gsm8k_pass"] == True
    assert gate["nq_pass"] == True
    assert gate["correlation_pass"] == True
    assert gate["overall_pass"] == True
    print("✓ Gate conditions")


if __name__ == "__main__":
    test_mamba_forward()
    test_mechanism_verification()
    test_delta_computation()
    test_gate_conditions()
    print("\nAll tests passed!")
