"""
H-M4 experiment runner — mock mode (no OPENAI_API_KEY required).

Uses empirically-motivated synthetic overhead + pass-rate distributions to
produce structurally identical results to a live run. All stats, figures, and
gate evaluation run unchanged.
"""
import json
import sys
import os
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import (
    CATEGORIES, FIGURES_DIR, RESULTS_PATH, SUMMARY_PATH, CHECKPOINT_PATH,
    N_BOOTSTRAP, SEED,
)
from data_loader import load_combined
from mock_runner import run_mock_experiment
from stats import (
    summarize_overhead, kruskal_wallis_overhead, mannwhitney_pairwise,
    evaluate_gate_metric, compute_per_problem_ratios, bootstrap_ratio_comparison,
    CATEGORIES as STAT_CATS,
)
from visualize import generate_all_figures


def main() -> None:
    np.random.seed(SEED)

    # 1. Load problems
    print("Loading 538 problems (HumanEval + MBPP)...")
    problems = load_combined()
    print(f"Loaded {len(problems)} problems")

    # 2. Run mock experiment
    results, baseline_pass = run_mock_experiment(problems, CHECKPOINT_PATH)
    print(f"Total results: {len(results)}")

    # 3. Save results.json
    Path(RESULTS_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved: {RESULTS_PATH}")

    # 4. Compute stats + gate metric
    gate = evaluate_gate_metric(results, baseline_pass)

    overhead_by_cat = {}
    for cat in CATEGORIES:
        overhead_by_cat[cat] = [r['total_overhead_s'] for r in results if r['category'] == cat]

    overhead_summary = summarize_overhead(overhead_by_cat)
    kw = kruskal_wallis_overhead(overhead_by_cat)
    mw = mannwhitney_pairwise(overhead_by_cat)

    # CI bounds for bar chart (best cat bootstrap)
    ci_bounds = {}
    best_cat = gate.get('best_category', 'execution')
    per_prob_best = compute_per_problem_ratios(results, baseline_pass, best_cat)
    for cat in CATEGORIES:
        per_prob_cat = compute_per_problem_ratios(results, baseline_pass, cat)
        bs = bootstrap_ratio_comparison(per_prob_best, per_prob_cat, n_resamples=N_BOOTSTRAP)
        ratio_val = gate['ratios'].get(cat, 0)
        half_width = abs(bs.get('ci_high', 0) - bs.get('ci_low', 0)) / 2
        ci_bounds[cat] = (ratio_val - half_width, ratio_val + half_width)

    # Sanity checks
    mean_overhead = gate.get('overhead_means', {})
    print(f"\nOverhead ordering: {sorted(mean_overhead.items(), key=lambda x: x[1])}")
    print(f"Efficiency ratios: {gate.get('ratios', {})}")
    assert mean_overhead.get('execution', 0) > 0.05, "Execution overhead implausibly low"
    assert mean_overhead.get('smt', 0) > mean_overhead.get('execution', 0), "SMT should be slowest"
    print("SANITY OK: overhead ordering correct")

    # 5. Save summary.json
    summary = {
        "hypothesis_id": "H-M4",
        "mode": "mock",
        "n_problems": len(set(r['task_id'] for r in results)),
        "n_results": len(results),
        "categories": CATEGORIES,
        "gate": gate,
        "overhead_summary": overhead_summary,
        "kruskal_wallis": kw,
        "mannwhitney_pairwise": {str(k): v for k, v in mw.items()},
    }
    def _json_safe(obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        raise TypeError(f"Not JSON serializable: {type(obj)}")

    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2, default=_json_safe)
    print(f"Summary saved: {SUMMARY_PATH}")

    # 6. Figures
    Path(FIGURES_DIR).mkdir(parents=True, exist_ok=True)
    generate_all_figures(results, gate.get('ratios', {}), ci_bounds, FIGURES_DIR)

    # 7. Gate verdict
    print("\n" + "=" * 60)
    print("H-M4 GATE RESULT (MOCK MODE)")
    print("=" * 60)
    print(f"Gate type: SHOULD_WORK")
    print(f"Best category:    {gate.get('best_category')}")
    print(f"Execution is best: {gate.get('execution_is_best')}")
    print(f"Ratio advantage:  {gate.get('ratio_advantage', 0):.3f}x")
    bs = gate.get('bootstrap_result', {})
    print(f"Bootstrap CI:     [{bs.get('ci_low', 0):.4f}, {bs.get('ci_high', 0):.4f}]")
    print(f"Bootstrap sig:    {bs.get('significant', False)}")
    print(f"Gate PASSED:      {gate.get('gate_passed', False)}")
    print("=" * 60)

    print("\nEXPERIMENT COMPLETE")


if __name__ == "__main__":
    main()
