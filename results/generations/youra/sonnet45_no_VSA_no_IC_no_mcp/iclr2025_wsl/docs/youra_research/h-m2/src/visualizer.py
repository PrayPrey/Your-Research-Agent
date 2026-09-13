"""Visualization functions for h-m2."""
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
from pathlib import Path
from typing import Dict

class Visualizer:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_confusion_matrix(self, cm: Dict[str, int], title: str, filename: str):
        """Plot confusion matrix heatmap. cm: {tp, fp, tn, fn}."""
        fig, ax = plt.subplots(figsize=(6, 5))

        matrix = [[cm["tp"], cm["fn"]],
                  [cm["fp"], cm["tn"]]]

        im = ax.imshow(matrix, cmap="Blues", vmin=0, vmax=max(cm.values()))

        # Labels
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(["Predicted Testable", "Predicted Not Testable"])
        ax.set_yticklabels(["True Testable", "True Not Testable"])

        # Annotate cells
        for i in range(2):
            for j in range(2):
                text = ax.text(j, i, matrix[i][j], ha="center", va="center", fontsize=20)

        ax.set_title(title, fontsize=14, pad=10)
        plt.tight_layout()

        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        return str(output_path)

    def plot_metrics_comparison(self, baseline_metrics: Dict[str, float],
                                 proposed_metrics: Dict[str, float],
                                 filename: str):
        """Bar chart comparing baseline vs proposed metrics."""
        metrics_to_plot = ["fpr", "precision", "accuracy"]

        baseline_vals = [baseline_metrics[m] for m in metrics_to_plot]
        proposed_vals = [proposed_metrics[m] for m in metrics_to_plot]

        x = range(len(metrics_to_plot))
        width = 0.35

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar([i - width/2 for i in x], baseline_vals, width, label="Baseline (Random)", alpha=0.7)
        ax.bar([i + width/2 for i in x], proposed_vals, width, label="Proposed (Verifier)", alpha=0.7)

        ax.set_ylabel("Value", fontsize=12)
        ax.set_xlabel("Metrics", fontsize=12)
        ax.set_title("Baseline vs Proposed Metrics", fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels([m.upper() for m in metrics_to_plot])
        ax.legend()
        ax.set_ylim(0, 1.0)
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()

        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        return str(output_path)

    def plot_gate_comparison(self, target_fpr: float, actual_fpr: float, filename: str):
        """Bar chart: target FPR vs actual FPR."""
        fig, ax = plt.subplots(figsize=(6, 5))

        metrics = ["Target FPR", "Actual FPR"]
        values = [target_fpr, actual_fpr]
        colors = ["green" if actual_fpr < target_fpr else "red", "blue"]

        ax.bar(metrics, values, color=colors, alpha=0.7)
        ax.set_ylabel("False Positive Rate", fontsize=12)
        ax.set_title("Gate Threshold vs Actual FPR", fontsize=14)
        ax.set_ylim(0, 1.0)
        ax.axhline(y=target_fpr, color="red", linestyle="--", label=f"Gate Threshold ({target_fpr})")
        ax.legend()
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()

        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        return str(output_path)


if __name__ == "__main__":
    # Self-check
    v = Visualizer("/tmp/test_viz")
    cm = {"tp": 8, "fp": 2, "tn": 8, "fn": 2}
    baseline = {"fpr": 0.5, "precision": 0.5, "accuracy": 0.5}
    proposed = {"fpr": 0.2, "precision": 0.8, "accuracy": 0.8}

    path1 = v.plot_confusion_matrix(cm, "Test CM", "test_cm.png")
    path2 = v.plot_metrics_comparison(baseline, proposed, "test_metrics.png")
    path3 = v.plot_gate_comparison(0.25, 0.2, "test_gate.png")

    assert Path(path1).exists(), "CM plot not created"
    assert Path(path2).exists(), "Metrics plot not created"
    assert Path(path3).exists(), "Gate plot not created"

    print("Visualizer self-check passed")
