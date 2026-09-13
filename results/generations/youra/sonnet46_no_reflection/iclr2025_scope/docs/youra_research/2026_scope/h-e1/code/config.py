from dataclasses import dataclass
import os

@dataclass
class ExperimentConfig:
    # Dataset
    dataset_id: str = "nyu-mll/glue"
    dataset_config: str = "mnli"
    primary_n: int = 100
    extended_n: int = 500
    borderline_low: float = 0.65
    borderline_high: float = 0.75
    misalignment_threshold: float = 0.7
    max_seq_len: int = 512
    seed: int = 42

    # LoRA model
    lora_base_model: str = "meta-llama/Meta-Llama-3.1-8B"
    lora_checkpoint: str = "yophis/DRM-Llama-3.1-8B-mnli"
    num_labels: int = 3
    attn_impl: str = "eager"

    # Locret model
    locret_checkpoint: str = "hyx21/Locret-llama-3.1-8B-instruct"

    # GQA config
    num_query_heads: int = 32
    num_kv_heads: int = 8
    num_layers: int = 32
    kv_repeat: int = 4  # num_query_heads // num_kv_heads

    # Correlation
    aggregation_method: str = "mean"
    spearman_alternative: str = "less"

    # Output (relative to hypothesis folder)
    hypothesis_folder: str = "."
    results_dir: str = "results"
    figures_dir: str = "figures"

    # Runtime
    dtype: str = "float16"
    device_map: str = "auto"

    def get_results_path(self) -> str:
        return os.path.join(self.hypothesis_folder, self.results_dir, "spearman_correlation_results.json")

    def get_figures_dir(self) -> str:
        return os.path.join(self.hypothesis_folder, self.figures_dir)
