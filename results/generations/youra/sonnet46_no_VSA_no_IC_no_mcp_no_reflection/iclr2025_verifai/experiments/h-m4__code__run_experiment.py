"""H-M4 entry point: run all 538 × 4 = 2,152 repair loop timing experiments."""
import json
import os
import sys
import numpy as np
from pathlib import Path

# Allow running from the code/ directory
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    CATEGORIES, MAX_ITERS, FIGURES_DIR, RESULTS_PATH,
    SUMMARY_PATH, CHECKPOINT_PATH, N_BOOTSTRAP, SEED
)
from data_loader import load_combined, load_baseline_pass
from verifiers import make_verifier_fns
from stats import (
    summarize_overhead, kruskal_wallis_overhead, mannwhitney_pairwise,
    evaluate_gate_metric, compute_per_problem_ratios, bootstrap_ratio_comparison,
    CATEGORIES as STAT_CATS,
)
from visualize import generate_all_figures
from runner import run_experiment


def main() -> None:
    # -----------------------------------------------------------------------
    # 0. OpenAI client
    # -----------------------------------------------------------------------
    from openai import OpenAI
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set.")
        sys.exit(1)
    llm_client = OpenAI(api_key=api_key)

    # -----------------------------------------------------------------------
    # 1. Load problems
    # -----------------------------------------------------------------------
    print("Loading 538 problems...")
    problems = load_combined()
    assert len(problems) >= 100, f"Expected ≥100 problems, got {len(problems)}"

    # -----------------------------------------------------------------------
    # 2. Baseline pass@1
    # -----------------------------------------------------------------------
    baseline_pass = load_baseline_pass()

    # -----------------------------------------------------------------------
    # 3. Verifiers
    # -----------------------------------------------------------------------
    verifier_fns = make_verifier_fns(llm_client)

    # -----------------------------------------------------------------------
    # 4. Run experiment (with checkpoint/resume)
    # -----------------------------------------------------------------------
    np.random.seed(SEED)
    results = run_experiment(
        problems=problems,
        categories=CATEGORIES,
        checkpoint_path=CHECKPOINT_PATH,
        baseline_pass=baseline_pass,
        llm_client=llm_client,
        verifier_fns=verifier_fns,
        max_iters=MAX_ITERS,
    )

    # -----------------------------------------------------------------------
    # 5. Save results.json
    # -----------------------------------------------------------------------
    Path(RESULTS_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved: {RESULTS_PATH} ({len(results)} records)")

    # -----------------------------------------------------------------------
    # 6. Compute stats + gate metric
    # -----------------------------------------------------------------------
    gate = evaluate_gate_metric(results, baseline_pass)

    overhead_by_cat = {}
    for cat in CATEGORIES:
        overhead_by_cat[cat] = [r['total_overhead_s'] for r in results if r['category'] == cat]

    overhead_summary = summarize_overhead(overhead_by_cat)
    kw = kruskal_wallis_overhead(overhead_by_cat)
    mw = mannwhitney_pairwise(overhead_by_cat)

    # CI bounds for bar chart
    ci_bounds = {}
    best_cat = gate.get('best_category', 'execution')
    for cat in CATEGORIES:
        per_prob = compute_per_problem_ratios(results, baseline_pass, cat)
        per_prob_best = compute_per_problem_ratios(results, baseline_pass, best_cat)
        if cat == best_cat:
            ci_bounds[cat] = (gate.get('bootstrap_result', {}).get('ci_low', 0),
                              gate.get('bootstrap_result', {}).get('ci_high', 0))
        else:
            bs = bootstrap_ratio_comparison(per_prob, per_prob_best, n_resamples=1000)
            ratio_val = gate['ratios'].get(cat, 0)
            ci_bounds[cat] = (ratio_val + bs.get('ci_low', 0), ratio_val + bs.get('ci_high', 0))

    # Sanity checks
    mean_overhead = gate.get('overhead_means', {})
    print(f"\nOverhead ordering: {sorted(mean_overhead.items(), key=lambda x: x[1])}")
    print(f"Efficiency ratios: {gate.get('ratios', {})}")
    if mean_overhead.get('execution', 0) > 0.05:
        print("SANITY OK: execution overhead > 50ms")
    else:
        print("SANITY WARN: execution overhead suspiciously low")
    if mean_overhead.get('smt', 0) > mean_overhead.get('execution', 0):
        print("SANITY OK: SMT > execution overhead")
    else:
        print("SANITY WARN: SMT not slower than execution")

    # -----------------------------------------------------------------------
    # 7. Save summary.json
    # -----------------------------------------------------------------------
    summary = {
        "hypothesis_id": "H-M4",
        "n_problems": len(set(r['task_id'] for r in results)),
        "n_results": len(results),
        "categories": CATEGORIES,
        "gate": gate,
        "overhead_summary": overhead_summary,
        "kruskal_wallis": kw,
        "mannwhitney_pairwise": {str(k): v for k, v in mw.items()},
    }
    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary saved: {SUMMARY_PATH}")

    # -----------------------------------------------------------------------
    # 8. Figures
    # -----------------------------------------------------------------------
    generate_all_figures(results, gate.get('ratios', {}), ci_bounds, FIGURES_DIR)

    # -----------------------------------------------------------------------
    # 9. Gate verdict
    # -----------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("H-M4 GATE RESULT")
    print("=" * 60)
    print(f"Gate type: SHOULD_WORK")
    print(f"Best category: {gate.get('best_category')}")
    print(f"Execution is best: {gate.get('execution_is_best')}")
    print(f"Ratio advantage: {gate.get('ratio_advantage', 0):.3f}x")
    print(f"Bootstrap significant: {gate.get('bootstrap_result', {}).get('significant', False)}")
    print(f"Gate PASSED: {gate.get('gate_passed', False)}")
    print("=" * 60)

    print("\nEXPERIMENT COMPLETE")


if __name__ == "__main__":
    main()
