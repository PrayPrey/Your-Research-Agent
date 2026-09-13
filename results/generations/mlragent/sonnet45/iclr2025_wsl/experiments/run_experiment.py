"""
Main experiment runner script.
"""

import torch
import numpy as np
import json
import os
import sys
from tqdm import tqdm
from datetime import datetime

import config
from data_generator import generate_dataset, SimpleMLPModel, SimpleCNNModel
from models.gnn_fingerprinter import GNNFingerprinter, model_to_graph
from models.baseline_models import (
    WeightStatisticsFingerprinter,
    PCAFingerprinter,
    NaiveHashFingerprinter,
    NeuronEmbeddingFingerprinter
)
from train_gnn import train_gnn_fingerprinter, load_models_as_graphs
from utils.evaluation import (
    evaluate_provenance_tracking,
    evaluate_symmetry_invariance,
    evaluate_backdoor_detection,
    evaluate_discriminative_power,
    MetricsTracker
)
from utils.visualization import (
    plot_training_curves,
    plot_model_comparison,
    plot_symmetry_analysis,
    plot_backdoor_detection_roc,
    create_results_table
)


def extract_embeddings_gnn(
    model: GNNFingerprinter,
    graphs,
    device: torch.device
) -> np.ndarray:
    """Extract embeddings using trained GNN model."""
    model.eval()
    embeddings = []

    with torch.no_grad():
        for graph_data, _, _ in tqdm(graphs, desc="Extracting GNN embeddings"):
            graph_data = graph_data.to(device)
            # Add batch dimension
            graph_data.batch = torch.zeros(graph_data.x.size(0), dtype=torch.long, device=device)
            emb = model(graph_data)
            embeddings.append(emb.cpu().numpy())

    return np.vstack(embeddings)


def extract_embeddings_baseline(
    fingerprinter,
    model_infos,
    dataset_info
) -> np.ndarray:
    """Extract embeddings using baseline methods."""
    embeddings = []

    for model_info in tqdm(model_infos, desc=f"Extracting {type(fingerprinter).__name__} embeddings"):
        filepath = model_info['filepath']
        state_dict = torch.load(filepath, map_location='cpu')
        emb = fingerprinter(state_dict)
        embeddings.append(emb)

    return np.vstack(embeddings)


