#!/usr/bin/env python3
"""Experiment Orchestrator for H-M3: Eigenmode Energy Redistribution.

Pipeline:
1. Load config and model (MambaProbe)
2. Apply LoRA (LoRAAdapter), verify A_log frozen
3. Pre-training energy measurement (EigenmodeEnergyAnalyzer)
4. Load data, train
5. Post-training energy measurement
6. Compute ΔE, evaluate gate
7. Compute perplexity (sanity check)
8. Save figures and results.yaml

Gate: SHOULD_WORK (G4)
Pass Condition: ΔE > 0.1 nats (energy shift toward slow eigenmodes)
"""

import os
import sys
from datetime import datetime
from typing import Any, Tuple

import torch
from torch.utils.data import DataLoader

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ExperimentConfig
from model import MambaProbe, LoRAAdapter, EigenmodeEnergyAnalyzer
from train import (
    load_wikitext103_train,
    build_dataloader,
    build_optimizer_and_scheduler,
    train,
)
from evaluate import (
    load_wikitext103_eval,
    compute_perplexity,
    plot_gate_metrics,
    plot_energy_distribution,
    plot_per_layer_slow_fraction,
    plot_eigenvalue_energy_scatter,
    plot_training_loss,
    save_results,
)


def _load_model_and_lora(config: ExperimentConfig) -> Tuple[Any, Any, Any]:
    """Load MambaProbe, apply LoRAAdapter, verify mechanism.

    Args:
        config: Experiment configuration

    Returns:
        (probe, lora_adapter, model)  # model is PEFT-wrapped
    """
    print("\n" + "="*60)
    print("Step 1: Loading Model and Applying LoRA")
    print("="*60)

    # Load model
    probe = MambaProbe(config)
    probe.load_model()

    # Apply LoRA
    lora_adapter = LoRAAdapter(probe.get_model(), config)
    model = lora_adapter.apply()

    # Verify mechanism (A_log frozen, proj LoRA trainable)
    lora_adapter.verify_mechanism()

    return probe, lora_adapter, model


