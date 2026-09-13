"""
eval_from_checkpoint.py — Compute UQ scores and AUROC from existing generation checkpoints.

Uses already-generated data in checkpoints/ to skip expensive LLM inference.
Runs UQ computation (NLI-based SE/KLE) + AUROC evaluation on checkpointed data.

Usage:
    python eval_from_checkpoint.py --config ../config/h-e1.yaml [--max-samples N]
"""
import argparse
import json
import logging
import os
import pickle
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(__file__))

from config import ExperimentConfig, load_config
from data_loader import compute_exact_match, get_dataset
from evaluate import evaluate_all, run_gate_check, save_results
from generate import GenerationResult
from model_loader import load_deberta_nli
from uq_methods import compute_all_uq, verify_se_mechanism
from visualize import generate_all_figures

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def load_generation_checkpoint(ckpt_path: str) -> Optional[List[GenerationResult]]:
    """Load generation checkpoint if it exists."""
    if os.path.exists(ckpt_path):
        with open(ckpt_path, "rb") as f:
            results = pickle.load(f)
        logger.info(f"Loaded {len(results)} results from {ckpt_path}")
        return results
    return None


def process_model_dataset(
    model_key: str,
    dataset_name: str,
    cfg: ExperimentConfig,
    nli_model: Any,
    nli_tokenizer: Any,
    base_dir: str,
    max_samples: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """Process one model x dataset using existing checkpoint."""

    ckpt_dir = os.path.join(base_dir, "checkpoints")
    ckpt_path = os.path.join(ckpt_dir, f"gen_{model_key}_{dataset_name}.pkl")

    results = load_generation_checkpoint(ckpt_path)
    if results is None:
        logger.error(f"No checkpoint found: {ckpt_path}")
        return None

    # Load dataset for gold answers (needed for correctness labels)
    logger.info(f"Loading dataset {dataset_name} for gold answers...")
    items = get_dataset(dataset_name, n_few_shot=cfg.sampling.n_few_shot)
    logger.info(f"Dataset has {len(items)} items, checkpoint has {len(results)} results")

    # Build question_id -> gold_answers lookup for reliable alignment
    id_to_gold = {item["question_id"]: item["gold_answers"] for item in items}

    # Filter results to those with matching gold answers
    aligned = [(r, id_to_gold[r.question_id]) for r in results if r.question_id in id_to_gold]
    if not aligned:
        # Fall back to positional alignment
        logger.warning("No question_id matches found, falling back to positional alignment")
        n_use = min(len(results), len(items))
        if max_samples and max_samples < n_use:
            n_use = max_samples
        aligned = list(zip(results[:n_use], [items[i]["gold_answers"] for i in range(n_use)]))
    else:
        if max_samples and max_samples < len(aligned):
            aligned = aligned[:max_samples]
        n_use = len(aligned)

    logger.info(f"Processing {n_use} queries for {model_key}/{dataset_name}")

    # Compute correctness labels
    correctness_labels = np.array([
        compute_exact_match(r.greedy_text, gold)
        for r, gold in aligned
    ])
    results = [r for r, _ in aligned]
    correct_rate = correctness_labels.mean()
    logger.info(f"Correctness rate: {correct_rate:.3f} ({int(correctness_labels.sum())}/{n_use})")

    if len(np.unique(correctness_labels)) < 2:
        logger.warning(f"Only one class in correctness labels - AUROC undefined. "
                       f"Correct={int(correctness_labels.sum())}, N={n_use}")
        # Still proceed - run_gate_check handles this gracefully

    # Compute UQ scores
    logger.info("Computing UQ scores (SE, KLE, token-prob, SelfCheck, SEPs)...")
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
        "n_samples": n_use,
    }


