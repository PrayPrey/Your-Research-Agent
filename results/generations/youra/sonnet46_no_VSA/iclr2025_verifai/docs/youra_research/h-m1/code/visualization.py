"""Visualization for H-M1 oracle isolation experiment."""
import numpy as np
from pathlib import Path


def _save(fig, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"Saved: {path}")


def plot_gate_metrics(stats, out_path: str = "figures/gate_metrics_comparison.png") -> None:
    """Required: bar chart of gate metrics vs thresholds with 95% CI."""
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    fig.suptitle("H-M1 Gate Metrics vs Thresholds", fontsize=14)

    # Plot 1: Oracle isolation gap
    ax = axes[0]
    gap = stats.mean_isolation_gap
    gap_err_lo = gap - stats.gap_ci_lower
    gap_err_hi = stats.gap_ci_upper - gap
    ax.bar([0], [gap], yerr=[[gap_err_lo], [gap_err_hi]], capsize=8,
           color="steelblue", alpha=0.8, label="Mean gap")
    ax.axhline(0.10, color="red", linestyle="--", linewidth=1.5, label="Threshold (0.10)")
    ax.set_xticks([0])
    ax.set_xticklabels(["Oracle Isolation Gap"])
    ax.set_ylabel("Gap (contract_rate − diff_rate)")
    ax.set_title(f"Gap = {gap:.3f}\n(CI: [{stats.gap_ci_lower:.3f}, {stats.gap_ci_upper:.3f}])")
    ax.legend()
    ax.set_ylim(bottom=min(0, gap - gap_err_lo - 0.05))

    # Plot 2: Contract-unique mass
    ax2 = axes[1]
    cu = stats.mean_contract_unique_mass
    cu_err_lo = cu - stats.cu_ci_lower
    cu_err_hi = stats.cu_ci_upper - cu
    ax2.bar([0], [cu], yerr=[[cu_err_lo], [cu_err_hi]], capsize=8,
            color="darkorange", alpha=0.8, label="CU mass")
    ax2.axhline(0.05, color="red", linestyle="--", linewidth=1.5, label="Threshold (0.05)")
    ax2.axhline(0.03, color="orange", linestyle=":", linewidth=1, label="CI lower threshold (0.03)")
    ax2.set_xticks([0])
    ax2.set_xticklabels(["Contract-Unique Mass"])
    ax2.set_ylabel("Fraction of inputs")
    ax2.set_title(f"CU mass = {cu:.3f}\n(CI lower: {stats.cu_ci_lower:.3f})")
    ax2.legend()
    ax2.set_ylim(bottom=0)

    gate_str = "PASSED" if stats.gate_passed else "FAILED"
    fig.text(0.5, 0.01, f"Gate: {gate_str} | Wilcoxon p={stats.wilcoxon_p_corrected:.4f}",
             ha="center", fontsize=11, color="green" if stats.gate_passed else "red")

    _save(fig, out_path)
    plt.close(fig)


def plot_oracle_breakdown_by_model(results: list, out_path: str = "figures/oracle_failure_breakdown.png") -> None:
    """Stacked bar per model: redundant / contract_unique / differential_only / neither."""
    import matplotlib.pyplot as plt
    from dataclasses import asdict

    model_data = {}
    for r in results:
        m = r.model
        model_data.setdefault(m, {"redundant": 0, "cu": 0, "diff_only": 0, "neither": 0, "n": 0})
        model_data[m]["redundant"] += r.n_redundant
        model_data[m]["cu"] += r.n_contract_unique
        model_data[m]["diff_only"] += r.n_differential_only
        model_data[m]["neither"] += r.n_neither
        model_data[m]["n"] += r.n_inputs

    models = list(model_data.keys())
    n = len(models)
    if n == 0:
        return

    cats = ["neither", "diff_only", "redundant", "cu"]
    colors = ["#aec7e8", "#ffbb78", "#ff9896", "#98df8a"]
    labels = ["Neither", "Diff-only", "Redundant", "Contract-unique"]

    fig, ax = plt.subplots(figsize=(max(8, n * 2), 5))
    bottoms = np.zeros(n)
    for cat, color, label in zip(cats, colors, labels):
        vals = np.array([
            model_data[m][cat] / max(model_data[m]["n"], 1)
            for m in models
        ])
        ax.bar(models, vals, bottom=bottoms, color=color, label=label, alpha=0.85)
        bottoms += vals

    ax.set_ylabel("Fraction of inputs")
    ax.set_title("Oracle Failure Breakdown by Model")
    ax.legend(loc="upper right")
    ax.set_ylim(0, 1)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    _save(fig, out_path)
    plt.close(fig)


def plot_gap_distribution(per_task: dict, out_path: str = "figures/gap_distribution.png") -> None:
    """Violin of per-task oracle-isolation gap."""
    import matplotlib.pyplot as plt

    gaps = [d["mean_gap"] for d in per_task.values()]
    if not gaps:
        return

    fig, ax = plt.subplots(figsize=(6, 5))
    parts = ax.violinplot([gaps], showmedians=True)
    ax.axhline(0.10, color="red", linestyle="--", label="Threshold (0.10)")
    ax.axhline(0, color="gray", linestyle=":", alpha=0.5)
    ax.set_xticks([1])
    ax.set_xticklabels(["Oracle Isolation Gap"])
    ax.set_ylabel("Per-task mean gap")
    ax.set_title(f"Distribution across {len(gaps)} tasks\nmean={np.mean(gaps):.3f}")
    ax.legend()
    plt.tight_layout()
    _save(fig, out_path)
    plt.close(fig)


def plot_scatter_failure_rates(per_task: dict, out_path: str = "figures/scatter_failure_rates.png") -> None:
    """Scatter: per-task diff_rate (x) vs contract_rate (y)."""
    import matplotlib.pyplot as plt

    diff_rates = [d["mean_diff_rate"] for d in per_task.values()]
    contract_rates = [d["mean_contract_rate"] for d in per_task.values()]
    task_types = [d["task_type"] for d in per_task.values()]

    if not diff_rates:
        return

    fig, ax = plt.subplots(figsize=(7, 6))
    colors = {"humaneval": "steelblue", "mbpp": "darkorange"}
    for tt in set(task_types):
        x = [d for d, t in zip(diff_rates, task_types) if t == tt]
        y = [c for c, t in zip(contract_rates, task_types) if t == tt]
        ax.scatter(x, y, alpha=0.4, s=20, color=colors.get(tt, "gray"), label=tt)

    # y=x line (equal failure rates)
    lim = max(max(diff_rates + contract_rates), 0.1)
    ax.plot([0, lim], [0, lim], "k--", alpha=0.4, label="y=x (equal)")
    ax.set_xlabel("Differential failure rate (Oracle A)")
    ax.set_ylabel("Contract failure rate (Oracle B)")
    ax.set_title("Per-task Oracle Failure Rates")
    ax.legend()
    plt.tight_layout()
    _save(fig, out_path)
    plt.close(fig)
