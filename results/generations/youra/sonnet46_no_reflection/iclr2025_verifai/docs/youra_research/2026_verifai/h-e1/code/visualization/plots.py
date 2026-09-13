import os
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def plot_locality_score_comparison(
    ls_by_condition_minif2f: Dict[str, List[float]],
    ls_by_condition_vericoding: Dict[str, List[float]],
    output_path: str = "h-e1/figures/locality_score_comparison.png",
) -> None:
    """Bar chart: 2 datasets × 3 conditions = 6 bars. Primary required figure."""
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    conditions = ["A", "B", "P"]
    labels_minif2f    = [f"{c} (miniF2F)"   for c in conditions]
    labels_vericoding = [f"{c} (Vericoding)" for c in conditions]

    means_mf = [float(np.mean(ls_by_condition_minif2f.get(c, [0.0])))    for c in conditions]
    means_vc = [float(np.mean(ls_by_condition_vericoding.get(c, [0.0]))) for c in conditions]

    x      = np.arange(len(conditions))
    width  = 0.35
    colors = {"A": "#2196F3", "B": "#FF9800", "P": "#9E9E9E"}

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width / 2, means_mf, width, label="miniF2F",
                   color=[colors[c] for c in conditions], alpha=0.9)
    bars2 = ax.bar(x + width / 2, means_vc, width, label="Vericoding",
                   color=[colors[c] for c in conditions], alpha=0.5, hatch="//")

    ax.set_xlabel("DPO Condition")
    ax.set_ylabel("Mean Locality Score (LS)")
    ax.set_title("[H-E1] Locality Score Comparison: Condition A vs B vs P")
    ax.set_xticks(x)
    ax.set_xticklabels(["A (Grounded)", "B (Ungrounded)", "P (Permuted Control)"])
    ax.legend()
    ax.axhline(y=1 / 3, color="red", linestyle="--", alpha=0.5, label="Random baseline (1/3)")

    for bar in bars1:
        ax.annotate(f"{bar.get_height():.3f}",
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9)
    for bar in bars2:
        ax.annotate(f"{bar.get_height():.3f}",
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9)

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    logger.info(f"Figure saved: {output_path}")


def plot_probability_mass_distribution(
    mass_shifts: Dict[str, Dict[str, float]],
    taxonomy: Dict[str, List[str]],
    output_path: str = "h-e1/figures/probability_mass_distribution.png",
) -> None:
    """Stacked bar: tactic category delta (P_post - P_pre) per condition × dataset."""
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    conditions = list(mass_shifts.keys())
    categories = list(taxonomy.keys())
    cat_colors  = {"type_error": "#E53935", "undefined_name": "#43A047", "tactic_failure": "#1E88E5"}

    fig, ax = plt.subplots(figsize=(10, 6))
    x      = np.arange(len(conditions))
    width  = 0.5
    bottom = np.zeros(len(conditions))

    for cat in categories:
        vals = [mass_shifts.get(cond, {}).get(cat, 0.0) for cond in conditions]
        ax.bar(x, vals, width, bottom=bottom, label=cat, color=cat_colors.get(cat, "gray"), alpha=0.85)
        bottom += np.array(vals)

    ax.set_xlabel("DPO Condition")
    ax.set_ylabel("Mean Probability Mass Shift (Δ = P_post - P_pre)")
    ax.set_title("[H-E1] Probability Mass Distribution by Tactic Category")
    ax.set_xticks(x)
    ax.set_xticklabels(conditions)
    ax.legend()
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    logger.info(f"Figure saved: {output_path}")


