from dataclasses import dataclass


@dataclass
class Config:
    model_id: str = "mistralai/Mistral-7B-v0.1"
    dtype: str = "bfloat16"
    device_map: str = "auto"

    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: tuple = ("q_proj", "v_proj")

    lr: float = 2e-4
    batch_size: int = 4
    grad_accum: int = 8
    epochs: int = 3

    contamination_levels: tuple = (0.0, 0.10, 0.50)
    k_paraphrases: int = 20
    n_eval_items: int = 500  # Statistically meaningful subset

    seed: int = 42

    auc_target: float = 0.7
    cohens_d_target: float = 0.5
