import os
import json
import numpy as np
import matplotlib.pyplot as plt
from config import Config, SEEDS

def plot_gate_metrics(results_dir: str, save_path: str):
    eval_file = os.path.join(results_dir, "evaluation.json")
    with open(eval_file, "r") as f:
        result = json.load(f)
    tau_per_seed = result["tau_per_seed"]
    corr_per_seed = result["corr_per_seed"]
    fig, ax = plt.subplots(figsize=(8, 5))
    all_lags = None
    all_corrs = []
    for i, item in enumerate(corr_per_seed):
        lags = np.array(item["lags"])
        corr = np.array(item["corr"])
        if all_lags is None:
            all_lags = lags
        all_corrs.append(corr)
        ax.plot(lags, corr, alpha=0.3, color="blue", label="Per-seed" if i == 0 else None)
    mean_corr = np.mean(all_corrs, axis=0)
    std_corr = np.std(all_corrs, axis=0)
    ax.plot(all_lags, mean_corr, color="blue", linewidth=2, label="Mean")
    ax.fill_between(all_lags, mean_corr - 1.96 * std_corr, mean_corr + 1.96 * std_corr, alpha=0.2, color="blue", label="95% CI")
    ax.axvline(x=result["tau_mean"], color="red", linestyle="--", label=f"τ_mean={result['tau_mean']:.2f}")
    ax.axvline(x=0, color="gray", linestyle=":", alpha=0.5)
    ax.set_xlabel("Lag (epochs)")
    ax.set_ylabel("Cross-correlation")
    ax.set_title("H-M1: τ_r→SR Lagged Cross-Correlation")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved gate metrics plot to {save_path}")

def plot_time_series(results_dir: str, save_path: str):
    all_seeds_file = os.path.join(results_dir, "all_seeds.json")
    with open(all_seeds_file, "r") as f:
        all_data = json.load(f)
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()
    epochs = np.arange(1, len(all_data[0]["r_series"]) + 1)
    for data in all_data:
        ax1.plot(epochs, data["r_series"], alpha=0.3, color="blue")
        ax2.plot(epochs, data["sr_series"], alpha=0.3, color="red")
    mean_r = np.mean([d["r_series"] for d in all_data], axis=0)
    mean_sr = np.mean([d["sr_series"] for d in all_data], axis=0)
    ax1.plot(epochs, mean_r, color="blue", linewidth=2, label="r_t (gradient ratio)")
    ax2.plot(epochs, mean_sr, color="red", linewidth=2, label="SR_t (sharpness ratio)")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Gradient Ratio r_t", color="blue")
    ax2.set_ylabel("Sharpness Ratio SR_t", color="red")
    ax1.tick_params(axis="y", labelcolor="blue")
    ax2.tick_params(axis="y", labelcolor="red")
    ax1.set_title("H-M1: Gradient Ratio and Sharpness Ratio Over Training")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
    ax1.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved time series plot to {save_path}")

def plot_tau_per_seed(results_dir: str, save_path: str):
    eval_file = os.path.join(results_dir, "evaluation.json")
    with open(eval_file, "r") as f:
        result = json.load(f)
    tau_per_seed = result["tau_per_seed"]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(range(len(tau_per_seed)), tau_per_seed, color="steelblue", alpha=0.7)
    ax.axhline(y=result["tau_mean"], color="red", linestyle="--", label=f"Mean={result['tau_mean']:.2f}")
    ax.axhline(y=result["tau_ci"][0], color="orange", linestyle=":", label=f"95% CI lower={result['tau_ci'][0]:.2f}")
    ax.axhline(y=result["tau_ci"][1], color="orange", linestyle=":")
    ax.axhline(y=0, color="gray", linestyle="-", alpha=0.5)
    ax.set_xlabel("Seed")
    ax.set_ylabel("τ_r→SR (epochs)")
    ax.set_title("H-M1: Per-Seed τ Values")
    ax.set_xticks(range(len(tau_per_seed)))
    ax.set_xticklabels([f"Seed {s}" for s in SEEDS[:len(tau_per_seed)]])
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved tau per seed plot to {save_path}")

def main():
    cfg = Config()
    figures_dir = os.path.join(os.path.dirname(cfg.results_dir), "figures")
    os.makedirs(figures_dir, exist_ok=True)
    plot_gate_metrics(cfg.results_dir, os.path.join(figures_dir, "gate_metrics.png"))
    plot_time_series(cfg.results_dir, os.path.join(figures_dir, "time_series.png"))
    plot_tau_per_seed(cfg.results_dir, os.path.join(figures_dir, "tau_per_seed.png"))

if __name__ == "__main__":
    main()
