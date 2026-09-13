"""Orchestration for H-E1: end-to-end experiment runner."""
import argparse
import json
import logging
import os
import sys

import numpy as np

# Add code dir to path so imports work when run from any directory
_code_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _code_dir)

from data_loader import load_adv_glue, load_glue_clean, load_anli_r3, load_checklist_suites
from fine_tuner import MODEL_CONFIGS, finetune_all, load_pretrained_glue_checkpoint
from evaluator import run_all_evaluations
from delta_star import filter_reliable_categories, build_delta_star_vectors
from statistical_analysis import run_all_analyses
from visualizer import generate_all_figures

logger = logging.getLogger(__name__)

GLUE_TASKS = ["sst2", "mnli", "qqp", "qnli", "rte"]


def _save_json(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, default=lambda x: x.tolist() if hasattr(x, "tolist") else str(x))
    logger.info(f"Saved: {path}")


def _load_json(path):
    with open(path) as f:
        return json.load(f)


def main(
    model_ids=None,
    tasks=None,
    checkpoint_dir="h-e1/checkpoints",
    results_dir="h-e1/results",
    figures_dir="h-e1/figures",
    seed=42,
    skip_finetuning=True,
    n_bootstrap=200,
    n_permutations=1000,
    resume=True,
):
    if model_ids is None:
        model_ids = list(MODEL_CONFIGS.keys())
    if tasks is None:
        tasks = GLUE_TASKS

    os.makedirs(checkpoint_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    # --- Stage 1: Load data ---
    logger.info("=== Stage 1: Loading data ===")
    adv_data_path = os.path.join(results_dir, "adv_data_loaded.json")

    logger.info("Loading AdvGLUE...")
    adv_data = load_adv_glue()

    logger.info("Loading GLUE clean...")
    clean_data = load_glue_clean()

    logger.info("Loading ANLI-R3...")
    anli_data = load_anli_r3()

    logger.info("Loading CheckList suites...")
    checklist_suites = load_checklist_suites()

    # Load GLUE train splits for fine-tuning
    from datasets import load_dataset
    train_data = {}
    for task in tasks:
        try:
            ds = load_dataset("glue", task)
            train_data[task] = ds["train"]
        except Exception as e:
            logger.warning(f"Could not load train split for {task}: {e}")

    data = {"train": train_data, "eval": clean_data}

    # --- Stage 2: Fine-tuning (or load pre-trained) ---
    finetuned_path = os.path.join(results_dir, "finetuned.json")
    if resume and os.path.exists(finetuned_path):
        logger.info(f"Resuming: loading finetuned from {finetuned_path}")
        finetuned_raw = _load_json(finetuned_path)
        # Convert list to tuple
        finetuned = {
            m: {t: tuple(v) for t, v in tasks_dict.items()}
            for m, tasks_dict in finetuned_raw.items()
        }
    else:
        logger.info("=== Stage 2: Fine-tuning / loading checkpoints ===")
        # Use textattack shortcuts where available; fine-tune the rest
        # For PoC: only fine-tune models that have no shortcut (OPT models)
        # Models with shortcuts use pre-trained; others use 1 task fine-tune if needed
        finetuned = finetune_all(
            model_ids=model_ids,
            tasks=tasks,
            data=data,
            checkpoint_dir=checkpoint_dir,
            seed=seed,
            skip_finetuning=skip_finetuning,
        )

        # For models without textattack shortcuts: fine-tune on sst2 only (fast, ~872 val examples)
        # OPT-125m, OPT-350m, GPT-2 (extra tasks), T5, BART all get sst2 fine-tune if missing
        finetune_task = "sst2"  # smallest + fastest
        if not skip_finetuning:
            pass  # already handled in finetune_all
        else:
            for model_id in model_ids:
                hub_id = load_pretrained_glue_checkpoint(model_id, finetune_task)
                if hub_id:
                    # Already covered by textattack shortcut
                    continue
                if model_id not in finetuned:
                    finetuned[model_id] = {}
                if finetune_task not in finetuned.get(model_id, {}) and finetune_task in data.get("train", {}):
                    logger.info(f"Fine-tuning {model_id}/{finetune_task} (no shortcut available)")
                    # Use subset for speed: 5000 train examples max
                    train_subset = data["train"][finetune_task].select(range(min(5000, len(data["train"][finetune_task]))))
                    try:
                        ckpt_path, clean_acc = finetune_model(
                            model_id, finetune_task, train_subset,
                            data["eval"][finetune_task], checkpoint_dir, seed
                        )
                        finetuned[model_id][finetune_task] = (ckpt_path, clean_acc)
                    except Exception as e:
                        logger.error(f"Fine-tuning failed {model_id}/{finetune_task}: {e}")
                        finetuned[model_id][finetune_task] = (None, None)

        _save_json(finetuned, finetuned_path)

    # --- Stage 3: Adversarial evaluation ---
    eval_path = os.path.join(results_dir, "eval_results.json")
    if resume and os.path.exists(eval_path):
        logger.info(f"Resuming: loading eval results from {eval_path}")
        eval_results = _load_json(eval_path)
    else:
        logger.info("=== Stage 3: Adversarial evaluation ===")
        eval_results = run_all_evaluations(
            finetuned=finetuned,
            adv_data=adv_data,
            anli_data=anli_data,
            checklist_suites=checklist_suites,
            clean_data=clean_data,
            checkpoint_dir=checkpoint_dir,
        )
        _save_json(eval_results, eval_path)

    # --- Stage 4: Δ* computation ---
    delta_path = os.path.join(results_dir, "delta_star.json")
    if resume and os.path.exists(delta_path):
        logger.info(f"Resuming: loading delta_star from {delta_path}")
        delta_data = _load_json(delta_path)
        X = np.array(delta_data["X"])
        reliable_categories = delta_data["reliable_categories"]
        model_ids_used = delta_data["model_ids"]
        family_labels = delta_data["family_labels"]
    else:
        logger.info("=== Stage 4: Δ* computation ===")
        reliable_categories = filter_reliable_categories(
            eval_results, min_r=0.7, min_n=50
        )

        # Fallback: if no categories pass filter, use all with data
        if len(reliable_categories) < 2:
            logger.warning("Fewer than 2 reliable categories — using all categories with data")
            from evaluator import ATTACK_CATEGORIES
            reliable_categories = []
            for model_results in eval_results.values():
                for entry in model_results.values():
                    cat = entry.get("category")
                    if cat and cat not in reliable_categories:
                        reliable_categories.append(cat)
            logger.info(f"Using fallback categories: {reliable_categories}")

        X, model_ids_used, family_labels = build_delta_star_vectors(eval_results, reliable_categories)

        delta_data = {
            "X": X.tolist(),
            "reliable_categories": reliable_categories,
            "model_ids": model_ids_used,
            "family_labels": family_labels,
        }
        _save_json(delta_data, delta_path)

    logger.info(f"Δ*-vector matrix: {X.shape}, categories: {reliable_categories}")
    logger.info(f"Models: {model_ids_used}")
    logger.info(f"Families: {family_labels}")

    # --- Stage 5: Statistical analysis ---
    stats_path = os.path.join(results_dir, "stats_results.json")
    if resume and os.path.exists(stats_path):
        logger.info(f"Resuming: loading stats from {stats_path}")
        stats_results = _load_json(stats_path)
    else:
        logger.info("=== Stage 5: Statistical analysis ===")
        stats_results = run_all_analyses(
            X=X,
            model_ids=model_ids_used,
            family_labels=family_labels,
            reliable_categories=reliable_categories,
            results_raw=eval_results,
            n_bootstrap=n_bootstrap,
            n_permutations=n_permutations,
        )
        _save_json(stats_results, stats_path)

    # --- Stage 6: Visualization ---
    logger.info("=== Stage 6: Generating visualizations ===")
    generate_all_figures(
        X=X,
        model_ids=model_ids_used,
        family_labels=family_labels,
        reliable_categories=reliable_categories,
        stats_results=stats_results,
        figures_dir=figures_dir,
    )

    # --- Summary ---
    summary = {
        "n_models": len(model_ids_used),
        "model_ids": model_ids_used,
        "family_labels": family_labels,
        "n_reliable_categories": len(reliable_categories),
        "reliable_categories": reliable_categories,
        "delta_star_matrix_shape": list(X.shape),
        "permutation_manova": {
            "eta_squared": stats_results.get("permutation_manova", {}).get("eta_squared"),
            "p_value": stats_results.get("permutation_manova", {}).get("p_value"),
        },
        "lomo_accuracy": stats_results.get("lomo", {}).get("accuracy"),
        "gate_eta_fraction_above_015": stats_results.get("gate_eta_fraction_above_015"),
        "gate_manova_satisfied": stats_results.get("gate_manova_satisfied"),
        "gate_interaction_ci_excludes_zero": stats_results.get("gate_interaction_ci_excludes_zero"),
        "gate_full_satisfied": stats_results.get("gate_full_satisfied"),
        "gate_poc_pass": stats_results.get("gate_poc_pass"),
    }
    _save_json(summary, os.path.join(results_dir, "summary.json"))

    logger.info("=== EXPERIMENT COMPLETE ===")
    logger.info(f"Gate (MUST_WORK): {summary.get('gate_full_satisfied')}")
    logger.info(f"PoC pass: {summary.get('gate_poc_pass')}")
    logger.info(f"MANOVA eta^2={summary['permutation_manova']['eta_squared']}, "
                f"p={summary['permutation_manova']['p_value']}")
    logger.info(f"LOMO accuracy={summary['lomo_accuracy']}")

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint_dir", default="h-e1/checkpoints")
    parser.add_argument("--results_dir", default="h-e1/results")
    parser.add_argument("--figures_dir", default="h-e1/figures")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--skip_finetuning", action="store_true", default=True)
    parser.add_argument("--no_skip_finetuning", dest="skip_finetuning", action="store_false")
    parser.add_argument("--n_bootstrap", type=int, default=200)
    parser.add_argument("--n_permutations", type=int, default=1000)
    parser.add_argument("--no_resume", action="store_true", default=False)
    parser.add_argument("--models", nargs="+", default=None)
    parser.add_argument("--tasks", nargs="+", default=None)
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )

    summary = main(
        model_ids=args.models,
        tasks=args.tasks,
        checkpoint_dir=args.checkpoint_dir,
        results_dir=args.results_dir,
        figures_dir=args.figures_dir,
        seed=args.seed,
        skip_finetuning=args.skip_finetuning,
        n_bootstrap=args.n_bootstrap,
        n_permutations=args.n_permutations,
        resume=not args.no_resume,
    )

    print("\n=== FINAL SUMMARY ===")
    print(json.dumps(summary, indent=2, default=str))
