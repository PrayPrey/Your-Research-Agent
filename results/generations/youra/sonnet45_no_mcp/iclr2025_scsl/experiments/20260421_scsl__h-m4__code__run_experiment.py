#!/usr/bin/env python3
"""Main experiment runner for H-M4 Geometry-Phenotype Coupling"""

import os
import sys
import logging
import torch
import numpy as np
from pathlib import Path

# Add code directory to path
CODE_DIR = Path(__file__).parent
sys.path.insert(0, str(CODE_DIR))

from config import ExperimentConfig
from data.waterbirds import get_waterbirds_dataloader
from data.models import get_resnet50
from experiments.coupling_experiment import CouplingExperiment
from experiments.train_endpoints import train_erm, train_dro


def setup_logging(log_file: str = "logs/experiment.log"):
    """Setup logging configuration"""
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def prepare_checkpoints(config, train_loader, val_loader, logger):
    """
    Prepare ERM and DRO checkpoints.
    Train them if they don't exist.
    """
    erm_path = Path("checkpoints/erm_final.pt")
    dro_path = Path("checkpoints/dro_final.pt")

    # Train ERM if needed
    if not erm_path.exists():
        logger.info("ERM checkpoint not found. Training ERM model...")
        erm_model = get_resnet50(num_classes=2, pretrained=True)
        train_erm(
            erm_model,
            train_loader,
            val_loader,
            device=config.compute.device,
            epochs=config.training.epochs,
            lr=config.training.lr,
            weight_decay=config.training.weight_decay,
            save_path=str(erm_path)
        )
        logger.info(f"ERM model saved to {erm_path}")
    else:
        logger.info(f"Using existing ERM checkpoint: {erm_path}")

    # Train DRO if needed
    if not dro_path.exists():
        logger.info("DRO checkpoint not found. Training DRO model...")
        dro_model = get_resnet50(num_classes=2, pretrained=True)
        train_dro(
            dro_model,
            train_loader,
            val_loader,
            device=config.compute.device,
            epochs=config.training.epochs,
            lr=config.training.lr,
            weight_decay=config.training.weight_decay,
            alpha=config.training.dro_alpha,
            save_path=str(dro_path)
        )
        logger.info(f"DRO model saved to {dro_path}")
    else:
        logger.info(f"Using existing DRO checkpoint: {dro_path}")

    return str(erm_path), str(dro_path)


def generate_validation_report(config, results, gate_result, output_path: str):
    """Generate Phase 4 validation report"""

    report = f"""# Phase 4 Validation Report: H-M4 Geometry-Phenotype Coupling

**Hypothesis:** {config.description}
**Gate Type:** {config.gate_type}
**Date:** {Path(output_path).stat().st_mtime}

---

## Executive Summary

**Gate Result:** {gate_result['result']}

**Key Finding:** {gate_result['message']}

---

## Results

### FGE Path

- **Spearman ρ:** {results.fge_rho:.4f}
- **p-value:** {results.fge_p_value:.6f}
- **Samples:** {len(results.alignment_values_fge)}

### Linear Path

- **Spearman ρ:** {results.linear_rho:.4f}
- **p-value:** {results.linear_p_value:.6f}
- **Samples:** {len(results.alignment_values_linear)}

---

## Gate Evaluation

**Success Criteria (SHOULD_WORK):**

1. **Primary:** FGE ρ < {config.success_criteria.primary_threshold} AND p < {config.success_criteria.p_value_threshold}
   - **Status:** {'✓ PASS' if gate_result['primary_passed'] else '✗ FAIL'}
   - **Actual:** ρ = {results.fge_rho:.4f}, p = {results.fge_p_value:.6f}

2. **Secondary:** Linear ρ < {config.success_criteria.secondary_threshold} AND p < {config.success_criteria.p_value_threshold}
   - **Status:** {'✓ PASS' if gate_result['secondary_passed'] else '✗ FAIL'}
   - **Actual:** ρ = {results.linear_rho:.4f}, p = {results.linear_p_value:.6f}

**Overall Gate Result:** {gate_result['result']}

---

## Interpretation

### FGE Path
- Alignment range: [{results.alignment_values_fge.min():.4f}, {results.alignment_values_fge.max():.4f}]
- WGA range: [{results.wga_values_fge.min():.4f}, {results.wga_values_fge.max():.4f}]
- Correlation strength: {'Strong' if abs(results.fge_rho) > 0.6 else 'Moderate' if abs(results.fge_rho) > 0.3 else 'Weak'}

### Linear Path
- Alignment range: [{results.alignment_values_linear.min():.4f}, {results.alignment_values_linear.max():.4f}]
- WGA range: [{results.wga_values_linear.min():.4f}, {results.wga_values_linear.max():.4f}]
- Correlation strength: {'Strong' if abs(results.linear_rho) > 0.6 else 'Moderate' if abs(results.linear_rho) > 0.3 else 'Weak'}

---

## Visualizations

1. `figures/coupling_scatter_fge.png` - FGE path coupling scatter plot
2. `figures/coupling_scatter_linear.png` - Linear path coupling scatter plot
3. `figures/trajectory_fge.png` - Metric evolution along FGE path
4. `figures/path_comparison.png` - FGE vs Linear comparison

---

## Conclusion

{gate_result['message']}

Gate evaluation: **{gate_result['result']}**

---

*Generated by Phase 4 Validation Pipeline*
"""

    with open(output_path, 'w') as f:
        f.write(report)


