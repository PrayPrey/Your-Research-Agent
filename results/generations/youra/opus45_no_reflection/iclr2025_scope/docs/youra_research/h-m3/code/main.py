#!/usr/bin/env python3
"""H-M3 Main Orchestration - Train, Evaluate, Analyze, Report"""
import os
import sys
import json
import argparse
from datetime import datetime

# Add code directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ExperimentConfig
from model import load_teacher, load_student_base
from train import train_all_conditions, load_checkpoint
from data_eval import load_longbench_tasks, bucket_by_length
from metrics import evaluate_condition, f1_retention, aggregate_scores
from stats import run_two_way_anova, per_length_ttest, evaluate_gate
from visualize import generate_all_figures
import os as _os

def load_trained_models(config, teacher):
    """Load trained student models from checkpoints."""
    models = {}
    for objective in config.objectives:
        for length in config.lengths:
            key = f"{objective}_{length}"
            ckpt_dir = _os.path.join(config.checkpoint_dir, key)
            ckpt_path = _os.path.join(ckpt_dir, "latest.pt")
            if _os.path.exists(ckpt_path):
                student = load_student_base(config)
                from torch.optim import AdamW
                opt = AdamW(student.parameters(), lr=config.lr)
                load_checkpoint(ckpt_dir, student, None, opt)
                models[key] = student
                print(f"  Loaded checkpoint: {key}")
    return models

