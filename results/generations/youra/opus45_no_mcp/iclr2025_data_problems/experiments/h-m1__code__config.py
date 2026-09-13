from dataclasses import dataclass, field


@dataclass
class Config:
    model_id: str = "mistralai/Mistral-7B-v0.1"
    dtype: str = "bfloat16"
    device_map: str = "auto"

    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: tuple = ("q_proj", "v_proj", "k_proj", "o_proj")  # Extended per PRD FR-2.2

    lr: float = 2e-5
    batch_size: int = 4
    grad_accum: int = 8
    epochs: int = 3

    contamination_levels: tuple = (0.0, 0.10, 0.50)  # PoC: 3 levels sufficient for mechanism validation
    seeds: tuple = (42,)  # PoC: single seed for fast validation
    n_test_items: int = 2000  # PoC: statistically meaningful subset (>500 per guidance)
    effect_size_target: float = 0.05  # 5% accuracy gain threshold
