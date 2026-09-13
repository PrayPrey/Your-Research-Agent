from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    models: tuple[str, ...] = ("gpt4", "claude3", "codellama", "codestral")
    completions_dir: str = "data/completions"
    results_dir: str = "results"
    figures_dir: str = "figures"
    variance_threshold: float = 0.15
    mean_r_threshold: float = 0.35
    min_r_threshold: float = 0.20
    alpha: float = 0.05
    min_models: int = 3
    sa_timeout_sec: int = 10
    test_timeout_sec: int = 3
    seed: int = 42
    max_samples_per_model: int = 150  # ponytail: sample for speed, full 421 if compute budget allows

CONFIG = Config()

def completion_path(model_id: str) -> str:
    return f"{CONFIG.completions_dir}/{model_id}.jsonl"
