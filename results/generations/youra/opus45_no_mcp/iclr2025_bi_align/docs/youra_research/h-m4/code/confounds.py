"""Confound variable extraction for H-M4."""

import re
import numpy as np
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def extract_length(texts: list) -> np.ndarray:
    """Character count of each task text."""
    return np.array([len(t) for t in texts])


def extract_topic_onehot(source_datasets: list) -> np.ndarray:
    """One-hot encode source dataset (truthfulqa/mmlu_moral/anthropic_hh)."""
    enc = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    return enc.fit_transform(np.array(source_datasets).reshape(-1, 1))


def extract_format_onehot(texts: list) -> np.ndarray:
    """Detect multiple choice vs open-ended format."""
    mc_pattern = re.compile(r'[A-D]\)|^\([a-d]\)|^[a-d]\)', re.MULTILINE)
    formats = []
    for t in texts:
        is_mc = 1 if mc_pattern.search(t) else 0
        formats.append([is_mc, 1 - is_mc])
    return np.array(formats)


def extract_difficulty(records: list) -> np.ndarray:
    """Difficulty proxy from logprob gap."""
    return np.array([
        abs(r["correct_logprob_norm"] - r["max_wrong_logprob_norm"])
        for r in records
    ])


def build_confound_matrix(records: list) -> np.ndarray:
    """Build and standardize confound matrix [N, F]."""
    texts = [r["question"] for r in records]
    sources = [r["source_dataset"] for r in records]

    length = extract_length(texts).reshape(-1, 1)
    difficulty = extract_difficulty(records).reshape(-1, 1)
    topic = extract_topic_onehot(sources)
    fmt = extract_format_onehot(texts)

    confounds = np.hstack([length, difficulty, topic, fmt])
    scaler = StandardScaler()
    return scaler.fit_transform(confounds)
