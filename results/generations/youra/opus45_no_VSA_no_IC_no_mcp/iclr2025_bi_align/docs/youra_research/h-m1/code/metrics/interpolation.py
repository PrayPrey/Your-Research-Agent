"""Interpolation behavior analysis."""
import torch
import numpy as np
from tqdm import tqdm
import sys
sys.path.insert(0, "..")
from model import get_reward


def interpolate_embeddings(model, tokenizer, chosen: str, rejected: str, alpha: float, device: str, max_length: int = 512) -> float:
    """Compute reward at embedding-space convex combination."""
    model.eval()

    tok_c = tokenizer(chosen, return_tensors="pt", truncation=True, max_length=max_length, padding="max_length")
    tok_r = tokenizer(rejected, return_tensors="pt", truncation=True, max_length=max_length, padding="max_length")

    tok_c = {k: v.to(device) for k, v in tok_c.items()}
    tok_r = {k: v.to(device) for k, v in tok_r.items()}

    emb_c = model.get_input_embeddings()(tok_c["input_ids"])
    emb_r = model.get_input_embeddings()(tok_r["input_ids"])

    mixed_emb = (1 - alpha) * emb_r + alpha * emb_c
    mixed_mask = torch.maximum(tok_c["attention_mask"], tok_r["attention_mask"])

    if hasattr(model, "base_model"):
        base = model.base_model
    else:
        base = model

    with torch.no_grad():
        outputs = base(inputs_embeds=mixed_emb, attention_mask=mixed_mask)

    return outputs.logits.squeeze().item()


def test_interpolation(model, tokenizer, pairs: list, device: str, n_steps: int = 10) -> dict:
    """Test interpolation smoothness. Returns mean/max deviation from linear."""
    errors = []

    all_rewards = []
    for chosen, rejected in pairs[:100]:
        all_rewards.append(get_reward(model, tokenizer, chosen, device))
        all_rewards.append(get_reward(model, tokenizer, rejected, device))
    reward_range = max(all_rewards) - min(all_rewards)
    reward_range = max(reward_range, 1e-6)

    for chosen, rejected in tqdm(pairs[:200], desc="Testing interpolation"):
        r_chosen = get_reward(model, tokenizer, chosen, device)
        r_rejected = get_reward(model, tokenizer, rejected, device)

        expected = np.linspace(r_rejected, r_chosen, n_steps)

        actual = []
        for alpha in np.linspace(0, 1, n_steps):
            r = interpolate_embeddings(model, tokenizer, chosen, rejected, alpha, device)
            actual.append(r)

        error = np.mean(np.abs(np.array(actual) - expected)) / reward_range
        errors.append(error)

    return {
        "mean_interpolation_error": float(np.mean(errors)),
        "max_interpolation_error": float(np.max(errors)),
    }
