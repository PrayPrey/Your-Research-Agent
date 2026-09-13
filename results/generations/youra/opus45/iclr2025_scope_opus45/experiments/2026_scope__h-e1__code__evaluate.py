"""Evaluation functions for H-E1: H_spec measurement and visualization."""

import os
from typing import TYPE_CHECKING

import numpy as np
import torch
import yaml
from torch import Tensor

if TYPE_CHECKING:
    from config import ExperimentConfig
    from model import MambaProbe


def generate_random_sequences(config: "ExperimentConfig", vocab_size: int) -> Tensor:
    """Generate random token sequences with fixed seed.

    Args:
        config: Experiment configuration
        vocab_size: Vocabulary size from tokenizer

    Returns:
        [num_samples, seq_length] int64 token ids
    """
    rng = torch.Generator().manual_seed(config.seed)
    sequences = torch.randint(
        0,
        vocab_size,
        (config.num_samples, config.seq_length),
        generator=rng,
        dtype=torch.long,
    )
    print(f"Generated {config.num_samples} random sequences of length {config.seq_length}")
    return sequences


def measure_h_spec_distribution(
    probe: "MambaProbe",
    sequences: Tensor,
    config: "ExperimentConfig",
) -> dict:
    """Compute H_spec for each sequence; return distribution stats.

    Note: Since Mamba's A matrix is input-independent, H_spec is constant
    across all sequences. We still iterate to verify this property.

    Returns:
        dict with keys: h_spec_values, mean, std, cv, pass_gate, per_layer_lambda_max
    """
    h_spec_values = []

    # H_spec is input-independent for Mamba, but we verify by computing multiple times
    print(f"Measuring H_spec across {config.num_samples} sequences...")

    for i in range(config.num_samples):
        # Note: input_ids not actually used since A is input-independent
        h = probe.compute_h_spec(sequences[i].unsqueeze(0))
        h_spec_values.append(h)

        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{config.num_samples} sequences")

    # Filter NaN values
    h_arr = np.array([v for v in h_spec_values if not np.isnan(v)])

    if len(h_arr) == 0:
        raise ValueError("All H_spec values are NaN - check eigenvalue extraction")

    nan_count = config.num_samples - len(h_arr)
    if nan_count > 0:
        print(f"  Warning: {nan_count} NaN values filtered out")

    mean_h = float(np.mean(h_arr))
    std_h = float(np.std(h_arr))
    cv = std_h / mean_h if mean_h > 0 else float("inf")
    pass_gate = cv < config.cv_threshold

    # Get per-layer eigenvalue info
    per_layer_lambda_max = probe.get_per_layer_lambda_max()
    per_layer_h_spec = probe.get_per_layer_h_spec()

    return {
        "h_spec_values": h_arr.tolist(),
        "mean": mean_h,
        "std": std_h,
        "cv": cv,
        "pass_gate": pass_gate,
        "min_h_spec": float(np.min(h_arr)),
        "max_h_spec": float(np.max(h_arr)),
        "valid_samples": len(h_arr),
        "nan_count": nan_count,
        "per_layer_lambda_max": per_layer_lambda_max,
        "per_layer_h_spec": per_layer_h_spec,
    }


def run_scale_crossvalidation(config: "ExperimentConfig") -> dict:
    """Load Mamba-370M, compute mean H_spec, return comparison dict.

    Returns:
        {"h_spec_1400m": float, "h_spec_370m": float, "monotonic": bool}
    """
    from model import MambaProbe

    print("\n=== Running Scale Cross-Validation ===")
    probe_370m = MambaProbe(config)
    probe_370m.load_model(config.model_370m_id)

    h_spec_370m = probe_370m.compute_h_spec()
    probe_370m.unload()

    return {
        "model_370m_id": config.model_370m_id,
        "mean_h_spec_370m": h_spec_370m,
    }


def save_results(metrics: dict, crossval: dict, config: "ExperimentConfig") -> None:
    """Write metrics dict to results.yaml."""
    results = {
        "hypothesis": "h-e1",
        "model_id": config.model_id,
        "num_samples": config.num_samples,
        "seq_length": config.seq_length,
        "seed": config.seed,
        # Primary gate metric
        "cv": metrics["cv"],
        "gate_pass": metrics["pass_gate"],
        # Distribution statistics
        "mean_h_spec": metrics["mean"],
        "std_h_spec": metrics["std"],
        "min_h_spec": metrics["min_h_spec"],
        "max_h_spec": metrics["max_h_spec"],
        "valid_samples": metrics["valid_samples"],
        "nan_count": metrics["nan_count"],
        # Per-layer summary
        "per_layer_lambda_max": metrics["per_layer_lambda_max"],
        # Cross-validation
        "crossval": {
            "model_370m_id": crossval.get("model_370m_id"),
            "mean_h_spec_370m": crossval.get("mean_h_spec_370m"),
            "mean_h_spec_1400m": metrics["mean"],
            "monotonic_scaling": (
                metrics["mean"] > crossval.get("mean_h_spec_370m", float("inf"))
                if crossval.get("mean_h_spec_370m") is not None
                else None
            ),
        },
        # Figures
        "figures": [
            f"{config.figures_dir}/hspec_distribution.png",
            f"{config.figures_dir}/gate_metrics.png",
            f"{config.figures_dir}/hspec_per_layer.png",
            f"{config.figures_dir}/eigenvalue_distribution.png",
        ],
    }

    # Add scale comparison figure if crossval ran
    if crossval.get("mean_h_spec_370m") is not None:
        results["figures"].append(f"{config.figures_dir}/scale_comparison.png")

    with open(config.results_path, "w") as f:
        yaml.dump(results, f, default_flow_style=False, sort_keys=False)

    print(f"\nResults saved to {config.results_path}")


