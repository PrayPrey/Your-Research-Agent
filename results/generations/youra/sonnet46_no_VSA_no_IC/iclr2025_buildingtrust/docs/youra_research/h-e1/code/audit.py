"""H-E1 gate audit and protocol consistency check."""
import logging

import pandas as pd

from .config import BENCHMARK_PAIRS, N_COMMON_GATE


def check_protocol_consistency(
    score_dicts: dict[str, dict[str, dict[str, float]]],
    threshold_pp: float = 5.0,
) -> tuple[list[dict], float]:
    """
    Find model-benchmark pairs scored by multiple sources; flag if |delta| > threshold_pp.

    Returns:
        warnings: list of {model, benchmark, source_a, val_a, source_b, val_b, delta_pp}
        consistency_fraction: float — fraction of cross-source pairs within threshold
    """
    warnings = []
    total_pairs = 0
    within_threshold = 0
    sources = list(score_dicts.keys())

    for i, src_a in enumerate(sources):
        for src_b in sources[i + 1 :]:
            models_a = set(score_dicts[src_a].keys())
            models_b = set(score_dicts[src_b].keys())
            shared_models = models_a & models_b
            for model in shared_models:
                benchmarks_a = set(score_dicts[src_a][model].keys())
                benchmarks_b = set(score_dicts[src_b][model].keys())
                shared_benchmarks = benchmarks_a & benchmarks_b
                for bench in shared_benchmarks:
                    val_a = score_dicts[src_a][model][bench]
                    val_b = score_dicts[src_b][model][bench]
                    # Normalize scale mismatch (0-1 vs 0-100)
                    if abs(val_a - val_b) > 50:
                        val_b = val_b / 100.0 if val_b > 1 else val_b * 100.0
                    delta = abs(val_a - val_b) * 100  # convert to percentage points
                    total_pairs += 1
                    if delta > threshold_pp:
                        warnings.append(
                            {
                                "model": model,
                                "benchmark": bench,
                                "source_a": src_a,
                                "val_a": val_a,
                                "source_b": src_b,
                                "val_b": val_b,
                                "delta_pp": round(delta, 2),
                            }
                        )
                    else:
                        within_threshold += 1

    consistency_fraction = (within_threshold / total_pairs) if total_pairs > 0 else 1.0
    return warnings, consistency_fraction


def run_h_e1_audit(
    matrix: pd.DataFrame,
    attribution: pd.DataFrame,
    score_dicts: dict[str, dict[str, dict[str, float]]],
) -> dict:
    """
    Run H-E1 gate audit.

    Returns dict with: N_common, pair_counts, complete_matrix, gate_passed,
    protocol_warnings, protocol_consistency, mmlu_coverage.
    """
    complete_matrix = matrix.dropna()
    n_common = len(complete_matrix)

    pair_counts: dict[str, int] = {}
    for col_a, col_b in BENCHMARK_PAIRS:
        pair_key = f"{col_a}/{col_b}"
        n_pair = matrix[[col_a, col_b]].dropna().shape[0]
        pair_counts[pair_key] = n_pair

    protocol_warnings, consistency_fraction = check_protocol_consistency(score_dicts)

    models_with_mmlu = int(matrix["MMLU"].notna().sum())
    mmlu_coverage = models_with_mmlu / len(matrix) if len(matrix) > 0 else 0.0

    gate_passed = n_common >= N_COMMON_GATE
    print(f"N_common = {n_common} → {'PASS' if gate_passed else 'FAIL'}")

    return {
        "N_common": n_common,
        "pair_counts": pair_counts,
        "complete_matrix": complete_matrix,
        "gate_passed": gate_passed,
        "protocol_warnings": protocol_warnings,
        "protocol_consistency": round(consistency_fraction, 3),
        "mmlu_coverage": round(float(mmlu_coverage), 3),
    }


if __name__ == "__main__":
    import numpy as np
    from .config import REQUIRED_COLS

    models = [f"Model-{i}" for i in range(12)]
    data = {col: list(range(40, 52)) for col in REQUIRED_COLS}
    # normalize to 0-1
    data = {col: [v / 100.0 for v in vals] for col, vals in data.items()}
    df = pd.DataFrame(data, index=models)
    attr = pd.DataFrame({col: ["TrustLLM"] * 12 for col in REQUIRED_COLS}, index=models)
    result = run_h_e1_audit(df, attr, {})
    assert result["N_common"] == 12, f"Expected 12, got {result['N_common']}"
    assert result["gate_passed"] is True
    print("Self-check passed.")
