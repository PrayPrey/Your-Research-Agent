"""H-M3: DeepSets Mechanism Closure Validation — orchestration entry point."""
import sys
import os
import json
import logging
import numpy as np

# Path injection: h-m2, h-e1 code
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))
_H_M2_CODE = os.path.join(_ROOT, "docs", "youra_research", "h-m2", "code")
_H_E1_CODE = os.path.join(_ROOT, "docs", "youra_research", "h-e1", "code")
_DATA_PATH = os.path.join(_ROOT, "data", "cifar10_gs", "dataset_cifar_small_hyp_rand.pt")
_H_M2_RESULTS = os.path.join(_ROOT, "docs", "youra_research", "h-m2", "experiment_results.json")
_RESULTS_DIR = os.path.join(_ROOT, "docs", "youra_research", "h-m3")
_FIGURES_DIR = os.path.join(_RESULTS_DIR, "figures")

sys.path.insert(0, _H_M2_CODE)
sys.path.insert(0, _H_E1_CODE)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(_RESULTS_DIR, "experiment.log"), mode="w"),
    ],
)
log = logging.getLogger(__name__)

# Reference values from H-M2
MSE_PERM_C1 = 0.006137
MSE_TOTAL_C1 = 0.001834
R2_C1 = 0.851
TAU_C1 = 0.721
R2_C0_THRESHOLD = 0.984

LGBM_PARAMS = {
    "n_estimators": 500,
    "learning_rate": 0.05,
    "num_leaves": 31,
    "reg_alpha": 0.0,
    "reg_lambda": 0.1,
    "random_state": 42,
    "boosting_type": "gbdt",
    "verbose": -1,
}


def load_c1_reference():
    with open(_H_M2_RESULTS) as f:
        d = json.load(f)
    return {
        "mse_total": d["mse_total"],
        "mse_perm": d["mse_perm"],
        "r2": d["r2_c1"],
        "tau": d["tau_c1"],
    }


