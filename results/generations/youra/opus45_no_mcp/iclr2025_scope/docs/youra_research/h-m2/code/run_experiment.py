"""Main experiment runner for H-M2: Task-Specific Sharpness Comparison"""

import os
import sys
import json
import torch
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import GATE_THRESHOLD, SHARPNESS_CONFIG, TRAIN_CONFIG
from model import load_tokenizer
from data import load_task_loader
from finetune import finetune_on_task
from sharpness import measure_task_sharpness, compare_task_sharpness
from gate import evaluate_gate, verify_mechanism
from visualize import plot_gate_comparison, plot_sharpness_distribution


def main(output_dir: str = None, epochs: int = None, max_batches: int = None):
    """
    Run H-M2 experiment:
    1. Fine-tune Mamba+LoRA on GSM8K and NQ separately
    2. Measure SAM sharpness for each task
    3. Compute ratio and evaluate gate
    4. Generate visualizations
    """
    if output_dir is None:
        output_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    figures_dir = os.path.join(output_dir, "figures")
    checkpoints_dir = os.path.join(output_dir, "checkpoints")
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(checkpoints_dir, exist_ok=True)

    train_config = TRAIN_CONFIG.copy()
    if epochs is not None:
        train_config["epochs"] = epochs

    sharpness_batches = max_batches if max_batches else SHARPNESS_CONFIG["max_batches"]

    print("=" * 60)
    print("H-M2: Task-Specific Sharpness Comparison")
    print("=" * 60)
    print(f"Train config: {train_config}")
    print(f"Sharpness batches: {sharpness_batches}")
    print(f"Gate threshold: {GATE_THRESHOLD}")
    print()

    print("[1/6] Loading tokenizer...")
    tokenizer = load_tokenizer()
    print(f"  Tokenizer loaded, vocab_size={tokenizer.vocab_size}")

    print("\n[2/6] Fine-tuning on GSM8K (sequential)...")
    gsm8k_out = finetune_on_task("gsm8k", tokenizer, train_config, checkpoints_dir)
    print(f"  GSM8K training complete. Final loss: {gsm8k_out['loss_curve'][-1]:.4f}")

    print("\n[3/6] Fine-tuning on NQ (retrieval)...")
    nq_out = finetune_on_task("nq", tokenizer, train_config, checkpoints_dir)
    print(f"  NQ training complete. Final loss: {nq_out['loss_curve'][-1]:.4f}")

    print("\n[4/6] Measuring sharpness...")
    gsm8k_loader = load_task_loader("gsm8k", tokenizer)
    nq_loader = load_task_loader("nq", tokenizer)

    print("  Measuring GSM8K sharpness...")
    gsm8k_sharp = measure_task_sharpness(gsm8k_out["model"], gsm8k_loader, max_batches=sharpness_batches)
    print(f"  GSM8K mean sharpness: {gsm8k_sharp['mean_sharpness']:.6f}")

    print("  Measuring NQ sharpness...")
    nq_sharp = measure_task_sharpness(nq_out["model"], nq_loader, max_batches=sharpness_batches)
    print(f"  NQ mean sharpness: {nq_sharp['mean_sharpness']:.6f}")

    print("\n[5/6] Evaluating gate...")
    comparison = compare_task_sharpness(gsm8k_sharp, nq_sharp)
    gate_result = evaluate_gate(comparison, GATE_THRESHOLD)
    mechanism_check = verify_mechanism(comparison)

    print(f"  Sequential sharpness: {gate_result['sequential_sharpness']:.6f}")
    print(f"  Retrieval sharpness: {gate_result['retrieval_sharpness']:.6f}")
    print(f"  Ratio: {gate_result['ratio']:.4f} (threshold: <{GATE_THRESHOLD})")
    print(f"  Gate: {'PASS' if gate_result['pass'] else 'FAIL'}")
    print(f"  Mechanism check: {mechanism_check[1]}")

    print("\n[6/6] Generating figures...")
    plot_gate_comparison(
        gate_result["sequential_sharpness"],
        gate_result["retrieval_sharpness"],
        GATE_THRESHOLD,
        os.path.join(figures_dir, "gate_comparison.png")
    )
    plot_sharpness_distribution(
        gsm8k_sharp["per_batch"],
        nq_sharp["per_batch"],
        os.path.join(figures_dir, "sharpness_dist.png")
    )

    results = {
        "hypothesis_id": "h-m2",
        "timestamp": datetime.now().isoformat(),
        "gate_result": {
            "ratio": gate_result["ratio"],
            "pass": gate_result["pass"],
            "threshold": GATE_THRESHOLD,
            "sequential_sharpness": gate_result["sequential_sharpness"],
            "retrieval_sharpness": gate_result["retrieval_sharpness"],
        },
        "mechanism_check": {
            "passed": mechanism_check[0],
            "message": mechanism_check[1],
        },
        "training": {
            "gsm8k_loss_curve": gsm8k_out["loss_curve"],
            "nq_loss_curve": nq_out["loss_curve"],
        },
        "sharpness": {
            "gsm8k_mean": gsm8k_sharp["mean_sharpness"],
            "nq_mean": nq_sharp["mean_sharpness"],
            "gsm8k_std": float(torch.tensor(gsm8k_sharp["per_batch"]).std()) if gsm8k_sharp["per_batch"] else 0,
            "nq_std": float(torch.tensor(nq_sharp["per_batch"]).std()) if nq_sharp["per_batch"] else 0,
        },
        "figures": [
            os.path.join(figures_dir, "gate_comparison.png"),
            os.path.join(figures_dir, "sharpness_dist.png"),
        ],
    }

    results_path = os.path.join(output_dir, "experiment_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_path}")

    print("\n" + "=" * 60)
    print(f"H-M2 EXPERIMENT COMPLETE")
    print(f"Gate verdict: {'PASS' if gate_result['pass'] else 'FAIL'}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-M2 Experiment Runner")
    parser.add_argument("--output-dir", type=str, default=None)
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--max-batches", type=int, default=None)
    args = parser.parse_args()

    main(output_dir=args.output_dir, epochs=args.epochs, max_batches=args.max_batches)