def run_all_experiments(log_file):
    """Run all experiments and save results."""
    # Redirect output to log file
    class Logger:
        def __init__(self, filename):
            self.terminal = sys.stdout
            self.log = open(filename, 'a')

        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)
            self.log.flush()

        def flush(self):
            self.terminal.flush()
            self.log.flush()

    sys.stdout = Logger(log_file)

    print(f"=" * 80)
    print(f"Starting experiments at {datetime.now()}")
    print(f"=" * 80)

    # Step 1: Generate dataset
    print("\n[Step 1/6] Generating dataset...")
    if not os.path.exists(os.path.join(config.DATA_DIR, 'dataset_info.json')):
        dataset_info = generate_dataset()
    else:
        with open(os.path.join(config.DATA_DIR, 'dataset_info.json'), 'r') as f:
            dataset_info = json.load(f)
        print("Dataset already exists, loading...")

    print(f"Dataset: {dataset_info['metadata']['num_base_models']} base models, "
          f"{dataset_info['metadata']['num_symmetry_variants']} symmetry variants, "
          f"{dataset_info['metadata']['num_backdoored_models']} backdoored models")

    # Step 2: Train GNN model
    print("\n[Step 2/6] Training GNN fingerprinting model...")
    if not os.path.exists(os.path.join(config.CHECKPOINTS_DIR, 'best_gnn_model.pt')):
        gnn_model, gnn_history = train_gnn_fingerprinter(dataset_info)
        # Plot training curves
        plot_training_curves(
            gnn_history,
            os.path.join(config.RESULTS_DIR, 'gnn_training_curves.png'),
            title="GNN Fingerprinter Training"
        )
    else:
        print("Loading pre-trained GNN model...")
        gnn_model = GNNFingerprinter(
            node_feature_dim=4,
            edge_feature_dim=3,
            hidden_dim=config.GNN_HIDDEN_DIM,
            num_layers=config.GNN_NUM_LAYERS,
            embedding_dim=config.GNN_EMBEDDING_DIM,
            pooling=config.GNN_POOLING
        ).to(config.DEVICE)
        gnn_model.load_state_dict(torch.load(
            os.path.join(config.CHECKPOINTS_DIR, 'best_gnn_model.pt'),
            map_location=config.DEVICE
        ))

    # Step 3: Extract embeddings for all models
    print("\n[Step 3/6] Extracting embeddings for all models...")

    # Load all models as graphs for GNN
    all_graphs = load_models_as_graphs(dataset_info, 'test')

    # Extract GNN embeddings
    gnn_embeddings = extract_embeddings_gnn(gnn_model, all_graphs, config.DEVICE)

    # Extract baseline embeddings
    all_model_infos = (dataset_info['base_models'] +
                       dataset_info['symmetry_variants'] +
                       dataset_info['backdoored_models'])

    print("\nExtracting baseline embeddings...")
    stats_fp = WeightStatisticsFingerprinter()
    stats_embeddings = extract_embeddings_baseline(stats_fp, all_model_infos, dataset_info)

    pca_fp = PCAFingerprinter(n_components=config.PCA_COMPONENTS)
    pca_embeddings = extract_embeddings_baseline(pca_fp, all_model_infos, dataset_info)

    neuron_fp = NeuronEmbeddingFingerprinter(embedding_dim=config.GNN_EMBEDDING_DIM)
    neuron_embeddings = extract_embeddings_baseline(neuron_fp, all_model_infos, dataset_info)

    # Step 4: Evaluate all methods
    print("\n[Step 4/6] Evaluating all methods...")

    all_embeddings = {
        'GNN': gnn_embeddings,
        'Statistics': stats_embeddings,
        'PCA': pca_embeddings,
        'NeuronEmbedding': neuron_embeddings
    }

    results = {}

    for method_name, embeddings in all_embeddings.items():
        print(f"\nEvaluating {method_name}...")
        method_results = {}

        # Build ID lists
        all_ids = [m['id'] for m in all_model_infos]

        # 1. Symmetry Invariance
        print("  - Symmetry invariance...")
        base_model_ids = [m['id'] for m in dataset_info['base_models']]
        base_indices = [all_ids.index(id_) for id_ in base_model_ids if id_ in all_ids]
        base_embeddings = embeddings[base_indices]

        variant_embeddings_list = []
        for base_id in base_model_ids:
            variant_ids = [v['id'] for v in dataset_info['symmetry_variants'] if v['base_id'] == base_id]
            variant_indices = [all_ids.index(id_) for id_ in variant_ids if id_ in all_ids]
            if variant_indices:
                variant_embeddings_list.append(embeddings[variant_indices])
            else:
                variant_embeddings_list.append(np.zeros((1, embeddings.shape[1])))

        symmetry_results = evaluate_symmetry_invariance(base_embeddings, variant_embeddings_list)
        method_results.update({f'symmetry_{k}': v for k, v in symmetry_results.items()})

        # 2. Provenance Tracking
        print("  - Provenance tracking...")
        variant_to_base = {v['id']: v['base_id'] for v in dataset_info['symmetry_variants']}
        provenance_results = evaluate_provenance_tracking(
            embeddings,
            all_ids,
            variant_to_base,
            top_k_values=config.TOP_K_VALUES
        )
        method_results.update({f'provenance_{k}': v for k, v in provenance_results.items()})

        # 3. Backdoor Detection
        print("  - Backdoor detection...")
        clean_indices = [i for i, m in enumerate(all_model_infos) if not m['is_backdoored']]
        backdoor_indices = [i for i, m in enumerate(all_model_infos) if m['is_backdoored']]

        if backdoor_indices:
            clean_embeddings = embeddings[clean_indices]
            backdoor_embeddings = embeddings[backdoor_indices]
            labels = np.array([0] * len(clean_indices) + [1] * len(backdoor_indices))

            backdoor_results = evaluate_backdoor_detection(clean_embeddings, backdoor_embeddings, labels)
            method_results.update({f'backdoor_{k}': v for k, v in backdoor_results.items()})

        # 4. Discriminative Power
        print("  - Discriminative power...")
        discriminative_results = evaluate_discriminative_power(base_embeddings, base_model_ids)
        method_results.update({f'discriminative_{k}': v for k, v in discriminative_results.items()})

        results[method_name] = method_results

    # Step 5: Create visualizations
    print("\n[Step 5/6] Creating visualizations...")

    # Model comparison
    comparison_metrics = {
        'Symmetry Similarity': {k: v['symmetry_mean_similarity'] for k, v in results.items()},
        'Top-1 Accuracy': {k: v.get('provenance_top_1_accuracy', 0) for k, v in results.items()},
        'Backdoor AUROC': {k: v.get('backdoor_auroc', 0) for k, v in results.items()},
        'Discriminative Distance': {k: v['discriminative_mean_inter_model_distance'] for k, v in results.items()}
    }

    plot_model_comparison(
        comparison_metrics,
        os.path.join(config.RESULTS_DIR, 'model_comparison.png'),
        title="Performance Comparison Across Methods"
    )

    # Symmetry analysis for GNN
    transform_types = []
    for v in dataset_info['symmetry_variants'][:len(base_embeddings)*10]:
        transform_types.append(v['transform_type'])

    variant_indices_all = []
    for base_id in base_model_ids:
        variant_ids = [v['id'] for v in dataset_info['symmetry_variants'] if v['base_id'] == base_id]
        variant_indices = [all_ids.index(id_) for id_ in variant_ids if id_ in all_ids]
        variant_indices_all.extend(variant_indices)

    if variant_indices_all:
        plot_symmetry_analysis(
            gnn_embeddings[base_indices],
            gnn_embeddings[variant_indices_all],
            transform_types,
            os.path.join(config.RESULTS_DIR, 'symmetry_analysis.png')
        )

    # Backdoor detection ROC for GNN
    if backdoor_indices:
        clean_centroid = np.mean(gnn_embeddings[clean_indices], axis=0)
        clean_distances = np.linalg.norm(gnn_embeddings[clean_indices] - clean_centroid, axis=1)
        backdoor_distances = np.linalg.norm(gnn_embeddings[backdoor_indices] - clean_centroid, axis=1)

        plot_backdoor_detection_roc(
            clean_distances,
            backdoor_distances,
            os.path.join(config.RESULTS_DIR, 'backdoor_detection_roc.png')
        )

    # Step 6: Save results
    print("\n[Step 6/6] Saving results...")

    # Save results as JSON
    with open(os.path.join(config.RESULTS_DIR, 'experiment_results.json'), 'w') as f:
        json.dump(results, f, indent=2)

    # Create results table
    results_df = create_results_table(
        results,
        os.path.join(config.RESULTS_DIR, 'results_table.csv')
    )

    print("\n" + "=" * 80)
    print("EXPERIMENT RESULTS SUMMARY")
    print("=" * 80)
    print("\nResults Table:")
    print(results_df.to_string())

    print(f"\n{'=' * 80}")
    print(f"Experiments completed at {datetime.now()}")
    print(f"{'=' * 80}")

    return results


if __name__ == "__main__":
    torch.manual_seed(config.SEED)
    np.random.seed(config.SEED)

    # Create directories
    os.makedirs(config.DATA_DIR, exist_ok=True)
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    os.makedirs(config.CHECKPOINTS_DIR, exist_ok=True)

    # Run experiments
    log_file = os.path.join(config.RESULTS_DIR, 'log.txt')
    results = run_all_experiments(log_file)

    print("\nAll experiments completed successfully!")
    print(f"Results saved to: {config.RESULTS_DIR}")
