"""
run_experiment_m4.py - H-M4 PM-Score OLS Mediation Regression orchestrator.

H-M4: PM-proxy (chosen/rejected preference) positively predicts C_sem^H←A
above surface-feature controls (response length, bullet structure, politeness
markers, syntactic complexity).

Gate: SHOULD_WORK — requires >=2/3 SBERT models with beta_pm > 0, p < 0.05
"""
import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

# CRITICAL: Set thread limits before loading numpy-dependent libraries
os.environ.setdefault("OPENBLAS_NUM_THREADS", "4")
os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")

# CRITICAL: Insert h-m4 FIRST so h-m4 modules (config, data_loader, etc.) take priority
_H_M4_CODE = str(Path(__file__).parent)
if _H_M4_CODE not in sys.path:
    sys.path.insert(0, _H_M4_CODE)

# Add h-m2 AFTER h-m4 for Embedder, controls, accommodation (not in h-m4)
_H_M2_CODE = str(Path(__file__).parent.parent.parent / "h-m2" / "code")
if _H_M2_CODE not in sys.path:
    sys.path.append(_H_M2_CODE)  # append (not insert) so h-m4 modules remain first

from embedder import Embedder
from controls import build_topic_control, build_random_control
from accommodation import compute_h_given_a_csem_array

# h-m4 modules
from config import ExperimentConfig, load_config, TIER_ORDER, BRANCH_LABELS
from data_loader import split_by_tier_bidir, build_regression_dataframe
from surface_features import batch_extract_features
from regression import run_mediation_ols, MediationResult, SURFACE_FEATURE_COLS
from evaluate import evaluate_cross_model_gate, generate_gate_report, OverallGateResult
from visualize_m4 import generate_all_figures

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

HYPOTHESIS_ID = "h-m4"


def setup_logging(output_dir: str) -> None:
    """Setup file logging in addition to console."""
    os.makedirs(output_dir, exist_ok=True)
    log_path = os.path.join(output_dir, "h-m4_experiment.log")
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logging.getLogger().addHandler(fh)


def compute_csem_per_branch(
    tier_pairs: Dict,
    embedder: Embedder,
    tier: str,
    branch: str,
    seed: int = 42,
) -> np.ndarray:
    """Compute per-row C_sem^H<-A for one tier+branch.

    Args:
        tier_pairs: Dict from split_by_tier_bidir()
        embedder: Embedder instance
        tier: Tier name (e.g., 'helpful-base')
        branch: 'chosen' or 'rejected'
        seed: Random seed for build_random_control

    Returns:
        np.ndarray of shape [N,] float32
    """
    pairs = tier_pairs[tier]

    # Get indices for this branch
    branch_indices = [i for i, b in enumerate(pairs["branch"]) if b == branch]
    if not branch_indices:
        logger.warning(f"No {branch} pairs for tier {tier}")
        return np.array([], dtype=np.float32)

    h_next_texts = [pairs["h_next"][i] for i in branch_indices]
    a_response_texts = [pairs["a_response"][i] for i in branch_indices]
    h_prompt_texts = [pairs["h_prompt"][i] for i in branch_indices]
    N = len(branch_indices)

    # Encode with distinct cache prefix per branch
    emb_h = embedder.encode_tier(h_next_texts, prefix='h', tier=tier, n_pairs=N)
    emb_p = embedder.encode_tier(h_prompt_texts, prefix='p', tier=tier, n_pairs=N)
    # CRITICAL: distinct cache prefix prevents collision between chosen/rejected
    emb_a = embedder.encode_tier(a_response_texts, prefix=f'a_{branch}', tier=tier, n_pairs=N)

    # Topic-matched shuffle: n_jobs=1 hardcoded in build_topic_control
    emb_shuffle = build_topic_control(emb_p, emb_a, k=5)

    csem_array = compute_h_given_a_csem_array(emb_h, emb_a, emb_shuffle)
    return csem_array.astype(np.float32)


def compute_all_branch_csem(
    tier_pairs: Dict,
    embedder: Embedder,
    seed: int = 42,
) -> Dict[str, Dict[str, np.ndarray]]:
    """Compute C_sem for all tier x branch combinations.

    Args:
        tier_pairs: Dict from split_by_tier_bidir()
        embedder: Embedder instance
        seed: Random seed

    Returns:
        Dict: {tier: {'chosen': [N,], 'rejected': [N,]}}
    """
    csem_arrays = {}

    for tier in TIER_ORDER:
        if tier not in tier_pairs:
            logger.warning(f"Tier {tier} not in tier_pairs, skipping")
            continue

        csem_arrays[tier] = {}
        for branch in BRANCH_LABELS:
            logger.info(f"[H-M4] Computing C_sem for tier={tier}, branch={branch}")
            csem_arr = compute_csem_per_branch(tier_pairs, embedder, tier, branch, seed=seed)
            csem_arrays[tier][branch] = csem_arr
            logger.info(
                f"[H-M4] tier={tier} branch={branch}: N={len(csem_arr)}, "
                f"mean_csem={csem_arr.mean():.4f}" if len(csem_arr) > 0 else
                f"[H-M4] tier={tier} branch={branch}: N=0"
            )

    return csem_arrays


