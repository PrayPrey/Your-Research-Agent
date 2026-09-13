"""Main experiment orchestrator for H-E1."""
from __future__ import annotations

import argparse
import json
import os
import sys

from .generate_solutions import (
    load_all_problems,
    partition_by_benchmark,
    generate_solutions_for_model,
    MODEL_IDS,
    MODEL_SHORT_NAMES,
)
from .evaluate_solutions import (
    evaluate_all_solutions,
    compute_coverage_rate,
    save_correctness,
    load_problems,
)
from .analyze_tiers import (
    compute_pass_at_1,
    assign_tiers,
    count_tiers,
    evaluate_gate,
    relax_and_retry,
    save_tier_statistics,
    save_pass_at_1,
    compute_cross_model_overlap,
    MIN_N,
)
from .visualize import (
    plot_tier_sizes_bar,
    plot_pass_at_1_distribution,
    plot_tier_size_heatmap,
    plot_coverage_rate,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="H-E1 Experiment: Difficulty-Tier Viability Check")
    parser.add_argument("--output_dir", type=str, default="results", help="Directory for result files")
    parser.add_argument("--figures_dir", type=str, default="figures", help="Directory for figures")
    parser.add_argument("--smoke_test", action="store_true", help="Run on 5 problems only")
    parser.add_argument("--skip_generation", action="store_true", help="Skip generation if solutions exist")
    parser.add_argument("--gpu_id", type=str, default="0", help="GPU ID to use")
    parser.add_argument("--hard_threshold", type=float, default=0.0)
    parser.add_argument("--easy_threshold", type=float, default=0.6)
    return parser.parse_args()


