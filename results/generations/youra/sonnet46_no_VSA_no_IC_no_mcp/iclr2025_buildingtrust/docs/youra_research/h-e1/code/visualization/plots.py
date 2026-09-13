import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def fig1_ece_comparison(df: pd.DataFrame, out_path: str) -> None:
    tasks = df["task"].unique()
    models = df["model"].unique()
    fig, axes = plt.subplots(1, len(tasks), figsize=(5 * len(tasks), 4), squeeze=False)
    for col, task in enumerate(tasks):
        ax = axes[0][col]
        task_df = df[df["task"] == task]
        x = np.arange(len(models))
        width = 0.35
        clean_eces = [task_df[(task_df["model"] == m) & (task_df["split"] == "clean")]["ece_15"].values for m in models]
        adv_eces = [task_df[(task_df["model"] == m) & (task_df["split"].isin(["adversarial", "anli_r1", "anli_r2", "anli_r3"]))]["ece_15"].values for m in models]
        clean_vals = [v[0] if len(v) > 0 and v[0] is not None else 0 for v in clean_eces]
        adv_vals = [v[0] if len(v) > 0 and v[0] is not None else 0 for v in adv_eces]
        ax.bar(x - width/2, clean_vals, width, label="clean", color="steelblue")
        ax.bar(x + width/2, adv_vals, width, label="adversarial", color="tomato")
        ax.set_title(f"Task: {task}")
        ax.set_xticks(x)
        ax.set_xticklabels([m.split("/")[-1] for m in models], rotation=15, ha="right", fontsize=7)
        ax.set_ylabel("ECE (15 bins)")
        ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=100)
    plt.close()


def _load_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(l) for l in f]


def fig2_reliability_diagrams(example_jsonl_paths: list, out_path: str) -> None:
    n = len(example_jsonl_paths)
    cols = min(4, n)
    rows = max(1, (n + cols - 1) // cols)
    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 4 * rows), squeeze=False)
    for idx, path in enumerate(example_jsonl_paths):
        r, c = divmod(idx, cols)
        ax = axes[r][c]
        records = _load_jsonl(path)
        if not records:
            ax.set_visible(False)
            continue
        confs = np.array([x["confidence"] for x in records])
        correct = np.array([x["correct"] for x in records])
        bins = np.linspace(0, 1, 11)
        bin_acc, bin_conf = [], []
        for b in range(10):
            mask = (confs > bins[b]) & (confs <= bins[b + 1])
            if mask.sum() > 0:
                bin_acc.append(correct[mask].mean())
                bin_conf.append(confs[mask].mean())
        if bin_acc:
            ax.plot([0, 1], [0, 1], "k--", alpha=0.5)
            ax.scatter(bin_conf, bin_acc, s=30)
        label = os.path.basename(path).replace("_examples.jsonl", "")
        ax.set_title(label, fontsize=7)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    for idx in range(n, rows * cols):
        r, c = divmod(idx, cols)
        axes[r][c].set_visible(False)
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=100)
    plt.close()


def fig3_coverage_heatmap(df: pd.DataFrame, out_path: str) -> None:
    pivot = df.pivot_table(index="model", columns=["task", "split"], values="n_examples", aggfunc="first")
    fig, ax = plt.subplots(figsize=(max(6, len(pivot.columns)), max(3, len(pivot))))
    im = ax.imshow(pivot.fillna(0).values, aspect="auto", cmap="YlOrRd")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([f"{t}/{s}" for t, s in pivot.columns], rotation=45, ha="right", fontsize=7)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([m.split("/")[-1] for m in pivot.index], fontsize=8)
    plt.colorbar(im, ax=ax, label="n_examples")
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=100)
    plt.close()


def fig4_confidence_boxplots(example_jsonl_paths: list, out_path: str) -> None:
    labels, data = [], []
    for path in example_jsonl_paths:
        records = _load_jsonl(path)
        if records:
            labels.append(os.path.basename(path).replace("_examples.jsonl", "")[-20:])
            data.append([x["confidence"] for x in records])
    if not data:
        return
    fig, ax = plt.subplots(figsize=(max(6, len(data)), 4))
    ax.boxplot(data, labels=labels)
    plt.xticks(rotation=45, ha="right", fontsize=7)
    plt.ylabel("Max-softmax confidence")
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=100)
    plt.close()


def fig5_ece_sensitivity(df: pd.DataFrame, out_path: str) -> None:
    valid = df.dropna(subset=["ece_15", "ece_10"])
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(valid["ece_15"], valid["ece_10"], alpha=0.7)
    lim = max(valid["ece_15"].max(), valid["ece_10"].max()) * 1.1
    ax.plot([0, lim], [0, lim], "k--", alpha=0.5)
    ax.set_xlabel("ECE (15 bins)")
    ax.set_ylabel("ECE (10 bins)")
    ax.set_title("ECE Sensitivity: 10 vs 15 bins")
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=100)
    plt.close()
