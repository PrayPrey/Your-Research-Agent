"""Tests for DeepSets C2 encoder — permutation invariance."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import torch
from encoder_c2 import build_c2_encoder, DeepSetsChannelEncoder
from permutation import sample_functional_permutations, apply_permutation
from data_loader import CHANNELS_PER_LAYER


def make_dummy_state_dict():
    sd = {}
    shapes = {
        "module_list.0.weight": (8, 3, 5, 5),
        "module_list.0.bias": (8,),
        "module_list.3.weight": (6, 8, 5, 5),
        "module_list.3.bias": (6,),
        "module_list.6.weight": (4, 6, 2, 2),
        "module_list.6.bias": (4,),
        "module_list.9.weight": (20, 36),
        "module_list.9.bias": (20,),
        "module_list.11.weight": (10, 20),
        "module_list.11.bias": (10,),
    }
    torch.manual_seed(123)
    for k, s in shapes.items():
        sd[k] = torch.randn(s)
    return sd


def test_c2_output_shape():
    enc = build_c2_encoder(embed_dim=128)
    enc.eval()
    sd = make_dummy_state_dict()
    with torch.no_grad():
        out = enc(sd)
    assert out.shape == (128,), f"Expected (128,), got {out.shape}"


def test_c2_permutation_invariance():
    """OrbitVar of DeepSets must be ~0 (numerical precision only)."""
    enc = build_c2_encoder(embed_dim=128)
    enc.eval()
    sd = make_dummy_state_dict()
    specs = sample_functional_permutations(CHANNELS_PER_LAYER, K=20, seed=1)

    embeddings = []
    with torch.no_grad():
        embeddings.append(enc(sd))
        for spec in specs:
            perm_sd = apply_permutation(sd, spec)
            embeddings.append(enc(perm_sd))

    emb_tensor = torch.stack(embeddings, 0).double()  # (21, 128)
    var_per_dim = torch.var(emb_tensor, dim=0, unbiased=False)
    orbit_var = var_per_dim.mean().item()

    assert orbit_var < 1e-10, (
        f"C2 OrbitVar={orbit_var:.3e} should be < 1e-10 (numerical precision). "
        f"Check phi layer uses no position-aware indexing."
    )


def test_c2_different_models_different_embeddings():
    """Two different state dicts should produce different embeddings."""
    enc = build_c2_encoder(embed_dim=128)
    enc.eval()
    sd1 = make_dummy_state_dict()
    torch.manual_seed(999)
    sd2 = {k: torch.randn(v.shape) for k, v in sd1.items()}
    with torch.no_grad():
        e1 = enc(sd1)
        e2 = enc(sd2)
    assert not torch.allclose(e1, e2), "Different weights should produce different embeddings"
