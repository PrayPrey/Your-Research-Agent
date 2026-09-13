"""H-M4: Probe invariance computation."""

import sys
import os
from typing import Dict, List, Tuple, Optional

import torch
import torch.nn as nn
import numpy as np

H_M3_CODE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "h-m3", "code")
H_M1_CODE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "h-m1", "code")
sys.path.insert(0, H_M3_CODE_DIR)
sys.path.insert(0, H_M1_CODE_DIR)

from test_variance import flatten_state_dict
from permute import generate_permutations, permute_state_dict


def compute_probe_invariance(
    model: nn.Module,
    state_dict: Dict[str, torch.Tensor],
    hidden_dims: Tuple[int, ...] = (32, 32),
    num_permutations: int = 10,
    device: str = "cpu",
) -> Tuple[float, List[float], float]:
    """Compute probe invariance for a model on a single weight vector.

    Uses RAW FLAT-VECTOR PERMUTATION (torch.randperm on indices) per experiment brief,
    NOT semantic neuron permutation. MLP should NOT be invariant to raw shuffling.

    Returns:
        (invariance_score, predictions, cv)

    invariance = max(0, 1 - min(cv, 1.0))
    Higher invariance means predictions are stable under permutation.
    """
    model.eval()
    predictions = []

    with torch.no_grad():
        flat_orig = flatten_state_dict(state_dict).squeeze(0).to(device)
        pred_orig = model(flat_orig.unsqueeze(0)).item()
        predictions.append(pred_orig)

        for perm_seed in range(num_permutations):
            torch.manual_seed(perm_seed)
            perm_indices = torch.randperm(flat_orig.size(0))
            flat_perm = flat_orig[perm_indices].to(device)
            pred_perm = model(flat_perm.unsqueeze(0)).item()
            predictions.append(pred_perm)

    preds_array = np.array(predictions)
    mean_pred = preds_array.mean()
    std_pred = preds_array.std()

    cv = std_pred / (abs(mean_pred) + 1e-8)
    invariance_score = max(0.0, 1.0 - min(cv, 1.0))

    return invariance_score, predictions, cv


def evaluate_population_invariance(
    model: nn.Module,
    test_population: List[Dict],
    hidden_dims: Tuple[int, ...] = (32, 32),
    num_permutations: int = 10,
    device: str = "cpu",
) -> Dict:
    """Evaluate probe invariance over test population.

    Returns:
        {"mean_invariance", "std_invariance", "mean_cv", "invariance_scores"}
    """
    invariance_scores = []
    cvs = []

    for model_data in test_population:
        inv, preds, cv = compute_probe_invariance(
            model,
            model_data["state_dict"],
            hidden_dims=model_data.get("hidden_dims", hidden_dims),
            num_permutations=num_permutations,
            device=device,
        )
        invariance_scores.append(inv)
        cvs.append(cv)

    return {
        "mean_invariance": float(np.mean(invariance_scores)),
        "std_invariance": float(np.std(invariance_scores)),
        "mean_cv": float(np.mean(cvs)),
        "invariance_scores": invariance_scores,
    }


if __name__ == "__main__":
    from mlp_model import MLPMatched
    from test_data import generate_test_mlp

    model = MLPMatched(input_dim=2274)
    sd = generate_test_mlp(hidden_dims=(32, 32), input_dim=32, output_dim=10, seed=0)

    inv, preds, cv = compute_probe_invariance(model, sd)
    print(f"Invariance: {inv:.4f}, CV: {cv:.4f}")
    print(f"Predictions (first 5): {preds[:5]}")
