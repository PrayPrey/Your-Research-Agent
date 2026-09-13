#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import torch
import json
import matplotlib.pyplot as plt
from data import WikiText103Dataset, create_dataloader
from models import TeacherModel, StudentModel, LayerWiseMSELoss
from training import Validator, load_checkpoint
from config import ExperimentConfig


def main():
    config = ExperimentConfig()
    config.data.cache_dir = f"{config.output_dir}/data"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load validation dataset
    print("Loading validation dataset...")
    val_dataset = WikiText103Dataset(
        split="validation",
        cache_dir=config.data.cache_dir,
        max_length=config.data.max_length
    )
    val_loader = create_dataloader(
        val_dataset,
        batch_size=config.training.batch_size,
        shuffle=False,
        num_workers=config.data.num_workers
    )

    # Initialize models
    print("Initializing models...")
    teacher = TeacherModel(model_name=config.teacher.model_name).to(device)
    student = StudentModel(
        d_model=config.student.d_model,
        n_layer=config.student.n_layer,
        vocab_size=config.student.vocab_size,
        ssm_d_state=config.student.ssm_d_state,
        ssm_d_conv=config.student.ssm_d_conv,
        ssm_expand=config.student.ssm_expand
    ).to(device)

    # Load best checkpoint
    checkpoint_path = f"{config.output_dir}/checkpoints/best.pt"
    print(f"Loading checkpoint: {checkpoint_path}")
    step, _ = load_checkpoint(checkpoint_path, student)

    # Validator
    loss_fn = LayerWiseMSELoss(epsilon=config.loss.epsilon)
    validator = Validator(teacher, student, loss_fn, val_loader, device)

    # Evaluate
    print("Evaluating...")
    mean_loss, per_layer = validator.evaluate()
    print(f"Final normalized MSE: {mean_loss:.4f}")
    print(f"Converged at step: {step}")

    # Gate decision
    gate_satisfied = mean_loss < config.training.early_stop_threshold
    print(f"Gate satisfied (MSE < 0.1): {gate_satisfied}")

    # Save metrics
    metrics = {
        "normalized_mse": float(mean_loss),
        "converged_at_step": int(step),
        "gate_satisfied": gate_satisfied,
        "per_layer_mse": [float(l) for l in per_layer]
    }

    os.makedirs(f"{config.output_dir}/results", exist_ok=True)
    with open(f"{config.output_dir}/results/final_metrics.json", 'w') as f:
        json.dump(metrics, f, indent=2)

    # Plot per-layer MSE
    plt.figure(figsize=(10, 6))
    plt.bar(range(1, 13), per_layer)
    plt.xlabel("Layer")
    plt.ylabel("Normalized MSE")
    plt.title("Per-Layer MSE Breakdown")
    plt.savefig(f"{config.output_dir}/results/layer_mse_breakdown.png")
    print(f"Results saved to {config.output_dir}/results/")


if __name__ == "__main__":
    main()
