"""H-E1: FAIL FAST Gate Validation Pipeline.

Validates data pipeline for YouRA diversity research.
Gates G0-G4 must all pass; failure at any gate halts pipeline.
"""

import json
import os
import sys
from pathlib import Path

from config import CFG
from gates import GateValidator, VIFChecker
from output import OutputWriter, Visualizer
from pipeline import DataLoader, DiversityAggregator, FuzzyJoiner, PanelBuilder


def main() -> None:
    # Resolve paths relative to code/ directory
    code_dir = Path(__file__).parent
    hyp_dir = code_dir.parent
    panel_path = code_dir / CFG.panel_path
    output_path = hyp_dir / CFG.output_csv
    figures_dir = hyp_dir / CFG.figures_dir
    results_path = hyp_dir / "experiment_results.json"
    outputs_dir = code_dir / "outputs"
    outputs_dir.mkdir(exist_ok=True)
    results_csv = outputs_dir / "results.csv"

    print("=" * 60)
    print("H-E1: FAIL FAST Gate Validation Pipeline")
    print("=" * 60)

    # --- Step 1: Load h-e2 panel ---
    panel_builder = PanelBuilder()
    panel = panel_builder.load_or_build(str(panel_path))

    # --- Step 2: Load pwc-archive/evaluation-tables ---
    loader = DataLoader()
    eval_df = loader.load()

    # --- Step 3: Fuzzy join ---
    joiner = FuzzyJoiner()
    joined = joiner.join(eval_df, panel)
    n_matched = joiner.coverage_count(joined)
    print(f"Benchmarks with >=1 paper_url: {n_matched}/{CFG.n_benchmarks}")

    # --- Step 4: Diversity aggregation ---
    agg = DiversityAggregator()
    filtered = agg.filter_temporal(joined, panel)
    stats_df = agg.aggregate(filtered)
    stats_df = agg.z_standardize(stats_df)

    # --- Step 5: Merge for enriched panel ---
    writer = OutputWriter()
    enriched_panel = panel.merge(
        stats_df[["task_path", "log_unique_paper_count_at_intro_z",
                  "paper_diversity_ratio_at_intro_z",
                  "paper_diversity_ratio_at_intro",
                  "log_unique_paper_count_at_intro"]],
        on="task_path", how="left",
    )

    # --- Step 6: Run all gates (FAIL FAST) ---
    validator = GateValidator()
    gate_results = validator.run_all(stats_df, panel, n_matched, enriched_panel)

    # --- Step 7: Collinearity failsafe ---
    checker = VIFChecker()
    pearson_r = checker.collinearity_failsafe(stats_df)

    # --- Step 8: Save output artifact ---
    enriched_panel = writer.merge_and_save(panel, stats_df, str(output_path))

    # --- Step 9: Generate figures ---
    viz = Visualizer(str(figures_dir))
    viz.save_all(joined, stats_df, gate_results, enriched_panel, panel)

    # --- Step 10: Save results.csv ---
    results_rows = []
    for r in gate_results:
        results_rows.append({
            "gate": r.gate,
            "passed": r.passed,
            "value": r.value,
            "threshold": r.threshold,
            "message": r.message,
        })
    import pandas as pd
    results_df = pd.DataFrame(results_rows)
    results_df.to_csv(str(results_csv), index=False)
    print(f"Results CSV: {results_csv}")

    # --- Step 11: Save experiment_results.json ---
    gate_dict = {r.gate: {"passed": bool(r.passed), "value": float(r.value), "threshold": float(r.threshold)}
                 for r in gate_results}
    experiment_results = {
        "hypothesis_id": "h-e1",
        "gate_result": "PASS",
        "gates": gate_dict,
        "n_matched": n_matched,
        "n_benchmarks": CFG.n_benchmarks,
        "coverage": n_matched / CFG.n_benchmarks,
        "collinearity_pearson_r": float(pearson_r),
        "n_stats_benchmarks": len(stats_df),
        "output_csv": str(output_path),
    }
    with open(str(results_path), "w") as f:
        json.dump(experiment_results, f, indent=2)
    print(f"Experiment results: {results_path}")

    print("\n" + "=" * 60)
    print("ALL GATES PASSED — H-E1 PIPELINE VALIDATED")
    print("=" * 60)
    for r in gate_results:
        status = "PASS" if r.passed else "FAIL"
        print(f"  [{status}] {r.message}")
    print(f"\n  Collinearity r={pearson_r:.3f}")
    print(f"  Output: {output_path}")
    print(f"  Figures: {figures_dir}")


if __name__ == "__main__":
    main()
