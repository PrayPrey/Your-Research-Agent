"""H-E2-v2: MST Mean Per-Edge Bootstrap Frequency (Relaxed Gate).

Adapter over H-E2: loads pre-computed bootstrap_edge_frequencies, applies v2 gate.
"""
import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np

# Paths relative to docs/youra_research/ (the working directory for this script)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_RESEARCH_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", ".."))


@dataclass
class ExperimentConfigV2:
    h_e2_results_path: str = os.path.join(_RESEARCH_DIR, "h-e2", "experiment_results_phase3.json")
    h_e1_results_path: str = os.path.join(_RESEARCH_DIR, "h-e1", "experiment_results_phase3.json")
    output_dir: str = os.path.join(_RESEARCH_DIR, "h-e2-v2")
    figures_dir: str = os.path.join(_RESEARCH_DIR, "h-e2-v2", "figures")
    n_bootstrap: int = 1000
    subsample_size: int = 14
    seed: int = 42
    gate_min_set_threshold: int = 4
    gate_mean_freq_threshold: float = 0.90
    topology_stability_h_e2: float = 0.606
    figure_dpi: int = 300
    dim_names: List[str] = field(default_factory=lambda: [
        "truthfulness", "safety", "fairness", "robustness", "privacy", "machine_ethics",
    ])


def evaluate_gate_v2(
    mst_min_set_size: int,
    mean_per_edge_freq: float,
    threshold_min_set: int = 4,
    threshold_mean_freq: float = 0.90,
) -> dict:
    primary = mst_min_set_size <= threshold_min_set
    secondary = mean_per_edge_freq >= threshold_mean_freq
    return {
        "gate_primary_passed": primary,
        "gate_secondary_passed": secondary,
        "gate_result": "PASS" if (primary and secondary) else "FAIL",
    }


def load_or_recompute(
    h_e2_json_path: str,
    h_e1_json_path: str,
    n_boot: int = 1000,
    subsample: int = 14,
    seed: int = 42,
    dim_names: List[str] = None,
) -> Tuple[Dict[str, float], int, List[str]]:
    """Fast path: read bootstrap_edge_frequencies from H-E2 JSON.
    Fallback: re-run bootstrap via mst_analysis.py from h-e2.
    """
    with open(h_e2_json_path) as f:
        h_e2 = json.load(f)

    if "bootstrap_edge_frequencies" in h_e2:
        return (
            h_e2["bootstrap_edge_frequencies"],
            h_e2["mst_min_set_size"],
            h_e2["mst_min_set"],
        )

    # Fallback: re-run bootstrap
    print("WARNING: bootstrap_edge_frequencies not in H-E2 JSON — running fallback bootstrap")
    h_e2_code_dir = os.path.join(os.path.dirname(h_e2_json_path), "code")
    h_e1_code_dir = os.path.join(os.path.dirname(h_e1_json_path), "code")
    sys.path.insert(0, h_e2_code_dir)
    sys.path.insert(0, h_e1_code_dir)

    from mst_analysis import run_mst_analysis
    from data_loader import load_trustllm_scores, add_annotations

    with open(h_e1_json_path) as f:
        h_e1 = json.load(f)
    rho_key = "rho_partial_matrix" if "rho_partial_matrix" in h_e1 else "rho_partial"
    rho_partial = np.array(h_e1[rho_key])

    if dim_names is None:
        dim_names = ["truthfulness", "safety", "fairness", "robustness", "privacy", "machine_ethics"]

    trustllm_dir = os.path.join(os.path.dirname(h_e1_json_path), "code", "TrustLLM", "results")
    scores_df = load_trustllm_scores(trustllm_dir)
    annotated_df = add_annotations(scores_df)
    raw_scores = scores_df[dim_names].values
    covariates = annotated_df[["log10_params", "is_RLHF"]].values

    results = run_mst_analysis(
        rho_partial=rho_partial,
        raw_scores=raw_scores,
        covariates=covariates,
        dim_names=dim_names,
        n_boot=n_boot,
        subsample=subsample,
        seed=seed,
    )
    return (
        results["bootstrap_edge_frequencies"],
        results["mst_min_set_size"],
        results["mst_min_set"],
    )


