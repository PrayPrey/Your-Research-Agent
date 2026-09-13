"""
run_experiment.py — Main orchestration for h-e1 UQ existence verification.

Usage:
    python run_experiment.py --config h-e1/config/h-e1.yaml

Pipeline:
    For each model_key x dataset_name:
        1. Load model
        2. Generate answers (with checkpoint resume)
        3. Compute UQ scores
        4. Evaluate AUROC + bootstrap CI
        5. Save results
    Run gate check (MUST_WORK: SE > TP CI excludes zero)
    Generate figures
    Write run_config.json
"""
import argparse
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict

import torch

# Add code dir to path
sys.path.insert(0, os.path.dirname(__file__))

from config import ExperimentConfig, load_config
from data_loader import compute_exact_match, get_dataset
from evaluate import evaluate_all, run_gate_check, save_results
from generate import generate_dataset
from model_loader import get_model, load_deberta_nli
from uq_methods import compute_all_uq, verify_se_mechanism
from visualize import generate_all_figures

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run_model_dataset(
    model_key: str,
    dataset_name: str,
    cfg: ExperimentConfig,
    nli_model: Any,
    nli_tokenizer: Any,
    base_dir: str,
) -> Dict[str, Any]:
    """Full pipeline for one model x dataset combination."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Running: model={model_key}, dataset={dataset_name}")
    logger.info(f"{'='*60}")

    model_cfg = cfg.models[model_key]
    batch_size = (
        cfg.evaluation.batch_size_8b if model_key == "small" else cfg.evaluation.batch_size_70b
    )

    # Load dataset
    logger.info(f"Loading dataset {dataset_name}...")
    items = get_dataset(dataset_name, n_few_shot=cfg.sampling.n_few_shot)
    max_samples = int(os.environ.get("H_E1_MAX_SAMPLES", 0))
    if max_samples > 0:
        items = items[:max_samples]
        logger.info(f"Dry-run: truncated to {max_samples} samples")
    logger.info(f"Loaded {len(items)} items from {dataset_name}")

    # Compute correctness labels from gold answers (will be filled after generation)
    # We need greedy_text to compute EM, so labels computed post-generation
    correctness_labels_raw = None  # computed after generation

    # Load LLM model
    logger.info(f"Loading model {model_key} ({model_cfg.hf_id})...")
    model, tokenizer = get_model(model_key, model_cfg)
    logger.info(f"Model loaded")

    # Generation checkpoint path (dry-run uses isolated temp dir)
    dryrun_ckpt_dir = os.environ.get("H_E1_DRYRUN_CKPT_DIR")
    gen_ckpt_dir = dryrun_ckpt_dir if dryrun_ckpt_dir else os.path.join(base_dir, "checkpoints")
    os.makedirs(gen_ckpt_dir, exist_ok=True)
    gen_ckpt_path = os.path.join(gen_ckpt_dir, f"gen_{model_key}_{dataset_name}.pkl")

    # Generate answers
    logger.info(f"Generating answers (batch_size={batch_size}, n_samples={cfg.sampling.n_samples})...")
    results = generate_dataset(
        model=model,
        tokenizer=tokenizer,
        dataset=items,
        cfg=cfg.sampling,
        batch_size=batch_size,
        checkpoint_path=gen_ckpt_path,
        checkpoint_every=cfg.evaluation.checkpoint_every,
    )
    logger.info(f"Generation complete: {len(results)} results")

    # Free LLM memory
    del model
    del tokenizer
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # Compute correctness labels from greedy predictions
    import numpy as np
    correctness_labels = np.array([
        compute_exact_match(r.greedy_text, items[i]["gold_answers"])
        for i, r in enumerate(results)
    ])
    correct_rate = correctness_labels.mean()
    logger.info(f"Correctness rate: {correct_rate:.3f} ({correctness_labels.sum()}/{len(correctness_labels)})")

    # Compute UQ scores
    logger.info("Computing UQ scores...")
    uq_scores, cluster_counts = compute_all_uq(results, nli_model, nli_tokenizer)

    # Verify SE mechanism
    se_ok, se_stats = verify_se_mechanism(cluster_counts, n_samples=cfg.sampling.n_samples)
    logger.info(f"SE mechanism: ok={se_ok}, stats={se_stats}")

    # Evaluate AUROC
    logger.info("Evaluating AUROC with bootstrap CI...")
    auroc_results = evaluate_all(uq_scores, correctness_labels, cfg, dataset_name, model_key)

    # Save results
    results_dir = os.path.join(base_dir, "results")
    save_results(auroc_results, uq_scores, correctness_labels, dataset_name, model_key, results_dir)

    return {
        "auroc_results": auroc_results,
        "uq_scores": uq_scores,
        "correctness_labels": correctness_labels,
        "se_mechanism": {"ok": se_ok, "stats": se_stats},
        "correct_rate": float(correct_rate),
    }


def main(config_path: str) -> None:
    start_time = datetime.now()
    logger.info(f"Phase 4 Experiment: h-e1 UQ Existence Verification")
    logger.info(f"Config: {config_path}")
    logger.info(f"Start: {start_time.isoformat()}")

    cfg = load_config(config_path)
    base_dir = os.path.dirname(os.path.dirname(config_path))  # h-e1/

    # Pick empty GPU
    if torch.cuda.is_available():
        import subprocess
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,memory.used", "--format=csv,noheader,nounits"],
            capture_output=True, text=True
        )
        available_gpu = None
        for line in result.stdout.strip().split("\n"):
            idx, mem = line.split(",")
            if int(mem.strip()) < 1000:
                available_gpu = int(idx.strip())
                break
        if available_gpu is not None:
            os.environ["CUDA_VISIBLE_DEVICES"] = str(available_gpu)
            logger.info(f"Using GPU {available_gpu}")
        else:
            logger.warning("No empty GPU found, using all available")

    # Load NLI model once (shared across all runs)
    logger.info("Loading NLI model (DeBERTa-large-mnli)...")
    nli_model, nli_tokenizer = load_deberta_nli()
    logger.info("NLI model loaded")

    # Collect all results
    all_auroc_results: Dict[str, Any] = {}
    all_uq_scores: Dict[str, Dict[str, Any]] = {}
    all_correctness_labels: Dict[str, Any] = {}

    # Run primary datasets x primary models (8B + 70B for MUST_WORK gate)
    primary_models = ["small", "large"]
    primary_datasets = [ds.name for ds in cfg.datasets_primary]

    for model_key in primary_models:
        all_auroc_results[model_key] = {}
        all_uq_scores[model_key] = {}
        for ds_name in primary_datasets:
            try:
                run_result = run_model_dataset(
                    model_key, ds_name, cfg, nli_model, nli_tokenizer, base_dir
                )
                all_auroc_results[model_key][ds_name] = run_result["auroc_results"]
                all_uq_scores[model_key][ds_name] = run_result["uq_scores"]
                all_correctness_labels[ds_name] = run_result["correctness_labels"]
            except Exception as e:
                logger.error(f"FAILED: model={model_key}, dataset={ds_name}: {e}", exc_info=True)

    # Run MUST_WORK gate check
    logger.info("\n" + "="*60)
    logger.info("Running MUST_WORK Gate Check...")
    gate_pass, condition_results = run_gate_check(
        all_auroc_results, all_uq_scores, all_correctness_labels,
        n_resamples=cfg.evaluation.bootstrap_resamples,
    )
    logger.info(f"Gate result: {'PASS' if gate_pass else 'FAIL'}")
    for cond, passed in condition_results.items():
        logger.info(f"  {cond}: {'PASS' if passed else 'FAIL'}")

    # Generate figures
    figures_dir = os.path.join(base_dir, "figures")
    try:
        generate_all_figures(all_auroc_results, all_uq_scores, all_correctness_labels, figures_dir)
    except Exception as e:
        logger.error(f"Figure generation failed: {e}", exc_info=True)

    # Write experiment results JSON
    end_time = datetime.now()
    import numpy as np

    def _json_safe(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.floating, np.integer)):
            return float(obj)
        return obj

    experiment_results = {
        "hypothesis_id": cfg.hypothesis_id,
        "gate": {
            "type": "MUST_WORK",
            "pass": gate_pass,
            "conditions": condition_results,
        },
        "auroc_summary": {
            mk: {
                ds: {
                    method: {k: v for k, v in res.items() if not isinstance(v, np.ndarray)}
                    for method, res in ds_res.items()
                }
                for ds, ds_res in model_res.items()
            }
            for mk, model_res in all_auroc_results.items()
        },
        "run_config": {
            "n_samples": cfg.sampling.n_samples,
            "temperature": cfg.sampling.temperature,
            "top_p": cfg.sampling.top_p,
            "seed": cfg.sampling.seed,
            "max_new_tokens": cfg.sampling.max_new_tokens,
            "n_few_shot": cfg.sampling.n_few_shot,
            "bootstrap_resamples": cfg.evaluation.bootstrap_resamples,
            "models": {k: v.hf_id for k, v in cfg.models.items()},
            "primary_datasets": primary_datasets,
        },
        "timing": {
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            "duration_seconds": (end_time - start_time).total_seconds(),
        },
    }

    results_dir = os.path.join(base_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    exp_results_path = os.path.join(results_dir, "experiment_results.json")
    with open(exp_results_path, "w") as f:
        json.dump(experiment_results, f, indent=2, default=_json_safe)
    logger.info(f"Experiment results saved to {exp_results_path}")

    # Also save to hypothesis-level path for pipeline
    pipeline_results_path = os.path.join(base_dir, "experiment_results.json")
    with open(pipeline_results_path, "w") as f:
        json.dump(experiment_results, f, indent=2, default=_json_safe)

    # Final summary
    logger.info("\n" + "="*60)
    logger.info("EXPERIMENT COMPLETE")
    logger.info(f"Gate: {'PASS' if gate_pass else 'FAIL'}")
    logger.info(f"Duration: {(end_time - start_time).total_seconds():.0f}s")
    logger.info("="*60)

    if not gate_pass:
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default=os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "h-e1.yaml"),
        help="Path to h-e1.yaml config file",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Limit dataset to N samples (for dry run)",
    )
    parser.add_argument(
        "--models",
        type=str,
        default=None,
        help="Comma-separated model keys to run (e.g. 'small' or 'small,large')",
    )
    args = parser.parse_args()
    if args.max_samples is not None:
        os.environ["H_E1_MAX_SAMPLES"] = str(args.max_samples)
        # Dry run uses isolated temp checkpoint dir to avoid corrupting full-run checkpoints
        import tempfile
        os.environ["H_E1_DRYRUN_CKPT_DIR"] = tempfile.mkdtemp(prefix="h_e1_dryrun_")
    if args.models is not None:
        os.environ["H_E1_MODELS"] = args.models
    main(args.config)
