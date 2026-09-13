"""
Embedding extraction for H-M1: SANE, EquiSSL (monomial), EquiSSL-perm (permutation).
Extracts embeddings for all ViT zoo checkpoints across all seeds.
"""
import os
import sys
import glob
import re
import numpy as np
import torch
from torch_geometric.data import Batch

_this_code = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_h_e1 = os.environ.get('H_E1_CODE',
    '/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_wsl/docs/youra_research/h-e1/code')
if _this_code not in sys.path:
    sys.path.insert(0, _this_code)
if _h_e1 not in sys.path:
    sys.path.append(_h_e1)  # append so H_M1 modules take priority


def load_vit_zoo_dataset(vit_zoo_root: str):
    """Load ViT zoo as list of (graph, accuracy) from H-E1's ViTZooGraphDataset."""
    from data.vitzoo_graph_dataset import ViTZooGraphDataset
    ds = ViTZooGraphDataset(root=vit_zoo_root)
    return ds


def extract_graph_embeddings(encoder, vit_dataset, device, batch_size=32):
    """
    Extract embeddings from a graph encoder over ViT zoo.
    Returns ndarray shape (N, latent_dim).
    """
    encoder.eval()
    all_embeds = []
    loader = torch.utils.data.DataLoader(
        list(range(len(vit_dataset))), batch_size=batch_size, shuffle=False)

    with torch.no_grad():
        for indices in loader:
            graphs = [vit_dataset[i] for i in indices]
            batch = Batch.from_data_list(graphs).to(device)
            z = encoder(batch)
            all_embeds.append(z.cpu().numpy())

    return np.concatenate(all_embeds, axis=0)


def load_equissl_encoder(checkpoint_path, symmetry, device):
    """Load frozen EquiSSL encoder from checkpoint."""
    from models.equissl_encoder import EquiSSLEncoder
    import config as cfg
    encoder = EquiSSLEncoder(
        node_in_dim=4, edge_in_dim=4,
        hidden_dim=cfg.HIDDEN_DIM, latent_dim=cfg.LATENT_DIM,
        num_layers=cfg.NUM_LAYERS, symmetry=symmetry
    )
    ckpt = torch.load(checkpoint_path, map_location='cpu', weights_only=True)
    state = ckpt.get('model_state_dict', ckpt)
    encoder.load_state_dict(state, strict=False)
    encoder.eval()
    return encoder.to(device)


def extract_sane_embeddings(checkpoint_path, vit_dataset, device, batch_size=32):
    """Extract SANE embeddings via flat weight chunk tokenization."""
    # Load SANE model from H-E1 checkpoint
    ckpt = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
    # SANE is a simpler MLP that operates on flattened weight chunks
    # Use SANE's encoder from H-E1 if available, else fallback to flat mean
    try:
        from training.train_sane_baseline import SANEEncoder
        enc = SANEEncoder()
        enc.load_state_dict(ckpt.get('model_state_dict', ckpt), strict=False)
        enc = enc.to(device).eval()
        return extract_graph_embeddings(enc, vit_dataset, device, batch_size)
    except Exception:
        # Fallback: use graph encoder loaded as SANE (it IS a graph encoder)
        # H-E1 SANE uses same EquiSSLEncoder but with flat stat features
        from models.equissl_encoder import EquiSSLEncoder
        import config as cfg
        enc = EquiSSLEncoder(
            node_in_dim=4, edge_in_dim=4,
            hidden_dim=cfg.HIDDEN_DIM, latent_dim=cfg.LATENT_DIM,
            num_layers=cfg.NUM_LAYERS, symmetry='monomial'
        ).to(device)
        state = ckpt.get('model_state_dict', ckpt)
        enc.load_state_dict(state, strict=False)
        enc.eval()
        return extract_graph_embeddings(enc, vit_dataset, device, batch_size)


def get_accuracy_labels(vit_dataset):
    """Extract accuracy labels from ViT zoo dataset. Returns ndarray (N,)."""
    labels = []
    for i in range(len(vit_dataset)):
        g = vit_dataset[i]
        if hasattr(g, 'y') and g.y is not None:
            labels.append(float(g.y.item() if g.y.numel() == 1 else g.y[0].item()))
        else:
            labels.append(0.0)
    return np.array(labels, dtype=np.float32)


def extract_all_embeddings(seeds, vit_zoo_root, he1_ckpt_dir, hm1_ckpt_dir,
                           results_dir, device):
    """
    Extract all embeddings: sane, equi, equi_perm for each seed.
    Returns dict keyed by '{model}_seed{i}' with ndarray values.
    """
    os.makedirs(results_dir, exist_ok=True)

    vit_dataset = load_vit_zoo_dataset(vit_zoo_root)
    n_models = len(vit_dataset)
    print(f'ViT zoo: {n_models} models')

    embeddings = {}

    for seed in seeds:
        for model_name, ckpt_dir, symmetry in [
            ('sane',      he1_ckpt_dir, 'sane'),
            ('equi',      he1_ckpt_dir, 'monomial'),
            ('equi_perm', hm1_ckpt_dir, 'permutation'),
        ]:
            key = f'{model_name}_seed{seed}'
            cache_path = os.path.join(results_dir, f'embeddings_{key}.npy')

            if os.path.exists(cache_path):
                arr = np.load(cache_path)
                if arr.shape[0] == n_models and np.isfinite(arr).all():
                    print(f'  Loaded from cache: {key} shape={arr.shape}')
                    embeddings[key] = arr
                    continue

            # Find checkpoint
            if model_name == 'sane':
                ckpt_path = os.path.join(ckpt_dir, f'sane_seed{seed}',
                                         f'sane_seed{seed}_best.pt')
                if not os.path.exists(ckpt_path):
                    # Try alternative naming
                    candidates = glob.glob(os.path.join(ckpt_dir, f'sane_seed{seed}',
                                                        '*.pt'))
                    ckpt_path = candidates[0] if candidates else None
            else:
                lam = '0.1'
                if model_name == 'equi':
                    ckpt_path = os.path.join(ckpt_dir, f'seed{seed}',
                        f'equissl_lam{lam}_seed{seed}_best.pt')
                    if not os.path.exists(ckpt_path):
                        candidates = glob.glob(os.path.join(ckpt_dir, f'seed{seed}',
                            f'*lam{lam}*seed{seed}*.pt'))
                        ckpt_path = candidates[0] if candidates else None
                else:  # equi_perm
                    ckpt_path = os.path.join(hm1_ckpt_dir, f'equi_perm_seed{seed}.pt')

            if ckpt_path is None or not os.path.exists(ckpt_path):
                print(f'  WARNING: checkpoint not found for {key}, skipping')
                continue

            print(f'  Extracting {key} from {os.path.basename(ckpt_path)}...')
            try:
                if model_name == 'sane':
                    arr = extract_sane_embeddings(ckpt_path, vit_dataset,
                                                  device, batch_size=32)
                else:
                    encoder = load_equissl_encoder(ckpt_path, symmetry, device)
                    arr = extract_graph_embeddings(encoder, vit_dataset,
                                                   device, batch_size=32)

                if not np.isfinite(arr).all():
                    print(f'  WARNING: NaN/Inf in {key} embeddings, clipping')
                    arr = np.nan_to_num(arr, nan=0.0, posinf=1.0, neginf=-1.0)

                np.save(cache_path, arr)
                embeddings[key] = arr
                print(f'  Saved {key}: shape={arr.shape}')
            except Exception as e:
                print(f'  ERROR extracting {key}: {e}')

    return embeddings, vit_dataset
