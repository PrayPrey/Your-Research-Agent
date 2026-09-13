"""
Training utilities for EmbedPrint.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import AdamW
from torch.cuda.amp import GradScaler, autocast
from transformers import get_linear_schedule_with_warmup
from tqdm import tqdm
import numpy as np
import logging
import time
from typing import Dict, List, Tuple, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbedPrintTrainer:
    """Trainer for EmbedPrint model."""

    def __init__(
        self,
        model,
        config,
        train_loader,
        eval_loader,
        device: str = "cuda",
    ):
        self.model = model.to(device)
        self.config = config
        self.train_loader = train_loader
        self.eval_loader = eval_loader
        self.device = device

        # Separate parameter groups for model and signatures
        model_params = []
        signature_params = []
        for name, param in model.named_parameters():
            if "signature" in name:
                signature_params.append(param)
            else:
                model_params.append(param)

        self.optimizer = AdamW(
            [
                {"params": model_params, "lr": config.learning_rate},
                {"params": signature_params, "lr": config.fingerprint_lr},
            ],
            weight_decay=0.01,
        )

        total_steps = len(train_loader) * config.num_epochs
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=total_steps // 10,
            num_training_steps=total_steps,
        )

        self.scaler = GradScaler() if config.use_fp16 else None

        # Training history
        self.history = {
            "train_loss": [],
            "train_lm_loss": [],
            "train_fp_loss": [],
            "eval_loss": [],
            "eval_perplexity": [],
            "attribution_accuracy": [],
            "epoch_times": [],
        }

        # Checkpoints for TracIn
        self.checkpoints = []

    def train_epoch(self, epoch: int) -> Dict[str, float]:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0.0
        total_lm_loss = 0.0
        total_fp_loss = 0.0
        num_batches = 0

        pbar = tqdm(self.train_loader, desc=f"Epoch {epoch+1}")
        for batch in pbar:
            input_ids = batch["input_ids"].to(self.device)
            attention_mask = batch["attention_mask"].to(self.device)
            cluster_ids = batch["cluster_id"].to(self.device)

            self.optimizer.zero_grad()

            if self.config.use_fp16:
                with autocast():
                    outputs = self.model(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        cluster_ids=cluster_ids,
                    )
                    lm_loss = outputs["lm_loss"]
                    fp_loss = outputs["fp_loss"]
                    loss = lm_loss + self.config.lambda_fp * fp_loss

                self.scaler.scale(loss).backward()
                self.scaler.unscale_(self.optimizer)
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    cluster_ids=cluster_ids,
                )
                lm_loss = outputs["lm_loss"]
                fp_loss = outputs["fp_loss"]
                loss = lm_loss + self.config.lambda_fp * fp_loss

                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.optimizer.step()

            self.scheduler.step()

            total_loss += loss.item()
            total_lm_loss += lm_loss.item()
            total_fp_loss += fp_loss.item()
            num_batches += 1

            pbar.set_postfix(
                {
                    "loss": f"{loss.item():.4f}",
                    "lm": f"{lm_loss.item():.4f}",
                    "fp": f"{fp_loss.item():.4f}",
                }
            )

        return {
            "train_loss": total_loss / num_batches,
            "train_lm_loss": total_lm_loss / num_batches,
            "train_fp_loss": total_fp_loss / num_batches,
        }

    @torch.no_grad()
    def evaluate(self) -> Dict[str, float]:
        """Evaluate the model."""
        self.model.eval()
        total_loss = 0.0
        num_batches = 0

        for batch in tqdm(self.eval_loader, desc="Evaluating"):
            input_ids = batch["input_ids"].to(self.device)
            attention_mask = batch["attention_mask"].to(self.device)

            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            total_loss += outputs["lm_loss"].item()
            num_batches += 1

        avg_loss = total_loss / num_batches
        perplexity = np.exp(avg_loss)

        return {
            "eval_loss": avg_loss,
            "eval_perplexity": perplexity,
        }

    @torch.no_grad()
    def evaluate_attribution(
        self,
        train_texts: List[str],
        cluster_ids: np.ndarray,
        is_canary: np.ndarray,
        tokenizer,
        top_k_values: List[int] = [1, 5, 10],
    ) -> Dict[str, float]:
        """Evaluate attribution accuracy on canary samples."""
        self.model.eval()

        # Get canary indices
        canary_indices = np.where(is_canary)[0]
        if len(canary_indices) == 0:
            return {}

        results = {}

        for k in top_k_values:
            correct = 0
            total = 0

            for idx in canary_indices:
                text = train_texts[idx]
                true_cluster = cluster_ids[idx]

                # Tokenize
                encoding = tokenizer(
                    text,
                    max_length=self.config.max_seq_length,
                    padding="max_length",
                    truncation=True,
                    return_tensors="pt",
                )

                input_ids = encoding["input_ids"].to(self.device)
                attention_mask = encoding["attention_mask"].to(self.device)

                # Get attribution
                outputs = self.model(input_ids, attention_mask, return_attribution=True)
                attr_scores = outputs["attribution_scores"][0]

                # Get top-k predicted clusters
                top_k_clusters = torch.topk(attr_scores, k).indices.cpu().numpy()

                if true_cluster in top_k_clusters:
                    correct += 1
                total += 1

            results[f"precision@{k}"] = correct / total if total > 0 else 0.0

        return results

    def save_checkpoint(self, epoch: int, path: str):
        """Save model checkpoint."""
        checkpoint = {
            "epoch": epoch,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "history": self.history,
        }
        torch.save(checkpoint, path)
        logger.info(f"Saved checkpoint to {path}")

    def train(
        self,
        train_texts: List[str],
        cluster_ids: np.ndarray,
        is_canary: np.ndarray,
        tokenizer,
    ) -> Dict[str, List[float]]:
        """Full training loop."""
        logger.info("Starting training...")

        for epoch in range(self.config.num_epochs):
            start_time = time.time()

            # Train
            train_metrics = self.train_epoch(epoch)
            self.history["train_loss"].append(train_metrics["train_loss"])
            self.history["train_lm_loss"].append(train_metrics["train_lm_loss"])
            self.history["train_fp_loss"].append(train_metrics["train_fp_loss"])

            # Evaluate
            eval_metrics = self.evaluate()
            self.history["eval_loss"].append(eval_metrics["eval_loss"])
            self.history["eval_perplexity"].append(eval_metrics["eval_perplexity"])

            # Evaluate attribution
            attr_metrics = self.evaluate_attribution(
                train_texts, cluster_ids, is_canary, tokenizer, self.config.top_k_values
            )

            # Store precision@10 as main attribution metric
            if "precision@10" in attr_metrics:
                self.history["attribution_accuracy"].append(attr_metrics["precision@10"])

            epoch_time = time.time() - start_time
            self.history["epoch_times"].append(epoch_time)

            logger.info(
                f"Epoch {epoch+1}/{self.config.num_epochs} - "
                f"Train Loss: {train_metrics['train_loss']:.4f}, "
                f"LM Loss: {train_metrics['train_lm_loss']:.4f}, "
                f"FP Loss: {train_metrics['train_fp_loss']:.4f}, "
                f"Eval PPL: {eval_metrics['eval_perplexity']:.2f}, "
                f"Attr P@10: {attr_metrics.get('precision@10', 0):.3f}, "
                f"Time: {epoch_time:.1f}s"
            )

            # Save checkpoint for TracIn baseline
            self.checkpoints.append(
                {
                    "epoch": epoch,
                    "state_dict": {k: v.clone() for k, v in self.model.state_dict().items()},
                }
            )

        return self.history


class BaselineTrainer:
    """Trainer for baseline LM without fingerprints."""

    def __init__(
        self,
        model,
        config,
        train_loader,
        eval_loader,
        device: str = "cuda",
    ):
        self.model = model.to(device)
        self.config = config
        self.train_loader = train_loader
        self.eval_loader = eval_loader
        self.device = device

        self.optimizer = AdamW(model.parameters(), lr=config.learning_rate, weight_decay=0.01)

        total_steps = len(train_loader) * config.num_epochs
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=total_steps // 10,
            num_training_steps=total_steps,
        )

        self.scaler = GradScaler() if config.use_fp16 else None

        self.history = {
            "train_loss": [],
            "eval_loss": [],
            "eval_perplexity": [],
            "epoch_times": [],
        }

    def train_epoch(self, epoch: int) -> Dict[str, float]:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0.0
        num_batches = 0

        pbar = tqdm(self.train_loader, desc=f"Baseline Epoch {epoch+1}")
        for batch in pbar:
            input_ids = batch["input_ids"].to(self.device)
            attention_mask = batch["attention_mask"].to(self.device)

            self.optimizer.zero_grad()

            if self.config.use_fp16:
                with autocast():
                    outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                    logits = outputs.logits
                    shift_logits = logits[..., :-1, :].contiguous()
                    shift_labels = input_ids[..., 1:].contiguous()
                    loss = F.cross_entropy(
                        shift_logits.view(-1, shift_logits.size(-1)),
                        shift_labels.view(-1),
                        ignore_index=-100,
                    )

                self.scaler.scale(loss).backward()
                self.scaler.unscale_(self.optimizer)
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                logits = outputs.logits
                shift_logits = logits[..., :-1, :].contiguous()
                shift_labels = input_ids[..., 1:].contiguous()
                loss = F.cross_entropy(
                    shift_logits.view(-1, shift_logits.size(-1)),
                    shift_labels.view(-1),
                    ignore_index=-100,
                )

                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.optimizer.step()

            self.scheduler.step()

            total_loss += loss.item()
            num_batches += 1

            pbar.set_postfix({"loss": f"{loss.item():.4f}"})

        return {"train_loss": total_loss / num_batches}

    @torch.no_grad()
    def evaluate(self) -> Dict[str, float]:
        """Evaluate the model."""
        self.model.eval()
        total_loss = 0.0
        num_batches = 0

        for batch in tqdm(self.eval_loader, desc="Evaluating Baseline"):
            input_ids = batch["input_ids"].to(self.device)
            attention_mask = batch["attention_mask"].to(self.device)

            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = input_ids[..., 1:].contiguous()
            loss = F.cross_entropy(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1),
                ignore_index=-100,
            )
            total_loss += loss.item()
            num_batches += 1

        avg_loss = total_loss / num_batches
        perplexity = np.exp(avg_loss)

        return {
            "eval_loss": avg_loss,
            "eval_perplexity": perplexity,
        }

    def train(self) -> Dict[str, List[float]]:
        """Full training loop."""
        logger.info("Starting baseline training...")

        for epoch in range(self.config.num_epochs):
            start_time = time.time()

            train_metrics = self.train_epoch(epoch)
            self.history["train_loss"].append(train_metrics["train_loss"])

            eval_metrics = self.evaluate()
            self.history["eval_loss"].append(eval_metrics["eval_loss"])
            self.history["eval_perplexity"].append(eval_metrics["eval_perplexity"])

            epoch_time = time.time() - start_time
            self.history["epoch_times"].append(epoch_time)

            logger.info(
                f"Epoch {epoch+1}/{self.config.num_epochs} - "
                f"Train Loss: {train_metrics['train_loss']:.4f}, "
                f"Eval PPL: {eval_metrics['eval_perplexity']:.2f}, "
                f"Time: {epoch_time:.1f}s"
            )

        return self.history
