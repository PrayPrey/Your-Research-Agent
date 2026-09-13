import os
from typing import Any, Dict

import torch
import torch.nn.functional as F
from torch.nn.utils import clip_grad_norm_
from torch.optim import AdamW
from transformers import get_cosine_schedule_with_warmup

from stability import StabilityError, StabilityMonitor


class JointLoRAKVTrainer:
    def __init__(self, model, data_manager, stability_monitor: StabilityMonitor, training_config, seed: int) -> None:
        self.model = model
        self.data_manager = data_manager
        self.monitor = stability_monitor
        self.cfg = training_config
        self.seed = seed
        self.train_loader = data_manager.get_glue_train_loader()
        total_steps = len(self.train_loader) * training_config.max_epochs
        self.optimizer = self.build_optimizer()
        self.scheduler = self.build_scheduler(self.optimizer, total_steps)

    def build_optimizer(self) -> AdamW:
        lora_params = self.model.get_lora_params()
        locret_params = self.model.get_locret_params()
        assert len(lora_params) > 0, "No LoRA params found"
        assert len(locret_params) > 0, "No Locret params found"
        return AdamW(
            [
                {"params": lora_params, "lr": self.cfg.lora_lr},
                {"params": locret_params, "lr": self.cfg.locret_lr},
            ],
            weight_decay=self.cfg.weight_decay,
            betas=self.cfg.betas,
            eps=self.cfg.eps,
        )

    def build_scheduler(self, optimizer: AdamW, total_steps: int):
        warmup_steps = int(total_steps * self.cfg.warmup_ratio)
        return get_cosine_schedule_with_warmup(
            optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=total_steps,
        )

    def train_step(self, batch: Dict[str, Any], step: int) -> float:
        device = next(self.model.parameters()).device
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        logits, cis_scores, loss = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=None,
            kv_budget_ratio=self.model.locret_cfg.kv_budget_ratio,
            training_mode=True,
        )

        # CE loss on classification logits (use last token for causal LM)
        # For classification, take mean-pool of non-padding tokens
        # Determine num_labels from logits vocab vs label range
        # Use cross-entropy directly on last token logit slice
        num_labels = int(labels.max().item()) + 1
        num_labels = max(num_labels, 2)
        cls_logits = logits[:, -1, :num_labels]  # [B, num_labels]
        loss = F.cross_entropy(cls_logits, labels)

        if self.monitor.check_nan(loss):
            raise StabilityError(f"NaN loss at step {step}, seed {self.seed}")

        self.monitor.update(loss.item(), step)
        if self.monitor.check_divergence(loss.item()):
            pass  # log but continue

        loss.backward()

        # Grad norm logging every 50 steps
        if step % 50 == 0:
            lora_params = self.model.get_lora_params()
            locret_params = self.model.get_locret_params()
            lora_norm = torch.nn.utils.clip_grad_norm_(lora_params, float("inf")).item()
            locret_norm = torch.nn.utils.clip_grad_norm_(locret_params, float("inf")).item()
            self.monitor.record_grad_norms(step, lora_norm, locret_norm)

        all_params = self.model.get_lora_params() + self.model.get_locret_params()
        clip_grad_norm_(all_params, self.cfg.grad_clip_norm)
        self.optimizer.step()
        self.scheduler.step()
        self.optimizer.zero_grad()
        return loss.item()

    def train_epoch(self, epoch: int) -> Dict[str, Any]:
        self.model.train()
        total_loss = 0.0
        steps = 0
        for step, batch in enumerate(self.train_loader):
            global_step = epoch * len(self.train_loader) + step
            loss_val = self.train_step(batch, global_step)
            total_loss += loss_val
            steps += 1
            if steps % 100 == 0:
                print(f"  Epoch {epoch+1} step {steps}/{len(self.train_loader)} loss={loss_val:.4f}")
        mean_loss = total_loss / max(steps, 1)
        return {
            "epoch": epoch,
            "mean_loss": mean_loss,
            "nan_events": self.monitor.nan_events,
            "divergence_events": self.monitor.divergence_events,
        }

    def train(self) -> Dict[str, Any]:
        torch.manual_seed(self.seed)
        print(f"\n[JointLoRAKVTrainer] Training seed={self.seed}")
        for epoch in range(self.cfg.max_epochs):
            result = self.train_epoch(epoch)
            print(f"  Epoch {epoch+1}/{self.cfg.max_epochs}: mean_loss={result['mean_loss']:.4f} "
                  f"nan={result['nan_events']} div={result['divergence_events']}")
        return self.monitor.get_report()

    def save_checkpoint(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save({
            "model_state": self.model.state_dict(),
            "optimizer_state": self.optimizer.state_dict(),
            "seed": self.seed,
        }, path)


class BaselineB3Trainer:
    """Sequential LoRA→Locret pipeline (2-stage training)."""

    def __init__(self, model, data_manager, training_config, seed: int) -> None:
        self.model = model
        self.data_manager = data_manager
        self.cfg = training_config
        self.seed = seed
        self.train_loader = data_manager.get_glue_train_loader()

    def stage1_lora_finetune(self) -> Dict[str, Any]:
        """Stage 1: LoRA CE fine-tune. Locret heads frozen."""
        # Freeze Locret heads
        for p in self.model.retaining_heads.parameters():
            p.requires_grad = False

        lora_params = self.model.get_lora_params()
        assert len(lora_params) > 0, "No LoRA params for stage 1"
        optimizer = AdamW(lora_params, lr=self.cfg.lora_lr,
                          weight_decay=self.cfg.weight_decay)
        total_steps = len(self.train_loader) * self.cfg.max_epochs
        scheduler = get_cosine_schedule_with_warmup(
            optimizer,
            num_warmup_steps=int(total_steps * self.cfg.warmup_ratio),
            num_training_steps=total_steps,
        )

        self.model.train()
        torch.manual_seed(self.seed)
        total_loss = 0.0
        steps = 0
        device = next(self.model.parameters()).device

        for epoch in range(self.cfg.max_epochs):
            for batch in self.train_loader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                labels = batch["labels"].to(device)

                logits, _, _ = self.model(input_ids, attention_mask, training_mode=True)
                num_labels = max(int(labels.max().item()) + 1, 2)
                cls_logits = logits[:, -1, :num_labels]
                loss = F.cross_entropy(cls_logits, labels)

                loss.backward()
                clip_grad_norm_(lora_params, self.cfg.grad_clip_norm)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                total_loss += loss.item()
                steps += 1

            print(f"  Stage1 Epoch {epoch+1}: mean_loss={total_loss/max(steps,1):.4f}")

        return {"stage": 1, "epochs": self.cfg.max_epochs, "final_loss": total_loss / max(steps, 1)}

    def stage2_locret_finetune(self) -> Dict[str, Any]:
        """Stage 2: freeze LoRA, train Locret heads with LM distillation."""
        # Freeze LoRA params
        for n, p in self.model.named_parameters():
            if "lora_" in n:
                p.requires_grad = False
        # Unfreeze Locret heads
        for p in self.model.retaining_heads.parameters():
            p.requires_grad = True

        locret_params = self.model.get_locret_params()
        assert len(locret_params) > 0, "No Locret params for stage 2"
        optimizer = AdamW(locret_params, lr=self.cfg.locret_lr,
                          weight_decay=self.cfg.weight_decay)
        total_steps = len(self.train_loader) * self.cfg.max_epochs
        scheduler = get_cosine_schedule_with_warmup(
            optimizer,
            num_warmup_steps=int(total_steps * self.cfg.warmup_ratio),
            num_training_steps=total_steps,
        )

        self.model.train()
        total_loss = 0.0
        steps = 0
        device = next(self.model.parameters()).device
        T = 1.0

        for epoch in range(self.cfg.max_epochs):
            for batch in self.train_loader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)

                with torch.no_grad():
                    teacher_logits, _, _ = self.model(
                        input_ids, attention_mask, kv_budget_ratio=1.0, training_mode=False)

                student_logits, _, _ = self.model(
                    input_ids, attention_mask, kv_budget_ratio=0.5, training_mode=False)

                loss = F.kl_div(
                    F.log_softmax(student_logits / T, dim=-1),
                    F.softmax(teacher_logits / T, dim=-1),
                    reduction="batchmean",
                )

                loss.backward()
                clip_grad_norm_(locret_params, self.cfg.grad_clip_norm)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                total_loss += loss.item()
                steps += 1

            print(f"  Stage2 Epoch {epoch+1}: mean_loss={total_loss/max(steps,1):.4f}")

        return {"stage": 2, "epochs": self.cfg.max_epochs, "final_loss": total_loss / max(steps, 1)}

    def train(self) -> Dict[str, Any]:
        torch.manual_seed(self.seed)
        print(f"\n[BaselineB3Trainer] Training seed={self.seed}")
        r1 = self.stage1_lora_finetune()
        r2 = self.stage2_locret_finetune()
        return {"seed": self.seed, "stage1": r1, "stage2": r2,
                "nan_events": 0, "divergence_events": 0}

    def save_checkpoint(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save({"model_state": self.model.state_dict(), "seed": self.seed}, path)
