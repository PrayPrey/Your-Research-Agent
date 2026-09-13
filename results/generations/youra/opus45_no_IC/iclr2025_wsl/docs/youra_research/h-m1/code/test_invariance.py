#!/usr/bin/env python3
"""H-M1: Test NFN permutation invariance.

Validates that NFN produces identical outputs for permuted MLP weights.
Gate: max_deviation < 1e-5 OR correlation > 0.99
"""

import sys
import os
import json
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Any, Dict, List, Tuple

H_M1_CODE_DIR = Path(__file__).parent
H_E1_CODE_DIR = H_M1_CODE_DIR.parent.parent / "h-e1" / "code"
sys.path.insert(0, str(H_E1_CODE_DIR))

from test_data import generate_test_mlp
from permute import generate_permutations, permute_state_dict
from metrics import compute_invariance_metrics, gate_passed


def load_nfn_model(
    checkpoint_path: str,
    network_spec: Any,
    nfn_channels: int = 32,
) -> nn.Module:
    """Load trained NFN from H-E1 checkpoint."""
    from model import NFNRegressor

    model = NFNRegressor(network_spec, nfn_channels=nfn_channels)
    model.load_state_dict(torch.load(checkpoint_path, map_location="cpu"))
    model.eval()
    return model


def state_dict_to_wsfeat(state_dict: Dict[str, torch.Tensor], network_spec: Any) -> Any:
    """Convert state_dict to batched WeightSpaceFeatures [B=1]."""
    from nfn.common import state_dict_to_tensors, WeightSpaceFeatures

    wts, bs = state_dict_to_tensors(state_dict)
    wts_batched = [w.unsqueeze(0) for w in wts]
    bs_batched = [b.unsqueeze(0) for b in bs]
    return WeightSpaceFeatures(wts_batched, bs_batched)


def run_predictions(
    nfn_model: nn.Module,
    base_state_dict: Dict[str, torch.Tensor],
    hidden_dims: Tuple[int, ...],
    network_spec: Any,
    n_perms: int = 10,
) -> List[float]:
    """Run NFN on original + n_perms permuted state_dicts."""
    predictions = []

    wsfeat = state_dict_to_wsfeat(base_state_dict, network_spec)
    with torch.no_grad():
        pred = nfn_model(wsfeat)
        predictions.append(pred.item())

    for seed in range(n_perms):
        perms = generate_permutations(hidden_dims, base_seed=seed)
        perm_sd = permute_state_dict(base_state_dict, len(hidden_dims), perms)
        wsfeat_perm = state_dict_to_wsfeat(perm_sd, network_spec)
        with torch.no_grad():
            pred = nfn_model(wsfeat_perm)
            predictions.append(pred.item())

    return predictions


