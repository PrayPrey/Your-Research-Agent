"""Main experiment runner for H-M1 reward conflation analysis."""

import os
import sys
import json
import math
import torch
import numpy as np
from datetime import datetime
from tqdm import tqdm

from config import CONFIG
from data import load_all_tasks, Task
from inference import load_model, get_length_normalized_logprob
from task_classifier import classify_all_tasks, get_classification_summary
from overlap_analysis import (
    analyze_conflation, cross_model_overlap, per_dataset_overlap,
    cluster_task_correlation
)
from visualize import (
    plot_gate_metrics, plot_confidence_histograms,
    plot_cross_model_heatmap, plot_cluster_correlation_scatter,
    plot_per_dataset_overlap
)


def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def extract_confidence_for_tasks(model, tokenizer, tasks, batch_size: int = 8):
    """Extract confidence (exp of normalized logprob) for each task's correct answer."""
    confidences = {}
    for task in tqdm(tasks, desc="Extracting confidence"):
        try:
            logprob_norm = get_length_normalized_logprob(
                model, tokenizer, task["question"], task["correct_answer"]
            )
            conf = math.exp(logprob_norm)
            conf = min(conf, 1.0)  # Clip overflow
            confidences[task["task_id"]] = conf
        except Exception as e:
            print(f"Error on {task['task_id']}: {e}")
            confidences[task["task_id"]] = 0.0
    return confidences


def run_all_models_confidence(tasks, model_ids):
    """Run confidence extraction for all models."""
    result = {}
    for model_id in model_ids:
        print(f"\n{'='*60}")
        print(f"Model: {model_id}")
        print('='*60)

        model, tokenizer = load_model(model_id)
        conf = extract_confidence_for_tasks(model, tokenizer, tasks, CONFIG.batch_size)
        result[model_id] = conf

        # Free memory
        del model
        torch.cuda.empty_cache()
        print(f"Completed {model_id}, extracted {len(conf)} confidences")

    return result


def load_he1_cluster_labels(path: str):
    """Load cluster labels from H-E1 results."""
    with open(path, 'r') as f:
        he1 = json.load(f)
    return {t["task_id"]: t["cluster_label"] for t in he1["per_task"]}


def build_results(
    task_types, conf_by_model, conflation, cross_model,
    dataset_overlap, cluster_corr, classification_summary
):
    """Build results dictionary matching expected schema."""
    primary_model = CONFIG.models[CONFIG.primary_model_index]

    # Per-task data
    per_task = []
    for task_id, task_type in task_types.items():
        entry = {
            "task_id": task_id,
            "task_type": task_type,
        }
        for model_id, conf_dict in conf_by_model.items():
            short_name = model_id.split('/')[-1].replace('-', '_')[:15]
            entry[f"confidence_{short_name}"] = conf_dict.get(task_id, None)
        per_task.append(entry)

    return {
        "aggregate": {
            "gate_pass": conflation["gate_pass"],
            "gate_fail": conflation["gate_fail"],
            "overlap": conflation["overlap"],
            "mean_diff": conflation["diff"],
            "mean_confidence_type_a": conflation["mean_a"],
            "mean_confidence_type_b": conflation["mean_b"],
            "std_type_a": conflation["std_a"],
            "std_type_b": conflation["std_b"],
            "n_type_a": conflation["n_a"],
            "n_type_b": conflation["n_b"],
            "cross_model_overlap": cross_model,
            "per_dataset_overlap": dataset_overlap,
            "cluster_correlation": {
                "r": cluster_corr[0],
                "p": cluster_corr[1],
                "supporting": cluster_corr[0] > CONFIG.correlation_supporting_threshold
            },
            "classification_summary": classification_summary,
            "primary_model": primary_model,
            "models_evaluated": CONFIG.models,
            "bidir_threshold": CONFIG.bidir_score_threshold,
            "timestamp": datetime.now().isoformat()
        },
        "per_task": per_task
    }


