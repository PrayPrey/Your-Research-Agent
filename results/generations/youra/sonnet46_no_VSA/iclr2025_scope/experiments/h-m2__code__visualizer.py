"""Generate 4 required figures for H-M2."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from config import FIGURES_DIR


def _logistic(x, beta0, beta1):
    return 1.0 / (1.0 + np.exp(-(beta0 + beta1 * x)))


def plot_gate_metrics(gate_result: dict, reg_results: dict) -> str:
    """
    FR-5.1: Bar chart of |β_depth| with 95% CI error bars.
    """
    ssm = reg_results["mohawk_ssm"]
    lawcat = reg_results["lawcat"]

    labels = ["MOHAWK-SSM", "LAWCAT"]
    betas = [abs(ssm["beta"]), abs(lawcat["beta"])]
    ci_errs = [
        [abs(ssm["beta"]) - max(0, -ssm["ci_high"]), min(abs(ssm["ci_low"]), abs(ssm["beta"]) + abs(ssm["ci_low"]))],
        [abs(lawcat["beta"]) - max(0, -lawcat["ci_high"]), min(abs(lawcat["ci_low"]), abs(lawcat["beta"]) + abs(lawcat["ci_low"]))],
    ]

    # Simpler error computation: distance from beta to CI bounds
    ssm_err_lo = abs(ssm["beta"]) - ssm["ci_low"] if ssm["beta"] < 0 else ssm["ci_high"] - abs(ssm["beta"])
    ssm_err_hi = ssm["ci_high"] - abs(ssm["beta"]) if ssm["beta"] < 0 else abs(ssm["beta"]) - ssm["ci_low"]
    lawcat_err_lo = abs(lawcat["beta"]) - lawcat["ci_low"] if lawcat["beta"] < 0 else lawcat["ci_high"] - abs(lawcat["beta"])
    lawcat_err_hi = lawcat["ci_high"] - abs(lawcat["beta"]) if lawcat["beta"] < 0 else abs(lawcat["beta"]) - lawcat["ci_low"]

    yerr = [
        [max(0, ssm_err_lo), max(0, lawcat_err_lo)],
        [max(0, ssm_err_hi), max(0, lawcat_err_hi)],
    ]

    fig, ax = plt.subplots(figsize=(7, 5))
    colors = ["#e74c3c", "#3498db"]
    bars = ax.bar(labels, betas, color=colors, alpha=0.8, yerr=yerr, capsize=8, width=0.5)

    # Reference line at 2× LAWCAT
    ref_line = 2.0 * betas[1]
    ax.axhline(ref_line, color="gray", linestyle="--", linewidth=1.5, label=f"2× |β_LAWCAT| = {ref_line:.3f}")

    ax.set_ylabel("|β_depth|", fontsize=13)
    ax.set_title("Depth Coefficient Magnitude by Model\n(|β_depth| with 95% CI)", fontsize=12)
    ax.legend(fontsize=10)

    verdict = gate_result.get("verdict", "?")
    ratio = gate_result.get("ratio", 0)
    ax.text(0.5, 0.95, f"Ratio={ratio:.2f} | Gate: {verdict}",
            transform=ax.transAxes, ha="center", va="top", fontsize=10,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, "gate_metrics.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[Viz] Saved: {path}")
    return path


def plot_depth_accuracy_scatter(
    mohawk_records: list[dict],
    lawcat_records: list[dict],
    reg_results: dict,
) -> str:
    """
    FR-5.2: Scatter of depth_percentile vs correct with logistic fit curves.
    """
    np.random.seed(42)
    fig, ax = plt.subplots(figsize=(9, 5))

    for records, label, color in [
        (mohawk_records, "MOHAWK-SSM", "#e74c3c"),
        (lawcat_records, "LAWCAT", "#3498db"),
    ]:
        depths = np.array([r["depth_percentile"] for r in records])
        corrects = np.array([r["correct"] for r in records])
        jitter = np.random.uniform(-0.04, 0.04, len(corrects))
        ax.scatter(depths, corrects + jitter, alpha=0.3, s=12, color=color, label=f"{label} (n={len(records)})")

    # Logistic fit curves
    x_range = np.linspace(0, 1, 200)
    for model_key, label, color in [
        ("mohawk_ssm", "MOHAWK-SSM fit", "#c0392b"),
        ("lawcat", "LAWCAT fit", "#2980b9"),
    ]:
        r = reg_results[model_key]
        # Approximate intercept as mean(correct) logit
        beta0 = 0.0  # simplified — intercept not critical for shape comparison
        y = _logistic(x_range, beta0, r["beta"])
        ax.plot(x_range, y, color=color, linewidth=2.5, linestyle="--", label=label)

    ax.set_xlabel("Depth Percentile (1=near start, 0=near end)", fontsize=12)
    ax.set_ylabel("Correct (jittered)", fontsize=12)
    ax.set_title("Depth-Accuracy Scatter: MOHAWK-SSM vs LAWCAT", fontsize=12)
    ax.legend(fontsize=9, loc="upper left")
    ax.set_ylim(-0.15, 1.15)

    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, "depth_accuracy_scatter.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[Viz] Saved: {path}")
    return path


def plot_depth_quartile_accuracy(
    mohawk_records: list[dict],
    lawcat_records: list[dict],
) -> str:
    """
    FR-5.3: Accuracy by depth quartile for both models.
    """
    def quartile_acc(records):
        accs = []
        for q_lo, q_hi in [(0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.0)]:
            subset = [r for r in records if q_lo <= r["depth_percentile"] < q_hi or
                      (q_hi == 1.0 and r["depth_percentile"] == 1.0)]
            if subset:
                accs.append(sum(r["correct"] for r in subset) / len(subset))
            else:
                accs.append(0.0)
        return accs

    labels = ["0-25%", "25-50%", "50-75%", "75-100%"]
    ssm_accs = quartile_acc(mohawk_records)
    lawcat_accs = quartile_acc(lawcat_records)

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width/2, ssm_accs, width, label="MOHAWK-SSM", color="#e74c3c", alpha=0.8)
    ax.bar(x + width/2, lawcat_accs, width, label="LAWCAT", color="#3498db", alpha=0.8)

    ax.set_xlabel("Depth Quartile", fontsize=12)
    ax.set_ylabel("Accuracy", fontsize=12)
    ax.set_title("Accuracy by Depth Quartile\n(Retrieval-Heavy Tasks)", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.set_ylim(0, 1.0)

    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, "depth_quartile_accuracy.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[Viz] Saved: {path}")
    return path


def plot_beta_forest(gate_result: dict, reg_results: dict) -> str:
    """
    FR-5.4: Forest plot of β_depth with 95% CIs and ratio annotation.
    """
    ssm = reg_results["mohawk_ssm"]
    lawcat = reg_results["lawcat"]

    fig, ax = plt.subplots(figsize=(7, 4))

    models = ["MOHAWK-SSM", "LAWCAT"]
    betas = [ssm["beta"], lawcat["beta"]]
    ci_lows = [ssm["ci_low"], lawcat["ci_low"]]
    ci_highs = [ssm["ci_high"], lawcat["ci_high"]]
    colors = ["#e74c3c", "#3498db"]

    y_pos = [1, 0]
    for i, (model, beta, clo, chi, color) in enumerate(zip(models, betas, ci_lows, ci_highs, colors)):
        y = y_pos[i]
        ax.plot([clo, chi], [y, y], color=color, linewidth=3, alpha=0.8)
        ax.scatter([beta], [y], color=color, s=120, zorder=5)
        ax.text(chi + 0.002, y, f"β={beta:.3f} [{clo:.3f}, {chi:.3f}]",
                va="center", ha="left", fontsize=9)

    ax.axvline(0, color="black", linestyle="-", linewidth=1, alpha=0.5)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(models, fontsize=11)
    ax.set_xlabel("β_depth (depth_percentile coefficient)", fontsize=11)
    ax.set_title("Forest Plot: Depth-Accuracy Coefficient\n(Retrieval-Heavy Tasks)", fontsize=11)

    ratio = gate_result.get("ratio", 0)
    verdict = gate_result.get("verdict", "?")
    ax.text(0.5, -0.18, f"Ratio |β_SSM|/|β_LAWCAT| = {ratio:.2f} | Gate: {verdict}",
            transform=ax.transAxes, ha="center", fontsize=9,
            bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, "beta_forest_plot.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[Viz] Saved: {path}")
    return path


def generate_all_figures(
    mohawk_records: list[dict],
    lawcat_records: list[dict],
    reg_results: dict,
    gate_result: dict,
) -> list[str]:
    """Generate all 4 required figures. Returns list of saved paths."""
    paths = []
    paths.append(plot_gate_metrics(gate_result, reg_results))
    paths.append(plot_depth_accuracy_scatter(mohawk_records, lawcat_records, reg_results))
    paths.append(plot_depth_quartile_accuracy(mohawk_records, lawcat_records))
    paths.append(plot_beta_forest(gate_result, reg_results))
    return paths
