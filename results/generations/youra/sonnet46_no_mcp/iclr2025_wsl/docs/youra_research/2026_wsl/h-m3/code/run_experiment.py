"""h-m3 experiment orchestrator: NFN vs Flat MLP Delta-rho controlled benchmark."""
import json
import logging
import sys
from pathlib import Path

import numpy as np
import torch

# Ensure h-m3/code is on path
CODE_DIR = Path(__file__).parent.resolve()
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from config import ExperimentConfig, RunConfig, VisualizationConfig, set_seed
from data_loader import download_cifar_zoo, load_mnist_flat, load_mnist_nfn, load_cifar_flat, load_cifar_nfn
from models import grid_search_deep_sets, load_flat_mlp_checkpoint, load_nfn_checkpoint, DeepSetsWithHead, count_params
from train import get_weight_shapes, prepare_flat_elements_batch, train_deep_sets, train_flat_mlp_fresh, train_nfn_fresh
from evaluate import (bootstrap_spearman_ci, evaluate_flat_encoder, evaluate_deep_sets_encoder,
                       evaluate_nfn_encoder, compute_delta_rho_ci, compute_tier_analysis,
                       check_hm3_gate, save_results)
from visualize import (plot_rho_comparison, plot_symmetry_spectrum, plot_tier_delta_rho,
                        plot_bootstrap_distribution, plot_cross_zoo_consistency)


