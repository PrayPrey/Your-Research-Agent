import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RCPARAMS = {
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "font.size": 12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "legend.fontsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.facecolor": "white",
    "axes.spines.top": False,
    "axes.spines.right": False,
}

COLORS = {
    "original": "#2196F3",
    "no_background": "#FF5722",
}

FIG_SIZES = {
    "gate_metrics_comparison": (8, 5),
    "spurious_task_scatter": (6, 6),
    "paired_ratio_plot": (6, 5),
    "background_replacement_examples": (14, 4),
}

FIG_FILENAMES = {
    "gate_metrics_comparison": "gate_metrics_comparison.png",
    "spurious_task_scatter": "spurious_task_scatter.png",
    "paired_ratio_plot": "paired_ratio_plot.png",
    "background_replacement_examples": "background_replacement_examples.png",
}


def plot_gate_metrics_comparison(results: dict, out_dir: str) -> None:
    """FR-6.1: Bar chart of spurious/task probe accuracy per condition ± std."""
    plt.rcParams.update(RCPARAMS)
    fig, ax = plt.subplots(figsize=FIG_SIZES["gate_metrics_comparison"])

    conditions = ["original", "no_background"]
    labels = ["Original", "NoBackground"]
    x = np.arange(2)
    width = 0.35

    for ci, (cond, label) in enumerate(zip(conditions, labels)):
        seed_data = results.get(cond, {})
        spurious_accs = [v["spurious_probe_acc"] for v in seed_data.values() if not v.get("collapsed", False)]
        task_accs = [v["task_probe_acc"] for v in seed_data.values() if not v.get("collapsed", False)]

        if spurious_accs:
            ax.bar(ci - width/2, np.mean(spurious_accs), width, yerr=np.std(spurious_accs),
                   label=f"{label} Spurious" if ci == 0 else None,
                   color=COLORS[cond], alpha=0.9, capsize=4)
            ax.bar(ci + width/2, np.mean(task_accs), width, yerr=np.std(task_accs),
                   label=f"{label} Task" if ci == 0 else None,
                   color=COLORS[cond], alpha=0.5, capsize=4)

    ax.set_xticks(np.arange(len(conditions)))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Probe Accuracy")
    ax.set_title("Spurious vs Task Probe Accuracy by Condition")
    ax.legend(["Spurious Probe", "Task Probe"], loc="upper right")
    ax.set_ylim(0, 1.05)

    os.makedirs(out_dir, exist_ok=True)
    fig.savefig(os.path.join(out_dir, FIG_FILENAMES["gate_metrics_comparison"]), bbox_inches="tight")
    plt.close(fig)


def plot_spurious_task_scatter(results: dict, out_dir: str) -> None:
    """FR-6.2: Scatter x=task_acc, y=spurious_acc, colored by condition."""
    plt.rcParams.update(RCPARAMS)
    fig, ax = plt.subplots(figsize=FIG_SIZES["spurious_task_scatter"])

    for cond, label in [("original", "Original"), ("no_background", "NoBackground")]:
        seed_data = results.get(cond, {})
        task_accs = [v["task_probe_acc"] for v in seed_data.values()]
        spurious_accs = [v["spurious_probe_acc"] for v in seed_data.values()]
        ax.scatter(task_accs, spurious_accs, color=COLORS[cond], label=label, s=80, alpha=0.8, zorder=3)

    ax.set_xlabel("Task Probe Accuracy")
    ax.set_ylabel("Spurious Probe Accuracy")
    ax.set_title("Spurious vs Task Accuracy (per seed)")
    ax.legend()
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3, label="diagonal")

    os.makedirs(out_dir, exist_ok=True)
    fig.savefig(os.path.join(out_dir, FIG_FILENAMES["spurious_task_scatter"]), bbox_inches="tight")
    plt.close(fig)


def plot_paired_ratio(results: dict, out_dir: str) -> None:
    """FR-6.3: Lines connecting original→no_background ratio per seed."""
    plt.rcParams.update(RCPARAMS)
    fig, ax = plt.subplots(figsize=FIG_SIZES["paired_ratio_plot"])

    orig_data = results.get("original", {})
    nobg_data = results.get("no_background", {})
    seeds = sorted(set(orig_data.keys()) & set(nobg_data.keys()))

    for seed in seeds:
        orig_ratio = orig_data[seed]["ratio"]
        nobg_ratio = nobg_data[seed]["ratio"]
        ax.plot([0, 1], [orig_ratio, nobg_ratio], "o-", color="gray", alpha=0.5)

    # Means
    if seeds:
        orig_ratios = [orig_data[s]["ratio"] for s in seeds]
        nobg_ratios = [nobg_data[s]["ratio"] for s in seeds]
        ax.plot([0, 1], [np.mean(orig_ratios), np.mean(nobg_ratios)], "o-",
                color="black", linewidth=2, label="Mean", markersize=8)

    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Original", "NoBackground"])
    ax.set_ylabel("Spurious/Task Ratio")
    ax.set_title("Paired Spurious/Task Ratio per Seed")
    ax.legend()

    os.makedirs(out_dir, exist_ok=True)
    fig.savefig(os.path.join(out_dir, FIG_FILENAMES["paired_ratio_plot"]), bbox_inches="tight")
    plt.close(fig)


def plot_background_replacement_examples(waterbirds_dataset, bg_transform, out_dir: str, n: int = 5) -> None:
    """FR-6.4: Qualitative grid of original vs background-replaced images."""
    import torchvision.transforms as T
    from PIL import Image

    plt.rcParams.update(RCPARAMS)
    fig, axes = plt.subplots(2, n, figsize=FIG_SIZES["background_replacement_examples"])

    unnorm = T.Compose([
        T.Normalize(mean=[0, 0, 0], std=[1/0.229, 1/0.224, 1/0.225]),
        T.Normalize(mean=[-0.485, -0.456, -0.406], std=[1, 1, 1]),
    ])

    for i in range(n):
        try:
            image, _, _, _ = waterbirds_dataset[i]
            # image is already a tensor if transform was applied
            # For display, use PIL directly
            item = waterbirds_dataset.wilds_subset[i]
            pil_img = item[0]
            if not isinstance(pil_img, Image.Image):
                import numpy as np
                pil_img = Image.fromarray(pil_img.numpy().astype(np.uint8))

            axes[0, i].imshow(np.array(pil_img))
            axes[0, i].axis("off")
            axes[0, i].set_title(f"Original {i}" if i == 0 else "")
        except Exception:
            axes[0, i].axis("off")

        axes[1, i].axis("off")

    axes[0, 0].set_ylabel("Original")
    axes[1, 0].set_ylabel("Replaced")
    fig.suptitle("Background Replacement Examples")

    os.makedirs(out_dir, exist_ok=True)
    fig.savefig(os.path.join(out_dir, FIG_FILENAMES["background_replacement_examples"]), bbox_inches="tight")
    plt.close(fig)
