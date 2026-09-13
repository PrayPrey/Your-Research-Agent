"""H-M2 pipeline orchestration: round-stratified coefficient comparison."""
import datetime
import json
import logging
import sys
from pathlib import Path

import numpy as np
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path setup (H-M1 verified pattern)
# ---------------------------------------------------------------------------

def setup_paths() -> Path:
    """Insert H-E1 code dir into sys.path. Returns project base dir."""
    code_dir = Path(__file__).parent
    hypothesis_dir = code_dir.parent
    bi_align_dir = hypothesis_dir.parent
    base_dir = bi_align_dir.parent.parent  # …/TEST_bi_align_3

    HE1_CODE_DIR = bi_align_dir / "h-e1" / "code"
    if HE1_CODE_DIR.exists() and str(HE1_CODE_DIR) not in sys.path:
        sys.path.insert(1, str(HE1_CODE_DIR))
        log.info("H-E1 code dir added to sys.path: %s", HE1_CODE_DIR)
    return base_dir


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_pipeline(subsample: int = None) -> dict:
    """Orchestrate full H-M2 experiment. Returns metrics dict."""
    from config import (
        BOOTSTRAP_ITERS, FIGURE_FILENAMES, FIGURES_DPI, LR_PARAMS,
        N_DIRECTIONAL_GATE, RANDOM_SEED, ROUND_SIZE_MIN, TEST_SIZE,
    )
    from coefficient_comparison import (
        check_topic_balance,
        check_cross_round_held_out,
        compare_coefficients,
        evaluate_gate,
        fit_auxiliary_round2_model,
        fit_round_predictor,
        prepare_round_splits,
        set_q_early_model,
    )
    from visualize import (
        plot_bootstrap_distributions,
        plot_coefficient_comparison,
        plot_cross_round_scatter,
        plot_feature_stability,
        plot_gate_metrics,
        plot_topic_balance,
    )
    from data_loader import load_hh_rlhf
    from q_early import QEarlyModel

    # ── Resolve output dirs ────────────────────────────────────────────────
    code_dir = Path(__file__).parent
    hypothesis_dir = code_dir.parent
    bi_align_dir = hypothesis_dir.parent
    figures_dir = hypothesis_dir / "figures"
    results_dir = hypothesis_dir / "results"
    figures_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir = code_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    # ── Stage 1: Load dataset ──────────────────────────────────────────────
    log.info("Stage: load_dataset — started")
    df = load_hh_rlhf()
    if subsample:
        df = df.iloc[:subsample].reset_index(drop=True)
        log.info("Subsampled to %d rows", len(df))
    log.info("HH-RLHF loaded: %d rows", len(df))

    n_total = len(df)
    round_size = n_total // 3
    log.info("Round size: %d (min required: %d)", round_size, ROUND_SIZE_MIN)

    # ── Stage 2: Topic balance check ──────────────────────────────────────
    log.info("Stage: topic_balance — started")
    early_df = df.iloc[0:round_size].reset_index(drop=True)
    late_df = df.iloc[2 * round_size:].reset_index(drop=True)
    topic_pvalue, chi2_residuals, topic_labels = check_topic_balance(early_df, late_df)

    # ── Stage 3: Fit Q_early model on round-1 data ────────────────────────
    log.info("Stage: fit_q_early — started")
    from features import build_feature_matrix
    X_r1, y_r1 = build_feature_matrix(early_df)
    q_model = QEarlyModel()
    q_model.fit(X_r1, y_r1)
    # calibrate on round-2 data
    mid_df = df.iloc[round_size: 2 * round_size].reset_index(drop=True)
    X_r2, y_r2 = build_feature_matrix(mid_df)
    q_model.calibrate(X_r2, y_r2)
    set_q_early_model(q_model)
    log.info("Q_early model fitted and calibrated")

    # ── Stage 4: Prepare round splits ────────────────────────────────────
    log.info("Stage: prepare_round_splits — started")
    early_split, late_split = prepare_round_splits(
        df, q_model, round_size, test_size=TEST_SIZE, random_state=RANDOM_SEED
    )
    log.info("Early split: train=%d test=%d", len(early_split.y_train), len(early_split.y_test))
    log.info("Late split:  train=%d test=%d", len(late_split.y_train), len(late_split.y_test))

    # Shared held-out test set (concatenation of early_test + late_test)
    X_test_shared = np.vstack([early_split.X_test, late_split.X_test])
    y_test_shared = np.concatenate([early_split.y_test, late_split.y_test])
    q_test_shared = np.concatenate([early_split.q_test, late_split.q_test])

    # ── Stage 5: Fit early-round predictor (creates shared_scaler) ────────
    log.info("Stage: fit_early_predictor — started")
    early_model = fit_round_predictor(early_split, shared_scaler=None)
    shared_scaler = early_model.scaler
    log.info("Early model AUC=%.4f, coefs=%s", early_model.auc, early_model.coefs)

    # ── Stage 6: Fit late-round predictor (use shared_scaler) ────────────
    log.info("Stage: fit_late_predictor — started")
    late_model = fit_round_predictor(late_split, shared_scaler=shared_scaler)
    log.info("Late model AUC=%.4f, coefs=%s", late_model.auc, late_model.coefs)

    # ── Stage 7: Bootstrap CI + coefficient comparison ────────────────────
    log.info("Stage: compare_coefficients — started (bootstrap_iters=%d)", BOOTSTRAP_ITERS)
    result = compare_coefficients(
        early_model, late_model, early_split, late_split,
        shared_scaler, topic_balance_pvalue=topic_pvalue,
        n_resamples=BOOTSTRAP_ITERS, random_state=RANDOM_SEED,
    )
    log.info("n_directional=%d/3, sign_consistent=%s, beta_q_stable=%s",
             result.n_directional, result.sign_consistent, result.beta_q_stable)

    # ── Stage 8: Auxiliary round-2 model for monotonicity check ──────────
    log.info("Stage: fit_auxiliary_round2 — started")
    try:
        mid_model = fit_auxiliary_round2_model(df, q_model, shared_scaler, round_size)
        log.info("Mid model AUC=%.4f, coefs=%s", mid_model.auc, mid_model.coefs)
    except Exception as e:
        log.warning("Auxiliary round-2 model failed: %s — using early model as proxy", e)
        mid_model = early_model

    # ── Stage 9: Cross-round held-out validation ──────────────────────────
    log.info("Stage: cross_round_held_out — started")
    held_out = check_cross_round_held_out(
        early_model, late_model, X_test_shared, y_test_shared, q_test_shared,
        shared_scaler, ambiguity_threshold=0.1,
    )
    log.info("Cross-round held-out: early_auc=%.4f late_auc=%.4f longer_pref=%.3f",
             held_out["early_auc"], held_out["late_auc"], held_out["longer_pref_rate"])

    # ── Stage 10: Gate evaluation ─────────────────────────────────────────
    log.info("Stage: evaluate_gate — started")
    gate = evaluate_gate(result)
    gate_status = gate["gate_status"]

    # ── Stage 11: Generate figures ────────────────────────────────────────
    log.info("Stage: generate_figures — started")
    figures_generated = []

    def fig_path(key: str) -> Path:
        return figures_dir / FIGURE_FILENAMES[key]

    try:
        plot_coefficient_comparison(result, fig_path("coef_comparison"))
        figures_generated.append(str(fig_path("coef_comparison")))
    except Exception as e:
        log.warning("fig1 failed: %s", e)

    try:
        plot_bootstrap_distributions(result, fig_path("bootstrap_dist"))
        figures_generated.append(str(fig_path("bootstrap_dist")))
    except Exception as e:
        log.warning("fig2 failed: %s", e)

    try:
        plot_feature_stability(early_model, mid_model, late_model, fig_path("feature_stability"))
        figures_generated.append(str(fig_path("feature_stability")))
    except Exception as e:
        log.warning("fig3 failed: %s", e)

    try:
        early_scores = early_model.clf.predict_proba(
            np.hstack([shared_scaler.transform(X_test_shared),
                       q_model.predict_proba(X_test_shared)[:, 1:2]])
        )[:, 1]
        late_scores = late_model.clf.predict_proba(
            np.hstack([shared_scaler.transform(X_test_shared),
                       q_model.predict_proba(X_test_shared)[:, 1:2]])
        )[:, 1]
        plot_cross_round_scatter(early_scores, late_scores, fig_path("cross_round_scatter"))
        figures_generated.append(str(fig_path("cross_round_scatter")))
    except Exception as e:
        log.warning("fig4 failed: %s", e)

    try:
        plot_topic_balance(chi2_residuals, topic_labels, topic_pvalue, fig_path("topic_balance"))
        figures_generated.append(str(fig_path("topic_balance")))
    except Exception as e:
        log.warning("fig5 failed: %s", e)

    try:
        plot_gate_metrics(result, gate_status, fig_path("gate_metrics"))
        figures_generated.append(str(fig_path("gate_metrics")))
    except Exception as e:
        log.warning("fig6 failed: %s", e)

    log.info("%d figures generated", len(figures_generated))

    # ── Stage 12: Build metrics dict ─────────────────────────────────────
    metrics = {
        "hypothesis_id": "h-m2",
        "gate_type": "SHOULD_WORK",
        "gate_status": gate_status,
        "n_directional": result.n_directional,
        "coefficients": {
            "early": {
                "beta_L": float(result.early_coefs[0]),
                "beta_H": float(result.early_coefs[1]),
                "beta_S": float(result.early_coefs[2]),
                "beta_Q": float(early_model.beta_q),
            },
            "late": {
                "beta_L": float(result.late_coefs[0]),
                "beta_H": float(result.late_coefs[1]),
                "beta_S": float(result.late_coefs[2]),
                "beta_Q": float(late_model.beta_q),
            },
            "deltas": {
                "beta_L": float(result.deltas[0]),
                "beta_H": float(result.deltas[1]),
                "beta_S": float(result.deltas[2]),
            },
        },
        "confidence_intervals": {
            "early_95ci": {
                "beta_L": [float(result.early_ci[0, 0]), float(result.early_ci[1, 0])],
                "beta_H": [float(result.early_ci[0, 1]), float(result.early_ci[1, 1])],
                "beta_S": [float(result.early_ci[0, 2]), float(result.early_ci[1, 2])],
            },
            "late_95ci": {
                "beta_L": [float(result.late_ci[0, 0]), float(result.late_ci[1, 0])],
                "beta_H": [float(result.late_ci[0, 1]), float(result.late_ci[1, 1])],
                "beta_S": [float(result.late_ci[0, 2]), float(result.late_ci[1, 2])],
            },
            "non_overlap": {
                "beta_L": bool(result.early_ci[1, 0] < result.late_ci[0, 0]),
                "beta_H": bool(result.early_ci[1, 1] < result.late_ci[0, 1]),
                "beta_S": bool(result.early_ci[1, 2] < result.late_ci[0, 2]),
            },
        },
        "diagnostics": {
            "sign_consistent": bool(result.sign_consistent),
            "beta_q_stable": bool(result.beta_q_stable),
            "topic_balance_pvalue": float(topic_pvalue),
            "early_auc": float(held_out["early_auc"]),
            "late_auc": float(held_out["late_auc"]),
            "longer_pref_rate": float(held_out["longer_pref_rate"]),
            "n_high_ambiguity": int(held_out["n_high_ambiguity"]),
        },
        "figures_generated": figures_generated,
        "completed_at": datetime.datetime.utcnow().isoformat() + "Z",
    }

    return metrics, results_dir, outputs_dir


