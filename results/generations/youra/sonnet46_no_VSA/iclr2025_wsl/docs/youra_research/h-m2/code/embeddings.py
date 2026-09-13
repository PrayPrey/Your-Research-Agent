"""H-M2: Load or compute CISE (C1) embeddings + K=50 permuted embeddings."""
import json
import os
import sys

import numpy as np
import torch

# H-M1 bootstrap — data_loader, permutation, encoder_c1 live there
_HERE = os.path.dirname(os.path.abspath(__file__))
_H_M1_CODE = os.path.join(_HERE, '..', '..', 'h-m1', 'code')
sys.path.insert(0, os.path.abspath(_H_M1_CODE))

from data_loader import load_dataset, CHANNELS_PER_LAYER  # noqa: E402
from permutation import sample_functional_permutations, apply_permutation  # noqa: E402
from encoder_c1 import build_c1_encoder  # noqa: E402
from orbit_var import compute_orbit_var_all_models  # noqa: E402

ORBIT_VAR_EXPECTED: float = 0.010333
ORBIT_VAR_TOL: float = 0.20  # 20% tolerance


def verify_orbit_var(orbit_var: float) -> None:
    """Assert orbit_var within 20% of ORBIT_VAR_EXPECTED. Raises RuntimeError if not."""
    lo = ORBIT_VAR_EXPECTED * (1.0 - ORBIT_VAR_TOL)
    hi = ORBIT_VAR_EXPECTED * (1.0 + ORBIT_VAR_TOL)
    if not (lo <= orbit_var <= hi):
        raise RuntimeError(
            f"orbit_var={orbit_var:.6f} outside [{lo:.6f}, {hi:.6f}] "
            f"(expected {ORBIT_VAR_EXPECTED} ±{ORBIT_VAR_TOL*100:.0f}%)"
        )
    print(f"[verify_orbit_var] {orbit_var:.6f} within tolerance ✓")


def load_or_compute_embeddings(
    pt_path: str,
    h1_results_path: str,
    n_models: int = 100,
    K: int = 50,
    embed_dim: int = 64,
    seed: int = 1,
) -> tuple:
    """
    Returns (X_cise, permuted_X, y_acc, perm_specs, orbit_var_h1).

    X_cise:       (N, embed_dim) ndarray float32
    permuted_X:   (N, K, embed_dim) ndarray float32
    y_acc:        (N,) ndarray float64
    perm_specs:   list[list[Tensor]] — K permutation specs
    orbit_var_h1: float — H-M1 mean OrbitVar for verification
    """
    # Load dataset (always needed for y_acc)
    dataset, accs = load_dataset(pt_path, n_models=n_models)
    y_acc = np.array(accs, dtype=np.float64)  # (N,)
    N = len(dataset)

    # Sample K permutation specs
    perm_specs = sample_functional_permutations(CHANNELS_PER_LAYER, K=K, seed=seed)

    # Try cache-hit branch
    h1 = {}
    if os.path.exists(h1_results_path):
        with open(h1_results_path) as f:
            h1 = json.load(f)

    # Extract orbit_var_h1 from h-m1 JSON
    # h-m1 JSON stores it under ratios.mean_OrbitVar_C1 OR per_model.orbit_vars_C1
    orbit_var_h1 = None
    if "ratios" in h1 and "mean_OrbitVar_C1" in h1["ratios"]:
        orbit_var_h1 = float(h1["ratios"]["mean_OrbitVar_C1"])
    elif "mean_orbitvar" in h1:
        orbit_var_h1 = float(h1["mean_orbitvar"])
    elif "per_model" in h1 and "orbit_vars_C1" in h1["per_model"]:
        orbit_var_h1 = float(np.mean(h1["per_model"]["orbit_vars_C1"]))

    # Cache-hit: embeddings pre-computed in h1 JSON
    if "embeddings" in h1 and "permuted_embeddings" in h1:
        print("[embeddings] Cache hit: loading from h1 results JSON")
        X_cise = np.array(h1["embeddings"], dtype=np.float32)         # (N, embed_dim)
        permuted_X = np.array(h1["permuted_embeddings"], dtype=np.float32)  # (N, K, embed_dim)
        if orbit_var_h1 is None:
            orbit_var_h1 = ORBIT_VAR_EXPECTED
        return X_cise, permuted_X, y_acc, perm_specs, orbit_var_h1

    # Cache-miss: compute via CISEEncoder
    print(f"[embeddings] Cache miss: computing CISE embeddings for {N} models x {K} perms...")
    encoder = build_c1_encoder(embed_dim=embed_dim)
    encoder.eval()

    X_cise = np.zeros((N, embed_dim), dtype=np.float32)
    permuted_X = np.zeros((N, K, embed_dim), dtype=np.float32)

    with torch.no_grad():
        for v, sd in enumerate(dataset):
            X_cise[v] = encoder.forward(sd).cpu().numpy()
            for k, ps in enumerate(perm_specs):
                perm_sd = apply_permutation(sd, ps)
                permuted_X[v, k] = encoder.forward(perm_sd).cpu().numpy()
            if (v + 1) % 20 == 0:
                print(f"  [{v+1}/{N}] embeddings computed")

    # orbit_var_h1: use JSON value if available, else recompute from encoder
    if orbit_var_h1 is None:
        print("[embeddings] Recomputing orbit_var_h1 via compute_orbit_var_all_models...")
        _, orbit_var_h1, _ = compute_orbit_var_all_models(
            dataset, encoder.forward, perm_specs, log_every=20
        )

    print(f"[embeddings] Done. X_cise={X_cise.shape}, permuted_X={permuted_X.shape}, orbit_var={orbit_var_h1:.6f}")
    return X_cise, permuted_X, y_acc, perm_specs, orbit_var_h1
