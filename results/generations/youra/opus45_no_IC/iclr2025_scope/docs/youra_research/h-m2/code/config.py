"""H-M2: Configuration - Entropy-eviction tolerance experiment."""

from dataclasses import dataclass

# LongBench-v2 domains (copied from H-M1)
DOMAIN_CATEGORIES: dict[str, str] = {
    "Single-Document QA": "single_doc_qa",
    "Multi-Document QA": "multi_doc_qa",
    "Long Structured Data Understanding": "structured_data",
    "Long-dialogue History Understanding": "dialogue",
    "Long In-context Learning": "icl",
    "Code Repository Understanding": "code",
}

DOMAINS: list[str] = list(DOMAIN_CATEGORIES.keys())


@dataclass
class DataConfig:
    dataset_name: str = "THUDM/LongBench-v2"
    samples_per_domain: int = 30
    n_probe_tokens: int = 100
    seed: int = 42


@dataclass
class ModelConfig:
    model_name: str = "meta-llama/Llama-2-7b-hf"
    torch_dtype: str = "float16"
    device_map: str = "auto"
    output_attentions: bool = True
    n_layers: int = 32
    n_heads: int = 32


@dataclass
class StratConfig:
    entropy_matrix_path: str = "/home/PrayPrey/YouRA_no_IC_opus45/TEST_scope/docs/youra_research/h-m1/code/entropy_matrix.npy"
    domain_means_path: str = "/home/PrayPrey/YouRA_no_IC_opus45/TEST_scope/docs/youra_research/h-m1/code/domain_means.json"


@dataclass
class EvictionConfig:
    retention_ratios: tuple = (1.0, 0.8, 0.4)
    heavy_ratio_frac: float = 0.5
    recent_ratio_frac: float = 0.5
    verify_margin: float = 0.05


@dataclass
class ExperimentConfig:
    output_dir: str = "outputs"
    figure_dir: str = "figures"
    results_path: str = "results.json"
    save_artifacts: bool = True
    dpi: int = 150
    batch_size: int = 1
    max_new_tokens: int = 128
    seed: int = 42


@dataclass
class GateConfig:
    p_threshold: float = 0.05
    min_d: float = 0.5
    direction: str = "greater"
