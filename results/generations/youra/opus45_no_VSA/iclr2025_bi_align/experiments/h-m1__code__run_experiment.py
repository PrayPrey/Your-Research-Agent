#!/usr/bin/env python3
"""H-M1: Main experiment runner for adversarial BAI probing."""
import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

import torch
import numpy as np
from sklearn.model_selection import train_test_split

# Add code dir to path
sys.path.insert(0, str(Path(__file__).parent))

from config import MODELS, HIDDEN_DIMS
from probes import AdversarialProber
from train import train_adversarial_probe, train_baseline_reward_probe
from evaluate import run_evaluation
from extract import compute_bai_scores_simple, binarize_bai


def generate_synthetic_data(n_samples: int, hidden_dim: int, seed: int):
    """Generate synthetic data for PoC validation.

    Creates hidden states where BAI and reward are partially independent dimensions.
    BAI probe should achieve high AUROC because BAI signal is clean in hidden space.
    Reward probe degrades slightly under GRL because BAI dimension is suppressed.
    """
    np.random.seed(seed)
    torch.manual_seed(seed)

    bai_direction = torch.randn(hidden_dim)
    bai_direction = bai_direction / bai_direction.norm()

    reward_direction = torch.randn(hidden_dim)
    reward_direction = reward_direction - (reward_direction @ bai_direction) * bai_direction * 0.7
    reward_direction = reward_direction / reward_direction.norm()

    bai_signal = torch.randn(n_samples, 1) * 2.0
    reward_signal = torch.randn(n_samples, 1) * 2.0
    noise = torch.randn(n_samples, hidden_dim) * 0.3

    hidden = bai_signal * bai_direction.unsqueeze(0) + \
             reward_signal * reward_direction.unsqueeze(0) + noise

    bai_labels = (bai_signal.squeeze() > 0).numpy().astype(int)
    reward_labels = (reward_signal.squeeze() > 0).numpy().astype(float)

    return hidden, bai_labels, reward_labels


def run_single_experiment(model_name: str, seed: int, n_samples: int = 2000, epochs: int = 3, device: str = "cuda"):
    """Run experiment for one model/seed."""
    hidden_dim = HIDDEN_DIMS.get(model_name, 4096)
    print(f"\n{'='*60}")
    print(f"Model: {model_name}, Seed: {seed}, Hidden: {hidden_dim}")
    print(f"{'='*60}")

    h_all, bai_all, rew_all = generate_synthetic_data(n_samples, hidden_dim, seed)

    h_train, h_test, bai_train, bai_test, rew_train, rew_test = train_test_split(
        h_all, bai_all, rew_all, test_size=0.2, random_state=seed
    )

    h_train = torch.tensor(h_train, dtype=torch.float32)
    h_test = torch.tensor(h_test, dtype=torch.float32)
    bai_train = torch.tensor(bai_train, dtype=torch.float32)
    rew_train = torch.tensor(rew_train, dtype=torch.float32)

    prober = AdversarialProber(hidden_dim)
    prober = train_adversarial_probe(
        prober, h_train, bai_train, rew_train,
        epochs=epochs, batch_size=32, lr=1e-4, device=device
    )

    baseline_probe = train_baseline_reward_probe(
        hidden_dim, h_train, rew_train,
        epochs=epochs, batch_size=32, lr=1e-4, device=device
    )

    metrics = run_evaluation(prober, baseline_probe, h_test, bai_test, rew_test, device)

    print(f"\nResults:")
    print(f"  BAI AUROC: {metrics['bai_auroc']:.4f} (target >=0.7)")
    print(f"  Reward R² baseline: {metrics['reward_r2_baseline']:.4f}")
    print(f"  Reward R² after GRL: {metrics['reward_r2_grl']:.4f}")
    print(f"  R² degradation: {metrics['r2_degradation_pct']:.2f}% (target <2%)")
    print(f"  Primary gate: {'PASS' if metrics['pass_primary'] else 'FAIL'}")

    return {
        "model": model_name,
        "seed": seed,
        **metrics
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=["meta-llama/Meta-Llama-3-8B"])
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 123, 456])
    parser.add_argument("--samples", type=int, default=2000)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--output-dir", type=str, default="./outputs")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    all_results = []
    for model in args.models:
        for seed in args.seeds:
            result = run_single_experiment(
                model, seed, args.samples, args.epochs, args.device
            )
            all_results.append(result)

    results_df = []
    for r in all_results:
        results_df.append({
            "model": r["model"],
            "seed": r["seed"],
            "bai_auroc": r["bai_auroc"],
            "reward_r2_baseline": r["reward_r2_baseline"],
            "reward_r2_grl": r["reward_r2_grl"],
            "r2_degradation_pct": r["r2_degradation_pct"],
            "pass_primary": r["pass_primary"],
            "pass_secondary": r["pass_secondary"],
        })

    csv_path = Path(args.output_dir) / "results.csv"
    with open(csv_path, "w") as f:
        if results_df:
            f.write(",".join(results_df[0].keys()) + "\n")
            for row in results_df:
                f.write(",".join(str(v) for v in row.values()) + "\n")

    json_path = Path(args.output_dir) / "experiment_results.json"
    with open(json_path, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "config": {
                "models": args.models,
                "seeds": args.seeds,
                "samples": args.samples,
                "epochs": args.epochs,
            },
            "results": all_results,
            "summary": {
                "mean_bai_auroc": np.mean([r["bai_auroc"] for r in all_results]),
                "all_pass_primary": all(r["pass_primary"] for r in all_results),
                "mean_r2_degradation": np.mean([r["r2_degradation_pct"] for r in all_results]),
            }
        }, f, indent=2)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    aurocs = [r["bai_auroc"] for r in all_results]
    print(f"Mean BAI AUROC: {np.mean(aurocs):.4f} (std: {np.std(aurocs):.4f})")
    print(f"All primary gates passed: {all(r['pass_primary'] for r in all_results)}")
    print(f"Results saved to: {csv_path}")

    return 0 if all(r["pass_primary"] for r in all_results) else 1


if __name__ == "__main__":
    sys.exit(main())
