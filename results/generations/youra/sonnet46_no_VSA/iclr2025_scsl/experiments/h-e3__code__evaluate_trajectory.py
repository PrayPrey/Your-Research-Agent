import os
import sys
import numpy as np
import torch
from torch import Tensor
from sklearn.metrics import roc_auc_score
from scipy.stats import spearmanr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(__file__))
import config
from compute_traces import compute_traces_for_checkpoint, compute_hutchinson_cv
from train_erm import load_checkpoint


def compute_auroc(traces: Tensor, minority_mask: Tensor) -> float:
    t = traces.cpu().numpy()
    m = minority_mask.cpu().numpy()
    if m.sum() == 0 or (~m).sum() == 0:
        return 0.5
    return float(roc_auc_score(m.astype(int), t))


def compute_R(traces: Tensor, minority_mask: Tensor) -> float:
    t = traces.cpu().numpy()
    m = minority_mask.cpu().numpy().astype(bool)
    mean_min = t[m].mean() if m.sum() > 0 else 0.0
    mean_maj = t[~m].mean() if (~m).sum() > 0 else 1.0
    return float(mean_min / (mean_maj + 1e-12))


def compute_spearman(t_values: list, auroc_values: list):
    """Spearman ρ over rising segment. Returns (rho, p_value)."""
    if len(t_values) < 2:
        return 0.0, 1.0
    rho, p = spearmanr(t_values, auroc_values)
    return float(rho), float(p)


def evaluate_seed(
    seed: int,
    loader,
    minority_mask: Tensor,
    checkpoint_epochs: list,
    device: str,
) -> dict:
    results = {}
    traces_at_epochs = {}

    for epoch in checkpoint_epochs:
        traces = compute_traces_for_checkpoint(seed, epoch, loader, K=config.K_HUTCHINSON, device=device)
        auroc = compute_auroc(traces, minority_mask)
        R = compute_R(traces, minority_mask)
        t = traces.cpu().numpy()
        m = minority_mask.cpu().numpy().astype(bool)
        mean_min = float(t[m].mean()) if m.sum() > 0 else 0.0
        mean_maj = float(t[~m].mean()) if (~m).sum() > 0 else 0.0
        traces_std_min = float(t[m].std()) if m.sum() > 1 else 0.0
        results[epoch] = {
            "auroc": auroc,
            "R": R,
            "mean_min": mean_min,
            "mean_maj": mean_maj,
            "traces_std_min": traces_std_min,
        }
        traces_at_epochs[epoch] = traces
        print(f"  [seed={seed} epoch={epoch}] AUROC={auroc:.4f} R={R:.4f}")

    # Find t* = argmax R(t)
    R_values = [results[e]["R"] for e in checkpoint_epochs]
    t_star_idx = int(np.argmax(R_values))
    t_star = checkpoint_epochs[t_star_idx]

    # Spearman ρ over rising segment [0, t*]
    rising_epochs = checkpoint_epochs[:t_star_idx + 1]
    rising_aurocs = [results[e]["auroc"] for e in rising_epochs]
    rho, p_val = compute_spearman(rising_epochs, rising_aurocs)

    # Hutchinson CV at t*
    model_tstar = load_checkpoint(seed, t_star, device)
    cv = compute_hutchinson_cv(model_tstar, loader, n_resamples=5, K=config.K_HUTCHINSON, device=device)

    # Gate checks per seed
    auroc_tstar = results[t_star]["auroc"]
    auroc_t0 = results[0]["auroc"]
    gate_auroc_tstar = auroc_tstar >= 0.85
    gate_auroc_t0 = auroc_t0 < 0.70
    gate_spearman = rho >= 0.80
    seed_passes = gate_auroc_tstar and gate_auroc_t0 and gate_spearman

    return {
        "checkpoints": results,
        "t_star": t_star,
        "spearman_rho": rho,
        "spearman_p": p_val,
        "hutchinson_cv": cv,
        "gate_auroc_tstar": gate_auroc_tstar,
        "gate_auroc_t0": gate_auroc_t0,
        "gate_spearman": gate_spearman,
        "seed_passes": seed_passes,
        "traces_at_tstar": traces_at_epochs[t_star],
    }


def check_gate(all_seed_results: dict):
    per_seed_pass = {str(s): r["seed_passes"] for s, r in all_seed_results.items()}
    n_passing = sum(1 for v in per_seed_pass.values() if v)
    gate_satisfied = n_passing >= 4  # ≥4/5 seeds
    return gate_satisfied, per_seed_pass


# --- Figures ---

