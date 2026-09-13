"""Config for H-E1: Static Analysis Tool Coverage Validation."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    TIMEOUT_SEC: int = 30
    HUMANEVAL_N: int = 164
    MBPP_N: int = 500
    TOTAL_N: int = 664
    HUMANEVAL_SOURCE: str = "openai_humaneval"
    MBPP_SOURCE: str = "mbpp"
    MBPP_SPLIT: str = "test"
    RESULTS_DIR: str = "results"
    TEMP_DIR: str = "/tmp/h_e1_samples"
    COVERAGE_FILE: str = "h_e1_coverage.json"
    SUMMARY_FILE: str = "h_e1_summary.json"
    FAILURES_FILE: str = "h_e1_failures.json"
    VALID_RATE_THRESHOLD: float = 0.95

CONFIG = Config()