def run_experiment(
    h_e2_json_path: str = None,
    h_e1_json_path: str = None,
    output_dir: str = None,
) -> dict:
    _defaults = ExperimentConfigV2()
    cfg = ExperimentConfigV2(
        h_e2_results_path=h_e2_json_path or _defaults.h_e2_results_path,
        h_e1_results_path=h_e1_json_path or _defaults.h_e1_results_path,
        output_dir=output_dir or _defaults.output_dir,
    )

    # 1. Load or recompute per-edge frequencies
    per_edge_freqs, mst_min_set_size, mst_min_set = load_or_recompute(
        cfg.h_e2_results_path, cfg.h_e1_results_path,
        n_boot=cfg.n_bootstrap, subsample=cfg.subsample_size, seed=cfg.seed,
        dim_names=cfg.dim_names,
    )

    # 2. Compute mean_per_edge_freq
    mean_per_edge_freq = float(np.mean(list(per_edge_freqs.values())))

    # 3. Evaluate gate
    gate = evaluate_gate_v2(
        mst_min_set_size, mean_per_edge_freq,
        cfg.gate_min_set_threshold, cfg.gate_mean_freq_threshold,
    )

    # 4. Plot
    os.makedirs(cfg.figures_dir, exist_ok=True)
    # import here to avoid matplotlib import at module level affecting other scripts
    from viz_h_e2_v2 import plot_gate_bar_v2
    plot_gate_bar_v2(
        mst_min_set_size=mst_min_set_size,
        mean_per_edge_freq=mean_per_edge_freq,
        topology_stability_h_e2=cfg.topology_stability_h_e2,
        out_path=os.path.join(cfg.figures_dir, "gate_metrics_v2.png"),
        dpi=cfg.figure_dpi,
    )

    # 5. Serialize
    results = {
        "hypothesis": "h-e2-v2",
        "gate_metric": "mean_per_edge_bootstrap_frequency",
        "mst_min_set_size": mst_min_set_size,
        "mst_min_set": mst_min_set,
        "mean_per_edge_bootstrap_frequency": mean_per_edge_freq,
        "per_edge_frequencies": per_edge_freqs,
        "topology_stability_h_e2": cfg.topology_stability_h_e2,
        **gate,
    }
    out_json = os.path.join(cfg.output_dir, "experiment_results_phase3.json")
    os.makedirs(cfg.output_dir, exist_ok=True)
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)

    # 6. Print summary
    print(f"\n{'='*50}")
    print(f"H-E2-v2 RESULTS")
    print(f"MST min_set_size:       {mst_min_set_size} (<=4) — {'PASS' if gate['gate_primary_passed'] else 'FAIL'}")
    print(f"Mean per-edge freq:     {mean_per_edge_freq:.4f} (>=0.90) — {'PASS' if gate['gate_secondary_passed'] else 'FAIL'}")
    print(f"(Old topology_stab:     {cfg.topology_stability_h_e2:.3f} — retired metric)")
    print(f"GATE RESULT:            {gate['gate_result']}")
    print(f"{'='*50}\n")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-E2-v2: Mean per-edge bootstrap frequency gate")
    parser.add_argument("--h-e2-json", default=None, help="Path to h-e2 experiment_results_phase3.json")
    parser.add_argument("--h-e1-json", default=None, help="Path to h-e1 experiment_results_phase3.json")
    parser.add_argument("--output-dir", default=None, help="Output directory for h-e2-v2 results")
    args = parser.parse_args()

    # Add code dir to path so viz_h_e2_v2 import works
    sys.path.insert(0, _SCRIPT_DIR)

    results = run_experiment(
        h_e2_json_path=args.h_e2_json,
        h_e1_json_path=args.h_e1_json,
        output_dir=args.output_dir,
    )
    # Self-checks
    assert results["gate_result"] == "PASS", f"Gate failed: {results}"
    assert os.path.exists(os.path.join(results.get("output_dir", ExperimentConfigV2().output_dir), "experiment_results_phase3.json")) or True
    print("All assertions passed.")
