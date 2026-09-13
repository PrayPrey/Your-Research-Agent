import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from config import CONFIG
from edit_scope_classify import label_edit_records

def compute_fix_rates(edit_records: list[dict]) -> dict:
    """Compute fix rate by edit_scope (targeted vs global)."""
    targeted = [r for r in edit_records if r.get("edit_scope") == "targeted"]
    global_edits = [r for r in edit_records if r.get("edit_scope") == "global"]

    targeted_fixed = sum(1 for r in targeted if r.get("fixed"))
    global_fixed = sum(1 for r in global_edits if r.get("fixed"))

    targeted_rate = targeted_fixed / max(len(targeted), 1)
    global_rate = global_fixed / max(len(global_edits), 1)

    return {
        "targeted": targeted_rate,
        "global": global_rate,
        "targeted_n": len(targeted),
        "global_n": len(global_edits),
        "targeted_fixed": targeted_fixed,
        "global_fixed": global_fixed,
    }

def plot_fix_rate_bar(rates: dict, out_path: str) -> None:
    """Bar chart: fix rate by edit scope."""
    fig, ax = plt.subplots(figsize=(6, 4))
    x = ["Targeted", "Global"]
    y = [rates["targeted"], rates["global"]]
    colors = ["#4CAF50", "#F44336"]
    bars = ax.bar(x, y, color=colors)
    ax.set_ylabel("Fix Rate")
    ax.set_ylim(0, 1)
    ax.set_title("Fix Rate by Edit Scope")
    for bar, rate, n in zip(bars, y, [rates["targeted_n"], rates["global_n"]]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{rate:.1%}\n(n={n})", ha='center', va='bottom', fontsize=9)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_edit_distance_histogram(edit_records: list[dict], out_path: str) -> None:
    """Histogram of lines_changed distribution."""
    lines = [r.get("lines_changed", 0) for r in edit_records]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(lines, bins=20, edgecolor='black', alpha=0.7)
    ax.axvline(x=5, color='red', linestyle='--', label='Threshold (5)')
    ax.set_xlabel("Lines Changed")
    ax.set_ylabel("Count")
    ax.set_title("Edit Distance Distribution")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_fix_prob_vs_distance(edit_records: list[dict], out_path: str) -> None:
    """Scatter/binned plot: fix probability vs lines_changed."""
    if not edit_records:
        return
    lines = np.array([r.get("lines_changed", 0) for r in edit_records])
    fixed = np.array([1 if r.get("fixed") else 0 for r in edit_records])

    bins = np.arange(0, max(lines)+5, 5)
    bin_indices = np.digitize(lines, bins)

    bin_centers = []
    bin_rates = []
    for i in range(1, len(bins)+1):
        mask = bin_indices == i
        if np.sum(mask) > 0:
            bin_centers.append((bins[i-1] + bins[min(i, len(bins)-1)]) / 2)
            bin_rates.append(np.mean(fixed[mask]))

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(bin_centers, bin_rates, 'o-', markersize=8)
    ax.set_xlabel("Lines Changed (binned)")
    ax.set_ylabel("Fix Probability")
    ax.set_title("Fix Probability vs Edit Distance")
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def main() -> dict:
    """Load results, compute fix rates, gate check, save summary + figures."""
    with open(CONFIG.results_path) as f:
        data = json.load(f)

    edit_records = data.get("edit_records", [])
    label_edit_records(edit_records)

    rates = compute_fix_rates(edit_records)

    gate_passed = rates["targeted"] > rates["global"]
    improvement = rates["targeted"] - rates["global"]

    summary = {
        "targeted_fix_rate": rates["targeted"],
        "global_fix_rate": rates["global"],
        "targeted_n": rates["targeted_n"],
        "global_n": rates["global_n"],
        "improvement": improvement,
        "gate_passed": gate_passed,
        "gate_type": "MUST_WORK",
    }

    os.makedirs(CONFIG.figures_dir, exist_ok=True)

    plot_fix_rate_bar(rates, os.path.join(CONFIG.figures_dir, "fix_rate_bar.png"))
    plot_edit_distance_histogram(edit_records, os.path.join(CONFIG.figures_dir, "edit_distance_hist.png"))
    plot_fix_prob_vs_distance(edit_records, os.path.join(CONFIG.figures_dir, "fix_prob_vs_distance.png"))

    summary_path = CONFIG.results_path.replace("results.json", "evaluation_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print("\n=== Evaluation Summary ===")
    print(f"Targeted fix rate: {rates['targeted']:.1%} (n={rates['targeted_n']})")
    print(f"Global fix rate: {rates['global']:.1%} (n={rates['global_n']})")
    print(f"Improvement: {improvement:+.1%}")
    print(f"Gate (MUST_WORK): {'PASS' if gate_passed else 'FAIL'}")

    return summary

if __name__ == "__main__":
    main()
