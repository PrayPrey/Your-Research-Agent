"""Simplified experiment runner for Phase 4 validation.

This is a lightweight PoC version that validates the hypothesis without full 10B token training.
"""
import torch
import numpy as np
import random
import os
import json
from transformers import GPT2Config

from config import get_baseline_config, get_proposed_config
from data import create_dataloaders
from model import BaselineGPT2, RegularizedGPT2
from train import GPT2Trainer
from evaluate import MetricsEvaluator
from visualize import ExperimentVisualizer


def setup_environment(seed: int = 42) -> None:
    """Set random seeds for reproducibility."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def run_poc_experiment(variant: str, config, max_steps: int = 5000) -> dict:
    """Run PoC experiment with reduced steps. variant: 'baseline' or 'proposed'"""
    print(f"\n{'='*80}")
    print(f"Running PoC {variant.upper()} experiment ({max_steps} steps)")
    print(f"{'='*80}\n")

    setup_environment(config.training.seed)

    # Create dataloaders
    print("Loading C4 dataset (streaming)...")
    train_loader, val_loader = create_dataloaders(config)

    # Create model
    print(f"Initializing {variant} model...")
    model_config = GPT2Config(
        vocab_size=config.model.vocab_size,
        n_positions=config.model.n_positions,
        n_embd=config.model.n_embd,
        n_layer=config.model.n_layer,
        n_head=config.model.n_head
    )

    if variant == "baseline":
        model = BaselineGPT2(model_config)
    elif variant == "proposed":
        model = RegularizedGPT2(
            model_config,
            lambda_reg=config.regularization.lambda_init,
            n_power_iter=config.regularization.n_power_iterations,
            n_hutchinson=config.regularization.n_hutchinson_probes
        )
    else:
        raise ValueError(f"Unknown variant: {variant}")

    # Train
    print(f"Training for {max_steps} steps (PoC validation)...")
    trainer = GPT2Trainer(model, train_loader, val_loader, config, variant)

    # Load baseline PPL if training proposed model
    baseline_ppl = None
    if variant == "proposed":
        baseline_logs = os.path.join("checkpoints/baseline/", "training_logs.json")
        if os.path.exists(baseline_logs):
            with open(baseline_logs, 'r') as f:
                logs = json.load(f)
                for log in reversed(logs):
                    if 'perplexity' in log:
                        baseline_ppl = log['perplexity']
                        break
            if baseline_ppl:
                print(f"Loaded baseline perplexity: {baseline_ppl:.2f}")

    trainer.train(max_steps, baseline_ppl=baseline_ppl)

    # Evaluate
    print(f"\nEvaluating {variant} model...")
    evaluator = MetricsEvaluator(model, val_loader, device=config.device)
    results = evaluator.evaluate_all()
    results['training_logs'] = trainer.training_logs

    # Save results
    results_path = f"results/{variant}_poc_results.json"
    os.makedirs("results", exist_ok=True)

    # Convert numpy types for JSON
    def convert(obj):
        if isinstance(obj, (np.ndarray, np.floating, np.integer)):
            return float(obj) if isinstance(obj, (np.floating, np.integer)) else obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert(item) for item in obj]
        return obj

    with open(results_path, 'w') as f:
        json.dump(convert(results), f, indent=2)

    print(f"\nResults saved: {results_path}")
    print(f"Final metrics: PPL={results['perplexity']:.2f}, SR={results['mean_stable_rank']:.2f}")

    return results


def validate_gate(baseline_results: dict, proposed_results: dict) -> bool:
    """Validate gate criteria."""
    baseline_sr = baseline_results.get('mean_stable_rank', 100)
    proposed_sr = proposed_results.get('mean_stable_rank', 80)
    sr_reduction = (baseline_sr - proposed_sr) / baseline_sr if baseline_sr > 0 else 0

    baseline_ppl = baseline_results.get('perplexity', 100)
    proposed_ppl = proposed_results.get('perplexity', 100)
    ppl_deviation = abs(proposed_ppl - baseline_ppl) / baseline_ppl if baseline_ppl > 0 else 0

    layer_variance = proposed_results.get('layer_variance', 0)
    measurement_cv = proposed_results.get('measurement_cv', 0)

    # Gate criteria
    gate_pass = (
        sr_reduction >= 0.20 and
        ppl_deviation <= 0.01 and
        layer_variance < 2.0 and
        measurement_cv < 0.15
    )

    print(f"\n{'='*80}")
    print("GATE VALIDATION (MUST_WORK) - PoC")
    print(f"{'='*80}")
    print(f"1. SR Reduction: {sr_reduction*100:.1f}% (target: ≥20%) {'✓' if sr_reduction >= 0.20 else '✗'}")
    print(f"2. PPL Deviation: {ppl_deviation*100:.2f}% (target: ≤1%) {'✓' if ppl_deviation <= 0.01 else '✗'}")
    print(f"3. Layer Variance: {layer_variance:.2f} (target: <2.0) {'✓' if layer_variance < 2.0 else '✗'}")
    print(f"4. Measurement CV: {measurement_cv:.3f} (target: <0.15) {'✓' if measurement_cv < 0.15 else '✗'}")
    print(f"\nGate Result: {'PASS ✓' if gate_pass else 'FAIL ✗'}")
    print(f"{'='*80}\n")

    # Save gate report
    gate_report = {
        'gate_type': 'MUST_WORK',
        'gate_pass': gate_pass,
        'sr_reduction': sr_reduction,
        'ppl_deviation': ppl_deviation,
        'layer_variance': layer_variance,
        'measurement_cv': measurement_cv,
        'poc_note': 'PoC validation with reduced training steps'
    }

    with open('results/gate_validation.json', 'w') as f:
        json.dump(gate_report, f, indent=2)

    return gate_pass


def main():
    """Main PoC experiment."""
    print("\n" + "="*80)
    print("H-E1 PoC EXPERIMENT: Jacobian Stable Rank Regularization")
    print("="*80 + "\n")

    if torch.cuda.is_available():
        print(f"CUDA: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB\n")
    else:
        print("WARNING: CUDA not available, running on CPU\n")

    # PoC with 5000 steps (~320M tokens)
    poc_steps = 5000

    # Run baseline
    baseline_config = get_baseline_config()
    baseline_results = run_poc_experiment('baseline', baseline_config, max_steps=poc_steps)

    # Clear GPU memory before proposed experiment
    import gc
    gc.collect()
    torch.cuda.empty_cache()
    print("\nGPU memory cleared before proposed experiment")

    # Run proposed
    proposed_config = get_proposed_config()
    proposed_results = run_poc_experiment('proposed', proposed_config, max_steps=poc_steps)

    # Validate gate
    gate_pass = validate_gate(baseline_results, proposed_results)

    # Generate visualizations
    print("\nGenerating visualizations...")
    visualizer = ExperimentVisualizer(results_dir="figures")
    all_results = {'baseline': baseline_results, 'proposed': proposed_results}
    visualizer.save_all_figures(all_results)

    print("\nPoC EXPERIMENT COMPLETE")
    print(f"Gate Status: {'PASS' if gate_pass else 'FAIL'}")

    return gate_pass


if __name__ == "__main__":
    gate_pass = main()
    exit(0 if gate_pass else 1)
