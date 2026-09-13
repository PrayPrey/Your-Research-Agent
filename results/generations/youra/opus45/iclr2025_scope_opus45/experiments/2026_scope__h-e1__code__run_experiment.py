#!/usr/bin/env python3
"""Run H-E1 Experiment: Spectral Memory Horizon Stability Measurement.

This script measures whether H_spec = -1/log|λ_max| is a stable property
of pretrained Mamba models with CV < 0.3 across random input sequences.

Usage:
    python run_experiment.py
"""

import os
import sys

# Add code directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from transformers import AutoTokenizer

from config import ExperimentConfig
from evaluate import (
    generate_figures,
    generate_random_sequences,
    measure_h_spec_distribution,
    run_scale_crossvalidation,
    save_results,
)
from model import MambaProbe


def main() -> None:
    """Orchestrate full experiment pipeline."""
    print("=" * 60)
    print("H-E1: Spectral Memory Horizon Stability Experiment")
    print("=" * 60)

    # 1. Build ExperimentConfig
    config = ExperimentConfig()
    print(f"\nConfiguration:")
    print(f"  Model: {config.model_id}")
    print(f"  Samples: {config.num_samples}")
    print(f"  Seq Length: {config.seq_length}")
    print(f"  CV Threshold: {config.cv_threshold}")
    print(f"  Device: {config.device}")

    # Ensure figures directory exists
    os.makedirs(config.figures_dir, exist_ok=True)

    # 2. Load tokenizer and generate random sequences
    print("\n--- Loading Tokenizer ---")
    tokenizer = AutoTokenizer.from_pretrained(config.tokenizer_id)
    vocab_size = tokenizer.vocab_size
    print(f"Tokenizer loaded: vocab_size={vocab_size}")

    print("\n--- Generating Random Sequences ---")
    sequences = generate_random_sequences(config, vocab_size)

    # 3. Load MambaProbe
    print("\n--- Loading Model ---")
    probe = MambaProbe(config)
    probe.load_model(config.model_id)

    # 4. Measure H_spec distribution
    print("\n--- Measuring H_spec Distribution ---")
    metrics = measure_h_spec_distribution(probe, sequences, config)

    print(f"\n--- Results ---")
    print(f"  Mean H_spec: {metrics['mean']:.4f} tokens")
    print(f"  Std H_spec: {metrics['std']:.6f}")
    print(f"  CV: {metrics['cv']:.6f}")
    print(f"  Valid samples: {metrics['valid_samples']}/{config.num_samples}")

    # 5. Run scale cross-validation (optional but recommended)
    print("\n--- Scale Cross-Validation ---")
    probe.unload()  # Free memory before loading another model
    crossval = run_scale_crossvalidation(config)
    print(f"  H_spec (370M): {crossval['mean_h_spec_370m']:.4f} tokens")
    print(f"  H_spec (1.4B): {metrics['mean']:.4f} tokens")

    # 6. Save results
    print("\n--- Saving Results ---")
    save_results(metrics, crossval, config)

    # 7. Generate figures
    print("\n--- Generating Figures ---")
    generate_figures(metrics, crossval, config)

    # 8. Print gate verdict
    print("\n" + "=" * 60)
    gate_result = "PASS" if metrics["pass_gate"] else "FAIL"
    print(f"GATE VERDICT: {gate_result}")
    print(f"CV = {metrics['cv']:.6f} {'<' if metrics['pass_gate'] else '>='} {config.cv_threshold}")
    print("=" * 60)

    # Return appropriate exit code
    sys.exit(0 if metrics["pass_gate"] else 1)


if __name__ == "__main__":
    main()
