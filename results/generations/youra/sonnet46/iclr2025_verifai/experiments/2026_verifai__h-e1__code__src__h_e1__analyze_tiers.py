"""Tier analysis, gate evaluation, and pass@1 for H-E1."""
from __future__ import annotations

import csv
import itertools
import json
import os
from typing import Optional

import numpy as np

HARD_THRESHOLD: float = 0.0
EASY_THRESHOLD: float = 0.6
MIN_N: int = 20


def compute_pass_at_1(
    correctness: dict[str, list[bool]],
    k: int = 5,
) -> dict[str, float]:
    """Compute pass@1 = correct_count / k per task.
    correctness: {task_id: [bool × k]}
    Returns: {task_id: float}  # values in {0.0, 0.2, 0.4, 0.6, 0.8, 1.0}
    """
    return {tid: sum(res) / k for tid, res in correctness.items()}


def assign_tiers(
    pass_at_1: dict[str, float],
    hard_thresh: float = HARD_THRESHOLD,
    easy_thresh: float = EASY_THRESHOLD,
) -> dict[str, str]:
    """Assign tier labels per task.
    Returns: {task_id: "hard" | "easy" | "medium"}
    hard:   pass@1 <= hard_thresh (default: ==0.0)
    easy:   pass@1 >= easy_thresh (default: >=0.6)
    medium: otherwise
    """
    tiers: dict[str, str] = {}
    for tid, p in pass_at_1.items():
        if p <= hard_thresh:
            tiers[tid] = "hard"
        elif p >= easy_thresh:
            tiers[tid] = "easy"
        else:
            tiers[tid] = "medium"
    return tiers


def count_tiers(
    tiers: dict[str, str],
    problem_ids_he: list[str],
    problem_ids_mbpp: list[str],
) -> dict[str, dict[str, int]]:
    """Count tier members per benchmark.
    Returns: {"humaneval": {"hard": int, "easy": int, "medium": int},
              "mbpp":      {"hard": int, "easy": int, "medium": int}}
    """
    result: dict[str, dict[str, int]] = {
        "humaneval": {"hard": 0, "easy": 0, "medium": 0},
        "mbpp": {"hard": 0, "easy": 0, "medium": 0},
    }
    he_set = set(problem_ids_he)
    mbpp_set = set(problem_ids_mbpp)
    for tid, tier in tiers.items():
        if tid in he_set:
            result["humaneval"][tier] = result["humaneval"].get(tier, 0) + 1
        elif tid in mbpp_set:
            result["mbpp"][tier] = result["mbpp"].get(tier, 0) + 1
    return result


def evaluate_gate(
    all_tier_counts: dict[str, dict[str, dict[str, int]]],
    min_n: int = MIN_N,
) -> dict:
    """Evaluate gate condition across all models and benchmarks.
    all_tier_counts: {model_id: {benchmark: {tier: count}}}
    Returns: {
        "gate_pass": bool,
        "models_passing": int,
        "benchmark_passing": str | None,
        "n_hard_per": dict,
        "n_easy_per": dict,
    }
    Gate PASS: models_passing >= 2 on at least 1 benchmark
    """
    n_hard_per: dict[str, dict[str, int]] = {}
    n_easy_per: dict[str, dict[str, int]] = {}

    benchmarks = ["humaneval", "mbpp"]
    models_passing_per_benchmark: dict[str, int] = {b: 0 for b in benchmarks}

    for model_id, bench_counts in all_tier_counts.items():
        n_hard_per[model_id] = {}
        n_easy_per[model_id] = {}
        for benchmark in benchmarks:
            counts = bench_counts.get(benchmark, {})
            n_hard = counts.get("hard", 0)
            n_easy = counts.get("easy", 0)
            n_hard_per[model_id][benchmark] = n_hard
            n_easy_per[model_id][benchmark] = n_easy
            if n_hard >= min_n and n_easy >= min_n:
                models_passing_per_benchmark[benchmark] += 1

    # Gate PASS: >= 2 models passing on >= 1 benchmark
    best_passing = max(models_passing_per_benchmark.values())
    benchmark_passing: Optional[str] = None
    for b, cnt in models_passing_per_benchmark.items():
        if cnt == best_passing and cnt >= 2:
            benchmark_passing = b
            break

    gate_pass = best_passing >= 2
    models_passing = best_passing

    return {
        "gate_pass": gate_pass,
        "models_passing": models_passing,
        "benchmark_passing": benchmark_passing,
        "n_hard_per": n_hard_per,
        "n_easy_per": n_easy_per,
    }


