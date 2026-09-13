"""run_experiment.py — Entry point for H-M1 RI→ECE mechanism verification."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="H-M1: RI→ECE partial correlation experiment")
    parser.add_argument("--data-dir", default="../h-e1/code/outputs", help="H-E1 outputs directory")
    parser.add_argument("--output-dir", default="results", help="Results output directory")
    parser.add_argument("--figures-dir", default="../figures", help="Figures output directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--no-compute-ece", action="store_true", help="Skip ECE computation, use mock")
    parser.add_argument("--lmeval-logits-dir", default=None, help="lm-eval logits directory")
    return parser.parse_args()


def export_results(
    gate_result: dict,
    corr_results: dict,
    secondary_results: dict,
    output_dir: Path,
    merged_df: pd.DataFrame,
    ece_df: pd.DataFrame,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    # gate_results.yaml
    full = corr_results["full"]
    family_df = corr_results["family_df"]
    family_dict = {}
    for _, row in family_df.iterrows():
        family_dict[row["family"]] = {
            "rho": float(row["rho"]),
            "p_val": float(row["p_value"]),
            "p_val_holm": float(row.get("p_value_holm", float("nan"))),
            "n": int(row["n"]),
        }
    gate_yaml = {
        "gate": gate_result["gate"],
        "rho": full["rho"],
        "p_val": full["p_value"],
        "ci95_lower": full["ci_low"],
        "ci95_upper": full["ci_high"],
        "n": full["n"],
        "consistent_positive_families": gate_result["n_consistent_positive"],
        "family_results": family_dict,
        "secondary": {
            "baseline_rho": secondary_results["baseline_corr"]["rho"],
            "baseline_p": secondary_results["baseline_corr"]["p_val"],
            "vif": secondary_results["vif"],
            "cooks_flagged_models": secondary_results["cooks"]["flagged_models"],
            "fisher_z_stat": secondary_results["fisher_z"]["z_stat"],
            "fisher_z_p": secondary_results["fisher_z"]["p_val"],
        },
    }
    with open(output_dir / "gate_results.yaml", "w") as f:
        yaml.dump(gate_yaml, f, default_flow_style=False, allow_unicode=True)

    # partial_corr_results.yaml
    pcorr_yaml = {
        "full": {
            "rho": full["rho"],
            "p_val": full["p_value"],
            "ci95_lower": full["ci_low"],
            "ci95_upper": full["ci_high"],
            "n": full["n"],
            "covariates": ["PC1", "mean_confidence"],
            "method": "spearman",
        },
        "family": family_dict,
        "holm_corrected_p_values": family_df["p_value_holm"].tolist() if "p_value_holm" in family_df.columns else [],
        "n_families_significant": int((family_df["p_value_holm"] < 0.05).sum()) if "p_value_holm" in family_df.columns else 0,
    }
    with open(output_dir / "partial_corr_results.yaml", "w") as f:
        yaml.dump(pcorr_yaml, f, default_flow_style=False, allow_unicode=True)

    # ece_scores.csv
    ece_df.to_csv(output_dir / "ece_scores.csv", index=False)

    # model_matrix_m1.csv
    merged_df.to_csv(output_dir / "model_matrix_m1.csv", index=False)

    # experiment_results.json (pipeline summary)
    results_json = {
        "gate": gate_result["gate"],
        "rho_full": full["rho"],
        "p_value_full": full["p_value"],
        "ci95": [full["ci_low"], full["ci_high"]],
        "n": full["n"],
        "n_consistent_positive_families": gate_result["n_consistent_positive"],
        "conditions_met": gate_result["conditions_met"],
        "baseline_rho_pc1_ece": secondary_results["baseline_corr"]["rho"],
    }
    with open(output_dir / "experiment_results.json", "w") as f:
        json.dump(results_json, f, indent=2)


def main() -> int:
    args = parse_args()

    import config
    from ece_computer import ECEComputer
    from data_loader import DataLoader
    from partial_corr import PartialCorrAnalyzer
    from evaluate import GateEvaluator
    from visualize import Visualizer

    output_dir = Path(args.output_dir)
    figures_dir = Path(args.figures_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("H-M1: RI → ECE Mechanism Verification")
    print("=" * 60)

    # Step 1: ECE computation
    print("\n[1/6] Computing ECE scores...")
    loader_base = DataLoader(h_e1_outputs_dir=args.data_dir)
    matrix_df = loader_base.load_model_matrix()
    model_ids = matrix_df["model_id"].tolist() if "model_id" in matrix_df.columns else matrix_df.index.tolist()

    ece_computer = ECEComputer(seed=args.seed, cache_dir=output_dir)
    logit_paths = {}
    if args.lmeval_logits_dir and not args.no_compute_ece:
        import glob
        logit_dir = Path(args.lmeval_logits_dir)
        for p in glob.glob(str(logit_dir / "*.json")):
            mid = Path(p).stem
            logit_paths[mid] = Path(p)

    # force_recompute=False: always prefer cached real ECE from results/ece_scores.csv
    ece_df = ece_computer.load_or_compute(
        model_ids=model_ids,
        model_logit_paths=logit_paths if logit_paths else None,
        force_recompute=False,
    )
    print(f"   ECE computed for {len(ece_df)} models")

    # Step 2: Load + merge data
    print("\n[2/6] Loading H-E1 data and merging ECE...")
    ece_series = ece_df.set_index("model_id")["ECE"]
    loader = DataLoader(h_e1_outputs_dir=args.data_dir)
    merged_df = loader.merge_with_ece(ece_series)
    loader.validate(merged_df)
    print(f"   Merged DataFrame shape: {merged_df.shape}")

    # Step 3: Partial correlation analysis
    print("\n[3/6] Running Spearman partial correlation analysis...")
    analyzer = PartialCorrAnalyzer(n_bootstrap=config.N_BOOTSTRAP, seed=args.seed)
    corr_results = analyzer.run_all(merged_df)
    full = corr_results["full"]
    print(f"   ρ(RI, ECE | PC1, mean_confidence) = {full['rho']:.4f} (p={full['p_value']:.4f})")
    print(f"   Bootstrap 95% CI: [{full['ci_low']:.4f}, {full['ci_high']:.4f}]")
    print(f"   Consistent positive families: {corr_results['n_consistent_positive']}")

    # Step 4: Gate evaluation
    print("\n[4/6] Evaluating gate...")
    evaluator = GateEvaluator()
    gate_result = evaluator.evaluate_gate(
        rho=full["rho"],
        p_value=full["p_value"],
        family_results=corr_results["family_df"],
    )
    secondary_results = evaluator.run_all_secondary(merged_df, corr_results["family_df"])
    print(f"   Gate result: {gate_result['gate']} (conditions met: {gate_result['conditions_met']}/3)")

    # Step 5: Visualize
    print("\n[5/6] Generating figures...")
    viz = Visualizer(figures_dir=str(figures_dir), dpi=config.FIGURE_DPI)
    try:
        fig_paths = viz.generate_all(merged_df, ece_df, corr_results, secondary_results)
        print(f"   Generated {len(fig_paths)} figures in {figures_dir}")
    except Exception as e:
        print(f"   WARNING: Figure generation error: {e}")
        fig_paths = []

    # Step 6: Export
    print("\n[6/6] Exporting results...")
    export_results(gate_result, corr_results, secondary_results, output_dir, merged_df, ece_df)
    print(f"   Results exported to {output_dir}")

    print("\n" + "=" * 60)
    print(f"EXPERIMENT COMPLETE — Gate: {gate_result['gate']}")
    print(f"  ρ = {full['rho']:.4f}, p = {full['p_value']:.4f}")
    print(f"  Threshold: ρ ≥ {config.RHO_THRESHOLD}, p < {config.P_THRESHOLD}")
    print("=" * 60)

    return 0 if gate_result["gate"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
