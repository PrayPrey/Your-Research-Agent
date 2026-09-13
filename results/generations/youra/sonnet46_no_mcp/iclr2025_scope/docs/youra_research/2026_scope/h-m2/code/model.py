import os
import importlib.util as _ilu
import torch
import torch.nn as nn
from typing import Optional, Tuple

_H_E1_CODE = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../h-e1/code"))
_H_M1_CODE = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../h-m1/code"))

# Dynamic import from H-E1
_e1_spec = _ilu.spec_from_file_location("h_e1_model", os.path.join(_H_E1_CODE, "model.py"))
_e1_mod = _ilu.module_from_spec(_e1_spec)
_e1_spec.loader.exec_module(_e1_mod)

H2OEvictionAwareAttention = _e1_mod.H2OEvictionAwareAttention
inject_h2o_wrappers = _e1_mod.inject_h2o_wrappers
load_base_model = _e1_mod.load_base_model

# Dynamic import from H-M1
_m1_spec = _ilu.spec_from_file_location("h_m1_model", os.path.join(_H_M1_CODE, "model.py"))
_m1_mod = _ilu.module_from_spec(_m1_spec)
_m1_spec.loader.exec_module(_m1_mod)

load_adapter_model = _m1_mod.load_adapter_model
set_h2o_training_mode = _m1_mod.set_h2o_training_mode


def set_h2o_budget(model: nn.Module, kv_budget_ratio: float) -> None:
    """Set kv_budget_ratio on all H2OEvictionAwareAttention wrappers.
    Raises ValueError if no H2O wrappers found (budget not applied).
    """
    count = 0
    for module in model.modules():
        if isinstance(module, H2OEvictionAwareAttention):
            module.kv_budget_ratio = kv_budget_ratio
            count += 1
    if count == 0:
        raise ValueError(
            "No H2OEvictionAwareAttention wrappers found — budget not applied. "
            "Call inject_h2o_wrappers() first for eviction-aware adapters."
        )


def verify_budget_applied(model: nn.Module, expected_ratio: float) -> bool:
    """Return True if all H2OEvictionAwareAttention instances have expected_ratio."""
    found = False
    for module in model.modules():
        if isinstance(module, H2OEvictionAwareAttention):
            found = True
            if abs(getattr(module, "kv_budget_ratio", -1) - expected_ratio) > 1e-6:
                return False
    return found  # False if no wrappers found


def load_model_for_sweep(
    model_name: str,
    adapter_path: str,
    adapter_type: str,
    initial_budget: float = 0.5,
) -> Tuple[nn.Module, object]:
    """Load base model + PEFT adapter; inject H2O for eviction-aware; set eager attn.
    Returns: (model_in_eval_mode, tokenizer)
    """
    from transformers import AutoTokenizer

    # Map adapter_type to condition used by H-M1's load_adapter_model
    condition = "eviction-aware" if adapter_type == "eviction-aware" else "baseline"

    model = load_adapter_model(
        model_name=model_name,
        adapter_checkpoint=adapter_path,
        condition=condition,
        kv_budget_ratio=initial_budget,
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model.eval()
    return model, tokenizer
