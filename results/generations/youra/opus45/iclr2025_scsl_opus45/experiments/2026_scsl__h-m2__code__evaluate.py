"""Evaluation module for H-M2 experiment.

Implements multi-regime AUROC evaluation, delta computation, gate evaluation,
mechanism verification, and visualization functions.
"""

import os
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

from config import Config


def extract_trajectory_features(loss_matrix: np.ndarray) -> np.ndarray:
    """Extract 4 trajectory features per sample from loss trajectories.

    Features:
        F1 (L1): Initial loss at epoch 1
        F2 (slope): Linear slope (L5 - L1) / 4
        F3 (variance): Variance of normalized trajectory
        F4 (convergence_time): Epoch index of minimum loss

    Args:
        loss_matrix: Per-sample losses, shape (N, 5)

    Returns:
        Feature matrix, shape (N, 4)
    """
    N, E = loss_matrix.shape

    # F1: Initial loss (epoch 1)
    L1 = loss_matrix[:, 0]

    # F2: Slope (L5 - L1) / 4
    L5 = loss_matrix[:, -1]
    slope = (L5 - L1) / (E - 1)

    # F3: Variance of normalized trajectory
    L_norm = loss_matrix / (L1[:, None] + 1e-8)
    variance = np.var(L_norm, axis=1)

    # F4: Convergence time (epoch of minimum loss)
    convergence_time = np.argmin(loss_matrix, axis=1).astype(np.float32)

    # Stack features: shape (N, 4)
    features = np.stack([L1, slope, variance, convergence_time], axis=1)

    return features


def compute_auroc_cv(
    features: np.ndarray,
    minority_labels: np.ndarray,
    n_splits: int = 5,
    seed: int = 42,
) -> Tuple[float, float]:
    """Compute AUROC with stratified k-fold cross-validation.

    Uses LogisticRegression as classifier for trajectory features.

    Args:
        features: Trajectory features, shape (N, 4)
        minority_labels: Binary labels (1=minority, 0=majority), shape (N,)
        n_splits: Number of CV folds (default: 5)
        seed: Random seed for reproducibility

    Returns:
        Tuple of (mean_auroc, std_auroc)
    """
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    auroc_scores = []

    for train_idx, val_idx in skf.split(features, minority_labels):
        clf = LogisticRegression(max_iter=1000, random_state=seed)
        clf.fit(features[train_idx], minority_labels[train_idx])

        probs = clf.predict_proba(features[val_idx])[:, 1]
        auroc = roc_auc_score(minority_labels[val_idx], probs)
        auroc_scores.append(auroc)

    return float(np.mean(auroc_scores)), float(np.std(auroc_scores))


def evaluate_all_regimes(
    regime_features: Dict[str, np.ndarray],
    minority_labels: np.ndarray,
    config: Config,
) -> Dict[str, Tuple[float, float]]:
    """Compute AUROC CV for each regime.

    Args:
        regime_features: {'erm': (N,4), 'groupdro': (N,4), 'random': (N,4)}
        minority_labels: Binary labels, shape (N,)
        config: Experiment configuration

    Returns:
        {'erm': (mean, std), 'groupdro': (mean, std), 'random': (mean, std)}
    """
    results = {}
    for regime, features in regime_features.items():
        mean_auroc, std_auroc = compute_auroc_cv(
            features, minority_labels, n_splits=config.n_folds, seed=config.base_seed
        )
        results[regime] = (mean_auroc, std_auroc)
        print(f"[{regime.upper()}] AUROC = {mean_auroc:.4f} ± {std_auroc:.4f}")

    return results


def compute_delta_auroc(
    auroc_erm: float,
    auroc_gdro: float,
    auroc_random: float,
) -> Tuple[float, float]:
    """Compute AUROC deltas between ERM and other regimes.

    Args:
        auroc_erm: ERM AUROC
        auroc_gdro: GroupDRO AUROC
        auroc_random: Random reweighting AUROC

    Returns:
        (delta_gdro, delta_random)
        delta_gdro = auroc_erm - auroc_gdro
        delta_random = auroc_erm - auroc_random
    """
    delta_gdro = auroc_erm - auroc_gdro
    delta_random = auroc_erm - auroc_random
    return delta_gdro, delta_random


