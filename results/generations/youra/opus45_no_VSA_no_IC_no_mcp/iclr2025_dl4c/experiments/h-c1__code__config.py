"""Configuration for H-C1 experiment: Complexity Effect on Execution Feedback Advantage."""
from dataclasses import dataclass

@dataclass
class Config:
    seed: int = 42
    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    temperature: float = 0.2
    max_new_tokens: int = 512
    timeout_s: int = 10
    memory_mb: int = 512
    results_dir: str = "results"
    figures_dir: str = "figures"
    mbpp_n: int = 427
    humaneval_n: int = 164

CFG = Config()
