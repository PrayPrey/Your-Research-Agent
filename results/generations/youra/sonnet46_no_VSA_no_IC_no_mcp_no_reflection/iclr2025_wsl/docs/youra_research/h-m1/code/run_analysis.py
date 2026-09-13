"""
H-M1: Analysis — do equivariant encoders outperform FlatMLP on gap prediction?
Gate: ≥1 equivariant encoder (DWSNet/NFT/GNN) achieves Spearman(gap) > FlatMLP=0.5567
"""
import os
import sys
import json
import time
import numpy as np
import torch

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Bridge to H-E1 code
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
import matplotlib.pyplot as plt

# --- Config ---
CHECKPOINT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../h-e1/checkpoints"))
FIGURES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../figures"))
RESULTS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../04_results.json"))
FLAT_MLP_BASELINE_R = 0.5567
BOOTSTRAP_N = 1000
SEED = 42
ENCODER_NAMES = ["FlatMLP", "DWSNet", "NFT", "GNN"]
CHECKPOINT_FILES = {
    "FlatMLP": "flat_mlp_best.pt",
    "DWSNet":  "dws_net_best.pt",
    "NFT":     "nft_best.pt",
    "GNN":     "gnn_best.pt",
}
SHAPES_2D = [
    (3 * 3 * 3, 4),
    (4 * 3 * 3, 8),
    (8 * 8 * 8, 64),
    (64, 10),
]


def _get_arch_kwargs(name: str, input_dim: int) -> dict:
    cfg = ENCODER_CONFIGS[name]
    if name == "FlatMLP":
        return {"input_dim": input_dim, "hidden_dim": cfg.hidden_dim}
    elif name == "DWSNet":
        return {"weight_shapes": SHAPES_2D, "hidden_dim": cfg.hidden_dim}
    elif name == "NFT":
        return {"weight_shapes": SHAPES_2D, "d_model": cfg.hidden_dim, "n_heads": 4, "n_layers": 2}
    elif name == "GNN":
        return {"hidden_dim": cfg.hidden_dim, "n_layers": 3}
    raise ValueError(name)


ENCODER_CLS = {"FlatMLP": FlatMLP, "DWSNet": DWSNet, "NFT": NFT, "GNN": GNN}


def check_missing(checkpoint_dir: str) -> list:
    return [n for n in ENCODER_NAMES
            if not os.path.exists(os.path.join(checkpoint_dir, CHECKPOINT_FILES[n]))]


def retrain_and_save(name: str, zoo: ZooData, input_dim: int, device: str) -> str:
    print(f"[H-M1] Retraining {name} (checkpoint missing)...")
    cfg = ENCODER_CONFIGS[name]
    kwargs = _get_arch_kwargs(name, input_dim)
    best_model, best_hp, _ = random_search(
        encoder_cls=ENCODER_CLS[name],
        arch_kwargs=kwargs,
        zoo=zoo,
        lr_candidates=cfg.lr_candidates,
        batch_size=cfg.batch_size,
        epochs=cfg.epochs,
        n_trials=3,
        device=device,
        lr_schedule=cfg.lr_schedule,
        encoder_name=name,
    )
    save_path = os.path.join(CHECKPOINT_DIR, CHECKPOINT_FILES[name])
    torch.save({"model_state_dict": best_model.state_dict(), "best_hp": str(best_hp)}, save_path)
    val_r, _ = eval_spearman(best_model, zoo, "val", cfg.batch_size, device)
    print(f"[H-M1] {name} retrained: val_r={val_r:.4f} -> {save_path}")
    return save_path


def load_encoder(name: str, input_dim: int, device: str) -> torch.nn.Module:
    ckpt_path = os.path.join(CHECKPOINT_DIR, CHECKPOINT_FILES[name])
    kwargs = _get_arch_kwargs(name, input_dim)
    model = ENCODER_CLS[name](**kwargs).to(device)
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    state = ckpt["model_state_dict"] if "model_state_dict" in ckpt else ckpt
    model.load_state_dict(state)
    model.eval()
    return model


