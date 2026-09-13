"""H-M2 figure generation."""

import pathlib
import logging

logger = logging.getLogger(__name__)


def generate_all_figures(analysis: dict, results_a: list, results_b: list,
                         figures_dir: pathlib.Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        import numpy as np
    except ImportError:
        logger.warning("matplotlib not available — skipping figures")
        return

    figures_dir.mkdir(parents=True, exist_ok=True)

    type_info = analysis["type_error"]
    non_info = analysis["non_type_error"]

    # Figure 1: 4-bar repair rate comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    categories = ["Type-Error\n(Cond A)", "Type-Error\n(Cond B)",
                  "Non-Type\n(Cond A)", "Non-Type\n(Cond B)"]
    values = [type_info["rate_A"], type_info["rate_B"],
              non_info["rate_A"], non_info["rate_B"]]
    colors = ["#E57373", "#EF9A9A", "#64B5F6", "#90CAF9"]
    bars = ax.bar(categories, values, color=colors, edgecolor="black", width=0.6)
    ax.set_ylabel("Repair Rate at k=5")
    ax.set_title(f"H-M2: Per-Category Repair Rate by Condition\n"
                 f"n_type={type_info['n']}, n_non_type={non_info['n']}")
    ax.set_ylim(0, 1.1)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{val:.1%}", ha="center", va="bottom", fontsize=10)
    plt.tight_layout()
    plt.savefig(figures_dir / "repair_rate_comparison.png", dpi=150)
    plt.close()

    # Figure 2: Differential bar chart
    fig, ax = plt.subplots(figsize=(8, 5))
    delta_vals = [type_info["delta"], non_info["delta"]]
    delta_labels = [f"Type-Error\n(n={type_info['n']})",
                    f"Non-Type-Error\n(n={non_info['n']})"]
    delta_colors = ["#C62828" if v > 0 else "#1565C0" for v in delta_vals]
    bars = ax.bar(delta_labels, delta_vals, color=delta_colors, edgecolor="black", width=0.5)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_ylabel("Δ Repair Rate (Cond B − Cond A)")
    ax.set_title(f"H-M2: Differential Analysis\nDifferential = {analysis['differential']:.3f}"
                 f" (gate: {'PASS' if analysis['gate_passed'] else 'FAIL'})")
    for bar, val in zip(bars, delta_vals):
        ypos = val + 0.01 if val >= 0 else val - 0.03
        ax.text(bar.get_x() + bar.get_width() / 2, ypos,
                f"{val:+.1%}", ha="center", va="bottom", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(figures_dir / "differential_chart.png", dpi=150)
    plt.close()

    # Figure 3: Gate metrics summary
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis("off")
    summary = [
        ["Metric", "Value"],
        ["Type-error problems (n)", str(type_info["n"])],
        ["Non-type-error problems (n)", str(non_info["n"])],
        ["Repair rate Cond A (type)", f"{type_info['rate_A']:.1%}"],
        ["Repair rate Cond B (type)", f"{type_info['rate_B']:.1%}"],
        ["delta_type (B−A)", f"{type_info['delta']:+.3f}"],
        ["Repair rate Cond A (non-type)", f"{non_info['rate_A']:.1%}"],
        ["Repair rate Cond B (non-type)", f"{non_info['rate_B']:.1%}"],
        ["delta_non (B−A)", f"{non_info['delta']:+.3f}"],
        ["Differential (delta_type − delta_non)", f"{analysis['differential']:+.3f}"],
        ["Gate (differential > 0)", "PASS" if analysis["gate_passed"] else "FAIL"],
    ]
    table = ax.table(cellText=summary[1:], colLabels=summary[0],
                     loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)
    ax.set_title("H-M2 Gate Metrics", fontweight="bold", pad=20)
    plt.tight_layout()
    plt.savefig(figures_dir / "gate_metrics.png", dpi=150)
    plt.close()

    logger.info(f"Figures saved to {figures_dir}")