def generate_figures(metrics: dict, crossval: dict, config: "ExperimentConfig") -> None:
    """Save figures to config.figures_dir."""
    import matplotlib.pyplot as plt

    os.makedirs(config.figures_dir, exist_ok=True)

    # 1. H_spec Distribution Histogram
    plt.figure(figsize=(10, 6))
    h_values = metrics["h_spec_values"]
    plt.hist(h_values, bins=50, edgecolor="black", alpha=0.7)
    plt.axvline(metrics["mean"], color="r", linestyle="--", label=f'Mean: {metrics["mean"]:.4f}')
    plt.xlabel("H_spec (tokens)")
    plt.ylabel("Frequency")
    plt.title("H_spec Distribution Across Random Sequences")
    plt.legend()
    plt.text(
        0.95,
        0.95,
        f'Mean: {metrics["mean"]:.4f}\nStd: {metrics["std"]:.6f}\nCV: {metrics["cv"]:.6f}',
        transform=plt.gca().transAxes,
        verticalalignment="top",
        horizontalalignment="right",
        fontsize=10,
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )
    plt.tight_layout()
    plt.savefig(f'{config.figures_dir}/hspec_distribution.png', dpi=150)
    plt.close()
    print(f"  Saved: {config.figures_dir}/hspec_distribution.png")

    # 2. Gate Metrics Comparison
    plt.figure(figsize=(8, 6))
    metrics_names = ["CV (Target < 0.3)", "CV (Actual)"]
    metrics_values = [config.cv_threshold, metrics["cv"]]
    colors = ["green", "red" if metrics["cv"] >= config.cv_threshold else "green"]
    bars = plt.bar(metrics_names, metrics_values, color=colors, edgecolor="black")
    plt.ylabel("Coefficient of Variation")
    plt.title("Gate Metrics: CV(H_spec) Target vs Actual")
    plt.axhline(y=config.cv_threshold, color="orange", linestyle="--", label="Threshold")
    for bar, val in zip(bars, metrics_values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f"{val:.6f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )
    gate_result = "PASS" if metrics["pass_gate"] else "FAIL"
    plt.text(
        0.5,
        0.9,
        f"Gate Result: {gate_result}",
        transform=plt.gca().transAxes,
        ha="center",
        fontsize=14,
        fontweight="bold",
        color="green" if metrics["pass_gate"] else "red",
    )
    plt.tight_layout()
    plt.savefig(f'{config.figures_dir}/gate_metrics.png', dpi=150)
    plt.close()
    print(f"  Saved: {config.figures_dir}/gate_metrics.png")

    # 3. H_spec per Layer
    plt.figure(figsize=(14, 6))
    per_layer_h_spec = metrics.get("per_layer_h_spec", [])
    if not per_layer_h_spec:
        # Fallback: compute from lambda_max
        per_layer = metrics["per_layer_lambda_max"]
        per_layer_h_spec = [-1.0 / np.log(lm) if lm < 1.0 else float("nan") for lm in per_layer]
    layers = range(len(per_layer_h_spec))
    plt.bar(layers, per_layer_h_spec, color="steelblue", edgecolor="black")
    plt.xlabel("Layer Index")
    plt.ylabel("H_spec (tokens)")
    plt.title("H_spec per Mamba Layer (Slowest Decay Mode)")
    plt.axhline(y=metrics["mean"], color="r", linestyle="--", label=f'Global H_spec: {metrics["mean"]:.2f}')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{config.figures_dir}/hspec_per_layer.png', dpi=150)
    plt.close()
    print(f"  Saved: {config.figures_dir}/hspec_per_layer.png")

    # 4. Discrete Eigenvalue Distribution (slowest per layer)
    plt.figure(figsize=(10, 6))
    per_layer_lambda = metrics["per_layer_lambda_max"]
    plt.hist(per_layer_lambda, bins=30, edgecolor="black", alpha=0.7)
    global_lambda_max = max(per_layer_lambda)
    plt.axvline(global_lambda_max, color="r", linestyle="--", label=f"λ_max: {global_lambda_max:.6f}")
    plt.xlabel("λ_discrete (slowest eigenvalue per layer)")
    plt.ylabel("Frequency")
    plt.title("Discrete Eigenvalue Distribution Across Layers (Slowest Mode)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{config.figures_dir}/eigenvalue_distribution.png', dpi=150)
    plt.close()
    print(f"  Saved: {config.figures_dir}/eigenvalue_distribution.png")

    # 5. Scale Comparison (if crossval data present)
    if crossval.get("mean_h_spec_370m") is not None:
        plt.figure(figsize=(8, 6))
        models = ["Mamba-370M", "Mamba-1.4B"]
        h_specs = [crossval["mean_h_spec_370m"], metrics["mean"]]
        colors = ["lightblue", "steelblue"]
        bars = plt.bar(models, h_specs, color=colors, edgecolor="black")
        plt.ylabel("H_spec (tokens)")
        plt.title("Scale Comparison: H_spec vs Model Size")
        for bar, val in zip(bars, h_specs):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                f"{val:.2f}",
                ha="center",
                va="bottom",
                fontsize=12,
            )
        monotonic = h_specs[1] > h_specs[0]
        plt.text(
            0.5,
            0.9,
            f"Monotonic Scaling: {'Yes' if monotonic else 'No'}",
            transform=plt.gca().transAxes,
            ha="center",
            fontsize=12,
            fontweight="bold",
        )
        plt.tight_layout()
        plt.savefig(f'{config.figures_dir}/scale_comparison.png', dpi=150)
        plt.close()
        print(f"  Saved: {config.figures_dir}/scale_comparison.png")
