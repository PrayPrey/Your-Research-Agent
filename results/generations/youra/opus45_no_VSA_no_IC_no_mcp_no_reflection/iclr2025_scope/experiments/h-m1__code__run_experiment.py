#!/usr/bin/env python3
"""h-m1 mechanism hypothesis: duality vs random init reconstruction error."""

import os
import sys
import json
from typing import Dict, Any, List
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from transformers import BertModel

# Local imports
from duality_conversion import duality_init_ssm_from_attention
from selective_scan import selective_scan_ref
from random_init import random_init_ssm
from reconstruction_error import compute_reconstruction_error, paired_stats
from attention_reference import AttentionOutputCapture
from data_loader import load_wikitext_samples


def run_comparison(
    num_samples: int = 500,
    d_state: int = 64,
    device: str = "cuda"
) -> Dict[str, Any]:
    """Run duality vs random init comparison across 12 BERT layers."""
    print(f"Loading BERT model...")
    bert = BertModel.from_pretrained("bert-base-uncased").eval().to(device)
    d_model = 768

    print(f"Setting up attention capture hooks...")
    capture = AttentionOutputCapture(bert)

    print(f"Loading {num_samples} WikiText-103 samples...")
    samples = load_wikitext_samples(
        num_samples=num_samples,
        min_length=64,
        max_length=512
    )
    print(f"Loaded {len(samples)} samples")

    per_layer = {i: {"duality_errors": [], "random_errors": []} for i in range(12)}

    for sample_idx, sample in enumerate(samples):
        if sample_idx % 50 == 0:
            print(f"Processing sample {sample_idx}/{len(samples)}...")

        input_ids = sample["input_ids"].to(device)

        with torch.no_grad():
            embeddings = bert.embeddings(input_ids)
            capture.run_forward(input_ids)

        for layer_idx in range(12):
            attn_out = capture.get_layer_output(layer_idx)
            if attn_out is None:
                continue

            attn_layer = bert.encoder.layer[layer_idx].attention.self
            d_params = duality_init_ssm_from_attention(attn_layer, d_state)
            d_params = tuple(p.to(device) for p in d_params)

            r_params = random_init_ssm(d_model, d_state, seed=42 + layer_idx)
            r_params = tuple(p.to(device) for p in r_params)

            duality_out = selective_scan_ref(embeddings, *d_params)
            random_out = selective_scan_ref(embeddings, *r_params)

            err_d = compute_reconstruction_error(duality_out, attn_out)
            err_r = compute_reconstruction_error(random_out, attn_out)

            per_layer[layer_idx]["duality_errors"].append(err_d)
            per_layer[layer_idx]["random_errors"].append(err_r)

    capture.remove_hooks()
    return {"per_layer": per_layer, "num_samples": len(samples)}


def aggregate_results(per_layer: Dict[int, Dict[str, List[float]]]) -> Dict[str, Any]:
    """Aggregate results across all layers and compute global stats."""
    all_duality = []
    all_random = []

    for layer_data in per_layer.values():
        all_duality.extend(layer_data["duality_errors"])
        all_random.extend(layer_data["random_errors"])

    global_stats = paired_stats(all_duality, all_random)

    layer_stats = {}
    for i, layer_data in per_layer.items():
        if layer_data["duality_errors"] and layer_data["random_errors"]:
            layer_stats[i] = paired_stats(
                layer_data["duality_errors"],
                layer_data["random_errors"]
            )

    gate_pass = (
        global_stats["mean_duality"] < global_stats["mean_random"]
        and global_stats["reduction_pct"] > 0
    )

    return {
        **global_stats,
        "gate_pass": gate_pass,
        "per_layer_stats": layer_stats,
        "total_samples": len(all_duality) // 12
    }


