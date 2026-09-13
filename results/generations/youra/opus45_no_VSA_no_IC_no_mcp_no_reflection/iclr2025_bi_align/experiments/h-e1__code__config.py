"""H-E1 Configuration: Fixed experiment config for EXISTENCE PoC."""
from dataclasses import dataclass

@dataclass
class Config:
    dataset_id: str = "google/IFEval"
    model_id: str = "mistralai/Mistral-7B-Instruct-v0.2"
    dataset_split: str = "train"
    num_prompts: int = 541
    temperature: float = 0.7
    max_new_tokens: int = 512
    seed: int = 1
    soft_margin: float = 0.1
    batch_size: int = 8
    output_dir: str = "h-e1/figures"
    device: str = "cuda"
