"""CLI entry point for h-e1 domain exposure trajectory pipeline."""
import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np

# Add code dir to path so src imports work
CODE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(CODE_DIR))

from src.data.loader import build_checkpoint_steps, get_dataset, MODEL_SIZES, TOKENS_PER_STEP, SEQ_LEN
from src.data.domain_lookup import PILE_DOMAINS, get_or_build_domain_lookup
from src.compute.trajectories import compute_domain_exposure_trajectories
from src.analysis.stats import compute_variance_stats, compute_spearman_matrix, check_gate
from src.visualization.figures import (
    plot_gate_metrics, plot_trajectories, plot_variance_heatmap, plot_spearman_matrix
)

POC_SIZES = ["70m", "1b", "6.9b"]


def run_all_model_sizes(
    idxmap_prefix: str,
    doc_to_domain: dict,
    checkpoint_steps: list,
    domain_names: list,
    model_sizes: list,
    output_dir: Path,
) -> dict:
    """Process each model size; save .npy; return all trajectories.
    # ponytail: single shared index map; if per-size maps exist, parameterize prefix
    """
    results = {}
    dataset = None

    for model_size in model_sizes:
        logging.info(f"Processing model size: {model_size}")

        if dataset is None:
            try:
                dataset = get_dataset(idxmap_prefix)
                logging.info(f"Loaded MMapIndexedDataset from {idxmap_prefix}")
            except Exception as e:
                logging.error(f"Failed to load dataset from {idxmap_prefix}: {e}")
                continue

        try:
            traj = compute_domain_exposure_trajectories(
                dataset, doc_to_domain, checkpoint_steps, domain_names
            )
            out_path = output_dir / f"trajectories_{model_size}.npy"
            np.save(out_path, traj)
            logging.info(f"Saved {out_path}")
            results[model_size] = traj
        except Exception as e:
            logging.warning(f"Skipping {model_size}: {e}")

    return results


