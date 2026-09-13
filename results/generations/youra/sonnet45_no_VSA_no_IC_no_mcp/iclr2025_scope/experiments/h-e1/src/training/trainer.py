import torch
from torch.cuda.amp import autocast, GradScaler
from transformers import get_linear_schedule_with_warmup
from typing import Dict
from .utils import save_checkpoint


class DistillationTrainer:
    """Training loop for layer-wise distillation."""

    def __init__(
        self,
        teacher,
        student,
        loss_fn,
        train_loader,
        validator,
        config,
        device
    ):
        self.teacher = teacher.to(device)
        self.student = student.to(device)
        self.loss_fn = loss_fn.to(device)
        self.train_loader = train_loader
        self.validator = validator
        self.config = config
        self.device = device

        # Optimizer
        self.optimizer = torch.optim.AdamW(
            student.parameters(),
            lr=config.optimizer.lr,
            betas=config.optimizer.betas,
            eps=config.optimizer.eps,
            weight_decay=config.optimizer.weight_decay
        )

        # Scheduler
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=config.optimizer.warmup_steps,
            num_training_steps=config.optimizer.total_steps
        )

        # Mixed precision
        self.scaler = GradScaler(enabled=config.training.mixed_precision)

        # Tracking
        self.global_step = 0
        self.best_val_loss = float('inf')

    def train_step(self, batch: Dict[str, torch.Tensor]):
        """Single training step."""
        input_ids = batch['input_ids'].to(self.device)
        attention_mask = batch['attention_mask'].to(self.device)

        # Forward through teacher (frozen)
        teacher_hiddens = self.teacher(input_ids, attention_mask)

        # Forward through student
        with autocast(enabled=self.config.training.mixed_precision):
            student_hiddens = self.student(input_ids)
            loss, layer_losses = self.loss_fn(teacher_hiddens, student_hiddens)
            loss = loss / self.config.training.gradient_accumulation_steps

        # Backward
        self.scaler.scale(loss).backward()

        return loss, layer_losses

    def train(self):
        """Main training loop."""
        self.student.train()
        train_iter = iter(self.train_loader)

        for step in range(self.config.training.max_steps):
            try:
                batch = next(train_iter)
            except StopIteration:
                train_iter = iter(self.train_loader)
                batch = next(train_iter)

            loss, layer_losses = self.train_step(batch)
            self.global_step = step

            # Gradient accumulation
            if (step + 1) % self.config.training.gradient_accumulation_steps == 0:
                self.scaler.unscale_(self.optimizer)
                torch.nn.utils.clip_grad_norm_(
                    self.student.parameters(),
                    self.config.optimizer.max_grad_norm
                )
                self.scaler.step(self.optimizer)
                self.scaler.update()
                self.optimizer.zero_grad()
                self.scheduler.step()

            # Logging
            if step % self.config.training.logging_steps == 0:
                print(f"Step {step}: Loss={loss.item():.4f}")

            # Validation
            if step % self.config.training.eval_steps == 0:
                val_loss, per_layer = self.validator.evaluate()
                print(f"Step {step}: Val Loss={val_loss:.4f}")

                if val_loss < self.best_val_loss:
                    self.best_val_loss = val_loss
                    save_checkpoint(
                        f"{self.config.output_dir}/checkpoints/best.pt",
                        step,
                        self.student,
                        self.optimizer,
                        val_loss
                    )

            # Checkpointing
            if step % self.config.training.checkpoint_steps == 0:
                save_checkpoint(
                    f"{self.config.output_dir}/checkpoints/step_{step}.pt",
                    step,
                    self.student,
                    self.optimizer,
                    loss.item()
                )

            # Early stopping
            if loss.item() < self.config.training.early_stop_threshold:
                print(f"Converged at step {step}: MSE={loss.item():.4f}")
                break

        return self.best_val_loss