def plot_predictions_bar(predictions: List[float], out_path: str) -> None:
    """Bar chart of original + permuted predictions."""
    plt.figure(figsize=(10, 6))
    labels = ["original"] + [f"perm_{i}" for i in range(len(predictions) - 1)]
    colors = ["#2196F3"] + ["#4CAF50"] * (len(predictions) - 1)

    plt.bar(range(len(predictions)), predictions, color=colors)
    plt.xticks(range(len(predictions)), labels, rotation=45)
    plt.xlabel("Configuration")
    plt.ylabel("NFN Prediction")
    plt.title("H-M1: NFN Permutation Invariance Test")

    mean_pred = sum(predictions) / len(predictions)
    plt.axhline(y=mean_pred, color='r', linestyle='--', label=f'Mean: {mean_pred:.6f}')
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_deviation_heatmap(predictions: List[float], out_path: str) -> None:
    """Pairwise deviation heatmap."""
    n = len(predictions)
    deviations = [[abs(predictions[i] - predictions[j]) for j in range(n)] for i in range(n)]

    plt.figure(figsize=(8, 6))
    plt.imshow(deviations, cmap='Reds', aspect='auto')
    plt.colorbar(label='Absolute Deviation')

    labels = ["orig"] + [f"p{i}" for i in range(n - 1)]
    plt.xticks(range(n), labels)
    plt.yticks(range(n), labels)
    plt.title("Pairwise Prediction Deviations")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_prediction_histogram(predictions: List[float], out_path: str) -> None:
    """Histogram of predictions."""
    plt.figure(figsize=(8, 6))
    plt.hist(predictions, bins=20, edgecolor='black', alpha=0.7)
    plt.xlabel("Prediction Value")
    plt.ylabel("Count")
    plt.title("Distribution of Predictions (Should be Spike)")
    plt.axvline(x=sum(predictions) / len(predictions), color='r', linestyle='--', label='Mean')
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def main():
    """Orchestrate H-M1 permutation invariance test."""
    H_M1_DIR = H_M1_CODE_DIR.parent
    H_E1_DIR = H_M1_DIR.parent / "h-e1"

    CHECKPOINT_PATH = H_E1_DIR / "checkpoints" / "nfn_model.pt"
    FIGURES_DIR = H_M1_DIR / "figures"
    RESULTS_PATH = H_M1_DIR / "results.json"

    FIGURES_DIR.mkdir(exist_ok=True)

    print("H-M1: NFN Permutation Invariance Test")
    print("=" * 50)

    print("\n1. Creating test MLP matching H-E1 checkpoint architecture...")
    # H-E1 checkpoint was trained on 32-32-32-10 MLPs (discovered from in_embed shape)
    base_sd = generate_test_mlp(hidden_dims=(32, 32), input_dim=32, output_dim=10, seed=42)
    print(f"   Keys: {list(base_sd.keys())}")
    print(f"   Shapes: {[v.shape for v in base_sd.values()]}")

    print("\n2. Building network_spec from sample...")
    from nfn.common import state_dict_to_tensors, network_spec_from_wsfeat, WeightSpaceFeatures
    wts, bs = state_dict_to_tensors(base_sd)
    wts_b = [w.unsqueeze(0) for w in wts]
    bs_b = [b.unsqueeze(0) for b in bs]
    wsfeat_sample = WeightSpaceFeatures(wts_b, bs_b)
    network_spec = network_spec_from_wsfeat(wsfeat_sample)

    print("\n3. Loading NFN model from H-E1 checkpoint...")
    if not CHECKPOINT_PATH.exists():
        raise FileNotFoundError(f"Checkpoint not found: {CHECKPOINT_PATH}")
    nfn_model = load_nfn_model(str(CHECKPOINT_PATH), network_spec, nfn_channels=32)
    print(f"   Model loaded, eval mode: {not nfn_model.training}")

    print("\n4. Running predictions (original + 10 permuted)...")
    predictions = run_predictions(
        nfn_model, base_sd,
        hidden_dims=(32, 32),
        network_spec=network_spec,
        n_perms=10
    )
    print(f"   Predictions: {predictions}")

    print("\n5. Computing invariance metrics...")
    metrics = compute_invariance_metrics(predictions)
    passed = gate_passed(metrics)

    print(f"   Mean:        {metrics['mean']:.8f}")
    print(f"   Std:         {metrics['std']:.8e}")
    print(f"   Max Dev:     {metrics['max_deviation']:.8e}")
    print(f"   Inv Score:   {metrics['invariance_score']}")
    print(f"   Inv Corr:    {metrics['invariance_correlation']:.8f}")
    print(f"\n   GATE PASSED: {passed}")

    print("\n6. Generating visualizations...")
    plot_predictions_bar(predictions, str(FIGURES_DIR / "permutation_invariance.png"))
    plot_deviation_heatmap(predictions, str(FIGURES_DIR / "deviation_heatmap.png"))
    plot_prediction_histogram(predictions, str(FIGURES_DIR / "prediction_histogram.png"))
    print(f"   Saved to {FIGURES_DIR}")

    print("\n7. Saving results...")
    results = {
        "hypothesis_id": "H-M1",
        "hypothesis_type": "MECHANISM",
        "statement": "NFN equivariant layers produce permutation-invariant outputs (correlation > 0.99)",
        "predictions": predictions,
        "metrics": metrics,
        "gate_type": "MUST_WORK",
        "gate_passed": passed,
        "gate_criteria": "max_deviation < 1e-5 OR invariance_correlation > 0.99",
        "n_permutations": 10,
        "test_seed": 42,
    }

    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"   Saved to {RESULTS_PATH}")

    print("\n" + "=" * 50)
    print(f"H-M1 RESULT: {'PASSED' if passed else 'FAILED'}")
    print("=" * 50)

    return passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
