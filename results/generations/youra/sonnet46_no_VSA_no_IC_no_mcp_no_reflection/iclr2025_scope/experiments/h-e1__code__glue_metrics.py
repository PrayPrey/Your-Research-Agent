import os
import evaluate as hf_evaluate
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from config import ExperimentConfig

TASK_METRIC = {
    "sst2": "accuracy",
    "mnli": "accuracy",
    "qnli": "accuracy",
    "qqp":  "f1",
}


def compute_glue_metric(task: str, preds, labels) -> dict:
    metric = hf_evaluate.load("glue", task)
    return metric.compute(predictions=preds, references=labels)


def get_scalar(task: str, metrics: dict) -> float:
    key = TASK_METRIC[task]
    return metrics.get(key, metrics.get(list(metrics.keys())[0], 0.0))


def compute_glue_avg(results: dict) -> float:
    values = [get_scalar(t, results[t]) for t in ("sst2", "mnli", "qnli", "qqp") if t in results]
    return sum(values) / len(values) if values else 0.0


def plot_results(results: dict, cfg: ExperimentConfig, loss_history: dict = None) -> None:
    os.makedirs(cfg.figures_dir, exist_ok=True)
    tasks = list(results.get("zero_shot", {}).keys())
    if not tasks:
        return

    zero_vals = [get_scalar(t, results["zero_shot"].get(t, {})) for t in tasks]
    lora_vals  = [get_scalar(t, results["lora"].get(t, {}))      for t in tasks]

    x = range(len(tasks))
    fig, ax = plt.subplots(figsize=(8, 5))
    w = 0.35
    bars_zero = ax.bar([i - w/2 for i in x], zero_vals, w, label="Zero-shot", color="#5B9BD5")
    bars_lora  = ax.bar([i + w/2 for i in x], lora_vals,  w, label="LoRA (r=8)", color="#ED7D31")
    ax.axhline(0.70, color="red", linestyle="--", linewidth=1.5, label="Gate (70%)")
    ax.set_xticks(list(x))
    ax.set_xticklabels([t.upper() for t in tasks])
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Metric Score")
    ax.set_title("Mamba-130m: Zero-shot vs LoRA on GLUE Tasks")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(cfg.figures_dir, "comparison.png"), dpi=150)
    plt.close(fig)

    if loss_history:
        n = len(loss_history)
        fig, axes = plt.subplots(1, n, figsize=(5 * n, 4))
        if n == 1:
            axes = [axes]
        for ax, (task, losses) in zip(axes, loss_history.items()):
            ax.plot(losses)
            ax.set_title(f"{task.upper()} training loss")
            ax.set_xlabel("step")
            ax.set_ylabel("loss")
        fig.tight_layout()
        fig.savefig(os.path.join(cfg.figures_dir, "loss_curves.png"), dpi=150)
        plt.close(fig)
