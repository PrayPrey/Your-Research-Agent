"""Boundary case analysis for DPO."""
import numpy as np
from tqdm import tqdm
import sys
sys.path.insert(0, "..")
from model import compute_dpo_implicit_reward


def analyze_boundary_cases(
    dpo_model, ref_model, tokenizer,
    boundary_pairs: list, beta: float, device: str
) -> dict:
    """Evaluate DPO on RLHF boundary cases (margin < 0.1)."""
    decisions = []
    confidences = []
    for chosen, rejected, rlhf_margin in tqdm(boundary_pairs, desc="Boundary analysis"):
        r_chosen = compute_dpo_implicit_reward(dpo_model, ref_model, tokenizer, chosen, beta, device)
        r_rejected = compute_dpo_implicit_reward(dpo_model, ref_model, tokenizer, rejected, beta, device)
        margin = r_chosen - r_rejected
        decisions.append(margin > 0)
        confidences.append(abs(margin))
    return {
        "boundary_accuracy": float(np.mean(decisions)),
        "mean_confidence": float(np.mean(confidences)),
        "confident_ratio": float(np.mean([c > 0.1 for c in confidences])),
    }


def extract_boundary_cases(
    test_pairs: list, rlhf_margins: list, margin_threshold: float = 0.1
) -> list:
    """Extract pairs where RLHF showed weak preference (margin < threshold)."""
    boundary_pairs = []
    for (chosen, rejected), margin in zip(test_pairs, rlhf_margins):
        if abs(margin) < margin_threshold:
            boundary_pairs.append((chosen, rejected, margin))
    return boundary_pairs
