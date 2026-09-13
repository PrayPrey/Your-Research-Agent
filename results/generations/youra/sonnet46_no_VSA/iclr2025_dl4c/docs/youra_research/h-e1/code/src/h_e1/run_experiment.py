"""Full pipeline entry point for H-E1."""
import os
import sys
import json
import random
import logging
import argparse
import numpy as np
import torch

from .data_loader import load_all_corpora
from .embedder import encode_all_corpora
from .similarity import compute_similarity_matrix, evaluate_gate, verify_embeddings, SOURCES, BENCHMARKS
from .visualize import plot_heatmaps, plot_histograms, plot_tsne

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="H-E1: Code Embedding Distinctiveness Analysis")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-length-codebert", type=int, default=512)
    parser.add_argument("--max-length-minilm", type=int, default=256)
    parser.add_argument("--gate-threshold", type=float, default=0.95)
    parser.add_argument("--equal-mix-per-source", type=int, default=164)
    parser.add_argument("--figures-dir", type=str, default="docs/youra_research/h-e1/figures")
    parser.add_argument("--skip-tsne", action="store_true", default=False)
    parser.add_argument("--skip-histograms", action="store_true", default=False)
    parser.add_argument("--results-json", type=str, default=None)
    return parser.parse_args()


def main(
    batch_size: int = 32,
    device: str = "cuda",
    seed: int = 42,
    figures_dir: str = "docs/youra_research/h-e1/figures",
    skip_tsne: bool = False,
    skip_histograms: bool = False,
    results_json: str = None,
) -> dict:
    """Full pipeline: load -> embed -> similarity -> gate -> visualize -> log."""
    # Seed everything
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if device == "cuda" and not torch.cuda.is_available():
        logger.warning("CUDA unavailable, falling back to CPU")
        device = "cpu"
    logger.info(f"Using device: {device}")

    # Step 1: Load data
    logger.info("=== Step 1: Loading corpora ===")
    corpora = load_all_corpora(seed=seed)
    for name, texts in corpora.items():
        logger.info(f"  {name}: {len(texts)} texts")

    # Step 2: Embed
    logger.info("=== Step 2: Encoding all corpora ===")
    embeddings = encode_all_corpora(corpora, batch_size=batch_size, device=device)

    # Step 3: Similarity matrix
    logger.info("=== Step 3: Computing similarity matrices ===")
    sim_matrices = compute_similarity_matrix(embeddings)

    # Step 4: Gate evaluation
    gate_result = evaluate_gate(sim_matrices)

    # Step 5: Verify
    all_pass, checks = verify_embeddings(embeddings, sim_matrices)

    # Step 6: Visualize
    logger.info("=== Step 6: Generating visualizations ===")
    os.makedirs(figures_dir, exist_ok=True)
    plot_heatmaps(sim_matrices, figures_dir)
    if not skip_histograms:
        plot_histograms(embeddings, figures_dir)
    if not skip_tsne:
        plot_tsne(embeddings, figures_dir, encoder="codebert")

    # Step 7: Print summary table
    print("\n" + "=" * 70)
    print("H-E1: Code Embedding Distinctiveness — Results")
    print("=" * 70)
    for encoder, mat in sim_matrices.items():
        print(f"\n{encoder.upper()} Similarity Matrix (rows=sources, cols=benchmarks):")
        header = "  ".join(f"{b:<15}" for b in BENCHMARKS)
        print(f"  {'Source':<22} {header}")
        for i, src in enumerate(SOURCES):
            row = "  ".join(f"{mat[i, j]:.4f}         " for j in range(len(BENCHMARKS)))
            print(f"  {src:<22} {row}")

    status = "SATISFIED" if gate_result["gate_satisfied"] else "FAILED"
    print(f"\nGate (MUST_WORK): {status}")
    print(f"  threshold={gate_result['threshold']:.2f} | "
          f"min={gate_result['min_sim']:.4f} | "
          f"max={gate_result['max_sim']:.4f} | "
          f"mean={gate_result['mean_sim']:.4f} | "
          f"std={gate_result['std_sim']:.4f}")
    print(f"\nAll 16 values: {[f'{v:.4f}' for v in gate_result['all_values']]}")
    print("=" * 70)

    # Save results JSON
    if results_json is None:
        results_json = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "..", "experiment_results.json"
        )
        results_json = os.path.normpath(results_json)

    # Build corpus size info
    corpus_sizes = {name: len(texts) for name, texts in corpora.items()}
    sim_matrices_serializable = {
        enc: mat.tolist() for enc, mat in sim_matrices.items()
    }

    results = {
        "hypothesis_id": "h-e1",
        "status": "completed",
        "execution_mode": "auto",
        "gate": {
            "type": "MUST_WORK",
            "satisfied": gate_result["gate_satisfied"],
            "threshold": gate_result["threshold"],
            "result": status,
        },
        "metrics": {
            "gate_satisfied": gate_result["gate_satisfied"],
            "min_sim": gate_result["min_sim"],
            "max_sim": gate_result["max_sim"],
            "mean_sim": gate_result["mean_sim"],
            "std_sim": gate_result["std_sim"],
            "all_values": gate_result["all_values"],
        },
        "sim_matrices": sim_matrices_serializable,
        "sources": SOURCES,
        "benchmarks": BENCHMARKS,
        "corpus_sizes": corpus_sizes,
        "embedding_checks": checks,
        "config": {
            "batch_size": batch_size,
            "device": device,
            "seed": seed,
            "figures_dir": figures_dir,
        },
    }

    os.makedirs(os.path.dirname(os.path.abspath(results_json)), exist_ok=True)
    with open(results_json, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved to {results_json}")

    return gate_result


if __name__ == "__main__":
    args = parse_args()
    main(
        batch_size=args.batch_size,
        device=args.device,
        seed=args.seed,
        figures_dir=args.figures_dir,
        skip_tsne=args.skip_tsne,
        skip_histograms=args.skip_histograms,
        results_json=args.results_json,
    )
