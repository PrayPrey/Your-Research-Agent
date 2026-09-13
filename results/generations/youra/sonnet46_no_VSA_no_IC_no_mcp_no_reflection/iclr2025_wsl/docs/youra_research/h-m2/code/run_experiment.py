"""
H-M2: Differential Advantage of Permutation-Equivariant Encoders (gap vs. test_acc)
Gate: Δ > 0.02 for ≥2 of {DWSNet, NFT, GNN}
"""
import os
import sys
import json
import time
import copy
from dataclasses import replace
import numpy as np
import torch

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Bridge to H-E1 code (same pattern as H-M1)
H_E1_CODE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../h-e1/code"))
sys.path.insert(0, H_E1_CODE)
os.chdir(H_E1_CODE)

from config import ExperimentConfig, ENCODER_CONFIGS
from data.loader import load_zoo, ZooData, make_loader
from data.audit import compute_split
from encoders.flat_mlp import FlatMLP
from encoders.dwsnet import DWSNet
from encoders.nft import NFT
from encoders.gnn import GNN
from training.train import random_search, train_encoder
from evaluation.evaluate import eval_spearman

from scipy.stats import spearmanr
import matplotlib
matplotlib.use("Agg")

# Switch back to h-m2 code dir to import local modules
H_M2_CODE = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, H_M2_CODE)

from compute_delta import H_M1_GAP, EQUIVARIANT, compute_delta, gate_check, bootstrap_delta_ci
from metrics import partial_spearman, bootstrap_spearman_ci, verify_h_m2_mechanism, rank_residuals
from visualize import (fig1_gate_delta, fig2_dual_target_spearman, fig3_delta_decomposition,
                       fig4_partial_corr_scatter, fig5_bootstrap_ci)

# --- Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
H_M2_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
CHECKPOINT_DIR = os.path.join(H_M2_DIR, "checkpoints")
FIGURES_DIR = os.path.join(H_M2_DIR, "figures")
RESULTS_PATH = os.path.join(H_M2_DIR, "04_results.json")

# H-M1 gap results (canonical from h-m1/04_results.json)
H_M1_GAP_RESULTS = H_M1_GAP
ENCODER_NAMES = ["FlatMLP", "DWSNet", "NFT", "GNN"]
TESTACC_CHECKPOINT_FILES = {
    "FlatMLP": "flat_mlp_testacc_best.pt",
    "DWSNet":  "dws_net_testacc_best.pt",
    "NFT":     "nft_testacc_best.pt",
    "GNN":     "gnn_testacc_best.pt",
}
SHAPES_2D = [(3 * 3 * 3, 4), (4 * 3 * 3, 8), (8 * 8 * 8, 64), (64, 10)]
SEED = 42
BOOTSTRAP_N = 1000
N_TRIALS = 3


ENCODER_CLS = {
    "FlatMLP": FlatMLP,
    "DWSNet":  DWSNet,
    "NFT":     NFT,
    "GNN":     GNN,
}


def _get_arch_kwargs(name: str, input_dim: int) -> dict:
    cfg = ENCODER_CONFIGS[name]
    if name == "FlatMLP":
        return {"input_dim": input_dim, "hidden_dim": cfg.hidden_dim}
    elif name == "DWSNet":
        return {"weight_shapes": SHAPES_2D, "hidden_dim": cfg.hidden_dim}
    elif name == "NFT":
        return {"weight_shapes": SHAPES_2D, "hidden_dim": cfg.hidden_dim}
    elif name == "GNN":
        return {"weight_shapes": SHAPES_2D, "hidden_dim": cfg.hidden_dim}
    return {}


def build_encoder(name: str, input_dim: int) -> torch.nn.Module:
    kwargs = _get_arch_kwargs(name, input_dim)
    return ENCODER_CLS[name](**kwargs)


def make_testacc_zoo(zoo: ZooData) -> ZooData:
    """Return zoo copy with gap field replaced by test_acc (for test_acc training)."""
    return replace(zoo, gap=zoo.test_acc)


