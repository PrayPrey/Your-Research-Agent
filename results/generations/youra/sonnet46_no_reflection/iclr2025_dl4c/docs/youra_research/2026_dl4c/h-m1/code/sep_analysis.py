import os
import sys
import json
import logging
from typing import Optional

import numpy as np

from config import M1ExperimentConfig
from ast_decomposition import compute_sep, compute_edit_distribution

logger = logging.getLogger(__name__)


def _get_h_e1_code_path(cfg: M1ExperimentConfig) -> str:
    code_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(code_dir, cfg.h_e1_code_path))


def _make_h_e1_config(cfg: M1ExperimentConfig):
    """Build minimal H-E1 ExperimentConfig from M1ExperimentConfig for generate_solutions."""
    h_e1_path = _get_h_e1_code_path(cfg)
    if h_e1_path not in sys.path:
        sys.path.insert(0, h_e1_path)
    from config import ExperimentConfig  # H-E1's ExperimentConfig
    e1_cfg = ExperimentConfig()
    e1_cfg.model_id = cfg.sft_model_id
    e1_cfg.seed = cfg.seed
    e1_cfg.dtype = cfg.dtype
    e1_cfg.bootstrap_samples = cfg.bootstrap_samples
    e1_cfg.bootstrap_ci = cfg.bootstrap_ci
    e1_cfg.kl_tolerance = cfg.kl_tolerance
    return e1_cfg


def load_checkpoint_solutions(
    checkpoint_path: str,
    problems: dict,
    cfg: M1ExperimentConfig,
    cache_dir: Optional[str] = None,
) -> dict:
    """Load or generate solutions for a checkpoint.

    Cache: {cache_dir}/{checkpoint_basename}_solutions.json
    Uses H-E1 generate_solutions with ExperimentConfig shim.
    """
    basename = os.path.basename(checkpoint_path.rstrip("/"))
    if cache_dir is None:
        code_dir = os.path.dirname(os.path.abspath(__file__))
        cache_dir = os.path.join(code_dir, cfg.output_dir, "solutions_cache")
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"{basename}_solutions.json")

    if os.path.exists(cache_file):
        logger.info(f"Loading cached solutions from {cache_file}")
        with open(cache_file) as f:
            return json.load(f)

    logger.info(f"Generating solutions for checkpoint: {checkpoint_path}")
    h_e1_path = _get_h_e1_code_path(cfg)
    if h_e1_path not in sys.path:
        sys.path.insert(0, h_e1_path)

    from evaluate import generate_solutions
    e1_cfg = _make_h_e1_config(cfg)
    solutions = generate_solutions(checkpoint_path, problems, e1_cfg, max_new_tokens=cfg.max_new_tokens)

    with open(cache_file, "w") as f:
        json.dump(solutions, f)
    logger.info(f"Cached solutions to {cache_file}")
    return solutions


def compute_sep_for_checkpoint_pair(
    grpo_checkpoint: str,
    dpo_checkpoint: str,
    reference_solutions: dict,
    problems: dict,
    cfg: M1ExperimentConfig,
) -> dict:
    """Compute per-problem SEP for one KL-matched checkpoint pair."""
    grpo_solutions = load_checkpoint_solutions(grpo_checkpoint, problems, cfg)
    dpo_solutions = load_checkpoint_solutions(dpo_checkpoint, problems, cfg)

    sep_grpo = []
    sep_dpo = []
    edit_dist_grpo = {}
    edit_dist_dpo = {}
    n_valid_grpo = 0
    n_invalid_grpo = 0
    n_valid_dpo = 0
    n_invalid_dpo = 0

    for task_id, ref_code in reference_solutions.items():
        if not ref_code:
            continue

        grpo_code = grpo_solutions.get(task_id, "")
        dpo_code = dpo_solutions.get(task_id, "")

        if grpo_code:
            sep_g = compute_sep(ref_code, grpo_code)
            dist_g = compute_edit_distribution(ref_code, grpo_code)
            if sep_g is not None:
                sep_grpo.append(sep_g)
                n_valid_grpo += 1
            else:
                n_invalid_grpo += 1
            if dist_g is not None:
                edit_dist_grpo[task_id] = dist_g

        if dpo_code:
            sep_d = compute_sep(ref_code, dpo_code)
            dist_d = compute_edit_distribution(ref_code, dpo_code)
            if sep_d is not None:
                sep_dpo.append(sep_d)
                n_valid_dpo += 1
            else:
                n_invalid_dpo += 1
            if dist_d is not None:
                edit_dist_dpo[task_id] = dist_d

    # Extract step info from checkpoint path
    step_grpo = _extract_step(grpo_checkpoint)
    step_dpo = _extract_step(dpo_checkpoint)

    # Load KL values
    h_e1_path = _get_h_e1_code_path(cfg)
    if h_e1_path not in sys.path:
        sys.path.insert(0, h_e1_path)
    from kl_metric import load_checkpoint_kl_log
    grpo_kl_log = load_checkpoint_kl_log(os.path.dirname(grpo_checkpoint))
    dpo_kl_log = load_checkpoint_kl_log(os.path.dirname(dpo_checkpoint))
    kl_grpo = _get_kl_at_step(grpo_kl_log, step_grpo)
    kl_dpo = _get_kl_at_step(dpo_kl_log, step_dpo)

    return {
        "sep_grpo": sep_grpo,
        "sep_dpo": sep_dpo,
        "edit_dist_grpo": edit_dist_grpo,
        "edit_dist_dpo": edit_dist_dpo,
        "kl_grpo": kl_grpo,
        "kl_dpo": kl_dpo,
        "step_grpo": step_grpo,
        "step_dpo": step_dpo,
        "n_valid_grpo": n_valid_grpo,
        "n_valid_dpo": n_valid_dpo,
        "n_invalid_grpo": n_invalid_grpo,
        "n_invalid_dpo": n_invalid_dpo,
    }


