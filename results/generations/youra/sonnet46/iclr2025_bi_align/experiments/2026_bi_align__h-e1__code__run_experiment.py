"""
run_experiment.py - Full pipeline orchestration for h-e1 hypothesis.

Hypothesis: C_sem^{H<-A} = E[cos(SBERT(H_{t+1}), SBERT(A_t))]
            - E[cos(SBERT(H_{t+1}), SBERT(A_t^matched-shuffle))] > 0
"""
import os
import json
import logging
import argparse
import time
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional

import numpy as np

from data_loader import load_all_splits, extract_pairs
from embedder import Embedder
from controls import build_random_control, build_topic_control
from accommodation import compute_cosine_similarities, apply_residualization, compute_c_sem
from statistics import run_all_tests, verify_mechanism_activated, bootstrap_c_sem
from visualize import (
    plot_gate_metrics,
    plot_partner_specificity,
    plot_bootstrap_dist,
    plot_cosine_distributions,
    plot_residualization_check,
    plot_knn_quality,
)

HYPOTHESIS_ID = "h-e1"
DEFAULT_MODEL = "all-MiniLM-L6-v2"
ROBUSTNESS_MODELS = ["paraphrase-MiniLM-L6-v2", "all-mpnet-base-v2"]


@dataclass
class ExperimentResults:
    hypothesis_id: str
    model_name: str
    n_pairs: int
    c_sem: float
    c_sem_ci: List[float]
    cos_actual_mean: float
    cos_topic_mean: float
    cos_random_mean: float
    mann_whitney_actual_vs_topic: Dict
    mann_whitney_topic_vs_random: Dict
    cohen_d_actual_vs_topic: float
    cohen_d_actual_vs_random: float
    cohen_d_topic_vs_random: float
    mechanism_activated: bool
    mechanism_indicators: Dict
    timestamp: str
    gate_passed: bool


def _setup_logging(output_dir: str) -> logging.Logger:
    """Set up logging to both file and stdout."""
    os.makedirs(output_dir, exist_ok=True)
    logger = logging.getLogger("h-e1")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        logger.handlers.clear()

    fh = logging.FileHandler(os.path.join(output_dir, "experiment.log"))
    fh.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh.setFormatter(fmt)
    sh.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


