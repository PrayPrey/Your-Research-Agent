import torch
import torch.nn.functional as F
import numpy as np
from scipy.stats import spearmanr

def compute_entropy(logits):
    probs = F.softmax(logits, dim=-1)
    log_probs = torch.log(probs + 1e-10)
    entropy = -torch.sum(probs * log_probs)
    return entropy.item()

def compute_spearman(entropies, correctness):
    return spearmanr(entropies, correctness)

def extraction_rate(entropies):
    valid_count = sum(1 for e in entropies if e is not None and not np.isnan(e))
    return valid_count / len(entropies) if len(entropies) > 0 else 0

def quadrant_analysis(max_probs, entropies):
    max_probs_arr = np.array(max_probs)
    entropies_arr = np.array(entropies)

    median_maxprob = np.median(max_probs_arr)
    median_entropy = np.median(entropies_arr)

    q3_mask = (max_probs_arr > median_maxprob) & (entropies_arr > median_entropy)
    q3_count = np.sum(q3_mask)
    q3_fraction = q3_count / len(entropies)

    return {
        "median_maxprob": median_maxprob,
        "median_entropy": median_entropy,
        "q3_count": int(q3_count),
        "q3_fraction": q3_fraction
    }