def generate_nq_data(
    cfg: ExperimentConfig,
    nli_model: Any,
    nli_tokenizer: Any,
    base_dir: str,
    max_samples: int = 500,
) -> Optional[Dict[str, Any]]:
    """Generate NQ data from scratch (small subset) since no checkpoint exists."""
    from model_loader import get_model
    from generate import generate_dataset

    model_key = "small"
    dataset_name = "natural_questions"
    ckpt_dir = os.path.join(base_dir, "checkpoints")
    os.makedirs(ckpt_dir, exist_ok=True)
    ckpt_path = os.path.join(ckpt_dir, f"gen_{model_key}_{dataset_name}.pkl")

    # Load dataset
    logger.info(f"Loading dataset {dataset_name}...")
    items = get_dataset(dataset_name, n_few_shot=cfg.sampling.n_few_shot)
    items = items[:max_samples]
    logger.info(f"Using {len(items)} NQ items")

    # Load model
    model_cfg = cfg.models[model_key]
    logger.info(f"Loading model {model_key} ({model_cfg.hf_id})...")
    model, tokenizer = get_model(model_key, model_cfg)
    logger.info("Model loaded")

    batch_size = cfg.evaluation.batch_size_8b

    # Generate
    logger.info(f"Generating {len(items)} NQ queries (batch={batch_size}, n_samples=10)...")
    results = generate_dataset(
        model=model, tokenizer=tokenizer, dataset=items,
        cfg=cfg.sampling, batch_size=batch_size,
        checkpoint_path=ckpt_path, checkpoint_every=100,
    )
    logger.info(f"NQ generation complete: {len(results)} results")

    del model
    del tokenizer
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # Compute correctness labels (positional alignment - items were ordered for generation)
    correctness_labels = np.array([
        compute_exact_match(r.greedy_text, items[i]["gold_answers"])
        for i, r in enumerate(results)
        if i < len(items)
    ])
    correct_rate = correctness_labels.mean()
    logger.info(f"NQ correctness: {correct_rate:.3f} ({int(correctness_labels.sum())}/{len(correctness_labels)})")

    # UQ scores
    logger.info("Computing NQ UQ scores...")
    uq_scores, cluster_counts = compute_all_uq(results, nli_model, nli_tokenizer)
    se_ok, se_stats = verify_se_mechanism(cluster_counts, n_samples=cfg.sampling.n_samples)
    logger.info(f"NQ SE mechanism: ok={se_ok}, stats={se_stats}")

    # AUROC
    logger.info("Evaluating NQ AUROC...")
    auroc_results = evaluate_all(uq_scores, correctness_labels, cfg, dataset_name, model_key)

    results_dir = os.path.join(base_dir, "results")
    save_results(auroc_results, uq_scores, correctness_labels, dataset_name, model_key, results_dir)

    return {
        "auroc_results": auroc_results,
        "uq_scores": uq_scores,
        "correctness_labels": correctness_labels,
        "se_mechanism": {"ok": se_ok, "stats": se_stats},
        "correct_rate": float(correct_rate),
        "n_samples": len(results),
    }


