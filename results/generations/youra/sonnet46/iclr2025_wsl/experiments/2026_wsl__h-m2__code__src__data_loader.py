"""Data loading utilities for h-e1 experiment.

Loads the Unterthiner CNN zoo from pickle, provides flat and NFT modes,
and implements permutation stress for robustness evaluation.
"""
import pickle
import logging
import numpy as np
import torch
from torch import Tensor
from torch.utils.data import Dataset, DataLoader

logger = logging.getLogger(__name__)


def load_zoo(pkl_path: str) -> list:
    """Load pickle file and validate minimum sample count.

    Parameters
    ----------
    pkl_path : str
        Path to the zoo_enriched.pkl file.

    Returns
    -------
    list[dict]
        Each dict has keys: 'weights', 'biases', 'test_acc', 'train_acc'.

    Raises
    ------
    ValueError
        If fewer than 500 samples are found.
    """
    with open(pkl_path, "rb") as f:
        zoo_data = pickle.load(f)
    if len(zoo_data) < 500:
        raise ValueError(f"Zoo has only {len(zoo_data)} samples, expected >= 500")
    logger.info(f"Loaded {len(zoo_data)} zoo models from {pkl_path}")
    return zoo_data


def compute_gen_gap(sample: dict) -> float:
    """Compute generalization gap = train_acc - test_acc."""
    return float(sample["train_acc"]) - float(sample["test_acc"])


def flatten_weights(weight_list: list) -> np.ndarray:
    """Flatten list of weight arrays to a single 1D numpy array.

    Parameters
    ----------
    weight_list : list
        List of numpy arrays (any shape).

    Returns
    -------
    np.ndarray
        1D array with all weights concatenated.
    """
    parts = []
    for w in weight_list:
        arr = np.array(w, dtype=np.float32)
        parts.append(arr.flatten())
    return np.concatenate(parts, axis=0)


def _weight_to_2d(w: np.ndarray) -> np.ndarray:
    """Reshape a weight array to (n_units, fan_in).

    For a weight of shape (..., fan_in), n_units = product of all dims except last.
    """
    arr = np.array(w, dtype=np.float32)
    fan_in = arr.shape[-1]
    n_units = arr.size // fan_in
    return arr.reshape(n_units, fan_in)


def apply_permutation_stress(weight_list: list, severity: float) -> list:
    """Apply random permutation stress to each weight tensor.

    For each weight array w (any shape):
    1. Reshape to 2D (n_units, fan_in).
    2. Permute n_units * severity rows randomly.
    3. Reshape back to original shape.

    Parameters
    ----------
    weight_list : list
        List of numpy arrays representing weights.
    severity : float
        Fraction of units to permute, in [0, 1].

    Returns
    -------
    list
        List of permuted weight arrays with same shapes as input.
    """
    if severity == 0.0:
        return [np.array(w, dtype=np.float32) for w in weight_list]

    result = []
    for w in weight_list:
        arr = np.array(w, dtype=np.float32)
        original_shape = arr.shape
        fan_in = arr.shape[-1]
        n_units = arr.size // fan_in
        flat2d = arr.reshape(n_units, fan_in).copy()

        n_permute = max(1, int(n_units * severity))
        perm_indices = np.random.choice(n_units, size=n_permute, replace=False)
        shuffled = perm_indices[np.random.permutation(n_permute)]
        flat2d[perm_indices] = flat2d[shuffled]

        result.append(flat2d.reshape(original_shape))
    return result


class ZooDataset(Dataset):
    """Dataset returning (flat_vec, gap) or (list[Tensor], gap) depending on mode.

    Parameters
    ----------
    samples : list[dict]
        List of dicts with keys 'weights', 'train_acc', 'test_acc'.
    mode : str
        'flat' -> flatten all weights to 1D tensor
        'nft' -> list of 2D tensors per weight array (n_units, fan_in)
    """

    def __init__(self, samples: list, mode: str = "flat"):
        self.samples = samples
        self.mode = mode

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int):
        sample = self.samples[idx]
        gap = torch.tensor(compute_gen_gap(sample), dtype=torch.float32)
        weight_list = sample["weights"]

        if self.mode == "flat":
            flat = flatten_weights(weight_list)
            return torch.tensor(flat, dtype=torch.float32), gap
        elif self.mode == "nft":
            tensors = []
            for w in weight_list:
                t2d = _weight_to_2d(w)
                tensors.append(torch.tensor(t2d, dtype=torch.float32))
            return tensors, gap
        else:
            raise ValueError(f"Unknown mode: {self.mode}. Use 'flat' or 'nft'.")


