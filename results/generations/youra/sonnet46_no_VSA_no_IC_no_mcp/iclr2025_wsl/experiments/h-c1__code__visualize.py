"""H-C1: Visualizations."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

FIGURES_DIR = Path(__file__).parent.parent / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def plot_gate_metric(fraction_unique: float, threshold: float = 0.99):
    """Bar chart: fraction_unique vs threshold."""
    fig, ax = plt.subplots(figsize=(5, 4))
    color = "steelblue" if fraction_unique >= threshold else "tomato"
    ax.bar(["fraction_unique"], [fraction_unique], color=color, width=0.4)
    ax.axhline(threshold, color="black", linestyle="--", label=f"threshold={threshold}")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Fraction")
    verdict = "PASS" if fraction_unique >= threshold else "FAIL"
    ax.set_title(f"H-C1 Gate Metric — {verdict} ({fraction_unique:.4f})")
    ax.legend()
    out = FIGURES_DIR / "gate_metric.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")


def plot_tied_neuron_hist(results):
    """Histogram of tied neuron counts (conditional — only if degenerate > 0)."""
    counts = [r["tied_neuron_count"] for r in results if r["degenerate"]]
    if not counts:
        return
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.hist(counts, bins=max(10, max(counts) + 1), color="orange", edgecolor="black")
    ax.set_xlabel("Tied neuron count per model")
    ax.set_ylabel("Number of models")
    ax.set_title("H-C1: Tied neuron distribution (degenerate models only)")
    out = FIGURES_DIR / "tied_neuron_hist.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")
