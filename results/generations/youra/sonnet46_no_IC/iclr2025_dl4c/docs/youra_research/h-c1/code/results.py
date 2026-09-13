"""Aggregate results computation and output for H-C1."""

import json

FULL_SUBSET_SIZE = 12_960_052


def build_aggregate(per_file: list, duration_seconds: float) -> dict:
    """Compute aggregate statistics from per-file results."""
    n_sampled = len(per_file)
    n_pattern_positive = sum(1 for r in per_file if r["phase_a"])
    n_ast_positive = sum(1 for r in per_file if r["phase_b"])
    n_executable_positive = sum(1 for r in per_file if r["phase_c"] is True)

    doctest_pattern_rate = n_pattern_positive / n_sampled if n_sampled > 0 else 0.0
    doctest_ast_rate = n_ast_positive / n_sampled if n_sampled > 0 else 0.0
    doctest_executable_rate = n_executable_positive / n_sampled if n_sampled > 0 else 0.0

    estimated_full_subset_executable_files = int(doctest_executable_rate * FULL_SUBSET_SIZE)
    estimated_token_pool_M = sum(r["estimated_tokens"] for r in per_file) / 1e6

    return {
        "n_sampled": n_sampled,
        "n_pattern_positive": n_pattern_positive,
        "n_ast_positive": n_ast_positive,
        "n_executable_positive": n_executable_positive,
        "doctest_pattern_rate": doctest_pattern_rate,
        "doctest_ast_rate": doctest_ast_rate,
        "doctest_executable_rate": doctest_executable_rate,
        "estimated_full_subset_executable_files": estimated_full_subset_executable_files,
        "estimated_token_pool_M": estimated_token_pool_M,
        "scan_duration_seconds": duration_seconds,
        "seed": 42,
        "dataset": "bigcode/the-stack-dedup",
        "filter": "data/python",
    }


def write_json(aggregate: dict, path: str) -> None:
    """Write aggregate results as pretty-printed JSON."""
    with open(path, "w") as f:
        json.dump(aggregate, f, indent=2)


def write_jsonl(per_file: list, path: str) -> None:
    """Write per-file results as one JSON object per line."""
    with open(path, "w") as f:
        for rec in per_file:
            f.write(json.dumps(rec) + "\n")