def main():
    parser = argparse.ArgumentParser(description="h-e1: Pythia domain exposure trajectories")
    parser.add_argument("--idxmap-prefix", type=str,
                        help="Path prefix for unsharded index map (no .bin/.idx extension)")
    parser.add_argument("--domain-cache", type=str, default="data/doc_to_domain.pkl",
                        help="Path to doc_to_domain.pkl cache")
    parser.add_argument("--figures-dir", type=str, default="../../figures",
                        help="Output dir for figures")
    parser.add_argument("--output-dir", type=str, default="outputs",
                        help="Output dir for trajectory .npy files")
    parser.add_argument("--poc", action="store_true",
                        help="Run 3-size subset [70m, 1b, 6.9b] only")
    parser.add_argument("--build-lookup", action="store_true",
                        help="Build domain lookup and exit")
    parser.add_argument("--max-lookup-docs", type=int, default=None,
                        help="Limit docs for partial domain lookup build (PoC)")
    parser.add_argument("--model-sizes", nargs="+", default=None,
                        help="Override model size list")
    parser.add_argument("--results-json", type=str, default="outputs/results.json",
                        help="Path to save results JSON")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("experiment.log"),
        ],
    )

    domain_cache = Path(args.domain_cache)
    figures_dir = Path(args.figures_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    # Build domain lookup only
    if args.build_lookup:
        logging.info("Building domain lookup...")
        get_or_build_domain_lookup(domain_cache, force_rebuild=True, max_docs=args.max_lookup_docs)
        logging.info("Domain lookup built. Exiting.")
        return

    # Load domain lookup
    logging.info("Loading domain lookup...")
    doc_to_domain = get_or_build_domain_lookup(domain_cache, max_docs=args.max_lookup_docs)
    logging.info(f"Loaded {len(doc_to_domain)} doc->domain mappings")

    domain_names = PILE_DOMAINS
    checkpoint_steps = build_checkpoint_steps()
    logging.info(f"Checkpoint steps: {len(checkpoint_steps)} (first 5: {checkpoint_steps[:5]})")

    # Select model sizes
    if args.model_sizes:
        model_sizes = args.model_sizes
    elif args.poc:
        model_sizes = POC_SIZES
    else:
        model_sizes = MODEL_SIZES

    logging.info(f"Model sizes to process: {model_sizes}")

    if not args.idxmap_prefix:
        parser.error("--idxmap-prefix is required (unless --build-lookup)")

    # Compute trajectories for all model sizes
    all_trajectories = run_all_model_sizes(
        idxmap_prefix=args.idxmap_prefix,
        doc_to_domain=doc_to_domain,
        checkpoint_steps=checkpoint_steps,
        domain_names=domain_names,
        model_sizes=model_sizes,
        output_dir=output_dir,
    )

    if not all_trajectories:
        logging.error("No trajectories computed. Check idxmap_prefix and domain cache.")
        sys.exit(1)

    # Stats
    all_stats = {}
    all_stds = {}
    for size, traj in all_trajectories.items():
        stats = compute_variance_stats(traj)
        all_stats[size] = stats
        all_stds[size] = stats["per_domain_std"]
        logging.info(
            f"[{size}] n_domains_passing={stats['n_domains_passing']}, "
            f"max_std={stats['max_std']:.6f}, gate_passed={stats['gate_passed']}"
        )

    # Gate check (PoC: >=2 of 3 sizes; full: >=8 of 16)
    poc_mode = args.poc or (len(model_sizes) <= 3)
    gate_passed = check_gate(all_stats, min_domains=10, min_model_sizes=2 if poc_mode else 8)
    logging.info(f"GATE RESULT: {'PASSED' if gate_passed else 'FAILED'}")

    # Save results JSON
    results_path = Path(args.results_json)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results = {
        "gate_passed": gate_passed,
        "poc_mode": poc_mode,
        "model_sizes_processed": list(all_trajectories.keys()),
        "per_model_stats": {
            size: {
                "n_domains_passing": s["n_domains_passing"],
                "gate_passed": s["gate_passed"],
                "max_std": float(s["max_std"]),
                "min_std": float(s["min_std"]),
                "mean_std": float(s["mean_std"]),
                "per_domain_std": s["per_domain_std"].tolist(),
                "threshold_sensitivity": {str(k): v for k, v in s["threshold_sensitivity"].items()},
            }
            for size, s in all_stats.items()
        },
        "domain_names": domain_names,
        "n_checkpoints": len(checkpoint_steps),
        "gate_criteria": {
            "min_domains_passing": 10,
            "min_model_sizes": 2 if poc_mode else 8,
            "threshold": 0.001,
        },
    }

    if len(all_stds) > 1:
        rho_matrix, sizes_ordered = compute_spearman_matrix(all_stds)
        avg_rho = float(rho_matrix[np.triu_indices(len(sizes_ordered), k=1)].mean())
        results["avg_spearman_rho"] = avg_rho
        logging.info(f"Average Spearman rho across model sizes: {avg_rho:.4f}")

    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    logging.info(f"Results saved to {results_path}")

    # Figures
    first_size = list(all_trajectories.keys())[0]
    first_traj = all_trajectories[first_size]
    first_stats = all_stats[first_size]

    plot_gate_metrics(first_stats["per_domain_std"], domain_names,
                      figures_dir / "gate_metrics.png")
    plot_trajectories(first_traj, domain_names, checkpoint_steps,
                      figures_dir / "trajectories.png")

    if len(all_stds) > 1:
        plot_variance_heatmap(all_stds, domain_names, figures_dir / "variance_heatmap.png")
        rho_matrix, sizes_ordered = compute_spearman_matrix(all_stds)
        plot_spearman_matrix(rho_matrix, sizes_ordered, figures_dir / "spearman_matrix.png")

    logging.info(f"Figures saved to {figures_dir}")
    logging.info("=" * 60)
    logging.info(f"h-e1 GATE: {'PASSED' if gate_passed else 'FAILED'}")
    logging.info("=" * 60)


if __name__ == "__main__":
    main()
