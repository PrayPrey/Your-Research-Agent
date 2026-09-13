"""OrbitVar computation loop — 100 models × 50 permutations."""
import torch
import numpy as np
import json
import os
from typing import Callable

from data_loader import CONV_WEIGHT_KEYS, CONV_BIAS_KEYS
from permutation import apply_permutation


def compute_orbit_var_all_models(
    dataset: list,
    encoder_fn: Callable,
    perm_specs: list,
    log_every: int = 10,
) -> tuple:
    """
    Returns (per_model_vars, mean_orbitvar, max_orbitvar).
    OrbitVar(v) = mean over embed dims of Var_pi[enc(pi.W_v)].
    Computed in float64 for numerical precision.
    """
    per_model_vars = []

    for idx, state_dict in enumerate(dataset):
        embeddings = []

        # Include original (identity) + K permuted
        embed_orig = encoder_fn(state_dict)
        embeddings.append(embed_orig)

        for perm_spec in perm_specs:
            perm_sd = apply_permutation(state_dict, perm_spec)
            embed = encoder_fn(perm_sd)  # (embed_dim,), float32
            embeddings.append(embed)

        emb_tensor = torch.stack(embeddings, dim=0)             # (K+1, embed_dim)
        emb_f64 = emb_tensor.double()                           # float64
        var_per_dim = torch.var(emb_f64, dim=0, unbiased=False) # (embed_dim,)
        orbit_var_v = var_per_dim.mean().item()
        per_model_vars.append(orbit_var_v)

        if (idx + 1) % log_every == 0:
            print(f"  [{idx+1}/{len(dataset)}] orbit_var={orbit_var_v:.3e}")

    mean_orbitvar = float(np.mean(per_model_vars))
    max_orbitvar = float(np.max(per_model_vars))
    return per_model_vars, mean_orbitvar, max_orbitvar


def run_gate_check(
    mean_c2: float,
    mean_c3: float,
    threshold: float = 1e-6,
) -> bool:
    """Prints PASS/FAIL; returns True if both means < threshold."""
    passed = (mean_c2 < threshold) and (mean_c3 < threshold)
    status = "PASS" if passed else "FAIL"
    print(f"[Gate] mean_orbitvar_c2={mean_c2:.3e}  mean_orbitvar_c3={mean_c3:.3e}  "
          f"threshold={threshold:.0e}  => {status}")
    if not passed:
        fails = []
        if mean_c2 >= threshold:
            fails.append(f"C2={mean_c2:.3e}")
        if mean_c3 >= threshold:
            fails.append(f"C3={mean_c3:.3e}")
        print(f"  FAILED encoders: {', '.join(fails)}")
    return passed


def save_results(results: dict, path: str = "results/orbit_var_results.json") -> None:
    """Write results dict to JSON. Creates parent dir if needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {path}")
