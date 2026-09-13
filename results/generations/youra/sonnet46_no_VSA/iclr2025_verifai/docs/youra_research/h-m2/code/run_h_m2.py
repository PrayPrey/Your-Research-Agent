#!/usr/bin/env python3
"""Orchestrator for h-m2: contract richness stratification analysis."""
import json
import sys
from pathlib import Path

import pandas as pd

# Add code dir to path so sibling imports work
sys.path.insert(0, str(Path(__file__).parent))

from analyze_correlation import run_full_analysis
from score_richness import (
    FIGURES_DIR,
    H1_RESULTS_JSON,
    RESULTS_DIR,
    build_richness_df,
    load_contracteval_tasks,
    load_cu_dict,
    load_gap_dict,
    load_gap_dict_by_model,
    load_task_types,
    verify_mechanism_activated,
)
from visualize import save_all


def load_h1_results(json_path: Path = H1_RESULTS_JSON) -> dict:
    with open(json_path) as f:
        return json.load(f)


def save_results(results: dict, richness_df: pd.DataFrame, results_dir: Path) -> None:
    results_dir.mkdir(parents=True, exist_ok=True)
    with open(results_dir / "h_m2_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    richness_df.to_csv(results_dir / "richness_scores.csv", index=False)
    print(f"Results saved to {results_dir}")


def main() -> None:
    print("=" * 60)
    print("h-m2: Contract Richness Stratification Analysis")
    print("=" * 60)

    # 1. Load gap dict — fail early if missing
    print("\n[1/8] Loading H-M1 oracle isolation gaps...")
    gap_dict = load_gap_dict()
    print(f"  Loaded gaps for {len(gap_dict)} tasks")

    # 2. Load per-model gaps for ablation 2
    print("\n[2/8] Loading per-model gaps...")
    gap_dict_by_model = load_gap_dict_by_model()
    print(f"  Models: {list(gap_dict_by_model.keys())}")

    # 3. Load task types for ablation 3
    print("\n[3/8] Loading task types...")
    task_type_dict = load_task_types()

    # 4. Load CU mass for violin plot
    print("\n[4/8] Loading contract-unique mass...")
    cu_dict = load_cu_dict()

    # 5. Load ContractEval tasks
    print("\n[5/8] Loading ContractEval tasks...")
    contracteval_tasks = load_contracteval_tasks()

    # 6. Build richness dataframe
    print("\n[6/8] Building richness scores (AST analysis)...")
    richness_df = build_richness_df(contracteval_tasks)
    print(f"  Shape: {richness_df.shape}")
    tier_counts = richness_df["tier"].value_counts().sort_index()
    print(f"  Tier distribution:\n{tier_counts.to_string()}")

    # 7. Load h-m1 aggregated results
    print("\n[7/8] Loading H-M1 aggregated results...")
    h1_results = load_h1_results()

    # 8. Run full analysis
    print("\n[8/8] Running statistical analysis...")
    results = run_full_analysis(richness_df, gap_dict, h1_results, gap_dict_by_model, task_type_dict)

    print(f"\n  Spearman ρ = {results['rho']:.4f}")
    print(f"  p (asymptotic) = {results['p_asymptotic']:.4e}")
    print(f"  p (exact permutation) = {results['p_exact']:.4e}")
    print(f"  95% CI: [{results['ci_lower']:.4f}, {results['ci_upper']:.4f}]")
    print(f"  Kruskal-Wallis: H={results['kw_stat']:.2f}, p={results['kw_p']:.4e}")
    print(f"  Tier means: {results['tier_means']}")
    print(f"  FLAT_GRADIENT: {results['FLAT_GRADIENT']}")

    # Mechanism verification
    mech_passed, indicators = verify_mechanism_activated(richness_df, gap_dict, results)
    results["mechanism_indicators"] = indicators
    print(f"\n  Mechanism activated: {mech_passed}")
    for k, v in indicators.items():
        print(f"    {k}: {v}")

    # Figures
    print("\n[Figures] Generating visualizations...")
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    save_all(richness_df, gap_dict, gap_dict_by_model, cu_dict, results, FIGURES_DIR)

    # Save results
    save_results(results, richness_df, RESULTS_DIR)

    # Gate verdict
    print("\n" + "=" * 60)
    gate_type = "SHOULD_WORK"
    rho = results["rho"]
    p_exact = results["p_exact"]

    if results["FLAT_GRADIENT"]:
        verdict = "FLAT_GRADIENT"
        print(f"⚠  GATE RESULT: FLAT_GRADIENT — rho={rho:.3f} < 0.15 threshold")
    elif rho >= 0.30 and p_exact < 0.05:
        verdict = "PASS"
        print(f"✓  GATE RESULT: PASS — rho={rho:.3f} ≥ 0.30, p={p_exact:.4e} < 0.05")
    else:
        verdict = "FAIL"
        print(f"✗  GATE RESULT: FAIL — rho={rho:.3f} (need ≥0.30), p={p_exact:.4e} (need <0.05)")

    results["gate_result"] = verdict
    results["gate_type"] = gate_type

    # Overwrite with gate result
    save_results(results, richness_df, RESULTS_DIR)
    print("=" * 60)


if __name__ == "__main__":
    main()
