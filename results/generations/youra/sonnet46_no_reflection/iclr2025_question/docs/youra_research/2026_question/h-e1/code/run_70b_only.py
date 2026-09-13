"""
run_70b_only.py — Run 70B model generation+eval for h-e1 PoC gate.

Generates 200 samples per dataset with n_samples=5 stochastic draws.
Merges results with existing 8B results and writes final experiment_results.json.
"""
import json
import logging
import os
import pickle
import sys
from datetime import datetime
from typing import Any, Dict

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(__file__))

from config import load_config
from data_loader import compute_exact_match, get_dataset
from evaluate import evaluate_all, run_gate_check, save_results
from generate import generate_dataset
from model_loader import get_model, load_deberta_nli
from uq_methods import compute_all_uq, verify_se_mechanism
from visualize import generate_all_figures

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

MAX_SAMPLES = 200
N_SAMPLES_70B = 5   # reduced from 10 for speed

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # h-e1/
CONFIG_PATH = os.path.join(BASE_DIR, "config", "h-e1.yaml")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
CKPT_DIR = os.path.join(BASE_DIR, "checkpoints")


def run_70b_dataset(dataset_name, cfg, nli_model, nli_tokenizer):
    ckpt_path = os.path.join(CKPT_DIR, f"gen_large_{dataset_name}.pkl")

    logger.info(f"\n{'='*60}\nRunning 70B on {dataset_name} (max={MAX_SAMPLES})\n{'='*60}")

    items = get_dataset(dataset_name, n_few_shot=cfg.sampling.n_few_shot)
    items = items[:MAX_SAMPLES]
    logger.info(f"Loaded {len(items)} items")

    # Override n_samples for speed
    from dataclasses import replace
    sampling_cfg = replace(cfg.sampling, n_samples=N_SAMPLES_70B)

    model_cfg = cfg.models["large"]
    logger.info(f"Loading 70B ({model_cfg.hf_id})...")
    model, tokenizer = get_model("large", model_cfg)
    logger.info("70B loaded")

    results = generate_dataset(
        model=model, tokenizer=tokenizer, dataset=items,
        cfg=sampling_cfg, batch_size=cfg.evaluation.batch_size_70b,
        checkpoint_path=ckpt_path, checkpoint_every=50,
    )
    logger.info(f"Generation done: {len(results)} results")

    del model
    del tokenizer
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    correctness_labels = np.array([
        compute_exact_match(r.greedy_text, items[i]["gold_answers"])
        for i, r in enumerate(results) if i < len(items)
    ])
    logger.info(f"Correctness: {correctness_labels.mean():.3f} ({int(correctness_labels.sum())}/{len(correctness_labels)})")

    logger.info("Computing UQ scores...")
    uq_scores, cluster_counts = compute_all_uq(results, nli_model, nli_tokenizer)
    se_ok, se_stats = verify_se_mechanism(cluster_counts, n_samples=N_SAMPLES_70B)
    logger.info(f"SE mechanism: ok={se_ok}, stats={se_stats}")

    auroc_results = evaluate_all(uq_scores, correctness_labels, cfg, dataset_name, "large")
    save_results(auroc_results, uq_scores, correctness_labels, dataset_name, "large", RESULTS_DIR)

    return {
        "auroc_results": auroc_results,
        "uq_scores": uq_scores,
        "correctness_labels": correctness_labels,
        "correct_rate": float(correctness_labels.mean()),
        "n_samples": len(correctness_labels),
    }


