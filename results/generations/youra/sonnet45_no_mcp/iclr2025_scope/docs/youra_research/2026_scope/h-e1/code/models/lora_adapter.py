"""
Multi-Rank LoRA Adapter Factory
Based on: 03_architecture.md - Module 2: ModelModule
Based on: 03_logic.md - A-1: LoRA Adapter Module
"""

import torch
import torch.nn as nn
from transformers import AutoModelForSequenceClassification
from peft import LoraConfig, get_peft_model, PeftModel
from typing import Dict, Optional


class MultiRankLoRAFactory:
    """Create LoRA adapters with different ranks using PEFT library."""

    def __init__(self,
                 base_model_name: str = "meta-llama/Llama-2-7b-hf",
                 ranks: list = [4, 8, 16, 32],
                 lora_alpha: int = 16,
                 lora_dropout: float = 0.1,
                 target_modules: list = ["q_proj", "v_proj"]):
        """
        Initialize multi-rank LoRA factory.

        Args:
            base_model_name: HuggingFace model identifier
            ranks: List of LoRA ranks to support
            lora_alpha: LoRA scaling parameter
            lora_dropout: Dropout probability
            target_modules: Model layers to apply LoRA
        """
        self.base_model_name = base_model_name
        self.ranks = ranks
        self.lora_alpha = lora_alpha
        self.lora_dropout = lora_dropout
        self.target_modules = target_modules

    def create_adapter(self, rank: int, num_labels: int, device: str = "cuda") -> PeftModel:
        """
        Create LoRA adapter for specific rank and task.

        Args:
            rank: LoRA rank (4, 8, 16, or 32)
            num_labels: Number of output labels for the task
            device: Device to load model on

        Returns:
            Model with LoRA adapter attached
        """
        if rank not in self.ranks:
            raise ValueError(f"Rank {rank} not in supported ranks {self.ranks}")

        # Load base model
        base_model = AutoModelForSequenceClassification.from_pretrained(
            self.base_model_name,
            num_labels=num_labels,
            torch_dtype=torch.float16,
            device_map=device
        )

        # Configure LoRA
        lora_config = LoraConfig(
            r=rank,
            lora_alpha=self.lora_alpha,
            target_modules=self.target_modules,
            lora_dropout=self.lora_dropout,
            bias="none",
            task_type="SEQ_CLS"
        )

        # Create PEFT model
        model = get_peft_model(base_model, lora_config)
        model.print_trainable_parameters()

        return model

    def count_parameters(self, model: nn.Module) -> int:
        """
        Count trainable parameters in model.

        Args:
            model: PyTorch model

        Returns:
            Number of trainable parameters
        """
        return sum(p.numel() for p in model.parameters() if p.requires_grad)

    def count_flops(self, model: nn.Module, input_shape: tuple = (1, 512)) -> int:
        """
        Count FLOPs for forward pass (approximation).

        Args:
            model: PyTorch model
            input_shape: Input tensor shape (batch, seq_len)

        Returns:
            Approximate FLOPs count
        """
        # For LoRA: FLOPs ≈ 2 * d * r * seq_len
        # where d = hidden_dim, r = rank, seq_len = sequence length

        # Get LoRA rank from model config
        if hasattr(model, "peft_config"):
            peft_config = model.peft_config.get("default")
            if peft_config:
                rank = peft_config.r
                # LLaMA-2-7B has hidden_dim = 4096
                hidden_dim = 4096
                seq_len = input_shape[1]

                # Approximate FLOPs: 2 operations (A @ B) per adapter layer
                # Assuming 2 target modules (q_proj, v_proj) per layer
                num_layers = 32  # LLaMA-2-7B has 32 layers
                num_adapters = len(self.target_modules) * num_layers

                flops = 2 * hidden_dim * rank * seq_len * num_adapters
                return int(flops)

        # Fallback: count trainable parameters as proxy
        return self.count_parameters(model) * 2


class LoRATrainer:
    """Trainer for LoRA adapters with checkpointing."""

    def __init__(self,
                 model: PeftModel,
                 optimizer_config: Dict = None,
                 scheduler_config: Dict = None):
        """
        Initialize LoRA trainer.

        Args:
            model: PEFT model with LoRA adapter
            optimizer_config: Optimizer configuration
            scheduler_config: Learning rate scheduler configuration
        """
        self.model = model
        self.device = next(model.parameters()).device

        # Default optimizer config
        if optimizer_config is None:
            optimizer_config = {
                "lr": 3e-4,
                "betas": (0.9, 0.999),
                "weight_decay": 0.01
            }

        # Create optimizer (only for trainable parameters)
        self.optimizer = torch.optim.AdamW(
            filter(lambda p: p.requires_grad, model.parameters()),
            **optimizer_config
        )

        # Learning rate scheduler
        if scheduler_config:
            self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer,
                **scheduler_config
            )
        else:
            self.scheduler = None

    def train_epoch(self, train_loader, val_loader=None) -> Dict[str, float]:
        """
        Train for one epoch.

        Args:
            train_loader: Training data loader
            val_loader: Validation data loader (optional)

        Returns:
            Dictionary with training metrics
        """
        self.model.train()
        total_loss = 0
        total_correct = 0
        total_samples = 0

        for batch in train_loader:
            # Move batch to device
            input_ids = batch["input_ids"].to(self.device)
            attention_mask = batch["attention_mask"].to(self.device)
            labels = batch["labels"].to(self.device)

            # Forward pass
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )

            loss = outputs.loss

            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            self.optimizer.step()

            if self.scheduler:
                self.scheduler.step()

            # Track metrics
            total_loss += loss.item()
            predictions = outputs.logits.argmax(dim=-1)
            total_correct += (predictions == labels).sum().item()
            total_samples += labels.size(0)

        avg_loss = total_loss / len(train_loader)
        accuracy = total_correct / total_samples

        metrics = {
            "train_loss": avg_loss,
            "train_accuracy": accuracy
        }

        # Validation
        if val_loader:
            val_metrics = self.evaluate(val_loader)
            metrics.update(val_metrics)

        return metrics

    def evaluate(self, val_loader) -> Dict[str, float]:
        """
        Evaluate model on validation set.

        Args:
            val_loader: Validation data loader

        Returns:
            Dictionary with validation metrics
        """
        self.model.eval()
        total_loss = 0
        total_correct = 0
        total_samples = 0

        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["labels"].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )

                total_loss += outputs.loss.item()
                predictions = outputs.logits.argmax(dim=-1)
                total_correct += (predictions == labels).sum().item()
                total_samples += labels.size(0)

        avg_loss = total_loss / len(val_loader)
        accuracy = total_correct / total_samples

        return {
            "val_loss": avg_loss,
            "val_accuracy": accuracy
        }

    def save_adapter(self, path: str):
        """
        Save LoRA adapter weights.

        Args:
            path: Directory to save adapter
        """
        self.model.save_pretrained(path)
        print(f"✓ Adapter saved to {path}")
