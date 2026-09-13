"""
Experiment Configuration for h-m-integrated
Hypothesis: Semantic embeddings encode lifecycle role via distributional signatures
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class DataConfig:
    """Data loading configuration."""
    # Reuse h-e1 dataset
    dataset_path: str = "docs/youra_research/20260318_mldpr/h-e1/code/data/metadata_sample/metadata_fields.csv"
    data_dir: str = "data/metadata_sample"

    # Expected dataset statistics
    n_total_samples: int = 300
    n_huggingface: int = 150
    n_openml: int = 100
    n_uci: int = 50
    n_scaffolded: int = 75

    # Text preprocessing
    concat_separator: str = ": "  # field_name: field_value


@dataclass
class EmbeddingConfig:
    """Embedding model configuration."""
    model_name: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384
    batch_size: int = 32
    show_progress: bool = True
    normalize_embeddings: bool = True  # L2 normalization (default in sentence-transformers)


@dataclass
class ClusteringConfig:
    """Clustering configuration."""
    n_clusters: int = 2  # 2-tier lifecycle structure
    random_state: int = 42
    init_method: str = "k-means++"  # Smart centroid initialization
    max_iter: int = 300  # sklearn default
    n_init: int = 10  # sklearn default


@dataclass
class BaselineConfig:
    """Baseline method configurations."""
    # Permutation baseline
    permutation_seed: int = 42

    # LDA baseline
    lda_n_components: int = 2
    lda_max_iter: int = 100
    lda_random_state: int = 42
    lda_max_features: int = 1000  # CountVectorizer vocab size

    # Lexical baseline
    rai_keywords: List[str] = field(default_factory=lambda: [
        "bias", "ethics", "fairness", "responsible",
        "accountability", "transparency", "equity",
        "privacy", "safety", "interpretability"
    ])
    case_sensitive: bool = False


@dataclass
class ControlConfig:
    """Control experiment configuration."""
    # Length normalization
    length_normalization_tokens: int = 100
    truncate_method: str = "first"  # Take first N tokens

    # Modality filtering
    deontic_markers: List[str] = field(default_factory=lambda: [
        "should", "must", "required", "shall", "need",
        "ought", "mandatory", "obligatory"
    ])
    filter_method: str = "remove"  # Remove deontic markers


@dataclass
class GeneralizationConfig:
    """Generalization test configuration."""
    # Repository stratification
    repositories: List[str] = field(default_factory=lambda: ["HuggingFace", "OpenML", "UCI"])

    # Repository-specific probes
    probe_cv_folds: int = 3
    probe_random_state: int = 42
    probe_max_iter: int = 1000


@dataclass
class NMIConfig:
    """NMI evaluation configuration."""
    average_method: str = "arithmetic"  # NMI averaging method


@dataclass
class GateConfig:
    """Gate criteria configuration."""
    # Primary criteria
    nmi_threshold: float = 0.6
    baseline_gap_threshold: float = 0.15

    # Secondary criteria
    normalized_nmi_threshold: float = 0.6
    probe_variance_threshold: float = 0.1


@dataclass
class VisualizationConfig:
    """Visualization configuration."""
    figures_dir: str = "docs/youra_research/20260318_mldpr/h-m-integrated/figures"
    dpi: int = 300
    figsize_bar: tuple = (10, 6)
    figsize_scatter: tuple = (12, 8)
    figsize_matrix: tuple = (8, 6)

    # t-SNE parameters
    tsne_perplexity: int = 30
    tsne_random_state: int = 42
    tsne_n_iter: int = 1000


@dataclass
class ExperimentConfig:
    """Master experiment configuration."""
    # Experiment metadata
    experiment_id: str = "h-m-integrated"
    hypothesis_type: str = "MECHANISM"
    hypothesis_statement: str = (
        "Semantic embeddings encode lifecycle role via distributional signatures, "
        "enabling unsupervised clustering to recover 2-tier lifecycle structure that "
        "exceeds baselines by ≥0.15 NMI"
    )
    gate_type: str = "SHOULD_WORK"

    # Random seed (global)
    random_seed: int = 42

    # Output directories
    results_dir: str = "docs/youra_research/20260318_mldpr/h-m-integrated/results"

    # Nested configurations
    data: DataConfig = field(default_factory=DataConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    clustering: ClusteringConfig = field(default_factory=ClusteringConfig)
    baseline: BaselineConfig = field(default_factory=BaselineConfig)
    control: ControlConfig = field(default_factory=ControlConfig)
    generalization: GeneralizationConfig = field(default_factory=GeneralizationConfig)
    nmi: NMIConfig = field(default_factory=NMIConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)

    def __post_init__(self):
        """Create output directories if they don't exist."""
        Path(self.results_dir).mkdir(parents=True, exist_ok=True)
        Path(self.visualization.figures_dir).mkdir(parents=True, exist_ok=True)
