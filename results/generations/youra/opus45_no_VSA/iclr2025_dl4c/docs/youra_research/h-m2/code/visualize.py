"""Visualization for H-M2 DiD experiment."""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def plot_2x2_bar(cell_means: dict, out_path: Path) -> None:
    """2x2 grouped bar: Model x Condition."""
    models = ["RL", "CE"]
    conditions = ["actual", "control"]
    x = np.arange(len(models))
    width = 0.35

    actual_vals = [cell_means[f"{m}_actual"] for m in models]
    control_vals = [cell_means[f"{m}_control"] for m in models]

    fig, ax = plt.subplots(figsize=(8, 6))
    bars1 = ax.bar(x - width/2, actual_vals, width, label="Actual", color="#2ecc71")
    bars2 = ax.bar(x + width/2, control_vals, width, label="Control", color="#e74c3c")

    ax.set_ylabel("pass@1 (refined)")
    ax.set_xlabel("Training Method")
    ax.set_title("DiD Semantic Sensitivity: Model × Feedback Condition")
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend()
    ax.set_ylim(0, 1)

    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.3f}', xy=(bar.get_x() + bar.get_width()/2, height),
                       xytext=(0, 3), textcoords="offset points", ha='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_did_ci(did_result: dict, out_path: Path) -> None:
    """Single bar with CI error bars."""
    fig, ax = plt.subplots(figsize=(6, 5))

    did = did_result["did_contrast"]
    ci_lower = did_result["ci_lower"]
    ci_upper = did_result["ci_upper"]
    error = [[did - ci_lower], [ci_upper - did]]

    color = "#27ae60" if did > 0 else "#c0392b"
    ax.bar([0], [did], yerr=error, capsize=10, color=color, alpha=0.8)
    ax.axhline(y=0, color='black', linestyle='--', linewidth=1)

    ax.set_ylabel("DiD Contrast")
    ax.set_title(f"DiD = {did:.4f}, 95% CI [{ci_lower:.4f}, {ci_upper:.4f}]")
    ax.set_xticks([0])
    ax.set_xticklabels(["(RL_A - RL_C) - (CE_A - CE_C)"])

    sig_text = "p < 0.05" if did_result["significant"] else f"p = {did_result['p_value_one_sided']:.3f}"
    ax.text(0, did + (ci_upper - did) * 1.5, sig_text, ha='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_error_type_did(error_type_did: dict[str, float], out_path: Path) -> None:
    """Bar chart of DiD per error type."""
    if not error_type_did:
        return

    types = list(error_type_did.keys())
    vals = [error_type_did[t] for t in types]

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#27ae60" if v > 0 else "#c0392b" for v in vals]
    ax.bar(types, vals, color=colors, alpha=0.8)
    ax.axhline(y=0, color='black', linestyle='--', linewidth=1)
    ax.set_ylabel("DiD Contrast")
    ax.set_xlabel("Error Type")
    ax.set_title("DiD by Error Category")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_effect_hist(effects: list[float], out_path: Path) -> None:
    """Histogram of per-problem effect sizes."""
    if not effects:
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(effects, bins=20, color="#3498db", alpha=0.8, edgecolor="black")
    ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Zero effect')
    ax.axvline(x=np.mean(effects), color='green', linestyle='-', linewidth=2, label=f'Mean={np.mean(effects):.3f}')
    ax.set_xlabel("Per-problem DiD effect")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of Per-Problem Semantic Sensitivity Effects")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