def serialize_results(metrics: dict, results_dir: Path, outputs_dir: Path) -> None:
    """Write results.yaml and experiment_results.json."""
    results_path = results_dir / "results.yaml"
    with open(results_path, "w") as f:
        yaml.dump(metrics, f, default_flow_style=False, allow_unicode=True)
    log.info("Results saved: %s", results_path)

    # Also write CSV-like summary
    csv_path = outputs_dir / "results.csv"
    with open(csv_path, "w") as f:
        f.write("metric,value\n")
        f.write(f"gate_status,{metrics['gate_status']}\n")
        f.write(f"n_directional,{metrics['n_directional']}\n")
        f.write(f"beta_L_delta,{metrics['coefficients']['deltas']['beta_L']}\n")
        f.write(f"beta_H_delta,{metrics['coefficients']['deltas']['beta_H']}\n")
        f.write(f"beta_S_delta,{metrics['coefficients']['deltas']['beta_S']}\n")
        f.write(f"early_auc,{metrics['diagnostics']['early_auc']}\n")
        f.write(f"late_auc,{metrics['diagnostics']['late_auc']}\n")
    log.info("CSV saved: %s", csv_path)

    # experiment_results.json (for hypothesis loop tracking)
    json_path = Path(__file__).parent.parent / "experiment_results.json"
    with open(json_path, "w") as f:
        json.dump(metrics, f, indent=2)
    log.info("experiment_results.json saved: %s", json_path)


