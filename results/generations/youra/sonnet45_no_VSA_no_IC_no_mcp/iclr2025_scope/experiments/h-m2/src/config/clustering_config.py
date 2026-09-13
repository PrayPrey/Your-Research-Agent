from dataclasses import dataclass
from pathlib import Path


@dataclass
class ClusteringConfig:
    """H-M2 clustering pipeline configuration."""

    # Study Parameters
    hypothesis_id: str = "h-m2"
    random_seed: int = 42

    # Data Paths
    input_path: str = "../../h-m1/data/h-m1/extracted_features.csv"
    output_dir: str = "data/h-m2"
    figures_dir: str = "../../../docs/youra_research/h-m2/figures"

    # Embedding Model
    model_name: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384
    normalize_embeddings: bool = True

    # Clustering Parameters
    n_clusters: int = 4
    kmeans_max_iter: int = 300
    kmeans_n_init: int = 10

    # Gate Thresholds
    similarity_threshold: float = 0.60
    silhouette_threshold: float = 0.30
    partial_threshold: float = 0.50

    # Description Template
    description_template: str = "{task_type} benchmark for {modality} data, measuring {metrics}, with {dataset_size} samples"

    def __post_init__(self):
        """Create output directories."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.figures_dir).mkdir(parents=True, exist_ok=True)
