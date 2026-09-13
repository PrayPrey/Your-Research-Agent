"""Configuration dataclasses for h-e1."""
import os
from dataclasses import dataclass


@dataclass
class ModelConfig:
    model_name: str = "meta-llama/Llama-2-7b-hf"
    attn_implementation: str = "eager"
    torch_dtype: str = "float16"
    device_map: str = "auto"

    def __post_init__(self):
        if self.attn_implementation != "eager":
            raise ValueError(
                f"attn_implementation must be 'eager', got '{self.attn_implementation}'. "
                "flash_attention_2 does not support output_attentions=True."
            )

    @property
    def hf_token(self):
        return os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")


@dataclass
class ExperimentConfig:
    n_subsets: int = 3
    subset_size: int = 45  # validation split yields 145 chunks; 3×45=135 ≤ 145
    seqlen: int = 2048
    eps: float = 1e-9
    gate_threshold: float = 0.8
    output_dir: str = "."
    figures_dir: str = "figures/"
