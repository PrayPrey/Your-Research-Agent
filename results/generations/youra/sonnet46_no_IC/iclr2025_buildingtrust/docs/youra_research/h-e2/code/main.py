"""
H-E2 Orchestration: MST Minimum Evaluation Set + Bootstrap Topology Stability.
"""

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

import numpy as np

# H-E2 code dir first, then H-E1 code dir (order matters — h-e2 visualization shadows h-e1's)
_H_E2_CODE = os.path.dirname(os.path.abspath(__file__))
_H_E1_CODE = os.path.join(os.path.dirname(__file__), "../../h-e1/code")
sys.path.insert(0, os.path.abspath(_H_E1_CODE))
sys.path.insert(0, _H_E2_CODE)  # h-e2 takes priority for visualization/mst_analysis

from data_loader import DIMENSIONS, load_trustllm_scores, add_annotations
from mst_analysis import run_mst_analysis
from viz_h_e2 import visualize_all


@dataclass
class ExperimentConfig:
    h_e1_results_path: str = "../h-e1/experiment_results_phase3.json"
    out_dir: str = ".."
    n_bootstrap: int = 1000
    subsample_size: int = 14
    seed: int = 42
    gate_min_set_threshold: int = 4
    gate_stability_threshold: float = 0.90
    figure_dpi: int = 300
    dim_names: List[str] = field(default_factory=lambda: [
        "truthfulness", "safety", "fairness", "robustness", "privacy", "machine_ethics",
    ])


def check_gate(results: dict) -> bool:
    gate_primary = results["mst_min_set_size"] <= 4
    gate_secondary = results["bootstrap_topology_stability"] >= 0.90
    return gate_primary and gate_secondary


def serialize_results(results: dict, out_dir: str) -> None:
    h_e2_dir = os.path.join(out_dir, "h-e2")
    os.makedirs(h_e2_dir, exist_ok=True)
    out_path = os.path.join(h_e2_dir, "experiment_results_phase3.json")

    serializable = {}
    for k, v in results.items():
        if isinstance(v, list):
            serializable[k] = [
                list(item) if isinstance(item, (tuple, frozenset, set)) else item
                for item in v
            ]
        elif isinstance(v, dict):
            serializable[k] = {str(dk): dv for dk, dv in v.items()}
        elif isinstance(v, np.integer):
            serializable[k] = int(v)
        elif isinstance(v, np.floating):
            serializable[k] = float(v)
        elif isinstance(v, np.ndarray):
            serializable[k] = v.tolist()
        else:
            serializable[k] = v

    with open(out_path, "w") as f:
        json.dump(serializable, f, indent=2, default=str)
    return out_path


def run_experiment(cfg: ExperimentConfig) -> dict:
    h_e2_dir = os.path.join(cfg.out_dir, "h-e2")
    log_path = os.path.join(h_e2_dir, "experiment.log")
    figures_dir = os.path.join(h_e2_dir, "figures")
    os.makedirs(h_e2_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    log = logging.getLogger("h-e2")

    # Load H-E1 rho_partial from JSON
    log.info(f"Loading H-E1 results from {cfg.h_e1_results_path}")
    with open(cfg.h_e1_results_path) as f:
        h_e1 = json.load(f)

    # rho_partial key may be 'rho_partial' or 'rho_partial_matrix'
    rho_key = "rho_partial_matrix" if "rho_partial_matrix" in h_e1 else "rho_partial"
    rho_partial = np.array(h_e1[rho_key])
    log.info(f"rho_partial shape: {rho_partial.shape}")
    assert rho_partial.shape == (6, 6), f"Expected 6x6, got {rho_partial.shape}"

    # Load raw scores from H-E1 data source (data_loader)
    h_e1_code_dir = os.path.abspath(_H_E1_CODE)
    trustllm_results_dir = os.path.join(h_e1_code_dir, "TrustLLM", "results")
    log.info(f"Loading TrustLLM scores from {trustllm_results_dir}")
    scores_df = load_trustllm_scores(trustllm_results_dir)
    annotated_df = add_annotations(scores_df)

    raw_scores = scores_df[cfg.dim_names].values  # (16, 6)
    covariates = annotated_df[["log10_params", "is_RLHF"]].values  # (16, 2)
    log.info(f"raw_scores shape: {raw_scores.shape}, covariates shape: {covariates.shape}")

    # Run MST analysis
    log.info(f"Running MST analysis (n_boot={cfg.n_bootstrap}, subsample={cfg.subsample_size}, seed={cfg.seed})")
    results = run_mst_analysis(
        rho_partial=rho_partial,
        raw_scores=raw_scores,
        covariates=covariates,
        dim_names=cfg.dim_names,
        n_boot=cfg.n_bootstrap,
        subsample=cfg.subsample_size,
        seed=cfg.seed,
    )

    # Visualize
    log.info("Generating figures...")
    visualize_all(results, rho_partial, cfg.dim_names, figures_dir)

    # Serialize
    out_path = serialize_results(results, cfg.out_dir)
    log.info(f"Results saved to {out_path}")

    # Log summary
    gate_str = "PASS" if results["gate_passed"] else "FAIL"
    summary = (
        f"\n{'='*60}\n"
        f"H-E2 RESULTS\n"
        f"{'='*60}\n"
        f"MST min_set_size:          {results['mst_min_set_size']} (threshold ≤4) — {'PASS' if results['gate_primary_passed'] else 'FAIL'}\n"
        f"MST leaves:                {results['mst_leaves']}\n"
        f"MST min_set:               {results['mst_min_set']}\n"
        f"Bootstrap stability:       {results['bootstrap_topology_stability']:.4f} (threshold ≥0.90) — {'PASS' if results['gate_secondary_passed'] else 'FAIL'}\n"
        f"Raw MST min_set_size:      {results['raw_mst_min_set_size']}\n"
        f"GATE RESULT:               {gate_str}\n"
        f"{'='*60}\n"
    )
    print(summary)

    with open(log_path, "w") as f:
        f.write(summary)
        f.write("\nEdge frequencies:\n")
        for k, v in results["bootstrap_edge_frequencies"].items():
            f.write(f"  {k}: {v:.4f}\n")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-E2 MST Stability Analysis")
    parser.add_argument("--h-e1-results", default="../h-e1/experiment_results_phase3.json",
                        help="Path to h-e1 experiment_results_phase3.json")
    parser.add_argument("--out-dir", default="..", help="Output directory")
    parser.add_argument("--n-boot", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    cfg = ExperimentConfig(
        h_e1_results_path=args.h_e1_results,
        out_dir=args.out_dir,
        n_bootstrap=args.n_boot,
        seed=args.seed,
    )
    results = run_experiment(cfg)
    sys.exit(0 if results["gate_passed"] else 1)