def run_single_model(
    model_name: str,
    config: ExperimentConfig,
    tier_pairs: Dict,
) -> Tuple[MediationResult, pd.DataFrame]:
    """Run full pipeline for one SBERT model.

    Args:
        model_name: SBERT model name (e.g. 'all-MiniLM-L6-v2')
        config: ExperimentConfig
        tier_pairs: Dict from split_by_tier_bidir()

    Returns:
        Tuple (mediation_result, regression_df)
    """
    logger.info(f"[H-M4] Starting model: {model_name}")

    # Initialize embedder (uses h-m2 embeddings cache)
    embedder = Embedder(model_name=model_name, cache_dir=config.cache.embeddings_dir)

    # Compute C_sem per tier x branch
    csem_arrays = compute_all_branch_csem(tier_pairs, embedder, seed=config.stats.seed)

    # KS test for IPW trigger
    try:
        from scipy.stats import ks_2samp
        for tier in TIER_ORDER:
            if tier in csem_arrays:
                chosen_arr = csem_arrays[tier].get('chosen', np.array([]))
                rejected_arr = csem_arrays[tier].get('rejected', np.array([]))
                if len(chosen_arr) > 0 and len(rejected_arr) > 0:
                    stat, p = ks_2samp(chosen_arr, rejected_arr)
                    if p < config.ipw_ks_threshold:
                        logger.warning(
                            f"[IPW trigger] KS distribution shift in {tier}, p={p:.4f} "
                            f"(threshold={config.ipw_ks_threshold})"
                        )
    except ImportError:
        logger.warning("scipy not available — skipping KS test")

    # Extract surface features per tier x branch
    surf_feat_dfs = {}
    for tier in TIER_ORDER:
        if tier not in tier_pairs:
            continue
        pairs = tier_pairs[tier]
        branches = pairs["branch"]
        for branch in BRANCH_LABELS:
            branch_indices = [i for i, b in enumerate(branches) if b == branch]
            if not branch_indices:
                continue
            texts = [pairs["a_response"][i] for i in branch_indices]
            surf_feat_dfs[(tier, branch)] = batch_extract_features(texts)
            logger.info(f"[H-M4] Surface features extracted for tier={tier}, branch={branch}: N={len(texts)}")

    # Build regression DataFrame
    df = build_regression_dataframe(tier_pairs, csem_arrays, surf_feat_dfs)
    logger.info(f"[H-M4] Regression DataFrame: {len(df)} rows")

    # N_pairs < 1000 warning
    if len(df) < config.stats.min_n_pairs:
        logger.warning(f"[H-M4] N_rows={len(df)} < min_n_pairs={config.stats.min_n_pairs}")

    # Run 4-stage OLS mediation
    mediation_result = run_mediation_ols(
        df,
        model_name=model_name,
        cov_type=config.regression.cov_type,
    )
    logger.info(
        f"[H-M4] Model {model_name}: "
        f"beta_pm_full={mediation_result.beta_pm_full:.4f}, "
        f"p_full={mediation_result.stage_full.p_pm:.4f}"
    )

    return mediation_result, df