def run_experiment(config: dict) -> ExperimentResults:
    """Full pipeline orchestration.

    config keys:
      - cache_dir: HH-RLHF cache directory
      - model_name: SentenceTransformer model name
      - output_dir: directory for outputs
      - n_samples: optional int to subsample data (None = use all)
    """
    output_dir = config.get("output_dir", "outputs")
    model_name = config.get("model_name", DEFAULT_MODEL)
    cache_dir = config["cache_dir"]
    n_samples = config.get("n_samples", None)

    logger = _setup_logging(output_dir)
    embeddings_dir = os.path.join(output_dir, "embeddings")
    figures_dir = os.path.join(output_dir, "figures")
    os.makedirs(embeddings_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    logger.info(f"Starting experiment {HYPOTHESIS_ID}")
    logger.info(f"Model: {model_name}, cache_dir: {cache_dir}, output_dir: {output_dir}")

    # Step 1: Load data
    logger.info("Loading HH-RLHF splits...")
    conversations = load_all_splits(cache_dir)
    logger.info(f"Loaded {len(conversations)} conversations")

    # Step 2: Extract pairs
    logger.info("Extracting (h_next, a_actual, h_prompt) pairs...")
    pairs = extract_pairs(conversations)
    n_total = len(pairs["h_next"])
    logger.info(f"Extracted {n_total} pairs")

    # Optionally subsample
    if n_samples is not None and n_samples < n_total:
        rng = np.random.default_rng(42)
        idx = rng.choice(n_total, n_samples, replace=False)
        for key in pairs:
            if isinstance(pairs[key], list):
                pairs[key] = [pairs[key][i] for i in idx]
        n_total = n_samples
        logger.info(f"Subsampled to {n_total} pairs")

    n_pairs = n_total
    h_next_texts = pairs["h_next"]
    a_actual_texts = pairs["a_actual"]
    h_prompt_texts = pairs["h_prompt"]
    token_counts = pairs["token_counts"]
    jaccard_overlaps = pairs["jaccard_overlaps"]

    # Step 3: Compute embeddings
    logger.info("Computing embeddings...")
    # Use model name as part of cache key to avoid collisions
    model_slug = model_name.replace("/", "_").replace("-", "_")
    embedder = Embedder(model_name=model_name, cache_dir=embeddings_dir)

    # Include n_pairs in cache key to avoid loading stale embeddings when subsampling
    cache_suffix = f"{model_slug}_{n_pairs}"
    h_next_emb = embedder.encode(h_next_texts, f"h_next_{cache_suffix}")
    a_actual_emb = embedder.encode(a_actual_texts, f"a_actual_{cache_suffix}")
    h_prompt_emb = embedder.encode(h_prompt_texts, f"h_prompt_{cache_suffix}")
    logger.info(f"Embeddings shape: {h_next_emb.shape}")

    embeddings_computed = (
        h_next_emb is not None
        and h_next_emb.shape == (n_pairs, h_next_emb.shape[1])
    )

    # Step 4: Build control embeddings
    logger.info("Building control embeddings...")
    a_random_emb = build_random_control(a_actual_emb, seed=42)
    a_topic_emb = build_topic_control(h_prompt_emb, a_actual_emb, k=5)
    logger.info("Control embeddings built")

    # Step 5: Compute cosine similarities
    logger.info("Computing cosine similarities...")
    cos_dict = compute_cosine_similarities(h_next_emb, a_actual_emb, a_topic_emb, a_random_emb)
    cos_dict_before = {k: v.copy() for k, v in cos_dict.items()}
    logger.info(f"cos_actual mean (before resid): {cos_dict['cos_actual'].mean():.4f}")

    # Step 6: Residualization (for robustness checks)
    logger.info("Applying residualization (length + lexical overlap)...")
    cos_dict_resid = apply_residualization(cos_dict, token_counts, jaccard_overlaps)
    logger.info(f"cos_actual mean (after resid): {cos_dict_resid['cos_actual'].mean():.4f}")

    # Step 7: Statistical tests on RAW cosine similarities
    # C_sem = E[cos(H_{t+1}, A_t)] - E[cos(H_{t+1}, A_t^shuffle)] on raw similarities
    logger.info("Running statistical tests on raw cosine similarities...")
    stat_results = run_all_tests(
        cos_dict["cos_actual"],
        cos_dict["cos_topic"],
        cos_dict["cos_random"],
        n_pairs,
    )
    # Also run on residualized for robustness reporting
    logger.info("Running statistical tests on residualized cosine similarities...")
    stat_results_resid = run_all_tests(
        cos_dict_resid["cos_actual"],
        cos_dict_resid["cos_topic"],
        cos_dict_resid["cos_random"],
        n_pairs,
    )
    logger.info(f"C_sem (resid) = {stat_results_resid['c_sem']:.6f}")
    logger.info(f"C_sem = {stat_results['c_sem']:.6f}")
    logger.info(f"C_sem 95% CI = [{stat_results['c_sem_ci'][0]:.6f}, {stat_results['c_sem_ci'][1]:.6f}]")

    # Step 8: Verify mechanism
    mechanism_activated, mechanism_indicators = verify_mechanism_activated(
        stat_results, embeddings_computed
    )
    logger.info(f"Mechanism activated: {mechanism_activated}")
    logger.info(f"Indicators: {mechanism_indicators}")

    # Step 9: Generate figures
    logger.info("Generating figures...")
    c_sem_ci_list = [float(stat_results["c_sem_ci"][0]), float(stat_results["c_sem_ci"][1])]
    plot_gate_metrics(
        {
            "c_sem": float(stat_results["c_sem"]),
            "c_sem_ci": c_sem_ci_list,
            "cos_actual_mean": float(stat_results["cos_actual_mean"]),
            "cos_topic_mean": float(stat_results["cos_topic_mean"]),
            "cos_random_mean": float(stat_results["cos_random_mean"]),
        },
        figures_dir,
    )
    plot_partner_specificity(
        {
            "cos_actual_mean": float(stat_results["cos_actual_mean"]),
            "cos_topic_mean": float(stat_results["cos_topic_mean"]),
            "cos_random_mean": float(stat_results["cos_random_mean"]),
        },
        figures_dir,
    )

    # Bootstrap samples for distribution plot (using raw cosines)
    rng = np.random.default_rng(42)
    n_boot = len(cos_dict["cos_actual"])
    boot_samples = np.array([
        float(np.mean(cos_dict["cos_actual"][rng.integers(0, n_boot, n_boot)])
              - np.mean(cos_dict["cos_random"][rng.integers(0, n_boot, n_boot)]))
        for _ in range(1000)
    ])
    plot_bootstrap_dist(boot_samples, figures_dir)
    plot_cosine_distributions(
        cos_dict["cos_actual"],
        cos_dict["cos_topic"],
        cos_dict["cos_random"],
        figures_dir,
    )
    plot_residualization_check(cos_dict_before, cos_dict_resid, figures_dir)
    plot_knn_quality(h_prompt_emb, figures_dir)
    logger.info("Figures saved")

    # Step 10: Save results
    gate_passed = mechanism_activated and stat_results["c_sem"] > 0
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")

    exp_results = ExperimentResults(
        hypothesis_id=HYPOTHESIS_ID,
        model_name=model_name,
        n_pairs=n_pairs,
        c_sem=stat_results["c_sem"],
        c_sem_ci=stat_results["c_sem_ci"].tolist(),
        cos_actual_mean=stat_results["cos_actual_mean"],
        cos_topic_mean=stat_results["cos_topic_mean"],
        cos_random_mean=stat_results["cos_random_mean"],
        mann_whitney_actual_vs_topic=stat_results["mann_whitney_actual_vs_topic"],
        mann_whitney_topic_vs_random=stat_results["mann_whitney_topic_vs_random"],
        cohen_d_actual_vs_topic=stat_results["cohen_d_actual_vs_topic"],
        cohen_d_actual_vs_random=stat_results["cohen_d_actual_vs_random"],
        cohen_d_topic_vs_random=stat_results["cohen_d_topic_vs_random"],
        mechanism_activated=mechanism_activated,
        mechanism_indicators={k: bool(v) for k, v in mechanism_indicators.items()},
        timestamp=timestamp,
        gate_passed=gate_passed,
    )

    results_path = os.path.join(output_dir, "results.json")
    with open(results_path, "w") as f:
        json.dump(asdict(exp_results), f, indent=2)
    logger.info(f"Results saved to {results_path}")
    logger.info(f"Gate passed: {gate_passed}")

    return exp_results


def run_robustness_checks(base_config: dict) -> dict:
    """Run robustness checks with different models sequentially.

    Args:
        base_config: base experiment config dict

    Returns:
        dict mapping model_name -> ExperimentResults dict, saved to results_robustness.json
    """
    output_dir = base_config.get("output_dir", "outputs")
    logger = _setup_logging(output_dir)
    logger.info("Starting robustness checks...")

    all_results = {}
    for model_name in ROBUSTNESS_MODELS:
        logger.info(f"Running robustness check with model: {model_name}")
        config = {**base_config, "model_name": model_name}
        try:
            results = run_experiment(config)
            all_results[model_name] = asdict(results)
        except Exception as e:
            logger.error(f"Robustness check failed for {model_name}: {e}")
            all_results[model_name] = {"error": str(e)}

    robustness_path = os.path.join(output_dir, "results_robustness.json")
    with open(robustness_path, "w") as f:
        json.dump(all_results, f, indent=2)
    logger.info(f"Robustness results saved to {robustness_path}")
    return all_results


def main():
    parser = argparse.ArgumentParser(description="Run h-e1 experiment: semantic accommodation in HH-RLHF")
    parser.add_argument(
        "--cache-dir",
        default="/home/anonymous/YouRA_results_new_4/TEST_bi_align/docs/youra_research/20260315_bi_align/.data_cache/datasets/hh-rlhf",
        help="HH-RLHF dataset cache directory",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="SentenceTransformer model name",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Output directory for results and figures",
    )
    parser.add_argument(
        "--n-samples",
        type=int,
        default=None,
        help="Number of pairs to sample (None = all)",
    )
    args = parser.parse_args()

    config = {
        "cache_dir": args.cache_dir,
        "model_name": args.model,
        "output_dir": args.output_dir,
        "n_samples": args.n_samples,
    }

    results = run_experiment(config)
    print("\n" + "=" * 60)
    print(f"EXPERIMENT COMPLETE: {HYPOTHESIS_ID}")
    print(f"  C_sem = {results.c_sem:.6f}")
    print(f"  C_sem 95% CI = [{results.c_sem_ci[0]:.6f}, {results.c_sem_ci[1]:.6f}]")
    print(f"  cos_actual_mean = {results.cos_actual_mean:.6f}")
    print(f"  cos_topic_mean = {results.cos_topic_mean:.6f}")
    print(f"  cos_random_mean = {results.cos_random_mean:.6f}")
    print(f"  n_pairs = {results.n_pairs}")
    print(f"  mechanism_activated = {results.mechanism_activated}")
    print(f"  gate_passed = {results.gate_passed}")
    print(f"  indicators = {results.mechanism_indicators}")
    print("=" * 60)
    return results


if __name__ == "__main__":
    main()
