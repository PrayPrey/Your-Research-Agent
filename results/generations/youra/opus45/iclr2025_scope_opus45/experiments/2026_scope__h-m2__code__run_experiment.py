#!/usr/bin/env python3
"""Run H-M2 Experiment: Projection-Only LoRA Eigenvalue Preservation.

This experiment validates that projection-only LoRA preserves SSM eigenvalues
(|ΔH_spec| < 10%) after fine-tuning on WikiText-103.

MUST_WORK Gate: |ΔH_spec| < 10%
- Projection-only LoRA should NOT modify A_log parameters
- H_spec (eigenvalue-derived memory horizon) should remain unchanged

Usage:
    python run_experiment.py
"""

import os
import sys
import logging

# Add code directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ExperimentConfig
from evaluate import (
    compute_perplexity,
    generate_figures,
    load_wikitext103_valid,
    save_results,
)
from model import (
    EigenvaluePreservationValidator,
    LoRAAdapter,
    MambaProbe,
)
from train import (
    build_dataloader,
    build_optimizer_and_scheduler,
    load_wikitext103_train,
    train,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('experiment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main(config: ExperimentConfig = None) -> dict:
    """Orchestrate full H-M2 experiment pipeline.

    Pipeline:
    1. Load Mamba-1.4B via MambaProbe
    2. Extract baseline A_log tensors
    3. Verify baseline H_spec ~ 256.18
    4. Apply projection-only LoRA via LoRAAdapter
    5. Run verify_mechanism() - confirm A_log frozen
    6. Load WikiText-103 train split
    7. Fine-tune for 3 epochs
    8. Extract post-training A_log tensors
    9. Validate eigenvalue preservation
    10. Compute validation perplexity
    11. Generate figures
    12. Save results.yaml with gate verdict

    Args:
        config: Experiment configuration (uses default if None)

    Returns:
        Results dictionary with all metrics
    """
    if config is None:
        config = ExperimentConfig()

    logger.info("=" * 60)
    logger.info("H-M2: Projection-Only LoRA Eigenvalue Preservation")
    logger.info("=" * 60)

    logger.info("\nConfiguration:")
    logger.info(f"  Model: {config.model_id}")
    logger.info(f"  Dataset: {config.dataset_name}/{config.dataset_config}")
    logger.info(f"  LoRA r: {config.lora_r}, alpha: {config.lora_alpha}")
    logger.info(f"  Target modules: {config.lora_target_modules}")
    logger.info(f"  Epochs: {config.num_epochs}")
    logger.info(f"  Learning rate: {config.learning_rate}")
    logger.info(f"  H_spec (known): {config.h_spec_known}")
    logger.info(f"  Gate: |ΔH_spec| < {config.delta_h_spec_threshold}%")
    logger.info(f"  Device: {config.device}")

    # Ensure output directories exist
    os.makedirs(config.figures_dir, exist_ok=True)
    os.makedirs(config.checkpoint_dir, exist_ok=True)

    # =========================================================================
    # Step 1: Load Model
    # =========================================================================
    logger.info("\n--- Step 1: Loading Mamba-1.4B ---")
    probe = MambaProbe(config)
    probe.load_model()

    # =========================================================================
    # Step 2: Extract Baseline A_log Tensors
    # =========================================================================
    logger.info("\n--- Step 2: Extracting Baseline A_log ---")
    baseline_a_logs = probe.extract_layer_A_log()
    logger.info(f"  Extracted {len(baseline_a_logs)} layer A_log tensors")
    logger.info(f"  Shape per layer: {baseline_a_logs[0].shape}")

    # =========================================================================
    # Step 3: Compute Baseline H_spec
    # =========================================================================
    logger.info("\n--- Step 3: Computing Baseline H_spec ---")
    baseline_h_spec = probe.compute_h_spec()
    per_layer_baseline_h_spec = probe.get_per_layer_h_spec()

    logger.info(f"  Computed H_spec: {baseline_h_spec:.2f} tokens")
    logger.info(f"  Expected H_spec: {config.h_spec_known:.2f} tokens")
    logger.info(f"  Difference: {abs(baseline_h_spec - config.h_spec_known):.2f} tokens")

    # =========================================================================
    # Step 4: Apply Projection-Only LoRA
    # =========================================================================
    logger.info("\n--- Step 4: Applying Projection-Only LoRA ---")
    base_model = probe.get_model()
    tokenizer = probe.get_tokenizer()

    adapter = LoRAAdapter(base_model, config)
    peft_model = adapter.apply()

    trainable_params = adapter.get_trainable_param_count()
    total_params = sum(p.numel() for p in peft_model.parameters())
    logger.info(f"  Trainable params: {trainable_params:,} ({100*trainable_params/total_params:.2f}%)")

    # =========================================================================
    # Step 5: Verify Mechanism (A_log Frozen)
    # =========================================================================
    logger.info("\n--- Step 5: Verifying Mechanism ---")
    try:
        adapter.verify_mechanism()
        logger.info("  Mechanism verification PASSED")
    except AssertionError as e:
        logger.error(f"  Mechanism verification FAILED: {e}")
        raise

    # =========================================================================
    # Step 6: Load WikiText-103 Training Data
    # =========================================================================
    logger.info("\n--- Step 6: Loading WikiText-103 Training Data ---")
    train_dataset = load_wikitext103_train(config, tokenizer)
    train_dataloader = build_dataloader(train_dataset, config)
    logger.info(f"  Training batches: {len(train_dataloader)}")

    # =========================================================================
    # Step 7: Fine-tune for 3 Epochs
    # =========================================================================
    logger.info("\n--- Step 7: Fine-tuning ---")

    # Calculate total training steps
    num_update_steps = len(train_dataloader) // config.gradient_accumulation_steps
    num_training_steps = num_update_steps * config.num_epochs

    optimizer, scheduler = build_optimizer_and_scheduler(
        peft_model, config, num_training_steps
    )

    train_losses = train(
        peft_model, train_dataloader, optimizer, scheduler, config
    )
    logger.info(f"  Training complete. Final loss: {train_losses[-1]:.4f}")

    # =========================================================================
    # Step 8: Extract Post-Training A_log Tensors
    # =========================================================================
    logger.info("\n--- Step 8: Extracting Post-Training A_log ---")

    # Update probe model reference (PEFT model wraps base model)
    probe.model = peft_model
    post_a_logs = probe.extract_layer_A_log()
    logger.info(f"  Extracted {len(post_a_logs)} layer A_log tensors")

    per_layer_post_h_spec = probe.get_per_layer_h_spec()

    # =========================================================================
    # Step 9: Validate Eigenvalue Preservation
    # =========================================================================
    logger.info("\n--- Step 9: Validating Eigenvalue Preservation ---")
    validator = EigenvaluePreservationValidator(
        baseline_a_logs, post_a_logs, config
    )
    preservation_metrics = validator.validate()

    logger.info(f"  Baseline H_spec: {preservation_metrics['baseline_h_spec']:.2f}")
    logger.info(f"  Post-training H_spec: {preservation_metrics['post_h_spec']:.2f}")
    logger.info(f"  |ΔH_spec|: {preservation_metrics['delta_h_spec_percent']:.4f}%")
    logger.info(f"  Eigenvalue correlation: {preservation_metrics['eigenvalue_correlation']:.6f}")
    logger.info(f"  A_log max diff: {preservation_metrics['a_log_max_diff']:.2e}")
    logger.info(f"  A_log frozen: {preservation_metrics['a_log_frozen']}")

    # =========================================================================
    # Step 10: Compute Validation Perplexity (Secondary Metric)
    # =========================================================================
    logger.info("\n--- Step 10: Computing Validation Perplexity ---")
    valid_dataset = load_wikitext103_valid(config, tokenizer)
    val_perplexity = compute_perplexity(peft_model, tokenizer, valid_dataset, config)
    logger.info(f"  Validation perplexity: {val_perplexity:.2f}")

    # =========================================================================
    # Step 11: Generate Figures
    # =========================================================================
    logger.info("\n--- Step 11: Generating Figures ---")
    figure_paths = generate_figures(
        baseline_a_logs,
        post_a_logs,
        preservation_metrics,
        train_losses,
        per_layer_baseline_h_spec,
        per_layer_post_h_spec,
        config.figures_dir,
    )

    # =========================================================================
    # Step 12: Compile and Save Results
    # =========================================================================
    logger.info("\n--- Step 12: Saving Results ---")

    gate_pass = preservation_metrics['hypothesis_pass']

    results = {
        "hypothesis": "h-m2",
        "status": "PASS" if gate_pass else "FAIL",
        "gate": "MUST_WORK",

        # Model info
        "model_id": config.model_id,
        "dataset": f"{config.dataset_name}/{config.dataset_config}",

        # LoRA config
        "lora_config": {
            "r": config.lora_r,
            "alpha": config.lora_alpha,
            "target_modules": config.lora_target_modules,
            "dropout": config.lora_dropout,
        },

        # Training info
        "training": {
            "epochs": config.num_epochs,
            "batch_size": config.batch_size,
            "learning_rate": config.learning_rate,
            "gradient_accumulation": config.gradient_accumulation_steps,
            "warmup_steps": config.warmup_steps,
            "final_loss": train_losses[-1],
            "num_training_steps": len(train_losses),
        },

        # H_spec metrics
        "metrics": {
            "h_spec_pre": preservation_metrics['baseline_h_spec'],
            "h_spec_post": preservation_metrics['post_h_spec'],
            "delta_h_spec_percent": preservation_metrics['delta_h_spec_percent'],
            "eigenvalue_correlation": preservation_metrics['eigenvalue_correlation'],
            "a_log_max_diff": preservation_metrics['a_log_max_diff'],
            "a_log_frozen": preservation_metrics['a_log_frozen'],
            "val_perplexity": val_perplexity,
        },

        # Gate evaluation
        "gate_result": {
            "delta_h_spec_pass": preservation_metrics['delta_h_spec_pass'],
            "eigenvalue_corr_pass": preservation_metrics['eigenvalue_corr_pass'],
            "overall_pass": gate_pass,
            "threshold": config.delta_h_spec_threshold,
        },

        # Figures
        "figures": figure_paths,

        # Interpretation
        "interpretation": preservation_metrics['interpretation'],
    }

    save_results(results, config.results_path)

    # =========================================================================
    # Cleanup
    # =========================================================================
    logger.info("\n--- Cleanup ---")
    probe.unload()

    # =========================================================================
    # Final Verdict
    # =========================================================================
    logger.info("\n" + "=" * 60)
    gate_result = "PASS" if gate_pass else "FAIL"
    logger.info(f"GATE VERDICT: {gate_result}")
    logger.info(f"|ΔH_spec| = {preservation_metrics['delta_h_spec_percent']:.4f}% {'<' if gate_pass else '>='} {config.delta_h_spec_threshold}%")
    logger.info(f"Eigenvalue correlation = {preservation_metrics['eigenvalue_correlation']:.6f}")

    if gate_pass:
        logger.info("Projection-only LoRA PRESERVES eigenvalues!")
        logger.info("SSM core (A_log) remains frozen during LoRA fine-tuning.")
    else:
        logger.info("Projection-only LoRA MODIFIES eigenvalues!")
        logger.info("Hypothesis failed - LoRA unexpectedly affects SSM core.")
    logger.info("=" * 60)

    return results


if __name__ == "__main__":
    import torch
    torch.manual_seed(42)

    config = ExperimentConfig()
    results = main(config)
    sys.exit(0 if results["gate_result"]["overall_pass"] else 1)