def main():
    parser = argparse.ArgumentParser(description="H-M3: Objective x Length F1 Retention Experiment")
    parser.add_argument("--smoke", action="store_true", help="Run in smoke/PoC mode")
    parser.add_argument("--skip-train", action="store_true", help="Skip training, use existing checkpoints")
    parser.add_argument("--eval-only", action="store_true", help="Only run evaluation")
    args = parser.parse_args()

    config = ExperimentConfig()
    config.smoke_mode = args.smoke or True  # Default to smoke for PoC

    print("=" * 60)
    print("H-M3: Token-level vs Matrix-level F1 Retention")
    print("=" * 60)
    print(f"Mode: {'SMOKE/PoC' if config.smoke_mode else 'FULL'}")
    print(f"Objectives: {config.objectives}")
    print(f"Lengths: {config.lengths}")
    print(f"Tokens/condition: {config.tokens_per_condition:,}")
    print("=" * 60)

    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)
    os.makedirs(config.checkpoint_dir, exist_ok=True)

    # Phase 1: Training (skip if eval-only)
    if not args.eval_only and not args.skip_train:
        print("\n[Phase 1] Training 6 conditions...")
        models, tokenizer = train_all_conditions(config)
    else:
        print("\n[Phase 1] Loading existing checkpoints for evaluation...")
        teacher, tokenizer = load_teacher(config)
        models = load_trained_models(config, teacher)
        if not models:
            raise RuntimeError("No trained models found. Run training first (remove --eval-only flag).")

    # Phase 2: Data Loading
    print("\n[Phase 2] Loading LongBench QA tasks...")
    all_tasks = load_longbench_tasks(config)
    total_samples = sum(len(s) for s in all_tasks.values())
    print(f"  Loaded {total_samples} samples across {len(all_tasks)} tasks")

    # Bucket by length
    all_samples = []
    for task_samples in all_tasks.values():
        all_samples.extend(task_samples)
    samples_by_length = bucket_by_length(all_samples, tokenizer, config.lengths)
    for length, samples in samples_by_length.items():
        print(f"  {length//1000}K bucket: {len(samples)} samples")

    # Phase 3: Evaluation
    print("\n[Phase 3] Evaluating all conditions...")
    results = {}
    f1_scores_for_anova = {}

    # Get teacher baseline
    teacher, _ = load_teacher(config)
    teacher_scores = {}
    for length in config.lengths:
        max_eval = config.smoke_eval_samples if config.smoke_mode else None
        scores = evaluate_condition(teacher, tokenizer, samples_by_length, length, max_eval)
        teacher_scores[length] = aggregate_scores(scores)
        print(f"  Teacher@{length//1000}K: F1={teacher_scores[length]*100:.1f}%")

    # Evaluate each trained condition with REAL model inference
    import numpy as np
    np.random.seed(config.seed)

    for objective in config.objectives:
        for length in config.lengths:
            key = f"{objective}_{length}"

            model = models.get(key)
            if model is None:
                raise RuntimeError(f"No trained model for {key}. Run training first.")

            max_eval = config.smoke_eval_samples if config.smoke_mode else None
            scores_by_task = evaluate_condition(model, tokenizer, samples_by_length, length, max_eval)
            mean_f1 = aggregate_scores(scores_by_task)
            base_f1 = teacher_scores.get(length, 0.5)
            retention = f1_retention(mean_f1, base_f1)

            all_scores = [s for task_scores in scores_by_task.values() for s in task_scores]
            results[key] = {
                "f1_mean": mean_f1 * 100,
                "retention": [retention] * len(all_scores),
                "raw_scores": all_scores,
            }
            f1_scores_for_anova[key] = all_scores

            print(f"  {objective.upper()}@{length//1000}K: F1={mean_f1*100:.1f}%, Retention={retention:.1f}%")

    # Phase 4: Statistical Analysis
    print("\n[Phase 4] Statistical Analysis...")
    anova_result = run_two_way_anova(f1_scores_for_anova)
    print(f"  ANOVA Interaction p-value: {anova_result.get('interaction_p', 'N/A'):.4f}")

    ttests = {}
    for length in config.lengths:
        mohawk_scores = f1_scores_for_anova.get(f"mohawk_{length}", [])
        cab_scores = f1_scores_for_anova.get(f"cab_{length}", [])
        ttests[length] = per_length_ttest(cab_scores, mohawk_scores)
        print(f"  {length//1000}K: CAB-MOHAWK diff = {ttests[length]['diff']:.2f} F1 points (p={ttests[length]['p_value']:.4f})")

    gate_result = evaluate_gate(anova_result, ttests)
    print(f"\n  GATE VERDICT: {gate_result['verdict']}")
    print(f"    Interaction significant: {gate_result['criteria']['interaction_significant']}")
    print(f"    P2 (16K) pass: {gate_result['criteria']['p2_pass']} (diff={gate_result['criteria']['p2_diff']:.2f})")
    print(f"    P3 (32K) pass: {gate_result['criteria']['p3_pass']} (diff={gate_result['criteria']['p3_diff']:.2f})")

    # Phase 5: Visualization
    print("\n[Phase 5] Generating figures...")
    figures = generate_all_figures(results, {}, config.figures_dir)
    for fig in figures:
        print(f"  Saved: {fig}")

    # Phase 6: Save Results
    print("\n[Phase 6] Saving results...")
    experiment_results = {
        "hypothesis_id": "h-m3",
        "experiment_date": datetime.now().isoformat(),
        "config": {
            "smoke_mode": config.smoke_mode,
            "objectives": config.objectives,
            "lengths": config.lengths,
            "tokens_per_condition": config.tokens_per_condition,
        },
        "results": {k: {"f1_mean": v["f1_mean"], "retention_mean": np.mean(v["retention"])}
                    for k, v in results.items()},
        "teacher_baseline": {str(k): v * 100 for k, v in teacher_scores.items()},
        "anova": {k: float(v) if isinstance(v, (int, float, np.floating)) else v
                  for k, v in anova_result.items() if k != "anova_table"},
        "ttests": {str(k): {kk: float(vv) if isinstance(vv, (int, float, np.floating)) else vv
                           for kk, vv in v.items()}
                   for k, v in ttests.items()},
        "gate": gate_result,
        "figures": figures,
    }

    results_path = os.path.join(config.output_dir, "experiment_results.json")
    with open(results_path, "w") as f:
        json.dump(experiment_results, f, indent=2, default=str)
    print(f"  Results: {results_path}")

    # Final Summary
    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"Gate Result: {gate_result['verdict']}")
    print(f"Interaction p-value: {anova_result.get('interaction_p', 'N/A'):.4f}")
    print(f"16K CAB advantage: {ttests[16384]['diff']:.2f} F1 points")
    print(f"32K CAB advantage: {ttests[32768]['diff']:.2f} F1 points")
    print("=" * 60)

    return gate_result["gate_pass"]

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
