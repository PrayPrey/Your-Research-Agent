"""H-M3 visualization: 5 figures as per PRD FR-6."""

import pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_f1_bar_comparison(summaries: dict, figures_dir: pathlib.Path) -> None:
    """F1: Bar chart pass@1 CondA vs B on MBPP+ and HumanEval+ with std error bars."""
    datasets = ["humaneval+", "mbpp+"]
    labels = ["HumanEval+", "MBPP+"]
    mean_a = [summaries.get(d, {}).get("welch_test", {}).get("mean_pass_a", 0) for d in datasets]
    mean_b = [summaries.get(d, {}).get("welch_test", {}).get("mean_pass_b", 0) for d in datasets]

    x = np.arange(len(datasets))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    bars_a = ax.bar(x - width / 2, mean_a, width, label="Condition A (exec-only)", color="#4878CF")
    bars_b = ax.bar(x + width / 2, mean_b, width, label="Condition B (exec+mypy)", color="#6ACC65")

    ax.set_ylabel("pass@1 (mean over seeds × rounds)")
    ax.set_title("H-M3: pass@1 Comparison — Condition A vs B")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.0)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    # Annotate gate result
    for d in datasets:
        s = summaries.get(d, {})
        wt = s.get("welch_test", {})
        gate_str = f"p={wt.get('p_value', 1.0):.3f}, Δ={wt.get('absolute_improvement', 0.0):+.3f}"
        idx = datasets.index(d)
        ax.text(idx, max(mean_a[idx], mean_b[idx]) + 0.02, gate_str,
                ha="center", fontsize=8)

    plt.tight_layout()
    plt.savefig(figures_dir / "f1_pass_at_1_comparison.png", dpi=150)
    plt.close()


def plot_f2_repair_trajectory(trajectory: dict, dataset: str,
                               figures_dir: pathlib.Path) -> None:
    """F2: Line plot mean pass@1 per round k=1..5, CondA vs B."""
    fig, ax = plt.subplots(figsize=(8, 5))
    for cond, color, label in [("A", "#4878CF", "Condition A (exec-only)"),
                                 ("B", "#6ACC65", "Condition B (exec+mypy)")]:
        if cond in trajectory:
            rounds = sorted(trajectory[cond].keys())
            vals = [trajectory[cond][k] for k in rounds]
            ax.plot(rounds, vals, marker="o", color=color, label=label)

    ax.set_xlabel("Repair Round (k)")
    ax.set_ylabel("pass@1")
    ax.set_title(f"H-M3: Repair Trajectory — {dataset}")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    safe_name = dataset.replace("+", "plus")
    plt.savefig(figures_dir / f"f2_repair_trajectory_{safe_name}.png", dpi=150)
    plt.close()


def plot_f3_delta_distribution(pass_a: list, pass_b: list,
                                figures_dir: pathlib.Path) -> None:
    """F3: Histogram of per-problem (B-A) deltas on MBPP+."""
    deltas = [b - a for a, b in zip(pass_a, pass_b)]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(deltas, bins=20, color="#D95F02", edgecolor="white", alpha=0.8)
    ax.axvline(0, color="black", linestyle="--", linewidth=1.5)
    ax.set_xlabel("Per-problem Δpass@1 (B − A)")
    ax.set_ylabel("Count")
    ax.set_title("H-M3: Per-problem Delta Distribution (MBPP+)")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(figures_dir / "f3_delta_distribution.png", dpi=150)
    plt.close()


def plot_f4_mypy_error_by_round(results: list, dataset: str,
                                 figures_dir: pathlib.Path) -> None:
    """F4: Line plot mean mypy error count per round k for CondB."""
    from collections import defaultdict
    cond_b = [r for r in results if r.get("condition") == "B"
              and r.get("dataset") == dataset]
    by_round = defaultdict(list)
    for r in cond_b:
        for rd in r.get("rounds", []):
            cnt = rd.get("mypy_error_count", 0)
            by_round[rd["round"]].append(cnt)

    rounds = sorted(by_round.keys())
    means = [np.mean(by_round[k]) for k in rounds]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(rounds, means, marker="s", color="#7B2D8B", linewidth=2)
    ax.set_xlabel("Repair Round (k)")
    ax.set_ylabel("Mean mypy error count")
    ax.set_title(f"H-M3: mypy Error Count per Round — {dataset} (Condition B)")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    safe_name = dataset.replace("+", "plus")
    plt.savefig(figures_dir / f"f4_mypy_error_by_round_{safe_name}.png", dpi=150)
    plt.close()


def plot_f5_token_count(confound_by_dataset: dict, figures_dir: pathlib.Path) -> None:
    """F5: Bar chart mean prompt tokens per round CondA vs B (MBPP+)."""
    dataset = "mbpp+"
    confound = confound_by_dataset.get(dataset, {})
    per_round_delta = confound.get("per_round_delta", {})
    rounds = sorted(per_round_delta.keys())
    deltas = [per_round_delta[k] for k in rounds]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(rounds, deltas, color="#E6AB02", edgecolor="white")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Repair Round (k)")
    ax.set_ylabel("Token delta (B − A)")
    ax.set_title("H-M3: Prompt Token Count Delta per Round (MBPP+, Condition B − A)")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(figures_dir / "f5_token_count_comparison.png", dpi=150)
    plt.close()


def generate_all_figures(summaries: dict, results: list,
                          figures_dir: pathlib.Path) -> None:
    """Generate all 5 figures."""
    figures_dir.mkdir(parents=True, exist_ok=True)

    plot_f1_bar_comparison(summaries, figures_dir)

    from analysis import compute_pass_at_1_by_round
    for dataset in ["humaneval+", "mbpp+"]:
        trajectory = compute_pass_at_1_by_round(results, dataset)
        plot_f2_repair_trajectory(trajectory, dataset, figures_dir)

    mbpp_summary = summaries.get("mbpp+", {})
    if mbpp_summary:
        plot_f3_delta_distribution(
            mbpp_summary.get("pass_a", []),
            mbpp_summary.get("pass_b", []),
            figures_dir
        )

    for dataset in ["humaneval+", "mbpp+"]:
        plot_f4_mypy_error_by_round(results, dataset, figures_dir)

    confound_by_dataset = {d: summaries.get(d, {}).get("confound", {})
                           for d in ["humaneval+", "mbpp+"]}
    plot_f5_token_count(confound_by_dataset, figures_dir)