def main(config_path: str, max_samples: Optional[int] = None) -> None:
    start_time = datetime.now()
    logger.info("Phase 4 Eval-from-Checkpoint: h-e1 UQ Existence Verification")
    logger.info(f"Config: {config_path}")
    logger.info(f"Start: {start_time.isoformat()}")
    if max_samples:
        logger.info(f"Max samples per dataset: {max_samples}")

    cfg = load_config(config_path)
    base_dir = os.path.dirname(config_path)  # h-e1/ (config is in h-e1/config/)
    base_dir = os.path.dirname(base_dir)     # go up from config/ to h-e1/

    # Pick GPU
    if torch.cuda.is_available():
        import subprocess
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,memory.used", "--format=csv,noheader,nounits"],
            capture_output=True, text=True
        )
        available_gpu = None
        for line in result.stdout.strip().split("\n"):
            parts = line.split(",")
            idx, mem = int(parts[0].strip()), int(parts[1].strip())
            if mem < 1000:
                available_gpu = idx
                break
        if available_gpu is not None:
            os.environ["CUDA_VISIBLE_DEVICES"] = str(available_gpu)
            logger.info(f"Using GPU {available_gpu}")

    # Load NLI model once
    logger.info("Loading NLI model (DeBERTa-large-mnli)...")
    nli_model, nli_tokenizer = load_deberta_nli()
    logger.info("NLI model loaded")

    all_auroc_results: Dict[str, Any] = {"small": {}}
    all_uq_scores: Dict[str, Dict[str, Any]] = {"small": {}}
    all_correctness_labels: Dict[str, Any] = {}

    # ── TriviaQA: Use checkpoint if gold-aligned, else generate fresh ─────────
    logger.info("\n" + "=" * 60)
    tqa_max = max_samples if max_samples else 500
    tqa_ckpt = os.path.join(base_dir, "checkpoints", "gen_small_trivia_qa.pkl")
    tqa_result = None

    if os.path.exists(tqa_ckpt):
        logger.info("TriviaQA checkpoint found - checking gold answer alignment...")
        tqa_result = process_model_dataset(
            "small", "trivia_qa", cfg, nli_model, nli_tokenizer, base_dir,
            max_samples=tqa_max,
        )
        if tqa_result and tqa_result["correct_rate"] == 0.0:
            logger.warning("TriviaQA correctness=0 after fix - checkpoint may be from wrong split")
            logger.info("Falling back to fresh generation for TriviaQA...")
            tqa_result = None

    if tqa_result is None:
        logger.info(f"Generating TriviaQA fresh (max={tqa_max} samples)...")
        # Save fresh checkpoint to a new path to avoid overwriting misaligned data
        from model_loader import get_model
        from generate import generate_dataset
        items = get_dataset("trivia_qa", n_few_shot=cfg.sampling.n_few_shot)
        items = items[:tqa_max]
        logger.info(f"Using {len(items)} TriviaQA items from validation split")
        model_cfg = cfg.models["small"]
        logger.info(f"Loading 8B model ({model_cfg.hf_id})...")
        model, tokenizer = get_model("small", model_cfg)
        logger.info("Model loaded")
        fresh_ckpt = os.path.join(base_dir, "checkpoints", "gen_small_trivia_qa_valid.pkl")
        results_gen = generate_dataset(
            model=model, tokenizer=tokenizer, dataset=items,
            cfg=cfg.sampling, batch_size=cfg.evaluation.batch_size_8b,
            checkpoint_path=fresh_ckpt, checkpoint_every=100,
        )
        logger.info(f"Generation complete: {len(results_gen)} results")
        del model
        del tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        # Evaluate
        correctness_labels_tqa = np.array([
            compute_exact_match(r.greedy_text, items[i]["gold_answers"])
            for i, r in enumerate(results_gen)
            if i < len(items)
        ])
        correct_rate_tqa = correctness_labels_tqa.mean()
        logger.info(f"TriviaQA fresh correctness: {correct_rate_tqa:.3f} ({int(correctness_labels_tqa.sum())}/{len(correctness_labels_tqa)})")
        logger.info("Computing UQ scores...")
        uq_scores_tqa, cluster_counts_tqa = compute_all_uq(results_gen, nli_model, nli_tokenizer)
        se_ok_tqa, se_stats_tqa = verify_se_mechanism(cluster_counts_tqa, n_samples=cfg.sampling.n_samples)
        auroc_results_tqa = evaluate_all(uq_scores_tqa, correctness_labels_tqa, cfg, "trivia_qa", "small")
        results_dir = os.path.join(base_dir, "results")
        save_results(auroc_results_tqa, uq_scores_tqa, correctness_labels_tqa, "trivia_qa", "small", results_dir)
        tqa_result = {
            "auroc_results": auroc_results_tqa,
            "uq_scores": uq_scores_tqa,
            "correctness_labels": correctness_labels_tqa,
            "se_mechanism": {"ok": se_ok_tqa, "stats": se_stats_tqa},
            "correct_rate": float(correct_rate_tqa),
            "n_samples": len(correctness_labels_tqa),
        }

    if tqa_result:
        all_auroc_results["small"]["trivia_qa"] = tqa_result["auroc_results"]
        all_uq_scores["small"]["trivia_qa"] = tqa_result["uq_scores"]
        all_correctness_labels["trivia_qa"] = tqa_result["correctness_labels"]
        logger.info(f"TriviaQA done: n={tqa_result['n_samples']}, "
                    f"correct_rate={tqa_result['correct_rate']:.3f}")
    else:
        logger.error("TriviaQA processing failed")

    # ── NaturalQuestions: Generate fresh subset ────────────────────────────────
    logger.info("\n" + "=" * 60)
    nq_ckpt = os.path.join(base_dir, "checkpoints", "gen_small_natural_questions.pkl")
    nq_max = max_samples if max_samples else 500

    if os.path.exists(nq_ckpt):
        logger.info("NQ checkpoint found - using existing data")
        nq_result = process_model_dataset(
            "small", "natural_questions", cfg, nli_model, nli_tokenizer, base_dir,
            max_samples=nq_max,
        )
    else:
        logger.info(f"Generating NQ fresh (max={nq_max} samples)...")
        nq_result = generate_nq_data(cfg, nli_model, nli_tokenizer, base_dir, max_samples=nq_max)

    if nq_result:
        all_auroc_results["small"]["natural_questions"] = nq_result["auroc_results"]
        all_uq_scores["small"]["natural_questions"] = nq_result["uq_scores"]
        all_correctness_labels["natural_questions"] = nq_result["correctness_labels"]
        logger.info(f"NQ done: n={nq_result['n_samples']}, "
                    f"correct_rate={nq_result['correct_rate']:.3f}")
    else:
        logger.error("NQ processing failed")

    # ── Gate Check ─────────────────────────────────────────────────────────────
    logger.info("\n" + "=" * 60)
    logger.info("Running MUST_WORK Gate Check...")
    gate_pass, condition_results = run_gate_check(
        all_auroc_results, all_uq_scores, all_correctness_labels,
        n_resamples=cfg.evaluation.bootstrap_resamples,
    )
    logger.info(f"Gate result: {'PASS' if gate_pass else 'FAIL'}")
    for cond, passed in condition_results.items():
        logger.info(f"  {cond}: {'PASS' if passed else 'FAIL'}")

    # ── Figures ────────────────────────────────────────────────────────────────
    figures_dir = os.path.join(base_dir, "figures")
    try:
        generate_all_figures(all_auroc_results, all_uq_scores, all_correctness_labels, figures_dir)
        logger.info(f"Figures saved to {figures_dir}")
    except Exception as e:
        logger.error(f"Figure generation failed: {e}", exc_info=True)

    # ── Save experiment_results.json ───────────────────────────────────────────
    end_time = datetime.now()

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
        "data_summary": {
            "trivia_qa": {
                "n_samples": int(tqa_result["n_samples"]) if tqa_result else 0,
                "correct_rate": float(tqa_result["correct_rate"]) if tqa_result else None,
                "source": "checkpoint (5500 pre-generated)",
            },
            "natural_questions": {
                "n_samples": int(nq_result["n_samples"]) if nq_result else 0,
                "correct_rate": float(nq_result["correct_rate"]) if nq_result else None,
                "source": f"fresh generation ({nq_max} samples)",
            },
        },
        "run_config": {
            "n_samples": cfg.sampling.n_samples,
            "temperature": cfg.sampling.temperature,
            "seed": cfg.sampling.seed,
            "bootstrap_resamples": cfg.evaluation.bootstrap_resamples,
            "models": {"small": cfg.models["small"].hf_id},
            "note": "Phase 4 PoC — 8B only. 70B to be added in Phase 5.",
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
    logger.info(f"Results saved: {exp_results_path}")

    # Pipeline-level path
    pipeline_path = os.path.join(base_dir, "experiment_results.json")
    with open(pipeline_path, "w") as f:
        json.dump(experiment_results, f, indent=2, default=_json_safe)

    logger.info("\n" + "=" * 60)
    logger.info("EXPERIMENT COMPLETE")
    logger.info(f"Gate: {'PASS' if gate_pass else 'FAIL'}")
    logger.info(f"Duration: {(end_time - start_time).total_seconds():.0f}s")
    logger.info("=" * 60)

    if not gate_pass:
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default=os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "config", "h-e1.yaml"
        ),
    )
    parser.add_argument("--max-samples", type=int, default=None,
                        help="Max samples per dataset (default: use full checkpoint)")
    args = parser.parse_args()
    main(args.config, args.max_samples)
