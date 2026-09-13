#!/usr/bin/env python3
"""H-M1: Loss Landscape Geometry Analysis Experiment"""

import os
import sys
import json
import torch
import random
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import LANDSCAPE_CONFIG, BENCHMARKS, MODEL_ID_BASELINE, LORA_CONFIG_TRANSFORMER, LORA_CONFIG_MAMBA
from data import load_landscape_eval_set
from model import load_baseline_model, load_proposed_model, load_tokenizer
from landscape import measure_sharpness_sam, compute_hessian_eigenvalues
from metrics import compute_kl_divergence, spectral_norm_ratio, trace_ratio, check_gate_conditions
from visualize import plot_all_figures


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def analyze_model(model, dataloader, model_name, device):
    """Compute sharpness and Hessian eigenvalues for a model."""
    print(f"  Computing SAM sharpness for {model_name}...")
    sharpness = measure_sharpness_sam(model, dataloader, max_batches=4)
    print(f"    Sharpness: {sharpness:.6f}")

    print(f"  Computing Hessian eigenvalues for {model_name}...")
    hessian = compute_hessian_eigenvalues(model, dataloader, max_batches=2)
    print(f"    Top eigenvalue: {hessian['spectral_norm']:.6f}")
    print(f"    Trace estimate: {hessian['trace']:.6f}")

    return {
        "sharpness": sharpness,
        "eigenvalues": hessian["eigenvalues"],
        "trace": hessian["trace"],
        "spectral_norm": hessian["spectral_norm"],
    }


def main():
    set_seed(LANDSCAPE_CONFIG["seed"])

    script_dir = os.path.dirname(os.path.abspath(__file__))
    hypothesis_folder = os.path.dirname(script_dir)
    figures_folder = os.path.join(hypothesis_folder, "figures")
    os.makedirs(figures_folder, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    print("Loading tokenizer...")
    tokenizer = load_tokenizer()

    results = {}
    all_transformer_eigenvalues = []
    all_mamba_eigenvalues = []
    sharpness_results = {"transformer": [], "mamba": []}

    for dataset_name in ["gsm8k", "nq"]:
        print(f"\n{'='*60}")
        print(f"Analyzing {dataset_name.upper()}...")
        print(f"{'='*60}")

        print(f"Loading {dataset_name} evaluation set (500 samples)...")
        dataloader = load_landscape_eval_set(
            dataset_name, tokenizer,
            max_length=LANDSCAPE_CONFIG["max_length"],
            num_samples=LANDSCAPE_CONFIG["eval_samples"]
        )

        print("Loading Transformer baseline...")
        transformer_model = load_baseline_model(LORA_CONFIG_TRANSFORMER)
        transformer_model.eval()

        print("\nAnalyzing Transformer...")
        trans_results = analyze_model(transformer_model, dataloader, "Transformer", device)

        del transformer_model
        torch.cuda.empty_cache()

        print("Loading Mamba proposed model...")
        mamba_model = load_proposed_model(LORA_CONFIG_MAMBA)
        mamba_model = mamba_model.to(device).half()
        mamba_model.eval()

        print("\nAnalyzing Mamba...")
        mamba_results = analyze_model(mamba_model, dataloader, "Mamba", device)

        del mamba_model
        torch.cuda.empty_cache()

        results[dataset_name] = {
            "transformer": trans_results,
            "mamba": mamba_results,
        }

        all_transformer_eigenvalues.extend(trans_results["eigenvalues"])
        all_mamba_eigenvalues.extend(mamba_results["eigenvalues"])
        sharpness_results["transformer"].append(trans_results["sharpness"])
        sharpness_results["mamba"].append(mamba_results["sharpness"])

    print("\n" + "="*60)
    print("Computing aggregate metrics...")
    print("="*60)

    avg_sharpness_trans = np.mean(sharpness_results["transformer"])
    avg_sharpness_mamba = np.mean(sharpness_results["mamba"])

    kl_div = compute_kl_divergence(all_transformer_eigenvalues, all_mamba_eigenvalues)
    spec_ratio = spectral_norm_ratio(
        {"spectral_norm": max(all_transformer_eigenvalues)},
        {"spectral_norm": max(all_mamba_eigenvalues)}
    )
    tr_ratio = trace_ratio(
        {"trace": sum(all_transformer_eigenvalues)},
        {"trace": sum(all_mamba_eigenvalues)}
    )

    print(f"\nAggregate Results:")
    print(f"  Avg Transformer Sharpness: {avg_sharpness_trans:.6f}")
    print(f"  Avg Mamba Sharpness: {avg_sharpness_mamba:.6f}")
    print(f"  KL Divergence: {kl_div:.6f}")
    print(f"  Spectral Norm Ratio: {spec_ratio:.6f}")
    print(f"  Trace Ratio: {tr_ratio:.6f}")

    gate = check_gate_conditions(avg_sharpness_trans, avg_sharpness_mamba, kl_div)

    print(f"\n{'='*60}")
    print("GATE CHECK (MUST_WORK)")
    print(f"{'='*60}")
    print(f"  Sharpness Delta: {gate['sharpness_delta']:.6f}")
    print(f"  Sharpness Delta %: {gate['sharpness_delta_pct']*100:.2f}%")
    print(f"  Primary (|delta|>10%): {'PASS' if gate['primary_pass'] else 'FAIL'}")
    print(f"  KL Divergence: {gate['kl_divergence']:.6f}")
    print(f"  Secondary (KL>0.1): {'PASS' if gate['secondary_pass'] else 'FAIL'}")
    print(f"  GATE RESULT: {'PASS' if gate['gate_pass'] else 'FAIL'}")

    final_results = {
        "hypothesis_id": "h-m1",
        "timestamp": datetime.now().isoformat(),
        "datasets": results,
        "aggregate": {
            "avg_sharpness_transformer": avg_sharpness_trans,
            "avg_sharpness_mamba": avg_sharpness_mamba,
            "kl_divergence": kl_div,
            "spectral_norm_ratio": spec_ratio,
            "trace_ratio": tr_ratio,
        },
        "gate": gate,
    }

    results_path = os.path.join(hypothesis_folder, "experiment_results.json")
    with open(results_path, "w") as f:
        json.dump(final_results, f, indent=2, default=lambda x: float(x) if isinstance(x, np.floating) else x)
    print(f"\nResults saved: {results_path}")

    print("\nGenerating figures...")
    plot_all_figures(results, figures_folder)

    return final_results


if __name__ == "__main__":
    results = main()
    print("\nEXPERIMENT COMPLETE")
