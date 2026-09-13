import os
import json
import random
import numpy as np
import torch
from torch.utils.data import Dataset
from typing import List, Dict, Tuple, Callable, Any
from torch.utils.data.dataloader import default_collate


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_model_zoo(n_models: int, seed: int = 0, data_dir: str = None, zoo_dir: str = None) -> List[Dict]:
    """Load real CNN model zoo trained on CIFAR-10.

    Returns list of dicts with 'state_dict' and 'label' (actual accuracy).
    Models are trained with varying hyperparameters to create diversity.
    """
    from zoo_generator import load_model_zoo as _load_zoo
    import os

    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(__file__), 'cifar_data')
    if zoo_dir is None:
        zoo_dir = os.path.join(os.path.dirname(__file__), 'zoo_cache')

    return _load_zoo(n_models=n_models, seed=seed, data_dir=data_dir, zoo_dir=zoo_dir)


def normalize_weights(models: List[Dict]) -> List[Dict]:
    """Normalize weights per-layer to zero mean, unit variance."""
    if not models:
        return models

    layer_stats = {}
    for key in models[0]['state_dict'].keys():
        all_weights = torch.stack([m['state_dict'][key].flatten() for m in models])
        layer_stats[key] = {
            'mean': all_weights.mean(dim=0),
            'std': all_weights.std(dim=0).clamp(min=1e-6)
        }

    normalized = []
    for m in models:
        new_sd = {}
        for key, tensor in m['state_dict'].items():
            flat = tensor.flatten()
            normed = (flat - layer_stats[key]['mean']) / layer_stats[key]['std']
            new_sd[key] = normed.reshape(tensor.shape)
        normalized.append({
            'state_dict': new_sd,
            'label': m['label']
        })

    return normalized


def split_train_test(models: List[Dict], train_frac: float, seed: int) -> Tuple[List[Dict], List[Dict]]:
    """Split models into train/test sets."""
    set_seed(seed)
    indices = list(range(len(models)))
    random.shuffle(indices)

    n_train = int(len(models) * train_frac)
    train_idx = indices[:n_train]
    test_idx = indices[n_train:]

    train = [models[i] for i in train_idx]
    test = [models[i] for i in test_idx]

    return train, test


class WeightSpaceDataset(Dataset):
    """Dataset for weight space learning."""

    def __init__(self, models: List[Dict]):
        self.models = models

    def __getitem__(self, idx: int) -> Tuple[Dict[str, torch.Tensor], float]:
        m = self.models[idx]
        return m['state_dict'], m['label']

    def __len__(self) -> int:
        return len(self.models)


def make_collate_fn(network_spec: Any) -> Callable:
    """Create collate function for WeightSpaceFeatures batching."""
    from nfn.common import state_dict_to_tensors, WeightSpaceFeatures

    def collate_fn(batch: List[Tuple[Dict, float]]) -> Tuple[Any, torch.Tensor]:
        state_dicts = [b[0] for b in batch]
        labels = torch.tensor([b[1] for b in batch], dtype=torch.float32)

        wts_and_bs = [state_dict_to_tensors(sd) for sd in state_dicts]
        wts_and_bs = default_collate(wts_and_bs)
        wsfeat = WeightSpaceFeatures(*wts_and_bs)

        return wsfeat, labels

    return collate_fn


def get_network_spec_from_sample(models: List[Dict]) -> Any:
    """Extract network_spec from a sample model."""
    from nfn.common import state_dict_to_tensors, network_spec_from_wsfeat, WeightSpaceFeatures

    sample_sd = models[0]['state_dict']
    wts, bs = state_dict_to_tensors(sample_sd)
    wts_batched = [w.unsqueeze(0) for w in wts]
    bs_batched = [b.unsqueeze(0) for b in bs]
    wsfeat = WeightSpaceFeatures(wts_batched, bs_batched)

    return network_spec_from_wsfeat(wsfeat)
