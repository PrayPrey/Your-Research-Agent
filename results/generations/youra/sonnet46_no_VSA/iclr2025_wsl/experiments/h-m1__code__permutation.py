"""S_n functional permutations for CIFAR10-GS CNN (coupled row-column)."""
import torch
import numpy as np
from copy import deepcopy
from data_loader import CONV_WEIGHT_KEYS, CONV_BIAS_KEYS


def sample_functional_permutations(
    channels_per_layer: list,  # [C_out_0, C_out_1, C_out_2]
    K: int,
    seed: int = 1,
) -> list:
    """
    Returns K permutation specs. Each spec is a list of per-layer
    channel permutation indices implementing coupled S_n permutations.
    Per DWSNet Eq. 5: perm_spec[i] permutes rows of W^(i) and cols of W^(i+1).
    """
    rng = np.random.default_rng(seed)
    specs = []
    for _ in range(K):
        spec = [torch.from_numpy(rng.permutation(c).astype(np.int64))
                for c in channels_per_layer]
        specs.append(spec)
    return specs


def apply_permutation(
    state_dict: dict,
    perm_spec: list,
    conv_weight_keys: list = None,
    bias_keys: list = None,
) -> dict:
    """
    Applies coupled row-column permutation to CNN state dict.
    perm_spec[i]: LongTensor of shape (C_out_i,) — permutation for layer i output channels.
    Returns new state_dict (deep copy).
    """
    if conv_weight_keys is None:
        conv_weight_keys = CONV_WEIGHT_KEYS
    if bias_keys is None:
        bias_keys = CONV_BIAS_KEYS

    out = deepcopy(state_dict)
    n_conv = len(conv_weight_keys)

    for i, p_i in enumerate(perm_spec):
        # Row permutation on layer i (permute output channels)
        k_w = conv_weight_keys[i]
        out[k_w] = out[k_w][p_i]           # (C_out, C_in, kH, kW)
        out[bias_keys[i]] = out[bias_keys[i]][p_i]  # (C_out,)

        # Column permutation on next layer (permute input channels)
        if i + 1 < n_conv:
            # Next layer is another conv: permute its input channel dim
            k_next = conv_weight_keys[i + 1]
            out[k_next] = out[k_next][:, p_i]  # (C_out_next, C_in_next, kH, kW)
        elif i == n_conv - 1:
            # Last conv layer: permute FC1 input columns (flattened spatial blocks)
            # After Flatten, conv last output (C_out, H, W) → (C_out * H * W,)
            # Channel c occupies indices [c*H*W : (c+1)*H*W] in the flat input
            fc1_key = "module_list.9.weight"  # (out_fc1, C_out * H * W)
            if fc1_key in out:
                C_last = len(p_i)  # e.g. 4
                spatial = out[fc1_key].shape[1] // C_last  # H*W = 9
                # Build column permutation index
                p_fc = torch.cat([p_i[c] * spatial + torch.arange(spatial) for c in range(C_last)])
                out[fc1_key] = out[fc1_key][:, p_fc]

    return out


def build_cnn_from_state_dict(state_dict: dict) -> torch.nn.Module:
    """Instantiate the CIFAR10-GS CNN and load state_dict. Returns model in eval mode."""
    model = _CIFAR10GS_CNN()
    model.load_state_dict(state_dict)
    model.eval()
    return model


def audit_functional_equivalence(
    state_dict: dict,
    perm_specs: list,
    tol: float = 1e-6,
    n_checks: int = 5,
    n_perms: int = 3,
) -> float:
    """
    Verifies ||f_v(x) - f_{pi.v}(x)||_inf <= tol.
    Returns max_diff. Raises AssertionError if > tol.
    """
    rng = torch.Generator()
    rng.manual_seed(0)
    model_orig = build_cnn_from_state_dict(state_dict)
    max_diff = 0.0

    for perm_spec in perm_specs[:n_perms]:
        perm_sd = apply_permutation(state_dict, perm_spec)
        model_perm = build_cnn_from_state_dict(perm_sd)

        for _ in range(n_checks):
            x = torch.rand(1, 3, 28, 28, generator=rng)
            with torch.no_grad():
                y_orig = model_orig(x)
                y_perm = model_perm(x)
            diff = (y_orig - y_perm).abs().max().item()
            max_diff = max(max_diff, diff)

    if max_diff > tol:
        raise AssertionError(
            f"Functional equivalence FAILED: max_diff={max_diff:.2e} > tol={tol:.0e}. "
            f"Check coupled permutation logic."
        )
    print(f"[AUDIT] Functional permutation verified: max_diff={max_diff:.2e}")
    return max_diff


class _CIFAR10GS_CNN(torch.nn.Module):
    """Small CNN matching ModelZooDataset CIFAR10-GS architecture.
    Input: 28x28 grayscale (3-channel GS). No padding. Produces 4*3*3=36 features before FC.
    Architecture from /tmp/modelzoo_repo/code/model_definitions/def_net.py (no dropout)."""
    def __init__(self):
        super().__init__()
        self.module_list = torch.nn.ModuleList([
            torch.nn.Conv2d(3, 8, kernel_size=5, padding=0),   # 0: 28→24
            torch.nn.MaxPool2d(2),                               # 1: 24→12
            torch.nn.LeakyReLU(),                                # 2
            torch.nn.Conv2d(8, 6, kernel_size=5, padding=0),   # 3: 12→8
            torch.nn.MaxPool2d(2),                               # 4: 8→4
            torch.nn.LeakyReLU(),                                # 5
            torch.nn.Conv2d(6, 4, kernel_size=2, padding=0),   # 6: 4→3
            torch.nn.LeakyReLU(),                                # 7
            torch.nn.Flatten(),                                  # 8 → (B,36)
            torch.nn.Linear(36, 20),                            # 9
            torch.nn.LeakyReLU(),                                # 10
            torch.nn.Linear(20, 10),                            # 11
        ])

    def forward(self, x):
        for layer in self.module_list:
            x = layer(x)
        return x

    def load_state_dict(self, state_dict, strict=True):
        # State dict indices match module_list indices directly (0,3,6,9,11 are parametric)
        for k, v in state_dict.items():
            parts = k.split(".")  # ["module_list", "idx", "weight|bias"]
            idx = int(parts[1])
            param_name = parts[2]
            mod = self.module_list[idx]
            if hasattr(mod, param_name):
                getattr(mod, param_name).data.copy_(v)
