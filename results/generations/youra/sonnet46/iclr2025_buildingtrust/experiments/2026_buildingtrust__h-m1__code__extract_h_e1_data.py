"""
extract_h_e1_data.py — H-M1 Data Extraction from H-E1 artifacts
Path A: regex parse h-e1/04_validation.md
Path A-extended: reload log-probabilities from h-e1 JSONL samples
"""

import re
import sys
import logging
import numpy as np
from pathlib import Path
from typing import Optional

import config

# ── Logging ───────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)

# ── H-E1 import (via sys.path injection) ─────────────────────────────────────
sys.path.insert(0, config.H_E1_CODE_DIR)

BASE_SIZES = config.BASE_SIZES


# ═══════════════════════════════════════════════════════════════════════════════
# Path A: Regex parse h-e1/04_validation.md
# ═══════════════════════════════════════════════════════════════════════════════

def load_h_e1_ece_base(
    validation_file: Optional[str] = None,
) -> dict:
    """
    Extract ECE_base for 3 Pythia base sizes from h-e1/04_validation.md.

    Returns:
        dict: {"1.4b": float, "2.8b": float, "6.9b": float}

    Raises:
        KeyError: if any base size ECE cannot be found
        ValueError: if parsed value not in [0, 1]
    """
    if validation_file is None:
        validation_file = config.H_E1_VALIDATION_PATH

    path = Path(validation_file)
    if not path.exists():
        raise FileNotFoundError(f"H-E1 validation report not found: {validation_file}")

    text = path.read_text(encoding="utf-8")
    logger.info(f"Parsing {validation_file} ({len(text)} chars)")

    ece_base = {}

    # Pattern 1: markdown table row "| pythia-{size}-base | ... | {ece} | ..."
    # Table format: | Model | N Samples | ECE | Brier REL | ...
    table_pattern = re.compile(
        r"\|\s*pythia-(\d+\.?\d*[bB])-base\s*\|\s*\d+\s*\|\s*([0-9]+\.[0-9]+)\s*\|"
    )
    for match in table_pattern.finditer(text):
        size = match.group(1).lower()
        ece_val = float(match.group(2))
        if size in BASE_SIZES:
            ece_base[size] = ece_val
            logger.info(f"  Extracted ECE_base[{size}] = {ece_val:.4f} (table pattern)")

    # Pattern 2: key-value format "ece_base_{size}: {val}"
    if len(ece_base) < len(BASE_SIZES):
        kv_pattern = re.compile(
            r"ece_base[_\-](\d+\.?\d*[bB])\s*[:\=]\s*([0-9]+\.[0-9]+)",
            re.IGNORECASE,
        )
        for match in kv_pattern.finditer(text):
            size = match.group(1).lower()
            ece_val = float(match.group(2))
            if size in BASE_SIZES and size not in ece_base:
                ece_base[size] = ece_val
                logger.info(f"  Extracted ECE_base[{size}] = {ece_val:.4f} (kv pattern)")

    # Pattern 3: "pythia-{size}-base ... ECE ... {val}" in any line
    if len(ece_base) < len(BASE_SIZES):
        for size in BASE_SIZES:
            if size in ece_base:
                continue
            escaped = size.replace(".", r"\.")
            line_pattern = re.compile(
                rf"pythia-{escaped}-base[^\n]*?([0-9]+\.[0-9]+)",
                re.IGNORECASE,
            )
            match = line_pattern.search(text)
            if match:
                ece_val = float(match.group(1))
                ece_base[size] = ece_val
                logger.info(f"  Extracted ECE_base[{size}] = {ece_val:.4f} (line pattern)")

    # Validate completeness
    missing = [s for s in BASE_SIZES if s not in ece_base]
    if missing:
        raise KeyError(
            f"Could not extract ECE_base for sizes: {missing} "
            f"from {validation_file}. "
            f"Found: {list(ece_base.keys())}"
        )

    # Validate ranges
    for size, val in ece_base.items():
        if not (0.0 <= val <= 1.0):
            raise ValueError(
                f"ECE_base[{size}] = {val} is outside [0, 1]. Parsing error."
            )

    logger.info(f"✓ ECE_base extraction complete: {ece_base}")
    return ece_base


