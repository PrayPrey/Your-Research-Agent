"""H-M2: Entropy stratification - median split by domain entropy."""

import json
import numpy as np

from config import DOMAINS, StratConfig


def load_entropy_artifacts(strat_config: StratConfig) -> tuple[np.ndarray, dict]:
    """Load entropy matrix and domain means from H-M1."""
    entropy_matrix = np.load(strat_config.entropy_matrix_path)
    with open(strat_config.domain_means_path, 'r') as f:
        domain_means = json.load(f)
    return entropy_matrix, domain_means


def domain_median_split(domain_means: dict) -> tuple[list[str], list[str]]:
    """Split domains by median entropy."""
    median = np.median(list(domain_means.values()))

    high_domains = [d for d, v in domain_means.items() if v > median]
    low_domains = [d for d, v in domain_means.items() if v <= median]

    return high_domains, low_domains


def assign_sample_groups(domains_order: list[str], samples_per_domain: int,
                          high_domains: list[str]) -> np.ndarray:
    """Create boolean mask: True=high-entropy group."""
    n_samples = len(domains_order) * samples_per_domain
    group_mask = np.zeros(n_samples, dtype=bool)

    for i, domain in enumerate(domains_order):
        start = i * samples_per_domain
        end = start + samples_per_domain
        if domain in high_domains:
            group_mask[start:end] = True

    return group_mask


def per_sample_entropy(entropy_matrix: np.ndarray) -> np.ndarray:
    """Mean entropy per sample across layers/heads."""
    return entropy_matrix.mean(axis=(1, 2))


if __name__ == "__main__":
    cfg = StratConfig()
    entropy_matrix, domain_means = load_entropy_artifacts(cfg)
    print(f"Entropy matrix shape: {entropy_matrix.shape}")
    print(f"Domain means: {domain_means}")

    high, low = domain_median_split(domain_means)
    print(f"High-entropy domains: {high}")
    print(f"Low-entropy domains: {low}")

    mask = assign_sample_groups(DOMAINS, 30, high)
    print(f"High-entropy samples: {mask.sum()}, Low-entropy: {(~mask).sum()}")
