"""Main experiment runner for H-M1.

Full pipeline:
1. Parse CLI args → override ExperimentConfig
2. Sanity check (optional)
3. Multi-seed training: 6 encoders x 3 seeds = 18 runs
4. Evaluate all encoders (Delta_rho, Bootstrap, Holm correction)
5. Compute mediation Delta_R2
6. Gate v2 check: Delta_rho < 0.02 AND Delta_R2 >= 0.10
7. Generate 5 figures
8. Write h-m1_results.json + gate_result.json
"""
import argparse
import datetime
import json
import logging
import os
import sys

# Set GPU before any CUDA imports
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE_DIR)

import numpy as np
import torch

from src.config import ENCODER_CONFIG, ExperimentConfig, GateConfig, VizConfig
from src.data_loader import get_dataloaders
from src.evaluate import (
    apply_stress_and_predict,
    compute_mediation_delta_r2,
    evaluate_all_encoders,
    evaluate_gate_condition_v2,
    summarize_encoder_stats,
    verify_mechanism_activated,
)
from src.models import NFTEquivariantEncoder, build_encoder
from src.train import load_checkpoint, run_all_training, run_sanity_check, set_seed
from src.visualize import generate_all_figures

LOG_PATH = os.path.join(CODE_DIR, "experiment.log")


