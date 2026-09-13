"""Win-rate evaluation for DPO policy."""
import numpy as np
from tqdm import tqdm
import sys
sys.path.insert(0, "..")
from model import compute_dpo_implicit_reward, generate


def compute_win_rates(
    policy, ref_model, tokenizer,
    eval_prompts: list, beta: float, device: str, max_new_tokens: int = 128
) -> dict:
    """Compute win-rate of policy vs reference via implicit rewards."""
    wins = 0
    total = 0
    for prompt in tqdm(eval_prompts[:100], desc="Win-rate eval"):
        policy_response = generate(policy, tokenizer, prompt, device, max_new_tokens)
        ref_response = generate(ref_model, tokenizer, prompt, device, max_new_tokens)
        policy_text = prompt + policy_response
        ref_text = prompt + ref_response
        policy_reward = compute_dpo_implicit_reward(policy, ref_model, tokenizer, policy_text, beta, device)
        ref_reward = compute_dpo_implicit_reward(policy, ref_model, tokenizer, ref_text, beta, device)
        if policy_reward > ref_reward:
            wins += 1
        total += 1
    return {"win_rate": float(wins / total) if total > 0 else 0.0}
