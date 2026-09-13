import os
import json
import evaluate as hf_evaluate
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from config import ExperimentConfig

TASK_METRIC = {
    "sst2": "accuracy",
    "mnli": "accuracy",
    "qnli": "accuracy",
    "qqp": "f1",
}


def compute_glue_metric(task: str, preds, labels) -> dict:
    metric = hf_evaluate.load("glue", task)
    return metric.compute(predictions=preds, references=labels)


def get_scalar(task: str, metric_dict: dict) -> float:
    key = TASK_METRIC[task]
    return metric_dict.get(key, 0.0)


def compute_glue_avg(results: dict) -> float:
    return sum(results.values()) / len(results)


def plot_results(results: dict, cfg: ExperimentConfig) -> None:
    os.makedirs(cfg.figures_dir, exist_ok=True)
    tasks = list(results.get("zero_shot", {}).keys())
    zs_vals = [results["zero_shot"].get(t, 0.0) for t in tasks]
    lora_vals = [results["lora"].get(t, 0.0) for t in tasks]

    x = range(len(tasks))
    fig, ax = plt.subplots(figsize=(8, 5))
    w = 0.35
    ax.bar([i - w/2 for i in x], zs_vals, w, label="Zero-shot")
    ax.bar([i + w/2 for i in x], lora_vals, w, label="LoRA")
    ax.axhline(0.70, color="red", linestyle="--", label="Gate (0.70)")
    ax.set_xticks(list(x))
    ax.set_xticklabels(tasks)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Score")
    ax.set_title("Zero-shot vs LoRA on GLUE")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(cfg.figures_dir, "comparison.png"), dpi=120)
    plt.close(fig)

    if "loss_history" in results:
        fig, axes = plt.subplots(2, 2, figsize=(10, 8))
        for ax, task in zip(axes.flat, tasks):
            hist = results["loss_history"].get(task, [])
            ax.plot(hist)
            ax.set_title(f"{task} loss")
            ax.set_xlabel("step")
            ax.set_ylabel("loss")
        fig.tight_layout()
        fig.savefig(os.path.join(cfg.figures_dir, "loss_curves.png"), dpi=120)
        plt.close(fig)
