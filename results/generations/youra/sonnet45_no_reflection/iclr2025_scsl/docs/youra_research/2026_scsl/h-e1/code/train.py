"""Training loop for GPT-2 variants."""
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from transformers import get_cosine_schedule_with_warmup
from tqdm import tqdm
import json
import os
from typing import Dict


class GPT2Trainer:
    """Training loop for GPT-2 variants."""

    def __init__(self, model: nn.Module, train_loader: DataLoader, val_loader: DataLoader,
                 config, variant: str):
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.config = config
        self.variant = variant

        self.device = torch.device(config.device if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        # Optimizer
        self.optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=config.training.learning_rate,
            betas=config.training.betas,
            weight_decay=config.training.weight_decay
        )

        # Scheduler
        self.scheduler = get_cosine_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=config.training.warmup_steps,
            num_training_steps=config.total_steps
        )

        self.grad_accum_steps = config.training.gradient_accumulation_steps
        self.checkpoint_dir = f"checkpoints/{variant}/"
        os.makedirs(self.checkpoint_dir, exist_ok=True)

        # Training state
        self.global_step = 0
        self.training_logs = []

    def train_step(self, batch: Dict) -> Dict:
        """Single training step with gradient accumulation. batch: {input_ids: [B, L], labels: [B, L]}"""
        input_ids = batch['input_ids'].to(self.device)
        labels = batch['labels'].to(self.device)

        outputs = self.model(input_ids=input_ids, labels=labels)
        loss = outputs['loss'] / self.grad_accum_steps

        loss.backward()

        metrics = {
            'loss': outputs['loss'].item(),
            'lr': self.scheduler.get_last_lr()[0]
        }

        if 'reg_loss' in outputs:
            metrics['reg_loss'] = outputs['reg_loss'].item()
        if 'clm_loss' in outputs:
            metrics['clm_loss'] = outputs['clm_loss'].item()

        return metrics

    def validation_step(self) -> Dict:
        """Validation pass for perplexity."""
        self.model.eval()
        total_loss = 0.0
        num_batches = 0

        with torch.no_grad():
            for batch in self.val_loader:
                input_ids = batch['input_ids'].to(self.device)
                labels = batch['labels'].to(self.device)

                outputs = self.model(input_ids=input_ids, labels=labels)
                total_loss += outputs['loss'].item()
                num_batches += 1

                if num_batches >= self.config.evaluation.eval_samples // self.config.evaluation.eval_batch_size:
                    break

        avg_loss = total_loss / max(num_batches, 1)
        perplexity = torch.exp(torch.tensor(avg_loss)).item()

        self.model.train()

        return {
            'perplexity': perplexity,
            'val_loss': avg_loss
        }

    def train(self, total_steps: int, baseline_ppl: float = None) -> None:
        """Main training loop. total_steps: ~78,125 for 10B tokens"""
        self.model.train()
        train_iter = iter(self.train_loader)
        progress_bar = tqdm(range(total_steps), desc=f"Training {self.variant}")

        for step in progress_bar:
            self.global_step = step

            # Get batch
            try:
                batch = next(train_iter)
            except StopIteration:
                train_iter = iter(self.train_loader)
                batch = next(train_iter)

            # Training step
            metrics = self.train_step(batch)

            # Update weights
            if (step + 1) % self.grad_accum_steps == 0:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.training.max_grad_norm)
                self.optimizer.step()
                self.scheduler.step()
                self.optimizer.zero_grad()

            # Update progress bar
            progress_bar.set_postfix(loss=f"{metrics['loss']:.4f}", lr=f"{metrics['lr']:.2e}")

            # Evaluation
            if step % self.config.training.eval_interval == 0 and step > 0:
                val_metrics = self.validation_step()
                metrics.update(val_metrics)

                # Adaptive lambda tuning (for regularized model)
                if hasattr(self.model, 'adaptive_lambda_update') and baseline_ppl is not None:
                    if self.config.regularization.adaptive_tuning:
                        self.model.adaptive_lambda_update(
                            val_metrics['perplexity'],
                            baseline_ppl,
                            self.config.evaluation.target_ppl_deviation
                        )
                        metrics['lambda_reg'] = self.model.lambda_reg

                # Log metrics
                metrics['step'] = step
                self.training_logs.append(metrics)
                print(f"\nStep {step}: Loss={metrics['loss']:.4f}, PPL={val_metrics['perplexity']:.2f}")

            # Checkpoint
            if step % self.config.training.checkpoint_interval == 0 and step > 0:
                self.save_checkpoint(step, metrics)

        # Final checkpoint
        self.save_checkpoint(total_steps, metrics)
        print(f"Training complete for {self.variant}")

    def save_checkpoint(self, step: int, metrics: Dict) -> None:
        """Save model checkpoint with metrics."""
        checkpoint_path = os.path.join(self.checkpoint_dir, f"checkpoint_step_{step}.pt")

        checkpoint = {
            'step': step,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'metrics': metrics,
            'config': self.config
        }

        torch.save(checkpoint, checkpoint_path)

        # Save training logs
        logs_path = os.path.join(self.checkpoint_dir, "training_logs.json")
        with open(logs_path, 'w') as f:
            json.dump(self.training_logs, f, indent=2)

        print(f"Checkpoint saved: {checkpoint_path}")
