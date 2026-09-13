"""H-M4: Main experiment orchestrator."""
import json
import sys
from dataclasses import asdict
from pathlib import Path

from config import RESULTS_DIR, FIGURES_DIR, EXP_B_CSV
from data_loader import load_exp_b_rates, load_pass_at_1, load_task_metadata, build_df_long
from analysis import run_analysis, verify_mechanism_activated, H_M4_Results
from visualization import save_all_figures


def save_results(results: H_M4_Results, results_dir: Path = None) -> None:
    """Write h_m4_results.json + analysis_summary.txt."""
    rdir = results_dir or RESULTS_DIR
    rdir.mkdir(parents=True, exist_ok=True)

    # JSON — convert dataclass to dict, handle non-serializable types
    def make_serializable(obj):
        if isinstance(obj, float) and (obj != obj):  # NaN
            return None
        return obj

    data = asdict(results)
    # Clean NaN values
    def clean(d):
        if isinstance(d, dict):
            return {k: clean(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [clean(v) for v in d]
        elif isinstance(d, float) and (d != d):
            return None
        return d
    data = clean(data)

    json_path = rdir / "h_m4_results.json"
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Results saved: {json_path}")

    # Summary text
    gate_str = "PASS" if results.gate_pass else ("PARTIAL" if results.gate_partial else "FAIL")
    summary = f"""H-M4: Cross-Model Contract-Satisfaction Analysis
================================================
Gate Result: {gate_str}

Primary Metrics:
  Kendall τ = {results.tau:.4f} (threshold ≤ 0.60, p = {results.tau_pvalue:.4f})
  Partial ΔR² = {results.delta_R2:.4f} (threshold ≥ 0.10)
  Cross-Model Gap = {results.cross_model_gap:.4f} [{results.gap_ci_low:.4f}, {results.gap_ci_high:.4f}] (threshold ≥ 0.10)

Secondary Metrics:
  Spearman ρ = {results.spearman_rho:.4f} (p = {results.spearman_pvalue:.4f})
  Model Family p-value = {results.model_family_pvalue:.4f}
  MixedLM converged: {results.converged} | OLS fallback: {results.fallback_ols}
  R²_full = {results.R2_full:.4f}, R²_reduced = {results.R2_reduced:.4f}

Model Rankings:
  By contract rate: {results.model_ranking_by_contract}
  By pass@1*: {results.model_ranking_by_pass}
  Best (contract): {results.best_model}
  Worst (contract): {results.worst_model}

Subgroup Analysis:
  HumanEval+ τ = {results.tau_humaneval:.4f}
  MBPP+ τ = {results.tau_mbpp:.4f}
  HumanEval+ ΔR² = {results.delta_R2_humaneval:.4f}
  MBPP+ ΔR² = {results.delta_R2_mbpp:.4f}

Data:
  n_model_task_pairs = {results.n_model_task_pairs}
"""
    txt_path = rdir / "analysis_summary.txt"
    with open(txt_path, "w") as f:
        f.write(summary)
    print(f"Summary saved: {txt_path}")
    print(summary)


def main() -> None:
    print("=" * 60)
    print("H-M4: Cross-Model Contract-Satisfaction Statistical Analysis")
    print("=" * 60)

    # 1. Load H-M3 Experiment B results
    exp_b_df = load_exp_b_rates(EXP_B_CSV)

    # 2. Load EvalPlus pass@1* scores
    pass_at_1 = load_pass_at_1(use_evalplus_pkg=False)

    # 3. Load task metadata (ContractEval)
    task_meta = load_task_metadata()

    # 4. Build merged long-format DataFrame
    df_long = build_df_long(exp_b_df, pass_at_1, task_meta)

    # 5. Run analysis
    results = run_analysis(exp_b_df, df_long, pass_at_1)

    # 6. Verify mechanism activated
    activated, indicators = verify_mechanism_activated(results)
    if not activated:
        print(f"WARNING: Mechanism not fully activated: {indicators}")

    # 7. Save results
    save_results(results, RESULTS_DIR)

    # 8. Generate figures
    save_all_figures(results, exp_b_df, df_long, pass_at_1, FIGURES_DIR)

    # 9. Save structured JSON for Phase 4 reporting
    outputs_dir = Path(__file__).parent / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    results_csv_path = outputs_dir / "results.csv"

    import pandas as pd
    model_rates = exp_b_df.groupby("model_id")["contract_satisfaction_rate"].mean().reset_index()
    model_rates["pass_at_1"] = model_rates["model_id"].map(pass_at_1)
    model_rates["tau"] = results.tau
    model_rates["delta_R2"] = results.delta_R2
    model_rates["cross_model_gap"] = results.cross_model_gap
    model_rates.to_csv(results_csv_path, index=False)
    print(f"Results CSV: {results_csv_path}")

    gate_str = "PASS" if results.gate_pass else ("PARTIAL" if results.gate_partial else "FAIL")
    print(f"\n{'='*60}")
    print(f"EXPERIMENT COMPLETE — Gate: {gate_str}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
