"""PermAug: permutation augmentation for zoo CNN weight vectors.

Permutes hidden FC neurons following Zhou 2023 (NFN Eq. 1).
For the CIFAR-10 CNN zoo (2864-dim flat vector), the only permutable
FC hidden layer is fc0 (20 neurons). Conv layers are not permuted.
"""
import torch
from torch import Tensor
from torch.utils.data import Dataset


# Flat vector layout for CIFAR-10 CNN zoo (sorted state_dict keys)
# Computed from actual zoo architecture (see perm_aug.py header)
CIFAR10_CNN_FC_LAYOUT = {
    # (w_offset, w_rows, w_cols, b_offset)  for each FC hidden layer
    # fc0: W(20,36) at offset 1914, b(20) at offset 2634
    # fc1: W(10,20) at offset 2654, b(10) at offset 2854  (output, not permuted)
    "fc_hidden_layers": [
        {
            "w_offset": 1914,
            "w_rows": 20,   # out neurons (to permute)
            "w_cols": 36,   # in neurons
            "b_offset": 2634,
            "w_next_offset": 2654,
            "w_next_rows": 10,  # next layer rows
            "w_next_cols": 20,  # next layer cols (= w_rows above)
        }
    ]
}


def apply_random_permutation(weight_vector: Tensor, layer_sizes: list = None) -> Tensor:
    """Permute FC hidden neurons of a CIFAR-10 CNN flat weight vector.

    layer_sizes is ignored — layout is determined by CIFAR10_CNN_FC_LAYOUT.
    Returns permuted vector, same shape.
    """
    out = weight_vector.clone().float()

    for layer in CIFAR10_CNN_FC_LAYOUT["fc_hidden_layers"]:
        w_off = layer["w_offset"]
        h_out = layer["w_rows"]
        h_in = layer["w_cols"]
        b_off = layer["b_offset"]
        wn_off = layer["w_next_offset"]
        wn_rows = layer["w_next_rows"]
        wn_cols = layer["w_next_cols"]

        w_end = w_off + h_out * h_in
        b_end = b_off + h_out
        wn_end = wn_off + wn_rows * wn_cols

        if wn_end > len(out):
            break

        perm = torch.randperm(h_out)

        W = out[w_off:w_end].view(h_out, h_in)
        b = out[b_off:b_end]
        W_next = out[wn_off:wn_end].view(wn_rows, wn_cols)

        out[w_off:w_end] = W[perm, :].reshape(-1)
        out[b_off:b_end] = b[perm]
        out[wn_off:wn_end] = W_next[:, perm].reshape(-1)

    return out


class PermAugDataset(Dataset):
    """Wraps a TensorDataset of (flat_x, y) with permutation augmentation.

    __len__ = len(base) * (num_permutations + 1)
    aug_idx == 0 → original; aug_idx > 0 → apply_random_permutation
    """

    def __init__(self, base_dataset: Dataset, layer_sizes: list = None, num_permutations: int = 10):
        self.base = base_dataset
        self.layer_sizes = layer_sizes  # kept for API compat; not used in apply_random_permutation
        self.num_permutations = num_permutations
        self._n_aug = num_permutations + 1  # including original

    def __len__(self) -> int:
        return len(self.base) * self._n_aug

    def __getitem__(self, idx: int):
        base_idx = idx // self._n_aug
        aug_idx = idx % self._n_aug

        x, y = self.base[base_idx]
        if aug_idx == 0:
            return x, y
        return apply_random_permutation(x, self.layer_sizes), y
