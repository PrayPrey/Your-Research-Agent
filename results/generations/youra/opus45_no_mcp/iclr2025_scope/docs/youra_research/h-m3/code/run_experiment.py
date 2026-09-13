#!/usr/bin/env python3
"""Main experiment runner for H-M3: LoRA Adaptation Efficiency vs Landscape Geometry"""

import os
import sys
import json
import torch
import argparse
from datetime import datetime

H_M3_CODE = os.path.dirname(os.path.abspath(__file__))
H_M2_CODE = os.path.join(H_M3_CODE, "..", "..", "h-m2", "code")

sys.path.insert(0, H_M3_CODE)

import config as m3_config
from config import (
    BENCHMARKS, TRAIN_CONFIG, SHARPNESS_CONFIG, RANK_CONFIG, SEEDS, GATE_THRESHOLD,
    CHECKPOINTS_DIR, FIGURES_DIR, H_M3_DIR
)
from rank import compute_model_effective_rank
from evaluate import evaluate_accuracy, compute_generalization_gap
from correlate import compute_spearman, compute_gap_correlation, run_threshold_sensitivity
import m3_visualize as m3_viz

sys.path.insert(0, H_M2_CODE)

import importlib
import data as h_m2_data
import finetune as h_m2_finetune
import sharpness as h_m2_sharpness
import model as h_m2_model

finetune_on_task = h_m2_finetune.finetune_on_task
measure_task_sharpness = h_m2_sharpness.measure_task_sharpness
load_task_loader = h_m2_data.load_task_loader
load_tokenizer = h_m2_model.load_tokenizer


