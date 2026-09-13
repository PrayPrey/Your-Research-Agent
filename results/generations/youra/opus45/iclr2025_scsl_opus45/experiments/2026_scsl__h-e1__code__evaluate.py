"""Evaluation module for H-E1 experiment.

Implements trajectory feature extraction, AUROC evaluation, and visualization.
"""

import os
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
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
    N, E = loss_matrix.shape  # N=4795, E=5

    # F1: Initial loss (epoch 1)
    L1 = loss_matrix[:, 0]

    # F2: Slope (L5 - L1) / 4
    L5 = loss_matrix[:, -1]
    slope = (L5 - L1) / (E - 1)

    # F3: Variance of normalized trajectory
    # Normalize by L1 to get scale-invariant trajectory
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

        # Predict probabilities for positive class (minority)
        probs = clf.predict_proba(features[val_idx])[:, 1]
        auroc = roc_auc_score(minority_labels[val_idx], probs)
        auroc_scores.append(auroc)

    return np.mean(auroc_scores), np.std(auroc_scores)


def compute_per_feature_auroc(
    features: np.ndarray,
    minority_labels: np.ndarray,
) -> Dict[str, float]:
    """Compute AUROC for each individual feature.

    Uses single-feature logistic regression (no CV for simplicity).

    Args:
        features: Trajectory features, shape (N, 4)
        minority_labels: Binary labels, shape (N,)

    Returns:
        Dict mapping feature name to AUROC score
    """
    feature_names = ["L1", "slope", "variance", "convergence"]
    per_feature_auroc = {}

    for i, name in enumerate(feature_names):
        # Single feature
        X = features[:, i:i+1]
        clf = LogisticRegression(max_iter=1000, random_state=42)
        clf.fit(X, minority_labels)
        probs = clf.predict_proba(X)[:, 1]
        auroc = roc_auc_score(minority_labels, probs)
        per_feature_auroc[name] = auroc

    return per_feature_auroc


def evaluate_gate(auroc: float, threshold: float = 0.75) -> bool:
    """Evaluate MUST_WORK gate condition.

    Args:
        auroc: Achieved AUROC score
        threshold: Gate threshold (default: 0.75)

    Returns:
        True if auroc >= threshold (PASS), False otherwise (FAIL)
    """
    return auroc >= threshold


