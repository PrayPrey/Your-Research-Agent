"""Generate H-M2 figures."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from config import DELTA_ACC_GATE, CONF_WRONG_GATE, ANLI_TASKS
from cell_analyzer import DeltaStats
from gate_evaluator import GateResult


def _cell_label(model: str, task: str) -> str:
    short = {"Llama-2-7b-hf": "L2-7B", "advglue_mnli": "MNLI", "advglue_qqp": "QQP",
             "anli_r1": "R1", "anli_r2": "R2", "anli_r3": "R3"}
    m = short.get(model, model[:6])
    t = short.get(task, task[:6])
    return f"{m}\n{t}"


def plot_gate_metrics(cell_results: dict, gate_result: GateResult, out_dir: Path) -> None:
    items = list(cell_results.items())
    labels = [_cell_label(m, t) for (m, t), _ in items]
    delta_accs = [ds.delta_acc for _, ds in items]
    conf_wrongs = [ds.conf_wrong_adv if ds.conf_wrong_adv is not None else 0.0 for _, ds in items]
    colors = ["green" if ds.cell_pass else "red" for _, ds in items]

    x = np.arange(len(items))
    width = 0.35

    fig, ax = plt.subplots(figsize=(max(8, len(items) * 1.5), 5))
    bar_colors1 = ["#88cc88" if c == "green" else "#cc8888" for c in colors]
    bars1 = ax.bar(x - width/2, delta_accs, width, label="ΔAcc", color=bar_colors1)
    bars2 = ax.bar(x + width/2, conf_wrongs, width, label="conf_wrong_adv",
                   color=["steelblue" if cw >= CONF_WRONG_GATE else "orange" for cw in conf_wrongs])

    ax.axhline(DELTA_ACC_GATE,  color="red",   linestyle="--", linewidth=1, label=f"ΔAcc gate ({DELTA_ACC_GATE})")
    ax.axhline(CONF_WRONG_GATE, color="blue",  linestyle="--", linewidth=1, label=f"conf_wrong gate ({CONF_WRONG_GATE})")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("Metric Value")
    ax.set_title(f"H-M2 Gate Metrics per Cell\n(Gate: {gate_result.overall_result}, "
                 f"pass_rate={gate_result.gate_pass_rate:.2f})")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "gate_metrics_per_cell.png"
    plt.savefig(path, dpi=120)
    plt.close()
    print(f"Figure saved: {path}")


def plot_accuracy_scatter(cell_results: dict, out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 5))
    for (model, task), ds in cell_results.items():
        cwa = ds.conf_wrong_adv or 0.3
        ax.scatter(ds.accuracy_clean, ds.accuracy_adv,
                   s=cwa * 300, alpha=0.7, label=task)
        ax.annotate(task[:8], (ds.accuracy_clean, ds.accuracy_adv), fontsize=7)

    lim = [0, 1]
    ax.plot(lim, lim, "k--", linewidth=0.8, label="No drop")
    ax.set_xlabel("Accuracy (clean)")
    ax.set_ylabel("Accuracy (adversarial)")
    ax.set_title("H-M2: Clean vs Adversarial Accuracy\n(bubble size ~ conf_wrong_adv)")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    path = out_dir / "accuracy_scatter.png"
    plt.savefig(path, dpi=120)
    plt.close()
    print(f"Figure saved: {path}")


def plot_confidence_distributions(cell_results: dict, out_dir: Path) -> None:
    """Per-task conf_wrong_adv bar chart (histogram approximation with single values)."""
    tasks  = [t for (m, t), _ in cell_results.items()]
    values = [ds.conf_wrong_adv or 0.0 for _, ds in cell_results.items()]
    colors = ["green" if v >= CONF_WRONG_GATE else "orange" for v in values]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(tasks, values, color=colors)
    ax.axhline(CONF_WRONG_GATE, color="red", linestyle="--", label=f"Gate ({CONF_WRONG_GATE})")
    ax.set_ylabel("Mean conf on wrong adv predictions")
    ax.set_title("H-M2: Confidence on Wrong Adversarial Predictions")
    ax.legend()
    ax.set_ylim(0, 1)
    plt.xticks(rotation=20, fontsize=8)
    plt.tight_layout()
    path = out_dir / "confidence_distributions.png"
    plt.savefig(path, dpi=120)
    plt.close()
    print(f"Figure saved: {path}")


def plot_delta_acc_heatmap(cell_results: dict, out_dir: Path) -> None:
    from config import TASKS, MODEL
    tasks = TASKS
    data  = np.array([[cell_results.get((MODEL, t), None) and
                       cell_results[(MODEL, t)].delta_acc for t in tasks]])
    annot = [[
        ("PASS" if cell_results.get((MODEL, t)) and cell_results[(MODEL, t)].cell_pass else "FAIL")
        + f"\n{data[0][i]:.3f}"
        for i, t in enumerate(tasks)
    ]]

    fig, ax = plt.subplots(figsize=(max(8, len(tasks) * 1.5), 3))
    im = ax.imshow(data, cmap="RdYlGn", vmin=-0.5, vmax=0.0, aspect="auto")
    ax.set_xticks(range(len(tasks))); ax.set_xticklabels(tasks, rotation=20, fontsize=8)
    ax.set_yticks([0]); ax.set_yticklabels([MODEL])
    for i, t in enumerate(tasks):
        ax.text(i, 0, annot[0][i], ha="center", va="center", fontsize=7)
    plt.colorbar(im, ax=ax, label="ΔAcc")
    ax.set_title("H-M2: ΔAcc Heatmap (model × task)")
    plt.tight_layout()
    path = out_dir / "delta_acc_heatmap.png"
    plt.savefig(path, dpi=120)
    plt.close()
    print(f"Figure saved: {path}")


def plot_anli_gradient(anli_stats: dict, out_dir: Path) -> None:
    per_round = anli_stats.get("per_round", {})
    rounds  = [r for r in ["anli_r1", "anli_r2", "anli_r3"] if r in per_round]
    values  = [per_round[r] for r in rounds]
    colors  = ["steelblue"] * len(rounds)

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(rounds, values, color=colors)
    ax.set_ylabel("Mean ΔAcc")
    ax.set_title("H-M2: ANLI Difficulty Gradient\n(harder round → larger accuracy drop)")
    ax.axhline(0, color="k", linewidth=0.5)
    plt.tight_layout()
    path = out_dir / "anli_gradient.png"
    plt.savefig(path, dpi=120)
    plt.close()
    print(f"Figure saved: {path}")


def plot_base_vs_chat(cell_results: dict, out_dir: Path) -> None:
    """With single model, show per-task ΔAcc bar chart instead."""
    tasks  = [t for (m, t) in cell_results]
    deltas = [cell_results[(m, t)].delta_acc for m, t in cell_results]
    colors = ["green" if v <= DELTA_ACC_GATE else "orange" for v in deltas]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(tasks, deltas, color=colors)
    ax.axhline(DELTA_ACC_GATE, color="red", linestyle="--", label=f"Gate ({DELTA_ACC_GATE})")
    ax.set_ylabel("ΔAcc (adv − clean)")
    ax.set_title("H-M2: Accuracy Drop per Task (Llama-2-7b-hf)\n"
                 "(multi-model comparison deferred to H-E1 extension)")
    ax.legend()
    plt.xticks(rotation=20, fontsize=8)
    plt.tight_layout()
    path = out_dir / "base_vs_chat_comparison.png"
    plt.savefig(path, dpi=120)
    plt.close()
    print(f"Figure saved: {path}")
