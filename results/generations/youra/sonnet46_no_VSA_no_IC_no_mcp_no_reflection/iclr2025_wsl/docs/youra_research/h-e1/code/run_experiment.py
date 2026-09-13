"""
H-E1: CNN Weight-Space Encoders for Generalization Gap Prediction.
Gate: ≥1 encoder achieves Spearman r > 0.5 on held-out test set.
"""
import os
import sys
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)
import json
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import torch

from config import ExperimentConfig, ENCODER_CONFIGS
from data.loader import load_zoo, ZooData
from data.audit import run_audit, compute_split
from encoders.flat_mlp import FlatMLP
from encoders.dwsnet import DWSNet
from encoders.nft import NFT
from encoders.gnn import GNN
from training.train import random_search
from evaluation.evaluate import eval_spearman, eval_mse, gate_check, print_results_table
from visualization.figures import (
    plot_spearman_bar, plot_best_scatter, plot_gap_histogram,
    plot_audit_scatter, plot_training_curves,
)


def get_weight_shapes_2d(zoo: ZooData) -> list:
    """Return (fan_in, fan_out) shapes for layers from zoo metadata or infer."""
    if zoo.weight_shapes:
        return zoo.weight_shapes
    # SmallCNN-Tiny: conv1(3,4,3,3), conv2(4,8,3,3), fc1(512,64), fc2(64,10)
    # D=33890: 108+4+288+8+32768+64+640+10
    return [
        (3 * 3 * 3, 4),    # conv1.weight [4,3,3,3] -> [27,4]
        (4 * 3 * 3, 8),    # conv2.weight [8,4,3,3] -> [36,8]
        (8 * 8 * 8, 64),   # fc1.weight [64,512] -> [512,64]
        (64, 10),           # fc2.weight [10,64] -> [64,10]
    ]


def build_encoder(name: str, cfg, zoo: ZooData, input_dim: int) -> torch.nn.Module:
    shapes_2d = get_weight_shapes_2d(zoo)
    # Only use weight (not bias) shapes — but we pass all flat weights
    # Use shapes that are actually present in the flat vector
    # Compute cumulative sizes to extract only weight (non-bias) 2D matrices
    # For simplicity: use actual 2D weight tensors from SmallCNN
    # Layer sizes in flat vector (weights + biases interleaved):
    # conv1.weight: 16*3*3*3=432, conv1.bias: 16
    # conv2.weight: 32*16*3*3=4608, conv2.bias: 32
    # fc1.weight: 128*2048=262144, fc1.bias: 128
    # fc2.weight: 10*128=1280, fc2.bias: 10
    # Total: 432+16+4608+32+262144+128+1280+10 = 268650

    if name == "FlatMLP":
        return FlatMLP(input_dim=input_dim, hidden_dim=cfg.hidden_dim)
    elif name == "DWSNet":
        return DWSNet(weight_shapes=shapes_2d, hidden_dim=cfg.hidden_dim)
    elif name == "NFT":
        return NFT(weight_shapes=shapes_2d, d_model=cfg.hidden_dim, n_heads=4, n_layers=2)
    elif name == "GNN":
        return GNN(hidden_dim=cfg.hidden_dim, n_layers=3)
    else:
        raise ValueError(f"Unknown encoder: {name}")