def run_inference(model: torch.nn.Module, zoo: ZooData, device: str,
                  batch_size: int = 256) -> tuple:
    loader = make_loader(zoo, "test", batch_size, shuffle=False, num_workers=0)
    preds_list, gap_list = [], []
    with torch.no_grad():
        for x, y in loader:
            x = x.to(device)
            out = model(x).cpu().numpy()
            preds_list.extend(out.tolist())
            gap_list.extend(y.numpy().tolist())
    return np.array(preds_list), np.array(gap_list)


def bootstrap_ci(preds: np.ndarray, targets: np.ndarray,
                 n: int = BOOTSTRAP_N, seed: int = SEED) -> tuple:
    rng = np.random.RandomState(seed)
    rs = []
    for _ in range(n):
        idx = rng.randint(0, len(preds), size=len(preds))
        r, _ = spearmanr(preds[idx], targets[idx])
        rs.append(r if r == r else 0.0)
    r_point, _ = spearmanr(preds, targets)
    return float(r_point), float(np.percentile(rs, 2.5)), float(np.percentile(rs, 97.5))


def gate_check(results: dict) -> bool:
    equivariant = ["DWSNet", "NFT", "GNN"]
    return any(results[n]["r"] > FLAT_MLP_BASELINE_R for n in equivariant if n in results)


def compute_delta_gap(results: dict) -> float:
    equivariant = ["DWSNet", "NFT", "GNN"]
    rs = [results[n]["r"] for n in equivariant if n in results]
    return float(np.mean(rs)) - FLAT_MLP_BASELINE_R


# --- Figures ---

def fig1_bar_chart(results: dict, out_dir: str):
    names = list(results.keys())
    rs = [results[n]["r"] for n in names]
    ci_low = [results[n]["r"] - results[n]["ci_low"] for n in names]
    ci_high = [results[n]["ci_high"] - results[n]["r"] for n in names]
    colors = ["steelblue" if n == "FlatMLP" else "darkorange" for n in names]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(names, rs, color=colors, yerr=[ci_low, ci_high], capsize=5, alpha=0.85)
    ax.axhline(FLAT_MLP_BASELINE_R, color="red", linestyle="--", linewidth=1.5,
               label=f"FlatMLP baseline r={FLAT_MLP_BASELINE_R}")
    ax.set_ylabel("Spearman r (gap prediction, test split)")
    ax.set_title("H-M1: Encoder Comparison — Spearman(gap)")
    ax.legend()
    ax.set_ylim(0, 0.8)
    for bar, r in zip(bars, rs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{r:.4f}", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig1_bar.png"), dpi=150)
    plt.close()


def fig2_scatter_grid(preds_dict: dict, true_gap: np.ndarray, out_dir: str):
    names = list(preds_dict.keys())
    n = len(names)
    ncols = 2
    nrows = (n + 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(10, 4 * nrows))
    axes = axes.flatten()
    for i, name in enumerate(names):
        ax = axes[i]
        r, _ = spearmanr(preds_dict[name], true_gap)
        ax.scatter(true_gap, preds_dict[name], alpha=0.3, s=5)
        ax.set_xlabel("True gap")
        ax.set_ylabel("Predicted gap")
        ax.set_title(f"{name} (r={r:.4f})")
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)
    plt.suptitle("H-M1: Predicted vs True Gap (test split)")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig2_scatter.png"), dpi=150)
    plt.close()


def fig3_delta_gap(results: dict, out_dir: str):
    names = [n for n in results if n != "FlatMLP"]
    baseline = results["FlatMLP"]["r"]
    deltas = [results[n]["r"] - baseline for n in names]
    colors = ["green" if d > 0 else "red" for d in deltas]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(names, deltas, color=colors, alpha=0.8)
    ax.axvline(0, color="black", linewidth=1)
    ax.set_xlabel("Δ Spearman r vs FlatMLP")
    ax.set_title("H-M1: Δ_gap — Equivariant Improvement over FlatMLP")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig3_delta.png"), dpi=150)
    plt.close()


def fig4_gap_dist(true_gap: np.ndarray, out_dir: str):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(true_gap, bins=50, color="teal", alpha=0.7, edgecolor="white")
    ax.set_xlabel("Generalization gap (train_acc - test_acc)")
    ax.set_ylabel("Count")
    ax.set_title("H-M1: Test Split Gap Distribution")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "fig4_gap_dist.png"), dpi=150)
    plt.close()


