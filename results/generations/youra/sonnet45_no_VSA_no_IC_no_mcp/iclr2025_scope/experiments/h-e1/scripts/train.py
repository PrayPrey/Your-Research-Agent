#!/usr/bin/env python3
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import torch
from data import WikiText103Dataset, create_dataloader
from models import TeacherModel, StudentModel, LayerWiseMSELoss
from training import DistillationTrainer, Validator, set_seed
from config import ExperimentConfig


def main():
    # Load config
    config = ExperimentConfig()
    config.data.cache_dir = f"{config.output_dir}/data"

    # Set seed
    set_seed(config.training.seed)

    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Load datasets
    print("Loading datasets...")
    train_dataset = WikiText103Dataset(
        split="calibration",
        cache_dir=config.data.cache_dir,
        max_length=config.data.max_length
    )
    val_dataset = WikiText103Dataset(
        split="validation",
        cache_dir=config.data.cache_dir,
        max_length=config.data.max_length
    )

    train_loader = create_dataloader(
        train_dataset,
        batch_size=config.training.batch_size,
        shuffle=True,
        num_workers=config.data.num_workers
    )
    val_loader = create_dataloader(
        val_dataset,
        batch_size=config.training.batch_size,
        shuffle=False,
        num_workers=config.data.num_workers
    )

    print(f"Train dataset: {len(train_dataset)} examples")
    print(f"Val dataset: {len(val_dataset)} examples")

    # Initialize models
    print("Initializing models...")
    teacher = TeacherModel(model_name=config.teacher.model_name)
    student = StudentModel(
        d_model=config.student.d_model,
        n_layer=config.student.n_layer,
        vocab_size=config.student.vocab_size,
        ssm_d_state=config.student.ssm_d_state,
        ssm_d_conv=config.student.ssm_d_conv,
        ssm_expand=config.student.ssm_expand
    )

    # Loss function
    loss_fn = LayerWiseMSELoss(epsilon=config.loss.epsilon)

    # Validator
    validator = Validator(teacher, student, loss_fn, val_loader, device)

    # Trainer
    print("Starting training...")
    trainer = DistillationTrainer(
        teacher=teacher,
        student=student,
        loss_fn=loss_fn,
        train_loader=train_loader,
        validator=validator,
        config=config,
        device=device
    )

    best_val_loss = trainer.train()
    print(f"Training complete. Best validation loss: {best_val_loss:.4f}")


if __name__ == "__main__":
    main()
