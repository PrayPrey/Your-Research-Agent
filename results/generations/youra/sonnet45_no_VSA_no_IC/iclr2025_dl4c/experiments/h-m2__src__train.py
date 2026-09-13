"""Training engine for SFT baseline and GRPO RLVR."""

import torch
import torch.nn as nn
import logging
import os
import random
import numpy as np
from tqdm import tqdm
from transformers import Trainer, TrainingArguments, DataCollatorForLanguageModeling
from datasets import Dataset
from typing import List, Dict, Optional
from sandbox import ExecutionSandbox
from dynamics_logger import DynamicsLogger

logger = logging.getLogger(__name__)

def compute_gradient_variance(model: nn.Module) -> float:
    """Compute mean std of gradients across all trainable parameters."""
    grad_stds = []
    for param in model.parameters():
        if param.requires_grad and param.grad is not None:
            grad_stds.append(param.grad.std().item())

    if len(grad_stds) == 0:
        return -1.0  # Sentinel value

    mean_std = np.mean(grad_stds)
    if np.isnan(mean_std):
        return -1.0

    return mean_std

def compute_gradient_norm(model: nn.Module) -> float:
    """Compute L2 norm of gradients."""
    total_norm = 0.0
    for param in model.parameters():
        if param.requires_grad and param.grad is not None:
            total_norm += param.grad.norm(2).item() ** 2

    return np.sqrt(total_norm) if total_norm > 0 else -1.0

class SFTTrainer:
    def __init__(self, config: dict, model, tokenizer):
        self.config = config
        self.model = model
        self.tokenizer = tokenizer
        self.sft_config = config["training"]["sft"]

    def train(self, sft_pairs: List[Dict]) -> str:
        """Supervised fine-tuning on (prompt, solution) pairs."""
        logger.info("Starting SFT training...")

        def tokenize_function(examples):
            texts = [p + s for p, s in zip(examples["prompt"], examples["solution"])]
            return self.tokenizer(texts, truncation=True, max_length=512, padding="max_length")

        dataset_dict = {
            "prompt": [pair["prompt"] for pair in sft_pairs],
            "solution": [pair["solution"] for pair in sft_pairs]
        }
        dataset = Dataset.from_dict(dataset_dict)
        tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["prompt", "solution"])

        os.makedirs(self.sft_config["checkpoint_dir"], exist_ok=True)

        training_args = TrainingArguments(
            output_dir=self.sft_config["checkpoint_dir"],
            num_train_epochs=self.sft_config["epochs"],
            per_device_train_batch_size=self.sft_config["batch_size"],
            gradient_accumulation_steps=self.sft_config["gradient_accumulation_steps"],
            learning_rate=self.sft_config["learning_rate"],
            weight_decay=self.sft_config["weight_decay"],
            warmup_steps=self.sft_config["warmup_steps"],
            lr_scheduler_type=self.sft_config["lr_scheduler"],
            max_grad_norm=self.sft_config["max_grad_norm"],
            logging_steps=self.sft_config["log_interval"],
            save_steps=self.sft_config["save_interval"],
            fp16=self.config["hardware"]["fp16"],
            report_to="none",
            save_total_limit=3
        )

        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator
        )

        trainer.train()

        final_checkpoint = os.path.join(self.sft_config["checkpoint_dir"], "final_checkpoint.pt")
        torch.save({
            "model_state_dict": self.model.state_dict(),
            "config": self.config
        }, final_checkpoint)

        logger.info(f"SFT training complete. Checkpoint saved to {final_checkpoint}")
        return final_checkpoint


