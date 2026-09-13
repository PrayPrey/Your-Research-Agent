"""Training pipeline for LoRA intervention"""
import torch
from torch.optim import AdamW
from transformers import get_cosine_schedule_with_warmup
from torch.utils.data import DataLoader
from peft import PeftModel
from typing import Dict
from tqdm import tqdm

class InterventionTrainer:
    """LoRA intervention trainer"""

    def __init__(self, model: PeftModel, config: Dict):
        """Initialize trainer.

        Args:
            model: PEFT model with LoRA adapters
            config: Training configuration
        """
        self.model = model
        self.config = config
        self.optimizer = None
        self.scheduler = None

    def setup_optimizer(self, lr: float) -> AdamW:
        """Setup AdamW optimizer.

        Args:
            lr: Learning rate

        Returns:
            AdamW optimizer
        """
        self.optimizer = AdamW(
            self.model.parameters(),
            lr=lr,
            betas=(0.9, 0.999),
            eps=1e-8
        )
        return self.optimizer

    def setup_scheduler(self, optimizer: AdamW, num_training_steps: int) -> any:
        """Setup cosine learning rate scheduler.

        Args:
            optimizer: Optimizer instance
            num_training_steps: Total training steps

        Returns:
            Learning rate scheduler
        """
        num_warmup_steps = int(self.config.get("warmup_ratio", 0.1) * num_training_steps)

        self.scheduler = get_cosine_schedule_with_warmup(
            optimizer,
            num_warmup_steps=num_warmup_steps,
            num_training_steps=num_training_steps
        )
        return self.scheduler

    def train_epoch(self, dataloader: DataLoader) -> Dict[str, float]:
        """Train one epoch.

        Args:
            dataloader: Training data loader

        Returns:
            Training metrics (loss, etc.)
        """
        self.model.train()
        total_loss = 0.0
        num_batches = 0

        for batch in tqdm(dataloader, desc="Training"):
            # Move batch to device
            batch = {k: v.to(self.model.device) for k, v in batch.items()}

            # Forward pass
            outputs = self.model(**batch)
            loss = outputs.loss

            # Backward pass
            loss.backward()

            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(),
                self.config.get("max_grad_norm", 1.0)
            )

            # Optimizer step
            self.optimizer.step()
            self.scheduler.step()
            self.optimizer.zero_grad()

            total_loss += loss.item()
            num_batches += 1

        avg_loss = total_loss / num_batches if num_batches > 0 else 0.0

        return {
            "loss": avg_loss,
            "num_batches": num_batches
        }

    def run_intervention(
        self,
        train_dataloader: DataLoader,
        num_epochs: int
    ) -> Dict[str, any]:
        """Run full intervention training.

        Args:
            train_dataloader: Training data
            num_epochs: Number of training epochs

        Returns:
            Training history
        """
        # Setup optimizer and scheduler
        num_training_steps = len(train_dataloader) * num_epochs
        self.setup_optimizer(self.config.get("learning_rate", 1e-4))
        self.setup_scheduler(self.optimizer, num_training_steps)

        # Training loop
        history = {
            "epoch_losses": [],
            "num_steps": num_training_steps
        }

        for epoch in range(num_epochs):
            metrics = self.train_epoch(train_dataloader)
            history["epoch_losses"].append(metrics["loss"])

            print(f"Epoch {epoch + 1}/{num_epochs} - Loss: {metrics['loss']:.4f}")

        return history
