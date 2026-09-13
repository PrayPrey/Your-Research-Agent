"""Main experiment runner for h-e1.

Full pipeline:
1. Set seed and GPU
2. Load data from cache
3. Build dataloaders (flat + nft)
4. Infer input_dim and layer_fan_ins
5. Initialize and train both models
6. Evaluate (delta_rho, bootstrap, gate)
7. Verify mechanism
8. Generate figures
9. Write results JSON
"""
import os
import sys
import json
import logging
import datetime

# IMPORTANT: Set GPU before any CUDA imports
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

# Add code dir to path
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE_DIR)

import numpy as np
import torch

from src.data_loader import get_dataloaders
from src.models import FlatMLPEncoder, NFTEquivariantEncoder
from src.train import set_seed, train_model
from src.evaluate import (
    apply_stress_and_predict,
    compute_delta_rho,
    bootstrap_delta_rho,
    holm_correction,
    evaluate_gate_condition,
    verify_mechanism_activated,
)
from src.visualize import generate_all_figures

# Paths
PKL_PATH = "/home/anonymous/YouRA_results_new_4/TEST_wsl/docs/youra_research/20260316_wsl/.data_cache/datasets/unterthiner_mnist_zoo/zoo_enriched.pkl"

FIGURES_DIR = os.path.join(CODE_DIR, "figures")
CHECKPOINTS_DIR = os.path.join(CODE_DIR, "checkpoints")
RESULTS_DIR = os.path.join(CODE_DIR, "results")
LOG_PATH = os.path.join(CODE_DIR, "experiment.log")


