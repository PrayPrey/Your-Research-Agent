"""Main experiment runner for h-e1 existence validation."""

import json
import os
from pathlib import Path
from typing import Dict, Any, List

import torch
import matplotlib.pyplot as plt
from transformers import BertModel

from duality_conversion import duality_init_ssm_from_attention
from selective_scan import selective_scan_ref
from stability_validation import validate_ssm_stability, compute_stability_metrics
from data_loader import load_wikitext_samples


def run_existence_validation(
    num_samples: int = 100,
    d_state: int = 64,
    device: str = "cuda"
) -> Dict[str, Any]:
    """
    Run h-e1 existence validation experiment.

    Returns:
        Results dict with pass/fail and metrics
    """
    if device == "cuda" and not torch.cuda.is_available():
        device = "cpu"

    print(f"Running on device: {device}")

    # Load BERT
    print("Loading BERT-base-uncased...")
    bert = BertModel.from_pretrained("bert-base-uncased")
    bert.eval()
    bert.to(device)

    # Extract layer 0 attention
    layer_0_attn = bert.encoder.layer[0].attention.self

    # Convert to SSM via duality
    print(f"Converting attention to SSM (d_state={d_state})...")
    A, B, C, D, dt = duality_init_ssm_from_attention(layer_0_attn, d_state=d_state)

    # Move SSM params to device
    A, B, C, D, dt = A.to(device), B.to(device), C.to(device), D.to(device), dt.to(device)

    # Load data
    print(f"Loading {num_samples} WikiText-103 samples...")
    samples = load_wikitext_samples(num_samples=num_samples, min_length=64, max_length=512)
    print(f"Loaded {len(samples)} samples")

    # Validate
    results = []
    stable_count = 0

    for i, sample in enumerate(samples):
        input_ids = sample["input_ids"].to(device)

        with torch.no_grad():
            # Get embeddings
            embeddings = bert.embeddings(input_ids)

            # Get BERT layer 0 output for reference
            bert_out = bert(input_ids).last_hidden_state

            # Run SSM
            ssm_out = selective_scan_ref(embeddings, A, B, C, D, dt)

            # Validate
            is_stable, mag_ratio = validate_ssm_stability(ssm_out, bert_out)
            metrics = compute_stability_metrics(ssm_out, bert_out)

        results.append({
            "sample_idx": i,
            "is_stable": is_stable,
            "magnitude_ratio": mag_ratio,
            **metrics
        })

        if is_stable:
            stable_count += 1

        if (i + 1) % 20 == 0:
            print(f"  Processed {i + 1}/{len(samples)}, stable: {stable_count}/{i + 1}")

    # Aggregate
    all_stable = all(r["is_stable"] for r in results)
    ratios = [r["magnitude_ratio"] for r in results]
    max_ratio = max(ratios) if ratios else 0.0
    mean_ratio = sum(ratios) / len(ratios) if ratios else 0.0

    nan_inf_rate = sum(not r["is_stable"] for r in results) / len(results) if results else 1.0

    # Gate condition: all stable AND max ratio < 10
    gate_pass = all_stable and max_ratio < 10.0

    return {
        "pass": gate_pass,
        "nan_inf_rate": nan_inf_rate,
        "magnitude_ratio_mean": mean_ratio,
        "magnitude_ratio_max": max_ratio,
        "samples_tested": len(samples),
        "stable_samples": stable_count,
        "per_sample_results": results
    }


def generate_figures(
    results: Dict[str, Any],
    output_dir: str = "figures/"
) -> List[str]:
    """Generate visualization figures."""
    os.makedirs(output_dir, exist_ok=True)
    saved = []

    per_sample = results.get("per_sample_results", [])
    if not per_sample:
        return saved

    # Figure 1: Gate metrics bar chart
    fig, ax = plt.subplots(figsize=(8, 5))
    metrics = ["NaN/Inf Rate", "Max Magnitude Ratio"]
    values = [results["nan_inf_rate"] * 100, results["magnitude_ratio_max"]]
    thresholds = [0.0, 10.0]
    colors = ["green" if v <= t else "red" for v, t in zip(values, thresholds)]

    bars = ax.bar(metrics, values, color=colors, alpha=0.7)
    ax.axhline(y=10.0, color="red", linestyle="--", label="Threshold (10x)")
    ax.set_ylabel("Value")
    ax.set_title("h-e1 Gate Metrics")
    ax.legend()

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{val:.2f}", ha="center", va="bottom")

    path1 = os.path.join(output_dir, "gate_metrics.png")
    plt.savefig(path1, dpi=150, bbox_inches="tight")
    plt.close()
    saved.append(path1)

    # Figure 2: Magnitude ratio scatter
    fig, ax = plt.subplots(figsize=(10, 5))
    indices = [r["sample_idx"] for r in per_sample]
    ratios = [r["magnitude_ratio"] for r in per_sample]

    ax.scatter(indices, ratios, alpha=0.6, s=20)
    ax.axhline(y=10.0, color="red", linestyle="--", label="Threshold (10x)")
    ax.set_xlabel("Sample Index")
    ax.set_ylabel("Magnitude Ratio (SSM/Transformer)")
    ax.set_title("Magnitude Ratio per Sample")
    ax.legend()

    path2 = os.path.join(output_dir, "magnitude_ratio_scatter.png")
    plt.savefig(path2, dpi=150, bbox_inches="tight")
    plt.close()
    saved.append(path2)

    # Figure 3: Output value distribution (histogram of min/max)
    fig, ax = plt.subplots(figsize=(8, 5))
    max_vals = [r["max_value"] for r in per_sample]
    min_vals = [r["min_value"] for r in per_sample]

    ax.hist(max_vals, bins=30, alpha=0.5, label="Max values")
    ax.hist(min_vals, bins=30, alpha=0.5, label="Min values")
    ax.set_xlabel("Output Value")
    ax.set_ylabel("Frequency")
    ax.set_title("SSM Output Value Distribution")
    ax.legend()

    path3 = os.path.join(output_dir, "output_distribution.png")
    plt.savefig(path3, dpi=150, bbox_inches="tight")
    plt.close()
    saved.append(path3)

    return saved


def main():
    """Main entry point."""
    print("=" * 60)
    print("h-e1: Duality-based SSM Initialization Existence Validation")
    print("=" * 60)

    # Run validation
    results = run_existence_validation(
        num_samples=100,
        d_state=64,
        device="cuda"
    )

    # Save results
    os.makedirs("results", exist_ok=True)
    results_file = "results/validation_results.json"

    # Remove per-sample for JSON (too verbose)
    save_results = {k: v for k, v in results.items() if k != "per_sample_results"}
    save_results["per_sample_summary"] = {
        "total": len(results.get("per_sample_results", [])),
        "stable": results.get("stable_samples", 0)
    }

    with open(results_file, "w") as f:
        json.dump(save_results, f, indent=2)
    print(f"\nResults saved to: {results_file}")

    # Generate figures
    figures = generate_figures(results)
    print(f"Figures saved: {figures}")

    # Summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Gate Pass: {'✅ PASS' if results['pass'] else '❌ FAIL'}")
    print(f"NaN/Inf Rate: {results['nan_inf_rate'] * 100:.1f}% (threshold: 0%)")
    print(f"Magnitude Ratio (max): {results['magnitude_ratio_max']:.2f} (threshold: 10x)")
    print(f"Magnitude Ratio (mean): {results['magnitude_ratio_mean']:.2f}")
    print(f"Samples Tested: {results['samples_tested']}")
    print(f"Stable Samples: {results['stable_samples']}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