class GRPOTrainer:
    def __init__(self, config: dict, policy_model, ref_model, tokenizer, sandbox: ExecutionSandbox, dynamics_logger: Optional[DynamicsLogger] = None):
        self.config = config
        self.policy = policy_model
        self.ref = ref_model
        self.tokenizer = tokenizer
        self.sandbox = sandbox
        self.device = policy_model.device
        self.dynamics_logger = dynamics_logger
        self.global_step = 0

    def train(self, test_suites: List[Dict], reward_type: str, grpo_config: dict) -> str:
        """GRPO training with execution rewards."""
        logger.info(f"Starting GRPO training with {reward_type} rewards...")

        if self.dynamics_logger:
            self.dynamics_logger.log_epoch({"epoch": 0, "feedback_type": reward_type, "eval_loss": 0.0, "eval_reward_mean": 0.0, "eval_pass@1": 0.0})

        optimizer = torch.optim.AdamW(
            self.policy.parameters(),
            lr=grpo_config.get("learning_rate", 2e-7),
            weight_decay=grpo_config.get("weight_decay", 0.01)
        )

        os.makedirs(grpo_config["checkpoint_dir"], exist_ok=True)

        reward_history = []
        for step in range(grpo_config["steps"]):
            batch = random.sample(test_suites, k=grpo_config["batch_size"])

            all_rewards = []
            all_advantages = []

            for problem in batch:
                inputs = self.tokenizer(problem["prompt"], return_tensors="pt", padding=True, truncation=True).to(self.device)

                with torch.no_grad():
                    outputs = self.policy.generate(
                        **inputs,
                        max_new_tokens=self.config["generation"]["training"]["max_new_tokens"],
                        temperature=self.config["generation"]["training"]["temperature"],
                        top_p=self.config["generation"]["training"]["top_p"],
                        do_sample=self.config["generation"]["training"]["do_sample"],
                        num_return_sequences=grpo_config["samples_per_problem"],
                        pad_token_id=self.tokenizer.pad_token_id
                    )

                samples = [self.tokenizer.decode(o, skip_special_tokens=True).replace(problem["prompt"], "").strip() for o in outputs]

                rewards = self.sandbox.batch_compute_rewards(samples, problem, reward_type)

                mean_reward = np.mean(rewards)
                std_reward = np.std(rewards) + 1e-8
                advantages = [(r - mean_reward) / std_reward for r in rewards]

                all_rewards.extend(rewards)
                all_advantages.extend(advantages)

            mean_batch_reward = np.mean(all_rewards)
            reward_history.append(mean_batch_reward)

            loss = -torch.tensor(np.mean(all_advantages), dtype=torch.float32, device=self.device)

            optimizer.zero_grad()
            loss.backward()

            grad_variance = compute_gradient_variance(self.policy)
            grad_norm = compute_gradient_norm(self.policy)

            if self.dynamics_logger:
                try:
                    self.dynamics_logger.log_batch({
                        "step": self.global_step,
                        "grad_variance": grad_variance,
                        "grad_norm": grad_norm,
                        "reward_mean": mean_batch_reward,
                        "loss": loss.item()
                    })
                except Exception as e:
                    logger.warning(f"Dynamics logging failed: {e}. Continuing training.")

            torch.nn.utils.clip_grad_norm_(self.policy.parameters(), grpo_config["max_grad_norm"])
            optimizer.step()
            self.global_step += 1

            if step % grpo_config["log_interval"] == 0:
                logger.info(f"Step {step}/{grpo_config['steps']}: mean_reward={mean_batch_reward:.3f}, loss={loss.item():.3f}, grad_var={grad_variance:.6f}")

            if step % grpo_config["save_interval"] == 0:
                checkpoint_path = os.path.join(grpo_config["checkpoint_dir"], f"checkpoint_step_{step}.pt")
                torch.save({
                    "model_state_dict": self.policy.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "step": step,
                    "config": self.config
                }, checkpoint_path)

            if grpo_config.get("early_stopping", {}).get("enabled", False):
                patience = grpo_config["early_stopping"]["patience"]
                min_reward = grpo_config["early_stopping"]["min_reward"]
                if len(reward_history) >= patience:
                    recent_mean = np.mean(reward_history[-patience:])
                    if recent_mean < min_reward:
                        logger.warning(f"Early stopping: mean reward {recent_mean:.3f} < {min_reward} for {patience} steps")
                        break

        final_checkpoint = os.path.join(grpo_config["checkpoint_dir"], "final_checkpoint.pt")
        torch.save({
            "model_state_dict": self.policy.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "step": step,
            "config": self.config
        }, final_checkpoint)

        logger.info(f"GRPO training complete. Checkpoint saved to {final_checkpoint}")
        return final_checkpoint