def evaluate_gate(
    delta_gdro: float,
    delta_random: float,
    config: Config,
) -> Tuple[bool, str]:
    """Evaluate H-M2 gate condition.

    Gate: delta_gdro > 0.10 AND delta_random < 0.05

    Args:
        delta_gdro: AUROC_ERM - AUROC_GroupDRO
        delta_random: AUROC_ERM - AUROC_Random
        config: Experiment configuration

    Returns:
        (passed, result_str)
    """
    cond1 = delta_gdro > config.delta_gdro_threshold  # > 0.10
    cond2 = delta_random < config.delta_random_threshold  # < 0.05
    passed = cond1 and cond2

    result_str = "PASS" if passed else "FAIL"

    print(f"\n{'='*60}")
    print("GATE EVALUATION")
    print(f"{'='*60}")
    print(f"Condition 1: ΔAUROC_GroupDRO = {delta_gdro:.4f} > {config.delta_gdro_threshold} → {'✓' if cond1 else '✗'}")
    print(f"Condition 2: ΔAUROC_Random = {delta_random:.4f} < {config.delta_random_threshold} → {'✓' if cond2 else '✗'}")
    print(f"Gate Result: {result_str}")
    print(f"{'='*60}\n")

    return passed, result_str


def verify_mechanism_activation(
    group_weights_history: np.ndarray,
    groupdro_grad_var: float,
    random_grad_var: float,
) -> Dict[str, bool]:
    """Verify GroupDRO mechanism activation.

    Checks:
    1. GroupDRO weights diverge from uniform (>5% deviation)
    2. Gradient variance matching within 20% tolerance

    Args:
        group_weights_history: GroupDRO weights over epochs, shape (epochs, 4)
        groupdro_grad_var: Gradient variance under GroupDRO
        random_grad_var: Gradient variance under random reweighting

    Returns:
        {'weights_diverged': bool, 'variance_matched': bool}
    """
    # Check final weights divergence from uniform
    final_weights = group_weights_history[-1]
    uniform = np.ones(4) / 4
    max_deviation = np.max(np.abs(final_weights - uniform))
    weights_diverged = max_deviation > 0.05

    # Check variance matching (within 20% tolerance)
    if groupdro_grad_var > 0:
        variance_diff = abs(groupdro_grad_var - random_grad_var) / (groupdro_grad_var + 1e-8)
        variance_matched = variance_diff < 0.20
    else:
        variance_matched = True  # Default if variance is zero

    print(f"\nMECHANISM VERIFICATION:")
    print(f"  GroupDRO weights diverged: {weights_diverged} (max deviation: {max_deviation:.4f})")
    print(f"  Variance matched: {variance_matched} (diff: {variance_diff:.4f})" if groupdro_grad_var > 0 else f"  Variance matched: {variance_matched}")

    return {
        'weights_diverged': weights_diverged,
        'variance_matched': variance_matched,
    }


def compute_gradient_variance(weights: np.ndarray) -> float:
    """Compute variance of sample weights (proxy for gradient variance).

    Args:
        weights: Sample weights, shape (N,)

    Returns:
        Variance of weights
    """
    return float(np.var(weights))


# ==============================================================================
# VISUALIZATION FUNCTIONS
# ==============================================================================

