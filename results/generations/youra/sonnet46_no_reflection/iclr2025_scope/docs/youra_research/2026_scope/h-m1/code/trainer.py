"""
H-M1 JointLoRAKVTrainer: separate param groups for LoRA and Locret heads.
"""
import os
import math
import torch
import torch.nn as nn
from typing import List, Dict, Optional
from torch.optim import AdamW
from transformers import get_linear_schedule_with_warmup
from config import ExperimentConfig
from model import JointLoRAKVModel


class JointLoRAKVTrainer:
    def __init__(
        self,
        model: JointLoRAKVModel,
        train_loader,
        config: ExperimentConfig,
        task: str,
        seed: int,
        is_b1: bool = False,
        log_path: Optional[str] = None,
    ):
        self.model = model
        self.train_loader = train_loader
        self.config = config
        self.task = task
        self.seed = seed
        self.is_b1 = is_b1
        self.log_path = log_path or str(config.get_log_path(f"{task}_seed{seed}"))
        self.device = next(model.parameters()).device

        self.optimizer = self.build_optimizer()
        num_epochs = config.get_epochs(task)
        total_steps = math.ceil(len(train_loader) / config.grad_accum_steps) * num_epochs
        warmup_steps = int(total_steps * config.warmup_ratio)
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer, warmup_steps, total_steps
        )

        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        self._log_file = open(self.log_path, "w")

    def _log(self, msg: str):
        print(msg)
        self._log_file.write(msg + "\n")
        self._log_file.flush()

    def build_optimizer(self) -> AdamW:
        lora_params = [p for n, p in self.model.named_parameters()
                       if "lora_" in n and p.requires_grad]
        classifier_params = [p for n, p in self.model.named_parameters()
                              if "classifier" in n and p.requires_grad]
        param_groups = [
            {"params": lora_params + classifier_params, "lr": self.config.lora_lr},
        ]
        if not self.is_b1:
            locret_params = list(self.model.locret_heads.parameters())
            locret_trainable = [p for p in locret_params if p.requires_grad]
            if locret_trainable:
                param_groups.append({"params": locret_trainable, "lr": self.config.locret_lr})

        optimizer = AdamW(
            param_groups,
            weight_decay=self.config.weight_decay,
            betas=(self.config.adam_beta1, self.config.adam_beta2),
            eps=self.config.adam_eps,
        )
        return optimizer

    def train_epoch(self, epoch: int) -> Dict:
        self.model.train()
        total_loss = 0.0
        step_count = 0
        locret_grad_norms = []

        self.optimizer.zero_grad()
        for batch_idx, batch in enumerate(self.train_loader):
            input_ids = batch["input_ids"].to(self.device)
            attention_mask = batch["attention_mask"].to(self.device)
            labels = batch["labels"].to(self.device)

            out = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels,
                budget_ratio=self.config.kv_budget_ratio,
                training_mode=True,
            )
            loss = out["loss"] / self.config.grad_accum_steps
            loss.backward()

            if (batch_idx + 1) % self.config.grad_accum_steps == 0:
                torch.nn.utils.clip_grad_norm_(
                    self.model.parameters(), self.config.grad_clip
                )

                # Log Locret grad norm (mechanism activation indicator)
                if not self.is_b1:
                    locret_params = [p for p in self.model.locret_heads.parameters()
                                     if p.grad is not None]
                    if locret_params:
                        locret_grad_norm = torch.stack(
                            [p.grad.norm() for p in locret_params]
                        ).norm().item()
                        locret_grad_norms.append(locret_grad_norm)
                        msg = (
                            f"JointLoRA-KV: Locret heads receiving CE gradients — "
                            f"epoch {epoch}, step {step_count}, locret_grad_norm={locret_grad_norm:.4f}"
                        )
                        self._log(msg)

                self.optimizer.step()
                self.scheduler.step()
                self.optimizer.zero_grad()
                step_count += 1
                total_loss += loss.item() * self.config.grad_accum_steps

        avg_loss = total_loss / max(step_count, 1)
        avg_locret_grad = sum(locret_grad_norms) / max(len(locret_grad_norms), 1)
        self._log(f"Epoch {epoch}: avg_loss={avg_loss:.4f}, locret_grad_norm={avg_locret_grad:.4f}")
        return {
            "loss": avg_loss,
            "locret_grad_norm": avg_locret_grad,
            "step_count": step_count,
        }

    def train(self) -> List[Dict]:
        history = []
        num_epochs = self.config.get_epochs(self.task)
        for epoch in range(1, num_epochs + 1):
            result = self.train_epoch(epoch)
            history.append(result)
            self._log(f"  → epoch {epoch}/{num_epochs} done, loss={result['loss']:.4f}")
        self._log_file.close()
        return history

    def save_checkpoint(self, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        self.model.base_model.save_pretrained(output_dir)
        torch.save(
            self.model.locret_heads.state_dict(),
            os.path.join(output_dir, "locret_heads.pt"),
        )
        torch.save(
            self.model.classifier.state_dict(),
            os.path.join(output_dir, "classifier.pt"),
        )
