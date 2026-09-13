from dataclasses import dataclass


@dataclass
class Config:
    model_id: str = "mistralai/Mistral-7B-v0.1"
    dtype: str = "bfloat16"
    device_map: str = "auto"
    dataset_name: str = "cais/mmlu"
    n_items: int = 14042
    k_paraphrases: int = 20
    ssi_epsilon: float = 1e-8
    contamination_levels: tuple = (0, 5, 10, 20, 50)
    seeds: tuple = (42, 123, 456)
    auc_threshold: float = 0.7
    pearson_r_threshold: float = 0.6
    effect_size_threshold: float = 0.5
    batch_size: int = 8
    output_dir: str = "outputs"
    figure_dir: str = "../figures"
