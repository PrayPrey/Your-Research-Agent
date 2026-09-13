"""
Minimal REAL Experiment for H-E1
Uses REAL models, REAL HumanEval+ data, but minimal scale (3 models, 10 tasks, 10 samples)
Generates REAL profiling results (not mock data)
"""

import os
import sys
import random
import numpy as np
import pandas as pd
import torch
from typing import List, Dict

# Import local modules
from config_minimal_real import (
    MODEL_CONFIG,
    GENERATION_CONFIG,
    PROFILING_CONFIG,
    CLUSTERING_CONFIG,
    VIZ_CONFIG,
    EXPERIMENT_CONFIG,
    GATE_CONFIG
)
from data_loader import HumanEvalPlusLoader
from model_manager import ModelManager
from profiler import CodeProfiler
from clustering import AlignmentClusterer
from visualizer import ResultVisualizer


def set_seeds(seeds: dict):
    """Set all random seeds for reproducibility."""
    random.seed(seeds["random"])
    np.random.seed(seeds["numpy"])
    torch.manual_seed(seeds["torch"])
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seeds["torch"])
    print(f"Seeds set: {seeds}")


def aggregate_signatures(signatures: List[Dict[str, float]]) -> Dict[str, float]:
    """Average signatures across tasks."""
    if not signatures:
        return {
            "correctness": 0.0,
            "cyclomatic": 0.0,
            "ast_depth": 0.0,
            "runtime_ms": 0.0,
            "memory_kb": 0.0
        }

    keys = signatures[0].keys()
    return {k: np.mean([s[k] for s in signatures]) for k in keys}


def save_results(
    signatures: List[Dict[str, float]],
    model_names: List[str],
    alignment_types: List[str],
    cohens_d: float,
    silhouette: float,
    purity: float,
    output_dir: str
) -> None:
    """Save signatures and metrics to CSV."""
    os.makedirs(output_dir, exist_ok=True)

    # Signatures CSV
    df_sigs = pd.DataFrame(signatures)
    df_sigs["model"] = model_names
    df_sigs["alignment_type"] = alignment_types
    # Reorder columns: model, alignment_type, then metrics
    cols = ["model", "alignment_type"] + [c for c in df_sigs.columns if c not in ["model", "alignment_type"]]
    df_sigs = df_sigs[cols]
    df_sigs.to_csv(f"{output_dir}/signatures.csv", index=False)
    print(f"\nSaved signatures to: {output_dir}/signatures.csv")

    # Metrics CSV
    df_metrics = pd.DataFrame({
        "metric": ["cohens_d", "silhouette", "purity"],
        "value": [cohens_d, silhouette, purity]
    })
    df_metrics.to_csv(f"{output_dir}/metrics.csv", index=False)
    print(f"Saved metrics to: {output_dir}/metrics.csv")


