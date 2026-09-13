"""Reward distribution analysis."""
import numpy as np
from scipy import stats
from tqdm import tqdm
import sys
sys.path.insert(0, "..")
from model import get_reward


def compute_bimodality(values: list) -> float:
    """Sarle's bimodality coefficient. < 0.555 indicates unimodal."""
    n = len(values)
    if n < 3:
        return 0.0

    m3 = stats.skew(values)
    m4 = stats.kurtosis(values, fisher=False)  # Pearson kurtosis

    bc = (m3**2 + 1) / m4
    return float(bc)


def analyze_reward_distribution(model, tokenizer, test_pairs: list, device: str) -> dict:
    """Analyze reward distribution for continuity."""
    rewards_chosen = []
    rewards_rejected = []

    for chosen, rejected in tqdm(test_pairs[:1000], desc="Analyzing distribution"):
        r_c = get_reward(model, tokenizer, chosen, device)
        r_r = get_reward(model, tokenizer, rejected, device)
        rewards_chosen.append(r_c)
        rewards_rejected.append(r_r)

    all_rewards = rewards_chosen + rewards_rejected

    unique_ratio = len(set(np.round(all_rewards, 2))) / len(all_rewards)
    bimodality = compute_bimodality(all_rewards)

    return {
        "reward_range": float(max(all_rewards) - min(all_rewards)),
        "reward_std": float(np.std(all_rewards)),
        "unique_reward_ratio": float(unique_ratio),
        "bimodality_coefficient": float(bimodality),
        "mean_chosen": float(np.mean(rewards_chosen)),
        "mean_rejected": float(np.mean(rewards_rejected)),
        "margin": float(np.mean(rewards_chosen) - np.mean(rewards_rejected)),
    }
