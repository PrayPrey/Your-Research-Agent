#!/usr/bin/env python3
"""H-E1 Experiment Runner: Task-Dependent Adaptation Transformation Exists"""

import os
import sys
import json
import argparse
from datetime import datetime

import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    BENCHMARKS, LORA_CONFIG_TRANSFORMER, LORA_CONFIG_MAMBA,
    TRAIN_CONFIG, GATE_THRESHOLDS
)
from data import load_benchmark, format_for_causal_lm, get_benchmark_split
from model import (
    load_baseline_model, load_proposed_model, load_tokenizer,
    verify_mechanism_active, MambaWithLoRA
)
from train import train_one_benchmark, run_all_training
from evaluate import (
    evaluate_benchmark, compute_deltas, get_densities,
    spearman_correlation, check_gate_conditions
)
from visualize import (
    plot_gate_metrics_comparison, plot_delta_vs_density, plot_loss_curves
)


def run_experiment(output_dir, skip_training=False, quick_mode=False):
    """Run the full H-E1 experiment."""
    print("=" * 60)
    print("H-E1: Task-Dependent Adaptation Transformation Exists")
    print("=" * 60)
    print(f"Output directory: {output_dir}")
    print(f"Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
    print()

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "checkpoints"), exist_ok=True)
    figures_dir = os.path.join(os.path.dirname(output_dir), "figures")
    os.makedirs(figures_dir, exist_ok=True)

    results = {
        "hypothesis_id": "H-E1",
        "started_at": datetime.now().isoformat(),
        "config": {
            "lora_transformer": LORA_CONFIG_TRANSFORMER,
            "lora_mamba": LORA_CONFIG_MAMBA,
            "train": TRAIN_CONFIG,
            "benchmarks": list(BENCHMARKS.keys()),
        },
    }

    print("[1/6] Loading tokenizer...")
    tokenizer = load_tokenizer()

    print("\n[2/6] Verifying Mamba mechanism...")
    mamba_model = MambaWithLoRA(d_model=256, d_state=16, n_layers=2, vocab_size=32000)
    sample = torch.randint(0, 32000, (1, 32))
    verify_mechanism_active(mamba_model, sample)
    del mamba_model
    results["mechanism_verified"] = True

    transformer_scores = {}
    mamba_scores = {}
    transformer_losses = {}
    mamba_losses = {}

    if not skip_training:
        print("\n[3/6] Training Transformer + LoRA on all benchmarks...")
        transformer_losses = run_all_training(
            load_baseline_model, LORA_CONFIG_TRANSFORMER, tokenizer,
            "transformer", os.path.join(output_dir, "checkpoints")
        )

        print("\n[4/6] Training Mamba + LoRA on all benchmarks...")
        mamba_losses = run_all_training(
            load_proposed_model, LORA_CONFIG_MAMBA, tokenizer,
            "mamba", os.path.join(output_dir, "checkpoints")
        )
    else:
        print("\n[3-4/6] Skipping training (skip_training=True)")

    print("\n[5/6] Evaluating models...")
    eval_samples = 100 if quick_mode else 500

    for name, cfg in BENCHMARKS.items():
        print(f"  Evaluating {name}...")
        ds = load_benchmark(name)
        split = get_benchmark_split(name)
        eval_ds = ds.get(split, ds.get("test", ds.get("validation")))

        if eval_ds is None:
            print(f"    Warning: No eval split for {name}")
            transformer_scores[name] = 0.0
            mamba_scores[name] = 0.0
            continue

        try:
            t_model = load_baseline_model()
            transformer_scores[name] = evaluate_benchmark(
                t_model, tokenizer, eval_ds, cfg["metric"], max_samples=eval_samples
            )
            del t_model
            torch.cuda.empty_cache()
        except Exception as e:
            print(f"    Transformer eval failed: {e}")
            transformer_scores[name] = 0.0

        try:
            m_model = load_proposed_model()
            mamba_scores[name] = evaluate_benchmark(
                m_model, tokenizer, eval_ds, cfg["metric"], max_samples=eval_samples
            )
            del m_model
            torch.cuda.empty_cache()
        except Exception as e:
            print(f"    Mamba eval failed: {e}")
            mamba_scores[name] = 0.0

    print("\n[6/6] Computing results and generating figures...")
    deltas = compute_deltas(transformer_scores, mamba_scores)
    densities = get_densities()
    correlation = spearman_correlation(deltas, densities)
    gate_results = check_gate_conditions(deltas, correlation)

    results["transformer_scores"] = transformer_scores
    results["mamba_scores"] = mamba_scores
    results["deltas"] = deltas
    results["densities"] = densities
    results["correlation"] = correlation
    results["gate_results"] = gate_results
    results["completed_at"] = datetime.now().isoformat()

    plot_gate_metrics_comparison(
        transformer_scores, mamba_scores,
        os.path.join(figures_dir, "gate_metrics_comparison.png")
    )

    plot_delta_vs_density(
        deltas, densities, correlation,
        os.path.join(figures_dir, "delta_vs_density.png")
    )

    if transformer_losses and mamba_losses:
        plot_loss_curves(
            transformer_losses, mamba_losses,
            os.path.join(figures_dir, "loss_curves.png")
        )

    results_path = os.path.join(os.path.dirname(output_dir), "experiment_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_path}")

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Transformer scores: {transformer_scores}")
    print(f"Mamba scores: {mamba_scores}")
    print(f"Deltas: {deltas}")
    print(f"Spearman correlation: {correlation:.4f}")
    print(f"Gate verdict: {gate_results['gate_verdict']}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--skip-training", action="store_true")
    parser.add_argument("--quick", action="store_true", help="Quick mode with fewer samples")
    args = parser.parse_args()

    run_experiment(args.output_dir, args.skip_training, args.quick)
