"""Main experiment script for H-M1: Flat MLP Permutation Sensitivity Probing.

Pipeline:
  1. Load dataset_mnist_hyp_rand.pt (Schurholt zoo, hyp_rand variant)
  2. Grid-search FlatMLPEncoder to ~500K params
  3. Train FlatMLPWithHead (150 epochs, Adam + CosineAnnealingLR)
  4. Compute Spearman rho on test set
  5. Compute permutation sensitivity (equiv-pair vs random-pair L2)
  6. Run MUST_WORK gate: sensitivity_score > 0.3
  7. Save results + generate 5 figures

Gate: PASS if sensitivity_score > 0.3
"""
import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Any

import torch

# sys.path wiring: h-e1 first (shared utils), then h-m1 at front (overrides config)
HE1_CODE = Path(__file__).resolve().parent.parent.parent / "h-e1" / "code"
if str(HE1_CODE) not in sys.path:
    sys.path.insert(0, str(HE1_CODE))
HM1_CODE = Path(__file__).resolve().parent
if str(HM1_CODE) not in sys.path:
    sys.path.insert(0, str(HM1_CODE))

from config import ExperimentConfig, set_seed
from data_loader import load_and_split_dataset, build_dataloaders
from models import FlatMLPWithHead, grid_search_architecture
from train import train_encoder
from evaluate import compute_spearman, run_gate_check, save_results
from probe import compute_permutation_sensitivity
from visualize import (
    plot_gate_metrics,
    plot_l2_distribution,
    plot_training_curve,
    plot_sensitivity_by_decile,
    plot_embedding_scatter,
)


def setup_logging() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger("h-m1")


def setup_device(device_str: str = "auto") -> torch.device:
    if device_str == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(device_str)
    logging.getLogger("h-m1").info(f"[H-M1] Using device: {device}")
    return device


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="H-M1: Flat MLP Permutation Sensitivity")
    parser.add_argument("--data-dir", default=None)
    parser.add_argument("--results-dir", default=None)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--smoke-test", action="store_true")
    return parser.parse_args()


