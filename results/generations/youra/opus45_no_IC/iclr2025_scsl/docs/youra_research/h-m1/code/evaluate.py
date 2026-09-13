"""Mechanism verification and visualization for H-M1."""
import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def verify_mechanism(results: dict) -> dict:
    epoch5 = results["epoch_5"]
    epoch50 = results["epoch_50"]
    bias_exists = epoch5["spurious_acc"] > epoch5["core_acc"]
    core_improves = epoch50["core_acc"] > epoch5["core_acc"]
    return {"bias_exists": bias_exists, "core_improves": core_improves}


def plot_probe_accuracy_curve(results: dict, out_path: str) -> None:
    epochs = [5, 20, 50]
    spurious = [results[f"epoch_{e}"]["spurious_acc"] for e in epochs]
    core = [results[f"epoch_{e}"]["core_acc"] for e in epochs]

    plt.figure(figsize=(8, 6))
    plt.plot(epochs, spurious, 'o-', label='Spurious (background)', color='red')
    plt.plot(epochs, core, 's-', label='Core (bird type)', color='blue')
    plt.xlabel('Epoch')
    plt.ylabel('Probe Accuracy')
    plt.title('Linear Probe Accuracy: Spurious vs Core Features')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved figure: {out_path}")


def run_evaluation(results: dict, figures_dir: str, metrics_path: str) -> dict:
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)

    verification = verify_mechanism(results)
    plot_probe_accuracy_curve(results, os.path.join(figures_dir, "probe_accuracy.png"))

    output = {
        "results": results,
        "verification": verification,
    }
    with open(metrics_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Saved metrics: {metrics_path}")

    return verification
