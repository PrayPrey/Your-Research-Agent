"""
grpo_trainer.py — Minimal GRPO (Group Relative Policy Optimization) implementation.

Implements GRPO as described in DeepSeekMath (Shao et al., 2024):
  L_GRPO = -E[sum_t log π_θ(a_t|s_t) * A_t] + β * KL(π_θ || π_ref)

Where A_t is the group-normalized advantage:
  A_i = (r_i - mean(r_group)) / std(r_group)

This avoids TRL 1.x dependency (requires PyTorch 2.6+).
"""
import json
from pathlib import Path
from typing import Callable

import numpy as np
import torch
import torch.nn.functional as F
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from transformers import AutoModelForCausalLM, AutoTokenizer


class SimpleGRPOTrainer:
    """
    Minimal single-GPU GRPO trainer for RLEF-Fraction experiment.

    Reference: GRPO (Shao et al., 2024) — no value model needed.
    """

    def __init__(
        self,
        model,
        ref_model,
        tokenizer,
        reward_fn: Callable,
        dataset,
        output_dir: str,
        lr: float = 1e-5,
        batch_size: int = 2,
        grad_accum: int = 4,
        num_epochs: int = 1,
        G: int = 4,
        beta: float = 0.04,
        max_new_tokens: int = 256,
        temperature: float = 0.8,
        max_grad_norm: float = 1.0,
        seed: int = 42,
        logging_steps: int = 20,
        reward_log_path: str = "logs/reward_monitoring.jsonl",
    ):
        self.model = model
        self.ref_model = ref_model
        self.tokenizer = tokenizer
        self.reward_fn = reward_fn
        self.dataset = dataset
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.lr = lr
        self.batch_size = batch_size
        self.grad_accum = grad_accum
        self.num_epochs = num_epochs
        self.G = G
        self.beta = beta
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.max_grad_norm = max_grad_norm
        self.seed = seed
        self.logging_steps = logging_steps
        self.reward_log_path = Path(reward_log_path)
        self.reward_log_path.parent.mkdir(parents=True, exist_ok=True)

        self.device = next(model.parameters()).device
        ref_model.eval()
        for p in ref_model.parameters():
            p.requires_grad_(False)

    def _generate_completions(self, prompt_tokens: dict, G: int) -> list:
        """Generate G completions per prompt via sampling."""
        input_ids = prompt_tokens["input_ids"]  # [1, L]
        attention_mask = prompt_tokens["attention_mask"]

        # Repeat for G rollouts
        input_ids = input_ids.repeat(G, 1)
        attention_mask = attention_mask.repeat(G, 1)

        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=self.max_new_tokens,
                do_sample=True,
                temperature=self.temperature,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        # Decode only the generated part
        prompt_len = input_ids.shape[1]
        completions = []
        for i in range(G):
            generated = outputs[i][prompt_len:]
            text = self.tokenizer.decode(generated, skip_special_tokens=True)
            completions.append(text)
        return completions

    def _compute_log_probs(self, model, input_ids, attention_mask, labels):
        """Compute per-token log probabilities for the completion tokens."""
        with torch.cuda.amp.autocast(dtype=torch.bfloat16):
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits  # [B, L, V]
        # Shift: labels are input_ids[1:], logits are [:-1]
        shift_logits = logits[:, :-1, :]
        shift_labels = labels[:, 1:]
        log_probs = F.log_softmax(shift_logits, dim=-1)
        # Gather log probs for actual tokens
        token_log_probs = log_probs.gather(-1, shift_labels.unsqueeze(-1)).squeeze(-1)
        return token_log_probs  # [B, L-1]

    def _grpo_loss(self, prompt_ids, completions, rewards, metadata_batch):
        """
        Compute GRPO loss for one prompt with G completions.

        rewards: list[float] of length G (from reward_fn)
        Returns: scalar loss
        """
        rewards_tensor = torch.tensor(rewards, dtype=torch.float32)

        # Group-normalize advantages
        if rewards_tensor.std() > 1e-8:
            advantages = (rewards_tensor - rewards_tensor.mean()) / (rewards_tensor.std() + 1e-8)
        else:
            advantages = rewards_tensor - rewards_tensor.mean()

        prompt_len = prompt_ids.shape[1]
        total_loss = torch.tensor(0.0, device=self.device, requires_grad=True)
        valid_count = 0

        for i, (completion, adv) in enumerate(zip(completions, advantages)):
            # Tokenize completion
            comp_ids = self.tokenizer(
                completion,
                return_tensors="pt",
                max_length=self.max_new_tokens,
                truncation=True,
                add_special_tokens=False,
            ).input_ids.to(self.device)

            if comp_ids.shape[1] == 0:
                continue

            # Full sequence: [prompt | completion]
            full_ids = torch.cat([prompt_ids, comp_ids], dim=1)
            attn_mask = torch.ones_like(full_ids)
            labels = full_ids.clone()
            labels[:, :prompt_len] = -100  # Don't compute loss on prompt

            # Policy log probs
            with torch.cuda.amp.autocast(dtype=torch.bfloat16):
                policy_out = self.model(input_ids=full_ids, attention_mask=attn_mask)
            policy_logits = policy_out.logits[:, prompt_len - 1:-1, :]  # completion logits
            policy_log_probs = F.log_softmax(policy_logits, dim=-1)
            comp_token_lp = policy_log_probs.gather(-1, comp_ids.unsqueeze(-1)).squeeze(-1).sum()

            # Reference log probs (for KL)
            with torch.no_grad():
                with torch.cuda.amp.autocast(dtype=torch.bfloat16):
                    ref_out = self.ref_model(input_ids=full_ids, attention_mask=attn_mask)
            ref_logits = ref_out.logits[:, prompt_len - 1:-1, :]
            ref_log_probs = F.log_softmax(ref_logits, dim=-1)
            ref_token_lp = ref_log_probs.gather(-1, comp_ids.unsqueeze(-1)).squeeze(-1).sum()

            # KL penalty: KL(π || π_ref) ≈ log π - log π_ref
            kl = comp_token_lp - ref_token_lp

            # GRPO objective: maximize advantage-weighted log prob, penalize KL
            # loss = -adv * log_prob + beta * KL  (minimize)
            adv_val = adv.item()
            sample_loss = -adv_val * comp_token_lp + self.beta * kl
            total_loss = total_loss + sample_loss
            valid_count += 1

        if valid_count == 0:
            return torch.tensor(0.0, device=self.device, requires_grad=True)
        return total_loss / valid_count

    def train(self) -> str:
        """Run GRPO training. Returns output_dir path."""
        torch.manual_seed(self.seed)

        optimizer = AdamW(self.model.parameters(), lr=self.lr)
        n_steps = (len(self.dataset) // self.batch_size) * self.num_epochs
        scheduler = CosineAnnealingLR(optimizer, T_max=n_steps)

        global_step = 0
        self.model.train()

        for epoch in range(self.num_epochs):
            # Shuffle dataset indices
            indices = list(range(len(self.dataset)))
            rng = np.random.default_rng(self.seed + epoch)
            rng.shuffle(indices)

            optimizer.zero_grad()
            accum_loss = 0.0
            accum_rewards_by_difficulty = {"intro": [], "interview": [], "competition": []}

            for batch_start in range(0, len(indices), self.batch_size):
                batch_indices = indices[batch_start:batch_start + self.batch_size]
                batch_loss = torch.tensor(0.0, device=self.device)
                n_in_batch = 0

                for idx in batch_indices:
                    sample = self.dataset[idx]
                    prompt = sample["prompt"]
                    test_cases = sample["test_cases"]
                    difficulty = sample.get("difficulty", "interview")

                    # Tokenize prompt
                    enc = self.tokenizer(
                        prompt, return_tensors="pt", max_length=512, truncation=True
                    ).to(self.device)
                    prompt_ids = enc["input_ids"]

                    # Generate G completions
                    completions = self._generate_completions(enc, self.G)

                    # Compute rewards
                    meta = [{"test_cases": test_cases}] * self.G
                    rewards = self.reward_fn(
                        completions=completions,
                        prompts=[prompt] * self.G,
                        metadata=meta,
                    )

                    # Log rewards by difficulty
                    for r in rewards:
                        if difficulty in accum_rewards_by_difficulty:
                            accum_rewards_by_difficulty[difficulty].append(r)

                    # GRPO loss
                    loss = self._grpo_loss(prompt_ids, completions, rewards, meta)
                    batch_loss = batch_loss + loss / (len(batch_indices) * self.grad_accum)
                    n_in_batch += 1

                batch_loss.backward()
                accum_loss += batch_loss.item()

                # Gradient accumulation
                if (batch_start // self.batch_size + 1) % self.grad_accum == 0:
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.max_grad_norm)
                    optimizer.step()
                    scheduler.step()
                    optimizer.zero_grad()
                    global_step += 1

                    if global_step % self.logging_steps == 0:
                        def _mean(lst): return sum(lst) / len(lst) if lst else None
                        record = {
                            "step": global_step,
                            "loss": accum_loss,
                            "intro_reward": _mean(accum_rewards_by_difficulty["intro"]),
                            "interview_reward": _mean(accum_rewards_by_difficulty["interview"]),
                            "competition_reward": _mean(accum_rewards_by_difficulty["competition"]),
                        }
                        with open(self.reward_log_path, "a") as f:
                            f.write(json.dumps(record) + "\n")
                        print(f"Step {global_step}: loss={accum_loss:.4f}, "
                              f"int_r={record['intro_reward']}, "
                              f"ivw_r={record['interview_reward']}")
                        accum_loss = 0.0
                        accum_rewards_by_difficulty = {k: [] for k in accum_rewards_by_difficulty}

        # Save model
        self.model.save_pretrained(str(self.output_dir))
        self.tokenizer.save_pretrained(str(self.output_dir))
        print(f"✓ RLEF model saved: {self.output_dir}")
        return str(self.output_dir)
