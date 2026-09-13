"""H-M4: Main experiment orchestration.

Hypothesis: At N=1K, MLP probe invariance < 0.5 (insufficient data diversity)
Gate: SHOULD_WORK - MLP trained on limited data should NOT learn permutation invariance.
"""

import sys
import os
import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional

import torch
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats

CODE_DIR = os.path.dirname(__file__)
H_M3_CODE_DIR = os.path.join(CODE_DIR, "..", "..", "h-m3", "code")
H_M1_CODE_DIR = os.path.join(CODE_DIR, "..", "..", "h-m1", "code")
sys.path.insert(0, CODE_DIR)
sys.path.insert(0, H_M3_CODE_DIR)
sys.path.insert(0, H_M1_CODE_DIR)

from data_gen import load_model_zoo_population, split_train_test, to_dataset
from train_mlp import train_mlp_on_subset
from probe_invariance import evaluate_population_invariance
from nfn_control import load_nfn_model, measure_nfn_invariance


def run_seed(
    seed: int,
    train_pop: List[Dict],
    test_pop: List[Dict],
    input_dim: int,
    epochs: int = 50,
    batch_size: int = 32,
    lr: float = 1e-3,
    device: str = "cpu",
) -> Dict:
    """Run single-seed experiment."""
    print(f"  Seed {seed}: Training MLP...", flush=True)

    train_ds = to_dataset(train_pop)
    model = train_mlp_on_subset(
        train_ds,
        input_dim=input_dim,
        seed=seed,
        epochs=epochs,
        batch_size=batch_size,
        lr=lr,
        device=device,
    )

    print(f"  Seed {seed}: Evaluating invariance...", flush=True)
    result = evaluate_population_invariance(
        model, test_pop, num_permutations=10, device=device
    )

    return {
        "seed": seed,
        "mean_invariance": result["mean_invariance"],
        "std_invariance": result["std_invariance"],
        "mean_cv": result["mean_cv"],
        "invariance_scores": result["invariance_scores"],
    }


def aggregate_seeds(seed_results: List[Dict]) -> Dict:
    """Aggregate results across seeds."""
    means = [r["mean_invariance"] for r in seed_results]
    mean_inv = float(np.mean(means))
    std_inv = float(np.std(means))

    ci = stats.t.interval(
        0.95, len(means) - 1, loc=mean_inv, scale=stats.sem(means)
    ) if len(means) > 1 else (mean_inv, mean_inv)

    return {
        "mean": mean_inv,
        "std": std_inv,
        "ci_low": float(ci[0]) if not np.isnan(ci[0]) else mean_inv,
        "ci_high": float(ci[1]) if not np.isnan(ci[1]) else mean_inv,
        "all_means": means,
        "pass": mean_inv < 0.5,
    }


def plot_mlp_vs_nfn_bar(mlp_mean: float, nfn_mean: Optional[float], out_path: str) -> None:
    """Bar chart comparing MLP vs NFN invariance."""
    fig, ax = plt.subplots(figsize=(8, 6))

    labels = ["MLP (N=1K)"]
    values = [mlp_mean]
    colors = ["#4CAF50"]

    if nfn_mean is not None:
        labels.append("NFN")
        values.append(nfn_mean)
        colors.append("#2196F3")

    bars = ax.bar(labels, values, color=colors)
    ax.axhline(y=0.5, color="red", linestyle="--", label="Invariance Threshold (0.5)")

    ax.set_ylabel("Probe Invariance Score")
    ax.set_title("H-M4: MLP vs NFN Probe Invariance\n(Higher = More Invariant)")
    ax.set_ylim(0, 1.1)
    ax.legend()

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.3f}', ha='center', va='bottom', fontsize=12)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"  Saved: {out_path}")


def plot_prediction_scatter(predictions_list: List[float], out_path: str) -> None:
    """Scatter plot of original vs permuted predictions."""
    orig = predictions_list[0]
    perms = predictions_list[1:]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter([orig] * len(perms), perms, alpha=0.6)
    ax.axline((0, 0), slope=1, color="red", linestyle="--", label="y=x (perfect invariance)")

    ax.set_xlabel("Original Prediction")
    ax.set_ylabel("Permuted Prediction")
    ax.set_title("H-M4: MLP Prediction Stability Under Permutation")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"  Saved: {out_path}")


