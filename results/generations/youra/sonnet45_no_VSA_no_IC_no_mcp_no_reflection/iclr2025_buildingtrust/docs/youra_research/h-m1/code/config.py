from dataclasses import dataclass, field
from typing import List, Dict
from pathlib import Path


@dataclass
class DataConfig:
    benchmarks: List[str] = field(default_factory=lambda: ["TruthfulQA", "AdvBench", "BOLD"])
    data_dir: Path = Path("./data")
    h_e1_results_path: Path = Path("../h-e1/results/correlation_results.json")
    h_e1_benchmark_scores: Path = Path("../h-e1/data/benchmark_scores.csv")
    cache_distance_matrix: bool = True
    distance_matrix_path: Path = Path("./data/correlation_distance_matrix.npy")


@dataclass
class ClusteringConfig:
    linkage_method: str = "ward"
    k_range: List[int] = field(default_factory=lambda: [2, 3])
    distance_metric: str = "precomputed"
    random_seed: int = 42


@dataclass
class BootstrapConfig:
    n_iterations: int = 1000
    random_seed: int = 42
    sample_size: int = 20


@dataclass
class MetricsConfig:
    silhouette_threshold: float = 0.5
    consistency_threshold: float = 80.0
    cophenetic_threshold: float = 0.7


@dataclass
class VisualizationConfig:
    figures_dir: Path = Path("./figures")
    color_scheme: str = "RdBu_r"
    figure_dpi: int = 300
    dendrogram_labels: List[str] = field(default_factory=lambda: ["TruthfulQA", "AdvBench", "BOLD"])


@dataclass
class ExperimentConfig:
    data: DataConfig = field(default_factory=DataConfig)
    clustering: ClusteringConfig = field(default_factory=ClusteringConfig)
    bootstrap: BootstrapConfig = field(default_factory=BootstrapConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    viz: VisualizationConfig = field(default_factory=VisualizationConfig)
    results_dir: Path = Path("./results")
