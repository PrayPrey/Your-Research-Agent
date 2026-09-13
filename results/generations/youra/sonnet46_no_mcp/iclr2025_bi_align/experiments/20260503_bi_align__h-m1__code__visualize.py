import logging
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)


def _ensure_dir(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)


def plot_coefficient_drift(results: list, out_dir: Path) -> None:
    """Figure 1: β_L, β_H, β_S line plots across rounds with 95% CI bands."""
    _ensure_dir(out_dir)
    rounds = [r.round_id for r in results]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    feature_info = [
        ("beta_L", "β_L (Verbosity)", "blue"),
        ("beta_H", "β_H (Hedging)", "orange"),
        ("beta_S", "β_S (Structure)", "green"),
    ]
    for ax, (attr, label, color) in zip(axes, feature_info):
        vals = [getattr(r, attr) for r in results]
        ci_attr = "ci_" + attr.split("_")[1]
        cis = [getattr(r, ci_attr) for r in results]
        lo = [c[0] if not np.isnan(c[0]) else v for v, c in zip(vals, cis)]
        hi = [c[1] if not np.isnan(c[1]) else v for v, c in zip(vals, cis)]
        ax.plot(rounds, vals, marker="o", color=color, label=label)
        ax.fill_between(rounds, lo, hi, alpha=0.2, color=color)
        ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)
        ax.set_xlabel("Annotation Round")
        ax.set_ylabel("Coefficient Value")
        ax.set_title(label)
        ax.set_xticks(rounds)
    plt.suptitle("Stylistic Coefficient Drift Across Annotation Rounds")
    plt.tight_layout()
    out_path = out_dir / "coefficient_drift.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {out_path}")


def plot_ambiguity_stratification(
    results_hi: list, results_lo: list, out_dir: Path
) -> None:
    """Figure 2: coefficient drift high vs low ambiguity groups."""
    _ensure_dir(out_dir)
    if not results_hi or not results_lo:
        logger.warning("Empty results for ambiguity stratification plot; skipping")
        return
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    feature_info = [
        ("beta_L", "β_L (Verbosity)"),
        ("beta_H", "β_H (Hedging)"),
        ("beta_S", "β_S (Structure)"),
    ]
    for ax, (attr, label) in zip(axes, feature_info):
        hi_rounds = [r.round_id for r in results_hi]
        lo_rounds = [r.round_id for r in results_lo]
        hi_vals = [getattr(r, attr) for r in results_hi]
        lo_vals = [getattr(r, attr) for r in results_lo]
        ax.plot(hi_rounds, hi_vals, marker="o", color="red", label="High Ambiguity")
        ax.plot(lo_rounds, lo_vals, marker="s", color="blue", label="Low Ambiguity")
        ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)
        ax.set_xlabel("Annotation Round")
        ax.set_ylabel("Coefficient")
        ax.set_title(label)
        ax.legend(fontsize=8)
    plt.suptitle("Coefficient Drift by Ambiguity Stratum")
    plt.tight_layout()
    out_path = out_dir / "ambiguity_stratification.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {out_path}")


def plot_q_early_calibration(q_early_model, round_dfs: dict, out_dir: Path) -> None:
    """Figure 3: reliability diagrams per round + Brier scores."""
    _ensure_dir(out_dir)
    from features import build_feature_matrix
    from sklearn.calibration import calibration_curve

    fig, axes = plt.subplots(1, len(round_dfs), figsize=(5 * len(round_dfs), 5))
    if len(round_dfs) == 1:
        axes = [axes]

    for ax, (r, df_r) in zip(axes, sorted(round_dfs.items())):
        try:
            X, y = build_feature_matrix(df_r)
            proba = q_early_model.predict_proba(X)[:, 1]
            frac_pos, mean_pred = calibration_curve(y, proba, n_bins=10)
            brier = float(np.mean((proba - y) ** 2))
            ax.plot(mean_pred, frac_pos, marker="o", label=f"Round {r}")
            ax.plot([0, 1], [0, 1], "k--", linewidth=0.8)
            ax.set_xlabel("Mean Predicted Probability")
            ax.set_ylabel("Fraction of Positives")
            ax.set_title(f"Round {r}\nBrier={brier:.4f}")
            ax.legend(fontsize=8)
        except Exception as e:
            logger.warning(f"Calibration plot round {r} failed: {e}")
            ax.set_title(f"Round {r} (error)")

    plt.suptitle("Q_early Calibration Curves")
    plt.tight_layout()
    out_path = out_dir / "q_early_calibration.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {out_path}")


def plot_placebo_distribution(
    perm_results: dict, observed: dict, out_dir: Path
) -> None:
    """Figure 4: null distribution histogram with observed value marked."""
    _ensure_dir(out_dir)
    features = list(perm_results.keys())
    n = len(features)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 5))
    if n == 1:
        axes = [axes]
    for ax, feat in zip(axes, features):
        perm_vals = perm_results.get(feat, [])
        obs_val = observed.get(feat, 0.0)
        if len(perm_vals) > 0:
            ax.hist(perm_vals, bins=30, color="steelblue", alpha=0.7, label="Permuted")
        ax.axvline(obs_val, color="red", linewidth=2, label=f"Observed={obs_val:.3f}")
        ax.set_xlabel("Coefficient Difference (r3 - r1)")
        ax.set_ylabel("Count")
        ax.set_title(feat)
        ax.legend(fontsize=8)
    plt.suptitle("Placebo Permutation Test — Null Distributions")
    plt.tight_layout()
    out_path = out_dir / "placebo_distribution.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {out_path}")


def plot_feature_correlation(X: np.ndarray, out_dir: Path) -> None:
    """Figure 5: correlation heatmap / VIF diagnostic."""
    _ensure_dir(out_dir)
    import pandas as pd
    df_feat = pd.DataFrame(X, columns=["β_L", "β_H", "β_S"])
    corr = df_feat.corr()
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(corr, annot=True, fmt=".3f", cmap="coolwarm", ax=ax,
                vmin=-1, vmax=1, center=0)
    ax.set_title("Feature Correlation (VIF Diagnostic)")
    plt.tight_layout()
    out_path = out_dir / "feature_correlation.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {out_path}")


def plot_gate_metrics(brier_diff: float, interaction_p: float, out_dir: Path) -> None:
    """Figure 6: bar chart of key gate metrics vs thresholds."""
    _ensure_dir(out_dir)
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    # Brier diff gate
    ax = axes[0]
    ax.bar(["Observed", "Threshold"], [brier_diff, 0.02],
           color=["green" if brier_diff < 0.02 else "red", "gray"])
    ax.set_title("Brier Score Difference\n(gate: < 0.02)")
    ax.set_ylabel("Value")
    ax.axhline(0.02, color="red", linestyle="--", linewidth=1)

    # Interaction p-value gate
    ax = axes[1]
    ax.bar(["Observed", "Threshold"], [interaction_p, 0.0167],
           color=["green" if interaction_p < 0.0167 else "orange", "gray"])
    ax.set_title("Interaction Model p-value\n(gate: < 0.0167)")
    ax.set_ylabel("p-value")
    ax.axhline(0.0167, color="red", linestyle="--", linewidth=1)

    plt.suptitle("MUST_WORK Gate Metrics")
    plt.tight_layout()
    out_path = out_dir / "gate_metrics_comparison.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved: {out_path}")
