"""H-M3 figures (6 plots)."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

H1_CODE_DIR = Path(__file__).parent.parent.parent / "h-m1" / "code"


def _get_h1_save():
    import importlib.util
    spec = importlib.util.spec_from_file_location("h1_viz", H1_CODE_DIR / "visualization.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod._save


_save = _get_h1_save()


def plot_gate_metrics(stats, out_path: str = "figures/gate_metrics_adaptive_contribution.png") -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["Mean Adaptive\nContribution"], [stats.mean_adaptive_gap],
           yerr=[[stats.mean_adaptive_gap - stats.ci_lower], [stats.ci_upper - stats.mean_adaptive_gap]],
           capsize=8, color="steelblue", alpha=0.8)
    ax.axhline(0, color="red", linestyle="--", linewidth=1.5, label="Threshold = 0")
    ax.set_ylabel("Exp_B - Exp_A failure rate")
    ax.set_title(f"Gate Metric: Mean Adaptive Contribution\n(p_holm={stats.wilcoxon_p_holm:.2e})")
    ax.legend()
    fig.tight_layout()
    _save(fig, out_path)


def plot_scatter_exp_a_vs_exp_b(paired_records: list[dict], out_path: str = "figures/scatter_exp_a_vs_exp_b.png") -> None:
    a = [r["static_failure_rate"] for r in paired_records]
    b = [r["adaptive_failure_rate"] for r in paired_records]
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(a, b, alpha=0.15, s=5, color="steelblue")
    lim = max(max(a, default=1), max(b, default=1)) + 0.05
    ax.plot([0, lim], [0, lim], "r--", linewidth=1.5, label="y=x (no difference)")
    ax.set_xlabel("Exp A static failure rate")
    ax.set_ylabel("Exp B adaptive failure rate")
    ax.set_title("Adaptive vs Static Oracle per Triple")
    ax.legend()
    fig.tight_layout()
    _save(fig, out_path)


def plot_adaptive_gap_distribution(paired_records: list[dict], out_path: str = "figures/adaptive_gap_distribution.png") -> None:
    gaps = [r["adaptive_gap"] for r in paired_records]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(gaps, bins=60, color="steelblue", alpha=0.7, edgecolor="none")
    ax.axvline(0, color="red", linestyle="--", linewidth=1.5, label="0 (no contribution)")
    mean_gap = np.mean(gaps) if gaps else 0
    ax.axvline(mean_gap, color="orange", linestyle="-", linewidth=1.5, label=f"Mean={mean_gap:.3f}")
    ax.set_xlabel("Adaptive gap (Exp_B - Exp_A)")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of Adaptive Contribution per Triple")
    ax.legend()
    fig.tight_layout()
    _save(fig, out_path)


def plot_filter_rate_distribution(yield_stats: dict, out_path: str = "figures/filter_rate_distribution.png") -> None:
    rates = [s["mean_filter_rate"] for s in yield_stats.values()]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(rates, bins=40, color="teal", alpha=0.7, edgecolor="none")
    ax.axvline(0.95, color="red", linestyle="--", linewidth=1.5, label="High-filter threshold (0.95)")
    ax.set_xlabel("Mean filter rate per task")
    ax.set_ylabel("Task count")
    ax.set_title("Per-Task Filter Rate Distribution")
    ax.legend()
    fig.tight_layout()
    _save(fig, out_path)


def plot_model_stratified(stats, out_path: str = "figures/model_stratified_contribution.png") -> None:
    models = list(stats.by_model.keys())
    gaps = [stats.by_model[m]["mean_gap"] for m in models]
    short = [m.split("/")[-1][:20] for m in models]
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = ["steelblue" if g > 0 else "salmon" for g in gaps]
    ax.bar(range(len(models)), gaps, color=colors, alpha=0.8)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(range(len(models)))
    ax.set_xticklabels(short, rotation=30, ha="right")
    ax.set_ylabel("Mean adaptive gap")
    ax.set_title("Model-Stratified Adaptive Contribution")
    fig.tight_layout()
    _save(fig, out_path)


def plot_task_type_breakdown(stats, out_path: str = "figures/task_type_breakdown.png") -> None:
    types = list(stats.by_task_type.keys())
    gaps = [stats.by_task_type[tt]["mean_gap"] for tt in types]
    fig, ax = plt.subplots(figsize=(5, 4))
    colors = ["steelblue" if g > 0 else "salmon" for g in gaps]
    ax.bar(types, gaps, color=colors, alpha=0.8)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Mean adaptive gap")
    ax.set_title("Task-Type Adaptive Contribution")
    fig.tight_layout()
    _save(fig, out_path)