def run_single_seed(seed, tasks=None):
    """Run full pipeline for a single seed."""
    if tasks is None:
        tasks = ["gsm8k", "nq"]

    print(f"\n{'='*60}")
    print(f"Running H-M3 experiment (seed={seed})")
    print(f"{'='*60}")

    torch.manual_seed(seed)

    train_cfg = TRAIN_CONFIG.copy()
    train_cfg["seed"] = seed

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    tokenizer = load_tokenizer()
    print(f"Tokenizer loaded: {tokenizer.__class__.__name__}")

    task_metrics = {}
    models = {}
    loss_curves = {}

    for task_name in tasks:
        print(f"\n{'='*40}")
        print(f"Processing task: {task_name}")
        print(f"{'='*40}")

        print(f"\n[1/4] Fine-tuning on {task_name}...")
        output_dir = os.path.join(CHECKPOINTS_DIR, f"seed_{seed}")
        os.makedirs(output_dir, exist_ok=True)

        ft_result = finetune_on_task(
            task_name=task_name,
            tokenizer=tokenizer,
            train_config=train_cfg,
            output_dir=output_dir,
        )

        model = ft_result["model"]
        models[task_name] = model
        loss_curves[task_name] = ft_result["loss_curve"]

        print(f"\n[2/4] Measuring sharpness for {task_name}...")
        loader = load_task_loader(
            task_name,
            tokenizer,
            max_length=train_cfg["max_length"],
            batch_size=train_cfg["batch_size"],
        )

        sharpness_result = measure_task_sharpness(
            model,
            loader,
            max_batches=SHARPNESS_CONFIG["max_batches"],
            sam_epsilon=SHARPNESS_CONFIG["sam_epsilon"],
        )
        print(f"  Mean sharpness: {sharpness_result['mean_sharpness']:.4f}")

        print(f"\n[3/4] Computing effective rank for {task_name}...")
        rank_result = compute_model_effective_rank(model, RANK_CONFIG["default_threshold"])
        print(f"  Effective rank: {rank_result['effective_rank']}")
        print(f"  Mean effective rank: {rank_result.get('mean_effective_rank', rank_result['effective_rank']):.2f}")

        print(f"\n[4/4] Computing generalization gap for {task_name}...")
        cfg = BENCHMARKS[task_name]

        train_loader = load_task_loader(
            task_name,
            tokenizer,
            max_length=train_cfg["max_length"],
            batch_size=train_cfg["batch_size"],
            split=cfg.get("train_split", "train"),
            num_samples=cfg.get("train_samples", 500),
        )

        test_loader = load_task_loader(
            task_name,
            tokenizer,
            max_length=train_cfg["max_length"],
            batch_size=train_cfg["batch_size"],
            split=cfg["split"],
            num_samples=cfg["num_samples"],
        )

        gap_result = compute_generalization_gap(model, train_loader, test_loader, device)
        print(f"  Train acc: {gap_result['train_acc']:.4f}")
        print(f"  Test acc: {gap_result['test_acc']:.4f}")
        print(f"  Gen gap: {gap_result['gen_gap']:.4f}")

        task_metrics[task_name] = {
            "mean_sharpness": sharpness_result["mean_sharpness"],
            "per_batch_sharpness": sharpness_result["per_batch"],
            "effective_rank": rank_result["effective_rank"],
            "mean_effective_rank": rank_result["mean_effective_rank"],
            "per_module_rank": rank_result["per_module"],
            "singular_values": rank_result["singular_values"],
            "train_acc": gap_result["train_acc"],
            "test_acc": gap_result["test_acc"],
            "gen_gap": gap_result["gen_gap"],
            "loss_curve": ft_result["loss_curve"],
            "checkpoint_path": ft_result["checkpoint_path"],
        }

    print(f"\n{'='*40}")
    print("Computing correlations...")
    print(f"{'='*40}")

    sharpness_vals = [task_metrics[t]["mean_sharpness"] for t in tasks]
    rank_vals = [task_metrics[t]["effective_rank"] for t in tasks]
    gap_vals = [task_metrics[t]["gen_gap"] for t in tasks]

    spearman_result = compute_spearman(sharpness_vals, rank_vals)
    print(f"\nPrimary Gate (sharpness vs effective_rank):")
    print(f"  Spearman rho: {spearman_result['rho']:.4f}")
    print(f"  p-value: {spearman_result['p_value']:.4f}")
    print(f"  Gate pass (rho > {GATE_THRESHOLD}): {spearman_result['gate_pass']}")

    gap_correlation = compute_gap_correlation(sharpness_vals, gap_vals)
    print(f"\nSecondary (sharpness vs gen_gap):")
    print(f"  Spearman rho: {gap_correlation['rho']:.4f}")
    print(f"  p-value: {gap_correlation['p_value']:.4f}")

    return {
        "seed": seed,
        "rho": spearman_result["rho"],
        "p_value": spearman_result["p_value"],
        "gate_pass": spearman_result["gate_pass"],
        "gap_correlation": gap_correlation,
        "task_metrics": task_metrics,
        "models": models,
        "loss_curves": loss_curves,
    }