def _to_serializable(obj):
    """Recursively convert numpy/dataclass objects to JSON-serializable types."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    if isinstance(obj, (np.float64, np.float32, np.float16)):
        return float(obj)
    if isinstance(obj, float) and (obj != obj):  # nan
        return None
    if isinstance(obj, dict):
        return {k: _to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_serializable(v) for v in obj]
    return obj


def save_results(
    all_mediation_results: Dict[str, MediationResult],
    overall_gate: OverallGateResult,
    results_dir: str,
) -> None:
    """Save regression_results.json with all coefficients + gate evaluation.

    Args:
        all_mediation_results: Dict mapping model_name -> MediationResult
        overall_gate: OverallGateResult from evaluate_cross_model_gate()
        results_dir: Directory to save results JSON
    """
    os.makedirs(results_dir, exist_ok=True)

    output = {
        "hypothesis": HYPOTHESIS_ID,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "gate": {
            "overall_pass": overall_gate.overall_pass,
            "models_passed": overall_gate.models_passed,
            "models_required": overall_gate.models_required,
            "interpretation": overall_gate.interpretation,
        },
        "models": {},
    }

    for model_name, med_result in all_mediation_results.items():
        gate_result = overall_gate.gate_results.get(model_name)

        stage1 = med_result.stage_pm_only
        stage2 = med_result.stage_full
        stage3 = med_result.stage_robustness

        model_output = {
            "gate_pass": gate_result.gate_pass if gate_result else None,
            "stage_pm_only": {
                "beta_pm": stage1.beta_pm,
                "p_pm": stage1.p_pm,
                "beta_pm_ci": list(stage1.beta_pm_ci),
                "r_squared": stage1.r_squared,
                "nobs": stage1.nobs,
                "condition_number": stage1.condition_number,
            },
            "stage_full": {
                "beta_pm": stage2.beta_pm,
                "p_pm": stage2.p_pm,
                "beta_pm_ci": list(stage2.beta_pm_ci),
                "r_squared": stage2.r_squared,
                "nobs": stage2.nobs,
                "condition_number": stage2.condition_number,
                "all_params": stage2.all_params,
                "all_pvalues": stage2.all_pvalues,
                "all_ci": {k: list(v) for k, v in stage2.all_ci.items()},
            },
            "stage_robustness": {
                "beta_tier_rank": stage3.beta_pm,
                "p_tier_rank": stage3.p_pm,
                "r_squared": stage3.r_squared,
                "nobs": stage3.nobs,
            },
            "mediation": {
                "beta_pm_reduced": med_result.beta_pm_reduced,
                "beta_pm_full": med_result.beta_pm_full,
                "mediation_ratio": med_result.mediation_ratio,
                "pm_effect_retained": med_result.pm_effect_retained,
            },
        }
        output["models"][model_name] = model_output

    results_path = os.path.join(results_dir, "regression_results.json")
    with open(results_path, "w") as f:
        json.dump(_to_serializable(output), f, indent=2)

    logger.info(f"[H-M4] Results saved: {results_path}")


def main(config_path: Optional[str] = None, dry_run: bool = False) -> None:
    """Orchestrate full h-m4 pipeline.

    Steps:
    1. Load config
    2. Load chosen/rejected tier data
    3. For each SBERT model:
       a. Encode H_next, A_response per (conversation, branch)
       b. Compute C_sem^H<-A per row
       c. Extract surface features from A_response texts
       d. Build regression DataFrame
       e. Run 4-stage OLS mediation
    4. Evaluate cross-model gate (>=2/3)
    5. Generate 6 figures
    6. Save results JSON
    """
    config = load_config(config_path)

    if dry_run:
        config.dry_run = True

    setup_logging(config.output_dir)
    logger.info(f"[H-M4] Starting experiment (dry_run={config.dry_run})")

    # Resolve relative paths based on script location
    script_dir = str(Path(__file__).parent)

    def resolve(path: str) -> str:
        if os.path.isabs(path):
            return path
        return str(Path(script_dir) / path)

    cache_dir = resolve(config.cache.cache_dir)
    embeddings_dir = resolve(config.cache.embeddings_dir)
    results_dir = resolve(config.results_dir)
    figures_dir = resolve(config.figures.figures_dir)

    config.cache.cache_dir = cache_dir
    config.cache.embeddings_dir = embeddings_dir
    config.results_dir = results_dir
    config.figures.figures_dir = figures_dir

    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    logger.info(f"[H-M4] Dataset cache: {cache_dir}")
    logger.info(f"[H-M4] Embeddings dir: {embeddings_dir}")

    # Load chosen+rejected tier data
    tier_pairs = split_by_tier_bidir(cache_dir)

    if config.dry_run:
        logger.info(f"[H-M4] DRY RUN: subsampling to {config.n_samples_dry_run} per tier+branch")
        n = config.n_samples_dry_run
        for tier in TIER_ORDER:
            if tier in tier_pairs:
                pairs = tier_pairs[tier]
                total = len(pairs["h_next"])
                # Keep up to n*2 rows (n chosen + n rejected approximately)
                keep = min(n * 2, total)
                tier_pairs[tier] = {k: v[:keep] for k, v in pairs.items()}

    # Run pipeline for each SBERT model
    all_mediation_results = {}
    all_dfs = {}

    for model_name in config.cache.models:
        try:
            med_result, df = run_single_model(model_name, config, tier_pairs)
            all_mediation_results[model_name] = med_result
            all_dfs[model_name] = df
        except Exception as e:
            logger.error(f"[H-M4] Model {model_name} failed: {e}", exc_info=True)

    if not all_mediation_results:
        logger.error("[H-M4] No models completed successfully")
        return

    # Evaluate cross-model gate
    overall_gate = evaluate_cross_model_gate(
        all_mediation_results,
        models_required=config.stats.models_required,
        significance_level=config.stats.alpha,
    )
    logger.info(generate_gate_report(overall_gate))

    # Generate figures using first available model's df
    first_model = list(all_dfs.keys())[0]
    try:
        generate_all_figures(all_mediation_results, all_dfs[first_model], figures_dir)
    except Exception as e:
        logger.error(f"[H-M4] Figure generation failed: {e}", exc_info=True)

    # Save results
    save_results(all_mediation_results, overall_gate, results_dir)

    gate_status = "PASS" if overall_gate.overall_pass else "FAIL"
    logger.info(
        f"[H-M4] Experiment complete. Gate: {gate_status} "
        f"({overall_gate.models_passed}/{len(all_mediation_results)} models)"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-M4: PM-Score OLS Mediation Regression")
    parser.add_argument("--config", type=str, default=None, help="Path to config YAML")
    parser.add_argument("--dry-run", action="store_true", help="Run on small subset")
    args = parser.parse_args()
    main(config_path=args.config, dry_run=args.dry_run)
