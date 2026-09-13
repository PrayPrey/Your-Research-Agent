"""Evaluation and figure generation for H-M2."""
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import CFG


def summarize_methods(results: dict) -> pd.DataFrame:
    """Create summary DataFrame."""
    rows = []
    for name, r in results.items():
        rows.append({
            "method": name,
            "accuracy": r["acc_ensemble"],
            "improvement_pct": r["improvement_pct"],
            "p_value": r["p_value"],
            "hypothesis_supported": r["hypothesis_supported"]
        })
    return pd.DataFrame(rows)


def plot_accuracy_comparison(results: dict, path: str) -> None:
    """Bar chart comparing ensemble methods vs best single judge."""
    methods = list(results.keys())
    accs = [results[m]["acc_ensemble"] for m in methods]
    best_single = results[methods[0]]["acc_best_single"]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(methods) + 1)
    bars = ax.bar(x, [best_single] + accs, color=["gray"] + ["steelblue"] * len(methods))

    ax.axhline(y=best_single + 0.03, color="red", linestyle="--", label="+3% target")
    ax.set_xticks(x)
    ax.set_xticklabels(["Best Single"] + methods, rotation=45, ha="right")
    ax.set_ylabel("Accuracy")
    ax.set_title("Ensemble Methods vs Best Single Judge")
    ax.legend()

    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


def plot_contingency_heatmap(results: dict, method: str, path: str) -> None:
    """Heatmap of McNemar contingency table."""
    table = np.array(results[method]["contingency_table"])

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(table, cmap="Blues")

    labels = [["Both Correct", "Ensemble Only"], ["Best Only", "Both Wrong"]]
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{labels[i][j]}\n{table[i, j]}", ha="center", va="center")

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"McNemar Contingency: {method}")

    plt.colorbar(im)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


def plot_pivot_breakdown(results: dict, path: str) -> None:
    """Bar chart of unanimous vs split accuracy."""
    methods = list(results.keys())

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(methods))
    width = 0.35

    unanimous_acc = [results[m]["pivot"]["unanimous_acc"] or 0 for m in methods]
    split_acc = [results[m]["pivot"]["split_acc"] or 0 for m in methods]

    ax.bar(x - width/2, unanimous_acc, width, label="Unanimous", color="forestgreen")
    ax.bar(x + width/2, split_acc, width, label="Split", color="coral")

    ax.set_xticks(x)
    ax.set_xticklabels(methods, rotation=45, ha="right")
    ax.set_ylabel("Accuracy")
    ax.set_title("Ensemble Accuracy: Unanimous vs Split Verdicts")
    ax.legend()

    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


def main():
    print("Generating figures...")

    with open(CFG.mcnemar_json_path) as f:
        results = json.load(f)

    plot_accuracy_comparison(results, f"{CFG.figures_dir}/accuracy_comparison.png")
    plot_contingency_heatmap(results, "AB1_majority", f"{CFG.figures_dir}/contingency_ab1.png")
    plot_pivot_breakdown(results, f"{CFG.figures_dir}/pivot_breakdown.png")

    print("Done.")


if __name__ == "__main__":
    main()