def plot_invariance_histogram(invariance_scores: List[float], out_path: str) -> None:
    """Histogram of invariance scores across test models."""
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.hist(invariance_scores, bins=20, edgecolor="black", alpha=0.7)
    ax.axvline(x=0.5, color="red", linestyle="--", label="Threshold (0.5)")
    ax.axvline(x=np.mean(invariance_scores), color="green", linestyle="-",
               label=f"Mean ({np.mean(invariance_scores):.3f})")

    ax.set_xlabel("Invariance Score")
    ax.set_ylabel("Count")
    ax.set_title("H-M4: Distribution of Probe Invariance Scores (200 Test Models)")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"  Saved: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="H-M4 Experiment")
    parser.add_argument("--n-models", type=int, default=1200, help="Total synthetic models")
    parser.add_argument("--n-train", type=int, default=1000, help="Training set size")
    parser.add_argument("--n-test", type=int, default=200, help="Test set size")
    parser.add_argument("--n-seeds", type=int, default=10, help="Number of seeds")
    parser.add_argument("--epochs", type=int, default=50, help="Training epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--device", type=str, default="cpu", help="Device (cpu/cuda)")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory")
    args = parser.parse_args()

    device = args.device
    if device == "cuda" and not torch.cuda.is_available():
        print("CUDA not available, falling back to CPU")
        device = "cpu"

    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = os.path.dirname(CODE_DIR)
    figures_dir = os.path.join(output_dir, "figures")
    os.makedirs(figures_dir, exist_ok=True)
    outputs_dir = os.path.join(CODE_DIR, "outputs")
    os.makedirs(outputs_dir, exist_ok=True)

    print("=" * 60)
    print("H-M4: MLP Probe Invariance at N=1K")
    print("=" * 60)
    print(f"Hypothesis: MLP trained on N=1K shows invariance < 0.5")
    print(f"Gate Type: SHOULD_WORK")
    print(f"Device: {device}")
    print()

    print(f"[1/5] Loading {args.n_models} real Model Zoo CNN models...")
    population = load_model_zoo_population(max_models=args.n_models)
    train_pop, test_pop = split_train_test(population, args.n_train, args.n_test, seed=42)
    print(f"  Train: {len(train_pop)}, Test: {len(test_pop)}")

    sample_flat = to_dataset(train_pop[:1])[0][0]
    input_dim = sample_flat.shape[0]
    print(f"  Input dim (flattened weights): {input_dim}")

    print(f"\n[2/5] Running {args.n_seeds} seeds...")
    seed_results = []
    for seed in range(args.n_seeds):
        result = run_seed(
            seed, train_pop, test_pop, input_dim,
            epochs=args.epochs, batch_size=args.batch_size, lr=args.lr, device=device
        )
        seed_results.append(result)
        print(f"    Seed {seed}: invariance={result['mean_invariance']:.4f}")

    print("\n[3/5] Aggregating results...")
    agg = aggregate_seeds(seed_results)
    print(f"  Mean invariance: {agg['mean']:.4f} +/- {agg['std']:.4f}")
    print(f"  95% CI: [{agg['ci_low']:.4f}, {agg['ci_high']:.4f}]")
    print(f"  Pass (< 0.5): {agg['pass']}")

    print("\n[4/5] NFN control (optional)...")
    nfn_model = load_nfn_model(input_dim)
    nfn_result = None
    if nfn_model is not None:
        nfn_model = nfn_model.to(device)
        nfn_result = measure_nfn_invariance(nfn_model, test_pop, device=device)
        print(f"  NFN invariance: {nfn_result['mean_invariance']:.4f}")
    else:
        print("  NFN not available - skipping control comparison")

    gate_passed = agg["pass"]
    if nfn_result is not None and nfn_result["mean_invariance"] <= 0.95:
        print(f"  Warning: NFN invariance ({nfn_result['mean_invariance']:.4f}) < 0.95 expected")

    print("\n[5/5] Generating figures...")
    plot_mlp_vs_nfn_bar(
        agg["mean"],
        nfn_result["mean_invariance"] if nfn_result else None,
        os.path.join(figures_dir, "mlp_vs_nfn_bar.png")
    )

    last_seed_scores = seed_results[-1]["invariance_scores"]
    plot_invariance_histogram(
        last_seed_scores,
        os.path.join(figures_dir, "invariance_histogram.png")
    )

    sample_preds = None
    for sr in seed_results:
        if "invariance_scores" in sr and len(sr["invariance_scores"]) > 0:
            idx = 0
            model = train_mlp_on_subset(
                to_dataset(train_pop), input_dim, seed=sr["seed"],
                epochs=args.epochs, device=device
            )
            from probe_invariance import compute_probe_invariance
            _, sample_preds, _ = compute_probe_invariance(
                model, test_pop[idx]["state_dict"],
                hidden_dims=test_pop[idx].get("hidden_dims", (32, 32)),
                device=device
            )
            break

    if sample_preds:
        plot_prediction_scatter(
            sample_preds,
            os.path.join(figures_dir, "prediction_scatter.png")
        )

    results = {
        "hypothesis_id": "h-m4",
        "hypothesis_statement": "At N=1K, MLP probe invariance < 0.5",
        "gate_type": "SHOULD_WORK",
        "gate_passed": gate_passed,
        "timestamp": datetime.now().isoformat(),
        "config": {
            "n_models": args.n_models,
            "n_train": args.n_train,
            "n_test": args.n_test,
            "n_seeds": args.n_seeds,
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "lr": args.lr,
            "device": device,
        },
        "results": {
            "mlp": {
                "mean_invariance": agg["mean"],
                "std_invariance": agg["std"],
                "ci_95": [agg["ci_low"], agg["ci_high"]],
                "all_seed_means": agg["all_means"],
                "pass_threshold_0.5": agg["pass"],
            },
            "nfn": nfn_result if nfn_result else {"status": "unavailable"},
        },
        "seed_results": [
            {"seed": r["seed"], "mean_invariance": r["mean_invariance"], "std_invariance": r["std_invariance"]}
            for r in seed_results
        ],
        "figures": [
            "figures/mlp_vs_nfn_bar.png",
            "figures/invariance_histogram.png",
            "figures/prediction_scatter.png",
        ],
    }

    results_path = os.path.join(output_dir, "results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {results_path}")

    csv_path = os.path.join(outputs_dir, "results.csv")
    with open(csv_path, "w") as f:
        f.write("seed,mean_invariance,std_invariance,mean_cv\n")
        for r in seed_results:
            f.write(f"{r['seed']},{r['mean_invariance']:.6f},{r['std_invariance']:.6f},{r['mean_cv']:.6f}\n")
    print(f"CSV saved: {csv_path}")

    print("\n" + "=" * 60)
    print("H-M4 EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"Gate Result: {'PASS' if gate_passed else 'FAIL'}")
    print(f"MLP Invariance: {agg['mean']:.4f} (threshold < 0.5)")
    if nfn_result:
        print(f"NFN Invariance: {nfn_result['mean_invariance']:.4f} (expected > 0.95)")
    print("=" * 60)

    return 0 if gate_passed else 1


if __name__ == "__main__":
    exit(main())