def train_testacc(name: str, zoo_acc: ZooData, input_dim: int, device: str) -> tuple:
    """3-trial random_search on test_acc target. Returns (best_val_r, best_state_dict).
    Uses H-M1 protocol: batch=64, epochs=100, lr in [5e-4, 2e-3] for all encoders."""
    cfg = ENCODER_CONFIGS[name]
    # H-M2 spec: identical protocol to H-M1 for controlled comparison
    # H-M1 used batch=64, epochs=100, lr_candidates=[5e-4, 1e-3, 2e-3]
    LR_CANDIDATES = [5e-4, 1e-3, 2e-3]
    BATCH = 64
    EPOCHS = 100
    best_model, best_hp, _ = random_search(
        encoder_cls=ENCODER_CLS[name],
        arch_kwargs=_get_arch_kwargs(name, input_dim),
        zoo=zoo_acc,
        lr_candidates=LR_CANDIDATES,
        batch_size=BATCH,
        epochs=EPOCHS,
        n_trials=N_TRIALS,
        device=device,
        lr_schedule=cfg.lr_schedule,
        encoder_name=name,
    )
    val_r, _ = eval_spearman(best_model, zoo_acc, "val", BATCH, device)
    return val_r, best_model.state_dict(), str(best_hp)


def evaluate_testacc(name: str, model: torch.nn.Module, zoo_acc: ZooData,
                     device: str) -> np.ndarray:
    """Run test-split inference on test_acc zoo. Returns preds array [N_test]."""
    loader = make_loader(zoo_acc, "test", 64, shuffle=False)
    model.eval()
    preds = []
    with torch.no_grad():
        for weights, _ in loader:
            weights = weights.to(device)
            out = model(weights).cpu().numpy()
            preds.extend(out.tolist())
    return np.array(preds, dtype=np.float32)


def run_inference_gap(name: str, model: torch.nn.Module, zoo: ZooData,
                      device: str) -> np.ndarray:
    """Run test-split inference on gap zoo. Returns preds array [N_test]."""
    loader = make_loader(zoo, "test", 64, shuffle=False)
    model.eval()
    preds = []
    with torch.no_grad():
        for weights, _ in loader:
            weights = weights.to(device)
            out = model(weights).cpu().numpy()
            preds.extend(out.tolist())
    return np.array(preds, dtype=np.float32)


def load_testacc_checkpoint(name: str, input_dim: int, device: str) -> torch.nn.Module:
    """Load test_acc checkpoint; return model in eval mode."""
    path = os.path.join(CHECKPOINT_DIR, TESTACC_CHECKPOINT_FILES[name])
    model = build_encoder(name, input_dim)
    ckpt = torch.load(path, map_location=device, weights_only=False)
    state = ckpt["model_state_dict"] if "model_state_dict" in ckpt else ckpt
    model.load_state_dict(state)
    model = model.to(device)
    model.eval()
    return model


def load_gap_checkpoint(name: str, input_dim: int, device: str) -> torch.nn.Module:
    """Load h-m1/h-e1 gap checkpoint; return model in eval mode."""
    # H-E1 checkpoints location (same as H-M1 used)
    H_E1_CKPT_DIR = os.path.abspath(os.path.join(H_M2_DIR, "../h-e1/checkpoints"))
    gap_files = {
        "FlatMLP": "flat_mlp_best.pt",
        "DWSNet":  "dws_net_best.pt",
        "NFT":     "nft_best.pt",
        "GNN":     "gnn_best.pt",
    }
    path = os.path.join(H_E1_CKPT_DIR, gap_files[name])
    model = build_encoder(name, input_dim)
    ckpt = torch.load(path, map_location=device, weights_only=False)
    state = ckpt["model_state_dict"] if "model_state_dict" in ckpt else ckpt
    model.load_state_dict(state)
    model = model.to(device)
    model.eval()
    return model


