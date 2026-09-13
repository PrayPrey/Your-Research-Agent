from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    """h-e2: API Metadata Coverage Measurement"""
    hypothesis_id: str = "h-e2"
    corpus_path: str = "experiments/h-e2/data/dataset_corpus.csv"
    output_dir: str = "experiments/h-e2"
    results_file: str = "results/coverage_metrics.json"
    figures_dir: str = "figures"
    threshold: float = 80.0
    retry_count: int = 3
    rate_limit: float = 0.1
    timeout: int = 10
