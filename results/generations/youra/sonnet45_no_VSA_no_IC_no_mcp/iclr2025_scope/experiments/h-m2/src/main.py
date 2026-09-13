import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd

from h_m2.loader import FeatureLoader
from h_m2.clustering import ClusteringPipeline
from h_m2.metrics import Evaluator, SimilarityCalculator
from h_m2.visualize import Visualizer
from config.clustering_config import ClusteringConfig


def main():
    """H-M2 clustering pipeline."""
    print("=" * 60)
    print("H-M2: Benchmark Clustering via SentenceBERT")
    print("=" * 60)

    cfg = ClusteringConfig()

    # Load features
    print("\n[1/5] Loading features from h-m1...")
    loader = FeatureLoader(cfg.input_path)
    features = loader.load_features()
    print(f"  Loaded {len(features)} benchmarks")

    descriptions = loader.to_descriptions(features, cfg.description_template)
    print(f"  Generated {len(descriptions)} descriptions")

    # Embed and cluster
    print("\n[2/5] Embedding with SentenceBERT...")
    pipeline = ClusteringPipeline(
        model_name=cfg.model_name,
        n_clusters=cfg.n_clusters,
        random_state=cfg.random_seed,
        max_iter=cfg.kmeans_max_iter,
        n_init=cfg.kmeans_n_init
    )
    result = pipeline.run(descriptions, normalize_l2=cfg.normalize_embeddings)
    print(f"  Embeddings shape: {result['embeddings'].shape}")
    print(f"  Clusters: {cfg.n_clusters}")

    # Cluster distribution
    unique, counts = np.unique(result['labels'], return_counts=True)
    print("  Cluster distribution:", dict(zip(unique.tolist(), counts.tolist())))

    # Evaluate
    print("\n[3/5] Calculating metrics...")
    evaluator = Evaluator(
        similarity_threshold=cfg.similarity_threshold,
        silhouette_threshold=cfg.silhouette_threshold,
        partial_threshold=cfg.partial_threshold
    )
    metrics = evaluator.evaluate(result['embeddings'], result['labels'])

    print(f"  Intra-family similarity: {metrics['intra_family_similarity']:.3f}")
    print(f"  Silhouette score: {metrics['silhouette_score']:.3f}")
    print(f"  Gate decision: {metrics['gate_decision']}")

    # Visualize
    print("\n[4/5] Generating visualizations...")
    viz = Visualizer(cfg.figures_dir)
    viz.plot_gate_metrics(metrics['intra_family_similarity'], cfg.similarity_threshold)
    print(f"  Saved: gate_metrics.png")

    try:
        viz.plot_embedding_space(result['embeddings'], result['labels'])
        print(f"  Saved: embedding_space.png")
    except Exception as e:
        print(f"  Skipped embedding_space.png: {e}")

    try:
        calc = SimilarityCalculator()
        sim_matrix = calc.pairwise_matrix(result['embeddings'])
        viz.plot_similarity_heatmap(sim_matrix, result['labels'])
        print(f"  Saved: similarity_heatmap.png")
    except Exception as e:
        print(f"  Skipped similarity_heatmap.png: {e}")

    # Save outputs
    print("\n[5/5] Saving outputs...")
    output_path = Path(cfg.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save metrics
    with open(output_path / 'metrics.json', 'w') as f:
        json.dump({
            'intra_family_similarity': float(metrics['intra_family_similarity']),
            'silhouette_score': float(metrics['silhouette_score']),
            'gate_decision': metrics['gate_decision'],
            'n_clusters': cfg.n_clusters,
            'n_benchmarks': len(descriptions)
        }, f, indent=2)
    print(f"  Saved: metrics.json")

    # Save cluster assignments
    cluster_df = pd.DataFrame({
        'benchmark_name': features['benchmark_name'],
        'cluster': result['labels']
    })
    cluster_df.to_csv(output_path / 'cluster_assignments.csv', index=False)
    print(f"  Saved: cluster_assignments.csv")

    # Final result
    print("\n" + "=" * 60)
    print(f"GATE RESULT: {metrics['gate_decision']}")
    if metrics['gate_decision'] == 'PASS':
        print("✓ MUST_WORK gate PASSED")
        print(f"  Intra-family similarity {metrics['intra_family_similarity']:.3f} >= {cfg.similarity_threshold}")
        print(f"  Silhouette score {metrics['silhouette_score']:.3f} > {cfg.silhouette_threshold}")
    elif metrics['gate_decision'] == 'PARTIAL':
        print("⚠ PARTIAL: Try k=3 or k=5, or richer embedding model")
        print(f"  Intra-family similarity {metrics['intra_family_similarity']:.3f} in [{cfg.partial_threshold}, {cfg.similarity_threshold})")
    else:
        print("✗ MUST_WORK gate FAILED")
        print(f"  Intra-family similarity {metrics['intra_family_similarity']:.3f} < {cfg.partial_threshold}")
    print("=" * 60)

    return metrics['gate_decision'] == 'PASS'


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
