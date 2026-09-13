#!/usr/bin/env python3
"""Run H-M1 Experiment: SSM Eigenvalue Memory Horizon Empirical Validation.

This experiment validates that eigenvalue-derived H_spec predicts actual
perplexity degradation on real text (WikiText-103).

MUST_WORK Gate: Degradation ratio > 1.1
- Perplexity should be higher when context < H_spec
- Perplexity should plateau when context >= H_spec

Usage:
    python run_experiment.py
"""

import os
import sys

# Add code directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ExperimentConfig
from evaluate import (
    compute_context_lengths,
    generate_figures,
    load_wikitext103,
    prepare_eval_sequences,
    save_results,
)
from model import MambaProbe, PerplexityEvaluator


def main(config: ExperimentConfig = None) -> dict:
    """Orchestrate full experiment pipeline.

    Args:
        config: Experiment configuration (uses default if None)

    Returns:
        Results dictionary with all metrics
    """
    if config is None:
        config = ExperimentConfig()

    print("=" * 60)
    print("H-M1: SSM Eigenvalue Memory Horizon Empirical Validation")
    print("=" * 60)

    print(f"\nConfiguration:")
    print(f"  Model: {config.model_id}")
    print(f"  Dataset: {config.dataset_name}/{config.dataset_config}")
    print(f"  Eval Sequences: {config.num_eval_sequences}")
    print(f"  Max Seq Length: {config.max_seq_length}")
    print(f"  H_spec (known): {config.h_spec_known}")
    print(f"  Gate Threshold: {config.degradation_ratio_threshold}")
    print(f"  Device: {config.device}")

    # Ensure output directories exist
    os.makedirs(config.figures_dir, exist_ok=True)

    # =========================================================================
    # Step 1: Load Dataset
    # =========================================================================
    print("\n--- Loading WikiText-103 ---")
    dataset = load_wikitext103(config)

    # =========================================================================
    # Step 2: Load Model and Tokenizer
    # =========================================================================
    print("\n--- Loading Model ---")
    probe = MambaProbe(config)
    probe.load_model(config.model_id)

    # =========================================================================
    # Step 3: Compute H_spec from Eigenvalues
    # =========================================================================
    print("\n--- Computing H_spec from Eigenvalues ---")
    h_spec = probe.compute_h_spec()
    per_layer_h_specs = probe.get_per_layer_h_spec()
    per_layer_lambda_max = probe.get_per_layer_lambda_max()

    print(f"  Computed H_spec: {h_spec:.2f} tokens")
    print(f"  Expected H_spec: {config.h_spec_known:.2f} tokens")
    print(f"  Difference: {abs(h_spec - config.h_spec_known):.2f} tokens")

    # =========================================================================
    # Step 4: Prepare Evaluation Sequences
    # =========================================================================
    print("\n--- Preparing Evaluation Sequences ---")
    sequences = prepare_eval_sequences(dataset, probe.tokenizer, config)

    # =========================================================================
    # Step 5: Run Context Sweep
    # =========================================================================
    print("\n--- Running Context Sweep ---")
    context_lengths = compute_context_lengths(
        h_spec,
        config.context_length_multipliers,
        min_tokens=16
    )
    print(f"Context lengths: {context_lengths}")

    evaluator = PerplexityEvaluator(
        probe.model,
        probe.tokenizer,
        config.device,
        config.dtype,
    )

    ppl_curve = evaluator.run_context_sweep(sequences, context_lengths)

    # =========================================================================
    # Step 6: Compute Degradation Ratio
    # =========================================================================
    print("\n--- Computing Degradation Ratio ---")
    degradation_ratio = evaluator.compute_degradation_ratio(ppl_curve, h_spec)
    print(f"  Degradation Ratio: {degradation_ratio:.4f}")
    print(f"  Threshold: {config.degradation_ratio_threshold}")

    # =========================================================================
    # Step 7: Determine Gate Result
    # =========================================================================
    gate_pass = degradation_ratio > config.degradation_ratio_threshold

    # Check baseline perplexity (full context)
    max_ctx = max(ppl_curve.keys())
    baseline_ppl = ppl_curve[max_ctx]
    ppl_in_range = abs(baseline_ppl - config.baseline_ppl_expected) / config.baseline_ppl_expected < config.baseline_ppl_tolerance

    print(f"\n--- Gate Evaluation ---")
    print(f"  Baseline PPL: {baseline_ppl:.2f} (expected: {config.baseline_ppl_expected} ± {config.baseline_ppl_tolerance*100}%)")
    print(f"  PPL in range: {ppl_in_range}")
    print(f"  Degradation ratio > {config.degradation_ratio_threshold}: {gate_pass}")

    # =========================================================================
    # Step 8: Compile Results
    # =========================================================================
    results = {
        "hypothesis": "h-m1",
        "model_id": config.model_id,
        "dataset": f"{config.dataset_name}/{config.dataset_config}",
        "num_eval_sequences": config.num_eval_sequences,
        "max_seq_length": config.max_seq_length,
        "seed": config.seed,
        # H_spec
        "h_spec": h_spec,
        "h_spec_expected": config.h_spec_known,
        "per_layer_h_specs": per_layer_h_specs,
        "per_layer_lambda_max": per_layer_lambda_max,
        # Perplexity curve
        "ppl_curve": {str(k): v for k, v in ppl_curve.items()},
        "context_lengths": context_lengths,
        # Gate metrics
        "degradation_ratio": degradation_ratio,
        "degradation_threshold": config.degradation_ratio_threshold,
        "baseline_ppl": baseline_ppl,
        "baseline_ppl_expected": config.baseline_ppl_expected,
        "baseline_ppl_in_range": ppl_in_range,
        # Gate result
        "gate_pass": gate_pass,
        "gate_type": "MUST_WORK",
        # Figures
        "figures": [
            f"{config.figures_dir}/ppl_vs_context_length.png",
            f"{config.figures_dir}/gate_metrics_bar.png",
            f"{config.figures_dir}/per_layer_eigenvalues.png",
            f"{config.figures_dir}/decay_rate_profile.png",
        ],
    }

    # =========================================================================
    # Step 9: Save Results and Generate Figures
    # =========================================================================
    print("\n--- Saving Results ---")
    save_results(results, config.results_path)

    print("\n--- Generating Figures ---")
    generate_figures(
        ppl_curve,
        h_spec,
        degradation_ratio,
        per_layer_h_specs,
        config.figures_dir,
    )

    # =========================================================================
    # Step 10: Cleanup
    # =========================================================================
    print("\n--- Cleanup ---")
    probe.unload()

    # =========================================================================
    # Final Verdict
    # =========================================================================
    print("\n" + "=" * 60)
    gate_result = "PASS" if gate_pass else "FAIL"
    print(f"GATE VERDICT: {gate_result}")
    print(f"Degradation Ratio = {degradation_ratio:.4f} {'>' if gate_pass else '<='} {config.degradation_ratio_threshold}")
    if gate_pass:
        print("Eigenvalue-derived H_spec DOES predict perplexity degradation!")
    else:
        print("Eigenvalue-derived H_spec does NOT predict perplexity degradation.")
    print("=" * 60)

    return results


if __name__ == "__main__":
    config = ExperimentConfig()
    results = main(config)
    sys.exit(0 if results["gate_pass"] else 1)
