"""Dataset builder for h-c1 domain-stratified analysis."""

import numpy as np
from config import CONFIG, DNSI_DATA, GAP_DATA, DOMAIN_MAP


def build_domain_dataset(domain: str) -> tuple[list[str], np.ndarray, np.ndarray]:
    """Filter benchmarks by domain, return sorted (names, dnsi, gap) arrays."""
    names = sorted(k for k in DNSI_DATA if DOMAIN_MAP[k] == domain)
    if len(names) < 3:
        raise ValueError(f"Domain '{domain}': only {len(names)} benchmarks, need >=3")
    dnsi_arr = np.array([DNSI_DATA[k] for k in names])
    gap_arr = np.array([GAP_DATA[k] for k in names])
    return names, dnsi_arr, gap_arr
