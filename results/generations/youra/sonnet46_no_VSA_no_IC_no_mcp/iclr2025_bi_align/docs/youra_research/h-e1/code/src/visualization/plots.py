import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd


def plot_dual_axis(
    df: pd.DataFrame,
    dataset_name: str,
    out_dir: str,
    dpi: int = 150,
) -> str:
    fig, ax1 = plt.subplots(figsize=(8, 5))

    color_rm = "steelblue"
    ax1.set_xlabel("KL Divergence (nats)")
    ax1.set_ylabel("RM Score (proxy)", color=color_rm)
    ax1.plot(df["kl_budget"], df["rm_score"],
             marker="o", color=color_rm, label="RM Score")
    ax1.tick_params(axis="y", labelcolor=color_rm)

    ax2 = ax1.twinx()
    color_gold = "crimson"
    ax2.set_ylabel("Gold Preference Rate", color=color_gold)
    ax2.plot(df["kl_budget"], df["gold_preference"],
             marker="s", linestyle="--", color=color_gold, label="Gold Preference")
    ax2.tick_params(axis="y", labelcolor=color_gold)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    ax1.set_title(f"H-E1: Dual Signal Co-existence — {dataset_name}")
    fig.tight_layout()

    out_path = Path(out_dir) / f"dual_axis_{dataset_name.lower()}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return str(out_path.resolve())


def plot_comparison(
    results: list,
    dfs: list,
    dataset_names: list,
    out_dir: str,
    dpi: int = 150,
) -> str:
    n = len(dfs)
    fig, axes = plt.subplots(1, n, figsize=(7 * n, 5), sharey=False)
    if n == 1:
        axes = [axes]

    for ax, df, res, name in zip(axes, dfs, results, dataset_names):
        ax.plot(df["kl_budget"], df["rm_score"],
                marker="o", color="steelblue", label="RM Score")
        ax2 = ax.twinx()
        ax2.plot(df["kl_budget"], df["gold_preference"],
                 marker="s", linestyle="--", color="crimson", label="Gold Pref")

        status = "PASS" if res["passed"] else "FAIL"
        color = "green" if res["passed"] else "red"
        ax.set_title(
            f"{name}\n{status} ({res['n_kl_levels']} KL levels)",
            color=color, fontweight="bold",
        )
        ax.set_xlabel("KL Divergence (nats)")
        ax.set_ylabel("RM Score", color="steelblue")
        ax2.set_ylabel("Gold Preference", color="crimson")

    fig.suptitle("H-E1 Gate: Dual Signal Co-existence Verification", fontsize=13)
    fig.tight_layout()

    out_path = Path(out_dir) / "comparison_both_datasets.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return str(out_path.resolve())
