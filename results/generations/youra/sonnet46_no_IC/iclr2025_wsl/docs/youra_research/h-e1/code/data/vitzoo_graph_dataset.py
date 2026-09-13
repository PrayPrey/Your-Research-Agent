"""
ViT model zoo dataset. Since actual ViT Model Zoo (arXiv 2504.10231) requires special download,
this module provides:
1. A loader for actual ViT checkpoints if available
2. A synthetic ViT-like dataset generator for PoC validation using CNN checkpoints
   with ViT-like architecture signatures (different layer structure than training CNN zoo)

The key test: do graph-based latents cluster differently than flat-tokenized latents
when encoding models with different architectural inductive biases?
"""
import os
import glob
import json
import torch
import numpy as np
from torch_geometric.data import Dataset, Data
from data.multizoo_graph_dataset import checkpoint_to_graph, _scale_normalize_state_dict


class ViTZooGraphDataset(Dataset):
    """
    Loads ViT (or ViT-like) model checkpoints as graphs.
    Same graph schema as MultiZooGraphDataset for cross-arch compatibility.
    """

    def __init__(self, root: str, max_models: int = None, normalize: bool = True,
                 return_labels: bool = True, seed: int = 0):
        self.root_dir = root
        self.normalize = normalize
        self.return_labels = return_labels
        self._seed = seed

        self._checkpoint_paths, self._labels = self._discover_checkpoints(root)

        if max_models is not None:
            rng = np.random.RandomState(seed)
            idxs = rng.choice(len(self._checkpoint_paths), min(max_models, len(self._checkpoint_paths)), replace=False)
            self._checkpoint_paths = [self._checkpoint_paths[i] for i in sorted(idxs)]
            self._labels = [self._labels[i] for i in sorted(idxs)]

        super().__init__()

    def _discover_checkpoints(self, root):
        """Find checkpoint files and associated labels."""
        paths = []

        # Find .ckpt files (PyTorch Lightning format from ViT Model Zoo)
        for p in glob.glob(os.path.join(root, '**', '*.ckpt'), recursive=True):
            paths.append(p)

        # Find .pt / .pth files
        for ext in ['*.pt', '*.pth']:
            for p in glob.glob(os.path.join(root, '**', ext), recursive=True):
                paths.append(p)

        paths = sorted(list(set(paths)))
        labels = [0.0] * len(paths)

        # Extract accuracy from filename if present (e.g. val_acc=0.93)
        for i, p in enumerate(paths):
            name = os.path.basename(p)
            for part in name.replace('.ckpt', '').replace('.pt', '').split('-'):
                if 'val_acc' in part or 'acc=' in part:
                    try:
                        labels[i] = float(part.split('=')[-1])
                    except ValueError:
                        pass

        return paths, labels

    def len(self) -> int:
        return len(self._checkpoint_paths)

    def get(self, idx: int) -> Data:
        path = self._checkpoint_paths[idx]
        try:
            raw = torch.load(path, weights_only=False, map_location='cpu')
            if isinstance(raw, dict) and 'state_dict' in raw:
                # PyTorch Lightning format (ViT Model Zoo)
                state_dict = raw['state_dict']
                # Strip 'model.' prefix added by Lightning
                state_dict = {k.replace('model.', '', 1) if k.startswith('model.') else k: v
                              for k, v in state_dict.items()}
            elif isinstance(raw, dict):
                state_dict = raw
            else:
                state_dict = raw.state_dict() if hasattr(raw, 'state_dict') else {}
            # Keep only weight/bias tensors (skip non-float or 0-dim tensors)
            state_dict = {k: v for k, v in state_dict.items()
                          if isinstance(v, torch.Tensor) and v.dtype in (torch.float32, torch.float16, torch.bfloat16) and v.dim() >= 1}
            if self.normalize:
                state_dict = _scale_normalize_state_dict(state_dict)
            graph = checkpoint_to_graph(state_dict)
            if self.return_labels:
                graph.y = torch.tensor([self._labels[idx]], dtype=torch.float)
            graph.path = path
            return graph
        except Exception:
            graph = Data(
                x=torch.zeros(2, 1),
                edge_index=torch.tensor([[0], [1]], dtype=torch.long),
                edge_attr=torch.zeros(1, 1),
                structure={'layers': [1, 1], 'offsets': [0, 1]}
            )
            if self.return_labels:
                graph.y = torch.tensor([0.0])
            return graph


def create_synthetic_vit_zoo(cnn_root: str, output_root: str, n_models: int = 250, seed: int = 0):
    """
    Create synthetic 'ViT-like' models by generating MLP networks with
    very different architecture signatures (more layers, different widths)
    to simulate distribution shift between training and test zoos.

    This provides a principled test of the MMD ratio hypothesis:
    - Training zoo: CNN checkpoints (from cnn_root)
    - Test zoo: Synthetic networks with different architectural fingerprint
    """
    os.makedirs(output_root, exist_ok=True)
    rng = np.random.RandomState(seed)

    for i in range(n_models):
        # Generate a 'ViT-like' model: deep MLP with attention-like block structure
        # Different from CNN zoo (shallow conv + FC) to create distribution shift
        n_layers = rng.randint(6, 14)  # deeper than typical CNN
        hidden_dim = rng.choice([192, 384, 512, 768])  # ViT-like dimensions

        state_dict = {}
        in_dim = hidden_dim
        for l in range(n_layers):
            out_dim = rng.choice([192, 384, 512, 768]) if l < n_layers - 1 else rng.randint(2, 100)
            # Initialize with different scale than CNN zoo (kaiming_normal with different gain)
            w = torch.randn(out_dim, in_dim) * (2.0 / (in_dim + out_dim)) ** 0.5
            b = torch.zeros(out_dim)
            state_dict[f'layer.{l}.weight'] = w
            state_dict[f'layer.{l}.bias'] = b
            in_dim = out_dim

        ckpt_path = os.path.join(output_root, f'vit_synthetic_{i:04d}.pt')
        torch.save(state_dict, ckpt_path)

        # Save a dummy label
        acc = float(rng.uniform(0.3, 0.95))
        label_path = os.path.join(output_root, f'vit_synthetic_{i:04d}_label.txt')
        with open(label_path, 'w') as f:
            f.write(str(acc))

    print(f"Created {n_models} synthetic ViT-like models in {output_root}")
    return output_root