def main():
    t0 = time.time()
    cfg = ExperimentConfig()
    device = cfg.device if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    os.makedirs(cfg.figures_dir, exist_ok=True)

    # INFRA-1: Load zoo
    zoo_path = cfg.zoo.zoo_path
    if not os.path.exists(zoo_path):
        print(f"Zoo not found at {zoo_path}. Generating synthetic zoo...")
        from generate_zoo import generate_zoo
        generate_zoo()

    print(f"\n[1/6] Loading zoo from {zoo_path}")
    idx_train, idx_val, idx_test = compute_split(
        cfg.zoo.expected_n_models, seed=cfg.audit.seed,
        ratios=cfg.audit.split_ratios,
    )
    zoo = load_zoo(zoo_path, idx_train=idx_train, idx_val=idx_val, idx_test=idx_test)
    input_dim = zoo.weights.shape[1]
    print(f"  Zoo: N={len(zoo.gap)}, D={input_dim}")
    print(f"  Split: train={len(idx_train)}, val={len(idx_val)}, test={len(idx_test)}")

    # FR-0: Audit
    print("\n[2/6] Running A1 audit...")
    audit_r = run_audit(zoo, threshold=cfg.audit.spearman_threshold)

    # Figures: gap histogram + audit scatter
    plot_gap_histogram(zoo, cfg.figures_dir)
    plot_audit_scatter(zoo, audit_r, cfg.figures_dir)
    print(f"  Saved gap_distribution.png, a1_audit_scatter.png")

    # Train all encoders
    results = {}
    best_models = {}
    training_curves = {}

    encoder_names = list(ENCODER_CONFIGS.keys())
    print(f"\n[3/6] Training {len(encoder_names)} encoders...")

    for enc_name in encoder_names:
        enc_cfg = ENCODER_CONFIGS[enc_name]
        print(f"\n--- {enc_name} ---")
        print(f"  lr_candidates={enc_cfg.lr_candidates}, batch={enc_cfg.batch_size}, "
              f"epochs={enc_cfg.epochs}, trials={cfg.n_trials}")

        def make_enc():
            return build_encoder(enc_name, enc_cfg, zoo, input_dim)

        best_model, best_hp, best_curve = random_search(
            encoder_cls=type(make_enc()),
            arch_kwargs=_get_arch_kwargs(enc_name, enc_cfg, zoo, input_dim),
            zoo=zoo,
            lr_candidates=enc_cfg.lr_candidates,
            batch_size=enc_cfg.batch_size,
            epochs=enc_cfg.epochs,
            n_trials=cfg.n_trials,
            device=device,
            lr_schedule=enc_cfg.lr_schedule,
            encoder_name=enc_name,
        )

        val_r, _ = eval_spearman(best_model, zoo, "val", enc_cfg.batch_size, device)
        test_r, test_p = eval_spearman(best_model, zoo, "test", enc_cfg.batch_size, device)
        test_mse = eval_mse(best_model, zoo, "test", enc_cfg.batch_size, device)

        results[enc_name] = {
            "val_r": val_r, "test_r": test_r, "test_mse": test_mse,
            "test_p": test_p, "best_hp": best_hp,
        }
        best_models[enc_name] = best_model
        training_curves[enc_name] = best_curve
        print(f"  {enc_name}: test_r={test_r:.4f} test_mse={test_mse:.6f}")

    # Evaluation + gate check
    print("\n[4/6] Gate evaluation:")
    print_results_table(results, threshold=cfg.gate_threshold)
    gate = gate_check(results, threshold=cfg.gate_threshold)

    # Visualization
    print("\n[5/6] Generating figures...")
    plot_spearman_bar(results, cfg.gate_threshold, cfg.figures_dir)
    plot_training_curves(training_curves, cfg.figures_dir)

    best_enc_name = max(results, key=lambda k: results[k]["test_r"])
    plot_best_scatter(best_models[best_enc_name], zoo, "test",
                      best_enc_name, device, cfg.figures_dir)
    print(f"  Saved encoder_gap_spearman.png, training_curves.png, best_encoder_scatter.png")

    # Save results JSON
    results_path = "results.json"
    with open(results_path, "w") as f:
        json.dump({
            "gate": gate,
            "gate_threshold": cfg.gate_threshold,
            "audit_r": audit_r,
            "encoders": {k: {kk: float(vv) if isinstance(vv, float) else str(vv)
                             for kk, vv in v.items()} for k, v in results.items()},
            "elapsed_sec": time.time() - t0,
        }, f, indent=2)
    print(f"\n[6/6] Results saved to {results_path}")
    print(f"Total time: {(time.time()-t0)/60:.1f} min")
    print(f"\nH-E1 GATE: {'PASS' if gate else 'FAIL'}")
    return gate, results


def _get_arch_kwargs(enc_name: str, enc_cfg, zoo: ZooData, input_dim: int) -> dict:
    shapes_2d = [
        (3 * 3 * 3, 4),
        (4 * 3 * 3, 8),
        (8 * 8 * 8, 64),
        (64, 10),
    ]
    if enc_name == "FlatMLP":
        return {"input_dim": input_dim, "hidden_dim": enc_cfg.hidden_dim}
    elif enc_name == "DWSNet":
        return {"weight_shapes": shapes_2d, "hidden_dim": enc_cfg.hidden_dim}
    elif enc_name == "NFT":
        return {"weight_shapes": shapes_2d, "d_model": enc_cfg.hidden_dim,
                "n_heads": 4, "n_layers": 2}
    elif enc_name == "GNN":
        return {"hidden_dim": enc_cfg.hidden_dim, "n_layers": 3}
    raise ValueError(enc_name)


if __name__ == "__main__":
    gate, results = main()
    sys.exit(0 if gate else 1)
