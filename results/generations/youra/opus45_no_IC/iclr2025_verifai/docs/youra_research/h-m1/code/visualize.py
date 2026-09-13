import matplotlib.pyplot as plt
import os

def plot_error_rate_comparison(baseline_rate: float, constrained_rate: float, out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    conditions = ["Baseline\n(Unconstrained)", "Grammar-Constrained\n(SynCode)"]
    rates = [baseline_rate * 100, constrained_rate * 100]
    colors = ["#d62728", "#2ca02c"]

    bars = ax.bar(conditions, rates, color=colors, edgecolor="black", width=0.6)
    ax.set_ylabel("Compilation Error Rate (%)", fontsize=12)
    ax.set_title("H-M1: Grammar-Constrained Decoding Effect", fontsize=14)
    ax.set_ylim(0, max(rates) * 1.2 if max(rates) > 0 else 10)

    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f"{rate:.1f}%", ha="center", va="bottom", fontsize=11)

    reduction = ((baseline_rate - constrained_rate) / baseline_rate * 100) if baseline_rate > 0 else 0
    ax.text(0.5, 0.95, f"Reduction: {reduction:.1f}%", transform=ax.transAxes, ha="center", fontsize=12,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()

def save_summary_table(baseline_stats: dict, constrained_stats: dict, out_path: str) -> None:
    with open(out_path, "w") as f:
        f.write("# H-M1 Experiment Results Summary\n\n")
        f.write("| Metric | Baseline | Constrained | Δ |\n")
        f.write("|--------|----------|-------------|---|\n")
        b_rate = baseline_stats["error_rate"] * 100
        c_rate = constrained_stats["error_rate"] * 100
        delta = b_rate - c_rate
        f.write(f"| Error Rate | {b_rate:.2f}% | {c_rate:.2f}% | -{delta:.2f}% |\n")
        f.write(f"| Total Errors | {baseline_stats['n_errors']} | {constrained_stats['n_errors']} | -{baseline_stats['n_errors'] - constrained_stats['n_errors']} |\n")
        f.write(f"| Total Samples | {baseline_stats['n_total']} | {constrained_stats['n_total']} | - |\n")
