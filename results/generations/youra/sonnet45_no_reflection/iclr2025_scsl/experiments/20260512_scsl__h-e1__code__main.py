"""Main experiment runner for h-e1 SCSL experiment."""
import torch
import numpy as np
import random
import os
import json
from transformers import GPT2Config

from config import get_baseline_config, get_proposed_config, get_implicit_control_config
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
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def load_baseline_ppl(checkpoint_dir: str) -> float:
    """Load baseline perplexity from checkpoint."""
    logs_path = os.path.join(checkpoint_dir, "training_logs.json")
    if os.path.exists(logs_path):
        with open(logs_path, 'r') as f:
            logs = json.load(f)
            # Get final perplexity
            for log in reversed(logs):
                if 'perplexity' in log:
                    return log['perplexity']
    return None


def run_experiment(variant: str, config) -> dict:
    """Run single variant experiment. variant: 'baseline', 'proposed', 'implicit_control'"""
    print(f"\n{'='*80}")
    print(f"Running {variant.upper()} experiment")
    print(f"{'='*80}\n")

    # Setup
    setup_environment(config.training.seed)

    # Create dataloaders
    print("Loading C4 dataset...")
    train_loader, val_loader = create_dataloaders(config)

    # Create model
    print(f"Initializing {variant} model...")
    model_config = GPT2Config(
        vocab_size=config.model.vocab_size,
        n_positions=config.model.n_positions,
        n_embd=config.model.n_embd,
        n_layer=config.model.n_layer,
        n_head=config.model.n_head,
        n_inner=config.model.n_inner,
        activation_function=config.model.activation_function,
        resid_pdrop=config.model.resid_pdrop,
        embd_pdrop=config.model.embd_pdrop,
        attn_pdrop=config.model.attn_pdrop,
        layer_norm_epsilon=config.model.layer_norm_epsilon,
        initializer_range=config.model.initializer_range
    )

    if variant == "baseline" or variant == "implicit_control":
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
    print(f"Starting training for {config.total_steps} steps...")
    trainer = GPT2Trainer(model, train_loader, val_loader, config, variant)

    # Load baseline PPL if training proposed model
    baseline_ppl = None
    if variant == "proposed":
        baseline_ppl = load_baseline_ppl("checkpoints/baseline/")
        if baseline_ppl:
            print(f"Loaded baseline perplexity: {baseline_ppl:.2f}")

    trainer.train(config.total_steps, baseline_ppl=baseline_ppl)

    # Evaluate
    print(f"\nEvaluating {variant} model...")
    evaluator = MetricsEvaluator(model, val_loader, device=config.device)
    results = evaluator.evaluate_all()

    # Add training logs
    results['training_logs'] = trainer.training_logs

    # Save results
    results_dir = os.path.join(config.output_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    results_path = os.path.join(results_dir, f"{variant}_results.json")

    # Convert numpy types for JSON serialization
    def convert_to_serializable(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_serializable(item) for item in obj]
        return obj

    results_serializable = convert_to_serializable(results)

    with open(results_path, 'w') as f:
        json.dump(results_serializable, f, indent=2)

    print(f"Results saved: {results_path}")
    print(f"\nFinal metrics for {variant}:")
    print(f"  Perplexity: {results['perplexity']:.2f}")
    print(f"  Mean Stable Rank: {results['mean_stable_rank']:.2f}")
    print(f"  Layer Variance (CV): {results['layer_variance']:.3f}")
    print(f"  Measurement CV: {results['measurement_cv']:.3f}")

    return results


def compare_variants(results: dict) -> dict:
    """Compare baseline vs proposed vs implicit control."""
    baseline = results.get('baseline', {})
    proposed = results.get('proposed', {})

    baseline_sr = baseline.get('mean_stable_rank', 0)
    proposed_sr = proposed.get('mean_stable_rank', 0)
    sr_reduction = (baseline_sr - proposed_sr) / baseline_sr if baseline_sr > 0 else 0

    baseline_ppl = baseline.get('perplexity', 0)
    proposed_ppl = proposed.get('perplexity', 0)
    ppl_deviation = abs(proposed_ppl - baseline_ppl) / baseline_ppl if baseline_ppl > 0 else 0

    comparison = {
        'stable_rank_reduction': sr_reduction,
        'perplexity_deviation': ppl_deviation,
        'baseline_sr': baseline_sr,
        'proposed_sr': proposed_sr,
        'baseline_ppl': baseline_ppl,
        'proposed_ppl': proposed_ppl,
        'proposed_layer_variance': proposed.get('layer_variance', 0),
        'proposed_measurement_cv': proposed.get('measurement_cv', 0)
    }

    return comparison


def validate_gate_criteria(comparison: dict, config) -> bool:
    """Validate gate criteria (MUST_WORK). Returns True if gate passes."""
    sr_reduction = comparison['stable_rank_reduction']
    ppl_deviation = comparison['perplexity_deviation']
    layer_variance = comparison['proposed_layer_variance']
    measurement_cv = comparison['proposed_measurement_cv']

    targets = config.evaluation

    gate_pass = (
        sr_reduction >= targets.target_sr_reduction and
        ppl_deviation <= targets.target_ppl_deviation and
        layer_variance < targets.target_layer_variance_ratio and
        measurement_cv < targets.target_measurement_cv
    )

    print(f"\n{'='*80}")
    print("GATE VALIDATION (MUST_WORK)")
    print(f"{'='*80}")
    print(f"1. Stable Rank Reduction: {sr_reduction*100:.1f}% (target: ≥{targets.target_sr_reduction*100:.0f}%) {'✓' if sr_reduction >= targets.target_sr_reduction else '✗'}")
    print(f"2. Perplexity Deviation: {ppl_deviation*100:.2f}% (target: ≤{targets.target_ppl_deviation*100:.0f}%) {'✓' if ppl_deviation <= targets.target_ppl_deviation else '✗'}")
    print(f"3. Layer Variance: {layer_variance:.2f} (target: <{targets.target_layer_variance_ratio:.1f}x) {'✓' if layer_variance < targets.target_layer_variance_ratio else '✗'}")
    print(f"4. Measurement CV: {measurement_cv:.3f} (target: <{targets.target_measurement_cv:.2f}) {'✓' if measurement_cv < targets.target_measurement_cv else '✗'}")
    print(f"\nGate Result: {'PASS ✓' if gate_pass else 'FAIL ✗'}")
    print(f"{'='*80}\n")

    return gate_pass


def main():
    """Main experiment orchestration."""
    print("\n" + "="*80)
    print("H-E1 EXPERIMENT: Jacobian Stable Rank Regularization")
    print("="*80 + "\n")

    # Check GPU availability
    if torch.cuda.is_available():
        print(f"CUDA available: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB\n")
    else:
        print("WARNING: CUDA not available, running on CPU (will be very slow)\n")

    all_results = {}

    # Run baseline
    baseline_config = get_baseline_config()
    all_results['baseline'] = run_experiment('baseline', baseline_config)

    # Run proposed
    proposed_config = get_proposed_config()
    all_results['proposed'] = run_experiment('proposed', proposed_config)

    # Run implicit control
    implicit_config = get_implicit_control_config()
    all_results['implicit_control'] = run_experiment('implicit_control', implicit_config)

    # Compare results
    comparison = compare_variants(all_results)

    # Validate gate
    gate_pass = validate_gate_criteria(comparison, proposed_config)

    # Generate visualizations
    print("\nGenerating visualizations...")
    visualizer = ExperimentVisualizer(results_dir="figures")
    visualizer.save_all_figures(all_results)

    # Save gate validation report
    gate_report = {
        'gate_type': 'MUST_WORK',
        'gate_pass': gate_pass,
        'comparison': comparison,
        'timestamp': str(torch.cuda.Event(enable_timing=False))
    }

    report_path = "results/gate_validation.json"
    os.makedirs("results", exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(gate_report, f, indent=2)

    print(f"Gate validation report saved: {report_path}")
    print("\nEXPERIMENT COMPLETE")

    return gate_pass


if __name__ == "__main__":
    gate_pass = main()
    exit(0 if gate_pass else 1)
