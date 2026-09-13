"""H-E1 Evaluation and Figure Generation"""
import os
import json
import matplotlib.pyplot as plt
import numpy as np


def plot_loss_curves(matrix_history: list, token_history: list, out_dir: str):
    """Plot loss convergence for both objectives."""
    plt.figure(figsize=(10, 6))

    if matrix_history:
        plt.plot(range(len(matrix_history)), matrix_history, label="MOHAWK (Matrix)", color="blue")
    if token_history:
        plt.plot(range(len(token_history)), token_history, label="CAB (Token)", color="orange")

    plt.xlabel("Training Steps (x1000)")
    plt.ylabel("Loss")
    plt.title("H-E1: Loss Convergence Comparison")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(out_dir, "loss_curves.png"), dpi=150, bbox_inches="tight")
    plt.close()


def plot_grad_norm_hist(matrix_norms: list, token_norms: list, out_dir: str):
    """Plot gradient norm distribution."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    if matrix_norms:
        axes[0].hist(matrix_norms, bins=50, color="blue", alpha=0.7)
        axes[0].set_title("MOHAWK Gradient Norm Distribution")
        axes[0].set_xlabel("Gradient Norm")
        axes[0].set_ylabel("Frequency")
        axes[0].axvline(np.mean(matrix_norms), color="red", linestyle="--", label=f"Mean: {np.mean(matrix_norms):.2f}")
        axes[0].legend()

    if token_norms:
        axes[1].hist(token_norms, bins=50, color="orange", alpha=0.7)
        axes[1].set_title("CAB Gradient Norm Distribution")
        axes[1].set_xlabel("Gradient Norm")
        axes[1].set_ylabel("Frequency")
        axes[1].axvline(np.mean(token_norms), color="red", linestyle="--", label=f"Mean: {np.mean(token_norms):.2f}")
        axes[1].legend()

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "grad_norm_histogram.png"), dpi=150, bbox_inches="tight")
    plt.close()


def plot_gate_metrics(mohawk_metrics: dict, cab_metrics: dict, out_dir: str):
    """Plot gate metrics comparison bar chart."""
    metrics_names = ["Initial Loss", "Final Loss", "Loss Reduction %", "NaN Count"]

    mohawk_values = [
        mohawk_metrics.get("initial_loss", 0),
        mohawk_metrics.get("final_loss", 0),
        (1 - mohawk_metrics.get("final_loss", 0) / max(mohawk_metrics.get("initial_loss", 1), 1e-6)) * 100,
        mohawk_metrics.get("nan_count", 0)
    ]

    cab_values = [
        cab_metrics.get("initial_loss", 0),
        cab_metrics.get("final_loss", 0),
        (1 - cab_metrics.get("final_loss", 0) / max(cab_metrics.get("initial_loss", 1), 1e-6)) * 100,
        cab_metrics.get("nan_count", 0)
    ]

    x = np.arange(len(metrics_names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width/2, mohawk_values, width, label="MOHAWK (Matrix)", color="blue")
    bars2 = ax.bar(x + width/2, cab_values, width, label="CAB (Token)", color="orange")

    ax.set_ylabel("Value")
    ax.set_title("H-E1 Gate Metrics Comparison")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics_names)
    ax.legend()
    ax.axhline(50, color="green", linestyle="--", alpha=0.5, label="50% reduction target")

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "gate_metrics.png"), dpi=150, bbox_inches="tight")
    plt.close()


def check_gate_criteria(metrics: dict) -> dict:
    """Check if gate criteria are met."""
    results = {
        "pass": True,
        "reasons": []
    }

    if metrics.get("nan_count", 0) > 0:
        results["pass"] = False
        results["reasons"].append(f"NaN detected: {metrics['nan_count']} times")

    if metrics.get("inf_count", 0) > 0:
        results["pass"] = False
        results["reasons"].append(f"Inf detected: {metrics['inf_count']} times")

    initial = metrics.get("initial_loss", float("inf"))
    final = metrics.get("final_loss", float("inf"))

    if final >= initial * 0.5:
        results["pass"] = False
        results["reasons"].append(f"Insufficient loss reduction: {final:.4f} >= {initial * 0.5:.4f}")

    avg_grad_norm = np.mean(metrics.get("grad_norm_history", [0]))
    if avg_grad_norm > 10.0:
        results["pass"] = False
        results["reasons"].append(f"High average gradient norm: {avg_grad_norm:.4f}")

    if not results["reasons"]:
        results["reasons"].append("All criteria passed")

    return results


def generate_all_figures(results_path: str, out_dir: str):
    """Generate all figures from results file."""
    with open(results_path, "r") as f:
        results = json.load(f)

    mohawk = results.get("mohawk", {})
    cab = results.get("cab", {})

    os.makedirs(out_dir, exist_ok=True)

    plot_loss_curves(
        mohawk.get("loss_history", []),
        cab.get("loss_history", []),
        out_dir
    )

    plot_grad_norm_hist(
        mohawk.get("grad_norm_history", []),
        cab.get("grad_norm_history", []),
        out_dir
    )

    plot_gate_metrics(mohawk, cab, out_dir)

    mohawk_gate = check_gate_criteria(mohawk)
    cab_gate = check_gate_criteria(cab)

    print("MOHAWK Gate Check:", mohawk_gate)
    print("CAB Gate Check:", cab_gate)

    return {
        "mohawk_gate": mohawk_gate,
        "cab_gate": cab_gate,
        "overall_pass": mohawk_gate["pass"] and cab_gate["pass"]
    }


if __name__ == "__main__":
    import sys
    results_path = sys.argv[1] if len(sys.argv) > 1 else "outputs/results.json"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "figures/"
    result = generate_all_figures(results_path, out_dir)
    print(f"\nOverall Gate: {'PASS' if result['overall_pass'] else 'FAIL'}")