def verify_tier_mechanism_activated(
    tier_results: dict,
    coverage_rate: float,
) -> tuple[bool, dict]:
    """Assert n_hard > 0, n_easy > 0, coverage >= 0.95.
    Returns: (all_ok: bool, indicators: dict[str, bool])
    """
    indicators = {
        "n_hard_gt_0": any(
            tier_results.get("n_hard_per", {}).get(m, {}).get("humaneval", 0) > 0 or
            tier_results.get("n_hard_per", {}).get(m, {}).get("mbpp", 0) > 0
            for m in tier_results.get("n_hard_per", {})
        ),
        "n_easy_gt_0": any(
            tier_results.get("n_easy_per", {}).get(m, {}).get("humaneval", 0) > 0 or
            tier_results.get("n_easy_per", {}).get(m, {}).get("mbpp", 0) > 0
            for m in tier_results.get("n_easy_per", {})
        ),
        "coverage_ok": coverage_rate >= 0.95,
    }
    all_ok = all(indicators.values())
    return all_ok, indicators


def relax_and_retry(
    correctness_all: dict[str, dict[str, list[bool]]],
    benchmark_map: dict[str, str],
    problem_ids_he: list[str],
    problem_ids_mbpp: list[str],
    relaxed_hard_thresh: float = 0.2,
) -> dict:
    """Recompute gate with hard_thresh=0.2.
    correctness_all: {model_id: {task_id: [bool × k]}}
    Returns: gate result dict (same schema as evaluate_gate)
    """
    all_tier_counts: dict[str, dict[str, dict[str, int]]] = {}
    for model_id, correctness in correctness_all.items():
        pass_at_1 = compute_pass_at_1(correctness)
        tiers = assign_tiers(pass_at_1, hard_thresh=relaxed_hard_thresh, easy_thresh=EASY_THRESHOLD)
        all_tier_counts[model_id] = count_tiers(tiers, problem_ids_he, problem_ids_mbpp)
    return evaluate_gate(all_tier_counts)


def save_tier_statistics(stats: list[dict], output_path: str) -> None:
    """Save tier statistics CSV.
    CSV columns: model, benchmark, n_hard, n_easy, n_medium, n_total, coverage_rate, gate_pass
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fieldnames = ["model", "benchmark", "n_hard", "n_easy", "n_medium", "n_total", "coverage_rate", "gate_pass"]
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in stats:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def save_pass_at_1(pass_at_1: dict, output_path: str) -> None:
    """Save {task_id: float} as JSON per model."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(pass_at_1, f)


def compute_jaccard_similarity(set_a: set, set_b: set) -> float:
    """Jaccard = |A ∩ B| / |A ∪ B|. Returns 0.0 if union is empty."""
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)


def compute_cross_model_overlap(
    tiers_per_model: dict[str, dict[str, str]],
) -> dict[tuple[str, str], float]:
    """Compute pairwise Jaccard on hard-tier task sets across models.
    tiers_per_model: {model_id: {task_id: "hard"|"easy"|"medium"}}
    Returns: {(model_a, model_b): jaccard_float}
    """
    hard_sets = {
        model_id: {tid for tid, tier in tiers.items() if tier == "hard"}
        for model_id, tiers in tiers_per_model.items()
    }
    model_ids = list(hard_sets.keys())
    result: dict[tuple[str, str], float] = {}
    for a, b in itertools.combinations(model_ids, 2):
        result[(a, b)] = compute_jaccard_similarity(hard_sets[a], hard_sets[b])
    return result


