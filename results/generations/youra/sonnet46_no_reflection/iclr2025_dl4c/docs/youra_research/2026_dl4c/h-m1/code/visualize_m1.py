import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import M1ExperimentConfig


def plot_gate_sep_comparison(
    sep_results: dict,
    ci_results: dict,
    output_path: str,
) -> None:
    """FR-7.1 MANDATORY: Bar chart — mean SEP per condition with 95% CI error bars."""
    conditions = ["grpo_binary", "grpo_errortype", "dpo"]
    labels = ["GRPO-Binary", "GRPO-ErrorType", "DPO"]
    means = []
    errors = []

    for cond in conditions:
        ci = ci_results.get(cond, {})
        mean = ci.get("mean", 0.0)
        lower = ci.get("lower", mean)
        upper = ci.get("upper", mean)
        means.append(mean if not (mean != mean) else 0.0)  # nan-safe
        errors.append((mean - lower, upper - mean))

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(labels))
    yerr_low = [e[0] for e in errors]
    yerr_high = [e[1] for e in errors]
    colors = ["#2196F3", "#4CAF50", "#FF5722"]

    bars = ax.bar(x, means, color=colors, alpha=0.8, edgecolor="black", linewidth=0.8)
    ax.errorbar(x, means, yerr=[yerr_low, yerr_high], fmt="none",
                color="black", capsize=5, linewidth=1.5)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Mean Semantic Edit Proportion (SEP)", fontsize=11)
    ax.set_title("SEP Comparison: GRPO vs DPO (Gate Metric)", fontsize=13, fontweight="bold")
    ax.set_ylim(0, max(means) * 1.4 + 0.05 if means else 1.0)
    ax.grid(axis="y", alpha=0.3)

    for bar, mean in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f"{mean:.3f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_ast_edit_distribution(
    edit_distributions: dict,
    output_path: str,
) -> None:
    """FR-7.2: Stacked horizontal bar — CF/DF/surface proportions per condition."""
    conditions = ["grpo_binary", "grpo_errortype", "dpo"]
    labels = ["GRPO-Binary", "GRPO-ErrorType", "DPO"]
    cf_vals, df_vals, surf_vals = [], [], []

    for cond in conditions:
        dist = edit_distributions.get(cond, {})
        cf_vals.append(dist.get("control_flow", 0.0))
        df_vals.append(dist.get("data_flow", 0.0))
        surf_vals.append(dist.get("surface", 0.0))

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(labels))
    w = 0.5

    p1 = ax.bar(x, cf_vals, w, label="Control Flow", color="#1976D2")
    p2 = ax.bar(x, df_vals, w, bottom=cf_vals, label="Data Flow", color="#388E3C")
    surf_bottom = [c + d for c, d in zip(cf_vals, df_vals)]
    p3 = ax.bar(x, surf_vals, w, bottom=surf_bottom, label="Surface", color="#F57C00", alpha=0.7)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Edit Proportion", fontsize=11)
    ax.set_title("AST Edit Distribution by Category", fontsize=13, fontweight="bold")
    ax.legend(loc="upper right", fontsize=9)
    ax.set_ylim(0, 1.15)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_reward_correctness_scatter(
    reward_signals: dict,
    pass_at_1: dict,
    spearman_results: dict,
    output_path: str,
) -> None:
    """FR-7.3: Scatter — reward signal vs pass@1, annotated with Spearman rho."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    conditions = [("grpo_binary", "GRPO-Binary"), ("grpo_errortype", "GRPO-ErrorType")]
    colors = ["#2196F3", "#4CAF50"]

    for ax, (cond, label), color in zip(axes, conditions, colors):
        r = reward_signals.get(cond, [])
        p = pass_at_1.get(cond, [])
        n = min(len(r), len(p))
        if n > 0:
            ax.scatter(r[:n], p[:n], alpha=0.6, color=color, s=30, edgecolors="none")
        spear = spearman_results.get(cond, {})
        rho = spear.get("rho", float("nan"))
        p_val = spear.get("p_value", float("nan"))
        rho_str = f"ρ={rho:.3f}" if rho == rho else "ρ=N/A"
        p_str = f"p={p_val:.3f}" if p_val == p_val else "p=N/A"
        ax.set_title(f"{label}\n{rho_str}, {p_str}", fontsize=11)
        ax.set_xlabel("Reward Signal", fontsize=10)
        ax.set_ylabel("Pass@1", fontsize=10)
        ax.grid(alpha=0.3)

    plt.suptitle("Reward Signal vs Pass@1 (Spearman Correlation)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_sep_vs_kl_trajectory(
    pairs_data: dict,
    output_path: str,
) -> None:
    """FR-7.4: Line plot — mean SEP vs KL divergence over training steps, GRPO vs DPO."""
    fig, ax = plt.subplots(figsize=(9, 5))

    for cond, label, color in [
        ("grpo_binary", "GRPO-Binary", "#2196F3"),
        ("dpo", "DPO", "#FF5722"),
    ]:
        pairs = pairs_data.get(cond, {}).get("pairs", [])
        kl_vals = []
        sep_vals = []
        for pair in sorted(pairs, key=lambda p: p.get("kl_grpo", p.get("kl_dpo", 0))):
            kl = pair.get("kl_grpo", pair.get("kl_dpo", float("nan")))
            sep_g = pair.get("sep_grpo", [])
            sep_d = pair.get("sep_dpo", [])
            sep_list = sep_g if cond != "dpo" else sep_d
            if sep_list and kl == kl:
                kl_vals.append(kl)
                sep_vals.append(float(np.mean(sep_list)))
        if kl_vals:
            ax.plot(kl_vals, sep_vals, "o-", label=label, color=color, alpha=0.8, markersize=4)

    ax.set_xlabel("KL Divergence from Base Model", fontsize=11)
    ax.set_ylabel("Mean SEP", fontsize=11)
    ax.set_title("SEP vs KL Trajectory: GRPO vs DPO", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_ast_node_heatmap(
    node_freq_grpo: dict,
    node_freq_dpo: dict,
    node_types: list,
    output_path: str,
) -> None:
    """FR-7.5: Seaborn heatmap — normalized AST node frequencies, GRPO vs DPO rows."""
    total_grpo = sum(node_freq_grpo.values()) or 1
    total_dpo = sum(node_freq_dpo.values()) or 1

    matrix = np.array([
        [node_freq_grpo.get(n, 0) / total_grpo for n in node_types],
        [node_freq_dpo.get(n, 0) / total_dpo for n in node_types],
    ])

    fig, ax = plt.subplots(figsize=(10, 3))
    sns.heatmap(
        matrix,
        xticklabels=node_types,
        yticklabels=["GRPO", "DPO"],
        annot=True,
        fmt=".3f",
        cmap="YlOrRd",
        ax=ax,
        linewidths=0.5,
    )
    ax.set_title("AST Node Type Frequencies (Normalized): GRPO vs DPO", fontsize=12, fontweight="bold")
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def generate_all_figures(
    sep_results: dict,
    cfg: M1ExperimentConfig,
) -> None:
    """Call all 5 plot functions. Saves to cfg.figures_dir. Creates dir if missing."""
    code_dir = os.path.dirname(os.path.abspath(__file__))
    figures_dir = os.path.normpath(os.path.join(code_dir, cfg.figures_dir))
    os.makedirs(figures_dir, exist_ok=True)

    ci = sep_results.get("ci", {})
    plot_gate_sep_comparison(
        sep_results, ci,
        os.path.join(figures_dir, "gate_sep_comparison.png"),
    )

    # Aggregate edit distributions per condition
    edit_distributions = {}
    for cond in ["grpo_binary", "grpo_errortype", "dpo"]:
        cond_data = sep_results.get(cond, {})
        pairs = cond_data.get("pairs", [])
        cf_vals, df_vals, surf_vals = [], [], []
        for pair in pairs:
            for task_dist in (pair.get("edit_dist_grpo", {}) if cond != "dpo"
                              else pair.get("edit_dist_dpo", {})).values():
                cf_vals.append(task_dist.get("control_flow", 0.0))
                df_vals.append(task_dist.get("data_flow", 0.0))
                surf_vals.append(task_dist.get("surface", 0.0))
        if cf_vals:
            edit_distributions[cond] = {
                "control_flow": float(np.mean(cf_vals)),
                "data_flow": float(np.mean(df_vals)),
                "surface": float(np.mean(surf_vals)),
            }
        else:
            edit_distributions[cond] = {"control_flow": 0.0, "data_flow": 0.0, "surface": 0.0}

    plot_ast_edit_distribution(
        edit_distributions,
        os.path.join(figures_dir, "ast_edit_distribution.png"),
    )

    # Scatter: reward signals and pass@1 (use empty dicts if not available)
    stat_results = sep_results.get("stat_results", {})
    spearman = stat_results.get("spearman", {})
    plot_reward_correctness_scatter(
        reward_signals={},
        pass_at_1={},
        spearman_results=spearman,
        output_path=os.path.join(figures_dir, "reward_correctness_scatter.png"),
    )

    plot_sep_vs_kl_trajectory(
        pairs_data=sep_results,
        output_path=os.path.join(figures_dir, "sep_vs_kl_trajectory.png"),
    )

    # Node heatmap
    node_types = ["If", "For", "While", "Assign", "Call", "Return"]
    all_grpo_codes = []
    all_dpo_codes = []
    from ast_decomposition import compute_node_type_frequencies
    node_freq_grpo = compute_node_type_frequencies(all_grpo_codes, node_types)
    node_freq_dpo = compute_node_type_frequencies(all_dpo_codes, node_types)
    plot_ast_node_heatmap(
        node_freq_grpo, node_freq_dpo, node_types,
        os.path.join(figures_dir, "ast_node_heatmap.png"),
    )