def main():
    """Run full H-M1 experiment pipeline."""
    print("="*60)
    print("H-M1: RLHF Reward Signal Conflation Analysis")
    print("="*60)

    set_seed(CONFIG.seed)

    # Step 1: Load tasks
    print("\n[1/8] Loading tasks...")
    tasks = load_all_tasks()
    print(f"Loaded {len(tasks)} tasks")

    # Step 2: Classify tasks
    print("\n[2/8] Classifying tasks into Type A/B...")
    task_types = classify_all_tasks(tasks, CONFIG.bidir_score_threshold)
    summary = get_classification_summary(task_types)
    print(f"Classification: Type A={summary['type_a']}, Type B={summary['type_b']}")

    # Step 3: Load H-E1 cluster labels
    print("\n[3/8] Loading H-E1 cluster labels...")
    he1_path = os.path.join(os.path.dirname(__file__), CONFIG.he1_results_path)
    cluster_labels = load_he1_cluster_labels(he1_path)
    print(f"Loaded {len(cluster_labels)} cluster labels from H-E1")

    # Step 4: Extract confidence for all models
    print("\n[4/8] Extracting confidence for all models...")
    conf_by_model = run_all_models_confidence(tasks, CONFIG.models)

    # Step 5: Analyze conflation (primary model)
    print("\n[5/8] Analyzing reward conflation...")
    primary_model = CONFIG.models[CONFIG.primary_model_index]
    primary_conf = conf_by_model[primary_model]

    conflation = analyze_conflation(
        primary_conf, task_types,
        CONFIG.overlap_gate, CONFIG.mean_diff_gate,
        CONFIG.overlap_fail_gate, CONFIG.mean_diff_fail_gate,
        CONFIG.hist_bins
    )

    print(f"Overlap: {conflation['overlap']:.4f} (gate: >{CONFIG.overlap_gate})")
    print(f"Mean Diff: {conflation['diff']:.4f} (gate: <{CONFIG.mean_diff_gate})")
    print(f"Gate PASS: {conflation['gate_pass']}")

    # Step 6: Cross-model and per-dataset analysis
    print("\n[6/8] Cross-model and per-dataset analysis...")
    cross_model = cross_model_overlap(conf_by_model, task_types, CONFIG.hist_bins)
    dataset_overlap = per_dataset_overlap(tasks, primary_conf, task_types, CONFIG.hist_bins)

    for model, ov in cross_model.items():
        print(f"  {model.split('/')[-1]}: overlap={ov:.4f}")
    for ds, ov in dataset_overlap.items():
        print(f"  {ds}: overlap={ov:.4f}")

    # Step 7: Cluster correlation
    print("\n[7/8] Computing cluster-task correlation...")
    common_ids = [tid for tid in task_types if tid in cluster_labels]
    r, p = cluster_task_correlation(
        [cluster_labels[i] for i in common_ids],
        [task_types[i] for i in common_ids]
    )
    print(f"Correlation r={r:.4f}, p={p:.4f}")
    supporting = r > CONFIG.correlation_supporting_threshold
    print(f"Supporting evidence: {supporting} (threshold: {CONFIG.correlation_supporting_threshold})")

    # Step 8: Generate figures
    print("\n[8/8] Generating figures...")
    fig_dir = os.path.join(os.path.dirname(__file__), CONFIG.figures_dir)

    plot_gate_metrics(
        conflation["overlap"], conflation["diff"],
        CONFIG.overlap_gate, CONFIG.mean_diff_gate,
        os.path.join(fig_dir, "gate_metrics.png")
    )

    plot_confidence_histograms(
        np.array(conflation["dist_a"]), np.array(conflation["dist_b"]),
        os.path.join(fig_dir, "confidence_histograms.png")
    )

    plot_cross_model_heatmap(
        cross_model,
        os.path.join(fig_dir, "cross_model_heatmap.png")
    )

    plot_cluster_correlation_scatter(
        [cluster_labels[i] for i in common_ids],
        [task_types[i] for i in common_ids],
        r,
        os.path.join(fig_dir, "cluster_scatter.png")
    )

    plot_per_dataset_overlap(
        dataset_overlap,
        os.path.join(fig_dir, "per_dataset_overlap.png")
    )

    # Build and save results
    results = build_results(
        task_types, conf_by_model, conflation, cross_model,
        dataset_overlap, (r, p), summary
    )

    results_path = os.path.join(os.path.dirname(__file__), CONFIG.results_path)
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {results_path}")

    # Final summary
    print("\n" + "="*60)
    print("EXPERIMENT COMPLETE")
    print("="*60)
    print(f"Gate PASS: {conflation['gate_pass']}")
    print(f"  Overlap: {conflation['overlap']:.4f} (threshold: >{CONFIG.overlap_gate})")
    print(f"  Mean Diff: {conflation['diff']:.4f} (threshold: <{CONFIG.mean_diff_gate})")

    if conflation["gate_pass"]:
        print("\n✓ MUST_WORK gate PASSED - Evidence supports reward conflation hypothesis")
    elif conflation["gate_fail"]:
        print("\n✗ MUST_WORK gate FAILED - No evidence for reward conflation")
    else:
        print("\n? Inconclusive - Neither pass nor fail threshold met")

    return results


if __name__ == "__main__":
    main()
