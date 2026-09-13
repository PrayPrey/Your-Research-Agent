import json
import random
from collections import Counter
from typing import List, Dict


def compute_distribution(records: List[dict]) -> dict:
    """Compute bug-type distribution over failed records."""
    failures = [r for r in records if not r.get("passed")]
    n_total = len(records)
    n_failures = len(failures)
    n_passed = n_total - n_failures

    counts = Counter(r["bug_type"] for r in failures)
    total_failures = sum(counts.values())

    if total_failures == 0:
        fractions = {"type_error": 0.0, "runtime_error": 0.0, "logic_error": 0.0}
        max_fraction = 0.0
    else:
        fractions = {t: counts.get(t, 0) / total_failures for t in ["type_error", "runtime_error", "logic_error"]}
        max_fraction = max(fractions.values())

    # Per-source breakdown
    he_failures = [r for r in failures if r.get("source") == "humaneval"]
    mb_failures = [r for r in failures if r.get("source") == "mbpp"]

    he_counts = Counter(r["bug_type"] for r in he_failures)
    mb_counts = Counter(r["bug_type"] for r in mb_failures)

    return {
        "n_total": n_total,
        "n_passed": n_passed,
        "n_failures": n_failures,
        "pass_rate": n_passed / n_total if n_total else 0.0,
        "type_error": fractions["type_error"],
        "runtime_error": fractions["runtime_error"],
        "logic_error": fractions["logic_error"],
        "max_fraction": max_fraction,
        "mixed_distribution": max_fraction < 0.80,
        "counts": dict(counts),
        "humaneval": {
            "n_failures": len(he_failures),
            "counts": dict(he_counts),
        },
        "mbpp": {
            "n_failures": len(mb_failures),
            "counts": dict(mb_counts),
        },
    }


def spot_check_agreement(records: List[dict], n: int = 50, seed: int = 42) -> dict:
    """
    Automated spot-check: compare Pyright-based classification vs.
    exception-type-only classification (proxy for manual ground truth).
    Treats exception-type-only labels as reference.
    """
    failures = [r for r in records if not r.get("passed")]
    if len(failures) < n:
        n = len(failures)

    rng = random.Random(seed)
    sample = rng.sample(failures, n)

    agreements = 0
    details = []
    for r in sample:
        auto_label = r["bug_type"]
        # Reference: exception-type-only (no Pyright), per logic.md §2
        ref_label = _exception_only_label(r.get("error", ""), r.get("error_type", ""))
        match = auto_label == ref_label
        if match:
            agreements += 1
        details.append({"id": r["id"], "auto": auto_label, "ref": ref_label, "match": match})

    agreement_rate = agreements / n if n > 0 else 0.0
    return {
        "n_sampled": n,
        "agreements": agreements,
        "agreement_rate": agreement_rate,
        "passed": agreement_rate >= 0.70,
        "details": details,
    }


RUNTIME_EXCEPTIONS = [
    "TypeError", "AttributeError", "NameError",
    "IndexError", "KeyError", "ValueError", "ImportError",
    "RecursionError", "ZeroDivisionError", "StopIteration",
]
SYNTAX_EXCEPTIONS = ["SyntaxError", "IndentationError", "TabError"]


def _exception_only_label(error: str, error_type: str) -> str:
    """Exception-type-only classifier (no Pyright) used as spot-check reference."""
    if error_type in SYNTAX_EXCEPTIONS or any(e in error for e in SYNTAX_EXCEPTIONS):
        return "type_error"
    if error_type in RUNTIME_EXCEPTIONS or any(e in error for e in RUNTIME_EXCEPTIONS):
        return "runtime_error"
    return "logic_error"
