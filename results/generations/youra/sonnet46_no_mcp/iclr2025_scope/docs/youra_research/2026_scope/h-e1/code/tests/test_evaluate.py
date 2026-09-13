"""Tests for evaluate.py — task-011."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import json
import torch
from evaluate import compute_layer_cosine_similarity, evaluate_gate, save_results


def make_state_dict(n_layers=4, rank=16, in_features=64):
    """Create a fake LoRA state dict."""
    sd = {}
    for i in range(n_layers):
        sd[f"base_model.model.layers.{i}.self_attn.q_proj.lora_A.weight"] = \
            torch.randn(rank, in_features)
        sd[f"base_model.model.layers.{i}.self_attn.q_proj.lora_B.weight"] = \
            torch.randn(in_features, rank)
    return sd


def test_cosine_similarity_identical():
    """Identical weights → cosine similarity = 1.0."""
    sd = make_state_dict()
    results = compute_layer_cosine_similarity(sd, sd)
    for k, v in results.items():
        assert abs(v - 1.0) < 1e-5, f"Expected 1.0 for identical weights, got {v} for {k}"


def test_cosine_similarity_different():
    """Different random weights → similarity < 1.0."""
    sd1 = make_state_dict()
    sd2 = make_state_dict()
    results = compute_layer_cosine_similarity(sd1, sd2)
    assert len(results) > 0
    values = list(results.values())
    assert any(v < 0.99 for v in values), "Expected some dissimilarity between random weights"


def test_cosine_similarity_keys_filter():
    """Only lora_A and lora_B keys should appear in results."""
    sd1 = make_state_dict()
    # Add non-LoRA key
    sd1["base_model.model.embed_tokens.weight"] = torch.randn(32000, 64)
    sd2 = dict(sd1)
    results = compute_layer_cosine_similarity(sd1, sd2)
    for k in results:
        assert "lora_A" in k or "lora_B" in k


def test_evaluate_gate_pass():
    """Gate PASS when any layer has cosine similarity < 0.95."""
    results = {
        "layer.0.lora_A": 0.92,  # Below threshold
        "layer.1.lora_A": 0.98,
    }
    gate = evaluate_gate(results, threshold=0.95)
    assert gate["gate_pass"] is True
    assert gate["min_sim"] == 0.92
    assert "layer.0.lora_A" in gate["layers_below_threshold"]


def test_evaluate_gate_fail():
    """Gate FAIL when all cosine similarities >= 0.95."""
    results = {
        "layer.0.lora_A": 0.97,
        "layer.1.lora_A": 0.99,
    }
    gate = evaluate_gate(results, threshold=0.95)
    assert gate["gate_pass"] is False
    assert gate["layers_below_threshold"] == []


def test_evaluate_gate_empty():
    """Empty results → gate FAIL with error."""
    gate = evaluate_gate({}, threshold=0.95)
    assert gate["gate_pass"] is False
    assert "error" in gate


def test_save_results(tmp_path):
    """save_results creates valid JSON file."""
    results = {"gate_pass": True, "min_sim": 0.92}
    path = str(tmp_path / "sub" / "results.json")
    save_results(results, path)
    assert os.path.exists(path)
    with open(path) as f:
        loaded = json.load(f)
    assert loaded["gate_pass"] is True
    assert loaded["min_sim"] == 0.92