def setup_logging(run_cfg: RunConfig) -> None:
    handlers = [logging.StreamHandler(sys.stdout)]
    if run_cfg.log_to_file:
        run_cfg.log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(run_cfg.log_file))
    logging.basicConfig(
        level=getattr(logging, run_cfg.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
        force=True,
    )


def main():
    cfg = ExperimentConfig()
    run_cfg = RunConfig()
    vis_cfg = VisualizationConfig()

    setup_logging(run_cfg)
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("h-m3: NFN vs Flat MLP Delta-rho Controlled Benchmark")
    logger.info("=" * 60)

    # Step 1: Seed and device
    set_seed(cfg.seed)
    device = torch.device(cfg.device)
    logger.info(f"Device: {device}")

    # Step 2: Create output dirs
    cfg.results_dir.mkdir(parents=True, exist_ok=True)
    cfg.figures_dir.mkdir(parents=True, exist_ok=True)

    # Step 3: CIFAR-10 availability check
    cifar_available = False
    if run_cfg.skip_cifar_if_unavailable:
        cifar_available = download_cifar_zoo(cfg)
        if not cifar_available:
            logger.warning("CIFAR-10 unavailable — MNIST-CNN primary result only")
    else:
        cifar_available = True

    results = {
        "encoders": {
            "flat_mlp": {"mnist_cnn": {}, "cifar10": {}},
            "deep_sets": {"mnist_cnn": {}, "cifar10": {}},
            "nfn":       {"mnist_cnn": {}, "cifar10": {}},
        },
        "delta_metrics": {},
        "gate_results": {},
        "training_metadata": {},
        "tier_analysis": {},
    }

    # ─────────────────────────────────────────────────────────
    # MNIST-CNN: FlatMLP (checkpoint)
    # ─────────────────────────────────────────────────────────
    logger.info("\n[MNIST-CNN] Loading FlatMLP from checkpoint...")
    mnist_flat_train, mnist_flat_val, mnist_flat_test, input_dim = load_mnist_flat(cfg)
    flat_model = load_flat_mlp_checkpoint(cfg, input_dim)
    flat_model = flat_model.to(device)
    flat_model.eval()
    flat_res_mnist = evaluate_flat_encoder(flat_model, mnist_flat_test, device, cfg.n_resamples)
    results["encoders"]["flat_mlp"]["mnist_cnn"] = {
        "rho": flat_res_mnist["rho"],
        "ci_lower": flat_res_mnist["ci_lower"],
        "ci_upper": flat_res_mnist["ci_upper"],
        "param_count": count_params(flat_model),
    }
    logger.info(f"FlatMLP MNIST rho={flat_res_mnist['rho']:.4f}")

    # ─────────────────────────────────────────────────────────
    # MNIST-CNN: NFN (checkpoint)
    # ─────────────────────────────────────────────────────────
    logger.info("\n[MNIST-CNN] Loading NFN from checkpoint...")
    mnist_nfn_train, mnist_nfn_val, mnist_nfn_test, weight_shapes_mnist = load_mnist_nfn(cfg)
    nfn_model = load_nfn_checkpoint(cfg, weight_shapes_mnist)
    nfn_model = nfn_model.to(device)
    nfn_model.eval()
    nfn_res_mnist = evaluate_nfn_encoder(nfn_model, mnist_nfn_test, device, cfg.n_resamples)
    results["encoders"]["nfn"]["mnist_cnn"] = {
        "rho": nfn_res_mnist["rho"],
        "ci_lower": nfn_res_mnist["ci_lower"],
        "ci_upper": nfn_res_mnist["ci_upper"],
        "param_count": count_params(nfn_model),
    }
    logger.info(f"NFN MNIST rho={nfn_res_mnist['rho']:.4f}")

    # ─────────────────────────────────────────────────────────
    # MNIST-CNN: DeepSets (train fresh)
    # ─────────────────────────────────────────────────────────
    logger.info("\n[MNIST-CNN] Training DeepSets from scratch...")
    # Determine element_dim from weight_shapes
    element_dim_mnist = max(1 for s in weight_shapes_mnist
                            for _ in [1]) if not weight_shapes_mnist else max(
        int(np.prod(s)) for s in weight_shapes_mnist)
    # Recompute element_dim properly
    element_dim_mnist = max(int(np.prod(s)) for s in weight_shapes_mnist)

    ds_encoder_mnist, phi_hidden_mnist, n_params_mnist = grid_search_deep_sets(
        element_dim=element_dim_mnist,
        phi_hidden_candidates=cfg.phi_hidden_candidates,
        rho_hidden=cfg.rho_hidden,
        embed_dim=cfg.embed_dim,
        target_min=cfg.target_params_min,
        target_max=cfg.target_params_max,
    )
    ds_model_mnist = DeepSetsWithHead(ds_encoder_mnist, cfg.embed_dim).to(device)
    ds_model_mnist, ds_history_mnist = train_deep_sets(
        ds_model_mnist, mnist_flat_train, mnist_flat_val,
        cfg, device, "best_deep_sets_mnist.pt", weight_shapes_mnist
    )
    ds_res_mnist = evaluate_deep_sets_encoder(
        ds_model_mnist, mnist_flat_test, device, weight_shapes_mnist, cfg.n_resamples
    )
    results["encoders"]["deep_sets"]["mnist_cnn"] = {
        "rho": ds_res_mnist["rho"],
        "ci_lower": ds_res_mnist["ci_lower"],
        "ci_upper": ds_res_mnist["ci_upper"],
        "param_count": n_params_mnist,
    }
    results["training_metadata"]["deep_sets_mnist"] = {
        "phi_hidden": phi_hidden_mnist,
        "param_count": n_params_mnist,
        "best_val_loss": ds_history_mnist.get("best_val_loss"),
        "best_epoch": ds_history_mnist.get("best_epoch"),
    }
    logger.info(f"DeepSets MNIST rho={ds_res_mnist['rho']:.4f}")

    # ─────────────────────────────────────────────────────────
    # CIFAR-10 (if available)
    # ─────────────────────────────────────────────────────────
    if cifar_available:
        try:
            logger.info("\n[CIFAR-10] Training FlatMLP from scratch...")
            cifar_flat_train, cifar_flat_val, cifar_flat_test, cifar_input_dim = load_cifar_flat(cfg)
            flat_cifar_model, flat_cifar_hist = train_flat_mlp_fresh(
                cfg, device, cifar_flat_train, cifar_flat_val,
                cifar_input_dim, "best_flat_mlp_cifar.pt"
            )
            flat_res_cifar = evaluate_flat_encoder(flat_cifar_model, cifar_flat_test, device, cfg.n_resamples)
            results["encoders"]["flat_mlp"]["cifar10"] = {
                "rho": flat_res_cifar["rho"],
                "ci_lower": flat_res_cifar["ci_lower"],
                "ci_upper": flat_res_cifar["ci_upper"],
                "param_count": flat_cifar_hist.get("param_count", 0),
            }
            logger.info(f"FlatMLP CIFAR rho={flat_res_cifar['rho']:.4f}")

            logger.info("\n[CIFAR-10] Training NFN from scratch...")
            cifar_nfn_train, cifar_nfn_val, cifar_nfn_test, weight_shapes_cifar = load_cifar_nfn(cfg)
            nfn_cifar_model, nfn_cifar_hist = train_nfn_fresh(
                cfg, device, cifar_nfn_train, cifar_nfn_val,
                weight_shapes_cifar, "best_nfn_cifar.pt"
            )
            nfn_res_cifar = evaluate_nfn_encoder(nfn_cifar_model, cifar_nfn_test, device, cfg.n_resamples)
            results["encoders"]["nfn"]["cifar10"] = {
                "rho": nfn_res_cifar["rho"],
                "ci_lower": nfn_res_cifar["ci_lower"],
                "ci_upper": nfn_res_cifar["ci_upper"],
                "param_count": count_params(nfn_cifar_model),
            }
            logger.info(f"NFN CIFAR rho={nfn_res_cifar['rho']:.4f}")

            logger.info("\n[CIFAR-10] Training DeepSets from scratch...")
            element_dim_cifar = max(int(np.prod(s)) for s in weight_shapes_cifar)
            ds_encoder_cifar, phi_hidden_cifar, n_params_cifar = grid_search_deep_sets(
                element_dim=element_dim_cifar,
                phi_hidden_candidates=cfg.phi_hidden_candidates,
                rho_hidden=cfg.rho_hidden,
                embed_dim=cfg.embed_dim,
                target_min=cfg.target_params_min,
                target_max=cfg.target_params_max,
            )
            ds_model_cifar = DeepSetsWithHead(ds_encoder_cifar, cfg.embed_dim).to(device)
            ds_model_cifar, ds_hist_cifar = train_deep_sets(
                ds_model_cifar, cifar_flat_train, cifar_flat_val,
                cfg, device, "best_deep_sets_cifar.pt", weight_shapes_cifar
            )
            ds_res_cifar = evaluate_deep_sets_encoder(
                ds_model_cifar, cifar_flat_test, device, weight_shapes_cifar, cfg.n_resamples
            )
            results["encoders"]["deep_sets"]["cifar10"] = {
                "rho": ds_res_cifar["rho"],
                "ci_lower": ds_res_cifar["ci_lower"],
                "ci_upper": ds_res_cifar["ci_upper"],
                "param_count": n_params_cifar,
            }
            results["training_metadata"]["deep_sets_cifar"] = {
                "phi_hidden": phi_hidden_cifar, "param_count": n_params_cifar
            }

            # CIFAR delta_rho
            delta_cifar, ci_lower_cifar, ci_upper_cifar = compute_delta_rho_ci(
                nfn_res_cifar["preds"], flat_res_cifar["preds"],
                flat_res_cifar["labels"], cfg.n_resamples
            )
            results["delta_metrics"]["delta_rho_cifar"] = delta_cifar
            results["delta_metrics"]["ci_lower_cifar"] = ci_lower_cifar
            results["delta_metrics"]["ci_upper_cifar"] = ci_upper_cifar

        except Exception as e:
            logger.warning(f"CIFAR-10 processing failed: {e}. Continuing with MNIST-CNN only.")
            cifar_available = False

    # ─────────────────────────────────────────────────────────
    # Delta-rho CI (MNIST-CNN)
    # ─────────────────────────────────────────────────────────
    logger.info("\nComputing delta_rho CI (MNIST-CNN)...")
    delta_mnist, ci_lower_mnist, ci_upper_mnist = compute_delta_rho_ci(
        nfn_res_mnist["preds"], flat_res_mnist["preds"],
        flat_res_mnist["labels"], cfg.n_resamples
    )
    results["delta_metrics"]["delta_rho_mnist"] = delta_mnist
    results["delta_metrics"]["ci_lower_mnist"] = ci_lower_mnist
    results["delta_metrics"]["ci_upper_mnist"] = ci_upper_mnist

    # ─────────────────────────────────────────────────────────
    # Tier analysis (P3) on MNIST-CNN test set
    # ─────────────────────────────────────────────────────────
    logger.info("\nComputing tier analysis (P3)...")
    tier_res = compute_tier_analysis(
        flat_preds=flat_res_mnist["preds"],
        nfn_preds=nfn_res_mnist["preds"],
        deep_sets_preds=ds_res_mnist["preds"],
        labels=flat_res_mnist["labels"],
    )
    results["tier_analysis"] = tier_res

    # ─────────────────────────────────────────────────────────
    # Gate check (P1, P2)
    # ─────────────────────────────────────────────────────────
    logger.info("\nChecking gates (P1, P2)...")
    p1_pass, p2_pass = check_hm3_gate(results)
    results["gate_results"] = {
        "p1_pass": p1_pass,
        "p2_pass": p2_pass,
        "p3_tier_analysis": tier_res,
    }

    # ─────────────────────────────────────────────────────────
    # Visualizations
    # ─────────────────────────────────────────────────────────
    logger.info("\nGenerating figures...")
    try:
        plot_rho_comparison(results, cfg.figures_dir)
        plot_symmetry_spectrum(results, cfg.figures_dir)
        plot_tier_delta_rho(tier_res, cfg.figures_dir)

        # Bootstrap distribution for MNIST delta_rho
        from scipy.stats import spearmanr as _spr
        rng = np.random.default_rng(cfg.seed)
        n = len(flat_res_mnist["labels"])
        boot_deltas = []
        for _ in range(cfg.n_resamples):
            idx = rng.integers(0, n, size=n)
            d = (_spr(flat_res_mnist["labels"][idx], nfn_res_mnist["preds"][idx]).statistic
                 - _spr(flat_res_mnist["labels"][idx], flat_res_mnist["preds"][idx]).statistic)
            if not np.isnan(d):
                boot_deltas.append(d)
        plot_bootstrap_distribution(np.array(boot_deltas),
                                     (delta_mnist, ci_lower_mnist, ci_upper_mnist),
                                     cfg.figures_dir)
        if cifar_available:
            plot_cross_zoo_consistency(results, cfg.figures_dir)
    except Exception as e:
        logger.warning(f"Visualization error (non-fatal): {e}")

    # ─────────────────────────────────────────────────────────
    # Save results
    # ─────────────────────────────────────────────────────────
    save_results(results, cfg)

    # ─────────────────────────────────────────────────────────
    # Summary
    # ─────────────────────────────────────────────────────────
    logger.info("\n" + "=" * 60)
    logger.info("EXPERIMENT COMPLETE")
    logger.info("=" * 60)
    logger.info(f"FlatMLP MNIST rho:  {results['encoders']['flat_mlp']['mnist_cnn'].get('rho', 'N/A'):.4f}")
    logger.info(f"DeepSets MNIST rho: {results['encoders']['deep_sets']['mnist_cnn'].get('rho', 'N/A'):.4f}")
    logger.info(f"NFN MNIST rho:      {results['encoders']['nfn']['mnist_cnn'].get('rho', 'N/A'):.4f}")
    logger.info(f"delta_rho (MNIST):  {delta_mnist:.4f} (95% CI [{ci_lower_mnist:.4f}, {ci_upper_mnist:.4f}])")
    logger.info(f"Gate P1 (SHOULD_WORK): {'PASS' if p1_pass else 'FAIL'}")
    logger.info(f"Gate P2 (ordering):    {'PASS' if p2_pass else 'FAIL'}")
    logger.info("=" * 60)

    return results


if __name__ == "__main__":
    main()
