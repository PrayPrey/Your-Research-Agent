"""H-M5: Main experiment - MLP probe invariance at N=50K scale.

Hypothesis: At N=50K, MLP probe invariance > 0.8 (learned from data diversity)
Gate: SHOULD_WORK - With sufficient data, MLP should learn permutation invariance.
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
from sklearn.metrics import r2_score
import importlib.util

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
H_M4_CODE_DIR = os.path.join(CODE_DIR, "..", "..", "h-m4", "code")
H_M3_CODE_DIR = os.path.join(CODE_DIR, "..", "..", "h-m3", "code")
H_M1_CODE_DIR = os.path.join(CODE_DIR, "..", "..", "h-m1", "code")
sys.path.insert(0, CODE_DIR)
sys.path.insert(0, H_M3_CODE_DIR)
sys.path.insert(0, H_M1_CODE_DIR)

spec_data = importlib.util.spec_from_file_location("data_gen", os.path.join(CODE_DIR, "data_gen.py"))
data_gen = importlib.util.module_from_spec(spec_data)
spec_data.loader.exec_module(data_gen)
load_model_zoo_population = data_gen.load_model_zoo_population
split_train_test = data_gen.split_train_test
to_dataset = data_gen.to_dataset

from train_mlp_scheduled import train_mlp_on_subset
from probe_invariance import evaluate_population_invariance

spec = importlib.util.spec_from_file_location("h_m5_metrics", os.path.join(CODE_DIR, "metrics.py"))
h_m5_metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h_m5_metrics)
compute_r2 = h_m5_metrics.compute_r2
compare_with_baseline = h_m5_metrics.compare_with_baseline
gate_logic = h_m5_metrics.gate_logic

H_M4_BASELINE = {"r2": 0.0036, "invariance": 0.9193}


def run_seed(
    seed: int,
    train_pop: List[Dict],
    test_pop: List[Dict],
    input_dim: int,
    epochs: int = 50,
    batch_size: int = 64,
    lr: float = 1e-3,
    device: str = "cpu",
) -> Dict:
    """Run single-seed experiment with R² + invariance."""
    print(f"  Seed {seed}: Training MLP on {len(train_pop)} models...", flush=True)

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

    test_ds = to_dataset(test_pop)
    X_test = test_ds.tensors[0].to(device)
    y_test = test_ds.tensors[1].to(device)

    with torch.no_grad():
        y_pred = model(X_test)
    test_r2 = r2_score(y_test.cpu().numpy(), y_pred.cpu().numpy())
    print(f"  Seed {seed}: Test R² = {test_r2:.4f}", flush=True)

    print(f"  Seed {seed}: Evaluating invariance...", flush=True)
    result = evaluate_population_invariance(
        model, test_pop, num_permutations=10, device=device
    )

    return {
        "seed": seed,
        "test_r2": float(test_r2),
        "mean_invariance": result["mean_invariance"],
        "std_invariance": result["std_invariance"],
        "mean_cv": result["mean_cv"],
        "invariance_scores": result["invariance_scores"],
    }


def aggregate_seeds(seed_results: List[Dict]) -> Dict:
    """Aggregate results across seeds."""
    r2_vals = [r["test_r2"] for r in seed_results]
    inv_vals = [r["mean_invariance"] for r in seed_results]

    mean_r2 = float(np.mean(r2_vals))
    std_r2 = float(np.std(r2_vals))
    mean_inv = float(np.mean(inv_vals))
    std_inv = float(np.std(inv_vals))

    r2_ci = stats.t.interval(0.95, len(r2_vals) - 1, loc=mean_r2, scale=stats.sem(r2_vals)) if len(r2_vals) > 1 else (mean_r2, mean_r2)
    inv_ci = stats.t.interval(0.95, len(inv_vals) - 1, loc=mean_inv, scale=stats.sem(inv_vals)) if len(inv_vals) > 1 else (mean_inv, mean_inv)

    gate_status, gate_reason = gate_logic(mean_r2, mean_inv)

    return {
        "r2": {"mean": mean_r2, "std": std_r2, "ci": [float(r2_ci[0]), float(r2_ci[1])], "all": r2_vals},
        "invariance": {"mean": mean_inv, "std": std_inv, "ci": [float(inv_ci[0]), float(inv_ci[1])], "all": inv_vals},
        "gate_status": gate_status,
        "gate_reason": gate_reason,
        "pass": gate_status == "PASS",
    }


def plot_gate_comparison_bar(h_m4_inv: float, h_m5_inv: float, out_path: str) -> None:
    """Bar chart comparing H-M4 (N=1K) vs H-M5 (N=50K) invariance."""
    fig, ax = plt.subplots(figsize=(8, 6))

    labels = ["H-M4 (N=1K)", "H-M5 (N=50K)"]
    values = [h_m4_inv, h_m5_inv]
    colors = ["#FF9800", "#4CAF50"]

    bars = ax.bar(labels, values, color=colors)
    ax.axhline(y=0.8, color="red", linestyle="--", label="H-M5 Threshold (0.8)")
    ax.axhline(y=0.5, color="blue", linestyle=":", alpha=0.5, label="H-M4 Threshold (0.5)")

    ax.set_ylabel("Probe Invariance Score")
    ax.set_title("Gate Comparison: MLP Invariance at N=1K vs N=50K")
    ax.set_ylim(0, 1.1)
    ax.legend()

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.3f}', ha='center', va='bottom', fontsize=12)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"  Saved: {out_path}")


def plot_r2_comparison(h_m4_r2: float, h_m5_r2: float, out_path: str) -> None:
    """Bar chart comparing R² at N=1K vs N=50K."""
    fig, ax = plt.subplots(figsize=(8, 6))

    labels = ["H-M4 (N=1K)", "H-M5 (N=50K)"]
    values = [h_m4_r2, h_m5_r2]
    colors = ["#FF9800", "#4CAF50"]

    bars = ax.bar(labels, values, color=colors)
    ax.axhline(y=0.1, color="red", linestyle="--", label="Learning Threshold (0.1)")

    ax.set_ylabel("Test R² Score")
    ax.set_title("Learning Comparison: R² at N=1K vs N=50K")
    ax.set_ylim(0, max(1.0, max(values) * 1.2))
    ax.legend()

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.4f}', ha='center', va='bottom', fontsize=12)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"  Saved: {out_path}")


def plot_invariance_histogram(invariance_scores: List[float], out_path: str) -> None:
    """Histogram of invariance scores across test models."""
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.hist(invariance_scores, bins=20, edgecolor="black", alpha=0.7)
    ax.axvline(x=0.8, color="red", linestyle="--", label="Threshold (0.8)")
    ax.axvline(x=np.mean(invariance_scores), color="green", linestyle="-",
               label=f"Mean ({np.mean(invariance_scores):.3f})")

    ax.set_xlabel("Invariance Score")
    ax.set_ylabel("Count")
    ax.set_title(f"H-M5: Distribution of Probe Invariance ({len(invariance_scores)} Test Models)")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"  Saved: {out_path}")


def plot_prediction_scatter(y_true: np.ndarray, y_pred: np.ndarray, out_path: str) -> None:
    """Scatter plot of predicted vs actual accuracy."""
    fig, ax = plt.subplots(figsize=(8, 8))

    ax.scatter(y_true, y_pred, alpha=0.3, s=10)
    ax.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()],
            'r--', label='y=x (perfect)')

    r2 = r2_score(y_true, y_pred)
    ax.set_xlabel("True Accuracy")
    ax.set_ylabel("Predicted Accuracy")
    ax.set_title(f"H-M5: MLP Prediction (R² = {r2:.4f})")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"  Saved: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="H-M5 Experiment")
    parser.add_argument("--n-models", type=int, default=None, help="Total models (None=all)")
    parser.add_argument("--n-test", type=int, default=2000, help="Test set size")
    parser.add_argument("--n-seeds", type=int, default=10, help="Number of seeds")
    parser.add_argument("--epochs", type=int, default=50, help="Training epochs")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--device", type=str, default="cuda", help="Device")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory")
    args = parser.parse_args()

    device = args.device
    if device == "cuda" and not torch.cuda.is_available():
        print("CUDA not available, falling back to CPU")
        device = "cpu"

    output_dir = args.output_dir or os.path.dirname(CODE_DIR)
    figures_dir = os.path.join(output_dir, "figures")
    os.makedirs(figures_dir, exist_ok=True)
    outputs_dir = os.path.join(CODE_DIR, "outputs")
    os.makedirs(outputs_dir, exist_ok=True)

    print("=" * 60)
    print("H-M5: MLP Probe Invariance at N=50K")
    print("=" * 60)
    print(f"Hypothesis: MLP trained on N~50K shows invariance > 0.8")
    print(f"Gate Type: SHOULD_WORK")
    print(f"Device: {device}")
    print()

    print(f"[1/5] Loading FULL Model Zoo dataset...")
    population = load_model_zoo_population(max_models=args.n_models)
    train_pop, test_pop = split_train_test(population, n_train=None, n_test=args.n_test, seed=42)
    print(f"  Total: {len(population)}, Train: {len(train_pop)}, Test: {len(test_pop)}")

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
        print(f"    Seed {seed}: R²={result['test_r2']:.4f}, inv={result['mean_invariance']:.4f}")

    print("\n[3/5] Aggregating results...")
    agg = aggregate_seeds(seed_results)
    print(f"  Mean R²: {agg['r2']['mean']:.4f} +/- {agg['r2']['std']:.4f}")
    print(f"  Mean invariance: {agg['invariance']['mean']:.4f} +/- {agg['invariance']['std']:.4f}")
    print(f"  Gate Status: {agg['gate_status']}")
    print(f"  Gate Reason: {agg['gate_reason']}")

    print("\n[4/5] Comparing with H-M4 baseline...")
    comparison = compare_with_baseline(
        mlp_r2=agg['r2']['mean'],
        mlp_invariance=agg['invariance']['mean'],
    )
    print(f"  H-M4 R²: {comparison['h_m4_r2']:.4f}, H-M5 R²: {comparison['h_m5_r2']:.4f}")
    print(f"  R² improvement: {comparison['r2_improvement']:.4f}")
    print(f"  H-M4 inv: {comparison['h_m4_invariance']:.4f}, H-M5 inv: {comparison['h_m5_invariance']:.4f}")

    print("\n[5/5] Generating figures...")
    plot_gate_comparison_bar(
        H_M4_BASELINE["invariance"],
        agg['invariance']['mean'],
        os.path.join(figures_dir, "gate_comparison.png")
    )

    plot_r2_comparison(
        H_M4_BASELINE["r2"],
        agg['r2']['mean'],
        os.path.join(figures_dir, "r2_comparison.png")
    )

    last_seed_scores = seed_results[-1]["invariance_scores"]
    plot_invariance_histogram(
        last_seed_scores,
        os.path.join(figures_dir, "invariance_hist.png")
    )

    test_ds = to_dataset(test_pop)
    X_test = test_ds.tensors[0].to(device)
    y_test = test_ds.tensors[1].numpy()

    model = train_mlp_on_subset(
        to_dataset(train_pop), input_dim, seed=0,
        epochs=args.epochs, batch_size=args.batch_size, device=device
    )
    with torch.no_grad():
        y_pred = model(X_test).cpu().numpy()
    plot_prediction_scatter(y_test.squeeze(), y_pred.squeeze(),
                            os.path.join(figures_dir, "prediction_scatter.png"))

    results = {
        "hypothesis_id": "h-m5",
        "hypothesis_statement": "At N=50K, MLP probe invariance > 0.8",
        "gate_type": "SHOULD_WORK",
        "gate_passed": agg["pass"],
        "gate_status": agg["gate_status"],
        "gate_reason": agg["gate_reason"],
        "timestamp": datetime.now().isoformat(),
        "config": {
            "n_models": len(population),
            "n_train": len(train_pop),
            "n_test": len(test_pop),
            "n_seeds": args.n_seeds,
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "lr": args.lr,
            "device": device,
        },
        "results": {
            "mlp": {
                "mean_r2": agg["r2"]["mean"],
                "std_r2": agg["r2"]["std"],
                "r2_ci_95": agg["r2"]["ci"],
                "mean_invariance": agg["invariance"]["mean"],
                "std_invariance": agg["invariance"]["std"],
                "invariance_ci_95": agg["invariance"]["ci"],
            },
            "baseline_comparison": comparison,
        },
        "seed_results": [
            {"seed": r["seed"], "test_r2": r["test_r2"], "mean_invariance": r["mean_invariance"]}
            for r in seed_results
        ],
        "figures": [
            "figures/gate_comparison.png",
            "figures/r2_comparison.png",
            "figures/invariance_hist.png",
            "figures/prediction_scatter.png",
        ],
    }

    results_path = os.path.join(output_dir, "results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {results_path}")

    csv_path = os.path.join(outputs_dir, "results.csv")
    with open(csv_path, "w") as f:
        f.write("seed,test_r2,mean_invariance,std_invariance,mean_cv\n")
        for r in seed_results:
            f.write(f"{r['seed']},{r['test_r2']:.6f},{r['mean_invariance']:.6f},{r['std_invariance']:.6f},{r['mean_cv']:.6f}\n")
    print(f"CSV saved: {csv_path}")

    print("\n" + "=" * 60)
    print("H-M5 EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"Gate Result: {agg['gate_status']}")
    print(f"R²: {agg['r2']['mean']:.4f} (must be > 0.1 for meaningful invariance)")
    print(f"Invariance: {agg['invariance']['mean']:.4f} (threshold > 0.8)")
    print(f"Reason: {agg['gate_reason']}")
    print("=" * 60)

    return 0 if agg["pass"] else 1


if __name__ == "__main__":
    exit(main())
