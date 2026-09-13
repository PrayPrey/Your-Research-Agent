"""Shannon entropy computation for token-level uncertainty estimation.

This module computes Shannon entropy from logits with numerical stability.
"""

import numpy as np
from scipy.special import softmax
from typing import List, Tuple
from tqdm import tqdm


def compute_entropy(logits: np.ndarray, eps: float = 1e-10) -> float:
    """Compute Shannon entropy from logits.

    Parameters
    ----------
    logits : np.ndarray
        Raw logits, shape [vocab_size]
    eps : float
        Small constant to avoid log(0)

    Returns
    -------
    float
        Shannon entropy H = -Σ p(w) * log(p(w))
    """
    # Convert logits to probabilities
    probs = softmax(logits)

    # Clip probabilities to avoid log(0)
    probs = np.clip(probs, eps, 1.0)

    # Compute entropy
    entropy = -np.sum(probs * np.log(probs))

    return entropy


def validate_entropy(entropy: float, vocab_size: int) -> bool:
    """Validate entropy is in valid range.

    Parameters
    ----------
    entropy : float
        Computed entropy value
    vocab_size : int
        Vocabulary size

    Returns
    -------
    bool
        True if entropy is valid
    """
    max_entropy = np.log(vocab_size)
    return 0 <= entropy <= max_entropy


def compute_batch_entropy(
    logits_list: List[np.ndarray],
    vocab_size: int = 32000
) -> List[float]:
    """Compute entropy for a batch of logits.

    Parameters
    ----------
    logits_list : List[np.ndarray]
        List of logits arrays, each shape [vocab_size]
    vocab_size : int
        Expected vocabulary size

    Returns
    -------
    List[float]
        Entropy values
    """
    entropies = []

    for logits in logits_list:
        entropy = compute_entropy(logits)

        # Validate
        if not validate_entropy(entropy, vocab_size):
            print(f"Warning: entropy {entropy:.4f} outside valid range [0, {np.log(vocab_size):.4f}]")

        entropies.append(entropy)

    return entropies


def process_generated_outputs(
    generated_outputs: List[dict],
    vocab_size: int = 32000
) -> Tuple[np.ndarray, np.ndarray]:
    """Process generated outputs to extract entropies and labels.

    Parameters
    ----------
    generated_outputs : List[dict]
        Generated outputs with 'logits' and 'label' fields
    vocab_size : int
        Vocabulary size for validation

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        (entropies, labels) arrays
        - entropies: shape [N], dtype float32
        - labels: shape [N], dtype int8
        - N = total number of tokens across all samples
    """
    all_entropies = []
    all_labels = []

    for sample in tqdm(generated_outputs, desc="Computing entropy"):
        logits = sample['logits']
        label = sample['label']

        # Compute entropy for each token
        sample_entropies = compute_batch_entropy(logits, vocab_size)

        # Propagate response-level label to all tokens
        sample_labels = [label] * len(sample_entropies)

        all_entropies.extend(sample_entropies)
        all_labels.extend(sample_labels)

    # Convert to numpy arrays
    entropies = np.array(all_entropies, dtype=np.float32)
    labels = np.array(all_labels, dtype=np.int8)

    print(f"Processed {len(entropies)} tokens from {len(generated_outputs)} samples")
    print(f"Entropy range: [{entropies.min():.4f}, {entropies.max():.4f}]")
    print(f"Entropy mean: {entropies.mean():.4f}, std: {entropies.std():.4f}")
    print(f"Label distribution: {np.bincount(labels)}")

    return entropies, labels


def compute_entropy_statistics(
    entropies: np.ndarray,
    labels: np.ndarray
) -> dict:
    """Compute descriptive statistics for entropy by label.

    Parameters
    ----------
    entropies : np.ndarray
        Entropy values
    labels : np.ndarray
        Binary labels (0=correct, 1=hallucinated)

    Returns
    -------
    dict
        Statistics dictionary
    """
    correct_mask = labels == 0
    hallucinated_mask = labels == 1

    correct_entropies = entropies[correct_mask]
    hallucinated_entropies = entropies[hallucinated_mask]

    stats = {
        'overall': {
            'count': len(entropies),
            'mean': float(np.mean(entropies)),
            'std': float(np.std(entropies)),
            'median': float(np.median(entropies)),
            'min': float(np.min(entropies)),
            'max': float(np.max(entropies))
        },
        'correct': {
            'count': len(correct_entropies),
            'mean': float(np.mean(correct_entropies)),
            'std': float(np.std(correct_entropies)),
            'median': float(np.median(correct_entropies)),
            'q25': float(np.percentile(correct_entropies, 25)),
            'q75': float(np.percentile(correct_entropies, 75))
        },
        'hallucinated': {
            'count': len(hallucinated_entropies),
            'mean': float(np.mean(hallucinated_entropies)),
            'std': float(np.std(hallucinated_entropies)),
            'median': float(np.median(hallucinated_entropies)),
            'q25': float(np.percentile(hallucinated_entropies, 25)),
            'q75': float(np.percentile(hallucinated_entropies, 75))
        }
    }

    return stats


def save_entropy_data(
    entropies: np.ndarray,
    labels: np.ndarray,
    output_dir: str
):
    """Save entropy and label arrays to disk.

    Parameters
    ----------
    entropies : np.ndarray
        Entropy values
    labels : np.ndarray
        Binary labels
    output_dir : str
        Output directory
    """
    import os
    os.makedirs(output_dir, exist_ok=True)

    entropy_path = os.path.join(output_dir, 'entropies.npy')
    labels_path = os.path.join(output_dir, 'labels.npy')

    np.save(entropy_path, entropies)
    np.save(labels_path, labels)

    print(f"Saved entropies to {entropy_path}")
    print(f"Saved labels to {labels_path}")
