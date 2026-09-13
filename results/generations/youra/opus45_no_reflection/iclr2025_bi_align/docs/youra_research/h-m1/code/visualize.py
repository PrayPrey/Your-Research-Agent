"""Visualization suite for training metrics."""
import matplotlib.pyplot as plt
from config import CONFIG


def plot_loss_curves(history: dict, out_path: str) -> None:
    plt.figure(figsize=(10, 6))
    plt.plot(history["steps"], history["dpo_loss"], label="DPO Loss", color="blue")
    plt.plot(history["steps"], history["agency_loss"], label="Agency Loss", color="green")
    plt.plot(history["steps"], history["total_loss"], label="Total Loss", color="red")
    plt.xlabel("Steps")
    plt.ylabel("Loss")
    plt.title("BiDPO Training Loss Curves")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_gradient_norm(history: dict, out_path: str) -> None:
    plt.figure(figsize=(10, 6))
    plt.plot(history["steps"], history["grad_norm"], label="Gradient Norm", color="purple")
    plt.axhline(y=CONFIG.grad_clip_norm, color="red", linestyle="--", label=f"Clip Threshold ({CONFIG.grad_clip_norm})")
    plt.xlabel("Steps")
    plt.ylabel("Gradient Norm")
    plt.title("Gradient Norm Over Training")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_lr_schedule(history: dict, out_path: str) -> None:
    plt.figure(figsize=(10, 6))
    plt.plot(history["steps"], history["lr"], label="Learning Rate", color="orange")
    plt.xlabel("Steps")
    plt.ylabel("Learning Rate")
    plt.title("Learning Rate Schedule (Cosine with Warmup)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