def main() -> None:
    base_dir = setup_paths()
    log.info("H-M2 experiment starting")

    metrics, results_dir, outputs_dir = run_pipeline()
    serialize_results(metrics, results_dir, outputs_dir)

    gate_status = metrics["gate_status"]
    n = metrics["n_directional"]
    c = metrics["coefficients"]
    d = c["deltas"]
    ci = metrics["confidence_intervals"]
    diag = metrics["diagnostics"]

    print("=" * 64)
    print(f"H-M2 GATE RESULT: {gate_status}")
    print(f"n_directional: {n}/3 (target: >=2)")
    print(f"β_L: early={c['early']['beta_L']:.4f} late={c['late']['beta_L']:.4f} "
          f"δ={d['beta_L']:.4f} non-overlap={ci['non_overlap']['beta_L']}")
    print(f"β_H: early={c['early']['beta_H']:.4f} late={c['late']['beta_H']:.4f} "
          f"δ={d['beta_H']:.4f} non-overlap={ci['non_overlap']['beta_H']}")
    print(f"β_S: early={c['early']['beta_S']:.4f} late={c['late']['beta_S']:.4f} "
          f"δ={d['beta_S']:.4f} non-overlap={ci['non_overlap']['beta_S']}")
    print(f"β_Q stability: {diag['beta_q_stable']} "
          f"(Δ={abs(c['early']['beta_Q'] - c['late']['beta_Q']):.4f})")
    print(f"Sign consistent: {diag['sign_consistent']}")
    print(f"Topic balance p: {diag['topic_balance_pvalue']:.4f}")
    print("=" * 64)

    if gate_status in ("PARTIAL", "FAIL"):
        confirmed = []
        for feat, key in [("β_L", "beta_L"), ("β_H", "beta_H"), ("β_S", "beta_S")]:
            if ci["non_overlap"][key]:
                confirmed.append(feat)
        print(f"→ PIVOT: continue to H-M3 with {n} confirmed directional features: {confirmed}")

    # Gate result recording (task-024 failsafe)
    if gate_status == "PASS":
        log.info("H-M2 SHOULD_WORK gate PASSED → H-M3 can proceed with full scope")
    elif gate_status == "PARTIAL":
        log.info("H-M2 PARTIAL → H-M3 proceeds with reduced scope (document which features)")
    else:
        log.info("H-M2 FAILED → PIVOT: document null result; continue H-M3 with minimal scope")

    log.info("EXPERIMENT COMPLETE")


if __name__ == "__main__":
    main()
