"""Configuration for H-M1 bibliometric study."""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ExperimentConfig:
    vision_keywords: tuple = ("cifar", "mnist", "imagenet", "svhn", "fashion")
    n_high: int = 10
    n_low: int = 10

    s2_api_url: str = "https://api.semanticscholar.org/graph/v1/paper/search"
    s2_rate_limit_sleep: float = 3.1
    s2_max_retries: int = 5
    s2_backoff_base: float = 2.0

    ratio_threshold: float = 3.0
    p_threshold: float = 0.05

    seed: int = 42

    cache_dir: str = "cache/"
    results_dir: str = "results/"
    figures_dir: str = "figures/"

    def __post_init__(self):
        for d in (self.cache_dir, self.results_dir, self.figures_dir):
            os.makedirs(d, exist_ok=True)


def load_config() -> ExperimentConfig:
    return ExperimentConfig(
        n_high=int(os.environ.get("HM1_N_HIGH", 10)),
        n_low=int(os.environ.get("HM1_N_LOW", 10)),
        s2_rate_limit_sleep=float(os.environ.get("HM1_S2_SLEEP", 3.1)),
        ratio_threshold=float(os.environ.get("HM1_RATIO_THRESHOLD", 3.0)),
        p_threshold=float(os.environ.get("HM1_P_THRESHOLD", 0.05)),
        seed=int(os.environ.get("HM1_SEED", 42)),
    )


CONFIG = load_config()
