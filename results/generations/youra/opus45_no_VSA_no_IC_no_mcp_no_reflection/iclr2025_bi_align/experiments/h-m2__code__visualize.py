"""H-M2 Visualize: Gate comparison, constraint breakdown, alpha-beta tradeoff."""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from config import VARIANTS


def plot_gate_comparison(eval_results: dict, gate: dict, out_dir: Path):
    """Bar chart: strict accuracy per variant with threshold line."""
    out_dir.mkdir(parents=True, exist_ok=True)

    variants_order = ["B1", "B2", "B3", "T1", "T2", "T3", "T4"]
    scores = [eval_results.get(v, {}).get("strict_accuracy", 0) for v in variants_order]

    colors = ["#4169E1"] * 3 + ["#32CD32"] * 4  # blue for baselines, green for treatments

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(variants_order, scores, color=colors, edgecolor="black", alpha=0.8)

    # Threshold line
    threshold = gate.get("baseline_max", 0) + 0.02 if gate.get("baseline_max") else 0.5
    ax.axhline(y=threshold, color="red", linestyle="--", linewidth=2, label=f"Gate threshold ({threshold:.1%})")

    ax.set_xlabel("Model Variant", fontsize=12)
    ax.set_ylabel("IFEval Strict Accuracy", fontsize=12)
    ax.set_title("H-M2: IFEval Strict Accuracy by Variant", fontsize=14)
    ax.set_ylim(0, 1.0)
    ax.legend()

    # Add value labels
    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{score:.1%}", ha="center", fontsize=10)

    plt.tight_layout()
    plt.savefig(out_dir / "gate_comparison.png", dpi=150)
    plt.close()
    print(f"Saved gate_comparison.png")


def plot_constraint_breakdown(eval_results: dict, out_dir: Path):
    """Grouped bars: accuracy per constraint type per variant."""
    out_dir.mkdir(parents=True, exist_ok=True)

    variants_order = ["B1", "B2", "B3", "T1", "T2", "T3", "T4"]
    all_types = set()
    for v in variants_order:
        if v in eval_results and "per_constraint_type" in eval_results[v]:
            all_types.update(eval_results[v]["per_constraint_type"].keys())

    all_types = sorted(all_types)
    if not all_types:
        print("No constraint type data available")
        return

    x = np.arange(len(all_types))
    width = 0.1
    fig, ax = plt.subplots(figsize=(14, 6))

    for i, variant in enumerate(variants_order):
        if variant not in eval_results:
            continue
        per_type = eval_results[variant].get("per_constraint_type", {})
        scores = [per_type.get(t, 0) for t in all_types]
        offset = (i - len(variants_order)/2) * width
        ax.bar(x + offset, scores, width, label=variant, alpha=0.8)

    ax.set_xlabel("Constraint Type", fontsize=12)
    ax.set_ylabel("Accuracy", fontsize=12)
    ax.set_title("H-M2: Accuracy by Constraint Type", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(all_types, rotation=45, ha="right")
    ax.legend()
    ax.set_ylim(0, 1.0)

    plt.tight_layout()
    plt.savefig(out_dir / "constraint_breakdown.png", dpi=150)
    plt.close()
    print(f"Saved constraint_breakdown.png")


def plot_alpha_beta_tradeoff(eval_results: dict, out_dir: Path):
    """Scatter: T1-T4 IFEval strict vs alpha, annotated."""
    out_dir.mkdir(parents=True, exist_ok=True)

    variant_lookup = {v.name: v for v in VARIANTS}
    treatments = ["T1", "T2", "T3", "T4"]

    alphas = []
    ifeval_scores = []
    labels = []

    for t in treatments:
        if t not in eval_results:
            continue
        variant = variant_lookup[t]
        alphas.append(variant.alpha)
        ifeval_scores.append(eval_results[t].get("strict_accuracy", 0))
        labels.append(f"{t}\n(α={variant.alpha}, β={variant.beta})")

    if not alphas:
        print("No treatment data available")
        return

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(alphas, ifeval_scores, s=200, c="green", alpha=0.7, edgecolors="black")

    for i, label in enumerate(labels):
        ax.annotate(label, (alphas[i], ifeval_scores[i]), textcoords="offset points",
                    xytext=(0, 15), ha="center", fontsize=9)

    ax.set_xlabel("α (Helpfulness Weight)", fontsize=12)
    ax.set_ylabel("IFEval Strict Accuracy", fontsize=12)
    ax.set_title("H-M2: IFEval vs Helpfulness Weight", fontsize=14)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(out_dir / "alpha_beta_tradeoff.png", dpi=150)
    plt.close()
    print(f"Saved alpha_beta_tradeoff.png")


def generate_all_plots(eval_results: dict, gate: dict, out_dir: Path):
    """Generate all visualization plots."""
    plot_gate_comparison(eval_results, gate, out_dir)
    plot_constraint_breakdown(eval_results, out_dir)
    plot_alpha_beta_tradeoff(eval_results, out_dir)


if __name__ == "__main__":
    base_dir = Path(__file__).parent / "outputs"
    out_dir = base_dir / "figures"

    with open(base_dir / "eval_results.json") as f:
        eval_results = json.load(f)

    with open(base_dir / "gate_result.json") as f:
        gate = json.load(f)

    generate_all_plots(eval_results, gate, out_dir)
