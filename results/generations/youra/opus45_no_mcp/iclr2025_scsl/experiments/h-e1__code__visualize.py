import os
import numpy as np
import matplotlib.pyplot as plt
from detector import CrystallizationDetector

def plot_wga_curve(wga_history: list, peak_epoch: int, save_path: str) -> None:
    plt.figure(figsize=(10, 6))
    epochs = range(len(wga_history))
    plt.plot(epochs, wga_history, "b-", label="WGA")
    plt.axvline(x=peak_epoch, color="r", linestyle="--", label=f"Crystallization (epoch {peak_epoch})")
    plt.xlabel("Epoch")
    plt.ylabel("Worst-Group Accuracy")
    plt.title("WGA Curve with Crystallization Point")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()

def plot_second_derivative(d2: np.ndarray, peak_epoch: int, save_path: str) -> None:
    plt.figure(figsize=(10, 6))
    epochs = range(len(d2))
    plt.plot(epochs, d2, "g-", label="d²WGA/dt²")
    plt.axvline(x=peak_epoch, color="r", linestyle="--", label=f"Peak (epoch {peak_epoch})")
    plt.axhline(y=-0.01, color="orange", linestyle=":", label="Threshold (-0.01)")
    plt.xlabel("Epoch")
    plt.ylabel("Second Derivative")
    plt.title("Second Derivative of WGA")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()

def plot_multi_benchmark(histories: dict, save_path: str) -> None:
    plt.figure(figsize=(10, 6))
    for name, wga_hist in histories.items():
        normalized_epochs = np.linspace(0, 1, len(wga_hist))
        plt.plot(normalized_epochs, wga_hist, label=name)
    plt.xlabel("Normalized Epoch")
    plt.ylabel("WGA")
    plt.title("Multi-Benchmark WGA Comparison")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()

def plot_smoothing_sensitivity(wga_history: list, windows: list, save_path: str) -> None:
    plt.figure(figsize=(10, 6))
    for w in windows:
        detector = CrystallizationDetector(smoothing_window=w)
        for wga in wga_history:
            detector.log_epoch(wga)
        d2 = detector.compute_second_derivative()
        plt.plot(range(len(d2)), d2, label=f"window={w}")
    plt.xlabel("Epoch")
    plt.ylabel("d²WGA/dt²")
    plt.title("Smoothing Window Sensitivity")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()

def plot_group_divergence(group_acc_history: list, save_path: str) -> None:
    if not group_acc_history:
        return
    groups = sorted(group_acc_history[0].keys())
    plt.figure(figsize=(10, 6))
    for g in groups:
        accs = [epoch_acc.get(g, 0) for epoch_acc in group_acc_history]
        plt.plot(range(len(accs)), accs, label=f"Group {g}")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.title("Per-Group Accuracy Divergence")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
