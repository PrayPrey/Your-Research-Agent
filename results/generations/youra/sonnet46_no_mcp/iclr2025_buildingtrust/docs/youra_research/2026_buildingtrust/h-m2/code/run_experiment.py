from __future__ import annotations
import sys
import os
from pathlib import Path

# Ensure code dir is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import data_loader
import analyzers
import visualizer
import reporter


def main() -> dict:
    """Orchestrate H-M2 experiment: load → partial_rho → LOO-AUC → delta → gate → viz → report."""
    print("=" * 60)
    print("H-M2: Epistemic Composite Predictive Validity")
    print("=" * 60)

    # 1. Load data
    print("\n[1/7] Loading score matrix...")
    df = data_loader.load_score_matrix(config.SCORE_MATRIX_PATH)
    data_loader.validate_schema(df, config.REQUIRED_COLS, config.GATE_COLS if hasattr(config, 'GATE_COLS') else
                                ["ECE", "Brier", "TruthfulQA_pct", "AdvGLUE_drop", "MMLU_acc"])
    df = data_loader.add_top_quartile_label(df, "AdvGLUE_drop", config.TOP_QUARTILE)
    q75 = df["AdvGLUE_drop"].quantile(config.TOP_QUARTILE)
    print(f"  Loaded {len(df)} models. Top-quartile threshold (AdvGLUE_drop): {q75:.4f}")
    print(f"  Positive labels: {df[config.TARGET_COL].sum()} / {len(df)}")

    # 2. Partial rho analysis
    print("\n[2/7] Computing partial Spearman rho (BCa bootstrap)...")
    partial_result = analyzers.compute_partial_rho_advglue(
        df, n_boot=config.N_BOOTSTRAP, seed=config.BOOTSTRAP_SEED
    )
    print(f"  partial ρ(ECE, AdvGLUE|MMLU) = {partial_result['rho_partial_advglue']:.4f}")
    print(f"  BCa 95% CI: [{partial_result['bca_ci_low']:.4f}, {partial_result['bca_ci_high']:.4f}]")
    print(f"  CI excludes zero: {partial_result['ci_excludes_zero']}")
    print(f"  Passes threshold (|ρ|≥0.40): {partial_result['passes_threshold']}")
    print(f"  partial ρ(ECE, ANLI|MMLU)    = {partial_result['rho_partial_anli']:.4f}")

    # 3. LOO-AUC for composite predictor
    print("\n[3/7] Computing LOO-AUC for composite predictor...")
    composite_auc = analyzers.compute_loo_auc(
        df, config.COMPOSITE_COLS, config.TARGET_COL, config.BOOTSTRAP_SEED
    )
    print(f"  Composite LOO-AUC = {composite_auc['auc']:.4f}")

    # 4. LOO-AUC for MMLU-only baseline
    print("\n[4/7] Computing LOO-AUC for MMLU-only baseline...")
    baseline_auc = analyzers.compute_loo_auc(
        df, config.BASELINE_COLS, config.TARGET_COL, config.BOOTSTRAP_SEED
    )
    print(f"  Baseline LOO-AUC  = {baseline_auc['auc']:.4f}")

    # 5. Delta AUC bootstrap
    print(f"\n[5/7] Computing delta AUC bootstrap (n={config.N_BOOTSTRAP})...")
    delta_result = analyzers.compute_delta_auc_bootstrap(
        df,
        composite_cols=config.COMPOSITE_COLS,
        baseline_cols=config.BASELINE_COLS,
        target_col=config.TARGET_COL,
        n_boot=config.N_BOOTSTRAP,
        seed=config.BOOTSTRAP_SEED,
    )
    print(f"  ΔAUC = {delta_result['delta_auc']:.4f}  (95% CI [{delta_result['delta_auc_ci'][0]:.4f}, {delta_result['delta_auc_ci'][1]:.4f}])")
    print(f"  CI excludes zero: {delta_result['ci_excludes_zero']}")
    print(f"  Passes AUC threshold (≥0.70): {delta_result['passes_auc_threshold']}")
    print(f"  Passes delta threshold (≥0.10 & CI>0): {delta_result['passes_delta_threshold']}")

    # 6. Gate evaluation
    gate_pass = analyzers.evaluate_gate(composite_auc, delta_result)
    print(f"\n[6/7] Gate evaluation: {'PASS ✅' if gate_pass else 'FAIL/PARTIAL ❌'}")

    # 7. Generate figures
    print("\n[7/7] Generating figures...")
    fig_dir = Path(config.FIGURES_DIR)
    visualizer.plot_auc_comparison_bar(delta_result, config.AUC_THRESHOLD, fig_dir)
    visualizer.plot_roc_curves(composite_auc, baseline_auc, fig_dir)
    visualizer.plot_partial_rho_comparison(partial_result, -0.758, fig_dir)
    visualizer.plot_advglue_distribution(df, q75, fig_dir)
    visualizer.plot_feature_importance(df, config.COMPOSITE_COLS, config.TARGET_COL, config.BOOTSTRAP_SEED, fig_dir)
    visualizer.plot_composite_scatter(df, fig_dir)
    print(f"  6 figures saved to {fig_dir}")

    # 8. Write reports
    results_dir = Path(config.RESULTS_DIR)
    results_dir.mkdir(parents=True, exist_ok=True)
    reporter.write_results_json(
        partial_result, composite_auc, baseline_auc, delta_result, gate_pass,
        results_dir / "hm2_results.json"
    )
    validation_path = Path(config.FIGURES_DIR).parent / "04_validation.md"
    reporter.write_validation_md(
        partial_result, composite_auc, baseline_auc, delta_result, gate_pass,
        validation_path
    )
    print(f"  Results: {results_dir / 'hm2_results.json'}")
    print(f"  Validation: {validation_path}")

    print("\n" + "=" * 60)
    print(f"COMPLETE — Gate: {'PASS' if gate_pass else 'FAIL/PARTIAL'}")
    print("=" * 60)

    return {
        "PASS": gate_pass,
        "partial_result": partial_result,
        "composite_auc": composite_auc,
        "baseline_auc": baseline_auc,
        "delta_result": delta_result,
    }


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result["PASS"] else 1)