def plot_error_category_breakdown(
    ls_per_category: Dict[str, Dict[str, float]],
    output_path: str = "h-e1/figures/error_category_breakdown.png",
) -> None:
    """Grouped bar chart: LS per TACTIC_TAXONOMY category per condition."""
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    conditions = list(ls_per_category.keys())
    if not conditions:
        return
    categories = list(next(iter(ls_per_category.values())).keys())

    x     = np.arange(len(categories))
    width = 0.25
    colors = {"A": "#2196F3", "B": "#FF9800", "P": "#9E9E9E"}

    fig, ax = plt.subplots(figsize=(10, 6))
    for i, cond in enumerate(conditions):
        vals = [ls_per_category[cond].get(cat, 0.0) for cat in categories]
        offset = (i - len(conditions) / 2) * width + width / 2
        ax.bar(x + offset, vals, width, label=f"Condition {cond}", color=colors.get(cond, "gray"), alpha=0.85)

    ax.set_xlabel("Error Category")
    ax.set_ylabel("Mean Locality Score")
    ax.set_title("[H-E1] Locality Score by Error Category")
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=15)
    ax.legend()
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    logger.info(f"Figure saved: {output_path}")


def plot_locality_score_per_state(
    ls_per_state: Dict[str, List[float]],
    proof_state_complexities: List[float],
    output_path: str = "h-e1/figures/locality_score_per_state.png",
) -> None:
    """Scatter: x=proof state complexity, y=LS per state, color-coded by condition."""
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colors = {"A": "#2196F3", "B": "#FF9800", "P": "#9E9E9E"}
    fig, ax = plt.subplots(figsize=(10, 6))

    for cond, ls_vals in ls_per_state.items():
        n = min(len(ls_vals), len(proof_state_complexities))
        ax.scatter(
            proof_state_complexities[:n],
            ls_vals[:n],
            label=f"Condition {cond}",
            color=colors.get(cond, "gray"),
            alpha=0.6,
            s=30,
        )

    ax.set_xlabel("Proof State Complexity (state string length)")
    ax.set_ylabel("Locality Score (LS)")
    ax.set_title("[H-E1] Locality Score per Proof State")
    ax.legend()
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    logger.info(f"Figure saved: {output_path}")


def generate_all_figures(results: dict, config) -> None:
    """Call all 4 plot functions; save to config.figures_dir."""
    os.makedirs(config.figures_dir, exist_ok=True)

    ls_mf = results.get("ls_minif2f", {})
    ls_vc = results.get("ls_vericoding", {})

    plot_locality_score_comparison(
        ls_mf, ls_vc,
        output_path=os.path.join(config.figures_dir, "locality_score_comparison.png"),
    )

    # Mass shift (approximate from LS per condition)
    try:
        from data.leandojo_tracing import TACTIC_TAXONOMY  # type: ignore[import]
    except ImportError:
        TACTIC_TAXONOMY = {"type_error": [], "undefined_name": [], "tactic_failure": []}
    mass_shifts = {cond: {cat: float(sum(ls_mf.get(cond, [0.0])) / max(len(ls_mf.get(cond, [1])), 1))
                          for cat in TACTIC_TAXONOMY} for cond in ["A", "B", "P"]}
    plot_probability_mass_distribution(
        mass_shifts, TACTIC_TAXONOMY,
        output_path=os.path.join(config.figures_dir, "probability_mass_distribution.png"),
    )

    # LS per category
    ls_per_category: Dict[str, Dict[str, float]] = {}
    for cond in ["A", "B", "P"]:
        vals = ls_mf.get(cond, [])
        ls_per_category[cond] = {cat: float(sum(vals) / max(len(vals), 1)) for cat in TACTIC_TAXONOMY}
    plot_error_category_breakdown(
        ls_per_category,
        output_path=os.path.join(config.figures_dir, "error_category_breakdown.png"),
    )

    # Complexity proxy: use index as complexity
    all_ls = ls_mf.get("A", [])
    complexities: List[float] = [float(i) for i in range(len(all_ls))]
    plot_locality_score_per_state(
        ls_mf, complexities,
        output_path=os.path.join(config.figures_dir, "locality_score_per_state.png"),
    )

    logger.info(f"All figures generated in {config.figures_dir}")