def setup_logging(log_path: str = LOG_PATH) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(sys.stdout),
        ],
    )


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments. All flags override ExperimentConfig fields."""
    parser = argparse.ArgumentParser(description="H-M1: 6-Encoder Mechanism Analysis")
    parser.add_argument("--encoder", type=str, default=None,
                        help="Run single encoder only (default: all 6)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Run single seed only (default: all 3)")
    parser.add_argument("--data-path", type=str, default=None,
                        help="Override data_path")
    parser.add_argument("--device", type=str, default=None,
                        help="Override device (cuda or cpu)")
    parser.add_argument("--epochs", type=int, default=None,
                        help="Override n_epochs")
    parser.add_argument("--sanity-only", action="store_true",
                        help="Run only sanity check, skip training")
    parser.add_argument("--skip-sanity", action="store_true",
                        help="Skip sanity check, run training directly")
    return parser.parse_args()


def build_cfg_from_args(args: argparse.Namespace) -> ExperimentConfig:
    """Build ExperimentConfig with CLI overrides."""
    cfg = ExperimentConfig()

    if args.encoder is not None:
        cfg.encoder_names = [args.encoder]
    if args.seed is not None:
        cfg.seeds = [args.seed]
    if args.data_path is not None:
        cfg.data_path = args.data_path
    if args.device is not None:
        cfg.device = args.device
    if args.epochs is not None:
        cfg.n_epochs = args.epochs
    if args.sanity_only:
        cfg.run_training = False
        cfg.run_evaluation = False
        cfg.run_visualization = False
    if args.skip_sanity:
        cfg.run_sanity_check = False

    return cfg


def main() -> dict:
    args = parse_args()
    setup_logging()
    logger = logging.getLogger(__name__)
    cfg = build_cfg_from_args(args)

    logger.info("=" * 70)
    logger.info("H-M1 Experiment: 6-Encoder Mechanism Analysis (NFT equivariance)")
    logger.info(f"Started at: {datetime.datetime.now().isoformat()}")
    logger.info(f"Encoders: {cfg.encoder_names}")
    logger.info(f"Seeds: {cfg.seeds}")
    logger.info(f"Epochs: {cfg.n_epochs}")
    logger.info("=" * 70)

    os.makedirs(cfg.results_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)
    os.makedirs(cfg.checkpoint_dir, exist_ok=True)

    # Determine device
    if cfg.device == "cuda" and torch.cuda.is_available():
        device = torch.device("cuda")
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device("cpu")
        logger.info("Using CPU")
        cfg.device = "cpu"

    # Resolve data path
    data_path = cfg.data_path
    if not os.path.isabs(data_path):
        data_path = os.path.join(CODE_DIR, data_path)

    if not os.path.exists(data_path):
        # Try shared cache
        cache_path = "/home/anonymous/YouRA_results_new_4/TEST_wsl/docs/youra_research/20260316_wsl/.data_cache/datasets/unterthiner_mnist_zoo/zoo_enriched.pkl"
        if os.path.exists(cache_path):
            data_path = cache_path
            logger.info(f"Using shared cache: {data_path}")
        else:
            raise FileNotFoundError(f"Data not found at {data_path}")

    # Load data
    logger.info(f"Loading data from {data_path}")
    flat_train_loader, flat_test_loader, nft_train_loader, nft_test_loader = get_dataloaders(
        data_path, batch_size=cfg.batch_size, train_ratio=0.8, seed=42
    )

    # Infer dimensions
    flat_batch = next(iter(flat_train_loader))
    flat_input_dim = flat_batch[0].shape[1]
    nft_batch = next(iter(nft_train_loader))
    layer_fan_ins = [wm.shape[2] for wm in nft_batch[0]]
    logger.info(f"flat_input_dim={flat_input_dim}, layer_fan_ins={layer_fan_ins}")

    # --- Sanity check ---
    if cfg.run_sanity_check:
        logger.info("Running sanity check...")
        run_sanity_check(
            flat_train_loader, nft_train_loader, cfg,
            flat_input_dim, layer_fan_ins,
            n_samples=cfg.sanity_n_samples,
        )
        if not cfg.run_training:
            logger.info("--sanity-only: stopping after sanity check.")
            return {}

    # --- Training ---
    if cfg.run_training:
        logger.info("Starting multi-seed training (6 encoders x 3 seeds = 18 runs)...")
        training_results = run_all_training(
            cfg, flat_train_loader, nft_train_loader, flat_input_dim, layer_fan_ins
        )
    else:
        # Try to load existing training results
        tr_path = os.path.join(cfg.results_dir, "training_results.json")
        if os.path.exists(tr_path):
            with open(tr_path) as f:
                training_results = json.load(f)
            logger.info(f"Loaded existing training results: {len(training_results)} runs")
        else:
            logger.error("No training results found and run_training=False")
            return {}

    # --- Evaluation ---
    if cfg.run_evaluation:
        logger.info("Evaluating all encoders...")
        eval_df = evaluate_all_encoders(
            training_results, cfg,
            flat_test_loader, nft_test_loader,
            flat_input_dim, layer_fan_ins,
        )

        delta_r2 = compute_mediation_delta_r2(eval_df)
        logger.info(f"Mediation Delta_R2 = {delta_r2:.4f}")

        encoder_stats = summarize_encoder_stats(eval_df)

        gate_result = evaluate_gate_condition_v2(
            eval_df, delta_r2, cfg,
            gate_cfg=GateConfig(),
            results_dir=cfg.results_dir,
        )
        logger.info(f"Gate result: passed={gate_result['passed']}")
        logger.info(f"  NFT-base Delta_rho = {gate_result['nft_delta_rho']:.6f} (threshold < 0.02)")
        logger.info(f"  Delta_R2           = {gate_result['delta_r2']:.4f} (threshold >= 0.10)")

        all_pass, indicators = verify_mechanism_activated(eval_df, delta_r2)
        logger.info(f"Mechanism verification: all_pass={all_pass}")

        # Collect bootstrap data for fig5
        bootstrap_data = _collect_bootstrap_data(
            training_results, cfg, flat_test_loader, nft_test_loader,
            flat_input_dim, layer_fan_ins, device
        )

        # --- Visualization ---
        if cfg.run_visualization:
            logger.info("Generating figures...")
            generate_all_figures(
                eval_df, delta_r2, encoder_stats, bootstrap_data, VizConfig()
            )

        # Write full results JSON
        results_path = os.path.join(cfg.results_dir, "h-m1_results.json")
        json_results = {
            "hypothesis_id": "h-m1",
            "timestamp": datetime.datetime.now().isoformat(),
            "gate_result": gate_result,
            "encoder_stats": encoder_stats,
            "delta_r2": delta_r2,
            "mechanism_verified": all_pass,
            "mechanism_indicators": indicators,
            "config": {
                "n_epochs": cfg.n_epochs,
                "seeds": cfg.seeds,
                "encoder_names": cfg.encoder_names,
                "device": str(device),
                "flat_input_dim": flat_input_dim,
                "layer_fan_ins": layer_fan_ins,
                "severity_levels": cfg.severity_levels,
                "n_bootstrap": cfg.n_bootstrap,
            },
        }
        with open(results_path, "w") as f:
            json.dump(json_results, f, indent=2)
        logger.info(f"Results written: {results_path}")

    else:
        json_results = {}

    logger.info("=" * 70)
    logger.info("H-M1 EXPERIMENT COMPLETE")
    if cfg.run_evaluation:
        logger.info(f"Gate PASS: {gate_result['passed']}")
        logger.info(f"  NFT-base Delta_rho = {gate_result['nft_delta_rho']:.6f}")
        logger.info(f"  Mediation Delta_R2 = {gate_result['delta_r2']:.4f}")
    logger.info("=" * 70)

    return json_results


def _collect_bootstrap_data(
    training_results, cfg, flat_test_loader, nft_test_loader,
    flat_input_dim, layer_fan_ins, device
) -> dict:
    """Collect bootstrap samples for NFT-base and flat-MLP for fig5."""
    from src.evaluate import apply_stress_and_predict
    from scipy.stats import spearmanr

    bootstrap_data = {"nft_bootstrap": np.array([]), "flat_bootstrap": np.array([])}

    try:
        for enc_name, key in [("NFT-base", "nft_bootstrap"), ("flat-MLP", "flat_bootstrap")]:
            ckpt_paths = [
                r["checkpoint_path"] for r in training_results
                if r.get("encoder") == enc_name and r.get("checkpoint_path") and
                os.path.exists(r.get("checkpoint_path", ""))
            ]
            if not ckpt_paths:
                continue

            enc_cfg = ENCODER_CONFIG[enc_name]
            model_type = enc_cfg["model_type"]
            test_loader = nft_test_loader if model_type == "nft" else flat_test_loader

            model = build_encoder(enc_name, flat_input_dim, layer_fan_ins).to(device)
            model = load_checkpoint(model, ckpt_paths[0], device)
            model.eval()

            rng = np.random.default_rng(42)
            preds_s0, labels = apply_stress_and_predict(model, test_loader, 0.0, device, model_type)
            preds_s1, _ = apply_stress_and_predict(model, test_loader, 1.0, device, model_type)
            n = len(labels)

            bs_samples = np.empty(1000)  # Smaller for viz only
            for i in range(1000):
                idx = rng.integers(0, n, size=n)
                r0, _ = spearmanr(preds_s0[idx], labels[idx])
                r1, _ = spearmanr(preds_s1[idx], labels[idx])
                bs_samples[i] = r0 - r1

            bootstrap_data[key] = bs_samples
    except Exception as e:
        logging.getLogger(__name__).warning(f"Bootstrap data collection failed: {e}")

    return bootstrap_data


if __name__ == "__main__":
    main()