def generate_figures(results: Dict[str, Any], output_dir: str = "figures/") -> List[str]:
    """Generate visualization figures."""
    os.makedirs(output_dir, exist_ok=True)
    paths = []

    # Bar chart: mean error comparison
    fig, ax = plt.subplots(figsize=(8, 6))
    methods = ["Duality", "Random"]
    means = [results["mean_duality"], results["mean_random"]]
    colors = ["#2ecc71", "#e74c3c"]
    bars = ax.bar(methods, means, color=colors)
    ax.set_ylabel("Mean Reconstruction Error (Frobenius norm)")
    ax.set_title(f"h-m1: Duality vs Random Initialization\nReduction: {results['reduction_pct']:.1f}%, p={results['p_value']:.4f}")
    for bar, val in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{val:.2f}", ha='center', va='bottom')
    path = os.path.join(output_dir, "bar_comparison.png")
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    paths.append(path)

    # Per-layer comparison
    fig, ax = plt.subplots(figsize=(12, 6))
    layers = list(results["per_layer_stats"].keys())
    duality_means = [results["per_layer_stats"][i]["mean_duality"] for i in layers]
    random_means = [results["per_layer_stats"][i]["mean_random"] for i in layers]
    x = range(len(layers))
    width = 0.35
    ax.bar([i - width/2 for i in x], duality_means, width, label="Duality", color="#2ecc71")
    ax.bar([i + width/2 for i in x], random_means, width, label="Random", color="#e74c3c")
    ax.set_xlabel("BERT Layer")
    ax.set_ylabel("Mean Reconstruction Error")
    ax.set_title("Per-Layer Reconstruction Error Comparison")
    ax.set_xticks(x)
    ax.set_xticklabels([str(i) for i in layers])
    ax.legend()
    path = os.path.join(output_dir, "per_layer_comparison.png")
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    paths.append(path)

    # Effect size per layer
    fig, ax = plt.subplots(figsize=(12, 6))
    cohens_d_vals = [results["per_layer_stats"][i]["cohens_d"] for i in layers]
    colors = ["#2ecc71" if d > 0 else "#e74c3c" for d in cohens_d_vals]
    ax.bar(x, cohens_d_vals, color=colors)
    ax.axhline(y=0.5, color='#3498db', linestyle='--', label="Medium effect (0.5)")
    ax.axhline(y=0.8, color='#9b59b6', linestyle='--', label="Large effect (0.8)")
    ax.set_xlabel("BERT Layer")
    ax.set_ylabel("Cohen's d (Effect Size)")
    ax.set_title("Per-Layer Effect Size (Duality Advantage)")
    ax.set_xticks(x)
    ax.set_xticklabels([str(i) for i in layers])
    ax.legend()
    path = os.path.join(output_dir, "effect_size_per_layer.png")
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    paths.append(path)

    print(f"Generated {len(paths)} figures in {output_dir}")
    return paths


def main() -> Dict[str, Any]:
    """Run full experiment pipeline."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    raw = run_comparison(num_samples=500, d_state=64, device=device)

    results = aggregate_results(raw["per_layer"])
    results["num_samples"] = raw["num_samples"]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    figures_dir = os.path.join(script_dir, "figures")
    results_dir = os.path.join(script_dir, "results")

    figures = generate_figures(results, figures_dir)
    results["figures"] = figures

    os.makedirs(results_dir, exist_ok=True)
    results_file = os.path.join(results_dir, "comparison_results.json")

    output = {k: v for k, v in results.items() if k != "per_layer_stats"}
    output["per_layer_summary"] = {
        str(k): {
            "mean_duality": v["mean_duality"],
            "mean_random": v["mean_random"],
            "reduction_pct": v["reduction_pct"],
            "cohens_d": v["cohens_d"]
        }
        for k, v in results["per_layer_stats"].items()
    }

    with open(results_file, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Results saved to {results_file}")

    print("\n" + "="*60)
    print("EXPERIMENT RESULTS")
    print("="*60)
    print(f"Samples: {results['num_samples']}")
    print(f"Mean Duality Error: {results['mean_duality']:.4f}")
    print(f"Mean Random Error:  {results['mean_random']:.4f}")
    print(f"Error Reduction:    {results['reduction_pct']:.2f}%")
    print(f"P-value:            {results['p_value']:.6f}")
    print(f"Cohen's d:          {results['cohens_d']:.4f}")
    print(f"Gate Pass:          {results['gate_pass']}")
    print("="*60)

    return results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results["gate_pass"] else 1)