def plot_gate_metrics(all_seed_results: dict, out_dir: str) -> None:
    seeds = list(all_seed_results.keys())
    auroc_t0 = [all_seed_results[s]["checkpoints"][0]["auroc"] for s in seeds]
    t_stars = [all_seed_results[s]["t_star"] for s in seeds]
    auroc_tstar = [all_seed_results[s]["checkpoints"][t]["auroc"] for s, t in zip(seeds, t_stars)]

    x = np.arange(len(seeds))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - 0.2, auroc_t0, 0.4, label="AUROC(t=0)", alpha=0.8)
    ax.bar(x + 0.2, auroc_tstar, 0.4, label="AUROC(t*)", alpha=0.8)
    ax.axhline(0.85, color="r", linestyle="--", label="Gate 0.85")
    ax.axhline(0.70, color="orange", linestyle="--", label="t=0 ceiling 0.70")
    ax.set_xticks(x)
    ax.set_xticklabels([f"seed={s}" for s in seeds])
    ax.set_ylabel("AUROC")
    ax.set_title("Gate Metrics: AUROC(t=0) vs AUROC(t*)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig1_gate_metrics.png"), dpi=150)
    plt.close()


def plot_R_trajectory(all_seed_results: dict, out_dir: str) -> None:
    epochs = config.CHECKPOINT_EPOCHS
    r_matrix = np.array([[all_seed_results[s]["checkpoints"][e]["R"] for e in epochs]
                          for s in all_seed_results])
    mean_r = r_matrix.mean(0)
    std_r = r_matrix.std(0)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(epochs, mean_r, "b-o", label="mean R(t)")
    ax.fill_between(epochs, mean_r - std_r, mean_r + std_r, alpha=0.2)
    # annotate t*
    t_stars = [all_seed_results[s]["t_star"] for s in all_seed_results]
    for s, t in zip(all_seed_results.keys(), t_stars):
        ax.axvline(t, color="gray", alpha=0.3, linestyle=":")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("R(t) = mean_minority / mean_majority")
    ax.set_title("R(t) Trajectory (mean ± std)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig2_R_trajectory.png"), dpi=150)
    plt.close()


def plot_auroc_trajectory(all_seed_results: dict, out_dir: str) -> None:
    epochs = config.CHECKPOINT_EPOCHS
    fig, ax = plt.subplots(figsize=(8, 5))
    auroc_matrix = []
    for s, r in all_seed_results.items():
        vals = [r["checkpoints"][e]["auroc"] for e in epochs]
        auroc_matrix.append(vals)
        ax.plot(epochs, vals, alpha=0.5, label=f"seed={s}")
    mean_a = np.mean(auroc_matrix, 0)
    ax.plot(epochs, mean_a, "k-o", linewidth=2, label="mean")
    ax.axhline(0.85, color="r", linestyle="--", label="Gate 0.85")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("AUROC")
    ax.set_title("AUROC Trajectory per Seed")
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig3_auroc_trajectory.png"), dpi=150)
    plt.close()


def plot_trace_distribution(all_seed_results: dict, minority_mask: Tensor, out_dir: str) -> None:
    # Collect traces at t* across seeds
    min_traces_list, maj_traces_list = [], []
    m = minority_mask.cpu().numpy().astype(bool)
    for s, r in all_seed_results.items():
        traces = r["traces_at_tstar"].cpu().numpy()
        min_traces_list.extend(traces[m].tolist())
        maj_traces_list.extend(traces[~m].tolist())

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.violinplot([min_traces_list, maj_traces_list], positions=[1, 2], showmedians=True)
    ax.set_xticks([1, 2])
    ax.set_xticklabels(["Minority", "Majority"])
    ax.set_ylabel("Hutchinson Trace")
    ax.set_title("Trace Distribution at t* (all seeds)")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig4_trace_distribution.png"), dpi=150)
    plt.close()


def plot_spearman_rising(all_seed_results: dict, out_dir: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    for s, r in all_seed_results.items():
        t_star = r["t_star"]
        epochs = config.CHECKPOINT_EPOCHS
        rising_idx = epochs.index(t_star) + 1
        rising_epochs = epochs[:rising_idx]
        aurocs = [r["checkpoints"][e]["auroc"] for e in rising_epochs]
        ax.scatter(rising_epochs, aurocs, label=f"seed={s} ρ={r['spearman_rho']:.2f}", alpha=0.7)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("AUROC")
    ax.set_title("AUROC vs Epoch (Rising Segment, per Seed)")
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig5_spearman_rising.png"), dpi=150)
    plt.close()