def main():
    import torch
    from sklearn.linear_model import RidgeCV
    from sklearn.model_selection import KFold, cross_val_predict
    from sklearn.metrics import r2_score, mean_squared_error
    from scipy.stats import kendalltau

    # Import from base code
    from data_loader import load_dataset, CONV_WEIGHT_KEYS, CHANNELS_PER_LAYER
    from lgbm_trainer import run_cv_lgbm, compute_orbit_preds, LGBM_PARAMS as BASE_LGBM_PARAMS
    from evaluate import compute_c0_features
    from permutation import sample_functional_permutations, apply_permutation
    from encoder_c2 import DeepSetsChannelEncoder, build_c2_encoder

    os.makedirs(_FIGURES_DIR, exist_ok=True)

    # ── A-1: Data & Reference Load ──────────────────────────────────────────
    log.info("=== A-1: Dataset & Reference Load ===")
    state_dicts, accs = load_dataset(_DATA_PATH, split="testset", n_models=100)
    y = np.array(accs, dtype=np.float64)
    N = len(state_dicts)
    log.info(f"Loaded N={N} models; y.shape={y.shape}, y range=[{y.min():.3f},{y.max():.3f}]")

    c1_ref = load_c1_reference()
    log.info(f"C1 reference: MSE_total={c1_ref['mse_total']:.6f}, MSE_perm={c1_ref['mse_perm']:.6f}, R²={c1_ref['r2']:.4f}")

    # ── A-2: C0 Baseline ────────────────────────────────────────────────────
    log.info("=== A-2: C0 Baseline ===")
    X_c0 = compute_c0_features(state_dicts)
    log.info(f"X_c0.shape={X_c0.shape}")
    fold_preds_c0, _ = run_cv_lgbm(X_c0, y, n_splits=5, random_state=42, params=BASE_LGBM_PARAMS.copy())
    r2_c0 = float(r2_score(y, fold_preds_c0))
    tau_c0 = float(kendalltau(y, fold_preds_c0).statistic)
    mse_c0 = float(mean_squared_error(y, fold_preds_c0))
    log.info(f"C0: R²={r2_c0:.4f}, τ={tau_c0:.4f}, MSE={mse_c0:.6f}")

    # ── A-3: C2 DeepSets Encoder ────────────────────────────────────────────
    log.info("=== A-3: C2 DeepSets Encoder ===")
    encoder_c2 = build_c2_encoder(embed_dim=128, hidden_dim=64).eval()

    # Quick orbitvar check on 5 models K=10
    channels_per_layer = CHANNELS_PER_LAYER  # [8, 6, 4] from data_loader
    perm_specs_quick = sample_functional_permutations(channels_per_layer, K=10, seed=0)
    orbit_embs_check = []
    with torch.no_grad():
        for sd in state_dicts[:5]:
            model_orbit = []
            for spec in perm_specs_quick:
                perm_sd = apply_permutation(sd, spec)
                emb = encoder_c2.forward(perm_sd)
                model_orbit.append(emb.cpu().numpy())
            orbit_embs_check.append(np.var(np.stack(model_orbit), axis=0).mean())
    orbitvar_c2 = float(np.mean(orbit_embs_check))
    log.info(f"OrbitVar(C2) quick check = {orbitvar_c2:.2e}")
    assert orbitvar_c2 < 1e-4, f"OrbitVar={orbitvar_c2:.2e} >= 1e-4 — C2 invariance FAILED"

    # Extract all embeddings
    embeddings_c2 = []
    with torch.no_grad():
        for sd in state_dicts:
            emb = encoder_c2.forward(sd)
            embeddings_c2.append(emb.cpu().numpy())
    X_c2 = np.stack(embeddings_c2)
    log.info(f"X_c2.shape={X_c2.shape}")

    # ── A-4: C2 LightGBM Training ────────────────────────────────────────────
    log.info("=== A-4: C2 LightGBM Training ===")
    fold_preds_c2, lgbm_c2 = run_cv_lgbm(X_c2, y, n_splits=5, random_state=42, params=BASE_LGBM_PARAMS.copy())
    r2_c2 = float(r2_score(y, fold_preds_c2))
    tau_c2 = float(kendalltau(y, fold_preds_c2).statistic)
    mse_c2 = float(mean_squared_error(y, fold_preds_c2))
    log.info(f"C2: R²={r2_c2:.4f}, τ={tau_c2:.4f}, MSE={mse_c2:.6f}")

    # ── A-5: C3 NFN Encoder (with fallback) ──────────────────────────────────
    log.info("=== A-5: C3 NFN Encoder ===")
    X_c3 = None
    c3_method = "unknown"
    try:
        from nfn import layers as nfn_layers
        from nfn.common import network_spec_from_wsfeat, state_dict_to_tensors
        log.info("NFN library available — attempting NFN encoding")

        # Test first model
        test_tensors = state_dict_to_tensors(state_dicts[0])
        log.info(f"NFN tensors for first model: {[(t.shape if hasattr(t,'shape') else type(t)) for t in test_tensors]}")

        # Build network_spec from first model
        # NFN expects WeightSpaceFeatures; we need to construct it
        # state_dict_to_tensors returns list of weight tensors
        # Try building wsfeat and network_spec
        from nfn.common import network_spec_from_wsfeat
        try:
            from nfn.data import WeightSpaceFeatures
        except ImportError:
            from nfn.common import WeightSpaceFeatures

        # Build wsfeat from first state dict
        tensors_0 = state_dict_to_tensors(state_dicts[0])
        wsfeat_0 = WeightSpaceFeatures(tensors_0, None)
        network_spec = network_spec_from_wsfeat(wsfeat_0)
        log.info(f"network_spec built: {network_spec}")

        encoder_c3_nfn = torch.nn.Sequential(
            nfn_layers.NPLinear(network_spec, 1, 32, io_embed=True),
            torch.nn.ReLU(),
            nfn_layers.NPLinear(network_spec, 32, 32, io_embed=True),
            torch.nn.ReLU(),
            nfn_layers.HNPPool(network_spec),
            torch.nn.Flatten(),
        ).eval()
        log.info("NFN encoder built")

        nfn_embeddings = []
        with torch.no_grad():
            for i, sd in enumerate(state_dicts):
                tensors_i = state_dict_to_tensors(sd)
                wsfeat_i = WeightSpaceFeatures(tensors_i, None)
                emb_i = encoder_c3_nfn(wsfeat_i)
                if hasattr(emb_i, 'cpu'):
                    nfn_embeddings.append(emb_i.cpu().numpy().flatten())
                else:
                    nfn_embeddings.append(np.array(emb_i).flatten())
                if i == 0:
                    log.info(f"NFN first embedding shape: {nfn_embeddings[0].shape}")

        X_c3 = np.stack(nfn_embeddings)
        c3_method = "nfn"
        log.info(f"X_c3 (NFN) shape={X_c3.shape}")

    except Exception as e:
        log.warning(f"NFN path failed: {e} — using C2 DeepSets fallback for C3")
        # Fallback: use a separate C2 encoder with different seed (same arch)
        X_c3 = X_c2.copy()
        c3_method = "c2_fallback"
        log.info(f"C3 fallback X_c3.shape={X_c3.shape}")

    # ── A-6: Linear Head Ablation ────────────────────────────────────────────
    log.info("=== A-6: Linear Head Ablation ===")
    # C2 Ridge
    ridge_c2 = RidgeCV(alphas=[0.01, 0.1, 1.0, 10.0], cv=5)
    ridge_c2.fit(X_c2, y)
    preds_c2_ridge = cross_val_predict(
        RidgeCV(alphas=[0.01, 0.1, 1.0, 10.0]), X_c2, y, cv=5
    )
    r2_c2_ridge = float(r2_score(y, preds_c2_ridge))
    log.info(f"C2-Ridge OOF R²={r2_c2_ridge:.4f}")

    # C3 Ridge
    preds_c3_ridge = cross_val_predict(
        RidgeCV(alphas=[0.01, 0.1, 1.0, 10.0]), X_c3, y, cv=5
    )
    r2_c3_ridge = float(r2_score(y, preds_c3_ridge))
    log.info(f"C3-Ridge OOF R²={r2_c3_ridge:.4f}")

    # ── A-4b: C3 LightGBM ───────────────────────────────────────────────────
    log.info("=== C3 LightGBM Training ===")
    fold_preds_c3, lgbm_c3 = run_cv_lgbm(X_c3, y, n_splits=5, random_state=42, params=BASE_LGBM_PARAMS.copy())
    r2_c3 = float(r2_score(y, fold_preds_c3))
    tau_c3 = float(kendalltau(y, fold_preds_c3).statistic)
    mse_c3 = float(mean_squared_error(y, fold_preds_c3))
    log.info(f"C3: R²={r2_c3:.4f}, τ={tau_c3:.4f}, MSE={mse_c3:.6f}")

    # ── A-7: MSE Permutation Test (C2) ──────────────────────────────────────
    log.info("=== A-7: MSE Permutation Test C2 (K=50) ===")
    perm_specs_k50 = sample_functional_permutations(channels_per_layer, K=50, seed=1)
    permuted_X_c2 = np.zeros((N, 50, 128), dtype=np.float32)
    with torch.no_grad():
        for n_idx, sd in enumerate(state_dicts):
            for k_idx, spec in enumerate(perm_specs_k50):
                perm_sd = apply_permutation(sd, spec)
                emb = encoder_c2.forward(perm_sd)
                permuted_X_c2[n_idx, k_idx, :] = emb.cpu().numpy()
    orbit_preds_c2 = compute_orbit_preds(lgbm_c2, permuted_X_c2)  # (N, K)
    mse_perm_c2 = float(np.mean(np.var(orbit_preds_c2, axis=1, ddof=0)))
    log.info(f"MSE_perm(C2) = {mse_perm_c2:.6f}")

    # ── A-8: Mechanism Closure ───────────────────────────────────────────────
    log.info("=== A-8: Mechanism Closure ===")
    delta_mse = c1_ref["mse_total"] - mse_c2
    closure = abs(delta_mse - c1_ref["mse_perm"]) / c1_ref["mse_perm"]
    log.info(f"ΔMSE(C1→C2) = {delta_mse:.6f}")
    log.info(f"MSE_perm(C1) ref = {c1_ref['mse_perm']:.6f}")
    log.info(f"closure = |ΔMSE - MSE_perm(C1)| / MSE_perm(C1) = {closure:.4f}")

    # Mechanism indicators (4; need 3/4)
    ind = {
        "c2_orbitvar_near_zero": orbitvar_c2 < 1e-4,
        "mse_perm_c2_near_zero": mse_perm_c2 < 0.0001,
        "r2_c2_improves_c1": r2_c2 > c1_ref["r2"],
        "closure_within_tolerance": closure <= 0.10,
    }
    n_pass = sum(ind.values())
    mechanism_activated = n_pass >= 3
    log.info(f"Mechanism indicators: {ind}")
    log.info(f"Mechanism activated: {mechanism_activated} ({n_pass}/4 indicators)")

    # ── A-9: Gate Evaluation ─────────────────────────────────────────────────
    log.info("=== A-9: Gate Evaluation (SHOULD_WORK) ===")
    primary_gate_pass = (r2_c2 >= R2_C0_THRESHOLD) and (closure <= 0.10)
    explore_branch = (not primary_gate_pass) and (r2_c2 > c1_ref["r2"])
    pivot_branch = closure > 2.0

    if primary_gate_pass:
        gate_status = "GATE PASS"
    elif explore_branch:
        gate_status = "EXPLORE"
    elif pivot_branch:
        gate_status = "PIVOT"
    else:
        gate_status = "GATE FAIL"

    log.info(f"Gate status: {gate_status}")
    log.info(f"  R²(C2)={r2_c2:.4f} vs threshold={R2_C0_THRESHOLD}")
    log.info(f"  closure={closure:.4f} vs tolerance=0.10")

    # ── A-10: Visualization ──────────────────────────────────────────────────
    log.info("=== A-10: Visualization ===")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        # Mandatory: R² comparison bar chart
        encoders = ["C0", "C1", "C2", "C3"]
        r2_vals = [r2_c0, c1_ref["r2"], r2_c2, r2_c3]
        colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(encoders, r2_vals, color=colors, width=0.5, alpha=0.85)
        ax.axhline(y=R2_C0_THRESHOLD, color="#333333", linestyle="--", linewidth=1.5, label=f"R²={R2_C0_THRESHOLD} threshold")
        ax.set_ylim(max(0, min(r2_vals) - 0.1), 1.05)
        ax.set_ylabel("R² (OOF LightGBM)")
        ax.set_title("H-M3: R² Comparison Across Encoders\n(CIFAR10-GS, N=100, 5-fold CV)")
        ax.legend()
        for bar, val in zip(bars, r2_vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                    f"{val:.3f}", ha="center", va="bottom", fontsize=10)
        fig_path = os.path.join(_FIGURES_DIR, "r2_comparison.png")
        fig.tight_layout()
        fig.savefig(fig_path, dpi=150)
        plt.close(fig)
        log.info(f"Saved: {fig_path}")

        # MSE decomposition stacked bar
        fig, ax = plt.subplots(figsize=(10, 6))
        mse_res_c1 = c1_ref["mse_total"] - c1_ref["mse_perm"]
        mse_res_c2 = mse_c2 - mse_perm_c2
        enc_labels = ["C1 (CISE)", "C2 (DeepSets)"]
        mse_total_vals = [c1_ref["mse_total"], mse_c2]
        mse_perm_vals = [c1_ref["mse_perm"], mse_perm_c2]
        mse_res_vals = [mse_res_c1, mse_res_c2]
        x = np.arange(len(enc_labels))
        ax.bar(x, mse_res_vals, label="MSE_res", color="#4C72B0")
        ax.bar(x, mse_perm_vals, bottom=mse_res_vals, label="MSE_perm", color="#DD8452")
        ax.set_xticks(x)
        ax.set_xticklabels(enc_labels)
        ax.set_ylabel("MSE")
        ax.set_title(f"MSE Decomposition: C1 vs C2\nΔMSE={delta_mse:.4f}, closure={closure:.4f}")
        ax.legend()
        fig2_path = os.path.join(_FIGURES_DIR, "mse_decomposition.png")
        fig.tight_layout()
        fig.savefig(fig2_path, dpi=150)
        plt.close(fig)
        log.info(f"Saved: {fig2_path}")

        # Linear head ablation bar
        fig, ax = plt.subplots(figsize=(8, 5))
        heads = ["C2-LightGBM", "C2-Ridge", "C3-LightGBM", "C3-Ridge"]
        head_r2 = [r2_c2, r2_c2_ridge, r2_c3, r2_c3_ridge]
        ax.bar(heads, head_r2, color=["#55A868", "#aaccaa", "#C44E52", "#ffaaaa"])
        ax.axhline(y=R2_C0_THRESHOLD, color="#333333", linestyle="--", linewidth=1.5)
        ax.set_ylabel("R²")
        ax.set_title("H-M3: Linear Head Ablation (LightGBM vs Ridge)")
        for i, v in enumerate(head_r2):
            ax.text(i, v + 0.005, f"{v:.3f}", ha="center", va="bottom", fontsize=9)
        fig3_path = os.path.join(_FIGURES_DIR, "linear_head_ablation.png")
        fig.tight_layout()
        fig.savefig(fig3_path, dpi=150)
        plt.close(fig)
        log.info(f"Saved: {fig3_path}")

    except Exception as e:
        log.warning(f"Visualization failed: {e}")

    # ── A-11: Results Persistence ─────────────────────────────────────────────
    log.info("=== A-11: Results Persistence ===")
    results = {
        "hypothesis_id": "h-m3",
        "gate_status": gate_status,
        "primary_gate_pass": primary_gate_pass,
        "c0": {"r2": r2_c0, "tau": tau_c0, "mse": mse_c0},
        "c1": {"r2": c1_ref["r2"], "tau": c1_ref["tau"], "mse_total": c1_ref["mse_total"], "mse_perm": c1_ref["mse_perm"]},
        "c2": {"r2": r2_c2, "tau": tau_c2, "mse_total": mse_c2, "mse_perm": mse_perm_c2, "r2_ridge": r2_c2_ridge},
        "c3": {"r2": r2_c3, "tau": tau_c3, "mse_total": mse_c3, "r2_ridge": r2_c3_ridge, "method": c3_method},
        "delta_mse": delta_mse,
        "closure": closure,
        "orbitvar_c2": orbitvar_c2,
        "mechanism_indicators": ind,
        "mechanism_activated": mechanism_activated,
        "explore_branch": explore_branch,
        "pivot_branch": pivot_branch,
    }

    out_path = os.path.join(_RESULTS_DIR, "experiment_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    log.info(f"Results saved: {out_path}")

    # Final summary
    log.info("\n" + "=" * 70)
    log.info("H-M3 GATE CHECK (SHOULD_WORK)")
    log.info("=" * 70)
    log.info(f"R²(C0) = {r2_c0:.4f}  (target ≥ {R2_C0_THRESHOLD})")
    log.info(f"R²(C1) = {c1_ref['r2']:.4f}  (reference)")
    log.info(f"R²(C2) = {r2_c2:.4f}  {'✓' if r2_c2 >= R2_C0_THRESHOLD else '—'}")
    log.info(f"R²(C3) = {r2_c3:.4f}")
    log.info(f"closure = {closure:.4f}  (target ≤ 0.10)")
    log.info(f"MSE_perm(C2) = {mse_perm_c2:.6f}  (C1 ref = {c1_ref['mse_perm']:.6f})")
    log.info(f"OrbitVar(C2) = {orbitvar_c2:.2e}  (target < 1e-4)")
    log.info(f"Mechanism activated: {mechanism_activated}")
    log.info(f"GATE STATUS: {gate_status}")
    log.info("=" * 70)

    return results


if __name__ == "__main__":
    main()
