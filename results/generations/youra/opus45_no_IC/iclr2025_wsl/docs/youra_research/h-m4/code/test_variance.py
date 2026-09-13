#!/usr/bin/env python3
"""H-M3: Test that untrained MLP shows no permutation invariance.

Gate: coefficient_of_variation > 0.1 OR max_deviation > 0.01 (high variance = pass)
"""

import sys
import os
import json
import torch
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple, Optional

H_M3_CODE_DIR = Path(__file__).parent
H_M1_CODE_DIR = H_M3_CODE_DIR.parent.parent / "h-m1" / "code"
sys.path.insert(0, str(H_M1_CODE_DIR))

from test_data import generate_test_mlp
from permute import generate_permutations, permute_state_dict
from mlp_model import MLPMatched


def flatten_state_dict(state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
    """Concat all values flattened into [1, input_dim]."""
    return torch.cat([v.flatten() for v in state_dict.values()]).unsqueeze(0)


def run_mlp_variance_test(
    mlp: torch.nn.Module,
    base_state_dict: Dict[str, torch.Tensor],
    hidden_dims: Tuple[int, ...],
    n_hidden_layers: int = 2,
    n_perms: int = 10,
) -> Dict[str, List[float]]:
    """Run original + n_perms permuted predictions."""
    predictions = []
    mlp.eval()

    with torch.no_grad():
        x0 = flatten_state_dict(base_state_dict)
        pred_orig = mlp(x0).item()
        predictions.append(pred_orig)

        for seed in range(n_perms):
            perms = generate_permutations(hidden_dims, base_seed=seed)
            perm_sd = permute_state_dict(base_state_dict, n_hidden_layers, perms)
            x_perm = flatten_state_dict(perm_sd)
            pred = mlp(x_perm).item()
            predictions.append(pred)

    return {"predictions": predictions}


def compute_variance_metrics(predictions: List[float]) -> Dict[str, float]:
    """Compute variance metrics for untrained MLP test."""
    preds = torch.tensor(predictions)
    mean_val = preds.mean().item()
    std_val = preds.std().item()
    cv = std_val / (abs(mean_val) + 1e-12)
    max_dev = (preds - preds.mean()).abs().max().item()

    return {
        "mean": mean_val,
        "std": std_val,
        "coefficient_of_variation": cv,
        "max_deviation": max_dev,
    }


def gate_passed(metrics: Dict[str, float]) -> bool:
    """High variance = pass (opposite polarity from H-M1/H-M2)."""
    return metrics["coefficient_of_variation"] > 0.1 or metrics["max_deviation"] > 0.01


def plot_predictions_bar(predictions: List[float], out_path: str, title: str = "H-M3: MLP Permutation Variance") -> None:
    """Bar chart of predictions (reuse H-M1 style)."""
    plt.figure(figsize=(10, 6))
    labels = ["original"] + [f"perm_{i}" for i in range(len(predictions) - 1)]
    colors = ["#F44336"] + ["#FF9800"] * (len(predictions) - 1)

    plt.bar(range(len(predictions)), predictions, color=colors)
    plt.xticks(range(len(predictions)), labels, rotation=45)
    plt.xlabel("Configuration")
    plt.ylabel("MLP Prediction")
    plt.title(title)

    mean_pred = sum(predictions) / len(predictions)
    plt.axhline(y=mean_pred, color='b', linestyle='--', label=f'Mean: {mean_pred:.6f}')
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_prediction_histogram(predictions: List[float], out_path: str) -> None:
    """Histogram of predictions (expect wide spread)."""
    plt.figure(figsize=(8, 6))
    plt.hist(predictions, bins=20, edgecolor='black', alpha=0.7, color='#FF9800')
    plt.xlabel("Prediction Value")
    plt.ylabel("Count")
    plt.title("H-M3: MLP Prediction Distribution (Should be Wide)")
    plt.axvline(x=sum(predictions) / len(predictions), color='b', linestyle='--', label='Mean')
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_nfn_vs_mlp_comparison(
    mlp_predictions: List[float],
    out_path: str,
    nfn_predictions: Optional[List[float]] = None,
) -> None:
    """Side-by-side NFN (tight) vs MLP (scatter) comparison."""
    fig, axes = plt.subplots(1, 2 if nfn_predictions else 1, figsize=(12 if nfn_predictions else 8, 6))

    if nfn_predictions:
        ax1, ax2 = axes
        ax1.scatter(range(len(nfn_predictions)), nfn_predictions, c='#2196F3', s=100, label='NFN')
        ax1.axhline(y=sum(nfn_predictions) / len(nfn_predictions), color='r', linestyle='--')
        ax1.set_xlabel("Configuration")
        ax1.set_ylabel("Prediction")
        ax1.set_title("NFN: Tight Clustering (Invariant)")
        ax1.legend()

        ax2.scatter(range(len(mlp_predictions)), mlp_predictions, c='#F44336', s=100, label='MLP')
        ax2.axhline(y=sum(mlp_predictions) / len(mlp_predictions), color='b', linestyle='--')
        ax2.set_xlabel("Configuration")
        ax2.set_ylabel("Prediction")
        ax2.set_title("MLP: Wide Scatter (No Invariance)")
        ax2.legend()
    else:
        ax = axes if not nfn_predictions else axes
        ax.scatter(range(len(mlp_predictions)), mlp_predictions, c='#F44336', s=100, label='MLP')
        ax.axhline(y=sum(mlp_predictions) / len(mlp_predictions), color='b', linestyle='--')
        ax.set_xlabel("Configuration")
        ax.set_ylabel("Prediction")
        ax.set_title("MLP: Prediction Scatter (No NFN comparison available)")
        ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def main():
    """Orchestrate H-M3 variance test."""
    H_M3_DIR = H_M3_CODE_DIR.parent
    H_M2_DIR = H_M3_DIR.parent / "h-m2"

    FIGURES_DIR = H_M3_DIR / "figures"
    RESULTS_PATH = H_M3_DIR / "results.json"

    FIGURES_DIR.mkdir(exist_ok=True)

    print("H-M3: Untrained MLP Permutation Variance Test")
    print("=" * 50)

    print("\n1. Generating test MLP weights (seed=42)...")
    base_sd = generate_test_mlp(hidden_dims=(32, 32), input_dim=32, output_dim=10, seed=42)
    print(f"   Keys: {list(base_sd.keys())}")

    print("\n2. Creating untrained MLPMatched (seed=1042)...")
    input_dim = flatten_state_dict(base_sd).shape[1]
    torch.manual_seed(1042)
    mlp = MLPMatched(input_dim)
    mlp.eval()
    print(f"   Input dim: {input_dim}")

    print("\n3. Running variance test (original + 10 permuted)...")
    result = run_mlp_variance_test(mlp, base_sd, hidden_dims=(32, 32), n_perms=10)
    predictions = result["predictions"]
    print(f"   Predictions: {[f'{p:.6f}' for p in predictions]}")

    print("\n4. Computing variance metrics...")
    metrics = compute_variance_metrics(predictions)
    passed = gate_passed(metrics)

    print(f"   Mean:   {metrics['mean']:.8f}")
    print(f"   Std:    {metrics['std']:.8f}")
    print(f"   CV:     {metrics['coefficient_of_variation']:.8f}")
    print(f"   MaxDev: {metrics['max_deviation']:.8f}")
    print(f"\n   GATE PASSED: {passed}")

    print("\n5. Generating visualizations...")
    plot_predictions_bar(predictions, str(FIGURES_DIR / "predictions_bar.png"))
    plot_prediction_histogram(predictions, str(FIGURES_DIR / "prediction_histogram.png"))

    nfn_predictions = None
    h_m2_results = H_M2_DIR / "results.json"
    if h_m2_results.exists():
        try:
            with open(h_m2_results) as f:
                nfn_predictions = json.load(f).get("predictions")
            print(f"   Loaded NFN predictions from H-M2 for comparison")
        except Exception:
            pass

    plot_nfn_vs_mlp_comparison(predictions, str(FIGURES_DIR / "nfn_vs_mlp.png"), nfn_predictions)
    print(f"   Saved to {FIGURES_DIR}")

    print("\n6. Saving results...")
    results = {
        "hypothesis_id": "H-M3",
        "hypothesis_type": "MECHANISM",
        "statement": "Untrained MLP shows no permutation invariance (correlation < 0.3)",
        "predictions": predictions,
        "metrics": metrics,
        "gate_type": "SHOULD_WORK",
        "gate_passed": passed,
        "gate_criteria": "coefficient_of_variation > 0.1 OR max_deviation > 0.01",
        "n_permutations": 10,
        "test_seed": 42,
        "mlp_init_seed": 1042,
    }

    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"   Saved to {RESULTS_PATH}")

    print("\n" + "=" * 50)
    print(f"H-M3 RESULT: {'PASSED' if passed else 'FAILED'}")
    print("=" * 50)

    return passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
