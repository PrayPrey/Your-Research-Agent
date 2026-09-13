"""Evaluation and visualization."""
import os
import json
import matplotlib.pyplot as plt
from peak_detection import find_peak_epoch, compute_auc, wilcoxon_test

def verify_mechanism(results, spurious_peak, core_peak, auc_range=(1, 20)):
    """Verify H-M2: spurious peaks before core."""
    spurious_series = [results[e]["spurious_acc"] for e in sorted(results.keys())]
    core_series = [results[e]["core_acc"] for e in sorted(results.keys())]

    auc_spurious = compute_auc(spurious_series, auc_range[0], auc_range[1])
    auc_core = compute_auc(core_series, auc_range[0], auc_range[1])

    passed = bool(spurious_peak < core_peak)
    peak_diff = int(core_peak - spurious_peak)

    return {
        "passed": passed,
        "peak_diff": peak_diff,
        "spurious_peak": int(spurious_peak),
        "core_peak": int(core_peak),
        "auc_spurious": float(auc_spurious),
        "auc_core": float(auc_core)
    }

def plot_learning_curves(results, spurious_peak, core_peak, out_path):
    """Plot dual-line learning curves with peak markers."""
    epochs = sorted(results.keys())
    spurious = [results[e]["spurious_acc"] for e in epochs]
    core = [results[e]["core_acc"] for e in epochs]

    plt.figure(figsize=(10, 6))
    plt.plot(epochs, spurious, 'b-', label='Spurious (background)', linewidth=2)
    plt.plot(epochs, core, 'r-', label='Core (bird type)', linewidth=2)
    plt.axvline(spurious_peak, color='b', linestyle='--', alpha=0.7, label=f'Spurious peak (e={spurious_peak})')
    plt.axvline(core_peak, color='r', linestyle='--', alpha=0.7, label=f'Core peak (e={core_peak})')
    plt.xlabel('Epoch')
    plt.ylabel('Probe Accuracy')
    plt.title('H-M2: Spurious vs Core Feature Learning Dynamics')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved figure: {out_path}")

def run_evaluation(results, figures_dir, metrics_path, peak_window=5, auc_range=(1, 20)):
    """Run full evaluation."""
    spurious_series = [results[e]["spurious_acc"] for e in sorted(results.keys())]
    core_series = [results[e]["core_acc"] for e in sorted(results.keys())]

    spurious_peak = find_peak_epoch(spurious_series, peak_window)
    core_peak = find_peak_epoch(core_series, peak_window)

    verification = verify_mechanism(results, spurious_peak, core_peak, auc_range)
    wilcoxon_result = wilcoxon_test(spurious_series, core_series)

    metrics = {
        "verification": verification,
        "wilcoxon_test": wilcoxon_result,
        "epoch_results": {str(e): results[e] for e in results}
    }

    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics: {metrics_path}")

    fig_path = os.path.join(figures_dir, "learning_curves.png")
    plot_learning_curves(results, spurious_peak, core_peak, fig_path)

    return metrics
