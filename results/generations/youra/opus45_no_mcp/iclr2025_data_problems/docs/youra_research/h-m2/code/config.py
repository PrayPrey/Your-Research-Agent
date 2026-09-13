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

    # H-M2 specific: verbatim vs paraphrase-augmented training
    epochs_verbatim: int = 12  # Match compute with paraphrase (12 epochs * 1404 = 16848 steps)
    epochs_paraphrase: int = 3  # 3 epochs * 5616 = 16848 steps

    contamination_frac: float = 0.10  # 10% contamination level
    k_paraphrases_bank: int = 5  # K=5 paraphrases per item for evaluation
    k_paraphrases_train: int = 3  # Use 3 paraphrases in augmented training

    n_eval_items: int = 1000  # Evaluate representation invariance on 1000 items
    seeds: tuple = (42, 123, 456)  # 3 seeds for statistical validity

    # Mechanism verification thresholds
    mps_diff_threshold: float = 0.05  # MPS_paraphrase - MPS_verbatim > 0.05
    effect_size_target: float = 0.3  # Cohen's d > 0.3 (medium effect)
    p_value_threshold: float = 0.05