def main(cfg: ExperimentConfig = None, device_str: str = "auto") -> Dict[str, Any]:
    logger = setup_logging()
    if cfg is None:
        cfg = ExperimentConfig()

    set_seed(cfg.seed)
    cfg.results_dir.mkdir(parents=True, exist_ok=True)
    cfg.figures_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("H-M1: Flat MLP Encoder Permutation Sensitivity Probing")
    logger.info("=" * 60)

    device = setup_device(device_str)

    # Step 1: Load dataset
    logger.info("Step 1: Loading dataset...")
    train_ds, val_ds, test_ds, train_mean, train_std, all_checkpoints = (
        load_and_split_dataset(cfg)
    )
    logger.info(
        f"  train={len(train_ds)}, val={len(val_ds)}, test={len(test_ds)}, "
        f"total={len(all_checkpoints)}"
    )
    train_loader, val_loader, test_loader = build_dataloaders(train_ds, val_ds, test_ds, cfg)

    # Step 2: Grid-search architecture
    logger.info("Step 2: Grid-searching FlatMLPEncoder (~500K params)...")
    input_dim = train_ds.input_dim
    encoder, hidden_dims, param_count = grid_search_architecture(
        input_dim=input_dim,
        candidates=cfg.hidden_dims_candidates,
        embed_dim=cfg.embed_dim,
        dropout=cfg.dropout,
        target_min=cfg.target_params_min,
        target_max=cfg.target_params_max,
    )
    logger.info(f"  hidden_dims={hidden_dims}, params={param_count:,}")

    # Step 3: Train
    logger.info(f"Step 3: Training FlatMLPWithHead ({cfg.epochs} epochs)...")
    model = FlatMLPWithHead(encoder, embed_dim=cfg.embed_dim)
    model, history = train_encoder(model, train_loader, val_loader, cfg, device)
    logger.info(f"  Training complete. Final val_rho={history.val_spearman[-1]:.4f}")

    # Step 4: Test Spearman
    logger.info("Step 4: Computing Spearman rho on test set...")
    spearman_rho = compute_spearman(model, test_loader, device)
    logger.info(f"  [H-M1] Encoder trained. Spearman rho = {spearman_rho:.4f}")

    # Step 5: Permutation sensitivity
    logger.info("Step 5: Computing permutation sensitivity...")
    logger.info(
        f"[H-M1] Encoder trained. Spearman rho = {spearman_rho:.4f}. "
        f"Running permutation sensitivity probing..."
    )
    sensitivity_dict = compute_permutation_sensitivity(
        encoder=encoder,
        checkpoints=all_checkpoints,
        mean=train_mean,
        std=train_std,
        cfg=cfg,
        device=device,
    )
    logger.info(
        f"  sensitivity_score={sensitivity_dict['sensitivity_score']:.4f}, "
        f"mean_equiv_L2={sensitivity_dict['mean_equiv_L2']:.4f}, "
        f"mean_random_L2={sensitivity_dict['mean_random_L2']:.4f}"
    )

    # Step 6: Gate check
    logger.info("Step 6: Running MUST_WORK gate check...")
    gate_dict = run_gate_check(
        sensitivity_score=sensitivity_dict["sensitivity_score"],
        spearman_rho=spearman_rho,
        param_count=param_count,
        n_pairs=sensitivity_dict["n_pairs"],
        cfg=cfg,
    )
    logger.info(f"  [H-M1] Gate: {'PASS' if gate_dict['gate_pass'] else 'FAIL'}")

    # Step 7: Save results
    full_results = {**gate_dict, **sensitivity_dict, "hidden_dims": hidden_dims}
    save_results(full_results, cfg)

    # Step 8: Generate figures
    logger.info("Step 8: Generating figures...")
    try:
        plot_gate_metrics(sensitivity_dict["sensitivity_score"], spearman_rho, cfg)
        plot_l2_distribution(
            sensitivity_dict["equiv_dists"], sensitivity_dict["random_dists"], cfg
        )
        plot_training_curve(history, cfg)
        plot_sensitivity_by_decile(sensitivity_dict["decile_scores"], cfg)

        encoder.eval()
        embeddings_list, accuracies = [], []
        with torch.no_grad():
            for x, y in test_loader:
                emb = encoder(x.to(device)).cpu()
                embeddings_list.append(emb)
                accuracies.extend(y.numpy().tolist())
        embeddings_tensor = torch.cat(embeddings_list, dim=0)
        plot_embedding_scatter(embeddings_tensor, accuracies, [], cfg)
        logger.info(f"  Figures saved to {cfg.figures_dir}")
    except Exception as e:
        logger.warning(f"  Figure generation error (non-fatal): {e}")

    print("")
    print("=" * 60)
    gate_str = "PASS" if gate_dict["gate_pass"] else "FAIL"
    print(f"H-M1 MUST_WORK Gate: {gate_str}")
    print(f"  sensitivity_score = {gate_dict['sensitivity_score']:.4f} (threshold > {cfg.sensitivity_gate})")
    print(f"  spearman_rho      = {gate_dict['spearman_rho']:.4f}")
    print(f"  param_count       = {gate_dict['param_count']:,}")
    print(f"  n_pairs           = {gate_dict['n_pairs']}")
    print("=" * 60)
    print("EXPERIMENT COMPLETE")

    return full_results


if __name__ == "__main__":
    args = parse_args()
    cfg = ExperimentConfig()

    if args.data_dir:
        cfg.data_dir = Path(args.data_dir)
    if args.results_dir:
        cfg.results_dir = Path(args.results_dir)
    if args.epochs:
        cfg.epochs = args.epochs
    if args.smoke_test:
        cfg.epochs = 2
        cfg.n_pairs = 100

    main(cfg=cfg, device_str=args.device)