def main():
    t0 = time.time()
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    print(f"[H-M1] Device: {device}")
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    cfg = ExperimentConfig()
    zoo_path = cfg.zoo.zoo_path
    if not os.path.exists(zoo_path):
        print(f"Zoo not found at {zoo_path}. Generating...")
        from generate_zoo import generate_zoo
        generate_zoo()

    print("[H-M1] Loading zoo...")
    idx_train, idx_val, idx_test = compute_split(
        cfg.zoo.expected_n_models, seed=cfg.audit.seed,
        ratios=cfg.audit.split_ratios,
    )
    zoo = load_zoo(zoo_path, idx_train=idx_train, idx_val=idx_val, idx_test=idx_test)
    input_dim = zoo.weights.shape[1]
    print(f"[H-M1] Zoo: N={len(zoo.gap)}, D={input_dim}, test={len(idx_test)}")

    # Retrain missing checkpoints
    missing = check_missing(CHECKPOINT_DIR)
    if missing:
        print(f"[H-M1] Missing checkpoints: {missing}. Retraining...")
        for name in missing:
            retrain_and_save(name, zoo, input_dim, device)
    else:
        print("[H-M1] All checkpoints found.")

    # Analysis
    results = {}
    preds_dict = {}
    true_gap = None

    for name in ENCODER_NAMES:
        print(f"[H-M1] Loading {name}...")
        model = load_encoder(name, input_dim, device)
        cfg_enc = ENCODER_CONFIGS[name]
        preds, gap = run_inference(model, zoo, device, batch_size=cfg_enc.batch_size)
        if true_gap is None:
            true_gap = gap
        r, lo, hi = bootstrap_ci(preds, gap)
        results[name] = {"r": r, "ci_low": lo, "ci_high": hi}
        preds_dict[name] = preds
        print(f"[H-M1] {name}: Spearman(gap)={r:.4f} [{lo:.4f},{hi:.4f}] vs FlatMLP={FLAT_MLP_BASELINE_R}")

    assert results["FlatMLP"]["r"] > 0.4, f"H-E1 consistency check failed: FlatMLP r={results['FlatMLP']['r']}"

    gate = gate_check(results)
    delta = compute_delta_gap(results)
    best_equivariant = max(
        ["DWSNet", "NFT", "GNN"],
        key=lambda n: results[n]["r"] if n in results else -1
    )

    print(f"\n[H-M1] === SUMMARY ===")
    for name in ENCODER_NAMES:
        flag = "✅" if results[name]["r"] > FLAT_MLP_BASELINE_R else "  "
        print(f"  {flag} {name}: r={results[name]['r']:.4f} [{results[name]['ci_low']:.4f},{results[name]['ci_high']:.4f}]")
    print(f"[H-M1] Δ_gap={delta:.4f}")
    print(f"[H-M1] gate: {'PASS' if gate else 'FAIL'}")

    # Figures
    fig1_bar_chart(results, FIGURES_DIR)
    fig2_scatter_grid(preds_dict, true_gap, FIGURES_DIR)
    fig3_delta_gap(results, FIGURES_DIR)
    fig4_gap_dist(true_gap, FIGURES_DIR)
    print(f"[H-M1] Figures saved to {FIGURES_DIR}")

    # Save results
    out = {
        "hypothesis": "h-m1",
        "gate": gate,
        "gate_condition": "≥1 equivariant encoder Spearman(gap) > FlatMLP=0.5567",
        "flat_mlp_baseline_r": FLAT_MLP_BASELINE_R,
        "delta_gap": delta,
        "best_equivariant": best_equivariant,
        "best_equivariant_r": results[best_equivariant]["r"],
        "encoders": results,
        "elapsed_sec": time.time() - t0,
    }
    with open(RESULTS_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[H-M1] Results saved to {RESULTS_PATH}")
    print(f"[H-M1] Total time: {(time.time()-t0)/60:.1f} min")
    return gate, results


if __name__ == "__main__":
    gate, results = main()
    sys.exit(0 if gate else 1)
