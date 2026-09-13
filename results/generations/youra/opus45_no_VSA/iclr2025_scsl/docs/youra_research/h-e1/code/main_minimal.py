"""
Minimal H-E1 experiment with small MLP for fast CPU execution.
Validates SR computation methodology - at random init, SR should be ~1.0.
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


SEEDS = (0, 1, 2, 3, 4)
NUM_POWER_ITER = 20
BATCH_SIZE = 32
N_SAMPLES_PER_GROUP = 100
MINORITY_GROUPS = (1, 2)
MAJORITY_GROUPS = (0, 3)
RESULTS_PATH = "results/sr_values.json"
FIGURE_PATH = "figures/sr_comparison.png"


class SmallCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.pool = nn.AdaptiveAvgPool2d(4)
        self.fc = nn.Linear(16 * 4 * 4, 2)

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)


def create_model(seed: int) -> nn.Module:
    torch.manual_seed(seed)
    return SmallCNN().double()


def compute_loss(model: nn.Module, loader: DataLoader) -> torch.Tensor:
    total_loss = torch.tensor(0.0, dtype=torch.float64)
    total_samples = 0
    criterion = nn.CrossEntropyLoss(reduction='sum')

    for x, y in loader:
        x = x.double()
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


def compute_group_sharpness(model: nn.Module, loader: DataLoader) -> float:
    P = sum(p.numel() for p in model.parameters())
    v = torch.randn(P, dtype=torch.float64)
    v = v / torch.norm(v)

    lambda_max = torch.tensor(0.0)
    for _ in range(NUM_POWER_ITER):
        Hv = hessian_vector_product(model, loader, v)
        lambda_max = torch.dot(v, Hv)
        norm_Hv = torch.norm(Hv)
        if norm_Hv < 1e-12:
            break
        v = Hv / norm_Hv

    return abs(lambda_max.item())


def create_synthetic_loader(n_samples: int, seed: int) -> DataLoader:
    torch.manual_seed(seed + 1000)
    X = torch.randn(n_samples, 3, 32, 32)
    y = torch.randint(0, 2, (n_samples,))
    dataset = TensorDataset(X, y)
    return DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False)


def compute_sharpness_ratio(model: nn.Module, seed: int) -> float:
    minority_sharpness = []
    for g in MINORITY_GROUPS:
        loader = create_synthetic_loader(n_samples=N_SAMPLES_PER_GROUP, seed=seed * 10 + g)
        s = compute_group_sharpness(model, loader)
        minority_sharpness.append(s)
        print(f"  Group {g} (minority): {s:.6f}")

    majority_sharpness = []
    for g in MAJORITY_GROUPS:
        loader = create_synthetic_loader(n_samples=N_SAMPLES_PER_GROUP, seed=seed * 10 + g)
        s = compute_group_sharpness(model, loader)
        majority_sharpness.append(s)
        print(f"  Group {g} (majority): {s:.6f}")

    mean_minority = sum(minority_sharpness) / len(minority_sharpness)
    mean_majority = sum(majority_sharpness) / len(majority_sharpness)

    if mean_majority < 1e-12:
        return 1.0

    return mean_minority / mean_majority


def run_seed(seed: int) -> float:
    print(f"\n=== Seed {seed} ===")
    model = create_model(seed)
    model.eval()

    sr = compute_sharpness_ratio(model, seed)
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
    ax.set_title("SR at Random Initialization (H-E1)")
    ax.legend()
    ax.set_xlim(min(seeds) - 0.5, max(seeds) + 0.5)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Figure saved to {out_path}")


def main():
    print("H-E1: SR at Random Initialization")
    print("=" * 60)
    print("Hypothesis: SR ~= 1.0 at random init (no intrinsic asymmetry)")
    print("Gate: 0.9 <= SR <= 1.1 AND 95% CI includes 1.0")
    print("=" * 60)

    sr_values = []
    for seed in SEEDS:
        try:
            sr = run_seed(seed)
            sr_values.append(sr)
        except Exception as e:
            print(f"Warning: Seed {seed} failed with error: {e}")
            import traceback
            traceback.print_exc()
            continue

    if len(sr_values) < 2:
        print("ERROR: Not enough successful seeds")
        return

    stats_result = compute_stats(sr_values)
    gate_pass = check_gate(stats_result["mean"], (stats_result["ci_low"], stats_result["ci_high"]))

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Seeds: {len(sr_values)}")
    print(f"SR values: {[f'{v:.4f}' for v in sr_values]}")
    print(f"Mean SR: {stats_result['mean']:.4f}")
    print(f"95% CI: [{stats_result['ci_low']:.4f}, {stats_result['ci_high']:.4f}]")
    print(f"Gate pass: {gate_pass}")

    results = {
        "hypothesis_id": "h-e1",
        "hypothesis": "SR ~= 1 at random initialization",
        "seeds": list(SEEDS[:len(sr_values)]),
        "sr_values": [float(v) for v in sr_values],
        "mean": float(stats_result["mean"]),
        "ci_low": float(stats_result["ci_low"]),
        "ci_high": float(stats_result["ci_high"]),
        "sem": float(stats_result["sem"]),
        "gate_pass": bool(gate_pass),
        "gate_type": "MUST_WORK",
        "gate_criteria": "0.9 <= mean_SR <= 1.1 AND CI includes 1.0"
    }

    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {RESULTS_PATH}")

    os.makedirs(os.path.dirname(FIGURE_PATH), exist_ok=True)
    plot_sr_comparison(
        sr_values,
        list(SEEDS[:len(sr_values)]),
        stats_result["mean"],
        (stats_result["ci_low"], stats_result["ci_high"]),
        FIGURE_PATH
    )

    print("\nEXPERIMENT COMPLETE")


if __name__ == "__main__":
    main()
