"""Per-model hidden state extraction with caching."""

import numpy as np
import torch
import gc

from config import MODELS, LAYER_FRACTION
from models import ModelWrapper
from cache import HiddenStateCache


def get_layer_idx(n_layers: int, frac: float = LAYER_FRACTION) -> int:
    return int(n_layers * frac)


def extract_for_model(
    model_key: str, questions: list[str], split: str, cache: HiddenStateCache
) -> np.ndarray:
    """Load model, extract hidden states at 2/3 depth, cache to disk, unload model."""
    if cache.exists(model_key, split):
        print(f"  Loading cached {model_key}/{split}...")
        return cache.load(model_key, split)

    print(f"  Extracting {model_key}/{split} ({len(questions)} samples)...")
    model_cfg = MODELS[model_key]
    layer_idx = get_layer_idx(model_cfg["n_layers"])

    wrapper = ModelWrapper(model_cfg["id"])
    wrapper.load()

    hidden_list = []
    for i, q in enumerate(questions):
        if (i + 1) % 100 == 0:
            print(f"    {i+1}/{len(questions)}")
        h = wrapper.get_hidden_states(q, layer_idx)
        hidden_list.append(h)

    wrapper.unload()
    del wrapper
    gc.collect()
    torch.cuda.empty_cache()

    hidden = np.vstack(hidden_list)
    cache.save(model_key, split, hidden)
    print(f"  Cached {model_key}/{split}: shape {hidden.shape}")
    return hidden