def _measure_energy_pass(
    analyzer: EigenmodeEnergyAnalyzer,
    model: Any,
    eval_dataloader: DataLoader,
    config: ExperimentConfig,
    label: str,
) -> dict:
    """Run analyzer over eval_dataloader batches; average energy dicts.

    Args:
        analyzer: EigenmodeEnergyAnalyzer (hooks registered inside)
        model: PEFT-wrapped Mamba model
        eval_dataloader: batches of input_ids
        config: for device
        label: "pre" or "post" for logging

    Returns:
        averaged measure_energy dict over all batches
    """
    print(f"\n  Measuring {label}-training energy...")

    device = next(model.parameters()).device
    model.eval()

    # Register hooks
    analyzer.register_hooks()

    # Collect energy measurements across batches
    all_per_layer = []
    all_total_energy = []

    num_batches = min(config.num_energy_probe_sequences // config.batch_size, len(eval_dataloader))

    for i, batch in enumerate(eval_dataloader):
        if i >= num_batches:
            break

        input_ids = batch["input_ids"].to(device)
        energy = analyzer.measure_energy(model, input_ids)

        all_per_layer.append(energy['per_layer'])
        all_total_energy.append(energy['per_layer_total_energy'])

    # Average across batches
    num_layers = len(all_per_layer[0])
    avg_per_layer = []
    avg_total_energy = []

    for layer_idx in range(num_layers):
        layer_fracs = [batch[layer_idx] for batch in all_per_layer]
        layer_energies = [batch[layer_idx] for batch in all_total_energy]
        avg_per_layer.append(sum(layer_fracs) / len(layer_fracs))
        avg_total_energy.append(sum(layer_energies) / len(layer_energies))

    avg_slow_fraction = sum(avg_per_layer) / len(avg_per_layer)

    # Clear hooks to free memory
    analyzer.clear_hooks()

    print(f"  {label.capitalize()} slow mode fraction: {avg_slow_fraction:.6f}")

    return {
        'per_layer': avg_per_layer,
        'slow_fraction': avg_slow_fraction,
        'per_layer_total_energy': avg_total_energy,
    }


def main() -> None:
    """Full experiment pipeline."""
    print("\n" + "="*60)
    print("H-M3: Eigenmode Energy Redistribution via Projection-Only LoRA")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. Load configuration
    config = ExperimentConfig()
    print(f"\nConfiguration:")
    print(f"  Model: {config.model_id}")
    print(f"  Slow mode threshold: |λ| > {config.slow_mode_threshold}")
    print(f"  Gate threshold: ΔE > {config.delta_e_gate_threshold} nats")

    # Create output directories
    os.makedirs(config.figures_dir, exist_ok=True)

    # Set random seed
    torch.manual_seed(config.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(config.seed)

    # 2. Load model and apply LoRA
    probe, lora_adapter, model = _load_model_and_lora(config)
    tokenizer = probe.get_tokenizer()

    # 3. Initialize analyzer
    analyzer = EigenmodeEnergyAnalyzer(model, config)

    # 4. Load evaluation data for energy measurement
    print("\n" + "="*60)
    print("Step 2: Loading Evaluation Data")
    print("="*60)
    eval_dataset = load_wikitext103_eval(config, tokenizer)
    eval_dataloader = build_dataloader(eval_dataset, config)

    # 5. Pre-training energy measurement
    print("\n" + "="*60)
    print("Step 3: Pre-Training Energy Measurement")
    print("="*60)
    pre_energy = _measure_energy_pass(analyzer, model, eval_dataloader, config, "pre")

    # 6. Load training data and train
    print("\n" + "="*60)
    print("Step 4: Training")
    print("="*60)
    train_dataset = load_wikitext103_train(config, tokenizer)
    train_dataloader = build_dataloader(train_dataset, config)

    num_training_steps = len(train_dataloader) * config.num_epochs // config.gradient_accumulation_steps
    optimizer, scheduler = build_optimizer_and_scheduler(model, config, num_training_steps)

    losses = train(model, train_dataloader, optimizer, scheduler, config)

    # 7. Post-training energy measurement
    print("\n" + "="*60)
    print("Step 5: Post-Training Energy Measurement")
    print("="*60)
    post_energy = _measure_energy_pass(analyzer, model, eval_dataloader, config, "post")

    # 8. Compute ΔE and evaluate gate
    print("\n" + "="*60)
    print("Step 6: Gate Evaluation")
    print("="*60)
    delta_e_result = analyzer.compute_delta_e(pre_energy, post_energy)

    print(f"\n  Pre-training slow mode fraction:  {pre_energy['slow_fraction']:.6f}")
    print(f"  Post-training slow mode fraction: {post_energy['slow_fraction']:.6f}")
    print(f"  Delta slow fraction: {delta_e_result['delta_slow_fraction']:.6f}")
    print(f"  ΔE (nats): {delta_e_result['delta_e_nats']:.6f}")
    print(f"  Threshold: {config.delta_e_gate_threshold} nats")

    gate_status = "PASS" if delta_e_result['gate_pass'] else "FAIL"
    print(f"\n  {'='*40}")
    print(f"  GATE RESULT: {gate_status}")
    print(f"  {'='*40}")

    # 9. Get eigenvalues for visualization
    eigenvalues = analyzer.get_eigenvalues_per_layer()

    # 10. Compute perplexity (sanity check)
    print("\n" + "="*60)
    print("Step 7: Perplexity Sanity Check")
    print("="*60)
    perplexity = compute_perplexity(model, eval_dataset, config)

    # 11. Generate figures
    print("\n" + "="*60)
    print("Step 8: Generating Figures")
    print("="*60)

    plot_gate_metrics(delta_e_result['delta_e_nats'], config.delta_e_gate_threshold, config.figures_dir)
    plot_energy_distribution(pre_energy, post_energy, config.figures_dir)
    plot_per_layer_slow_fraction(pre_energy, post_energy, config.figures_dir)
    plot_eigenvalue_energy_scatter(eigenvalues, pre_energy, post_energy, config.figures_dir)
    plot_training_loss(losses, config.figures_dir)

    # 12. Save results
    print("\n" + "="*60)
    print("Step 9: Saving Results")
    print("="*60)

    results = {
        'gate_pass': delta_e_result['gate_pass'],
        'delta_e_nats': delta_e_result['delta_e_nats'],
        'delta_slow_fraction': delta_e_result['delta_slow_fraction'],
        'pre_energy': {
            'slow_fraction': pre_energy['slow_fraction'],
            'per_layer': pre_energy['per_layer'],
        },
        'post_energy': {
            'slow_fraction': post_energy['slow_fraction'],
            'per_layer': post_energy['per_layer'],
        },
        'perplexity': perplexity,
        'per_layer_delta': delta_e_result['per_layer_delta'],
        'metadata': {
            'model_id': config.model_id,
            'seed': config.seed,
            'num_train_sequences': config.num_train_sequences,
            'slow_mode_threshold': config.slow_mode_threshold,
            'delta_e_gate_threshold': config.delta_e_gate_threshold,
            'timestamp': datetime.now().isoformat(),
        },
    }

    save_results(results, config.results_path)

    # Final summary
    print("\n" + "="*60)
    print("EXPERIMENT COMPLETE")
    print("="*60)
    print(f"\nGate: {'PASS' if delta_e_result['gate_pass'] else 'FAIL'} "
          f"(ΔE={delta_e_result['delta_e_nats']:.4f} nats, threshold={config.delta_e_gate_threshold})")
    print(f"Pre slow fraction:  {pre_energy['slow_fraction']:.6f}")
    print(f"Post slow fraction: {post_energy['slow_fraction']:.6f}")
    print(f"Perplexity: {perplexity:.2f}")
    print(f"\nResults saved to: {config.results_path}")
    print(f"Figures saved to: {config.figures_dir}/")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
