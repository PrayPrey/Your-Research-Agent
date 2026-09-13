#!/usr/bin/env python3
"""H-M2: Test NFN prediction invariance under weight permutation.

Extends H-M1's layer-level invariance to final scalar predictions.
Gate: max_deviation < 1e-5
"""

import sys
import os
import json
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Any, Dict, List, Tuple

H_M2_CODE_DIR = Path(__file__).parent
H_M1_CODE_DIR = H_M2_CODE_DIR.parent.parent / "h-m1" / "code"
H_E1_CODE_DIR = H_M2_CODE_DIR.parent.parent / "h-e1" / "code"

sys.path.insert(0, str(H_M1_CODE_DIR))
sys.path.insert(0, str(H_E1_CODE_DIR))

from test_data import generate_test_mlp
from permute import generate_permutations, permute_state_dict
from metrics import compute_invariance_metrics, gate_passed
from test_invariance import (
    load_nfn_model,
    state_dict_to_wsfeat,
    run_predictions,
    plot_predictions_bar,
    plot_deviation_heatmap,
    plot_prediction_histogram,
)


def main():
    """Orchestrate H-M2 prediction invariance test."""
    H_M2_DIR = H_M2_CODE_DIR.parent
    H_E1_DIR = H_M2_DIR.parent / "h-e1"

    CHECKPOINT_PATH = H_E1_DIR / "checkpoints" / "nfn_model.pt"
    FIGURES_DIR = H_M2_DIR / "figures"
    RESULTS_PATH = H_M2_DIR / "results.json"

    FIGURES_DIR.mkdir(exist_ok=True)

    print("H-M2: NFN Prediction Invariance Test")
    print("=" * 50)

    print("\n1. Creating test MLP matching H-E1 checkpoint architecture...")
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
    passed = gate_passed(metrics, dev_threshold=1e-5)

    print(f"   Mean:        {metrics['mean']:.8f}")
    print(f"   Std:         {metrics['std']:.8e}")
    print(f"   Max Dev:     {metrics['max_deviation']:.8e}")
    print(f"   Inv Score:   {metrics['invariance_score']}")
    print(f"   Inv Corr:    {metrics['invariance_correlation']:.8f}")
    print(f"\n   GATE PASSED: {passed}")

    print("\n6. Generating visualizations...")
    plot_predictions_bar(predictions, str(FIGURES_DIR / "predictions_bar.png"))
    plot_deviation_heatmap(predictions, str(FIGURES_DIR / "deviation_heatmap.png"))
    plot_prediction_histogram(predictions, str(FIGURES_DIR / "prediction_histogram.png"))
    print(f"   Saved to {FIGURES_DIR}")

    print("\n7. Saving results...")
    results = {
        "hypothesis_id": "H-M2",
        "hypothesis_type": "MECHANISM",
        "statement": "NFN predictions identical under weight permutation (diff < 1e-5)",
        "predictions": predictions,
        "metrics": metrics,
        "gate_type": "SHOULD_WORK",
        "gate_passed": passed,
        "gate_criteria": "max_deviation < 1e-5",
        "n_permutations": 10,
        "test_seed": 42,
    }

    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"   Saved to {RESULTS_PATH}")

    print("\n" + "=" * 50)
    print(f"H-M2 RESULT: {'PASSED' if passed else 'FAILED'}")
    print("=" * 50)

    return passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
