"""Main experiment script for H-M2: NFN Equivariant Encoder Permutation Sensitivity Probing.

Pipeline:
  1. set_seed(42)
  2. load_and_split_dataset_nfn(cfg) → splits, mean, std, all_checkpoints
  3. grid_search_nfn(...) → nfn_encoder, channel_dim, n_layers, param_count
  4. Assert param_count in [475K, 525K]
  5. NFNWithHead(nfn_encoder) → nfn_model; train_encoder(...) → history
  6. compute_spearman(nfn_model, test_loader, device)
  7. compute_permutation_sensitivity_nfn(nfn_encoder, all_checkpoints, ...)
  8. run_gate_check_nfn(...) → gate_results
  9. save_results(gate_results, cfg)
  10. Generate all 6 figures

Gate: SHOULD_WORK — PASS if sensitivity_score < 0.1 AND < 0.3245
"""
import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Dict

import numpy as np
import torch

# sys.path wiring
HM2_CODE = Path(__file__).resolve().parent
if str(HM2_CODE) not in sys.path:
    sys.path.insert(0, str(HM2_CODE))

from config import ExperimentConfig, set_seed
from data_loader import load_and_split_dataset_nfn, build_dataloaders_nfn
from models import NFNWithHead, grid_search_nfn, count_params
from train import train_encoder
from evaluate import compute_spearman, run_gate_check_nfn, save_results
from probe import compute_permutation_sensitivity_nfn
from visualize import (
    plot_gate_metrics_comparison,
    plot_l2_distribution_comparison,
    plot_embedding_pca,
    plot_training_curves,
    plot_sensitivity_by_decile,
    plot_nfn_vs_mlp_decile_comparison,
)


def setup_logging() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger("h-m2")


def setup_device(device_str: str = "auto") -> torch.device:
    if device_str == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(device_str)
    logging.getLogger("h-m2").info(f"[H-M2] Using device: {device}")
    return device


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="H-M2: NFN Equivariant Encoder Permutation Sensitivity")
    parser.add_argument("--data-dir", default=None)
    parser.add_argument("--results-dir", default=None)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--n-pairs", type=int, default=None)
    parser.add_argument("--smoke-test", action="store_true",
                        help="Short test run: 2 epochs, 10 pairs")
    return parser.parse_args()