def main():
    parser = argparse.ArgumentParser(description="H-M3 Experiment: LoRA Efficiency vs Landscape Geometry")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--skip-ablations", action="store_true", help="Skip ablation studies")
    parser.add_argument("--tasks", nargs="+", default=["gsm8k", "nq"], help="Tasks to run")
    args = parser.parse_args()

    os.makedirs(CHECKPOINTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    result = run_single_seed(args.seed, args.tasks)

    task_metrics = result["task_metrics"]
    models = result["models"]
    loss_curves = result["loss_curves"]

    print(f"\n{'='*40}")
    print("Threshold sensitivity analysis (A-1)...")
    print(f"{'='*40}")

    sharpness_map = {t: task_metrics[t]["mean_sharpness"] for t in args.tasks}
    threshold_sensitivity = run_threshold_sensitivity(models, sharpness_map, RANK_CONFIG["thresholds"])

    for threshold, res in threshold_sensitivity.items():
        print(f"  Threshold {threshold}: rho={res['rho']:.4f}, ranks={res['ranks']}")

    print(f"\n{'='*40}")
    print("Generating figures...")
    print(f"{'='*40}")

    figures = []

    fig_path = m3_viz.plot_sharpness_vs_rank(task_metrics, result["rho"])
    figures.append(fig_path)
    print(f"  Saved: {fig_path}")

    sv_dict = {t: task_metrics[t]["singular_values"] for t in args.tasks}
    fig_path = m3_viz.plot_singular_values(sv_dict)
    figures.append(fig_path)
    print(f"  Saved: {fig_path}")

    fig_path = m3_viz.plot_generalization_gap(task_metrics)
    figures.append(fig_path)
    print(f"  Saved: {fig_path}")

    fig_path = m3_viz.plot_training_curves(loss_curves)
    figures.append(fig_path)
    print(f"  Saved: {fig_path}")

    fig_path = m3_viz.plot_correlation_matrix(task_metrics)
    figures.append(fig_path)
    print(f"  Saved: {fig_path}")

    print(f"\n{'='*60}")
    print("EXPERIMENT RESULTS SUMMARY")
    print(f"{'='*60}")

    print(f"\nTask-Level Results:")
    for task in args.tasks:
        tm = task_metrics[task]
        print(f"\n  {task.upper()}:")
        print(f"    Sharpness: {tm['mean_sharpness']:.4f}")
        print(f"    Effective Rank: {tm['effective_rank']}")
        print(f"    Train Acc: {tm['train_acc']:.4f}")
        print(f"    Test Acc: {tm['test_acc']:.4f}")
        print(f"    Gen Gap: {tm['gen_gap']:.4f}")

    print(f"\nCorrelation Results:")
    print(f"  Spearman rho (sharpness vs rank): {result['rho']:.4f}")
    print(f"  Spearman rho (sharpness vs gap): {result['gap_correlation']['rho']:.4f}")

    print(f"\nGate Result:")
    print(f"  MUST_WORK Gate (rho > {GATE_THRESHOLD}): {'PASS' if result['gate_pass'] else 'FAIL'}")

    experiment_results = {
        "hypothesis_id": "h-m3",
        "hypothesis_type": "MECHANISM",
        "timestamp": datetime.now().isoformat(),
        "seed": args.seed,
        "gate": {
            "type": "MUST_WORK",
            "threshold": float(GATE_THRESHOLD),
            "metric": "spearman_rho",
            "value": float(result["rho"]),
            "satisfied": bool(result["gate_pass"]),
            "result": "PASS" if result["gate_pass"] else "FAIL",
        },
        "primary_metrics": {
            "spearman_rho": float(result["rho"]),
            "p_value": float(result["p_value"]) if not (result["p_value"] != result["p_value"]) else None,
        },
        "secondary_metrics": {
            "gap_correlation_rho": float(result["gap_correlation"]["rho"]),
            "gap_correlation_p_value": float(result["gap_correlation"]["p_value"]) if not (result["gap_correlation"]["p_value"] != result["gap_correlation"]["p_value"]) else None,
        },
        "task_metrics": {
            task: {
                "sharpness": float(tm["mean_sharpness"]),
                "effective_rank": int(tm["effective_rank"]),
                "mean_effective_rank": float(tm.get("mean_effective_rank", tm["effective_rank"])),
                "train_acc": float(tm["train_acc"]),
                "test_acc": float(tm["test_acc"]),
                "gen_gap": float(tm["gen_gap"]),
                "loss_curve": [float(x) for x in tm["loss_curve"]],
            }
            for task, tm in task_metrics.items()
        },
        "threshold_sensitivity": {
            str(t): {"rho": float(r["rho"]), "p_value": float(r["p_value"]) if not (r["p_value"] != r["p_value"]) else None, "ranks": {k: int(v) for k,v in r["ranks"].items()}}
            for t, r in threshold_sensitivity.items()
        },
        "figures": figures,
        "config": {
            "train_config": TRAIN_CONFIG,
            "sharpness_config": SHARPNESS_CONFIG,
            "rank_config": RANK_CONFIG,
        },
    }

    results_path = os.path.join(H_M3_DIR, "experiment_results.json")
    with open(results_path, "w") as f:
        json.dump(experiment_results, f, indent=2)
    print(f"\nResults saved: {results_path}")

    return experiment_results


if __name__ == "__main__":
    main()
