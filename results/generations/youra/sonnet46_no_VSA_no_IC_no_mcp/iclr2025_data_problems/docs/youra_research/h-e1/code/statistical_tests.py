"""E4: Paired t-test + mechanism verification for Pile vs dedup-Pile benchmark comparison."""
import json
from pathlib import Path

import numpy as np
from scipy.stats import ttest_rel

BASE_DIR = Path(__file__).parent.parent
MATRIX_FILE = BASE_DIR / "results_matrix.json"
OUTPUT_FILE = BASE_DIR / "statistical_results.json"

SIZES = ["160m", "410m", "1b", "6.9b"]
BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
CORRECTED_ALPHA: float = 0.0125   # Bonferroni: 0.05 / 4
MIN_DELTA: float = 0.001


def verify_mechanism_activation(
    matrix: dict,
    sizes: list[str] = SIZES,
    benchmarks: list[str] = BENCHMARKS,
    min_delta: float = MIN_DELTA,
) -> bool:
    for s in sizes:
        for b in benchmarks:
            pile_acc = matrix.get(s, {}).get("pile", {}).get(b)
            dedup_acc = matrix.get(s, {}).get("dedup", {}).get(b)
            if pile_acc is not None and dedup_acc is not None:
                if abs(dedup_acc - pile_acc) > min_delta:
                    return True
    raise RuntimeError(
        "All model pairs produce identical accuracy (|delta| <= 0.001 for every (size, benchmark) pair). "
        "Checkpoint loading error — verify revision tags and model IDs."
    )


def paired_ttest_per_benchmark(
    matrix: dict,
    sizes: list[str] = SIZES,
    benchmarks: list[str] = BENCHMARKS,
    corrected_alpha: float = CORRECTED_ALPHA,
) -> dict:
    results = {}
    for bench in benchmarks:
        pile_accs = []
        dedup_accs = []
        for s in sizes:
            p = matrix.get(s, {}).get("pile", {}).get(bench)
            d = matrix.get(s, {}).get("dedup", {}).get(bench)
            if p is not None and d is not None:
                pile_accs.append(p)
                dedup_accs.append(d)

        if len(pile_accs) < 2:
            results[bench] = {
                "t_stat": None,
                "p_value": None,
                "mean_diff": None,
                "diffs": [],
                "significant": False,
                "direction": "insufficient_data",
            }
            continue

        t_stat, p_value = ttest_rel(dedup_accs, pile_accs)
        diffs = [d - p for d, p in zip(dedup_accs, pile_accs)]
        mean_diff = float(np.mean(diffs))

        if mean_diff > 0:
            direction = "dedup_higher"
        elif mean_diff < 0:
            direction = "pile_higher"
        else:
            direction = "mixed"

        results[bench] = {
            "t_stat": float(t_stat),
            "p_value": float(p_value),
            "mean_diff": round(mean_diff, 6),
            "diffs": [round(d, 6) for d in diffs],
            "significant": bool(p_value < corrected_alpha),
            "direction": direction,
        }

    gate_passed = any(v.get("significant", False) for v in results.values())
    mechanism_verified = True  # set after verify_mechanism_activation succeeds

    results["gate_passed"] = gate_passed
    results["mechanism_verified"] = mechanism_verified
    return results


def evaluate_gate(stats: dict) -> bool:
    return bool(stats.get("gate_passed", False))


def main() -> None:
    matrix = json.loads(MATRIX_FILE.read_text())

    print("Verifying mechanism activation...")
    verify_mechanism_activation(matrix)
    print("  Mechanism activation confirmed (≥1 pair shows |delta| > 0.001)")

    print("Running paired t-tests (Bonferroni α=0.0125)...")
    stats = paired_ttest_per_benchmark(matrix)

    print("\nResults:")
    for bench in BENCHMARKS:
        r = stats.get(bench, {})
        if r.get("t_stat") is None:
            print(f"  {bench}: INSUFFICIENT DATA")
        else:
            sig_marker = "***" if r["significant"] else "ns"
            print(
                f"  {bench}: t={r['t_stat']:.3f} p={r['p_value']:.4f} "
                f"mean_diff={r['mean_diff']:+.4f} [{r['direction']}] {sig_marker}"
            )

    gate = evaluate_gate(stats)
    print(f"\nGate PASSED: {gate}")

    OUTPUT_FILE.write_text(json.dumps(stats, indent=2))
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
