from dataclasses import dataclass
import os
import random
import torch

@dataclass
class ExperimentConfig:
    model_id: str = "bigcode/starcoder2-7b"
    dataset_id: str = "openai/openai_humaneval"
    dtype: str = "bfloat16"
    device: str = "cuda"
    num_samples: int = 2  # ponytail: PoC smoke test, increase for full eval
    temperature: float = 0.2
    max_new_tokens: int = 512
    syncode_mode: str = "grammar_strict"
    grammar: str = "python"
    quantize: bool = True
    seed: int = 1
    output_dir: str = "outputs"
    figures_dir: str = "../figures"

def setup_experiment(config: ExperimentConfig) -> None:
    random.seed(config.seed)
    torch.manual_seed(config.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(config.seed)
    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)
