"""H-M4: NFN control (optional - graceful skip if unavailable)."""

import sys
import os
from typing import Dict, List, Optional, Tuple
import warnings

import torch
import torch.nn as nn
import numpy as np

H_M3_CODE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "h-m3", "code")
sys.path.insert(0, H_M3_CODE_DIR)

from test_variance import flatten_state_dict


def load_nfn_model(input_dim: int) -> Optional[nn.Module]:
    """Load NFN model if available, else return None."""
    try:
        import nfn
        from nfn.layers import NPLinear, HNPPool

        class SimpleNFNRegressor(nn.Module):
            def __init__(self, in_dim: int):
                super().__init__()
                self.layer1 = NPLinear(in_dim, 256)
                self.pool = HNPPool()
                self.fc = nn.Linear(256, 1)

            def forward(self, x: torch.Tensor) -> torch.Tensor:
                x = torch.relu(self.layer1(x))
                x = self.pool(x)
                return self.fc(x)

        return SimpleNFNRegressor(input_dim)

    except ImportError:
        warnings.warn("nfn package not available. NFN control will be skipped.")
        return None
    except Exception as e:
        warnings.warn(f"Failed to load NFN model: {e}. NFN control will be skipped.")
        return None


def measure_nfn_invariance(
    nfn_model: Optional[nn.Module],
    test_population: List[Dict],
    num_permutations: int = 10,
    device: str = "cpu",
) -> Optional[Dict]:
    """Measure NFN invariance over test population.

    Returns None if nfn_model is None.
    """
    if nfn_model is None:
        return None

    from permute import generate_permutations, permute_state_dict

    nfn_model.eval()
    invariance_scores = []
    cvs = []

    with torch.no_grad():
        for model_data in test_population:
            state_dict = model_data["state_dict"]
            hidden_dims = model_data.get("hidden_dims", (32, 32))

            predictions = []
            flat_orig = flatten_state_dict(state_dict).to(device)
            pred_orig = nfn_model(flat_orig).item()
            predictions.append(pred_orig)

            for perm_seed in range(num_permutations):
                perms = generate_permutations(hidden_dims, base_seed=perm_seed)
                perm_sd = permute_state_dict(state_dict, n_hidden_layers=len(hidden_dims), perms=perms)
                flat_perm = flatten_state_dict(perm_sd).to(device)
                pred_perm = nfn_model(flat_perm).item()
                predictions.append(pred_perm)

            preds_array = np.array(predictions)
            mean_pred = preds_array.mean()
            std_pred = preds_array.std()

            cv = std_pred / (abs(mean_pred) + 1e-8)
            inv = max(0.0, 1.0 - min(cv, 1.0))

            invariance_scores.append(inv)
            cvs.append(cv)

    return {
        "mean_invariance": float(np.mean(invariance_scores)),
        "std_invariance": float(np.std(invariance_scores)),
        "mean_cv": float(np.mean(cvs)),
        "invariance_scores": invariance_scores,
    }


if __name__ == "__main__":
    model = load_nfn_model(2274)
    if model is None:
        print("NFN not available - expected in this environment")
    else:
        print("NFN loaded successfully")
