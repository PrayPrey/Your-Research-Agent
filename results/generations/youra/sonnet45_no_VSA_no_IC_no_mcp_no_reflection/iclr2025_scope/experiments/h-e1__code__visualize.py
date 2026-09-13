import matplotlib.pyplot as plt
import numpy as np
import os


def plot_gate_metrics(results: dict, output_dir: str):
    tasks = ["mnli", "qqp", "sst2"]
    accuracies = [results[task]["accuracy"] for task in tasks]
    baselines = [results[task]["baseline"] for task in tasks]

    x = np.arange(len(tasks))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width/2, accuracies, width, label="Zero-shot", color="#2E86AB")
    ax.bar(x + width/2, baselines, width, label="Random baseline", color="#A23B72")

    ax.set_xlabel("Task")
    ax.set_ylabel("Accuracy")
    ax.set_title("Zero-Shot Performance vs Random Baseline")
    ax.set_xticks(x)
    ax.set_xticklabels([t.upper() for t in tasks])
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "gate_metrics.png"), dpi=300)
    plt.close()


def generate_performance_table(results: dict, output_dir: str):
    tasks = ["mnli", "qqp", "sst2"]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis("tight")
    ax.axis("off")

    table_data = [["Task", "Samples", "Accuracy", "Baseline", "Pass"]]
    for task in tasks:
        r = results[task]
        passed = "✓" if r["accuracy"] > r["baseline"] else "✗"
        table_data.append([
            task.upper(),
            str(r["total"]),
            f"{r['accuracy']:.3f}",
            f"{r['baseline']:.3f}",
            passed
        ])

    table = ax.table(cellText=table_data, cellLoc="center", loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    for i in range(len(table_data)):
        for j in range(len(table_data[0])):
            cell = table[(i, j)]
            if i == 0:
                cell.set_facecolor("#2E86AB")
                cell.set_text_props(weight="bold", color="white")
            else:
                cell.set_facecolor("#F0F0F0" if i % 2 == 0 else "white")

    plt.savefig(os.path.join(output_dir, "performance_table.png"), dpi=300, bbox_inches="tight")
    plt.close()