def plot_gate_metrics(
    delta_gdro: float,
    delta_random: float,
    config: Config,
    save_path: str,
) -> None:
    """Plot gate metrics comparison bar chart.

    Shows ΔAUROC_GroupDRO vs ΔAUROC_Random with threshold lines.

    Args:
        delta_gdro: AUROC_ERM - AUROC_GroupDRO
        delta_random: AUROC_ERM - AUROC_Random
        config: Experiment configuration
        save_path: Path to save figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    categories = ["ΔAUROC (GroupDRO)\nTarget: > 0.10", "ΔAUROC (Random)\nTarget: < 0.05"]
    values = [delta_gdro, delta_random]
    thresholds = [config.delta_gdro_threshold, config.delta_random_threshold]

    # Color based on condition met
    colors = [
        "#4CAF50" if delta_gdro > config.delta_gdro_threshold else "#F44336",
        "#4CAF50" if delta_random < config.delta_random_threshold else "#F44336",
    ]

    bars = ax.bar(categories, values, color=colors, edgecolor="black", linewidth=1.5, width=0.5)

    # Add threshold lines
    ax.axhline(y=config.delta_gdro_threshold, color="#2196F3", linestyle="--", linewidth=2,
               label=f"GroupDRO threshold: {config.delta_gdro_threshold}")
    ax.axhline(y=config.delta_random_threshold, color="#FF9800", linestyle="--", linewidth=2,
               label=f"Random threshold: {config.delta_random_threshold}")

    # Value labels
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.01,
            f"{val:.4f}",
            ha="center",
            va="bottom",
            fontsize=14,
            fontweight="bold",
        )

    # Gate result annotation
    cond1 = delta_gdro > config.delta_gdro_threshold
    cond2 = delta_random < config.delta_random_threshold
    passed = cond1 and cond2
    result = "PASS ✓" if passed else "FAIL ✗"
    result_color = "#4CAF50" if passed else "#F44336"

    ax.text(
        0.98, 0.95,
        f"Gate Result: {result}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=16,
        fontweight="bold",
        color=result_color,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=result_color),
    )

    ax.set_ylabel("ΔAUROC (ERM - Regime)", fontsize=12)
    ax.set_title("H-M2 Gate: Spurious-Specificity Test", fontsize=14)
    ax.legend(loc="lower right")
    ax.set_ylim(-0.1, max(0.3, max(values) + 0.1))
    ax.axhline(y=0, color="gray", linestyle="-", linewidth=0.5)

    plt.tight_layout()
    plt.savefig(save_path, dpi=config.fig_dpi, format=config.fig_format, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def plot_auroc_comparison(
    auroc_results: Dict[str, Tuple[float, float]],
    config: Config,
    save_path: str,
) -> None:
    """Plot AUROC comparison across all regimes.

    Args:
        auroc_results: {'erm': (mean, std), 'groupdro': (mean, std), 'random': (mean, std)}
        config: Experiment configuration
        save_path: Path to save figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    regimes = ["ERM\n(Baseline)", "GroupDRO", "Random\nReweighting"]
    keys = ["erm", "groupdro", "random"]
    means = [auroc_results[k][0] for k in keys]
    stds = [auroc_results[k][1] for k in keys]
    colors = ["#2196F3", "#4CAF50", "#FF9800"]

    bars = ax.bar(regimes, means, yerr=stds, color=colors, edgecolor="black",
                  linewidth=1.5, capsize=5, width=0.5)

    # Value labels
    for bar, mean, std in zip(bars, means, stds):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + std + 0.02,
            f"{mean:.3f}",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
        )

    ax.set_ylabel("AUROC", fontsize=12)
    ax.set_title("Trajectory Feature AUROC by Training Regime", fontsize=14)
    ax.set_ylim(0, 1.1)

    plt.tight_layout()
    plt.savefig(save_path, dpi=config.fig_dpi, format=config.fig_format, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def plot_group_weights_evolution(
    group_weights_history: np.ndarray,
    config: Config,
    save_path: str,
) -> None:
    """Plot GroupDRO group weights evolution over epochs.

    Args:
        group_weights_history: Shape (epochs, 4)
        config: Experiment configuration
        save_path: Path to save figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    epochs = np.arange(1, len(group_weights_history) + 1)
    group_names = [
        "G0: Landbird+Land (Maj)",
        "G1: Landbird+Water (Min)",
        "G2: Waterbird+Land (Min)",
        "G3: Waterbird+Water (Maj)",
    ]
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    for g in range(4):
        ax.plot(epochs, group_weights_history[:, g], "-o", label=group_names[g],
                color=colors[g], linewidth=2, markersize=4)

    # Uniform line
    ax.axhline(y=0.25, color="gray", linestyle="--", linewidth=1, label="Uniform (0.25)")

    ax.set_xlabel("Epoch", fontsize=12)
    ax.set_ylabel("Group Weight", fontsize=12)
    ax.set_title("GroupDRO: Group Weight Evolution", fontsize=14)
    ax.legend(loc="best", fontsize=9)
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=config.fig_dpi, format=config.fig_format, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def plot_gradient_variance_comparison(
    gdro_var: float,
    random_var: float,
    config: Config,
    save_path: str,
) -> None:
    """Plot gradient variance comparison between GroupDRO and Random.

    Args:
        gdro_var: GroupDRO gradient variance
        random_var: Random reweighting gradient variance
        config: Experiment configuration
        save_path: Path to save figure
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    categories = ["GroupDRO", "Random\nReweighting"]
    values = [gdro_var, random_var]
    colors = ["#4CAF50", "#FF9800"]

    bars = ax.bar(categories, values, color=colors, edgecolor="black", linewidth=1.5, width=0.4)

    # Value labels
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.001,
            f"{val:.6f}",
            ha="center",
            va="bottom",
            fontsize=12,
        )

    # Variance match annotation
    diff = abs(gdro_var - random_var) / (gdro_var + 1e-8)
    matched = diff < 0.20
    match_text = f"Variance Match: {'✓' if matched else '✗'} ({diff:.1%} diff)"
    match_color = "#4CAF50" if matched else "#F44336"

    ax.text(
        0.98, 0.95,
        match_text,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=12,
        fontweight="bold",
        color=match_color,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=match_color),
    )

    ax.set_ylabel("Weight Variance", fontsize=12)
    ax.set_title("Gradient Variance Verification", fontsize=14)

    plt.tight_layout()
    plt.savefig(save_path, dpi=config.fig_dpi, format=config.fig_format, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def plot_loss_trajectory_panels(
    loss_matrices: Dict[str, np.ndarray],
    minority_labels: np.ndarray,
    config: Config,
    save_path: str,
) -> None:
    """Plot loss trajectory comparison panels for all regimes.

    Args:
        loss_matrices: {'erm': (N, 5), 'groupdro': (N, 5), 'random': (N, 5)}
        minority_labels: Binary labels, shape (N,)
        config: Experiment configuration
        save_path: Path to save figure
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    regime_names = ["ERM", "GroupDRO", "Random Reweighting"]
    keys = ["erm", "groupdro", "random"]

    majority_mask = minority_labels == 0
    minority_mask = minority_labels == 1

    for ax, name, key in zip(axes, regime_names, keys):
        loss_matrix = loss_matrices[key]
        epochs = np.arange(1, loss_matrix.shape[1] + 1)

        # Normalize by initial loss
        L_norm = loss_matrix / (loss_matrix[:, 0:1] + 1e-8)

        # Split by group
        majority_traj = L_norm[majority_mask]
        minority_traj = L_norm[minority_mask]

        # Compute mean and std
        maj_mean = np.mean(majority_traj, axis=0)
        maj_std = np.std(majority_traj, axis=0)
        min_mean = np.mean(minority_traj, axis=0)
        min_std = np.std(minority_traj, axis=0)

        # Plot
        ax.plot(epochs, maj_mean, "b-", linewidth=2, label=f"Majority (n={majority_mask.sum()})")
        ax.fill_between(epochs, maj_mean - maj_std, maj_mean + maj_std, alpha=0.2, color="blue")

        ax.plot(epochs, min_mean, "r-", linewidth=2, label=f"Minority (n={minority_mask.sum()})")
        ax.fill_between(epochs, min_mean - min_std, min_mean + min_std, alpha=0.2, color="red")

        ax.set_xlabel("Epoch", fontsize=11)
        ax.set_ylabel("Normalized Loss (L / L₁)", fontsize=11)
        ax.set_title(name, fontsize=12, fontweight="bold")
        ax.legend(loc="upper right", fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.suptitle("Loss Trajectory Comparison Across Training Regimes", fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=config.fig_dpi, format=config.fig_format, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")
