"""CodeT5-large model with PPO policy/value heads."""
import torch
import torch.nn as nn
from transformers import T5ForConditionalGeneration, AutoTokenizer
from config import MODEL_NAME, MAX_OUTPUT_LEN


class ValueHead(nn.Module):
    """Value head for PPO actor-critic."""

    def __init__(self, hidden_size: int = 512):  # 512 for codet5-small, 1024 for large
        super().__init__()
        self.linear = nn.Linear(hidden_size, 1)

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        return self.linear(hidden_states).squeeze(-1)


class PPOPolicy(nn.Module):
    """CodeT5-large with PPO training support."""

    def __init__(self, pretrained: str = MODEL_NAME):
        super().__init__()
        self.model = T5ForConditionalGeneration.from_pretrained(pretrained)
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained)
        self.value_head = ValueHead(self.model.config.d_model)

    def forward(
        self,
        input_ids: torch.Tensor,
        decoder_input_ids: torch.Tensor,
        attention_mask: torch.Tensor = None,
    ):
        outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            decoder_input_ids=decoder_input_ids,
            output_hidden_states=True,
        )
        logits = outputs.logits
        decoder_hidden = outputs.decoder_hidden_states[-1]
        values = self.value_head(decoder_hidden)
        return logits, values

    def generate(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor = None,
        max_new_tokens: int = MAX_OUTPUT_LEN,
        do_sample: bool = True,
        temperature: float = 0.8,
    ) -> torch.Tensor:
        return self.model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=max_new_tokens,
            do_sample=do_sample,
            temperature=temperature,
            pad_token_id=self.tokenizer.pad_token_id,
        )

    def get_logprobs(
        self,
        input_ids: torch.Tensor,
        decoder_input_ids: torch.Tensor,
        attention_mask: torch.Tensor = None,
    ) -> torch.Tensor:
        logits, _ = self.forward(input_ids, decoder_input_ids, attention_mask)
        log_probs = torch.log_softmax(logits, dim=-1)
        token_log_probs = torch.gather(
            log_probs[:, :-1, :],
            dim=2,
            index=decoder_input_ids[:, 1:].unsqueeze(-1)
        ).squeeze(-1)
        return token_log_probs


def compute_advantages(
    rewards: torch.Tensor,
    values: torch.Tensor,
    gamma: float = 1.0,
    lam: float = 0.95,
):
    """GAE advantage estimation."""
    advantages = torch.zeros_like(rewards)
    last_gae = 0

    for t in reversed(range(rewards.shape[1])):
        if t == rewards.shape[1] - 1:
            next_value = 0
        else:
            next_value = values[:, t + 1]

        delta = rewards[:, t] + gamma * next_value - values[:, t]
        advantages[:, t] = last_gae = delta + gamma * lam * last_gae

    returns = advantages + values
    return advantages, returns


def ppo_step(
    policy: PPOPolicy,
    optimizer: torch.optim.AdamW,
    input_ids: torch.Tensor,
    attention_mask: torch.Tensor,
    old_decoder_ids: torch.Tensor,
    old_log_probs: torch.Tensor,
    rewards: torch.Tensor,
    clip_eps: float = 0.2,
    entropy_coef: float = 0.01,
    value_coef: float = 0.5,
):
    """Single PPO update step."""
    logits, values = policy.forward(input_ids, old_decoder_ids, attention_mask)

    log_probs = torch.log_softmax(logits, dim=-1)
    new_log_probs = torch.gather(
        log_probs[:, :-1, :],
        dim=2,
        index=old_decoder_ids[:, 1:].unsqueeze(-1)
    ).squeeze(-1)

    seq_len = min(new_log_probs.shape[1], old_log_probs.shape[1], rewards.shape[1] - 1, values.shape[1] - 1)
    new_log_probs = new_log_probs[:, :seq_len]
    old_log_probs_trimmed = old_log_probs[:, :seq_len]
    rewards_trimmed = rewards[:, :seq_len]
    values_trimmed = values[:, :seq_len]

    advantages, returns = compute_advantages(rewards_trimmed, values_trimmed)
    advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

    ratio = torch.exp(new_log_probs - old_log_probs_trimmed)
    surr1 = ratio * advantages
    surr2 = torch.clamp(ratio, 1 - clip_eps, 1 + clip_eps) * advantages
    policy_loss = -torch.min(surr1, surr2).mean()

    value_loss = nn.functional.mse_loss(values_trimmed, returns)

    probs = torch.softmax(logits, dim=-1)
    entropy = -(probs * log_probs).sum(dim=-1).mean()

    loss = policy_loss + value_coef * value_loss - entropy_coef * entropy

    optimizer.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_norm_(policy.parameters(), 1.0)
    optimizer.step()

    return {
        "loss": loss.item(),
        "policy_loss": policy_loss.item(),
        "value_loss": value_loss.item(),
        "entropy": entropy.item(),
        "reward_mean": rewards.mean().item(),
    }
