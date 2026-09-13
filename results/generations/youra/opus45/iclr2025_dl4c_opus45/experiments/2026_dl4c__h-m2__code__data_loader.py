"""H-M2 Data Loader: Load and validate H-E1 execution results."""

import json
import logging
import os
from typing import Dict, List, Tuple

from config import HM2Config

logger = logging.getLogger(__name__)


def load_h_e1_results(config: HM2Config) -> Tuple[List[dict], List[dict]]:
    """Load RL and DPO execution results from H-E1 outputs.

    Args:
        config: H-M2 configuration with paths

    Returns:
        Tuple of (rl_results, dpo_results), each a list of dicts

    Raises:
        FileNotFoundError: If H-E1 output files are missing
    """
    if not os.path.exists(config.rl_results_path):
        raise FileNotFoundError(f"H-E1 RL results not found: {config.rl_results_path}")
    if not os.path.exists(config.dpo_results_path):
        raise FileNotFoundError(f"H-E1 DPO results not found: {config.dpo_results_path}")

    with open(config.rl_results_path, "r") as f:
        rl_results = json.load(f)
    logger.info(f"Loaded {len(rl_results)} RL results from {config.rl_results_path}")

    with open(config.dpo_results_path, "r") as f:
        dpo_results = json.load(f)
    logger.info(f"Loaded {len(dpo_results)} DPO results from {config.dpo_results_path}")

    return rl_results, dpo_results


def extract_failures(results: List[dict]) -> List[dict]:
    """Filter to status == 'fail' records only.

    Args:
        results: Execution results list

    Returns:
        List of failure records only
    """
    failures = [r for r in results if r.get("status") == "fail"]
    logger.info(f"Extracted {len(failures)} failures from {len(results)} total samples")
    return failures


def validate_data_integrity(
    rl_failures: List[dict],
    dpo_failures: List[dict],
    config: HM2Config,
) -> Dict:
    """Validate sample counts match H-E1 expectations.

    Args:
        rl_failures: RL failure records
        dpo_failures: DPO failure records
        config: H-M2 configuration with expected counts

    Returns:
        Dict with keys: rl_failures, dpo_failures, valid, warnings
    """
    warnings = []

    rl_count = len(rl_failures)
    dpo_count = len(dpo_failures)

    if rl_count != config.expected_rl_failures:
        warnings.append(
            f"RL failure count ({rl_count}) differs from expected ({config.expected_rl_failures})"
        )

    if dpo_count != config.expected_dpo_failures:
        warnings.append(
            f"DPO failure count ({dpo_count}) differs from expected ({config.expected_dpo_failures})"
        )

    # Validate required fields
    for i, r in enumerate(rl_failures[:5]):
        if "completion" not in r:
            warnings.append(f"RL failure {i} missing 'completion' field")
            break

    for i, r in enumerate(dpo_failures[:5]):
        if "completion" not in r:
            warnings.append(f"DPO failure {i} missing 'completion' field")
            break

    valid = len(warnings) == 0 or all("differs from expected" in w for w in warnings)

    return {
        "rl_failures": rl_count,
        "dpo_failures": dpo_count,
        "valid": valid,
        "warnings": warnings,
    }


# ICSE 2025 Error Taxonomy (inlined from H-M1)
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

    for err in SYNTAX_ERRORS:
        if err in error_lower:
            return "syntax"

    for err in ASSERTION_ERRORS:
        if err in error_lower:
            return "assertion"

    for err in RUNTIME_ERRORS:
        if err in error_lower:
            return "runtime"

    return "other"
