"""Configuration for H-M1: Attention sparsity analysis."""
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    # Data
    dataset_name: str = "glue"
    dataset_config: str = "sst2"
    split: str = "validation"  # 872 samples
    max_length: int = 128
    batch_size: int = 1

    # Models
    bert_model_id: str = "bert-base-uncased"
    gpt2_model_id: str = "gpt2"
    num_layers: int = 12
    num_heads: int = 12

    # Sparsity
    zero_threshold: float = 1e-6
    causal_threshold: float = 0.99

    # Gate thresholds
    bert_gate_max: float = 0.10
    gpt2_gate_min: float = 0.99

    # Repro
    seed: int = 42
    device: str = "cuda"

    # Output paths
    output_dir: str = "."
    results_path: str = "results.json"
    report_path: str = "report.md"
    figures_dir: str = "../figures"


GATE_CONFIG = {
    "bert_max_sparsity": 0.10,
    "gpt2_min_sparsity": 0.99,
}

FIGURE_FILES = {
    "gate_comparison": "gate_comparison.png",
    "attention_heatmaps": "attention_heatmaps.png",
    "layerwise_sparsity": "layerwise_sparsity.png",
    "entropy_histogram": "entropy_histogram.png",
}