def setup_logging():
    """Configure logging to both file and stdout."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler(sys.stdout),
        ],
    )


def main(
    data_path: str = PKL_PATH,
    figures_dir: str = FIGURES_DIR,
    checkpoints_dir: str = CHECKPOINTS_DIR,
    results_dir: str = RESULTS_DIR,
    device_str: str = "cuda",
    seed: int = 42,
    n_epochs: int = 50,  # PoC: 50 epochs
) -> None:
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("H-E1 Experiment: NFT vs Flat-MLP Permutation Robustness")
    logger.info(f"Started at: {datetime.datetime.now().isoformat()}")
    logger.info("=" * 60)

    # 1. Set seed
    set_seed(seed)

    # 2. Device
    if device_str == "cuda" and torch.cuda.is_available():
        device = torch.device("cuda")
        logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device("cpu")
        logger.info("Using CPU")

    # 3. Load data
    logger.info(f"Loading data from {data_path}")
    flat_train_loader, flat_test_loader, nft_train_loader, nft_test_loader = get_dataloaders(
        data_path, batch_size=64, train_ratio=0.8, seed=seed
    )

    # 4. Infer dimensions from first batch
    flat_batch = next(iter(flat_train_loader))
    input_dim = flat_batch[0].shape[1]
    logger.info(f"Flat input_dim: {input_dim}")

    nft_batch = next(iter(nft_train_loader))
    layer_fan_ins = [wm.shape[2] for wm in nft_batch[0]]
    logger.info(f"NFT layer_fan_ins: {layer_fan_ins}")

    # 5. Initialize models
    flat_model = FlatMLPEncoder(input_dim=input_dim, hidden_dim=512)
    nft_model = NFTEquivariantEncoder(layer_fan_ins=layer_fan_ins, d_model=128, n_heads=4)

    flat_params = sum(p.numel() for p in flat_model.parameters())
    nft_params = sum(p.numel() for p in nft_model.parameters())
    logger.info(f"FlatMLP params: {flat_params:,}")
    logger.info(f"NFT params: {nft_params:,}")

    # 6. Train flat-MLP
    logger.info(f"Training FlatMLPEncoder for {n_epochs} epochs...")
    os.makedirs(checkpoints_dir, exist_ok=True)
    flat_checkpoint = os.path.join(checkpoints_dir, "flat_mlp.pt")
    flat_train_result = train_model(
        flat_model, flat_train_loader,
        n_epochs=n_epochs, lr=1e-3,
        device=device, model_type="flat",
        checkpoint_path=flat_checkpoint,
    )
    logger.info(f"FlatMLP final loss: {flat_train_result['train_loss_history'][-1]:.6f}")

    # 7. Train NFT
    logger.info(f"Training NFTEquivariantEncoder for {n_epochs} epochs...")
    nft_checkpoint = os.path.join(checkpoints_dir, "nft_encoder.pt")
    nft_train_result = train_model(
        nft_model, nft_train_loader,
        n_epochs=n_epochs, lr=1e-3,
        device=device, model_type="nft",
        checkpoint_path=nft_checkpoint,
    )
    logger.info(f"NFT final loss: {nft_train_result['train_loss_history'][-1]:.6f}")

    # 8. Evaluate both models
    severity_levels = [0.0, 0.25, 0.5, 1.0]

    logger.info("Evaluating FlatMLP...")
    flat_delta, flat_rho_by_severity = compute_delta_rho(
        flat_model, flat_test_loader, severity_levels, device, "flat"
    )

    logger.info("Evaluating NFT...")
    nft_delta, nft_rho_by_severity = compute_delta_rho(
        nft_model, nft_test_loader, severity_levels, device, "nft"
    )

    logger.info(f"FlatMLP delta_rho: {flat_delta:.4f}")
    logger.info(f"NFT delta_rho: {nft_delta:.4f}")

    # 9. Bootstrap
    logger.info("Running bootstrap (n=10000)...")
    flat_bootstrap_samples, flat_p = bootstrap_delta_rho(
        flat_model, flat_test_loader, device, "flat", n_bootstrap=10000, seed=seed
    )
    nft_bootstrap_samples, nft_p = bootstrap_delta_rho(
        nft_model, nft_test_loader, device, "nft", n_bootstrap=10000, seed=seed
    )
    logger.info(f"FlatMLP p_value: {flat_p:.4f}")
    logger.info(f"NFT p_value: {nft_p:.4f}")

    # 10. Holm correction
    corrected_ps = holm_correction([flat_p, nft_p])
    flat_p_corrected, nft_p_corrected = corrected_ps
    logger.info(f"Holm-corrected: flat_p={flat_p_corrected:.4f}, nft_p={nft_p_corrected:.4f}")

    # 11. Gate condition
    gate_result = evaluate_gate_condition(
        flat_delta, nft_delta, flat_p_corrected, nft_p_corrected,
        results_dir=results_dir,
    )
    logger.info(f"GATE: pass={gate_result['pass_gate']}")

    # 12. Get predictions for all conditions
    flat_preds_s0, flat_labels = apply_stress_and_predict(
        flat_model, flat_test_loader, 0.0, device, "flat"
    )
    flat_preds_s1, _ = apply_stress_and_predict(
        flat_model, flat_test_loader, 1.0, device, "flat"
    )
    nft_preds_s0, _ = apply_stress_and_predict(
        nft_model, nft_test_loader, 0.0, device, "nft"
    )
    nft_preds_s1, _ = apply_stress_and_predict(
        nft_model, nft_test_loader, 1.0, device, "nft"
    )

    # 13. Verify mechanism
    results = {
        "rho_s0_nft": nft_rho_by_severity[0.0],
        "rho_s1_nft": nft_rho_by_severity[1.0],
        "nft_delta_rho": nft_delta,
        "flat_mlp_delta_rho": flat_delta,
    }

    # Get a sample NFT batch for mechanism verification
    sample_nft_batch = next(iter(nft_test_loader))

    all_pass, indicators = verify_mechanism_activated(nft_model, sample_nft_batch, results)
    logger.info(f"Mechanism verified: {all_pass}, indicators: {indicators}")

    # 14. Generate figures
    full_results = {
        "flat_mlp_delta_rho": flat_delta,
        "nft_delta_rho": nft_delta,
        "flat_rho_by_severity": {str(k): v for k, v in flat_rho_by_severity.items()},
        "nft_rho_by_severity": {str(k): v for k, v in nft_rho_by_severity.items()},
        "flat_preds_s0": flat_preds_s0,
        "flat_labels": flat_labels,
        "nft_preds_s0": nft_preds_s0,
        "flat_preds_s1": flat_preds_s1,
        "nft_preds_s1": nft_preds_s1,
        "flat_bootstrap": flat_bootstrap_samples,
        "nft_bootstrap": nft_bootstrap_samples,
    }
    generate_all_figures(full_results, figures_dir)

    # 15. Write h-e1_results.json
    os.makedirs(results_dir, exist_ok=True)
    json_results = {
        "hypothesis_id": "h-e1",
        "timestamp": datetime.datetime.now().isoformat(),
        "gate_result": gate_result,
        "flat_mlp": {
            "delta_rho": flat_delta,
            "rho_by_severity": {str(k): v for k, v in flat_rho_by_severity.items()},
            "p_value_raw": flat_p,
            "p_value_corrected": flat_p_corrected,
            "train_loss_final": flat_train_result["train_loss_history"][-1],
            "n_epochs": flat_train_result["final_epoch"],
        },
        "nft": {
            "delta_rho": nft_delta,
            "rho_by_severity": {str(k): v for k, v in nft_rho_by_severity.items()},
            "p_value_raw": nft_p,
            "p_value_corrected": nft_p_corrected,
            "train_loss_final": nft_train_result["train_loss_history"][-1],
            "n_epochs": nft_train_result["final_epoch"],
        },
        "mechanism_verified": all_pass,
        "mechanism_indicators": indicators,
        "config": {
            "n_epochs": n_epochs,
            "seed": seed,
            "device": str(device),
            "input_dim": input_dim,
            "layer_fan_ins": layer_fan_ins,
            "severity_levels": severity_levels,
        },
    }

    results_path = os.path.join(results_dir, "h-e1_results.json")
    with open(results_path, "w") as f:
        json.dump(json_results, f, indent=2)
    logger.info(f"Results written to {results_path}")

    logger.info("=" * 60)
    logger.info("EXPERIMENT COMPLETE")
    logger.info(f"Gate PASS: {gate_result['pass_gate']}")
    logger.info(f"  flat_mlp_delta_rho = {flat_delta:.4f} (threshold > 0.10)")
    logger.info(f"  nft_delta_rho      = {nft_delta:.4f} (threshold < 0.02)")
    logger.info("=" * 60)

    return json_results


if __name__ == "__main__":
    main()