def main():
    start = datetime.now()
    logger.info(f"70B-only run started: {start.isoformat()}")

    cfg = load_config(CONFIG_PATH)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(CKPT_DIR, exist_ok=True)

    # GPU selection
    if torch.cuda.is_available():
        import subprocess
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,memory.used", "--format=csv,noheader,nounits"],
            capture_output=True, text=True
        )
        for line in result.stdout.strip().split("\n"):
            idx, mem = int(line.split(",")[0].strip()), int(line.split(",")[1].strip())
            if mem < 1000:
                os.environ["CUDA_VISIBLE_DEVICES"] = str(idx)
                logger.info(f"Using GPU {idx}")
                break

    logger.info("Loading NLI model...")
    nli_model, nli_tokenizer = load_deberta_nli()
    logger.info("NLI model loaded")

    all_70b_results = {}
    for ds_name in ["trivia_qa", "natural_questions"]:
        try:
            result = run_70b_dataset(ds_name, cfg, nli_model, nli_tokenizer)
            all_70b_results[ds_name] = result
        except Exception as e:
            logger.error(f"Failed {ds_name}: {e}", exc_info=True)

    # Load existing 8B results
    small_auroc_path = os.path.join(RESULTS_DIR, "auroc_results.json")
    with open(small_auroc_path) as f:
        existing = json.load(f)

    # Build combined results for gate check
    all_auroc_results = {
        "small": existing.get("small", {}),
        "large": {ds: r["auroc_results"] for ds, r in all_70b_results.items()},
    }

    # Load small UQ scores from pickle
    all_uq_scores = {"small": {}, "large": {}}
    all_correctness_labels = {}
    for ds in ["trivia_qa", "natural_questions"]:
        pkl = os.path.join(RESULTS_DIR, f"uncertainty_scores_small_{ds}.pkl")
        lbl = os.path.join(RESULTS_DIR, f"correctness_labels_{ds}.pkl")
        if os.path.exists(pkl):
            with open(pkl, "rb") as f:
                all_uq_scores["small"][ds] = pickle.load(f)
        if os.path.exists(lbl):
            with open(lbl, "rb") as f:
                all_correctness_labels[ds] = pickle.load(f)
        if ds in all_70b_results:
            all_uq_scores["large"][ds] = all_70b_results[ds]["uq_scores"]

    # Gate check
    logger.info("\n" + "="*60 + "\nRunning MUST_WORK Gate Check...\n" + "="*60)
    gate_pass, condition_results = run_gate_check(
        all_auroc_results, all_uq_scores, all_correctness_labels,
        n_resamples=cfg.evaluation.bootstrap_resamples,
    )
    logger.info(f"Gate: {'PASS' if gate_pass else 'FAIL'}")
    for cond, passed in condition_results.items():
        logger.info(f"  {cond}: {'PASS' if passed else 'FAIL'}")

    # Figures
    figures_dir = os.path.join(BASE_DIR, "figures")
    try:
        generate_all_figures(all_auroc_results, all_uq_scores, all_correctness_labels, figures_dir)
        logger.info(f"Figures saved to {figures_dir}")
    except Exception as e:
        logger.error(f"Figures failed: {e}", exc_info=True)

    # Save final experiment_results.json
    def _safe(obj):
        if isinstance(obj, np.ndarray): return obj.tolist()
        if isinstance(obj, (np.floating, np.integer)): return float(obj)
        return obj

    experiment_results = {
        "hypothesis_id": cfg.hypothesis_id,
        "gate": {"type": "MUST_WORK", "pass": gate_pass, "conditions": condition_results},
        "auroc_summary": {
            mk: {
                ds: {m: {k: v for k, v in res.items() if not isinstance(v, np.ndarray)}
                     for m, res in ds_res.items()}
                for ds, ds_res in model_res.items()
            }
            for mk, model_res in all_auroc_results.items()
        },
        "data_summary": {
            "small": {"trivia_qa": {"n_samples": 500, "correct_rate": 0.660},
                      "natural_questions": {"n_samples": 500, "correct_rate": 0.194}},
            "large": {ds: {"n_samples": r["n_samples"], "correct_rate": r["correct_rate"]}
                      for ds, r in all_70b_results.items()},
        },
        "run_config": {
            "small_n_samples": 10, "large_n_samples": N_SAMPLES_70B,
            "max_samples": MAX_SAMPLES, "seed": cfg.sampling.seed,
        },
        "timing": {"start": start.isoformat(), "end": datetime.now().isoformat(),
                   "duration_seconds": (datetime.now() - start).total_seconds()},
    }

    exp_path = os.path.join(BASE_DIR, "experiment_results.json")
    results_path = os.path.join(RESULTS_DIR, "experiment_results.json")
    for p in [exp_path, results_path]:
        with open(p, "w") as f:
            json.dump(experiment_results, f, indent=2, default=_safe)
    logger.info(f"Results saved: {exp_path}")

    # Update auroc_results.json to include large
    with open(small_auroc_path) as f:
        combined_auroc = json.load(f)
    combined_auroc["large"] = {ds: r["auroc_results"] for ds, r in all_70b_results.items()}
    with open(small_auroc_path, "w") as f:
        json.dump(combined_auroc, f, indent=2, default=_safe)

    logger.info("\n" + "="*60)
    logger.info("EXPERIMENT COMPLETE")
    logger.info(f"Gate: {'PASS' if gate_pass else 'FAIL'}")
    logger.info("="*60)

    if not gate_pass:
        sys.exit(1)


if __name__ == "__main__":
    main()
