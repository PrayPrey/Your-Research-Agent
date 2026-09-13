"""Main experiment orchestration script for H-E1.

Verifies:
  1. BN-free architecture in Schurholt MNIST-CNN zoo
  2. Non-trivial proportion of permutation-orbit candidate pairs (>5%)

Gate: PASS if bn_free=True AND orbit_proportion > 0.05
"""
from pathlib import Path
from typing import Any, Dict

import numpy as np

from config import ExperimentConfig
from utils import ensure_dirs, save_results_yaml, set_seed, setup_logging
from data_loader import load_zoo_checkpoints
from bn_verify import verify_zoo_bn_free
from weight_analysis import stratified_pair_sample, flatten_weights
from orbit_statistics import compute_orbit_statistics, evaluate_gate, per_decile_proportions
from visualization import generate_all_figures


def main(cfg: ExperimentConfig = None) -> Dict[str, Any]:
    if cfg is None:
        cfg = ExperimentConfig()

    logger = setup_logging()
    set_seed(cfg.seed)
    ensure_dirs(cfg)

    logger.info("=" * 60)
    logger.info("H-E1: Permutation Orbit Non-Triviality Analysis")
    logger.info("=" * 60)

    # Step 1: Load zoo checkpoints
    logger.info("Step 1: Loading model zoo checkpoints...")
    checkpoints = load_zoo_checkpoints(cfg)
    logger.info(f"  Loaded {len(checkpoints)} checkpoints")

    # Step 2: BN-free verification
    logger.info("Step 2: Verifying BN-free architecture...")
    bn_free = verify_zoo_bn_free(checkpoints, cfg.bn_verify_sample_size, cfg.seed)
    logger.info(f"  BN-free: {bn_free}")

    # Step 3: Stratified pair sampling
    logger.info("Step 3: Sampling stratified model pairs...")
    pairs = stratified_pair_sample(
        checkpoints, cfg.n_per_decile, cfg.acc_threshold, cfg.seed
    )
    logger.info(f"  Sampled {len(pairs)} pairs")

    # Step 4: Compute orbit statistics
    logger.info("Step 4: Computing orbit statistics...")
    distances, orbit_proportion = compute_orbit_statistics(pairs, cfg.cosine_dist_threshold)
    logger.info(f"  Orbit proportion: {orbit_proportion:.4f}")

    # Step 5: Per-decile proportions
    per_decile = per_decile_proportions(distances)

    # Step 6: Gate evaluation
    gate_result = evaluate_gate(bn_free, orbit_proportion, cfg.orbit_proportion_gate)

    # Step 7: Generate figures
    logger.info("Step 7: Generating figures...")
    try:
        generate_all_figures(distances, pairs, orbit_proportion, per_decile, cfg)
        logger.info(f"  Figures saved to {cfg.figures_dir}")
    except Exception as e:
        logger.warning(f"  Figure generation failed: {e}")

    # Step 8: Compile results
    cosine_dists = [d["cosine_dist"] for d in distances]
    results = {
        "gate": gate_result,
        "statistics": {
            "mean_cosine_dist": float(np.mean(cosine_dists)) if cosine_dists else 0.0,
            "std_cosine_dist": float(np.std(cosine_dists)) if cosine_dists else 0.0,
            "n_pairs": len(pairs),
            "n_checkpoints": len(checkpoints),
            "per_decile_proportions": {str(k): float(v) for k, v in per_decile.items()},
        },
        "metadata": {
            "hypothesis_id": "h-e1",
            "date": "2026-05-05",
            "seed": cfg.seed,
            "zoo_name": cfg.zoo_name,
            "cosine_dist_threshold": cfg.cosine_dist_threshold,
            "orbit_proportion_gate": cfg.orbit_proportion_gate,
            "acc_threshold": cfg.acc_threshold,
        },
    }

    # Step 9: Save results
    results_path = cfg.results_dir / "h_e1_results.yaml"
    save_results_yaml(results, results_path)
    logger.info(f"Results saved to {results_path}")

    # Step 10: Print gate summary
    print("")
    print("=" * 50)
    print(f"H-E1 Gate: {gate_result['message']}")
    print(f"  BN-free: {gate_result['bn_free']}")
    print(f"  Orbit proportion: {gate_result['orbit_proportion']:.3f} (threshold: >{gate_result['threshold']})")
    print("=" * 50)

    print("EXPERIMENT COMPLETE")
    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="H-E1 Experiment")
    parser.add_argument("--data-dir", default="./data/model_zoo", help="Model zoo data directory")
    parser.add_argument("--results-dir", default="./results", help="Results output directory")
    parser.add_argument("--figures-dir", default="./figures", help="Figures output directory")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    cfg = ExperimentConfig(
        data_dir=Path(args.data_dir),
        results_dir=Path(args.results_dir),
        figures_dir=Path(args.figures_dir),
        seed=args.seed,
    )
    main(cfg)
