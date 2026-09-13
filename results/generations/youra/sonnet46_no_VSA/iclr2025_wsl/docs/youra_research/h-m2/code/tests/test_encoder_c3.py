"""Tests for NFN C3 encoder — structured equivariance."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import torch
from encoder_c3 import (
    state_dict_to_wsfeat,
    get_network_spec,
    build_nfn_encoder,
    encode_nfn,
)
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
    torch.manual_seed(456)
    for k, s in shapes.items():
        sd[k] = torch.randn(s)
    return sd


def test_c3_wsfeat_construction():
    sd = make_dummy_state_dict()
    wsfeat = state_dict_to_wsfeat(sd)
    # Should have 5 weight tensors (3 conv + 2 fc)
    assert len(wsfeat.weights) == 5, f"Expected 5 weight tensors, got {len(wsfeat.weights)}"
    assert len(wsfeat.biases) == 5


def test_c3_output_shape():
    sd = make_dummy_state_dict()
    network_spec = get_network_spec(sd)
    model = build_nfn_encoder(network_spec, sample_state_dict=sd, nfn_channels=32, embed_dim=128)
    model.eval()
    out = encode_nfn(model, sd)
    assert out.shape == (128,), f"Expected (128,), got {out.shape}"


def test_c3_permutation_invariance():
    """OrbitVar of NFN should be very small (near-zero)."""
    sd = make_dummy_state_dict()
    network_spec = get_network_spec(sd)
    model = build_nfn_encoder(network_spec, sample_state_dict=sd, nfn_channels=32, embed_dim=128)
    model.eval()

    specs = sample_functional_permutations(CHANNELS_PER_LAYER, K=20, seed=1)
    embeddings = [encode_nfn(model, sd)]
    for spec in specs:
        perm_sd = apply_permutation(sd, spec)
        embeddings.append(encode_nfn(model, perm_sd))

    emb_tensor = torch.stack(embeddings, 0).double()
    var_per_dim = torch.var(emb_tensor, dim=0, unbiased=False)
    orbit_var = var_per_dim.mean().item()

    assert orbit_var < 1e-4, (
        f"C3 OrbitVar={orbit_var:.3e} should be < 1e-4 for NFN equivariant encoder."
    )
