"""Margin distribution comparison between DPO and RLHF."""
import numpy as np
from tqdm import tqdm
import sys
sys.path.insert(0, "..")
from model import compute_dpo_implicit_reward


def compare_margin_distributions(
    dpo_model, ref_model, tokenizer, test_pairs: list,
    rlhf_margin_std: float, beta: float, device: str
) -> dict:
    """Compare DPO implicit reward margins to RLHF baseline."""
    dpo_margins = []
    for chosen, rejected in tqdm(test_pairs, desc="Computing DPO margins"):
        r_chosen = compute_dpo_implicit_reward(dpo_model, ref_model, tokenizer, chosen, beta, device)
        r_rejected = compute_dpo_implicit_reward(dpo_model, ref_model, tokenizer, rejected, beta, device)
        dpo_margins.append(r_chosen - r_rejected)
    dpo_std = np.std(dpo_margins)
    sharpness_ratio = dpo_std / rlhf_margin_std if rlhf_margin_std > 0 else float("inf")
    return {
        "dpo_margin_std": float(dpo_std),
        "dpo_margin_mean": float(np.mean(dpo_margins)),
        "rlhf_margin_std": float(rlhf_margin_std),
        "sharpness_ratio": float(sharpness_ratio),
        "dpo_margins": dpo_margins,
    }
