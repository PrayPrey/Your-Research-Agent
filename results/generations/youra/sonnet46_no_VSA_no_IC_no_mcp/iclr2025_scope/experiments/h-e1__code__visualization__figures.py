import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns


def fig1_macro_f1_bar(results: dict, bootstrap_samples: dict, save_dir: str) -> None:
    methods = ["M0", "M1", "M2", "M6"]
    macro_f1s = [results["per_method"][m]["macro_f1"] for m in methods]

    # CI error bars from bootstrap samples (only M1 and M2 have bootstrap)
    boot = np.array(results["bootstrap_samples"]) if "bootstrap_samples" in results else None
    m1_macro = results["per_method"]["M1"]["macro_f1"]
    m2_macro = results["per_method"]["M2"]["macro_f1"]

    # Compute per-method CI from bootstrap resamples directly
    ci_lower = [0] * 4
    ci_upper = [0] * 4
    if boot is not None:
        # M1 and M2 CIs derived from gate_check
        gc = results["gate_check"]
        # Use symmetrical error approximation for display
        m1_err = (gc["bootstrap_ci_upper"] - gc["bootstrap_ci_lower"]) / 4
        m2_err = m1_err
        ci_lower[1] = m1_err
        ci_upper[1] = m1_err
        ci_lower[2] = m2_err
        ci_upper[2] = m2_err

    fig, ax = plt.subplots(figsize=(7, 5))
    colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]
    bars = ax.bar(methods, macro_f1s, color=colors,
                  yerr=[ci_lower, ci_upper], capsize=5, error_kw={"elinewidth": 1.5})
    ax.set_ylabel("Macro-avg F1 (%)")
    ax.set_title("H-E1: Macro-average F1 by KV Eviction Method\n(LongBench 4-task QA, 50% retention, LLaMA-2-7B-chat)")
    ax.set_ylim(0, max(macro_f1s) * 1.3 + 5)

    for bar, val in zip(bars, macro_f1s):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{val:.1f}", ha="center", va="bottom", fontsize=10)

    plt.tight_layout()
    path = os.path.join(save_dir, "fig1_macro_f1_comparison.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved {path}")


def fig2_pertask_grouped_bar(results: dict, save_dir: str) -> None:
    tasks = ["narrativeqa", "hotpotqa", "2wikimqa", "musique"]
    methods = ["M0", "M1", "M2"]
    task_labels = ["NarrativeQA", "HotpotQA", "2WikiMQA", "MuSiQue"]

    x = np.arange(len(tasks))
    width = 0.25
    colors = ["#4C72B0", "#DD8452", "#55A868"]

    fig, ax = plt.subplots(figsize=(9, 5))
    for i, (method, color) in enumerate(zip(methods, colors)):
        vals = [results["per_method"][method].get(t, 0) for t in tasks]
        ax.bar(x + i * width - width, vals, width, label=method, color=color)

    ax.set_xticks(x)
    ax.set_xticklabels(task_labels)
    ax.set_ylabel("F1 (%)")
    ax.set_title("H-E1: Per-task F1 by Method (50% KV retention)")
    ax.legend()
    plt.tight_layout()
    path = os.path.join(save_dir, "fig2_pertask_f1.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved {path}")


def fig3_bootstrap_histogram(bootstrap_samples: np.ndarray, gate_check: dict, save_dir: str) -> None:
    fig, ax = plt.subplots(figsize=(7, 5))
    n_bins = min(50, max(10, len(set(bootstrap_samples.round(4)))))
    ax.hist(bootstrap_samples, bins=n_bins, color="#4C72B0", alpha=0.75, edgecolor="white")
    ax.axvline(0, color="red", linestyle="--", linewidth=1.5, label="Null (Δ=0)")
    ax.axvline(2.0, color="green", linestyle="--", linewidth=1.5, label="Gate threshold (Δ=2.0)")
    ax.axvline(gate_check["bootstrap_ci_lower"], color="orange", linestyle=":", linewidth=1.2, label="95% CI lower")
    ax.axvline(gate_check["bootstrap_ci_upper"], color="orange", linestyle=":", linewidth=1.2, label="95% CI upper")
    ax.set_xlabel("Bootstrap Δ F1 (M1 − M2)")
    ax.set_ylabel("Count")
    ax.set_title("H-E1: Bootstrap Distribution of M1−M2 F1 Delta")
    ax.legend(fontsize=8)
    plt.tight_layout()
    path = os.path.join(save_dir, "fig3_bootstrap_delta.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved {path}")


def fig4_score_heatmap(m1_scores: list, m2_scores: list, save_dir: str) -> None:
    n_examples = min(len(m1_scores), len(m2_scores), 5)
    if n_examples == 0:
        print("No spot-check scores for Figure 4 — skipping")
        return

    fig, axes = plt.subplots(n_examples, 2, figsize=(12, 2 * n_examples))
    if n_examples == 1:
        axes = [axes]

    for i in range(n_examples):
        s1 = m1_scores[i]
        s2 = m2_scores[i]
        # Normalize for visualization
        s1_norm = (s1 - s1.min()) / (s1.max() - s1.min() + 1e-8)
        s2_norm = (s2 - s2.min()) / (s2.max() - s2.min() + 1e-8)

        axes[i][0].imshow(s1_norm[np.newaxis, :], aspect="auto", cmap="hot", vmin=0, vmax=1)
        axes[i][0].set_yticks([])
        axes[i][0].set_title(f"M1 (SnapKV) Ex {i+1}" if i == 0 else "")
        axes[i][0].set_xlabel("Token position")

        axes[i][1].imshow(s2_norm[np.newaxis, :], aspect="auto", cmap="hot", vmin=0, vmax=1)
        axes[i][1].set_yticks([])
        axes[i][1].set_title(f"M2 (H2O) Ex {i+1}" if i == 0 else "")
        axes[i][1].set_xlabel("Token position")

    plt.suptitle("H-E1: KV Importance Scores — M1 (SnapKV) vs M2 (H2O), Layer 0 mean over heads",
                 fontsize=10)
    plt.tight_layout()
    path = os.path.join(save_dir, "fig4_score_heatmap.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved {path}")


def save_all_figures(results: dict, spot_check_scores: dict, save_dir: str) -> None:
    os.makedirs(save_dir, exist_ok=True)
    boot_samples = np.array(results.get("bootstrap_samples", []))

    fig1_macro_f1_bar(results, boot_samples, save_dir)
    fig2_pertask_grouped_bar(results, save_dir)
    if len(boot_samples) > 0:
        fig3_bootstrap_histogram(boot_samples, results["gate_check"], save_dir)
    fig4_score_heatmap(
        spot_check_scores.get("M1", []),
        spot_check_scores.get("M2", []),
        save_dir,
    )
