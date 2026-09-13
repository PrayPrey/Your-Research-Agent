"""
Feature extraction for H-E1.
Regex-based curation feature extraction, parameter/token count recovery, and arch family assignment.
"""
import re
import math
import os
import sys

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE_DIR)

import config
from typing import Optional


def extract_curation_features(card_text: str) -> dict:
    """Apply REGEX_PATTERNS case-insensitively to card_text.

    Returns: {"dedup_documented": 0|1, "perplexity_filter_documented": 0|1,
              "domain_composition_documented": 0|1, "decontamination_documented": 0|1}
    """
    features = {}
    for feature_name, pattern in config.REGEX_PATTERNS.items():
        match = re.search(pattern, card_text, re.IGNORECASE)
        features[feature_name] = 1 if match else 0
    return features


def recover_param_count(
    model_info: object,
    card_text: str,
    model_id: str,
) -> Optional[float]:
    """Recover parameter count N.

    Priority chain:
    1. model_info.safetensors.total
    2. regex parse card_text for "NB" / "N billion" patterns
    3. name-map lookup from PARAM_COUNT_MAP

    Returns: float (e.g. 7e9) or None if unrecoverable.
    """
    # Priority 1: model_info metadata
    if model_info is not None:
        try:
            if hasattr(model_info, 'safetensors') and model_info.safetensors:
                total = getattr(model_info.safetensors, 'total', None)
                if total and total > 0:
                    return float(total)
        except Exception:
            pass

    # Priority 2: parse card_text for "NB" / "N billion" patterns
    if card_text:
        # Match "7B parameters", "13 billion parameters", "7B params"
        m = re.search(r'(\d+(?:\.\d+)?)\s*[Bb]illion\s*param', card_text, re.IGNORECASE)
        if m:
            return float(m.group(1)) * 1e9

        m = re.search(r'(\d+(?:\.\d+)?)\s*[Bb](?:illion)?\s*param', card_text, re.IGNORECASE)
        if m:
            return float(m.group(1)) * 1e9

        m = re.search(r'(\d+(?:\.\d+)?)[Bb]\b', card_text)
        if m:
            val = float(m.group(1))
            # Sanity check: realistic param counts in billions
            if 0.1 <= val <= 1000:
                return val * 1e9

    # Priority 3: name-map lookup
    for pattern, n_params in config.PARAM_COUNT_MAP.items():
        if re.search(pattern, model_id, re.IGNORECASE):
            return n_params

    return None


def recover_token_count(card_text: str) -> Optional[float]:
    """Regex parse training token count from card_text.

    Patterns: "N trillion tokens", "N billion tokens", "Nt tokens".
    Returns: float (e.g. 1e12) or None.
    """
    if not card_text:
        return None

    # Match "1 trillion tokens", "1T tokens"
    m = re.search(r'(\d+(?:\.\d+)?)\s*trillion\s*tokens?', card_text, re.IGNORECASE)
    if m:
        return float(m.group(1)) * 1e12

    m = re.search(r'(\d+(?:\.\d+)?)[Tt]\s*tokens?', card_text, re.IGNORECASE)
    if m:
        return float(m.group(1)) * 1e12

    # Match "200 billion tokens", "200B tokens"
    m = re.search(r'(\d+(?:\.\d+)?)\s*billion\s*tokens?', card_text, re.IGNORECASE)
    if m:
        return float(m.group(1)) * 1e9

    m = re.search(r'(\d+(?:\.\d+)?)\s*[Bb]\s*tokens?', card_text, re.IGNORECASE)
    if m:
        return float(m.group(1)) * 1e9

    return None


def assign_arch_family(model_id: str) -> str:
    """Match model_id against ARCH_FAMILY_PATTERNS (case-insensitive).

    Returns: "LLaMA"|"Mistral"|"Falcon"|"Pythia"|"OLMo"|"Other".
    """
    for family, pattern in config.ARCH_FAMILY_PATTERNS.items():
        if re.search(pattern, model_id, re.IGNORECASE):
            return family
    return "Other"


def compute_derived_features(
    n_params: float,
    n_tokens: Optional[float],
) -> dict:
    """Compute log-scale features.

    Returns: {"log_params": float, "log_tokens": float|None}
    """
    log_params = math.log10(n_params) if n_params and n_params > 0 else None
    log_tokens = math.log10(n_tokens) if n_tokens and n_tokens > 0 else None
    return {
        "log_params": log_params,
        "log_tokens": log_tokens
    }
