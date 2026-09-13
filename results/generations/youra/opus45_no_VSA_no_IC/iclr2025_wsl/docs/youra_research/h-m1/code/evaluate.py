"""Evaluation and visualization for H-M1."""
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def plot_gate_comparison(nfn_r2: float, baseline_r2: float, out_path: str):
    """Bar chart comparing NFN vs baseline R²."""
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(["Statistics\nBaseline", "NFN\nEquivariant"], [baseline_r2, nfn_r2],
                  color=["#5B8FB9", "#E97451"])
    ax.axhline(y=0.85, color="red", linestyle="--", label="Target R² = 0.85")
    ax.set_ylabel("R² Score")
    ax.set_title("Gate Metrics: NFN vs Baseline")
    ax.set_ylim(0, 1.05)
    ax.legend()

    for bar, val in zip(bars, [baseline_r2, nfn_r2]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{val:.4f}", ha="center", fontsize=10)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_prediction_scatter(y_true: np.ndarray, y_pred: np.ndarray, r2: float, out_path: str):
    """Scatter plot of true vs predicted accuracy."""
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(y_true, y_pred, alpha=0.5, s=20)
    ax.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()],
            "r--", label="Perfect prediction")
    ax.set_xlabel("True Accuracy")
    ax.set_ylabel("Predicted Accuracy")
    ax.set_title(f"NFN Predictions (R² = {r2:.4f})")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_equivariance(pass_rate: float, max_error: float, out_path: str):
    """Visualize equivariance test results."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # Pass rate pie chart
    axes[0].pie([pass_rate, 1 - pass_rate], labels=["Pass", "Fail"],
                colors=["#4CAF50", "#F44336"], autopct="%1.1f%%")
    axes[0].set_title(f"Equivariance Pass Rate: {pass_rate*100:.1f}%")

    # Max error bar
    axes[1].bar(["Max Error"], [max_error], color="#E97451")
    axes[1].axhline(y=1e-5, color="green", linestyle="--", label="Tolerance (1e-5)")
    axes[1].set_ylabel("Absolute Error")
    axes[1].set_title("Equivariance Error")
    axes[1].legend()
    axes[1].set_yscale("log")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_training_curve(history: dict, out_path: str):
    """Plot training loss and validation R² curves."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    epochs = range(1, len(history["train_loss"]) + 1)

    axes[0].plot(epochs, history["train_loss"], label="Train Loss")
    axes[0].plot(epochs, history["val_loss"], label="Val Loss")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("MSE Loss")
    axes[0].set_title("Training Curve")
    axes[0].legend()

    axes[1].plot(epochs, history["val_r2"], label="Val R²", color="green")
    axes[1].axhline(y=0.85, color="red", linestyle="--", label="Target")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("R² Score")
    axes[1].set_title("Validation R²")
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_residuals(y_true: np.ndarray, y_pred: np.ndarray, out_path: str):
    """Histogram of prediction residuals."""
    residuals = y_pred - y_true

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(residuals, bins=30, edgecolor="black", alpha=0.7)
    ax.axvline(x=0, color="red", linestyle="--")
    ax.set_xlabel("Residual (Predicted - True)")
    ax.set_ylabel("Frequency")
    ax.set_title(f"Residual Distribution (MAE = {np.abs(residuals).mean():.4f})")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