def main(args=None) -> None:
    """Entry point: analyze tier statistics."""
    import argparse
    parser = argparse.ArgumentParser(description="Analyze tier statistics")
    parser.add_argument("--results_dir", type=str, default="results")
    parser.add_argument("--output_dir", type=str, default="results")
    parser.add_argument("--hard_threshold", type=float, default=HARD_THRESHOLD)
    parser.add_argument("--easy_threshold", type=float, default=EASY_THRESHOLD)
    if args is None:
        args = parser.parse_args()

    from evalplus.data import get_human_eval_plus, get_mbpp_plus
    problems_he = get_human_eval_plus()
    problems_mbpp = get_mbpp_plus()
    problem_ids_he = list(problems_he.keys())
    problem_ids_mbpp = list(problems_mbpp.keys())

    model_short_names = {"llama3_8b", "codellama_7b", "deepseek_6.7b"}
    correctness_all: dict[str, dict[str, list[bool]]] = {}

    for model_short in model_short_names:
        corr_path = os.path.join(args.results_dir, f"correctness_{model_short}.json")
        if os.path.exists(corr_path):
            with open(corr_path) as f:
                correctness_all[model_short] = json.load(f)

    if not correctness_all:
        print("No correctness files found. Run evaluate_solutions first.")
        return

    # Compute tier stats and gate
    all_tier_counts: dict[str, dict[str, dict[str, int]]] = {}
    tiers_per_model: dict[str, dict[str, str]] = {}
    stats = []

    for model_id, correctness in correctness_all.items():
        pass_at_1 = compute_pass_at_1(correctness)
        tiers = assign_tiers(pass_at_1, hard_thresh=args.hard_threshold, easy_thresh=args.easy_threshold)
        tiers_per_model[model_id] = tiers
        all_tier_counts[model_id] = count_tiers(tiers, problem_ids_he, problem_ids_mbpp)

        coverage_rate = len(correctness) / (len(problem_ids_he) + len(problem_ids_mbpp))
        for benchmark in ["humaneval", "mbpp"]:
            counts = all_tier_counts[model_id][benchmark]
            n_total = sum(counts.values())
            stats.append({
                "model": model_id,
                "benchmark": benchmark,
                "n_hard": counts.get("hard", 0),
                "n_easy": counts.get("easy", 0),
                "n_medium": counts.get("medium", 0),
                "n_total": n_total,
                "coverage_rate": round(coverage_rate, 4),
                "gate_pass": False,  # updated after gate eval
            })

        # Save pass@1
        p1_path = os.path.join(args.output_dir, f"pass_at_1_{model_id}.json")
        save_pass_at_1(pass_at_1, p1_path)

    gate = evaluate_gate(all_tier_counts)
    print(f"Gate result: {'PASS' if gate['gate_pass'] else 'FAIL'}")
    print(f"Models passing: {gate['models_passing']}")

    # Update gate_pass in stats
    for row in stats:
        model = row["model"]
        benchmark = row["benchmark"]
        n_hard = row["n_hard"]
        n_easy = row["n_easy"]
        row["gate_pass"] = n_hard >= MIN_N and n_easy >= MIN_N

    csv_path = os.path.join(args.output_dir, "tier_statistics.csv")
    save_tier_statistics(stats, csv_path)
    print(f"Saved tier statistics to {csv_path}")

    # Cross-model overlap
    overlap = compute_cross_model_overlap(tiers_per_model)
    for pair, jaccard in overlap.items():
        print(f"Jaccard {pair[0]} vs {pair[1]}: {jaccard:.3f}")


if __name__ == "__main__":
    main()
