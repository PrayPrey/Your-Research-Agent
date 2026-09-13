"""
surface_features.py - Surface feature extractors for h-m4 OLS mediation regression.

Extracts 5 surface features from AI response texts:
  1. response_length    - whitespace-split word count
  2. bullet_density     - fraction of lines starting with '-', '*', or bullet char
  3. politeness_freq    - fraction of words in POLITENESS_TOKENS
  4. ttr               - type-token ratio
  5. mean_sent_len      - mean words per sentence (split on '.')
"""
import re
import numpy as np
import pandas as pd
from typing import Dict, List

from config import POLITENESS_TOKENS, FEATURE_VALIDATION_THRESHOLDS


def extract_response_length(text: str) -> int:
    """Count whitespace-split words.

    Args:
        text: AI response text

    Returns:
        Word count (int >= 0)
    """
    if not text or not text.strip():
        return 0
    return len(text.split())


def extract_bullet_density(text: str) -> float:
    """Fraction of lines starting with '-', '*', or bullet char '•'.

    Args:
        text: AI response text

    Returns:
        float in [0.0, 1.0]
    """
    if not text or not text.strip():
        return 0.0

    lines = text.split('\n')
    lines = [l for l in lines if l.strip()]
    if not lines:
        return 0.0

    bullet_lines = sum(1 for l in lines if re.match(r'^\s*[-*•]', l))
    return bullet_lines / len(lines)


def extract_politeness_freq(text: str) -> float:
    """Fraction of words in POLITENESS_TOKENS set (lowercase match).

    Args:
        text: AI response text

    Returns:
        float in [0.0, 1.0]
    """
    if not text or not text.strip():
        return 0.0

    words = text.lower().split()
    if not words:
        return 0.0

    polite_count = sum(1 for w in words if w in POLITENESS_TOKENS)
    return polite_count / len(words)


def extract_ttr(text: str) -> float:
    """Type-token ratio: len(unique_words) / max(word_count, 1).

    Args:
        text: AI response text

    Returns:
        float in [0.0, 1.0]
    """
    if not text or not text.strip():
        return 0.0

    words = text.lower().split()
    if not words:
        return 0.0

    return len(set(words)) / len(words)


def extract_mean_sent_len(text: str) -> float:
    """Mean words per sentence. Sentences split on '.'.

    Args:
        text: AI response text

    Returns:
        float >= 0.0
    """
    if not text or not text.strip():
        return 0.0

    word_count = len(text.split())
    # Count sentences by splitting on '.'
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    sent_count = max(len(sentences), 1)
    return word_count / sent_count


def extract_all_features(text: str) -> Dict[str, float]:
    """Extract all 5 features for a single response text.

    Args:
        text: AI response text

    Returns:
        Dict with keys: response_length, bullet_density, politeness_freq, ttr, mean_sent_len
    """
    return {
        'response_length': float(extract_response_length(text)),
        'bullet_density': extract_bullet_density(text),
        'politeness_freq': extract_politeness_freq(text),
        'ttr': extract_ttr(text),
        'mean_sent_len': extract_mean_sent_len(text),
    }


def batch_extract_features(texts: List[str]) -> pd.DataFrame:
    """Batch extract all 5 surface features from list of response texts.

    Args:
        texts: List of AI response text strings

    Returns:
        DataFrame with columns: response_length, bullet_density,
        politeness_freq, ttr, mean_sent_len
        Shape: (len(texts), 5)
    """
    records = [extract_all_features(t) for t in texts]
    df = pd.DataFrame(records, columns=[
        'response_length', 'bullet_density', 'politeness_freq', 'ttr', 'mean_sent_len'
    ])
    return df


def validate_features(df: pd.DataFrame) -> Dict[str, bool]:
    """Check for NaN, zero-length, out-of-range values. Returns validation dict.

    Args:
        df: DataFrame from batch_extract_features()

    Returns:
        Dict mapping check_name -> bool (True = pass)
    """
    results = {}

    # Check no NaN
    results['no_nan'] = not df.isnull().any().any()

    # Check no all-zero column
    results['no_all_zero'] = not (df == 0).all().any()

    # Check range for each feature
    for col, thresholds in FEATURE_VALIDATION_THRESHOLDS.items():
        if col not in df.columns:
            results[f'{col}_in_range'] = False
            continue
        col_min = df[col].min()
        col_max = df[col].max()
        in_range = (col_min >= thresholds['min']) and (col_max <= thresholds['max'])
        results[f'{col}_in_range'] = bool(in_range)

    # Check non-empty
    results['non_empty'] = len(df) > 0

    return results
