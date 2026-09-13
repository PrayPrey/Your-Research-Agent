"""H-M1 visualization: 4 figure functions for repair loop results."""

import pathlib
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIGURES_DIR = pathlib.Path("docs/youra_research/h-m1/figures")
COLOR_MBPP = "#2196F3"
COLOR_HUMANEVAL = "#FF9800"
BENCHMARK_COLORS = {"mbpp": COLOR_MBPP, "humaneval": COLOR_HUMANEVAL}


def plot_error_trajectory(
    mean_errors: dict,
    figures_dir: pathlib.Path = FIGURES_DIR,
) -> None:
    """Line plot: mean mypy error count ± std vs round k, per benchmark."""
    figures_dir = pathlib.Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    for benchmark, trajectory in mean_errors.items():
        rounds = sorted(trajectory.keys())
        means = [trajectory[k]["mean"] for k in rounds]
        stds = [trajectory[k]["std"] for k in rounds]
        color = BENCHMARK_COLORS.get(benchmark, "#666666")
        ax.errorbar(rounds, means, yerr=stds, label=benchmark, color=color,
                    marker="o", capsize=4, linewidth=2)

    ax.set_xlabel("Repair Round (k)")
    ax.set_ylabel("Mean Mypy Error Count")
    ax.set_title("Mypy Error Trajectory Across Repair Rounds")
    ax.legend()
    ax.set_xticks(list(range(1, 6)))
    fig.tight_layout()
    fig.savefig(figures_dir / "error_trajectory.png", dpi=150)
    plt.close(fig)


def plot_gate_bar(
    summary: dict,
    figures_dir: pathlib.Path = FIGURES_DIR,
) -> None:
    """Bar chart: mean error count per round for each benchmark."""
    figures_dir = pathlib.Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    rounds = list(range(1, 6))
    x = np.arange(len(rounds))
    width = 0.35

    for i, (benchmark, stats) in enumerate(summary.items()):
        means = [stats["mean_errors_by_round"].get(k, {}).get("mean", 0) for k in rounds]
        color = BENCHMARK_COLORS.get(benchmark, "#666666")
        offset = (i - len(summary) / 2 + 0.5) * width
        ax.bar(x + offset, means, width, label=benchmark, color=color, alpha=0.8)

    ax.set_xlabel("Repair Round (k)")
    ax.set_ylabel("Mean Mypy Error Count")
    ax.set_title("Mean Mypy Errors per Round by Benchmark")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Round {k}" for k in rounds])
    ax.legend()
    fig.tight_layout()
    fig.savefig(figures_dir / "gate_metrics.png", dpi=150)
    plt.close(fig)


def plot_per_problem_heatmap(
    records: list,
    benchmark: str,
    figures_dir: pathlib.Path = FIGURES_DIR,
) -> None:
    """Heatmap: problems × rounds of mypy error count."""
    figures_dir = pathlib.Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    bench_short = benchmark.replace("+", "")
    bench_records = [r for r in records if r["benchmark"] == bench_short]
    task_ids = sorted(set(r["task_id"] for r in bench_records))
    rounds = list(range(1, 6))

    data = np.zeros((len(task_ids), len(rounds)))
    for r in bench_records:
        if r["task_id"] in task_ids and r["round"] in rounds:
            row = task_ids.index(r["task_id"])
            col = r["round"] - 1
            data[row, col] = r["mypy_error_count"]

    fig, ax = plt.subplots(figsize=(14, max(8, len(task_ids) * 0.2)))
    im = ax.imshow(data, aspect="auto", cmap="YlOrRd")
    ax.set_xticks(range(len(rounds)))
    ax.set_xticklabels([f"Round {k}" for k in rounds])
    ax.set_yticks([])
    ax.set_ylabel(f"Problems ({len(task_ids)})")
    ax.set_title(f"Mypy Error Count per Problem × Round ({benchmark})")
    fig.colorbar(im, ax=ax, label="Mypy Error Count")
    fig.tight_layout()
    fig.savefig(figures_dir / f"heatmap_{bench_short}.png", dpi=150)
    plt.close(fig)


def plot_error_distribution(
    records: list,
    figures_dir: pathlib.Path = FIGURES_DIR,
) -> None:
    """Box plots: distribution of per-problem mypy error counts per round."""
    figures_dir = pathlib.Path(figures_dir)
    figures_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    rounds = list(range(1, 6))
    data_by_round = []
    for k in rounds:
        errors = [r["mypy_error_count"] for r in records if r["round"] == k]
        data_by_round.append(errors)

    ax.boxplot(data_by_round, labels=[f"Round {k}" for k in rounds])
    ax.set_xlabel("Repair Round")
    ax.set_ylabel("Mypy Error Count")
    ax.set_title("Distribution of Mypy Error Counts per Repair Round")
    fig.tight_layout()
    fig.savefig(figures_dir / "error_distribution.png", dpi=150)
    plt.close(fig)


def generate_all_figures(
    records: list,
    summary: dict,
    figures_dir: pathlib.Path = FIGURES_DIR,
) -> None:
    """Generate all 4 H-M1 figures."""
    from analysis import compute_mean_errors_per_round
    mean_errors = {}
    for benchmark in summary:
        mean_errors[benchmark] = compute_mean_errors_per_round(records, benchmark)

    plot_error_trajectory(mean_errors, figures_dir)
    plot_gate_bar(summary, figures_dir)
    for benchmark in summary:
        plot_per_problem_heatmap(records, benchmark, figures_dir)
    plot_error_distribution(records, figures_dir)
