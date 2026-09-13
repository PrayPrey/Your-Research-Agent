"""
POC Experiment Orchestration Script for H-E1
Scaled-down version for faster execution while maintaining statistical validity
"""

import os
import sys
import random
import numpy as np
import pandas as pd
import torch
from typing import List, Dict

# Import local modules
from config_poc import (
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
    df_sigs.to_csv(f"{output_dir}/signatures.csv", index=False)
    print(f"\nSaved signatures to: {output_dir}/signatures.csv")

    # Metrics CSV
    df_metrics = pd.DataFrame({
        "metric": ["cohens_d", "silhouette", "purity"],
        "value": [cohens_d, silhouette, purity]
    })
    df_metrics.to_csv(f"{output_dir}/metrics.csv", index=False)
    print(f"Saved metrics to: {output_dir}/metrics.csv")


def run_experiment():
    """Main experiment loop - POC version."""
    print("=" * 80)
    print("H-E1: Alignment Method Clustering Analysis (POC)")
    print("=" * 80)
    print(f"POC Mode: Using {len(MODEL_CONFIG['models'])} models, "
          f"{PROFILING_CONFIG['num_tasks_subset']} tasks, "
          f"{PROFILING_CONFIG['num_samples_per_task']} samples/task")
    print("=" * 80)

    # Set seeds
    if EXPERIMENT_CONFIG["set_all_seeds"]:
        set_seeds(EXPERIMENT_CONFIG["seeds"])

    # 1. Load data
    print("\n[1/7] Loading dataset...")
    loader = HumanEvalPlusLoader()
    all_tasks = loader.load_dataset()

    # Subset tasks for POC
    task_ids = list(all_tasks.keys())
    random.seed(42)
    subset_ids = random.sample(task_ids, min(PROFILING_CONFIG["num_tasks_subset"], len(task_ids)))
    tasks = {tid: all_tasks[tid] for tid in subset_ids}
    print(f"Using {len(tasks)} tasks (subset from {len(all_tasks)} total)")

    # 2. Initialize components
    print("\n[2/7] Initializing components...")
    model_manager = ModelManager(MODEL_CONFIG, GENERATION_CONFIG)
    profiler = CodeProfiler(
        timeout=PROFILING_CONFIG["execution_timeout_sec"],
        n_workers=PROFILING_CONFIG["num_workers"]
    )
    clusterer = AlignmentClusterer(
        k=CLUSTERING_CONFIG["k_clusters"],
        random_state=CLUSTERING_CONFIG["random_state"]
    )

    # Get absolute path for figures
    script_dir = os.path.dirname(os.path.abspath(__file__))
    figures_dir = os.path.join(os.path.dirname(script_dir), "figures")
    results_dir = os.path.join(os.path.dirname(script_dir), "results")
    os.makedirs(figures_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    visualizer = ResultVisualizer(
        output_dir=figures_dir,
        colors=VIZ_CONFIG["colors"],
        dpi=VIZ_CONFIG["dpi"],
        figsize=VIZ_CONFIG["figsize"]
    )

    # 3. Profile all models
    print(f"\n[3/7] Profiling {len(MODEL_CONFIG['models'])} models...")
    all_signatures = []
    model_names = []
    alignment_types = []

    for model_idx, (model_name, alignment_type) in enumerate(MODEL_CONFIG["models"]):
        print(f"\n--- Model {model_idx + 1}/{len(MODEL_CONFIG['models'])}: {model_name} ({alignment_type}) ---")

        try:
            # Load model
            model_manager.load_model(model_name)

            # Generate and profile samples
            task_signatures = []
            for task_idx, (task_id, task) in enumerate(tasks.items()):
                if (task_idx + 1) % 10 == 0:
                    print(f"Progress: {task_idx + 1}/{len(tasks)} tasks completed")

                # Generate samples
                samples = model_manager.generate_batch(task, PROFILING_CONFIG["num_samples_per_task"])

                # Extract performance signature
                signature = profiler.extract_signature(task, samples)
                task_signatures.append(signature)

            # Aggregate across tasks
            avg_signature = aggregate_signatures(task_signatures)
            all_signatures.append(avg_signature)
            model_names.append(model_name)
            alignment_types.append(alignment_type)

            print(f"Average signature for {model_name}:")
            for k, v in avg_signature.items():
                print(f"  {k}: {v:.4f}")

            # Free memory
            if EXPERIMENT_CONFIG["unload_model_after_use"]:
                model_manager.unload_model()

        except Exception as e:
            print(f"ERROR: Failed to process model {model_name}: {e}")
            import traceback
            traceback.print_exc()
            print("Skipping this model...")
            continue

    if len(all_signatures) < 3:
        print(f"\nERROR: Only {len(all_signatures)} models processed successfully. Need at least 3 for clustering.")
        sys.exit(1)

    # 4. Clustering analysis
    print(f"\n[4/7] Performing clustering analysis...")
    X = clusterer.prepare_features(all_signatures)
    print(f"Feature matrix shape: {X.shape}")

    X_pca = clusterer.fit_pca(X)
    print(f"PCA-reduced shape: {X_pca.shape}")

    labels = clusterer.fit_kmeans(X_pca)
    print(f"Cluster assignments: {labels}")

    # 5. Compute metrics
    print(f"\n[5/7] Computing metrics...")
    cohens_d = clusterer.compute_cohens_d(X_pca, labels)
    silhouette = clusterer.compute_silhouette(X_pca, labels)
    purity = clusterer.compute_purity(labels, alignment_types)

    print(f"Cohen's d (effect size): {cohens_d:.3f}")
    print(f"Silhouette score: {silhouette:.3f}")
    print(f"Alignment purity: {purity:.3f}")

    # 6. Visualization
    print(f"\n[6/7] Generating visualizations...")
    visualizer.plot_3d_scatter(X_pca, labels, alignment_types, model_names)
    visualizer.plot_heatmap(all_signatures, model_names)
    visualizer.plot_boxplots(all_signatures, alignment_types)
    visualizer.plot_dendrogram(X, model_names)
    visualizer.plot_effect_size(cohens_d, CLUSTERING_CONFIG["cohens_d_threshold"])
    visualizer.plot_gate_metrics(GATE_CONFIG["threshold"], cohens_d)

    # 7. Save results
    print(f"\n[7/7] Saving results...")
    save_results(
        all_signatures,
        model_names,
        alignment_types,
        cohens_d,
        silhouette,
        purity,
        results_dir
    )

    # 8. Gate evaluation
    print("\n" + "=" * 80)
    print("GATE EVALUATION (MUST_WORK)")
    print("=" * 80)
    print(f"Metric: {GATE_CONFIG['metric']}")
    print(f"Threshold: {GATE_CONFIG['threshold']}")
    print(f"Actual: {cohens_d:.3f}")

    gate_passed = cohens_d > GATE_CONFIG["threshold"]
    print(f"\nGate Status: {'PASS ✓' if gate_passed else 'FAIL ✗'}")

    if not gate_passed:
        print("\nWARNING: MUST_WORK gate FAILED!")
        print(f"Cohen's d ({cohens_d:.3f}) is below threshold ({GATE_CONFIG['threshold']})")
        print("This indicates that alignment method signatures are NOT detectable.")
        print("Pipeline should HALT and route back to Phase 0.")
    else:
        print("\nSUCCESS: MUST_WORK gate PASSED!")
        print(f"Cohen's d ({cohens_d:.3f}) exceeds threshold ({GATE_CONFIG['threshold']})")
        print("Alignment method signatures are detectable in performance space.")

    print("\n" + "=" * 80)
    print("Experiment Complete!")
    print("=" * 80)

    return {
        "cohens_d": cohens_d,
        "silhouette": silhouette,
        "purity": purity,
        "gate_passed": gate_passed,
        "num_models": len(all_signatures)
    }


if __name__ == "__main__":
    try:
        results = run_experiment()
        sys.exit(0 if results["gate_passed"] else 1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