def run_pipeline(args) -> dict:
    """Orchestrate: generate → evaluate → analyze → visualize.
    Returns: gate result dict
    """
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.figures_dir, exist_ok=True)

    # Set GPU
    if hasattr(args, "gpu_id") and args.gpu_id:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu_id)

    # === PHASE 1: Load problems ===
    print("=" * 60)
    print("PHASE 1: Loading EvalPlus problems...")
    problems_he, problems_mbpp = load_all_problems()
    benchmark_map = partition_by_benchmark(problems_he, problems_mbpp)
    problems_all = {**problems_he, **problems_mbpp}

    if args.smoke_test:
        smoke_ids = list(problems_all.keys())[:5]
        problems_all = {tid: problems_all[tid] for tid in smoke_ids}
        benchmark_map = {tid: benchmark_map[tid] for tid in smoke_ids}

    print(f"  HumanEval+: {len(problems_he)} | MBPP+: {len(problems_mbpp)}")
    problem_ids_he = list(problems_he.keys())
    problem_ids_mbpp = list(problems_mbpp.keys())

    # === PHASE 2: Generate solutions ===
    print("\nPHASE 2: Generating k=5 solutions per model...")
    all_solutions: dict[str, dict] = {}

    for model_id in MODEL_IDS:
        model_short = MODEL_SHORT_NAMES[model_id]
        output_path = os.path.join(args.output_dir, f"solutions_{model_short}.jsonl")

        if args.skip_generation and os.path.exists(output_path):
            print(f"  Skipping {model_id} (solutions exist)")
            from .generate_solutions import load_existing_solutions
            sols = load_existing_solutions(output_path)
            all_solutions[model_id] = sols or {}
            continue

        print(f"  Generating for {model_id}...")
        try:
            sols = generate_solutions_for_model(model_id, problems_all, benchmark_map, output_path)
            all_solutions[model_id] = sols
            print(f"  ✓ {len(sols)} problems")
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            all_solutions[model_id] = {}

    # === PHASE 3: Evaluate correctness ===
    print("\nPHASE 3: Evaluating solutions with EvalPlus...")
    correctness_all: dict[str, dict] = {}

    for model_id in MODEL_IDS:
        model_short = MODEL_SHORT_NAMES[model_id]
        corr_path = os.path.join(args.output_dir, f"correctness_{model_short}.json")

        if os.path.exists(corr_path):
            print(f"  Loading existing correctness for {model_short}...")
            with open(corr_path) as f:
                correctness_all[model_id] = json.load(f)
            continue

        solutions = all_solutions.get(model_id, {})
        if not solutions:
            print(f"  No solutions for {model_id}, skipping evaluation")
            continue

        print(f"  Evaluating {model_id}...")
        try:
            correctness = evaluate_all_solutions(solutions, problems_he, problems_mbpp, args.output_dir, model_short)
            correctness_all[model_id] = correctness
            save_correctness(correctness, corr_path)
            coverage = compute_coverage_rate(set(correctness.keys()), set(problems_all.keys()))
            print(f"  ✓ Coverage: {coverage:.4f}")
        except Exception as e:
            print(f"  ✗ Evaluation failed: {e}")
            correctness_all[model_id] = {}

    # === PHASE 4: Tier analysis and gate ===
    print("\nPHASE 4: Computing tier statistics and gate...")
    all_tier_counts: dict[str, dict] = {}
    tiers_per_model: dict[str, dict] = {}
    stats = []
    coverage_per_model: dict[str, float] = {}
    pass_at_1_per_model: dict = {}

    total_problems = len(problems_he) + len(problems_mbpp)

    for model_id, correctness in correctness_all.items():
        if not correctness:
            continue
        model_short = MODEL_SHORT_NAMES[model_id]
        pass_at_1 = compute_pass_at_1(correctness)
        tiers = assign_tiers(pass_at_1, hard_thresh=args.hard_threshold, easy_thresh=args.easy_threshold)
        tiers_per_model[model_id] = tiers
        all_tier_counts[model_id] = count_tiers(tiers, problem_ids_he, problem_ids_mbpp)

        coverage = len(correctness) / total_problems
        coverage_per_model[model_short] = coverage

        # Save pass@1
        p1_path = os.path.join(args.output_dir, f"pass_at_1_{model_short}.json")
        save_pass_at_1(pass_at_1, p1_path)

        # Split pass@1 by benchmark for visualization
        he_p1 = {tid: v for tid, v in pass_at_1.items() if tid in problems_he}
        mbpp_p1 = {tid: v for tid, v in pass_at_1.items() if tid in problems_mbpp}
        pass_at_1_per_model[model_short] = {"humaneval": he_p1, "mbpp": mbpp_p1}

        for benchmark in ["humaneval", "mbpp"]:
            counts = all_tier_counts[model_id][benchmark]
            n_hard = counts.get("hard", 0)
            n_easy = counts.get("easy", 0)
            stats.append({
                "model": model_short,
                "benchmark": benchmark,
                "n_hard": n_hard,
                "n_easy": n_easy,
                "n_medium": counts.get("medium", 0),
                "n_total": sum(counts.values()),
                "coverage_rate": round(coverage, 4),
                "gate_pass": n_hard >= MIN_N and n_easy >= MIN_N,
            })

    # Primary gate
    gate_result = evaluate_gate(all_tier_counts)

    if not gate_result["gate_pass"]:
        print("  Primary gate FAIL — trying relaxed threshold (hard_thresh=0.2)...")
        gate_result = relax_and_retry(correctness_all, benchmark_map, problem_ids_he, problem_ids_mbpp)
        if gate_result["gate_pass"]:
            print("  Gate PASS with relaxed threshold=0.2")

    # Save tier statistics CSV
    csv_path = os.path.join(args.output_dir, "tier_statistics.csv")
    save_tier_statistics(stats, csv_path)

    # Cross-model overlap (for H-M2 prep)
    if len(tiers_per_model) > 1:
        overlap = compute_cross_model_overlap(tiers_per_model)
        overlap_path = os.path.join(args.output_dir, "cross_model_overlap.json")
        overlap_serializable = {str(k): v for k, v in overlap.items()}
        with open(overlap_path, "w") as f:
            json.dump(overlap_serializable, f, indent=2)

    # Save gate summary
    gate_summary = {
        "gate_pass": gate_result["gate_pass"],
        "models_passing": gate_result["models_passing"],
        "n_hard_per": gate_result.get("n_hard_per", {}),
        "n_easy_per": gate_result.get("n_easy_per", {}),
        "benchmark_passing": gate_result.get("benchmark_passing"),
        "hard_threshold": args.hard_threshold,
        "easy_threshold": args.easy_threshold,
    }
    gate_summary_path = os.path.join(args.output_dir, "gate_summary.json")
    with open(gate_summary_path, "w") as f:
        json.dump(gate_summary, f, indent=2)

    # === PHASE 5: Visualization ===
    print("\nPHASE 5: Generating figures...")
    if stats:
        plot_tier_sizes_bar(stats, output_path=os.path.join(args.figures_dir, "tier_sizes_bar.png"))
        plot_tier_size_heatmap(stats, output_path=os.path.join(args.figures_dir, "tier_size_heatmap.png"))
        print("  ✓ tier_sizes_bar.png, tier_size_heatmap.png")

    if pass_at_1_per_model:
        plot_pass_at_1_distribution(pass_at_1_per_model, output_path=os.path.join(args.figures_dir, "pass_at_1_distribution.png"))
        print("  ✓ pass_at_1_distribution.png")

    if coverage_per_model:
        plot_coverage_rate(coverage_per_model, output_path=os.path.join(args.figures_dir, "coverage_rate.png"))
        print("  ✓ coverage_rate.png")

    gate_result["stats"] = stats
    gate_result["coverage_per_model"] = coverage_per_model
    return gate_result


def print_summary(gate_result: dict) -> None:
    """Print gate PASS/FAIL with n_hard/n_easy counts."""
    print("\n" + "=" * 60)
    print("H-E1 GATE RESULT:", "PASS ✓" if gate_result["gate_pass"] else "FAIL ✗")
    print(f"Models passing: {gate_result['models_passing']}/3")
    print("=" * 60)

    n_hard_per = gate_result.get("n_hard_per", {})
    n_easy_per = gate_result.get("n_easy_per", {})
    for model_id in n_hard_per:
        for benchmark in ["humaneval", "mbpp"]:
            n_hard = n_hard_per.get(model_id, {}).get(benchmark, 0)
            n_easy = n_easy_per.get(model_id, {}).get(benchmark, 0)
            status = "OK" if n_hard >= 20 and n_easy >= 20 else "FAIL"
            print(f"  {model_id:<20} {benchmark:<12} hard={n_hard:3d} easy={n_easy:3d}  [{status}]")

    if gate_result["gate_pass"]:
        print("\n✓ H-E1 GATE PASS — H-M1 unblocked")
    else:
        print("\n✗ H-E1 GATE FAIL — Pipeline stopping")


if __name__ == "__main__":
    args = parse_args()
    result = run_pipeline(args)
    print_summary(result)
    sys.exit(0 if result["gate_pass"] else 1)
