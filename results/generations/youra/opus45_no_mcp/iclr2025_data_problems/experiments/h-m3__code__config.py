from dataclasses import dataclass


@dataclass
class Config:
    model_id: str = "mistralai/Mistral-7B-v0.1"
    dtype: str = "bfloat16"
    device_map: str = "auto"

    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: tuple = ("q_proj", "v_proj", "k_proj", "o_proj")

    lr: float = 2e-5
    batch_size: int = 4
    grad_accum: int = 8

    epochs_verbatim: int = 12
    epochs_paraphrase: int = 3

    contamination_frac: float = 0.10
    k_paraphrases_bank: int = 5
    k_paraphrases_train: int = 3

    n_eval_items: int = 1000
    seeds: tuple = (42, 123, 456)

    correlation_threshold: float = -0.4
    effect_size_threshold: float = 0.3
    p_value_threshold: float = 0.05
