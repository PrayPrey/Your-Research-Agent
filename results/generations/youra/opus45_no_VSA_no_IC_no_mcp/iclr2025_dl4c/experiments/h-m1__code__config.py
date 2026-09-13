"""Configuration for H-M1 experiment: Error Traces Contain Counterfactual Information."""
from dataclasses import dataclass

@dataclass
class Config:
    seed: int = 42
    data_dir: str = "data"
    results_dir: str = "results"
    humaneval_n: int = 164
    mbpp_n: int = 500
    bug_types: tuple = ("syntax", "logic", "type", "off_by_one")
    timeout_s: int = 10
    memory_mb: int = 512
    network_disabled: bool = True
    cf_threshold: float = 0.4
    human_sample_n: int = 100
    kappa_target: float = 0.7
    hypothesis_test_threshold: float = 0.4

CFG = Config()