def main():
    """Main experiment execution"""

    # Setup
    logger = setup_logging()
    logger.info("=" * 80)
    logger.info("H-M4 Geometry-Phenotype Coupling Experiment")
    logger.info("=" * 80)

    # Set random seed
    torch.manual_seed(42)
    np.random.seed(42)

    # Create default config
    config = ExperimentConfig()
    config.validate()

    logger.info(f"Device: {config.compute.device}")
    logger.info(f"Path sampling: {config.path_sampling.num_samples} samples")
    logger.info(f"Dataset: {config.dataset.name} at {config.dataset.path}")

    # Load data
    logger.info("Loading Waterbirds dataset...")
    train_loader = get_waterbirds_dataloader(
        root_dir=config.dataset.path,
        split="train",
        batch_size=config.dataloader.batch_size,
        shuffle=True,
        num_workers=config.dataloader.num_workers
    )

    val_loader = get_waterbirds_dataloader(
        root_dir=config.dataset.path,
        split="val",
        batch_size=config.dataloader.batch_size,
        shuffle=False,
        num_workers=config.dataloader.num_workers
    )

    logger.info(f"Train batches: {len(train_loader)}")
    logger.info(f"Val batches: {len(val_loader)}")

    # Prepare checkpoints
    erm_checkpoint, dro_checkpoint = prepare_checkpoints(
        config, train_loader, val_loader, logger
    )

    # Run coupling experiment
    logger.info("Starting coupling experiment...")
    experiment = CouplingExperiment(config)
    results = experiment.run(train_loader, val_loader, erm_checkpoint, dro_checkpoint)

    # Evaluate gate
    gate_result = experiment.evaluate_gate(results)
    logger.info(f"Gate Result: {gate_result['result']}")
    logger.info(f"Message: {gate_result['message']}")

    # Generate validation report
    report_path = "04_validation.md"
    generate_validation_report(config, results, gate_result, report_path)
    logger.info(f"Validation report saved to {report_path}")

    # Summary
    logger.info("=" * 80)
    logger.info("EXPERIMENT COMPLETE")
    logger.info(f"Gate Result: {gate_result['result']}")
    logger.info(f"FGE ρ: {results.fge_rho:.4f} (p={results.fge_p_value:.6f})")
    logger.info(f"Linear ρ: {results.linear_rho:.4f} (p={results.linear_p_value:.6f})")
    logger.info("=" * 80)

    return gate_result['result']


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result in ["PASS", "PARTIAL"] else 1)
