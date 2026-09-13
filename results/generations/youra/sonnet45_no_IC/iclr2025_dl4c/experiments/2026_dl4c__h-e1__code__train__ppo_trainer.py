"""
PPO Training with Tri-Modal Feedback
Tasks: A-2 (Baseline Models), A-6 (PPO Integration)
"""
import torch
import torch.nn as nn
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Dict, Optional
import json
from pathlib import Path


class SimplifiedPPOTrainer:
    """
    Simplified PPO trainer for PoC
    Integrates tri-modal aggregator into reward computation
    """

    def __init__(
        self,
        model_name: str,
        aggregator,
        feedback_collector,
        learning_rate: float = 5e-5,
        clip_range: float = 0.2,
        device: str = "cuda"
    ):
        self.device = device

        # Load model and tokenizer
        self.model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Reference model for KL penalty
        self.ref_model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
        self.ref_model.eval()

        # Tri-modal components
        self.aggregator = aggregator.to(device)
        self.feedback_collector = feedback_collector

        # Training config
        self.learning_rate = learning_rate
        self.clip_range = clip_range

        # Optimizer
        self.optimizer = torch.optim.Adam(
            list(self.model.parameters()) + list(self.aggregator.parameters()),
            lr=learning_rate
        )

        # Metrics
        self.global_step = 0
        self.total_steps = 0

    def train_step(
        self,
        prompts: list,
        test_cases: list,
        task_ids: list,
        max_new_tokens: int = 256
    ) -> Dict:
        """
        Single PPO training step

        Returns:
            Dict with metrics: loss, reward, kl, weights
        """
        self.model.train()
        self.aggregator.train()

        # Generate code samples
        inputs = self.tokenizer(prompts, return_tensors="pt", padding=True, truncation=True).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.8,
                top_p=0.95,
                pad_token_id=self.tokenizer.eos_token_id
            )

        # Decode generated code
        generated_codes = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)

        # Collect feedback for each sample
        execution_rewards = []
        ai_rewards = []
        human_rewards = []

        for code, prompt, tests, task_id in zip(generated_codes, prompts, test_cases, task_ids):
            feedback = self.feedback_collector.collect_all(
                code=code,
                prompt=prompt,
                test_cases=tests,
                task_id=task_id
            )
            execution_rewards.append(feedback['execution'])
            ai_rewards.append(feedback['ai'])
            human_rewards.append(feedback['human'])

        # Stack rewards
        exec_reward = torch.stack(execution_rewards)
        ai_reward = torch.stack(ai_rewards)
        human_reward = torch.stack(human_rewards)

        # Aggregate with tri-modal mechanism
        training_progress = self.global_step / max(self.total_steps, 1)
        aggregated_reward, weight_info = self.aggregator(
            exec_reward,
            ai_reward,
            human_reward,
            training_progress
        )

        # Simplified PPO loss (PoC version)
        # In full version, this would include proper advantage estimation, value function, etc.
        policy_loss = -aggregated_reward.mean()

        # Backprop
        self.optimizer.zero_grad()
        policy_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
        self.optimizer.step()

        self.global_step += 1

        # Return metrics
        return {
            'loss': policy_loss.item(),
            'reward': aggregated_reward.mean().item(),
            'execution_reward': exec_reward.mean().item(),
            'ai_reward': ai_reward.mean().item(),
            'human_reward': human_reward.mean().item(),
            **weight_info
        }

    def save_checkpoint(self, checkpoint_dir: str):
        """Save model and aggregator checkpoints"""
        checkpoint_dir = Path(checkpoint_dir)
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Save model
        self.model.save_pretrained(checkpoint_dir / "model")
        self.tokenizer.save_pretrained(checkpoint_dir / "model")

        # Save aggregator
        torch.save(self.aggregator.state_dict(), checkpoint_dir / "aggregator.pt")

        print(f"✓ Checkpoint saved to {checkpoint_dir}")


class BaselinePPOTrainer(SimplifiedPPOTrainer):
    """
    Baseline PPO with single feedback source
    Used for comparison (execution-only, human-only, AI-only)
    """

    def __init__(
        self,
        model_name: str,
        feedback_type: str,  # "execution", "human", "ai"
        feedback_collector,
        learning_rate: float = 5e-5,
        clip_range: float = 0.2,
        device: str = "cuda"
    ):
        # Skip aggregator for baselines
        self.feedback_type = feedback_type

        self.device = device
        self.model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.ref_model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
        self.ref_model.eval()

        self.feedback_collector = feedback_collector

        self.learning_rate = learning_rate
        self.clip_range = clip_range

        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)

        self.global_step = 0
        self.total_steps = 0

    def train_step(
        self,
        prompts: list,
        test_cases: list,
        task_ids: list,
        max_new_tokens: int = 256
    ) -> Dict:
        """Training step with single feedback source"""
        self.model.train()

        # Generate code
        inputs = self.tokenizer(prompts, return_tensors="pt", padding=True, truncation=True).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.8,
                top_p=0.95,
                pad_token_id=self.tokenizer.eos_token_id
            )

        generated_codes = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)

        # Collect single feedback type
        rewards = []
        for code, prompt, tests, task_id in zip(generated_codes, prompts, test_cases, task_ids):
            feedback = self.feedback_collector.collect_all(code, prompt, tests, task_id)
            rewards.append(feedback[self.feedback_type])

        reward = torch.stack(rewards)

        # Simplified loss
        policy_loss = -reward.mean()

        self.optimizer.zero_grad()
        policy_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
        self.optimizer.step()

        self.global_step += 1

        return {
            'loss': policy_loss.item(),
            'reward': reward.mean().item(),
            f'{self.feedback_type}_reward': reward.mean().item()
        }


if __name__ == "__main__":
    print("Testing PPO Trainer...")

    from models.tri_modal_aggregator import TriModalAggregator
    from models.feedback_collectors import FeedbackCollector

    # Initialize components
    aggregator = TriModalAggregator()
    collector = FeedbackCollector(device="cpu")

    # Create trainer
    trainer = SimplifiedPPOTrainer(
        model_name="Salesforce/codegen-350M-mono",
        aggregator=aggregator,
        feedback_collector=collector,
        device="cpu"
    )

    # Test step
    prompts = ["Write a function to add two numbers"]
    test_cases = ["assert add(2,3)==5"]
    task_ids = ["test_001"]

    metrics = trainer.train_step(prompts, test_cases, task_ids, max_new_tokens=50)

    print(f"\nMetrics: {metrics}")
    print("\n✓ PPO trainer test passed")
