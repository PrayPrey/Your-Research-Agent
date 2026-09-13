from dataclasses import dataclass, field
from typing import List

@dataclass
class ExperimentConfig:
    dataset_name: str = "glue"
    dataset_config: str = "sst2"
    max_length: int = 128
    train_batch_size: int = 32
    hessian_batch_size: int = 256

    epochs: int = 3
    lr: float = 2e-5

    lanczos_k: int = 20
    lanczos_steps: int = 50
    trace_matvecs: int = 100

    bert_model_id: str = "bert-base-uncased"
    gpt2_model_id: str = "gpt2"

    seeds: List[int] = field(default_factory=lambda: [42, 43])
    ablation_batch_sizes: List[int] = field(default_factory=lambda: [256, 512])

    gate_threshold: float = 0.10

    device: str = "cuda"

    output_dir: str = "."
    figures_dir: str = "../figures"
    checkpoints_dir: str = "./checkpoints"
    results_path: str = "results.yaml"
    eigenvalues_path: str = "eigenvalues.npz"

GATE_CONFIG = {"min_relative_diff": 0.10}

FIGURE_FILES = {
    "gate_comparison": "gate_comparison.png",
    "eigenvalue_spectrum": "eigenvalue_spectrum.png",
    "spectral_density": "spectral_density.png",
    "condition_by_layer": "condition_by_layer.png",
}

KRONECKER_LAYER_PREFIXES = {
    "bert": "bert.encoder.layer",
    "gpt2": "transformer.h",
}
