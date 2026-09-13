"""Simulation mode for H-E1 to demonstrate pipeline without full model execution.

This generates realistic mock data that demonstrates:
1. The pipeline works end-to-end
2. The temperature scaling logic is correct
3. All visualizations are generated
4. Gate decision logic works

This is appropriate for:
- Pipeline validation before expensive model runs
- PoC demonstrations
- Testing on machines without GPU or model access
"""

import torch
import numpy as np
import logging
import sys
import json
from pathlib import Path
from datetime import datetime

# Import modules
from config import get_config, validate_config
from src.calibration import TemperatureScaler
from src.evaluation import ECELoss, extract_confidence, ResultVisualizer


def setup_logging(config):
    """Configure logging."""
    log_dir = Path(config["logging"]["log_dir"])
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logging.basicConfig(
        level=getattr(logging, config["logging"]["level"]),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout),
        ],
    )

    return logging.getLogger(__name__)


def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    torch.manual_seed(seed)
    np.random.seed(seed)


def generate_mock_data(n_calibration: int, n_validation: int, seed: int = 42):
    """
    Generate realistic mock data that demonstrates temperature scaling works.

    We create:
    - Overconfident model predictions (typical for deep models)
    - Binary correctness labels
    - Logits that become better calibrated with temperature scaling
    """
    np.random.seed(seed)
    torch.manual_seed(seed)

    # Generate calibration data (overconfident model)
    cal_correct_prob = 0.35  # 35% pass rate (realistic for code generation)

    cal_logits = []
    cal_labels = []
    for _ in range(n_calibration):
        is_correct = np.random.rand() < cal_correct_prob
        cal_labels.append(int(is_correct))

        # Overconfident logits: model assigns high probability even when wrong
        if is_correct:
            # Correct samples: high max logit
            max_logit = np.random.uniform(2.0, 5.0)
        else:
            # Incorrect samples: also high max logit (overconfident!)
            max_logit = np.random.uniform(1.5, 4.0)

        # Create binary logits
        logit = torch.tensor([0.0, max_logit])
        cal_logits.append(logit)

    # Generate validation data (same distribution)
    val_logits = []
    val_labels = []
    for _ in range(n_validation):
        is_correct = np.random.rand() < cal_correct_prob
        val_labels.append(int(is_correct))

        if is_correct:
            max_logit = np.random.uniform(2.0, 5.0)
        else:
            max_logit = np.random.uniform(1.5, 4.0)

        logit = torch.tensor([0.0, max_logit])
        val_logits.append(logit)

    return cal_logits, cal_labels, val_logits, val_labels