def main(cfg: ExperimentConfig = None, device_str: str = "auto") -> Dict[str, Any]:
    logger = setup_logging()
    if cfg is None:
        cfg = ExperimentConfig()

    set_seed(cfg.seed)
    cfg.results_dir.mkdir(parents=True, exist_ok=True)
    cfg.figures_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("H-M2: NFN Equivariant Encoder Permutation Sensitivity Probing")
    logger.info("=" * 60)

    device = setup_device(device_str)

    # Step 1: Load dataset
    logger.info("Step 1: Loading NFN dataset...")
    train_ds, val_ds, test_ds, train_mean, train_std, all_checkpoints = (
        load_and_split_dataset_nfn(cfg)
    )
    weight_key_order = train_ds.weight_key_order
    logger.info(
        f"  train={len(train_ds)}, val={len(val_ds)}, test={len(test_ds)}, "
        f"total={len(all_checkpoints)}, keys={len(weight_key_order)}"
    )
    train_loader, val_loader, test_loader = build_dataloaders_nfn(train_ds, val_ds, test_ds, cfg)

    # Step 2: Grid-search NFN architecture
    logger.info("Step 2: Grid-searching NFNEncoder (~500K params)...")
    nfn_encoder, channel_dim, n_layers, param_count = grid_search_nfn(
        weight_shapes=cfg.weight_shapes,
        channel_dim_candidates=cfg.channel_dim_candidates,
        n_layers_candidates=cfg.n_layers_candidates,
        embed_dim=cfg.embed_dim,
        target_min=cfg.target_params_min,
        target_max=cfg.target_params_max,
    )
    assert cfg.target_params_min <= param_count <= cfg.target_params_max, (
        f"param_count={param_count:,} outside [{cfg.target_params_min:,}, {cfg.target_params_max:,}]"
    )
    logger.info(f"  channel_dim={channel_dim}, n_layers={n_layers}, params={param_count:,}")

    # Step 3: Train
    logger.info(f"Step 3: Training NFNWithHead ({cfg.epochs} epochs)...")
    nfn_model = NFNWithHead(nfn_encoder, embed_dim=cfg.embed_dim)
    nfn_model, history = train_encoder(nfn_model, train_loader, val_loader, cfg, device)
    logger.info(f"  Training complete. Final val_rho={history.val_spearman[-1]:.4f}")

    # Step 4: Test Spearman
    logger.info("Step 4: Computing Spearman rho on test set...")
    spearman_rho = compute_spearman(nfn_model, test_loader, device)
    logger.info(f"[H-M2] NFN trained. Spearman ρ = {spearman_rho:.4f}. Running permutation sensitivity probing...")

    # Step 5: Permutation sensitivity
    logger.info("Step 5: Computing NFN permutation sensitivity...")
    nfn_encoder_eval = nfn_model.encoder
    nfn_encoder_eval.eval()
    sensitivity_dict = compute_permutation_sensitivity_nfn(
        encoder=nfn_encoder_eval,
        checkpoints=all_checkpoints,
        weight_key_order=weight_key_order,
        cfg=cfg,
        device=device,
    )
    logger.info(
        f"  sensitivity_score={sensitivity_dict['sensitivity_score']:.4f}, "
        f"mean_equiv_L2={sensitivity_dict['mean_equiv_L2']:.4f}, "
        f"mean_random_L2={sensitivity_dict['mean_random_L2']:.4f}"
    )

    # Step 6: Gate check
    logger.info("Step 6: Running SHOULD_WORK gate check...")
    gate_dict = run_gate_check_nfn(
        sensitivity_score=sensitivity_dict["sensitivity_score"],
        spearman_rho=spearman_rho,
        param_count=param_count,
        n_pairs=sensitivity_dict["n_pairs"],
        cfg=cfg,
    )
    logger.info(f"  [H-M2] Gate: {'PASS' if gate_dict['gate_pass'] else 'FAIL'}")

    # Step 7: Save results
    full_results = {
        **gate_dict,
        "param_count": param_count,
        "channel_dim": channel_dim,
        "n_layers": n_layers,
        "spearman_rho": spearman_rho,
        "sensitivity_score": sensitivity_dict["sensitivity_score"],
        "mean_equiv_L2": sensitivity_dict["mean_equiv_L2"],
        "mean_random_L2": sensitivity_dict["mean_random_L2"],
        "n_pairs": sensitivity_dict["n_pairs"],
        "decile_scores": sensitivity_dict["decile_scores"],
        "flat_mlp_sensitivity_score": cfg.flat_mlp_sensitivity_score,
    }
    save_results(full_results, cfg)

    # Step 8: Generate all 6 figures
    logger.info("Step 8: Generating 6 figures...")
    try:
        plot_gate_metrics_comparison(
            nfn_score=sensitivity_dict["sensitivity_score"],
            flat_mlp_score=cfg.flat_mlp_sensitivity_score,
            threshold_abs=cfg.sensitivity_gate_absolute,
            threshold_rel=cfg.sensitivity_gate_relative,
            figures_dir=cfg.figures_dir,
        )
        plot_l2_distribution_comparison(
            nfn_equiv_dists=sensitivity_dict["equiv_dists"],
            nfn_random_dists=sensitivity_dict["random_dists"],
            mlp_equiv_dists=[],
            mlp_random_dists=[],
            figures_dir=cfg.figures_dir,
        )
        # PCA of test-set embeddings
        nfn_encoder_eval.eval()
        embeddings_list, accuracies_list = [], []
        with torch.no_grad():
            for weight_list, flat_w, acc in test_loader:
                weight_list = [w.to(device) for w in weight_list]
                emb = nfn_encoder_eval(weight_list).cpu()
                embeddings_list.append(emb)
                accuracies_list.extend(acc.numpy().tolist())
        embeddings_arr = torch.cat(embeddings_list, dim=0).numpy()
        plot_embedding_pca(
            embeddings=embeddings_arr,
            accuracies=np.array(accuracies_list),
            equiv_pair_indices=[],
            figures_dir=cfg.figures_dir,
        )
        plot_training_curves(history, cfg.figures_dir)
        plot_sensitivity_by_decile(
            nfn_decile_scores=sensitivity_dict["decile_scores"],
            mlp_decile_scores=[],
            figures_dir=cfg.figures_dir,
        )
        plot_nfn_vs_mlp_decile_comparison(
            nfn_decile_scores=sensitivity_dict["decile_scores"],
            mlp_decile_scores=[],
            figures_dir=cfg.figures_dir,
        )
        logger.info(f"  All 6 figures saved to {cfg.figures_dir}")
    except Exception as e:
        logger.warning(f"  Figure generation error (non-fatal): {e}", exc_info=True)

    print("")
    print("=" * 60)
    gate_str = "PASS" if gate_dict["gate_pass"] else "FAIL"
    print(f"H-M2 SHOULD_WORK Gate: {gate_str}")
    print(f"  sensitivity_score     = {sensitivity_dict['sensitivity_score']:.4f}")
    print(f"  gate_absolute (<0.1)  = {gate_dict['gate_absolute_pass']}")
    print(f"  gate_relative (<0.3245) = {gate_dict['gate_relative_pass']}")
    print(f"  spearman_rho          = {spearman_rho:.4f}")
    print(f"  param_count           = {param_count:,}")
    print(f"  n_pairs               = {sensitivity_dict['n_pairs']}")
    print(f"  flat_mlp_score (ref)  = {cfg.flat_mlp_sensitivity_score:.4f}")
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
    if args.epochs is not None:
        cfg.epochs = args.epochs
    if args.n_pairs is not None:
        cfg.n_pairs = args.n_pairs
    if args.smoke_test:
        cfg.epochs = 2
        cfg.n_pairs = 10
        cfg.min_pairs = 1

    main(cfg=cfg, device_str=args.device)