def _extract_step(checkpoint_path: str) -> int:
    """Extract step number from checkpoint path like .../checkpoint-100."""
    basename = os.path.basename(checkpoint_path.rstrip("/"))
    if "-" in basename:
        try:
            return int(basename.rsplit("-", 1)[-1])
        except ValueError:
            pass
    return 0


def _get_kl_at_step(kl_log: list, step: int) -> float:
    """Get KL divergence at a specific step from kl_log."""
    for entry in kl_log:
        if entry.get("step") == step:
            return entry.get("kl_divergence", float("nan"))
    return float("nan")


def aggregate_sep_across_pairs(
    grpo_checkpoint_dir: str,
    dpo_checkpoint_dir: str,
    reference_solutions: dict,
    problems: dict,
    cfg: M1ExperimentConfig,
    condition_label: str = "grpo_binary",
) -> dict:
    """Iterate all KL-matched pairs; collect SEP across problems × pairs."""
    h_e1_path = _get_h_e1_code_path(cfg)
    if h_e1_path not in sys.path:
        sys.path.insert(0, h_e1_path)
    from kl_metric import load_checkpoint_kl_log, match_checkpoints

    grpo_kl_log = load_checkpoint_kl_log(grpo_checkpoint_dir)
    dpo_kl_log = load_checkpoint_kl_log(dpo_checkpoint_dir)

    if not grpo_kl_log or not dpo_kl_log:
        logger.warning(f"Empty KL logs for {condition_label}")
        return {
            "sep_grpo": [], "sep_dpo": [], "pairs": [],
            "pass_at_1_per_step": {}, "condition": condition_label, "n_pairs": 0,
        }

    pairs = match_checkpoints(grpo_kl_log, dpo_kl_log, tolerance=cfg.kl_tolerance)
    logger.info(f"{condition_label}: found {len(pairs)} KL-matched pairs at tolerance={cfg.kl_tolerance}")

    all_sep_grpo = []
    all_sep_dpo = []
    pair_results = []

    for pair in pairs:
        grpo_ckpt = os.path.join(grpo_checkpoint_dir, f"checkpoint-{pair['grpo_step']}")
        dpo_ckpt = os.path.join(dpo_checkpoint_dir, f"checkpoint-{pair['dpo_step']}")

        if not os.path.isdir(grpo_ckpt) or not os.path.isdir(dpo_ckpt):
            logger.warning(f"Missing checkpoint dirs: {grpo_ckpt} or {dpo_ckpt}")
            continue

        result = compute_sep_for_checkpoint_pair(
            grpo_ckpt, dpo_ckpt, reference_solutions, problems, cfg
        )
        all_sep_grpo.extend(result["sep_grpo"])
        all_sep_dpo.extend(result["sep_dpo"])
        pair_results.append({**pair, **result})

    return {
        "sep_grpo": all_sep_grpo,
        "sep_dpo": all_sep_dpo,
        "pairs": pair_results,
        "pass_at_1_per_step": {},
        "condition": condition_label,
        "n_pairs": len(pair_results),
    }


def compute_bootstrap_ci_sep(
    sep_values: list,
    cfg: M1ExperimentConfig,
) -> dict:
    """Bootstrap CI for mean SEP. Delegates to H-E1 bootstrap_ci."""
    if not sep_values:
        return {"mean": float("nan"), "lower": float("nan"), "upper": float("nan"), "n": 0}

    h_e1_path = _get_h_e1_code_path(cfg)
    if h_e1_path not in sys.path:
        sys.path.insert(0, h_e1_path)
    from evaluate import bootstrap_ci
    return bootstrap_ci(sep_values, n_samples=cfg.bootstrap_samples,
                        ci=cfg.bootstrap_ci, seed=cfg.seed)


def collect_all_conditions(
    cfg: M1ExperimentConfig,
    problems: dict,
    reference_solutions: dict,
) -> dict:
    """Run aggregate_sep_across_pairs for all 3 conditions."""
    grpo_binary = aggregate_sep_across_pairs(
        cfg.grpo_binary_checkpoint_dir,
        cfg.dpo_checkpoint_dir,
        reference_solutions, problems, cfg,
        condition_label="grpo_binary",
    )
    grpo_errortype = aggregate_sep_across_pairs(
        cfg.grpo_errortype_checkpoint_dir,
        cfg.dpo_checkpoint_dir,
        reference_solutions, problems, cfg,
        condition_label="grpo_errortype",
    )
    dpo = aggregate_sep_across_pairs(
        cfg.dpo_checkpoint_dir,
        cfg.dpo_checkpoint_dir,
        reference_solutions, problems, cfg,
        condition_label="dpo",
    )

    ci = {
        "grpo_binary": compute_bootstrap_ci_sep(grpo_binary["sep_grpo"], cfg),
        "grpo_errortype": compute_bootstrap_ci_sep(grpo_errortype["sep_grpo"], cfg),
        "dpo": compute_bootstrap_ci_sep(dpo["sep_dpo"], cfg),
    }

    return {
        "grpo_binary": grpo_binary,
        "grpo_errortype": grpo_errortype,
        "dpo": dpo,
        "ci": ci,
    }
