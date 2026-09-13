"""H-M1 Oracle Isolation Experiment — orchestration entry point.

Oracle A: differential equality on CVT inputs — llm(x) != gt_plain(x)
Oracle B: contract oracle — reference_with_contracts(x) raises AssertionError
Both run on ContractEval CVT inputs (contract-violating test inputs).
"""
import sys
import json
import time
from pathlib import Path

CODE_DIR = Path(__file__).parent
ROOT = CODE_DIR.parent

sys.path.insert(0, str(CODE_DIR))

from data_loader import load_contracteval, load_evalplus_data, load_h1_corpus, verify_task_overlap
from soundness_check import run_soundness_precheck
from oracle_isolation import run_oracle_isolation, verify_activation
from statistical_analysis import aggregate_stats, save_results
from visualization import (
    plot_gate_metrics,
    plot_oracle_breakdown_by_model,
    plot_gap_distribution,
    plot_scatter_failure_rates,
)

RESULTS_DIR = str(ROOT / "code" / "results")
FIGURES_DIR = str(ROOT / "figures")
N_WORKERS = 8
TIMEOUT_PER_INPUT = 5
SEED = 42


def main():
    t0 = time.time()
    print("=" * 60)
    print("H-M1: Oracle Isolation Experiment")
    print("Oracle A: differential (llm vs gt_plain on CVT inputs)")
    print("Oracle B: contract (reference asserts on CVT inputs)")
    print("=" * 60)

    # Phase 1: Load data
    print("\n[Phase 1] Loading ContractEval, EvalPlus, H-E1 corpus...")
    tasks = load_contracteval()
    print(f"ContractEval tasks: {len(tasks)}")

    task_ids = list(tasks.keys())
    evalplus_data = load_evalplus_data(task_ids)
    print(f"EvalPlus data loaded for {len(evalplus_data)} tasks")

    corpus = load_h1_corpus()
    models = list(corpus.keys())
    print(f"H-E1 corpus: {len(models)} models, tasks per model: {[len(v) for v in corpus.values()]}")

    # Phase 2: Verify task ID overlap
    print("\n[Phase 2] Verifying task ID overlap...")
    ce_ids = set(tasks.keys())
    ep_ids = set(evalplus_data.keys())
    matched_ids, unmatched_ids = verify_task_overlap(ce_ids, ep_ids, threshold=0.90)
    print(f"Matched: {len(matched_ids)}, Unmatched: {len(unmatched_ids)}")

    # Check CVT coverage
    tasks_with_cvt = {tid for tid, t in tasks.items() if t.get("contract_violating_test")}
    print(f"Tasks with CVT inputs: {len(tasks_with_cvt)}/{len(tasks)}")

    # Phase 3: Soundness pre-check using CVT inputs
    print("\n[Phase 3] Oracle soundness pre-check...")
    soundness_path = str(Path(RESULTS_DIR) / "soundness_precheck.jsonl")
    valid_ids, quarantined_ids = run_soundness_precheck(
        tasks, results_path=soundness_path, timeout_per_task=30
    )
    print(f"Valid tasks: {len(valid_ids)}, Quarantined: {len(quarantined_ids)}")
    if len(valid_ids) < 100:
        print(f"WARNING: Only {len(valid_ids)} valid tasks")

    # Phase 4: Oracle isolation evaluation
    print(f"\n[Phase 4] Running dual-oracle evaluation ({N_WORKERS} workers)...")
    isolation_path = str(Path(RESULTS_DIR) / "isolation_results.jsonl")
    results = run_oracle_isolation(
        corpus=corpus,
        tasks=tasks,
        evalplus_data=evalplus_data,
        valid_task_ids=valid_ids,
        results_path=isolation_path,
        timeout_per_input=TIMEOUT_PER_INPUT,
        n_workers=N_WORKERS,
    )
    print(f"Evaluation complete: {len(results)} (model, task, program) triples")

    # Phase 5: Activation verification
    print("\n[Phase 5] Verifying oracle activation...")
    activated, indicators = verify_activation(results)
    print(f"Activation: {activated}")
    for k, v in indicators.items():
        print(f"  {k}: {v}")

    # Phase 6: Statistical analysis
    print("\n[Phase 6] Statistical analysis...")
    stats, per_task = aggregate_stats(
        results,
        n_total_tasks=len(tasks),
        n_bootstrap=10_000,
        seed=SEED,
        gap_threshold=0.10,
        cu_threshold=0.05,
        cu_ci_threshold=0.03,
        p_threshold=0.01,
    )
    print(f"Mean oracle-isolation gap: {stats.mean_isolation_gap:.4f}")
    print(f"  95% CI: [{stats.gap_ci_lower:.4f}, {stats.gap_ci_upper:.4f}]")
    print(f"Wilcoxon p (corrected): {stats.wilcoxon_p_corrected:.6f}")
    print(f"Mean contract-unique mass: {stats.mean_contract_unique_mass:.4f}")
    print(f"  95% CI lower: {stats.cu_ci_lower:.4f}")
    print(f"Mean diff failure rate: {stats.mean_diff_failure_rate:.4f}")
    print(f"Mean contract failure rate: {stats.mean_contract_failure_rate:.4f}")
    print(f"Task coverage: {stats.n_tasks_evaluated}/{len(tasks)} ({stats.task_coverage_rate:.1%})")
    print(f"Gate passed: {stats.gate_passed}")
    save_results(stats, per_task, RESULTS_DIR, results)

    # Phase 7: Figures
    print("\n[Phase 7] Generating figures...")
    plot_gate_metrics(stats, out_path=f"{FIGURES_DIR}/gate_metrics_comparison.png")
    plot_oracle_breakdown_by_model(results, out_path=f"{FIGURES_DIR}/oracle_failure_breakdown.png")
    plot_gap_distribution(per_task, out_path=f"{FIGURES_DIR}/gap_distribution.png")
    plot_scatter_failure_rates(per_task, out_path=f"{FIGURES_DIR}/scatter_failure_rates.png")

    # Phase 8: Write experiment_results.json
    elapsed = time.time() - t0
    experiment_results = {
        "hypothesis_id": "h-m1",
        "gate_passed": stats.gate_passed,
        "gate_verdict": "PASS" if stats.gate_passed else "FAIL",
        "mean_isolation_gap": stats.mean_isolation_gap,
        "gap_ci_lower": stats.gap_ci_lower,
        "gap_ci_upper": stats.gap_ci_upper,
        "wilcoxon_stat": stats.wilcoxon_stat,
        "wilcoxon_p_raw": stats.wilcoxon_p_raw,
        "wilcoxon_p_corrected": stats.wilcoxon_p_corrected,
        "mean_contract_unique_mass": stats.mean_contract_unique_mass,
        "cu_ci_lower": stats.cu_ci_lower,
        "cu_ci_upper": stats.cu_ci_upper,
        "n_tasks_evaluated": stats.n_tasks_evaluated,
        "n_quarantined": len(quarantined_ids),
        "task_coverage_rate": stats.task_coverage_rate,
        "n_programs_total": stats.n_programs_total,
        "mean_diff_failure_rate": stats.mean_diff_failure_rate,
        "mean_contract_failure_rate": stats.mean_contract_failure_rate,
        "by_model": stats.by_model,
        "by_task_type": stats.by_task_type,
        "elapsed_seconds": elapsed,
        "oracle_design_note": (
            "Oracle A: diff on CVT inputs (llm vs gt_plain); "
            "Oracle B: contract ref on CVT inputs (AssertionError = contract caught violation)"
        ),
    }

    out_path = Path(RESULTS_DIR) / "experiment_results.json"
    with open(out_path, "w") as f:
        json.dump(experiment_results, f, indent=2)
    print(f"\nExperiment results: {out_path}")
    print(f"Total elapsed: {elapsed/60:.1f} min")
    print(f"\n{'='*60}")
    print(f"GATE: {'PASSED' if stats.gate_passed else 'FAILED'}")
    print(f"{'='*60}")

    return experiment_results


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result["gate_passed"] else 1)