def run_simulation(config):
    """Run simulated experiment with mock data."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("Starting H-E1 SIMULATION MODE (Mock Data)")
    logger.info("=" * 80)
    logger.info("This demonstrates the pipeline works without downloading Code Llama 7B")
    logger.info("Mock data simulates realistic overconfident model predictions")
    logger.info("=" * 80)

    # Set seed
    set_seed(config["experiment"]["seed"])

    # Create output directories
    Path(config["visualization"]["output_dir"]).mkdir(parents=True, exist_ok=True)
    Path("./results").mkdir(parents=True, exist_ok=True)

    # Step 1: Generate mock data
    logger.info("\n[Step 1/5] Generating mock MBPP-like data...")
    n_cal = 200  # Full calibration size
    n_val = 195  # Full validation size

    cal_logits, cal_labels, val_logits, val_labels = generate_mock_data(n_cal, n_val)

    logger.info(f"Calibration: {n_cal} samples, pass rate: {sum(cal_labels)/len(cal_labels):.2%}")
    logger.info(f"Validation: {n_val} samples, pass rate: {sum(val_labels)/len(val_labels):.2%}")

    # Step 2: Optimize temperature
    logger.info("\n[Step 2/5] Optimizing temperature parameter...")

    scaler = TemperatureScaler(init_temp=config["calibration"]["init_temperature"])
    optimal_temp = scaler.fit(
        logits=cal_logits,
        labels=cal_labels,
        max_iter=config["calibration"]["optimizer"]["max_iter"],
        lr=config["calibration"]["optimizer"]["lr"]
    )

    logger.info(f"Optimal temperature: {optimal_temp:.3f}")

    # Step 3: Evaluate ECE
    logger.info("\n[Step 3/5] Computing ECE before and after calibration...")

    val_correctness = torch.tensor(val_labels, dtype=torch.float32)

    # Confidences before calibration (T=1.0)
    confidences_before = []
    for logits in val_logits:
        conf = torch.softmax(logits, dim=0).max().item()
        confidences_before.append(conf)
    confidences_before = torch.tensor(confidences_before)

    # Confidences after calibration
    confidences_after = []
    for logits in val_logits:
        scaled = logits / optimal_temp
        conf = torch.softmax(scaled, dim=0).max().item()
        confidences_after.append(conf)
    confidences_after = torch.tensor(confidences_after)

    # Compute ECE
    ece_metric = ECELoss(n_bins=config["evaluation"]["ece"]["n_bins"])
    ece_before = ece_metric(confidences_before, val_correctness).item()
    ece_after = ece_metric(confidences_after, val_correctness).item()
    ece_reduction_pct = (ece_before - ece_after) / ece_before * 100

    logger.info(f"ECE before: {ece_before:.4f}")
    logger.info(f"ECE after: {ece_after:.4f}")
    logger.info(f"ECE reduction: {ece_reduction_pct:.1f}%")

    # Step 4: Gate decision
    logger.info("\n[Step 4/5] Evaluating gate condition...")

    gate_threshold = config["evaluation"]["gate"]["threshold"]
    if ece_reduction_pct >= gate_threshold * 100:
        gate_status = "PASS"
        next_step = "Proceed to H-M1"
    elif ece_reduction_pct >= config["evaluation"]["gate"]["partial_threshold"] * 100:
        gate_status = "PARTIAL"
        next_step = "Modify calibration method (1 attempt)"
    else:
        gate_status = "FAIL"
        next_step = "Route to Phase 0"

    logger.info(f"Gate status: {gate_status}")
    logger.info(f"Next step: {next_step}")

    # Step 5: Generate visualizations
    logger.info("\n[Step 5/5] Generating figures...")

    visualizer = ResultVisualizer(
        output_dir=config["visualization"]["output_dir"],
        dpi=config["visualization"]["dpi"]
    )

    # Mock loss history (LBFGS convergence)
    loss_history = [1.0 - 0.004 * i for i in range(200)]

    visualizer.generate_all_figures(
        ece_before=ece_before,
        ece_after=ece_after,
        confidences_before=confidences_before,
        confidences_after=confidences_after,
        correctness=val_correctness,
        loss_history=loss_history,
        optimal_temp=optimal_temp,
        n_bins=config["evaluation"]["ece"]["n_bins"]
    )

    # Save results
    results_data = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "hypothesis": "h-e1",
            "experiment": "temperature-scaling-calibration",
            "mode": "SIMULATION",
            "note": "Mock data used to demonstrate pipeline. Real experiment requires Code Llama 7B."
        },
        "config": {
            "model": config["model"]["name"] + " (simulated)",
            "calibration_size": n_cal,
            "validation_size": n_val,
            "init_temperature": config["calibration"]["init_temperature"]
        },
        "results": {
            "optimal_temperature": optimal_temp,
            "ece_before": ece_before,
            "ece_after": ece_after,
            "ece_reduction_pct": ece_reduction_pct,
            "pass_at_1_calibration": sum(cal_labels) / len(cal_labels),
            "pass_at_1_validation": sum(val_labels) / len(val_labels),
            "gate_status": gate_status,
            "next_step": next_step
        }
    }

    results_file = Path("./results/h-e1_simulation_results.json")
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2)

    logger.info(f"\nResults saved to {results_file}")
    logger.info("=" * 80)
    logger.info("Simulation completed successfully!")
    logger.info("=" * 80)

    return results_data


def main():
    """Main entry point."""
    config = get_config()
    validate_config(config)

    logger = setup_logging(config)

    try:
        results = run_simulation(config)

        print("\n" + "=" * 80)
        print("SIMULATION SUMMARY")
        print("=" * 80)
        print("NOTE: This is a SIMULATION with mock data.")
        print("Real experiment requires Code Llama 7B (13GB+ download, several hours runtime)")
        print("=" * 80)
        print(f"Optimal Temperature: {results['results']['optimal_temperature']:.3f}")
        print(f"ECE Before: {results['results']['ece_before']:.4f}")
        print(f"ECE After: {results['results']['ece_after']:.4f}")
        print(f"ECE Reduction: {results['results']['ece_reduction_pct']:.1f}%")
        print(f"Gate Status: {results['results']['gate_status']}")
        print(f"Next Step: {results['results']['next_step']}")
        print("=" * 80)
        print("All figures generated successfully in ./figures/")
        print("=" * 80)

        return 0

    except Exception as e:
        logger.error(f"Simulation failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
