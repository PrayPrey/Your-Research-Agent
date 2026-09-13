import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
from config import CONFIG

def plot_gate_comparison(r_ensemble: float, r_individual_max: float, out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(["Ensemble", "Best Individual"], [r_ensemble, r_individual_max], color=["#4CAF50", "#2196F3"])
    ax.axhline(y=r_individual_max, color="red", linestyle="--", label=f"Threshold: {r_individual_max:.3f}")
    ax.set_ylabel("Partial Correlation (r)")
    ax.set_title("H-M2 Gate Comparison")
    ax.legend()
    for bar, val in zip(bars, [r_ensemble, r_individual_max]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f"{val:.3f}", ha="center")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_weight_sensitivity(weight_r_pairs: list[tuple[float, float]], out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    w_vals = [w for w, r in weight_r_pairs]
    r_vals = [r for w, r in weight_r_pairs]
    ax.plot(w_vals, r_vals, marker="o", linewidth=2, markersize=8)
    ax.axhline(y=CONFIG.max_r_individual, color="red", linestyle="--", label=f"Threshold: {CONFIG.max_r_individual:.3f}")
    ax.set_xlabel("w_pylint (w_radon = 1 - w_pylint)")
    ax.set_ylabel("Partial Correlation (r)")
    ax.set_title("Weight Sensitivity: r vs w_pylint")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def generate_all_figures(best_r: float, r_max_individual: float, weight_r_pairs: list) -> None:
    os.makedirs(CONFIG.figures_dir, exist_ok=True)
    plot_gate_comparison(best_r, r_max_individual, os.path.join(CONFIG.figures_dir, "gate_comparison.png"))
    plot_weight_sensitivity(weight_r_pairs, os.path.join(CONFIG.figures_dir, "weight_sensitivity.png"))
