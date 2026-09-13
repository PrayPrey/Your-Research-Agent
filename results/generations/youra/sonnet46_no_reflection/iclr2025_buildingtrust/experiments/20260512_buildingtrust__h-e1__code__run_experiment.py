"""
run_experiment.py — H-E1 Experiment Entry Point.

Orchestrates the full pipeline:
  1. assemble_matrix()               -> df [N, 11]
  2. compute_residual_instability()  -> df [N, 13], stats
  3. run_evaluation()                -> gate dict
  4. generate_figures()              -> figure paths

Exit codes: 0 = gate PASS, 1 = gate FAIL, 2 = runtime error
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="H-E1: Residual Instability Existence & Construct Validity"
    )
    parser.add_argument(
        "--trustllm-data-dir", default="data/trustllm",
        help="Path to TrustLLM data directory (default: data/trustllm)"
    )
    parser.add_argument(
        "--lmeval-results-dir", default="data/lmeval",
        help="Path to lm-eval JSON results directory (default: data/lmeval)"
    )
    parser.add_argument(
        "--output-dir", default="outputs",
        help="Path to output directory for CSV/YAML/JSON (default: outputs)"
    )
    parser.add_argument(
        "--figures-dir", default="../figures",
        help="Path to figures output directory (default: ../figures)"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Ensure working directory is the code folder
    code_dir = Path(__file__).parent
    os.chdir(code_dir)

    print("=" * 60)
    print("H-E1: Residual Instability — Existence & Construct Validity")
    print("=" * 60)

    try:
        # Step 1: Assemble model × benchmark matrix
        print("\n[1/4] Assembling model × benchmark matrix...")
        from data_assembly import assemble_matrix
        df = assemble_matrix(
            trustllm_data_dir=args.trustllm_data_dir,
            lmeval_results_dir=args.lmeval_results_dir,
        )
        print(f"  Matrix shape: {df.shape}")

        # Step 2: Compute PC1 + Residual Instability
        print("\n[2/4] Computing Residual Instability (PCA + OLS)...")
        from compute_ri import compute_residual_instability
        df, stats = compute_residual_instability(df)

        # Step 3: Evaluate gate conditions + bootstrap CIs
        print("\n[3/4] Evaluating gate conditions...")
        from evaluate import run_evaluation
        gate = run_evaluation(df, stats, output_dir=args.output_dir)

        # Step 4: Generate 5 required figures
        print("\n[4/4] Generating figures...")
        from visualize import generate_figures
        figure_paths = generate_figures(df, gate, figures_dir=args.figures_dir)

        # Save experiment_results.json for Phase 5
        results = {
            "hypothesis_id": "h-e1",
            "gate": gate,
            "stats": {k: (bool(v) if isinstance(v, bool) else
                          float(v) if isinstance(v, float) else v)
                      for k, v in stats.items()},
            "figures": figure_paths,
            "n_models": int(len(df)),
            "model_families": df["model_family"].value_counts().to_dict(),
        }
        results_path = Path(args.output_dir) / "experiment_results.json"
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)

        print("\n" + "=" * 60)
        print("EXPERIMENT COMPLETE")
        print("=" * 60)
        print(f"Gate result: {'✓ PASS' if gate['gate_passed'] else '✗ FAIL'}")
        print(f"  SD(AdvGLUE_drop) = {gate['sd_advglue_drop']:.4f} "
              f"(threshold > {gate.get('sd_threshold', 0.05):.2f}): "
              f"{'PASS' if gate['gate_sd_passed'] else 'FAIL'}")
        print(f"  R²_residualization = {gate['r2_residualization']:.4f} "
              f"(threshold < {gate.get('r2_threshold', 0.80):.2f}): "
              f"{'PASS' if gate['gate_r2_passed'] else 'FAIL'}")
        print(f"  Models: N={gate['n_models']}, "
              f"Families={gate['n_families']}, "
              f"Scales={gate['n_scales']}, "
              f"Regimes={gate['n_regimes']}")
        print(f"\nOutputs written to: {args.output_dir}/")
        print(f"Figures written to: {args.figures_dir}/")
        print(f"Results JSON: {results_path}")

        sys.exit(0 if gate["gate_passed"] else 1)

    except Exception as e:
        print(f"\n[ERROR] Experiment failed: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
