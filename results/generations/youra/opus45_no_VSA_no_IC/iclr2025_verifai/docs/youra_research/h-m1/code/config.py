from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    sa_timeout_sec: int = 30
    test_timeout_sec: int = 5
    results_dir: str = "results"
    figures_dir: str = "figures"
    completions_path: str = "data/completions.jsonl"
    corr_threshold: float = 0.35
    alpha: float = 0.05
    min_samples: int = 400  # ponytail: HumanEval(164)+MBPP-sanitized-test(257)=421, adjust if full MBPP used
    seed: int = 42

CONFIG = Config()
