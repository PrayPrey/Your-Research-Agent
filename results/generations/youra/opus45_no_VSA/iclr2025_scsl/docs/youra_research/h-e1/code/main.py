import json
import os
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import torch

from config import CONFIG
from model import create_random_model
from data import WaterbirdDataset
from sharpness import compute_sharpness_ratio


def run_seed(seed: int, dataset: WaterbirdDataset) -> float:
    print(f"\n=== Seed {seed} ===")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = create_random_model(seed).to(device)
    model.eval()

    with torch.no_grad():
        sr = compute_sharpness_ratio(model, dataset)

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
    ax.set_title("SR at Random Initialization")
    ax.legend()
    ax.set_xlim(min(seeds) - 0.5, max(seeds) + 0.5)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Figure saved to {out_path}")


def main():
    print("Loading Waterbirds dataset...")
    dataset = WaterbirdDataset(CONFIG.data_root, split="train")
    print(f"Dataset size: {len(dataset)}")

    sr_values = []
    for seed in CONFIG.seeds:
        try:
            sr = run_seed(seed, dataset)
            sr_values.append(sr)
        except Exception as e:
            print(f"Warning: Seed {seed} failed with error: {e}")
            continue

    if len(sr_values) < 2:
        print("ERROR: Not enough successful seeds for statistics")
        return

    stats_result = compute_stats(sr_values)
    gate_pass = check_gate(stats_result["mean"], (stats_result["ci_low"], stats_result["ci_high"]))

    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    print(f"Seeds computed: {len(sr_values)}")
    print(f"SR values: {sr_values}")
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
        "gate_pass": gate_pass
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
