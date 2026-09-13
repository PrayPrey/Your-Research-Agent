"""
model.py — Adapter model loading and attention extraction for H-M1.

Loads pre-trained LoRA adapters from H-E1, injects H2O wrappers for eviction-aware
inference, and extracts per-layer attention entropy and heavy-hitter concentration.
"""
from __future__ import annotations

import os
import sys
import logging
from typing import List, Tuple

import torch
import torch.nn as nn
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

_H_E1_CODE = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "../../h-e1/code")
)

import importlib.util as _ilu
_h_e1_model_spec = _ilu.spec_from_file_location(
    "h_e1_model",
    os.path.join(_H_E1_CODE, "model.py"),
)
_h_e1_model = _ilu.module_from_spec(_h_e1_model_spec)
_h_e1_model_spec.loader.exec_module(_h_e1_model)
H2OEvictionAwareAttention = _h_e1_model.H2OEvictionAwareAttention
inject_h2o_wrappers = _h_e1_model.inject_h2o_wrappers
load_base_model = _h_e1_model.load_base_model

logger = logging.getLogger(__name__)


def load_adapter_model(
    model_name: str,
    adapter_checkpoint: str,
    condition: str,
    kv_budget_ratio: float = 0.5,
    fp16: bool = True,
) -> nn.Module:
    """Load base model + PEFT adapter; inject H2O wrappers for eviction condition.

    Args:
        model_name: HuggingFace model ID
        adapter_checkpoint: path to directory with adapter_model.safetensors/bin
        condition: "eviction-aware" injects H2O wrappers; "baseline" does not
        kv_budget_ratio: KV budget ratio for H2O eviction
        fp16: unused (dtype determined by load_base_model)

    Returns:
        PeftModel in eval mode
    """
    if not os.path.isdir(adapter_checkpoint):
        raise FileNotFoundError(
            f"Adapter checkpoint not found: {adapter_checkpoint}. "
            "Run H-E1 experiment first to generate adapter weights."
        )

    logger.info(f"Loading base model: {model_name} (condition={condition})")
    base_model = load_base_model(model_name)
    # Switch to eager attention so output_attentions=True works (sdpa doesn't support it)
    try:
        base_model.config._attn_implementation = "eager"
    except Exception:
        pass

    if condition == "eviction-aware":
        logger.info(f"Injecting H2O wrappers (kv_budget_ratio={kv_budget_ratio})")
        base_model = inject_h2o_wrappers(base_model, kv_budget_ratio)

    logger.info(f"Loading PEFT adapter from: {adapter_checkpoint}")
    model = PeftModel.from_pretrained(base_model, adapter_checkpoint)
    model.eval()
    return model


def set_h2o_training_mode(model: nn.Module, train_mode: bool) -> None:
    """Toggle H2OEvictionAwareAttention wrappers to train/eval mode.

    H2OEvictionAwareAttention.forward() only applies eviction when self.training=True.
    Call with train_mode=True before extract_metrics() to activate eviction mask,
    then False afterward to restore eval mode.
    """
    for module in model.modules():
        if isinstance(module, H2OEvictionAwareAttention):
            if train_mode:
                module.train()
            else:
                module.eval()


class AttentionAnalysisExtractor:
    """Extract per-layer attention entropy and heavy-hitter concentration."""

    def __init__(self, model: nn.Module, top_ratio: float = 0.2):
        self.model = model
        self.top_ratio = top_ratio

    def verify_attention_extraction(
        self,
        tokenizer,
        device: str,
        max_length: int = 512,
    ) -> None:
        """Smoke test: verify output_attentions=True shapes and softmax normalization."""
        dummy_text = "Hello world " * 50
        tokens = tokenizer(
            dummy_text,
            return_tensors="pt",
            max_length=max_length,
            truncation=True,
        )
        input_ids = tokens["input_ids"].to(device)
        attention_mask = tokens["attention_mask"].to(device)

        set_h2o_training_mode(self.model, True)
        with torch.no_grad():
            out = self.model(
                input_ids,
                attention_mask=attention_mask,
                output_attentions=True,
            )
        set_h2o_training_mode(self.model, False)

        attentions = out.attentions
        assert attentions is not None, "output_attentions=True returned None attentions"
        assert len(attentions) > 0, "No attention layers returned"

        for i, attn in enumerate(attentions):
            assert attn.dim() == 4, f"Layer {i}: expected 4D tensor, got {attn.dim()}D"
            # Causal models: rows with all-zero attended tokens sum to 0; only check attended rows
            row_sums = attn.sum(dim=-1)
            attended = row_sums > 0.5
            if attended.any():
                assert torch.allclose(
                    row_sums[attended], torch.ones_like(row_sums[attended]), atol=1e-2
                ), f"Layer {i}: attention rows don't sum to 1"
            assert not torch.isnan(attn).any(), f"Layer {i}: NaN in attention weights"

        logger.info(
            f"Attention extraction verified: {len(attentions)} layers, "
            f"shape={attentions[0].shape}"
        )

    def extract_metrics(
        self,
        input_ids: torch.Tensor,       # [1, seq_len]
        attention_mask: torch.Tensor,  # [1, seq_len]
    ) -> Tuple[List[float], List[float]]:
        """Run forward pass with H2O eviction active; compute per-layer entropy and HH.

        Returns: (entropy_per_layer, hh_concentration_per_layer)
        Each list has length == num_hidden_layers.
        """
        set_h2o_training_mode(self.model, True)
        try:
            with torch.no_grad():
                out = self.model(
                    input_ids,
                    attention_mask=attention_mask,
                    output_attentions=True,
                )
        finally:
            set_h2o_training_mode(self.model, False)

        attentions = out.attentions  # tuple of [1, H, S, S]
        entropy_per_layer: List[float] = []
        hh_per_layer: List[float] = []

        for layer_attn in attentions:
            entropy_per_layer.append(self.compute_entropy(layer_attn))
            hh_per_layer.append(
                self.compute_hh_concentration(layer_attn, self.top_ratio)
            )

        return entropy_per_layer, hh_per_layer

    @staticmethod
    def compute_entropy(attn_weights: torch.Tensor, eps: float = 1e-9) -> float:
        """Mean attention entropy over heads and query positions. Returns scalar (nats).

        attn_weights: [B, H, S, S]; last dim is key distribution (softmax rows).
        """
        H_val = -(attn_weights * (attn_weights + eps).log()).sum(dim=-1)  # [B, H, S]
        return H_val.mean().item()

    @staticmethod
    def compute_hh_concentration(
        attn_weights: torch.Tensor,
        top_ratio: float = 0.2,
    ) -> float:
        """Ratio of attention mass on top top_ratio fraction of key tokens. Returns scalar.

        attn_weights: [B, H, S, S]; returns mean over B, H, S_q.
        """
        S = attn_weights.shape[-1]
        k = max(1, int(S * top_ratio))
        topk_vals, _ = attn_weights.topk(k, dim=-1)   # [B, H, S_q, k]
        return topk_vals.sum(dim=-1).mean().item()      # mean over B, H, S_q