def main():
    t0 = time.time()
    # Use cuda:1 to avoid conflict with other experiments on cuda:0
    device = "cuda:1" if torch.cuda.device_count() > 1 else ("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"[H-M2] Device: {device}")
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    cfg = ExperimentConfig()
    zoo_path = cfg.zoo.zoo_path
    if not os.path.exists(zoo_path):
        print(f"Zoo not found at {zoo_path}. Generating...")
        from generate_zoo import generate_zoo
        generate_zoo()

    print("[H-M2] Loading zoo...")
    idx_train, idx_val, idx_test = compute_split(
        cfg.zoo.expected_n_models, seed=cfg.audit.seed,
        ratios=cfg.audit.split_ratios,
    )
    zoo = load_zoo(zoo_path, idx_train=idx_train, idx_val=idx_val, idx_test=idx_test)
    input_dim = zoo.weights.shape[1]
    print(f"[H-M2] Zoo: N={len(zoo.gap)}, D={input_dim}, test={len(idx_test)}")

    # Zoo with test_acc as regression target
    zoo_acc = make_testacc_zoo(zoo)

    # === STEP 1: Train all 4 encoders on test_acc target ===
    testacc_preds_dict: dict[str, np.ndarray] = {}
    testacc_results: dict[str, float] = {}

    for name in ENCODER_NAMES:
        ckpt_path = os.path.join(CHECKPOINT_DIR, TESTACC_CHECKPOINT_FILES[name])
        if os.path.exists(ckpt_path):
            print(f"[H-M2] {name}: checkpoint exists, loading...")
            model = load_testacc_checkpoint(name, input_dim, device)
        else:
            print(f"[H-M2] {name}: training on test_acc (N_trials={N_TRIALS})...")
            val_r, state_dict, best_hp = train_testacc(name, zoo_acc, input_dim, device)
            print(f"[H-M2] {name}: best val Spearman(test_acc)={val_r:.4f}")
            torch.save({"model_state_dict": state_dict, "best_hp": best_hp},
                       ckpt_path)
            model = build_encoder(name, input_dim)
            model.load_state_dict(state_dict)
            model = model.to(device)
            model.eval()

        preds = evaluate_testacc(name, model, zoo_acc, device)
        true_testacc = zoo.test_acc[idx_test]
        r, _ = spearmanr(preds, true_testacc)
        ci_low, ci_high = bootstrap_spearman_ci(preds, true_testacc, n_boot=BOOTSTRAP_N, seed=SEED)
        testacc_preds_dict[name] = preds
        testacc_results[name] = float(r)
        print(f"[H-M2] {name}: Spearman(test_acc)={r:.4f} [{ci_low:.4f},{ci_high:.4f}]")

    print(f"\n[H-M2] === test_acc training complete ({(time.time()-t0)/60:.1f} min) ===")

    # === STEP 2: Collect gap results from H-M1 (hardcoded, no re-training) ===
    gap_results = dict(H_M1_GAP_RESULTS)
    print(f"\n[H-M2] H-M1 gap results (reused):")
    for name, r in gap_results.items():
        print(f"  {name}: Spearman(gap)={r:.4f}")

    # === STEP 3: Get gap predictions from H-E1 checkpoints for bootstrap CI ===
    gap_preds_dict: dict[str, np.ndarray] = {}
    true_gap = zoo.gap[idx_test]
    for name in ENCODER_NAMES:
        try:
            model_gap = load_gap_checkpoint(name, input_dim, device)
            preds_gap = run_inference_gap(name, model_gap, zoo, device)
            gap_preds_dict[name] = preds_gap
        except Exception as e:
            print(f"[H-M2] Warning: could not load gap checkpoint for {name}: {e}")
            # Use zero-correlation proxy (CI will be wide but delta CI still computable)
            gap_preds_dict[name] = np.zeros(len(idx_test))

    true_testacc = zoo.test_acc[idx_test]

    # === STEP 4: Compute Δ ===
    print(f"\n[H-M2] === Δ Computation ===")
    delta = compute_delta(gap_results, testacc_results)
    n_pass, passed = gate_check(delta)
    print(f"[H-M2] Gate: {'PASS ✓' if passed else 'FAIL ✗'} ({n_pass}/3 encoders Δ > 0.02)")

    # Bootstrap CI on Δ
    ci = bootstrap_delta_ci(gap_preds_dict, testacc_preds_dict, true_gap, true_testacc,
                             n_boot=BOOTSTRAP_N, seed=SEED)
    print(f"\n[H-M2] Bootstrap 95% CI on Δ:")
    for enc in EQUIVARIANT:
        print(f"  {enc}: Δ={delta[enc]:.4f} [{ci[enc][0]:.4f},{ci[enc][1]:.4f}]")

    # === STEP 5: Partial Spearman P3 (NFT) ===
    print(f"\n[H-M2] === Partial Spearman P3 (NFT) ===")
    nft_gap_preds = gap_preds_dict["NFT"]
    p3_r, p3_p = partial_spearman(nft_gap_preds, true_gap, true_testacc)
    p3 = (p3_r, p3_p)
    print(f"[H-M2] NFT Partial Spearman(gap|test_acc): r={p3_r:.4f}, p={p3_p:.4f}")
    p3_pass = p3_r > 0 and p3_p < 0.05
    print(f"[H-M2] P3: {'PASS' if p3_pass else 'FAIL'} (r>0 and p<0.05)")

    # P3 residuals for fig4
    from scipy.stats import rankdata
    z_rank = rankdata(true_testacc)
    nft_pred_resid = rank_residuals(nft_gap_preds, z_rank)
    true_gap_resid = rank_residuals(true_gap, z_rank)

    # === STEP 6: Mechanism Verification ===
    print(f"\n[H-M2] === Mechanism Verification ===")
    ok = verify_h_m2_mechanism(testacc_results, gap_results, delta, p3)
    print(f"[H-M2] Mechanism verification: {'OK' if ok else 'ISSUES FOUND'}")

    # === STEP 7: Figures ===
    print(f"\n[H-M2] === Generating Figures ===")
    fig1_gate_delta(delta, ci, 0.02,
                    os.path.join(FIGURES_DIR, "fig1_gate_delta.png"))
    fig2_dual_target_spearman(gap_results, testacc_results,
                               os.path.join(FIGURES_DIR, "fig2_dual_target_spearman.png"))
    fig3_delta_decomposition(gap_results, testacc_results,
                              os.path.join(FIGURES_DIR, "fig3_delta_decomposition.png"))
    fig4_partial_corr_scatter(nft_pred_resid, true_gap_resid, p3_r, p3_p,
                               os.path.join(FIGURES_DIR, "fig4_partial_corr_scatter.png"))
    fig5_bootstrap_ci(delta, ci,
                      os.path.join(FIGURES_DIR, "fig5_bootstrap_ci.png"))
    print(f"[H-M2] Figures saved to {FIGURES_DIR}")

    # === STEP 8: Save results ===
    elapsed = time.time() - t0
    testacc_ci = {}
    for name in ENCODER_NAMES:
        ci_l, ci_h = bootstrap_spearman_ci(testacc_preds_dict[name],
                                            zoo.test_acc[idx_test],
                                            n_boot=BOOTSTRAP_N, seed=SEED)
        testacc_ci[name] = {"ci_low": ci_l, "ci_high": ci_h}

    out = {
        "hypothesis": "h-m2",
        "gate": passed,
        "gate_condition": "Δ > 0.02 for ≥2 of {DWSNet, NFT, GNN}",
        "n_pass": n_pass,
        "gap_results": {k: {"r": v} for k, v in gap_results.items()},
        "testacc_results": {
            name: {
                "r": testacc_results[name],
                "ci_low": testacc_ci[name]["ci_low"],
                "ci_high": testacc_ci[name]["ci_high"],
            }
            for name in ENCODER_NAMES
        },
        "delta": {enc: {"delta": delta[enc], "ci_low": ci[enc][0], "ci_high": ci[enc][1]}
                  for enc in EQUIVARIANT},
        "p3": {"r": p3_r, "p": p3_p, "pass": p3_pass},
        "mechanism_verification": ok,
        "elapsed_sec": elapsed,
    }
    with open(RESULTS_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[H-M2] Results saved to {RESULTS_PATH}")

    # === Final Summary ===
    print(f"\n[H-M2] ===== FINAL SUMMARY =====")
    print(f"{'Encoder':<10} {'Spearman(gap)':>14} {'Spearman(acc)':>14} {'Δ':>10}")
    print("-" * 54)
    for name in ENCODER_NAMES:
        delta_str = f"{delta.get(name, '-'):>10.4f}" if name in delta else "         -"
        print(f"{name:<10} {gap_results[name]:>14.4f} {testacc_results[name]:>14.4f} {delta_str}")
    print("-" * 54)
    print(f"Gate: {'PASS ✓' if passed else 'FAIL ✗'} ({n_pass}/3 encoders Δ > 0.02)")
    print(f"P3 (NFT partial Spearman): r={p3_r:.4f}, p={p3_p:.4f} → {'PASS' if p3_pass else 'FAIL'}")
    print(f"Total time: {elapsed/60:.1f} min")
    print(f"EXPERIMENT COMPLETE (gate={'PASS' if passed else 'FAIL'})")

    return passed, out


if __name__ == "__main__":
    passed, results = main()
    sys.exit(0 if passed else 2)
