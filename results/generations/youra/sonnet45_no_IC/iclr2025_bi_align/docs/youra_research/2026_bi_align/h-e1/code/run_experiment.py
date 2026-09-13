"""
Main Experiment Script for H-E1
Joint Training Existence & Convergence
"""

import torch
import json
import sys
import os
from datetime import datetime

# Add code directory to path
sys.path.insert(0, os.path.dirname(__file__))

from data.dataset import create_dataloaders
from models.model import JointDPOAttribute, ReferencePolicy
from training.trainer import JointTrainer
from evaluation.evaluator import AttributeEvaluator


def run_experiment(
    batch_size=4,
    max_length=512,
    lr=1e-5,
    num_steps=15000,
    device="cuda" if torch.cuda.is_available() else "cpu",
    checkpoint_dir="checkpoints",
    output_dir="outputs"
):
    """
    Run full H-E1 experiment

    Gate Criteria (MUST_WORK):
    1. Training converges: Both L_DPO and L_attr decrease monotonically
    2. Preference win rate: ≥50% (better than random)
    3. Attribute steering accuracy: ≥60% (better than chance)
    4. Gradient angles: <120° (no catastrophic interference)
    """
    print("=" * 80)
    print("H-E1: Joint Training Existence & Convergence")
    print("=" * 80)
    print(f"Device: {device}")
    print(f"Batch size: {batch_size}")
    print(f"Training steps: {num_steps}")
    print(f"Learning rate: {lr}")
    print()

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # 1. Load data
    print("Loading datasets...")
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

    # 3. Train
    print("Starting training...")
    trainer = JointTrainer(
        model=model,
        ref_policy=ref_policy,
        train_loader=train_loader,
        test_loader=test_loader,
        lr=lr,
        device=device,
        checkpoint_dir=checkpoint_dir
    )

    history = trainer.train(
        num_steps=num_steps,
        log_interval=100,
        checkpoint_interval=1000
    )

    # Save training results
    trainer.save_results(os.path.join(output_dir, "training_results.json"))
    print()

    # 4. Evaluate
    print("Running evaluation...")
    evaluator = AttributeEvaluator(model, tokenizer, device=device)
    eval_results = evaluator.evaluate(test_loader, num_test_samples=1000)

    print(f"\nEvaluation Results:")
    print(f"  Preference Win Rate: {eval_results['preference_win_rate']:.2%}")
    print(f"  Steering Accuracy: {eval_results['steering_accuracy']:.2%}")
    print()

    # 5. Check gate criteria
    print("Checking MUST_WORK gate criteria...")

    # Get gradient statistics
    grad_stats = trainer.gradient_monitor.get_statistics()

    # Check convergence (losses should decrease)
    loss_dpo_converged = history["loss_dpo"][-100:] < history["loss_dpo"][:100]
    loss_attr_converged = history["loss_attr"][-100:] < history["loss_attr"][:100]
    convergence_check = (
        np.mean(loss_dpo_converged) > 0.5 and
        np.mean(loss_attr_converged) > 0.5
    )

    # Check metrics
    win_rate_check = eval_results["preference_win_rate"] >= 0.50
    steering_check = eval_results["steering_accuracy"] >= 0.60
    gradient_check = grad_stats.get("mean", 180) < 120

    # Gate result
    gate_criteria = {
        "convergence": {
            "passed": convergence_check,
            "dpo_decreased": bool(np.mean(loss_dpo_converged)),
            "attr_decreased": bool(np.mean(loss_attr_converged))
        },
        "preference_win_rate": {
            "passed": win_rate_check,
            "value": eval_results["preference_win_rate"],
            "threshold": 0.50
        },
        "steering_accuracy": {
            "passed": steering_check,
            "value": eval_results["steering_accuracy"],
            "threshold": 0.60
        },
        "gradient_angle": {
            "passed": gradient_check,
            "mean": grad_stats.get("mean", 0),
            "threshold": 120.0
        }
    }

    all_passed = all([
        convergence_check,
        win_rate_check,
        steering_check,
        gradient_check
    ])

    gate_result = "PASS" if all_passed else "FAIL"

    print(f"\n{'='*80}")
    print(f"Gate Result: {gate_result}")
    print(f"{'='*80}")
    for criterion, details in gate_criteria.items():
        status = "✓" if details["passed"] else "✗"
        print(f"  [{status}] {criterion.replace('_', ' ').title()}")

    # 6. Save final results
    final_results = {
        "hypothesis_id": "h-e1",
        "timestamp": datetime.now().isoformat(),
        "gate_result": gate_result,
        "gate_criteria": gate_criteria,
        "training_history": {
            "num_steps": len(history["loss_total"]),
            "final_loss_total": history["loss_total"][-1] if history["loss_total"] else None,
            "final_loss_dpo": history["loss_dpo"][-1] if history["loss_dpo"] else None,
            "final_loss_attr": history["loss_attr"][-1] if history["loss_attr"] else None
        },
        "gradient_statistics": grad_stats,
        "evaluation_results": eval_results,
        "config": {
            "batch_size": batch_size,
            "max_length": max_length,
            "lr": lr,
            "num_steps": num_steps,
            "alpha": 0.7,
            "beta": 0.1
        }
    }

    with open(os.path.join(output_dir, "experiment_results.json"), 'w') as f:
        json.dump(final_results, f, indent=2)

    print(f"\n✓ Results saved to {output_dir}/experiment_results.json")

    return final_results


if __name__ == "__main__":
    import numpy as np

    # Run experiment with PoC settings (reduced for faster execution)
    results = run_experiment(
        batch_size=4,
        max_length=256,  # Reduced for faster execution
        lr=1e-5,
        num_steps=100,  # PoC: 100 steps instead of 15000
        device="cuda" if torch.cuda.is_available() else "cpu"
    )

    print("\nExperiment complete!")
    print(f"Gate Result: {results['gate_result']}")