# ═══════════════════════════════════════════════════════════════════════════════
# Path A-extended: reload log-probs from h-e1 JSONL
# ═══════════════════════════════════════════════════════════════════════════════

def load_h_e1_logprobs_for_base(
    results_dir: Optional[str] = None,
) -> dict:
    """
    Reload log-probability data for Pythia base models from h-e1 JSONL samples.
    Uses h-e1/code/calibration_analysis.load_lmeval_samples().

    Returns:
        dict: {"1.4b": (logprobs: (N,4), y_true: (N,)), ...}

    Raises:
        ImportError: if h-e1/calibration_analysis not importable
        FileNotFoundError: if results_dir not found
    """
    if results_dir is None:
        results_dir = config.H_E1_RESULTS_DIR

    try:
        from calibration_analysis import load_lmeval_samples
    except ImportError as e:
        raise ImportError(
            f"Cannot import calibration_analysis from {config.H_E1_CODE_DIR}: {e}"
        )

    logprobs_dict = {}
    for size in BASE_SIZES:
        model_id = f"pythia-{size}-base"
        logger.info(f"  Loading logprobs for {model_id} from {results_dir}")
        try:
            logprobs, y_true = load_lmeval_samples(model_id, results_dir=results_dir)
            logprobs_dict[size] = (logprobs, y_true)
            logger.info(f"    Loaded {len(y_true)} samples")
        except Exception as e:
            logger.warning(f"    Failed to load {model_id}: {e}")
            raise RuntimeError(f"Failed to load logprobs for {model_id}: {e}")

    return logprobs_dict


def compute_ece_from_logprobs(
    logprobs_dict: dict,
) -> dict:
    """
    Compute ECE from loaded logprob data using h-e1/calibration_analysis.compute_ece().

    Args:
        logprobs_dict: output of load_h_e1_logprobs_for_base()

    Returns:
        dict: {"1.4b": float, "2.8b": float, "6.9b": float}
    """
    try:
        from calibration_analysis import compute_ece
        from scipy.special import softmax
    except ImportError as e:
        raise ImportError(f"Cannot import dependencies: {e}")

    ece_base = {}
    for size, (logprobs, y_true) in logprobs_dict.items():
        # Convert log-probs to probabilities
        probs = softmax(logprobs, axis=1)
        ece = compute_ece(y_true, probs, n_bins=config.N_BINS)
        ece_base[size] = float(ece)
        logger.info(f"  ECE_base[{size}] = {ece:.4f} (computed from logprobs)")

    return ece_base


# ═══════════════════════════════════════════════════════════════════════════════
# Dispatch: Path A → Path A-extended
# ═══════════════════════════════════════════════════════════════════════════════

def extract_or_recompute_ece_base(
    validation_file: Optional[str] = None,
    results_dir: Optional[str] = None,
) -> tuple:
    """
    Extract ECE_base via best available path.

    Priority:
        1. Path A: regex parse h-e1/04_validation.md (fast, no GPU)
        2. Path A-extended: reload logprobs from h-e1 JSONL (medium, no GPU)

    Returns:
        (ece_base: dict[str, float], path_label: str)

    Raises:
        RuntimeError: if both paths fail (caller should fall back to Path B)
    """
    # Path A: regex parse
    try:
        logger.info("Attempting Path A: regex parse h-e1/04_validation.md")
        ece_base = load_h_e1_ece_base(validation_file)
        logger.info("✓ Path A succeeded")
        return ece_base, "Path A (regex parse h-e1/04_validation.md)"
    except (FileNotFoundError, KeyError, ValueError) as e:
        logger.warning(f"Path A failed: {e}")

    # Path A-extended: logprob reload
    try:
        logger.info("Attempting Path A-extended: reload logprobs from h-e1 JSONL")
        logprobs_dict = load_h_e1_logprobs_for_base(results_dir)
        ece_base = compute_ece_from_logprobs(logprobs_dict)
        logger.info("✓ Path A-extended succeeded")
        return ece_base, "Path A-extended (logprob reload from h-e1 JSONL)"
    except Exception as e:
        logger.warning(f"Path A-extended failed: {e}")

    raise RuntimeError(
        "Both Path A and Path A-extended failed. "
        "Falling back to Path B (lm-eval re-run)."
    )