def get_dataloaders(
    pkl_path: str,
    batch_size: int = 64,
    train_ratio: float = 0.8,
    seed: int = 42,
):
    """Split zoo into train/test and return DataLoaders.

    Returns separate loaders for flat and nft modes.

    Returns
    -------
    tuple
        (flat_train_loader, flat_test_loader, nft_train_loader, nft_test_loader)
    """
    zoo = load_zoo(pkl_path)

    rng = np.random.default_rng(seed)
    indices = rng.permutation(len(zoo)).tolist()
    n_train = int(len(zoo) * train_ratio)
    train_idx = indices[:n_train]
    test_idx = indices[n_train:]

    train_samples = [zoo[i] for i in train_idx]
    test_samples = [zoo[i] for i in test_idx]

    flat_train = ZooDataset(train_samples, mode="flat")
    flat_test = ZooDataset(test_samples, mode="flat")
    nft_train = ZooDataset(train_samples, mode="nft")
    nft_test = ZooDataset(test_samples, mode="nft")

    g_train = torch.Generator()
    g_train.manual_seed(seed)
    g_test = torch.Generator()
    g_test.manual_seed(seed + 1)

    flat_train_loader = DataLoader(flat_train, batch_size=batch_size, shuffle=True,
                                   num_workers=0, generator=g_train)
    flat_test_loader = DataLoader(flat_test, batch_size=batch_size, shuffle=False,
                                  num_workers=0)
    nft_train_loader = DataLoader(nft_train, batch_size=batch_size, shuffle=True,
                                  collate_fn=nft_collate_fn, num_workers=0,
                                  generator=torch.Generator().manual_seed(seed))
    nft_test_loader = DataLoader(nft_test, batch_size=batch_size, shuffle=False,
                                 collate_fn=nft_collate_fn, num_workers=0)

    return flat_train_loader, flat_test_loader, nft_train_loader, nft_test_loader


def nft_collate_fn(batch):
    """Collate NFT batch with per-layer padding.

    Each batch item is (list_of_weight_matrices, label).
    Pads each layer to max n_units in that layer across the batch.

    Returns
    -------
    tuple
        (padded_by_layer, labels, attention_mask)
        - padded_by_layer: list of Tensor (B, max_n_units_l, fan_in_l)
        - labels: Tensor (B,)
        - attention_mask: Tensor (B, total_max_units) bool, True=padding
    """
    B = len(batch)
    n_layers = len(batch[0][0])

    # Find max n_units per layer across batch
    max_neurons_per_layer = [
        max(batch[b][0][l].shape[0] for b in range(B))
        for l in range(n_layers)
    ]

    padded_by_layer = []
    mask_by_layer = []

    for l in range(n_layers):
        max_n = max_neurons_per_layer[l]
        fan_in = batch[0][0][l].shape[1]
        padded_l = torch.zeros(B, max_n, fan_in, dtype=torch.float32)
        mask_l = torch.ones(B, max_n, dtype=torch.bool)  # True = ignore (padding)

        for b in range(B):
            wm = batch[b][0][l]
            n = wm.shape[0]
            padded_l[b, :n, :] = wm
            mask_l[b, :n] = False  # attend to real neurons

        padded_by_layer.append(padded_l)
        mask_by_layer.append(mask_l)

    attention_mask = torch.cat(mask_by_layer, dim=1)  # (B, total_max_units)
    labels = torch.stack([batch[b][1] for b in range(B)])  # (B,)

    return padded_by_layer, labels, attention_mask
