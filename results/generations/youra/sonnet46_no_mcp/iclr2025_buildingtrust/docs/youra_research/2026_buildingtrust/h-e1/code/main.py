from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

CODE_DIR = Path(__file__).parent
sys.path.insert(0, str(CODE_DIR))

from config import (
    FIGURES_DIR,
    GATE_PAIRS,
    GATE_THRESHOLD,
    INDICATORS,
    MODELS,
    RESULTS_DIR,
)


def main() -> None:
    results_dir = Path(RESULTS_DIR)
    figures_dir = Path(FIGURES_DIR)
    results_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    # Stage 1: Run lm-evaluation-harness on all 30 models
    logger.info("=== Stage 1: Running lm-evaluation-harness ===")
    import run_eval
    success_map = run_eval.run_all_models(MODELS, results_dir)
    logger.info(f"Stage 1 complete: {sum(success_map.values())}/{len(MODELS)} models succeeded")

    # Stage 2: Extract ECE + Brier calibration metrics
    logger.info("=== Stage 2: Extracting calibration metrics ===")
    import calibration
    calibration_data: dict[str, dict] = {}
    for model in MODELS:
        mid = model["id"]
        if not success_map.get(mid, False):
            logger.warning(f"Skipping calibration for failed model: {mid}")
            continue
        try:
            calib = calibration.extract_calibration_for_model(mid, results_dir)
            calibration_data[mid] = calib
            logger.info(f"  {mid}: ECE_greedy={calib['ece_greedy']:.4f}, Brier_greedy={calib['brier_greedy']:.4f}")
        except Exception as e:
            logger.error(f"  {mid} calibration failed: {e}")

    # Stage 3: Assemble score matrix
    logger.info("=== Stage 3: Assembling score matrix ===")
    import score_matrix as sm

    # attach family info to models for scatter plot
    model_family_map = {m["id"]: m["family"] for m in MODELS}

    df = sm.build_score_matrix(MODELS, results_dir, calibration_data)
    df["family"] = df["model_id"].map(model_family_map)

    if not sm.validate_matrix(df):
        logger.error(f"Score matrix validation failed: {len(df)} rows, NaN check failed")
        sys.exit("ABORT: Score matrix validation failed — insufficient valid models or NaN in gate columns")
    logger.info(f"Score matrix valid: {len(df)} models")

    # Stage 4: Statistical analysis
    logger.info("=== Stage 4: Statistical analysis ===")
    import analysis

    # Greedy partial correlations (primary)
    logger.info("  Computing partial Spearman correlation matrix (greedy)...")
    corr_greedy = analysis.compute_partial_corr_matrix(df, INDICATORS)
    logger.info(f"  Computed {len(corr_greedy)} pairs")

    # Stochastic score matrix for factor stability comparison
    df_stoch = df.copy()
    for model in MODELS:
        mid = model["id"]
        calib = calibration_data.get(mid, {})
        if mid in df_stoch["model_id"].values:
            idx = df_stoch[df_stoch["model_id"] == mid].index
            df_stoch.loc[idx, "ECE"] = calib.get("ece_stochastic", df_stoch.loc[idx, "ECE"])
            df_stoch.loc[idx, "Brier"] = calib.get("brier_stochastic", df_stoch.loc[idx, "Brier"])
    df_stoch = df_stoch.dropna(subset=["ECE", "Brier"])

    logger.info("  Computing partial Spearman correlation matrix (stochastic)...")
    corr_stochastic = analysis.compute_partial_corr_matrix(df_stoch, INDICATORS)

    # Factor analysis — greedy
    logger.info("  Running factor analysis (greedy)...")
    fa_g, loadings_g, var_g, kmo_g = analysis.run_factor_analysis(df.dropna(subset=INDICATORS))
    logger.info(f"  Greedy FA: var_explained={var_g:.3f}, KMO={kmo_g:.3f}")

    # Factor analysis — stochastic
    logger.info("  Running factor analysis (stochastic)...")
    fa_s, loadings_s, var_s, kmo_s = analysis.run_factor_analysis(df_stoch.dropna(subset=INDICATORS))
    logger.info(f"  Stochastic FA: var_explained={var_s:.3f}, KMO={kmo_s:.3f}")

    # Sign-align loadings before Tucker congruence
    import numpy as np
    if loadings_g[np.argmax(np.abs(loadings_g))] < 0:
        loadings_g = -loadings_g
    if loadings_s[np.argmax(np.abs(loadings_s))] < 0:
        loadings_s = -loadings_s

    congruence = analysis.compute_tucker_congruence(loadings_g, loadings_s)
    logger.info(f"  Tucker congruence: {congruence:.3f} (threshold >= 0.85)")

    # LOO logistic regression
    logger.info("  Running LOO logistic regression...")
    loo_features = ["ECE", "TruthfulQA_pct", "Brier"]
    loo_results = analysis.run_loo_logistic(df.dropna(subset=loo_features + ["AdvGLUE_drop", "MMLU_acc"]),
                                             loo_features)
    logger.info(f"  LOO AUC: {loo_results['auc']:.3f} (MMLU-only: {loo_results['auc_mmlu_only']:.3f})")

    # Gate evaluation
    gate_eval = analysis.evaluate_gates(corr_greedy, GATE_PAIRS, GATE_THRESHOLD)
    logger.info(f"  Gate result: {'PASS' if gate_eval['PASS'] else 'FAIL'}")
    for r in gate_eval["results"]:
        logger.info(f"    {r['pair']}: rho={r['rho']:.3f}, CI={r['ci']}, passes={r['passes']}")

    factor_results = {
        "loadings": loadings_g.tolist(),
        "variance_explained": var_g,
        "kmo": kmo_g,
        "congruence": congruence,
        "loadings_stochastic": loadings_s.tolist(),
    }

    # Stage 5a: Visualization
    logger.info("=== Stage 5a: Generating figures ===")
    import visualize

    visualize.plot_gate_bar(corr_greedy, GATE_PAIRS, GATE_THRESHOLD, figures_dir)
    visualize.plot_corr_heatmap(corr_greedy, figures_dir)
    visualize.plot_factor_loadings(fa_g, INDICATORS, figures_dir)
    visualize.plot_tucker_congruence(loadings_g, loadings_s, congruence, INDICATORS, figures_dir)
    visualize.plot_family_scatter(df, figures_dir)
    visualize.plot_decoding_invariance(corr_greedy, corr_stochastic, figures_dir)
    logger.info(f"  Figures saved to {figures_dir}")

    # Stage 5b: Write results
    logger.info("=== Stage 5b: Writing results ===")
    import report

    hypothesis_dir = Path(RESULTS_DIR).parent
    results_json_path = hypothesis_dir / "04_results.json"
    validation_md_path = hypothesis_dir / "04_validation.md"

    report.write_results_json(df, corr_greedy, factor_results, gate_eval, results_json_path)
    report.write_validation_md(gate_eval, corr_greedy, factor_results, loo_results, validation_md_path)
    logger.info(f"  Results written: {results_json_path}, {validation_md_path}")

    logger.info("=== Pipeline complete ===")
    gate_str = "PASS" if gate_eval["PASS"] else "FAIL"
    logger.info(f"MUST_WORK gate: {gate_str}")
    return gate_eval


if __name__ == "__main__":
    main()
