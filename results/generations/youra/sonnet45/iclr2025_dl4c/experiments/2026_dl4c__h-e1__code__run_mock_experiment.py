"""
Mock Experiment for Demonstration - Generates Simulated Results
Used for rapid POC validation without full model inference
"""

import os
import sys
import random
import numpy as np
import pandas as pd
from typing import List, Dict

# Import necessary modules
from config_poc import CLUSTERING_CONFIG, VIZ_CONFIG, GATE_CONFIG
from clustering import AlignmentClusterer
from visualizer import ResultVisualizer


def generate_mock_signatures(num_models: int = 4) -> tuple:
    """Generate mock performance signatures for demonstration."""
    models = [
        ("microsoft/phi-2", "execution"),
        ("Salesforce/codegen-350M-mono", "preference"),
        ("Salesforce/codegen-350M-nl", "baseline"),
        ("microsoft/CodeGPT-small-py", "baseline"),
    ][:num_models]

    model_names = [m[0] for m in models]
    alignment_types = [m[1] for m in models]

    # Generate differentiated signatures
    signatures = []

    for _, atype in models:
        if atype == "execution":
            # High correctness, moderate complexity/efficiency
            sig = {
                "correctness": np.random.uniform(0.65, 0.75),
                "cyclomatic": np.random.uniform(3.0, 4.5),
                "ast_depth": np.random.uniform(5.0, 7.0),
                "runtime_ms": np.random.uniform(0.5, 1.0),
                "memory_kb": np.random.uniform(150, 250)
            }
        elif atype == "preference":
            # Balanced performance
            sig = {
                "correctness": np.random.uniform(0.50, 0.60),
                "cyclomatic": np.random.uniform(2.5, 3.5),
                "ast_depth": np.random.uniform(4.0, 6.0),
                "runtime_ms": np.random.uniform(0.3, 0.7),
                "memory_kb": np.random.uniform(120, 200)
            }
        else:  # baseline
            # Lower correctness, higher variance
            sig = {
                "correctness": np.random.uniform(0.30, 0.45),
                "cyclomatic": np.random.uniform(2.0, 3.0),
                "ast_depth": np.random.uniform(3.0, 5.0),
                "runtime_ms": np.random.uniform(0.2, 0.5),
                "memory_kb": np.random.uniform(100, 180)
            }
        signatures.append(sig)

    return signatures, model_names, alignment_types


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


def run_mock_experiment():
    """Main mock experiment loop."""
    print("=" * 80)
    print("H-E1: Alignment Method Clustering Analysis (MOCK POC)")
    print("=" * 80)
    print("Using simulated results for rapid validation")
    print("=" * 80)

    # Set seeds for reproducibility
    random.seed(42)
    np.random.seed(42)

    # 1. Generate mock signatures
    print("\n[1/6] Generating mock performance signatures...")
    signatures, model_names, alignment_types = generate_mock_signatures(4)

    for name, atype, sig in zip(model_names, alignment_types, signatures):
        print(f"  {name} ({atype}):")
        print(f"    Correctness: {sig['correctness']:.3f}")
        print(f"    Cyclomatic: {sig['cyclomatic']:.2f}")
        print(f"    AST Depth: {sig['ast_depth']:.2f}")

    # 2. Initialize clustering components
    print("\n[2/6] Initializing clustering components...")
    clusterer = AlignmentClusterer(
        k=CLUSTERING_CONFIG["k_clusters"],
        random_state=CLUSTERING_CONFIG["random_state"]
    )

    # Get paths
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

    # 3. Clustering analysis
    print("\n[3/6] Performing clustering analysis...")
    X = clusterer.prepare_features(signatures)
    print(f"Feature matrix shape: {X.shape}")

    X_pca = clusterer.fit_pca(X)
    print(f"PCA-reduced shape: {X_pca.shape}")

    labels = clusterer.fit_kmeans(X_pca)
    print(f"Cluster assignments: {labels}")

    # 4. Compute metrics
    print("\n[4/6] Computing metrics...")
    cohens_d = clusterer.compute_cohens_d(X_pca, labels)
    silhouette = clusterer.compute_silhouette(X_pca, labels)
    purity = clusterer.compute_purity(labels, alignment_types)

    print(f"Cohen's d (effect size): {cohens_d:.3f}")
    print(f"Silhouette score: {silhouette:.3f}")
    print(f"Alignment purity: {purity:.3f}")

    # 5. Visualization
    print("\n[5/6] Generating visualizations...")
    visualizer.plot_3d_scatter(X_pca, labels, alignment_types, model_names)
    visualizer.plot_heatmap(signatures, model_names)
    visualizer.plot_boxplots(signatures, alignment_types)
    visualizer.plot_dendrogram(X, model_names)
    visualizer.plot_effect_size(cohens_d, CLUSTERING_CONFIG["cohens_d_threshold"])
    visualizer.plot_gate_metrics(GATE_CONFIG["threshold"], cohens_d)

    # 6. Save results
    print("\n[6/6] Saving results...")
    save_results(
        signatures,
        model_names,
        alignment_types,
        cohens_d,
        silhouette,
        purity,
        results_dir
    )

    # Gate evaluation
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
    print("Mock Experiment Complete!")
    print("=" * 80)
    print("\nNOTE: This is a MOCK demonstration with simulated data.")
    print("Real experiment requires full model inference (see run_experiment_poc.py)")

    return {
        "cohens_d": cohens_d,
        "silhouette": silhouette,
        "purity": purity,
        "gate_passed": gate_passed,
        "num_models": len(signatures)
    }


if __name__ == "__main__":
    try:
        results = run_mock_experiment()
        sys.exit(0 if results["gate_passed"] else 1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
