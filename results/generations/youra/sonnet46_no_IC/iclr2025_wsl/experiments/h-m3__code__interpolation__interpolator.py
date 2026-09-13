"""Latent-space interpolation via EquiSSL-perm encoder + graph decoder."""
import importlib.util
import os
import sys
import torch

PROJECT_ROOT = os.environ.get('PROJECT_ROOT', '/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_wsl')
H_M1_CODE = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-m1/code')


def _load_checkpoint_to_graph():
    """Load checkpoint_to_graph from h-m1 using importlib to avoid module conflicts."""
    spec = importlib.util.spec_from_file_location(
        "hm1_multizoo_graph_dataset",
        os.path.join(H_M1_CODE, "data", "multizoo_graph_dataset.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.checkpoint_to_graph


_checkpoint_to_graph = None


def encode_checkpoint(encoder, state_dict, device):
    """state_dict -> z (latent_dim,)"""
    global _checkpoint_to_graph
    if _checkpoint_to_graph is None:
        _checkpoint_to_graph = _load_checkpoint_to_graph()

    graph = _checkpoint_to_graph(state_dict)
    graph = graph.to(device)

    with torch.no_grad():
        z = encoder(graph)  # (1, latent_dim) or (latent_dim,)

    if z.dim() == 2:
        z = z.squeeze(0)
    return z  # (latent_dim,)


def decode_latent_to_state_dict(decoder, z, reference_state_dict, device):
    """
    z (latent_dim,) -> reconstructed state_dict matching reference shapes.
    GraphDecoder outputs (max_edge_dim,) stats vector; mapped to weight tensors
    by tiling/slicing proportional to parameter count.
    """
    with torch.no_grad():
        stats_vec = decoder(z.unsqueeze(0).to(device), {}).squeeze(0)  # (max_edge_dim,)

    param_specs = [(k, v.shape, v.numel()) for k, v in reference_state_dict.items()]
    total_params = sum(n for _, _, n in param_specs)

    max_edge_dim = stats_vec.shape[0]
    if total_params <= max_edge_dim:
        flat = stats_vec[:total_params]
    else:
        repeats = (total_params // max_edge_dim) + 1
        flat = stats_vec.repeat(repeats)[:total_params]
        # ponytail: tiling is naive; per-layer MLP projection if accuracy collapses

    new_sd = {}
    offset = 0
    for key, shape, n in param_specs:
        new_sd[key] = flat[offset:offset + n].reshape(shape).detach().cpu()
        offset += n

    return new_sd


def latent_interpolate(encoder, decoder, state_dict_a, state_dict_b, device, alpha=0.5):
    """Encode A, encode B, interpolate in latent space, decode -> state_dict."""
    z_a = encode_checkpoint(encoder, state_dict_a, device)
    z_b = encode_checkpoint(encoder, state_dict_b, device)
    z_mid = (1.0 - alpha) * z_a + alpha * z_b  # NOT re-normalized (deliberate)
    return decode_latent_to_state_dict(decoder, z_mid, state_dict_a, device)


def weight_space_average(state_dict_a, state_dict_b):
    """Naive element-wise average of all parameters."""
    return {k: (state_dict_a[k].float() + state_dict_b[k].float()) / 2.0
            for k in state_dict_a}
