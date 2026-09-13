"""H-M1: Configuration - Using LongBench-v2 domains for task discrimination."""

from dataclasses import dataclass

# LongBench-v2 domains -> category mapping (6 domain categories)
DOMAIN_CATEGORIES: dict[str, str] = {
    "Single-Document QA": "single_doc_qa",
    "Multi-Document QA": "multi_doc_qa",
    "Long Structured Data Understanding": "structured_data",
    "Long-dialogue History Understanding": "dialogue",
    "Long In-context Learning": "icl",
    "Code Repository Understanding": "code",
}

DOMAINS: list[str] = list(DOMAIN_CATEGORIES.keys())  # 6 domains


@dataclass
class DataConfig:
    dataset_name: str = "THUDM/LongBench-v2"
    samples_per_domain: int = 30  # ~500 total / 6 domains = ~80 per domain, use 30 for speed
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
class EntropyConfig:
    eps: float = 1e-10
    output_shape: tuple = (32, 32)  # (n_layers, n_heads)


@dataclass
class GateConfig:
    significance_threshold: float = 0.05
    effect_size_threshold: float = 0.10  # eta^2, secondary metric


@dataclass
class ExperimentConfig:
    output_dir: str = "."
    figure_dir: str = "figures"
    save_artifacts: bool = True
    dpi: int = 150
