"""
H-E1 Orchestration script: Contract-Strength Gap Existence Verification.

Pipeline:
  1. load_contracteval() — 364 tasks
  2. run_soundness_precheck() — quarantine tasks where ref impl has no contracts
  3. get_canonical_samples() — proxy for LLM-generated code (n=10 per task)
  4. run_contract_checking() — PBT using CVT inputs per model
  5. aggregate_metrics() — mean_gap + 95% CI + gate evaluation
  6. save results/summary.json + results/summary_report.md
  7. generate figures

Usage:
    python run_experiment.py
"""
import json
import sys
from pathlib import Path

# Ensure code/ is on path
sys.path.insert(0, str(Path(__file__).parent))

from config import default_config
from data_loader import load_contracteval, get_tasks_with_cvts, get_z3_tractable_ids
from oracle_checker import run_soundness_precheck
from code_generator import get_canonical_samples, save_samples, load_passing_samples, MODELS
from contract_checker import run_contract_checking
from metrics import aggregate_metrics, compute_per_task_gap, save_results_csv
from figures import (
    plot_gap_vs_baseline,
    plot_per_model_boxplot,
    plot_per_task_histogram,
    plot_cumulative_gap,
    plot_soundness_summary,
)


def main() -> None:
    cfg = default_config()

    # Setup directories
    base = Path(__file__).parent
    results_dir = Path(cfg.results_dir)
    figures_dir = Path(cfg.figures_dir)
    outputs_dir = Path(cfg.outputs_dir)
    for d in [results_dir, figures_dir, outputs_dir]:
        d.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("H-E1: Contract-Strength Gap Existence Verification")
    print("=" * 60)

    # Step 1: Load ContractEval
    print("\n[Step 1] Loading ContractEval dataset...")
    tasks = load_contracteval(cfg.contracteval_jsonl)
    tasks_with_cvts = get_tasks_with_cvts(tasks)
    z3_tractable_ids = get_z3_tractable_ids(tasks)
    print(f"  Total tasks: {len(tasks)}")
    print(f"  Tasks with CVTs: {len(tasks_with_cvts)}")
    print(f"  Z3-tractable (proxy): {len(z3_tractable_ids)}")

    # Step 2: Oracle soundness pre-check
    print("\n[Step 2] Oracle soundness pre-check...")
    oracle_path = str(results_dir / "oracle_precheck.jsonl")
    valid_ids, quarantined_ids = run_soundness_precheck(
        tasks_with_cvts,
        results_path=oracle_path,
        timeout_per_task=10,  # reduced for PoC speed
    )
    print(f"  Valid tasks: {len(valid_ids)}")
    print(f"  Quarantined tasks: {len(quarantined_ids)}")

    # Filter to valid tasks only
    valid_tasks = {tid: tasks_with_cvts[tid] for tid in valid_ids if tid in tasks_with_cvts}
    print(f"  Tasks for PBT: {len(valid_tasks)}")

    # Step 3: Generate proxy samples (canonical_solution as LLM output)
    print("\n[Step 3] Generating proxy LLM samples (canonical solutions)...")
    model_samples = get_canonical_samples(valid_tasks, n=cfg.n_samples, seed=cfg.pbt_seed)
    save_samples(model_samples, cfg.samples_dir)
    passing_by_model = load_passing_samples(valid_tasks, model_samples)

    total_programs = sum(
        sum(len(codes) for codes in task_samples.values())
        for task_samples in passing_by_model.values()
    )
    print(f"  Total programs: {total_programs} ({len(MODELS)} models × {len(valid_tasks)} tasks × {cfg.n_samples} samples)")

    # Step 4: Contract checking
    print("\n[Step 4] Running contract checking...")
    all_results = []
    for model in MODELS:
        if model not in passing_by_model:
            continue
        model_passing = passing_by_model[model]
        safe_model = model.replace("/", "__")
        results_path = str(results_dir / f"pbt_results_{safe_model}.jsonl")
        model_results = run_contract_checking(
            tasks=valid_tasks,
            passing_samples=model_passing,
            model=model,
            results_path=results_path,
            timeout=cfg.pbt_timeout,
        )
        all_results.extend(model_results)
        print(f"  {model}: {len(model_results)} results")

    # Step 5: Aggregate metrics
    print("\n[Step 5] Computing metrics...")
    metrics = aggregate_metrics(
        all_results=all_results,
        z3_tractable_ids=z3_tractable_ids,
        n_bootstrap=cfg.n_bootstrap,
        gate_threshold=cfg.gate_threshold,
    )
    metrics["n_quarantined"] = len(quarantined_ids)

    print(f"\n{'='*60}")
    print("RESULTS:")
    print(f"  Mean contract-strength gap: {metrics['mean_gap']:.4f}")
    print(f"  95% CI: [{metrics['ci_lower']:.4f}, {metrics['ci_upper']:.4f}]")
    print(f"  Tasks evaluated: {metrics['n_tasks']}")
    print(f"  Programs checked: {metrics['n_programs']}")
    print(f"  Gate (CI_lower > 0.01): {'PASS' if metrics['gate_passed'] else 'FAIL'}")
    if metrics.get("tractable_gap") is not None:
        print(f"  Z3-tractable subset gap: {metrics['tractable_gap']:.4f}")
    print(f"{'='*60}")

    # Step 6: Save results
    per_task_gap = compute_per_task_gap(all_results)

    summary = {
        "hypothesis_id": "h-e1",
        "mean_contract_strength_gap": metrics["mean_gap"],
        "ci_lower": metrics["ci_lower"],
        "ci_upper": metrics["ci_upper"],
        "n_tasks": metrics["n_tasks"],
        "n_programs": metrics["n_programs"],
        "gate_passed": metrics["gate_passed"],
        "gate_threshold": cfg.gate_threshold,
        "tractable_gap": metrics.get("tractable_gap"),
        "n_quarantined": metrics["n_quarantined"],
        "n_valid_tasks": len(valid_ids),
        "n_total_tasks": len(tasks),
        "per_task_gap_sample": dict(list(per_task_gap.items())[:10]),
    }

    summary_path = results_dir / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved: {summary_path}")

    # Save CSV
    csv_path = str(outputs_dir / "results.csv")
    save_results_csv(all_results, csv_path)
    print(f"Saved: {csv_path}")

    # Save experiment_results.json (for Phase 4 pipeline)
    experiment_results = {
        "status": "completed",
        "hypothesis_id": "h-e1",
        "metrics": {
            "mean_contract_strength_gap": metrics["mean_gap"],
            "ci_lower": metrics["ci_lower"],
            "ci_upper": metrics["ci_upper"],
            "gate_passed": metrics["gate_passed"],
            "gate_threshold": cfg.gate_threshold,
            "n_tasks": metrics["n_tasks"],
            "n_programs": metrics["n_programs"],
            "n_quarantined": metrics["n_quarantined"],
            "tractable_gap": metrics.get("tractable_gap"),
        },
        "gate_result": "PASS" if metrics["gate_passed"] else "FAIL",
        "execution_mode": "auto",
        "experiment_log": str(base.parent / "code/experiment.log"),
        "summary_path": str(summary_path),
    }
    exp_results_path = base.parent / "experiment_results.json"
    with open(exp_results_path, "w") as f:
        json.dump(experiment_results, f, indent=2)
    print(f"Saved: {exp_results_path}")

    # Step 7: Figures
    print("\n[Step 7] Generating figures...")
    plot_gap_vs_baseline(
        metrics["mean_gap"],
        metrics["ci_lower"],
        metrics["ci_upper"],
        out_path=str(figures_dir / "gap_vs_baseline.png"),
    )
    plot_per_model_boxplot(all_results, out_path=str(figures_dir / "per_model_gap.png"))
    plot_per_task_histogram(per_task_gap, out_path=str(figures_dir / "per_task_histogram.png"))
    plot_cumulative_gap(per_task_gap, out_path=str(figures_dir / "cumulative_gap.png"))
    plot_soundness_summary(valid_ids, quarantined_ids, out_path=str(figures_dir / "soundness_summary.png"))
    print(f"  5 figures saved to {figures_dir}")

    print("\n✅ H-E1 experiment complete.")
    print(f"Gate result: {'PASS' if metrics['gate_passed'] else 'FAIL'}")

    return experiment_results


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result.get("gate_result") == "PASS" else 1)