def main():
    print("=" * 80)
    print("H-E1: Minimal REAL Experiment (3 models, 10 tasks, 10 samples)")
    print("=" * 80)
    print("This generates REAL profiling data from REAL models on REAL HumanEval+ tasks")
    print("=" * 80)

    if EXPERIMENT_CONFIG["set_all_seeds"]:
        set_seeds(EXPERIMENT_CONFIG["seeds"])

    # [1/7] Load dataset
    print("\n[1/7] Loading HumanEval+ dataset...")
    loader = HumanEvalPlusLoader()
    problems = loader.load_dataset()

    # Use random subset of tasks
    task_ids = list(problems.keys())
    random.shuffle(task_ids)
    subset_tasks = task_ids[:PROFILING_CONFIG["num_tasks_subset"]]
    print(f"  Using {len(subset_tasks)} random tasks")

    # [2/7] Initialize components
    print("\n[2/7] Initializing components...")
    profiler = CodeProfiler(
        timeout=PROFILING_CONFIG["execution_timeout_sec"],
        n_workers=PROFILING_CONFIG["num_workers"]
    )
    print("  Profiler initialized")

    # [3/7] Profile models
    print(f"\n[3/7] Profiling {len(MODEL_CONFIG['models'])} models...")

    all_signatures = []
    model_names = []
    alignment_types = []

    for model_idx, (model_name, alignment_type) in enumerate(MODEL_CONFIG["models"], 1):
        print(f"\n--- Model {model_idx}/{len(MODEL_CONFIG['models'])}: {model_name} ({alignment_type}) ---")

        # Load model
        print(f"Loading model: {model_name}...")
        manager = ModelManager(
            model_name=model_name,
            cache_dir=MODEL_CONFIG["cache_dir"],
            device="cuda",
            dtype=MODEL_CONFIG["torch_dtype"]
        )
        manager.load_model()

        # Generate and profile for each task
        task_signatures = []
        for task_idx, task_id in enumerate(subset_tasks, 1):
            if task_idx % 5 == 0:
                print(f"  Task {task_idx}/{len(subset_tasks)}...")

            problem = problems[task_id]
            prompt = problem["prompt"]
            test_code = problem["test"]
            entry_point = problem["entry_point"]

            # Generate samples
            samples = []
            for _ in range(PROFILING_CONFIG["num_samples_per_task"]):
                try:
                    generated = manager.generate(
                        prompt=prompt,
                        max_new_tokens=GENERATION_CONFIG["max_new_tokens"],
                        temperature=GENERATION_CONFIG["temperature"],
                        top_p=GENERATION_CONFIG["top_p"]
                    )
                    samples.append(generated)
                except Exception as e:
                    print(f"    Generation error: {e}")
                    continue

            if not samples:
                continue

            # Profile samples
            signature = profiler.profile_samples(
                samples=samples,
                test_code=test_code,
                entry_point=entry_point
            )

            if signature:
                task_signatures.append(signature)

        # Aggregate signatures for this model
        if task_signatures:
            agg_signature = aggregate_signatures(task_signatures)
            all_signatures.append(agg_signature)
            model_names.append(model_name)
            alignment_types.append(alignment_type)

            print(f"  Model signature: correctness={agg_signature['correctness']:.3f}, "
                  f"cyclomatic={agg_signature['cyclomatic']:.2f}")

        # Unload model
        manager.unload_model()
        print(f"  Model unloaded")

    if len(all_signatures) < len(MODEL_CONFIG["models"]):
        print(f"\n⚠️ Warning: Only {len(all_signatures)}/{len(MODEL_CONFIG['models'])} models completed successfully")

    # [4/7] Clustering analysis
    print(f"\n[4/7] Running clustering analysis...")
    clusterer = AlignmentClusterer()

    # Convert to numpy array
    feature_matrix = np.array([
        [sig["correctness"], sig["cyclomatic"], sig["ast_depth"],
         sig["runtime_ms"], sig["memory_kb"]]
        for sig in all_signatures
    ])

    clusters = clusterer.fit_cluster(
        feature_matrix,
        alignment_types,
        n_clusters=min(3, len(set(alignment_types)))
    )

    # Compute metrics
    cohens_d = clusterer.compute_cohens_d()
    silhouette = clusterer.compute_silhouette()
    purity = clusterer.compute_purity(alignment_types)

    print(f"  Cohen's d: {cohens_d:.3f} (threshold: {GATE_CONFIG['threshold']})")
    print(f"  Silhouette score: {silhouette:.3f}")
    print(f"  Alignment purity: {purity:.3f}")

    # [5/7] Gate evaluation
    print(f"\n[5/7] Evaluating MUST_WORK gate...")
    gate_passed = cohens_d > GATE_CONFIG["threshold"]
    print(f"  Gate result: {'✅ PASS' if gate_passed else '❌ FAIL'}")

    if not gate_passed:
        print(f"  ⚠️ Cohen's d ({cohens_d:.3f}) below threshold ({GATE_CONFIG['threshold']})")

    # [6/7] Generate visualizations
    print(f"\n[6/7] Generating visualizations...")
    visualizer = ResultVisualizer(
        signatures=all_signatures,
        model_names=model_names,
        alignment_types=alignment_types,
        clusters=clusters,
        pca_components=clusterer.pca_features,
        output_dir=VIZ_CONFIG["output_dir"]
    )
    visualizer.plot_all(cohens_d, silhouette, purity, GATE_CONFIG["threshold"])
    print(f"  Generated {len(VIZ_CONFIG['figures'])} figures")

    # [7/7] Save results
    print(f"\n[7/7] Saving results...")
    save_results(
        signatures=all_signatures,
        model_names=model_names,
        alignment_types=alignment_types,
        cohens_d=cohens_d,
        silhouette=silhouette,
        purity=purity,
        output_dir=EXPERIMENT_CONFIG["output_dir"]
    )

    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)
    print(f"Gate: {'✅ PASS' if gate_passed else '❌ FAIL'}")
    print(f"Cohen's d: {cohens_d:.3f}")
    print(f"Models profiled: {len(all_signatures)}")
    print(f"Tasks completed: {len(subset_tasks)}")
    print("=" * 80)

    return 0 if gate_passed else 1


if __name__ == '__main__':
    exit(main())
