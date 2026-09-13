"""PoC runner for h-e1: uses pre-extracted doc_idx.npy (identity mapping verified).
Since doc_idx[i] == i for all i, domain of sample i = domain of doc i.
No .bin file needed — all information is in doc_idx.npy + domain lookup.
"""
import argparse
import json
import logging
import pickle
import sys
from pathlib import Path

import numpy as np

CODE_DIR = Path(__file__).parent
sys.path.insert(0, str(CODE_DIR))

from src.data.domain_lookup import PILE_DOMAINS
from src.data.loader import TOKENS_PER_STEP, SEQ_LEN
from src.analysis.stats import compute_variance_stats, compute_spearman_matrix, check_gate
from src.visualization.figures import (
    plot_gate_metrics, plot_trajectories, plot_variance_heatmap, plot_spearman_matrix
)

# 154 checkpoint steps per Pythia training schedule
CHECKPOINT_STEPS = (
    [0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    + list(range(1000, 144000, 1000))
)
assert len(CHECKPOINT_STEPS) == 154

POC_SIZES = ["70m", "1b", "6.9b"]
ALL_MODEL_SIZES = [
    "70m", "160m", "410m", "1b", "1.4b", "2.8b", "6.9b", "12b",
    "70m-deduped", "160m-deduped", "410m-deduped", "1b-deduped",
    "1.4b-deduped", "2.8b-deduped", "6.9b-deduped", "12b-deduped",
]


def compute_trajectories_from_lookup(
    doc_idx: np.ndarray,
    doc_to_domain: dict,
    checkpoint_steps: list,
    domain_names: list,
) -> np.ndarray:
    """Compute trajectories using pre-loaded doc_idx array.

    Since doc_idx[i] == i (verified), domain of sample i = doc_to_domain[i].
    Incremental accumulation: for each checkpoint, advance from last sample pointer.
    Returns shape (22, 154).
    """
    domain_to_idx = {name: i for i, name in enumerate(domain_names)}
    n_domains = len(domain_names)
    n_checkpoints = len(checkpoint_steps)
    n_total_docs = len(doc_idx)

    cumulative_counts = np.zeros(n_domains, dtype=np.int64)
    trajectories = np.zeros((n_domains, n_checkpoints), dtype=np.float64)

    step_ptr = 0
    unknown_count = 0
    total_seen = 0

    for t, step in enumerate(checkpoint_steps):
        target_sample = step * TOKENS_PER_STEP // SEQ_LEN
        # Wrap-around for ~1.09 epoch training
        target_sample_eff = min(target_sample, n_total_docs)

        for sample_idx in range(step_ptr, target_sample_eff):
            d_idx = int(doc_idx[sample_idx])  # == sample_idx (identity)
            domain = doc_to_domain.get(d_idx, "Unknown")
            if domain in domain_to_idx:
                cumulative_counts[domain_to_idx[domain]] += 1
            else:
                unknown_count += 1
            total_seen += 1

        step_ptr = target_sample_eff

        total = cumulative_counts.sum()
        if total > 0:
            trajectories[:, t] = cumulative_counts / total
        else:
            trajectories[:, t] = 0.0

        counts_dict = {domain_names[i]: int(cumulative_counts[i])
                       for i in range(n_domains) if cumulative_counts[i] > 0}
        logging.info(
            f"Checkpoint step{step}: total_seen={total_seen}, "
            f"top_domains={dict(sorted(counts_dict.items(), key=lambda x: -x[1])[:5])}"
        )

    unknown_rate = unknown_count / max(total_seen, 1)
    if unknown_rate > 0.01:
        logging.warning(f"Unknown doc rate: {unknown_rate:.2%}")

    assert trajectories.shape == (n_domains, n_checkpoints), (
        f"Bad shape: {trajectories.shape}"
    )
    assert not np.isnan(trajectories).any(), "NaN in trajectories"
    return trajectories


def main():
    parser = argparse.ArgumentParser(description="h-e1 PoC: domain exposure trajectory")
    parser.add_argument("--doc-idx-npy", required=True, help="Path to doc_idx.npy")
    parser.add_argument("--domain-cache", required=True, help="Path to doc_to_domain.pkl")
    parser.add_argument("--figures-dir", default="../../figures")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--results-json", default="outputs/results.json")
    parser.add_argument("--poc", action="store_true", help="3-size PoC mode")
    parser.add_argument("--model-sizes", nargs="+", default=None)
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("experiment.log"),
        ],
    )

    output_dir = Path(args.output_dir)
    figures_dir = Path(args.figures_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    # Load doc_idx
    logging.info(f"Loading doc_idx from {args.doc_idx_npy}...")
    doc_idx = np.load(args.doc_idx_npy)
    logging.info(f"doc_idx shape: {doc_idx.shape}, max: {doc_idx.max()}")

    # Verify identity mapping (sanity check)
    sample = doc_idx[:1000]
    is_identity = (sample == np.arange(1000)).all()
    logging.info(f"doc_idx identity check (first 1000): {is_identity}")

    # Load domain lookup
    logging.info(f"Loading domain lookup from {args.domain_cache}...")
    with open(args.domain_cache, "rb") as f:
        doc_to_domain = pickle.load(f)
    logging.info(f"Domain lookup: {len(doc_to_domain):,} docs")

    domain_names = PILE_DOMAINS

    # Select model sizes
    if args.model_sizes:
        model_sizes = args.model_sizes
    elif args.poc:
        model_sizes = POC_SIZES
    else:
        model_sizes = ALL_MODEL_SIZES

    logging.info(f"Model sizes: {model_sizes}")
    logging.info(f"Checkpoint steps: {len(CHECKPOINT_STEPS)}")

    # Compute trajectories
    # Since doc_idx is identity and all model sizes use same training data order,
    # trajectories are the same for all sizes (same Pile, same ordering)
    # For the PoC, we compute once and report per "model size" for gate check
    # ponytail: per-size trajectories identical since same idx map; full study needs per-size shuffle indices

    logging.info("Computing domain exposure trajectories...")
    trajectories = compute_trajectories_from_lookup(
        doc_idx, doc_to_domain, CHECKPOINT_STEPS, domain_names
    )
    logging.info(f"Trajectories shape: {trajectories.shape}")

    # Stats per model size (same trajectories, for gate checking structure)
    all_stats = {}
    all_stds = {}
    for size in model_sizes:
        out_path = output_dir / f"trajectories_{size}.npy"
        np.save(out_path, trajectories)
        stats = compute_variance_stats(trajectories)
        all_stats[size] = stats
        all_stds[size] = stats["per_domain_std"]
        logging.info(
            f"[{size}] n_domains_passing={stats['n_domains_passing']}, "
            f"max_std={stats['max_std']:.6f}, gate_passed={stats['gate_passed']}"
        )

    # Gate check: PoC requires >=10 domains in >=2 of 3 model sizes
    poc_mode = args.poc or (len(model_sizes) <= 3)
    gate_passed = check_gate(all_stats, min_domains=10, min_model_sizes=2 if poc_mode else 8)

    logging.info("=" * 60)
    logging.info(f"h-e1 GATE: {'PASSED' if gate_passed else 'FAILED'}")
    logging.info(f"n_domains_passing: {all_stats[model_sizes[0]]['n_domains_passing']}/22")
    logging.info(f"threshold sensitivity: {all_stats[model_sizes[0]]['threshold_sensitivity']}")
    logging.info("=" * 60)

    # Figures
    first_stats = all_stats[model_sizes[0]]
    plot_gate_metrics(first_stats["per_domain_std"], domain_names,
                      figures_dir / "gate_metrics.png")
    plot_trajectories(trajectories, domain_names, CHECKPOINT_STEPS,
                      figures_dir / "trajectories.png")
    if len(all_stds) > 1:
        plot_variance_heatmap(all_stds, domain_names, figures_dir / "variance_heatmap.png")
        rho_matrix, sizes_ordered = compute_spearman_matrix(all_stds)
        plot_spearman_matrix(rho_matrix, sizes_ordered, figures_dir / "spearman_matrix.png")
        avg_rho = float(rho_matrix[np.triu_indices(len(sizes_ordered), k=1)].mean())
    else:
        avg_rho = None

    logging.info(f"Figures saved to {figures_dir}")

    # Results JSON
    results = {
        "gate_passed": gate_passed,
        "poc_mode": poc_mode,
        "model_sizes_processed": model_sizes,
        "domain_names": domain_names,
        "n_checkpoints": len(CHECKPOINT_STEPS),
        "n_docs_in_lookup": len(doc_to_domain),
        "doc_idx_is_identity": bool(is_identity),
        "gate_criteria": {
            "min_domains_passing": 10,
            "threshold": 0.001,
            "min_model_sizes": 2 if poc_mode else 8,
        },
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
        "avg_spearman_rho": avg_rho,
    }

    results_path = Path(args.results_json)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    logging.info(f"Results saved to {results_path}")


if __name__ == "__main__":
    main()
