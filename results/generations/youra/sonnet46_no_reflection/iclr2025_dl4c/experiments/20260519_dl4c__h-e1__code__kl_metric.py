import os
import json
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM


def compute_kl_divergence(
    model: AutoModelForCausalLM,
    ref_model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    prompts: list,
    device: str = "cuda",
    max_new_tokens: int = 200,
) -> float:
    """Monte Carlo KL divergence: E_ref[log p_ref / p_model].
    Per-prompt, no batching to avoid OOM on 7B.
    Returns mean KL over prompts.
    """
    model.eval()
    ref_model.eval()
    kl_values = []

    with torch.no_grad():
        for prompt in prompts:
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(device)
            input_len = inputs["input_ids"].shape[1]

            # Generate continuation from ref model
            gen = ref_model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=1.0,
                pad_token_id=tokenizer.eos_token_id,
            )
            # Only continuation tokens
            continuation = gen[:, input_len:]
            if continuation.shape[1] == 0:
                continue

            full_ids = gen
            # ref logprobs
            ref_out = ref_model(full_ids)
            ref_logits = ref_out.logits[:, input_len - 1:-1, :]  # [1, T, V]
            ref_logprobs = torch.log_softmax(ref_logits, dim=-1)
            ref_token_logprobs = ref_logprobs[0, torch.arange(continuation.shape[1]), continuation[0]]

            # model logprobs
            model_out = model(full_ids)
            model_logits = model_out.logits[:, input_len - 1:-1, :]
            model_logprobs = torch.log_softmax(model_logits, dim=-1)
            model_token_logprobs = model_logprobs[0, torch.arange(continuation.shape[1]), continuation[0]]

            # KL = sum_t (log p_ref - log p_model)
            kl = (ref_token_logprobs - model_token_logprobs).sum().item()
            kl_values.append(kl)

    return float(np.mean(kl_values)) if kl_values else float("nan")


def load_checkpoint_kl_log(checkpoint_dir: str) -> list:
    """Load KL log from checkpoint directory.
    Returns list of dicts: [{step, kl_divergence}, ...]
    """
    kl_log_path = os.path.join(checkpoint_dir, "kl_log.json")
    if not os.path.exists(kl_log_path):
        return []
    with open(kl_log_path) as f:
        return json.load(f)


def save_kl_log(checkpoint_dir: str, kl_log: list) -> None:
    os.makedirs(checkpoint_dir, exist_ok=True)
    with open(os.path.join(checkpoint_dir, "kl_log.json"), "w") as f:
        json.dump(kl_log, f, indent=2)


def match_checkpoints(
    grpo_kl_log: list,
    dpo_kl_log: list,
    tolerance: float = 0.05,
) -> list:
    """Find (grpo_step, dpo_step) pairs with |kl_grpo - kl_dpo| <= tolerance.
    Returns list of dicts: [{grpo_step, dpo_step, kl_grpo, kl_dpo}, ...]
    """
    matched = []
    for g_entry in grpo_kl_log:
        g_kl = g_entry["kl_divergence"]
        for d_entry in dpo_kl_log:
            d_kl = d_entry["kl_divergence"]
            if abs(g_kl - d_kl) <= tolerance:
                matched.append({
                    "grpo_step": g_entry["step"],
                    "dpo_step": d_entry["step"],
                    "kl_grpo": g_kl,
                    "kl_dpo": d_kl,
                })
    return matched
