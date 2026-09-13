"""
Real PoC Experiment for H-E1
Runs actual training with real datasets and evaluation metrics
"""

import torch
import json
import sys
import os
from datetime import datetime
import numpy as np

# Add code directory to path
sys.path.insert(0, os.path.dirname(__file__))

from data.dataset import create_dataloaders
from models.model import JointDPOAttribute, ReferencePolicy
from training.trainer import JointTrainer
from evaluation.evaluator import AttributeEvaluator


def run_poc_experiment(
    batch_size=4,
    max_length=256,
    lr=1e-5,
    num_steps=500,  # PoC: 500 steps for faster execution while still meaningful
    device="cuda" if torch.cuda.is_available() else "cpu"
):
    """
    Run real PoC experiment with actual training and evaluation
    Uses REAL datasets (HH-RLHF + OpenAssistant) and REAL metrics
    """
    print("=" * 80)
    print("H-E1: Joint Training Existence & Convergence (PoC)")
    print("=" * 80)
    print("Mode: Real training with actual datasets and metrics")
    print(f"Device: {device}")
    print(f"Batch size: {batch_size}")
    print(f"Training steps: {num_steps}")
    print(f"Learning rate: {lr}")
    print()

    # Create output directory
    os.makedirs("outputs", exist_ok=True)

    # 1. Load REAL datasets
    print("Loading REAL datasets (HH-RLHF + OpenAssistant)...")
    train_loader, test_loader, tokenizer = create_dataloaders(
        batch_size=batch_size,
        max_length=max_length
    )
    print(f"✓ Train batches: {len(train_loader)}")
    print(f"✓ Test batches: {len(test_loader)}")
    print()

    # 2. Create models
    print("Initializing models...")
    model = JointDPOAttribute(model_name="gpt2-xl", beta=0.1, alpha=0.7)
    ref_policy = ReferencePolicy(model_name="gpt2-xl")
    print(f"✓ Model parameters: {sum(p.numel() for p in model.parameters())/1e9:.2f}B")
    print()

    # 3. REAL training with actual DPO + Attribute loss
    print("Starting REAL training...")
    trainer = JointTrainer(
        model=model,
        ref_policy=ref_policy,
        train_loader=train_loader,
        test_loader=test_loader,
        lr=lr,
        device=device,
        checkpoint_dir="checkpoints"
    )

    # Run actual training
    history = trainer.train(
        num_steps=num_steps,
        log_interval=50,
        checkpoint_interval=250
    )

    print(f"\n✓ Training completed: {num_steps} steps")
    print(f"  Initial loss_dpo: {history['loss_dpo'][0]:.4f}")
    print(f"  Final loss_dpo: {history['loss_dpo'][-1]:.4f}")
    print(f"  Initial loss_attr: {history['loss_attr'][0]:.4f}")
    print(f"  Final loss_attr: {history['loss_attr'][-1]:.4f}")
    print()

    # 4. REAL evaluation with trained model
    print("Running REAL evaluation...")
    evaluator = AttributeEvaluator(model, tokenizer, device=device)

    # Limit test samples for PoC speed while maintaining statistical validity
    eval_results = evaluator.evaluate(test_loader, num_test_samples=500)

    print(f"\nEvaluation Results (REAL metrics):")
    print(f"  Preference Win Rate: {eval_results['preference_win_rate']:.2%}")
    print(f"  Steering Accuracy: {eval_results['steering_accuracy']:.2%}")
    print()

    # 5. Check gate criteria with REAL metrics
    print("Checking MUST_WORK gate criteria...")

    # Get REAL gradient statistics
    grad_stats = trainer.gradient_monitor.get_statistics()
    gradient_angles = trainer.gradient_monitor.angles

    # Check convergence (losses should decrease)
    loss_dpo = history["loss_dpo"]
    loss_attr = history["loss_attr"]
    dpo_decreased = (loss_dpo[-1] < loss_dpo[0])
    attr_decreased = (loss_attr[-1] < loss_attr[0])
    convergence_check = dpo_decreased and attr_decreased

    # Check REAL metrics
    win_rate_check = eval_results["preference_win_rate"] >= 0.50
    steering_check = eval_results["steering_accuracy"] >= 0.60
    gradient_check = grad_stats.get("mean", 180) < 120

    gate_criteria = {
        "convergence": {
            "passed": bool(convergence_check),
            "dpo_decreased": bool(dpo_decreased),
            "attr_decreased": bool(attr_decreased)
        },
        "preference_win_rate": {
            "passed": bool(win_rate_check),
            "value": float(eval_results["preference_win_rate"]),
            "threshold": 0.50
        },
        "steering_accuracy": {
            "passed": bool(steering_check),
            "value": float(eval_results["steering_accuracy"]),
            "threshold": 0.60
        },
        "gradient_angle": {
            "passed": bool(gradient_check),
            "mean": float(grad_stats.get("mean", 0)),
            "threshold": 120.0
        }
    }

    all_passed = all([convergence_check, win_rate_check, steering_check, gradient_check])
    gate_result = "PASS" if all_passed else "FAIL"

    print(f"\n{'='*80}")
    print(f"Gate Result: {gate_result}")
    print(f"{'='*80}")
    for criterion, details in gate_criteria.items():
        status = "✓" if details["passed"] else "✗"
        print(f"  [{status}] {criterion.replace('_', ' ').title()}")

    # 6. Save REAL results
    final_results = {
        "hypothesis_id": "h-e1",
        "timestamp": datetime.now().isoformat(),
        "gate_result": gate_result,
        "gate_criteria": gate_criteria,
        "training_history": {
            "num_steps": num_steps,
            "final_loss_total": float(history["loss_total"][-1]),
            "final_loss_dpo": float(history["loss_dpo"][-1]),
            "final_loss_attr": float(history["loss_attr"][-1]),
            "loss_dpo_history": [float(x) for x in history["loss_dpo"]],
            "loss_attr_history": [float(x) for x in history["loss_attr"]],
            "loss_total_history": [float(x) for x in history["loss_total"]]
        },
        "gradient_statistics": {
            "mean": float(grad_stats.get("mean", 0)),
            "std": float(grad_stats.get("std", 0)),
            "min": float(grad_stats.get("min", 0)),
            "max": float(grad_stats.get("max", 0)),
            "catastrophic_interference": float(grad_stats.get("catastrophic_interference", 0))
        },
        "evaluation_results": {
            "preference_win_rate": float(eval_results["preference_win_rate"]),
            "steering_accuracy": float(eval_results["steering_accuracy"]),
            "num_preference_tests": eval_results["num_preference_tests"],
            "num_steering_tests": eval_results["num_steering_tests"]
        },
        "config": {
            "model": "gpt2-xl",
            "batch_size": batch_size,
            "max_length": max_length,
            "lr": lr,
            "num_steps": num_steps,
            "alpha": 0.7,
            "beta": 0.1
        },
        "note": "Real PoC experiment with actual HH-RLHF + OpenAssistant datasets and trained evaluation"
    }

    with open("outputs/experiment_results.json", 'w') as f:
        json.dump(final_results, f, indent=2)

    print(f"\n✓ Results saved to outputs/experiment_results.json")

    return final_results


if __name__ == "__main__":
    results = run_poc_experiment()
    print("\nExperiment complete!")
    print(f"Gate Result: {results['gate_result']}")
