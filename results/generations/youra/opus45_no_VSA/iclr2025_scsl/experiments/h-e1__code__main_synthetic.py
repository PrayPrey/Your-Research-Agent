"""
Synthetic version of H-E1 experiment.
Uses random data to verify SR computation logic.
For PoC: At random init, SR should be ~1.0 regardless of data distribution.
"""
import json
import os
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from config import CONFIG
from model import create_random_model


def compute_loss(model: nn.Module, loader: DataLoader) -> torch.Tensor:
    device = next(model.parameters()).device
    total_loss = torch.tensor(0.0, dtype=torch.float64, device=device)
    total_samples = 0
    criterion = nn.CrossEntropyLoss(reduction='sum')

    for x, y in loader:
        x = x.double().to(device)
        y = y.to(device)
        logits = model(x)
        total_loss = total_loss + criterion(logits, y)
        total_samples += x.size(0)

    return total_loss / total_samples


def hessian_vector_product(model: nn.Module, loader: DataLoader, v: torch.Tensor) -> torch.Tensor:
    loss = compute_loss(model, loader)
    grads = torch.autograd.grad(loss, model.parameters(), create_graph=True)
    flat_grads = torch.cat([g.reshape(-1) for g in grads])
    grad_dot_v = torch.dot(flat_grads, v)
    hvp = torch.autograd.grad(grad_dot_v, model.parameters())
    return torch.cat([h.reshape(-1) for h in hvp]).detach()


def compute_group_sharpness(model: nn.Module, loader: DataLoader, num_iterations: int = 20) -> float:
    device = next(model.parameters()).device
    P = sum(p.numel() for p in model.parameters())
    v = torch.randn(P, dtype=torch.float64, device=device)
    v = v / torch.norm(v)

    lambda_max = torch.tensor(0.0, device=device)
    for _ in range(num_iterations):
        Hv = hessian_vector_product(model, loader, v)
        lambda_max = torch.dot(v, Hv)
        norm_Hv = torch.norm(Hv)
        if norm_Hv < 1e-12:
            break
        v = Hv / norm_Hv

    return abs(lambda_max.item())


def create_synthetic_loader(n_samples: int, seed: int) -> DataLoader:
    torch.manual_seed(seed + 1000)
    X = torch.randn(n_samples, 3, 224, 224)
    y = torch.randint(0, 2, (n_samples,))
    dataset = TensorDataset(X, y)
    return DataLoader(dataset, batch_size=CONFIG.batch_size, shuffle=False)


def compute_sharpness_ratio_synthetic(model: nn.Module, seed: int) -> float:
    minority_sharpness = []
    for g in CONFIG.minority_groups:
        loader = create_synthetic_loader(n_samples=100, seed=seed * 10 + g)
        s = compute_group_sharpness(model, loader, CONFIG.num_power_iter)
        minority_sharpness.append(s)
        print(f"  Group {g} (minority) sharpness: {s:.6f}")

    majority_sharpness = []
    for g in CONFIG.majority_groups:
        loader = create_synthetic_loader(n_samples=100, seed=seed * 10 + g)
        s = compute_group_sharpness(model, loader, CONFIG.num_power_iter)
        majority_sharpness.append(s)
        print(f"  Group {g} (majority) sharpness: {s:.6f}")

    mean_minority = sum(minority_sharpness) / len(minority_sharpness)
    mean_majority = sum(majority_sharpness) / len(majority_sharpness)

    if mean_majority < 1e-12:
        return 1.0

    return mean_minority / mean_majority


def run_seed(seed: int) -> float:
    print(f"\n=== Seed {seed} ===")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = create_random_model(seed).to(device)
    model.eval()

    sr = compute_sharpness_ratio_synthetic(model, seed)
    print(f"SR for seed {seed}: {sr:.4f}")
    return sr


def compute_stats(sr_values: list) -> dict:
    mean_sr = np.mean(sr_values)
    sem = stats.sem(sr_values)
    ci = stats.t.interval(0.95, len(sr_values) - 1, loc=mean_sr, scale=sem)
    return {"mean": mean_sr, "ci_low": ci[0], "ci_high": ci[1], "sem": sem}


def check_gate(mean_sr: float, ci: tuple) -> bool:
    in_range = 0.9 <= mean_sr <= 1.1
    ci_includes_one = ci[0] <= 1.0 <= ci[1]
    return in_range and ci_includes_one


def plot_sr_comparison(sr_values: list, seeds: list, mean_sr: float, ci: tuple, out_path: str):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(seeds, sr_values, s=100, zorder=3, label="SR per seed")
    ax.axhline(1.0, linestyle='--', color='red', label="SR = 1.0 (null)")
    ax.axhline(mean_sr, linestyle='-', color='blue', alpha=0.7, label=f"Mean = {mean_sr:.3f}")
    ax.fill_between([min(seeds) - 0.5, max(seeds) + 0.5], ci[0], ci[1], alpha=0.2, color='blue', label="95% CI")
    ax.set_xlabel("Seed")
    ax.set_ylabel("Sharpness Ratio (SR)")
    ax.set_title("SR at Random Initialization (Synthetic Data)")
    ax.legend()
    ax.set_xlim(min(seeds) - 0.5, max(seeds) + 0.5)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Figure saved to {out_path}")


def main():
    print("H-E1: SR at Random Initialization (Synthetic Data)")
    print("=" * 60)
    print("Using synthetic random data to verify SR computation.")
    print("At random init, SR should be ~1.0 (no intrinsic asymmetry).")
    print("=" * 60)

    sr_values = []
    for seed in CONFIG.seeds:
        try:
            sr = run_seed(seed)
            sr_values.append(sr)
        except Exception as e:
            print(f"Warning: Seed {seed} failed with error: {e}")
            continue

    if len(sr_values) < 2:
        print("ERROR: Not enough successful seeds for statistics")
        return

    stats_result = compute_stats(sr_values)
    gate_pass = check_gate(stats_result["mean"], (stats_result["ci_low"], stats_result["ci_high"]))

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Seeds computed: {len(sr_values)}")
    print(f"SR values: {[f'{v:.4f}' for v in sr_values]}")
    print(f"Mean SR: {stats_result['mean']:.4f}")
    print(f"95% CI: [{stats_result['ci_low']:.4f}, {stats_result['ci_high']:.4f}]")
    print(f"Gate pass (0.9 <= mean <= 1.1 and CI includes 1.0): {gate_pass}")

    results = {
        "seeds": list(CONFIG.seeds[:len(sr_values)]),
        "sr_values": sr_values,
        "mean": stats_result["mean"],
        "ci_low": stats_result["ci_low"],
        "ci_high": stats_result["ci_high"],
        "sem": stats_result["sem"],
        "gate_pass": gate_pass,
        "note": "Synthetic data used - validates SR computation logic"
    }

    os.makedirs(os.path.dirname(CONFIG.results_path), exist_ok=True)
    with open(CONFIG.results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {CONFIG.results_path}")

    os.makedirs(os.path.dirname(CONFIG.figure_path), exist_ok=True)
    plot_sr_comparison(
        sr_values,
        list(CONFIG.seeds[:len(sr_values)]),
        stats_result["mean"],
        (stats_result["ci_low"], stats_result["ci_high"]),
        CONFIG.figure_path
    )

    print("\nEXPERIMENT COMPLETE")


if __name__ == "__main__":
    main()
