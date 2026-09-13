"""Compute cumulative domain exposure trajectories from Pythia index maps."""
import logging
import numpy as np

from src.data.loader import TOKENS_PER_STEP, SEQ_LEN

UNKNOWN_DOMAIN = "Unknown"


def _log_checkpoint(step: int, cumulative_counts: np.ndarray, total_tokens: int, domain_names: list) -> None:
    counts_dict = {domain_names[i]: int(cumulative_counts[i]) for i in range(len(domain_names))}
    logging.info(f"Checkpoint step{step}: domain_counts={counts_dict}, total_tokens={total_tokens}")


def compute_domain_exposure_trajectories(
    dataset,
    doc_to_domain: dict,
    checkpoint_steps: list,
    domain_names: list,
) -> np.ndarray:
    """Incremental domain accumulation across 154 checkpoints.
    Returns shape (22, 154), dtype float64.
    """
    domain_to_idx = {name: i for i, name in enumerate(domain_names)}
    n_domains = len(domain_names)
    n_checkpoints = len(checkpoint_steps)

    cumulative_counts = np.zeros(n_domains, dtype=np.int64)
    trajectories = np.zeros((n_domains, n_checkpoints), dtype=np.float64)

    step_ptr = 0
    unknown_count = 0
    total_samples_seen = 0

    dataset_len = len(dataset)

    for t, step in enumerate(checkpoint_steps):
        target_sample = step * TOKENS_PER_STEP // SEQ_LEN
        target_sample = min(target_sample, dataset_len)

        for sample_idx in range(step_ptr, target_sample):
            doc_idx = int(dataset.doc_idx[sample_idx])
            domain = doc_to_domain.get(doc_idx, UNKNOWN_DOMAIN)
            if domain in domain_to_idx:
                cumulative_counts[domain_to_idx[domain]] += 1
            else:
                unknown_count += 1
            total_samples_seen += 1

        step_ptr = target_sample

        total = cumulative_counts.sum()
        if total > 0:
            trajectories[:, t] = cumulative_counts / total
        else:
            trajectories[:, t] = 0.0

        _log_checkpoint(step, cumulative_counts, int(total), domain_names)

    unknown_rate = unknown_count / max(total_samples_seen, 1)
    if unknown_rate > 0.01:
        logging.warning(f"Unknown doc rate: {unknown_rate:.2%} ({unknown_count} samples)")

    assert trajectories.shape == (n_domains, n_checkpoints), (
        f"trajectories.shape={trajectories.shape}, expected ({n_domains}, {n_checkpoints})"
    )
    assert not np.isnan(trajectories).any(), "NaN in trajectories"

    return trajectories