def plot_gate_metrics(
    auroc: float,
    threshold: float,
    save_path: str,
    config: Config,
) -> None:
    """Plot gate metrics comparison bar chart.

    Args:
        auroc: Achieved AUROC score
        threshold: Gate threshold
        save_path: Path to save figure
        config: Experiment configuration
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    categories = ["Random\n(Baseline)", "Target\n(Threshold)", "Achieved\n(H-E1)"]
    values = [0.5, threshold, auroc]
    colors = ["#808080", "#2196F3", "#4CAF50" if auroc >= threshold else "#F44336"]

    bars = ax.bar(categories, values, color=colors, edgecolor="black", linewidth=1.5)

    # Add value labels
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.02,
            f"{val:.3f}",
            ha="center",
            va="bottom",
            fontsize=14,
            fontweight="bold",
        )

    # Add threshold line
    ax.axhline(y=threshold, color="#2196F3", linestyle="--", linewidth=2, label=f"Threshold: {threshold}")

    ax.set_ylabel("AUROC", fontsize=14)
    ax.set_title("H-E1 Gate Evaluation: Trajectory Features → Minority Prediction", fontsize=14)
    ax.set_ylim(0, 1.0)
    ax.legend(loc="lower right")

    # Gate result annotation
    result = "PASS ✓" if auroc >= threshold else "FAIL ✗"
    result_color = "#4CAF50" if auroc >= threshold else "#F44336"
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

    plt.tight_layout()
    plt.savefig(save_path, dpi=config.fig_dpi, format=config.fig_format, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def plot_loss_trajectories(
    loss_matrix: np.ndarray,
    minority_labels: np.ndarray,
    save_path: str,
    config: Config,
) -> None:
    """Plot loss trajectory comparison between minority and majority groups.

    Args:
        loss_matrix: Per-sample losses, shape (N, 5)
        minority_labels: Binary labels, shape (N,)
        save_path: Path to save figure
        config: Experiment configuration
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    epochs = np.arange(1, loss_matrix.shape[1] + 1)

    # Normalize by initial loss for scale-invariant comparison
    L_norm = loss_matrix / (loss_matrix[:, 0:1] + 1e-8)

    # Split by group
    majority_mask = minority_labels == 0
    minority_mask = minority_labels == 1

    majority_traj = L_norm[majority_mask]
    minority_traj = L_norm[minority_mask]

    # Compute mean and std
    maj_mean = np.mean(majority_traj, axis=0)
    maj_std = np.std(majority_traj, axis=0)
    min_mean = np.mean(minority_traj, axis=0)
    min_std = np.std(minority_traj, axis=0)

    # Plot majority
    ax.plot(epochs, maj_mean, "b-", linewidth=2, label=f"Majority (n={majority_mask.sum()})")
    ax.fill_between(epochs, maj_mean - maj_std, maj_mean + maj_std, alpha=0.2, color="blue")

    # Plot minority
    ax.plot(epochs, min_mean, "r-", linewidth=2, label=f"Minority (n={minority_mask.sum()})")
    ax.fill_between(epochs, min_mean - min_std, min_mean + min_std, alpha=0.2, color="red")

    ax.set_xlabel("Epoch", fontsize=12)
    ax.set_ylabel("Normalized Loss (L / L₁)", fontsize=12)
    ax.set_title("Loss Trajectory Comparison: Majority vs Minority Groups", fontsize=14)
    ax.legend(loc="upper right", fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=config.fig_dpi, format=config.fig_format, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def plot_roc_curve(
    features: np.ndarray,
    minority_labels: np.ndarray,
    save_path: str,
    config: Config,
) -> None:
    """Plot ROC curve with AUROC annotation.

    Args:
        features: Trajectory features, shape (N, 4)
        minority_labels: Binary labels, shape (N,)
        save_path: Path to save figure
        config: Experiment configuration
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    # Train on full data for ROC curve visualization
    clf = LogisticRegression(max_iter=1000, random_state=42)
    clf.fit(features, minority_labels)
    probs = clf.predict_proba(features)[:, 1]

    # Compute ROC curve
    fpr, tpr, _ = roc_curve(minority_labels, probs)
    auroc = roc_auc_score(minority_labels, probs)

    # Plot ROC curve
    ax.plot(fpr, tpr, "b-", linewidth=2, label=f"Trajectory Features (AUROC = {auroc:.3f})")

    # Plot random baseline
    ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="Random Baseline (AUROC = 0.500)")

    # Add threshold marker
    ax.axhline(y=config.auroc_threshold, color="r", linestyle=":", alpha=0.5)
    ax.axvline(x=1 - config.auroc_threshold, color="r", linestyle=":", alpha=0.5)

    ax.set_xlabel("False Positive Rate", fontsize=12)
    ax.set_ylabel("True Positive Rate", fontsize=12)
    ax.set_title("ROC Curve: Minority Group Prediction from Trajectory Features", fontsize=14)
    ax.legend(loc="lower right", fontsize=11)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=config.fig_dpi, format=config.fig_format, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def plot_feature_distributions(
    features: np.ndarray,
    minority_labels: np.ndarray,
    save_path: str,
    config: Config,
) -> None:
    """Plot feature distributions comparison.

    Args:
        features: Trajectory features, shape (N, 4)
        minority_labels: Binary labels, shape (N,)
        save_path: Path to save figure
        config: Experiment configuration
    """
    feature_names = ["L₁ (Initial Loss)", "Slope", "Variance", "Convergence Time"]
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    majority_mask = minority_labels == 0
    minority_mask = minority_labels == 1

    for i, (ax, name) in enumerate(zip(axes, feature_names)):
        maj_vals = features[majority_mask, i]
        min_vals = features[minority_mask, i]

        # Plot histograms
        ax.hist(maj_vals, bins=50, alpha=0.6, color="blue", label="Majority", density=True)
        ax.hist(min_vals, bins=50, alpha=0.6, color="red", label="Minority", density=True)

        # Add vertical lines for means
        ax.axvline(np.mean(maj_vals), color="blue", linestyle="--", linewidth=2)
        ax.axvline(np.mean(min_vals), color="red", linestyle="--", linewidth=2)

        ax.set_xlabel(name, fontsize=11)
        ax.set_ylabel("Density", fontsize=11)
        ax.set_title(f"Distribution: {name}", fontsize=12)
        ax.legend(loc="upper right")
        ax.grid(True, alpha=0.3)

    plt.suptitle("Trajectory Feature Distributions by Group", fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=config.fig_dpi, format=config.fig_format, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")
