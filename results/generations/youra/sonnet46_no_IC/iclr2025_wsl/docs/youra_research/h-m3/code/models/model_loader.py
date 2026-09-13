"""Load frozen encoder and decoder from H-M1/H-E1 checkpoints."""
import os
import sys
import torch

PROJECT_ROOT = os.environ.get('PROJECT_ROOT', '/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_wsl')
H_M1_CODE = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-m1/code')

if H_M1_CODE not in sys.path:
    sys.path.insert(0, H_M1_CODE)
H_M3_CODE = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-m3/code')


def load_frozen_encoder(ckpt_path, device, latent_dim=128, hidden_dim=256, num_layers=4):
    import importlib.util, importlib
    spec = importlib.util.spec_from_file_location(
        "hm1_equissl_encoder",
        os.path.join(H_M1_CODE, "models", "equissl_encoder.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    EquiSSLEncoder = mod.EquiSSLEncoder

    encoder = EquiSSLEncoder(
        node_in_dim=4, edge_in_dim=4,
        hidden_dim=hidden_dim, latent_dim=latent_dim,
        num_layers=num_layers, symmetry='permutation', pool='mean'
    )

    ckpt = torch.load(ckpt_path, map_location='cpu')
    if isinstance(ckpt, dict):
        if 'model_state_dict' in ckpt:
            state_dict = ckpt['model_state_dict']
        elif 'encoder_state_dict' in ckpt:
            state_dict = ckpt['encoder_state_dict']
        else:
            state_dict = ckpt
    else:
        state_dict = ckpt

    encoder.load_state_dict(state_dict, strict=False)
    encoder.eval()
    return encoder.to(device)


def load_frozen_decoder(ckpt_path, device, latent_dim=128, hidden_dim=256, max_edge_dim=512):
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "hm1_graph_decoder",
        os.path.join(H_M1_CODE, "models", "graph_decoder.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    GraphDecoder = mod.GraphDecoder

    decoder = GraphDecoder(latent_dim=latent_dim, hidden_dim=hidden_dim, max_edge_dim=max_edge_dim)

    ckpt = torch.load(ckpt_path, map_location='cpu')
    if isinstance(ckpt, dict):
        if 'decoder_state_dict' in ckpt:
            state_dict = ckpt['decoder_state_dict']
        else:
            state_dict = ckpt
    else:
        state_dict = ckpt

    decoder.load_state_dict(state_dict, strict=False)
    decoder.eval()
    return decoder.to(device)


def load_mlp_checkpoint(path, device='cpu'):
    return torch.load(path, map_location=device)
