"""H-M1 Data Loader: Load and validate H-E1 execution results."""

import json
import logging
import os
import sys
from typing import Dict, List, Tuple

from config import HM1Config

logger = logging.getLogger(__name__)


def load_h_e1_results(config: HM1Config) -> Tuple[List[dict], List[dict]]:
    """Load RL and DPO execution results from H-E1 outputs.

    Args:
        config: H-M1 configuration with paths

    Returns:
        Tuple of (rl_results, dpo_results), each a list of dicts with 'error_trace' key

    Raises:
        FileNotFoundError: If H-E1 output files are missing
    """
    # Check files exist
    if not os.path.exists(config.rl_results_path):
        raise FileNotFoundError(f"H-E1 RL results not found: {config.rl_results_path}")
    if not os.path.exists(config.dpo_results_path):
        raise FileNotFoundError(f"H-E1 DPO results not found: {config.dpo_results_path}")

    # Load RL results
    with open(config.rl_results_path, "r") as f:
        rl_results = json.load(f)
    logger.info(f"Loaded {len(rl_results)} RL results from {config.rl_results_path}")

    # Load DPO results
    with open(config.dpo_results_path, "r") as f:
        dpo_results = json.load(f)
    logger.info(f"Loaded {len(dpo_results)} DPO results from {config.dpo_results_path}")

    return rl_results, dpo_results


def validate_data_integrity(
    rl_results: List[dict],
    dpo_results: List[dict],
    config: HM1Config,
) -> Dict:
    """Validate sample counts match H-E1 expectations.

    Args:
        rl_results: RL execution results
        dpo_results: DPO execution results
        config: H-M1 configuration with expected counts

    Returns:
        Dict with keys: rl_failures, dpo_failures, valid, warnings
    """
    warnings = []

    # Count failures (status == 'fail')
    rl_failures = sum(1 for r in rl_results if r.get("status") == "fail")
    dpo_failures = sum(1 for r in dpo_results if r.get("status") == "fail")

    # Check against expectations
    if rl_failures != config.expected_rl_failures:
        warnings.append(
            f"RL failure count ({rl_failures}) differs from expected ({config.expected_rl_failures})"
        )

    if dpo_failures != config.expected_dpo_failures:
        warnings.append(
            f"DPO failure count ({dpo_failures}) differs from expected ({config.expected_dpo_failures})"
        )

    # Validate required fields
    for i, r in enumerate(rl_results[:5]):  # Sample check
        if "error_trace" not in r:
            warnings.append(f"RL result {i} missing 'error_trace' field")
            break

    for i, r in enumerate(dpo_results[:5]):  # Sample check
        if "error_trace" not in r:
            warnings.append(f"DPO result {i} missing 'error_trace' field")
            break

    valid = len(warnings) == 0 or all("differs from expected" in w for w in warnings)

    return {
        "rl_failures": rl_failures,
        "dpo_failures": dpo_failures,
        "rl_total": len(rl_results),
        "dpo_total": len(dpo_results),
        "valid": valid,
        "warnings": warnings,
    }


def extract_error_counts(
    results: List[dict],
    h_e1_code_dir: str = None,  # Unused but kept for API compat
) -> Dict[str, int]:
    """Count error types using ICSE 2025 error taxonomy.

    Same taxonomy as H-E1 classify_error, inlined here to avoid import issues.

    Args:
        results: Execution results with 'error_trace' key
        h_e1_code_dir: Unused (kept for API compatibility)

    Returns:
        Dict with keys: syntax, runtime, assertion, pass, other
    """
    counts = {"syntax": 0, "runtime": 0, "assertion": 0, "pass": 0, "other": 0}

    for r in results:
        error_trace = r.get("error_trace")
        category = classify_error(error_trace)
        counts[category] = counts.get(category, 0) + 1

    return counts


# ICSE 2025 Error Taxonomy (copied from H-E1 analyze.py)
SYNTAX_ERRORS = ["syntaxerror", "indentationerror"]
RUNTIME_ERRORS = [
    "typeerror", "nameerror", "attributeerror",
    "indexerror", "keyerror", "valueerror",
    "zerodivisionerror", "recursionerror", "timeout"
]
ASSERTION_ERRORS = ["assertionerror", "expected"]


def classify_error(error_trace: str) -> str:
    """Classify error_trace using ICSE 2025 taxonomy.

    Args:
        error_trace: Error string or None for pass

    Returns:
        One of: "pass", "syntax", "runtime", "assertion", "other"
    """
    if error_trace is None:
        return "pass"

    error_lower = error_trace.lower()

    # Syntax errors (parse-time failures)
    for err in SYNTAX_ERRORS:
        if err in error_lower:
            return "syntax"

    # Assertion errors (code runs but wrong output)
    for err in ASSERTION_ERRORS:
        if err in error_lower:
            return "assertion"

    # Runtime errors (execution-time failures before assertion)
    for err in RUNTIME_ERRORS:
        if err in error_lower:
            return "runtime"

    return "other"


def load_h_e1_metrics(config: HM1Config) -> Dict:
    """Load pre-computed metrics from H-E1 metrics.json.

    Args:
        config: H-M1 configuration

    Returns:
        Dict with H-E1 metrics including rl_proportions, dpo_proportions
    """
    if not os.path.exists(config.h_e1_metrics_path):
        raise FileNotFoundError(f"H-E1 metrics not found: {config.h_e1_metrics_path}")

    with open(config.h_e1_metrics_path, "r") as f:
        metrics = json.load(f)

    return metrics
