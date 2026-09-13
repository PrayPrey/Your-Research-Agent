"""H-M1 Configuration: Foundation Model Emergence Timeline"""
from dataclasses import dataclass, field


@dataclass
class ExperimentConfig:
    # Foundation papers (GPT-3, ViT, BERT, RoBERTa, T5)
    foundation_papers: list[str] = field(default_factory=lambda: [
        "ARXIV:2005.14165",  # GPT-3
        "ARXIV:2010.11929",  # ViT
        "ACL:N19-1423",      # BERT
        "ARXIV:1907.11692",  # RoBERTa
        "ARXIV:1910.10683",  # T5
    ])

    # Comparison set scope
    venues: list[str] = field(default_factory=lambda: ["NeurIPS", "ICML", "ACL", "CVPR"])
    years: list[int] = field(default_factory=lambda: [2019, 2020, 2021])
    min_papers_per_year: int = 1000

    # Gate thresholds
    zscore_threshold: float = 2.0
    gate_min_passing: int = 3

    # Paths
    cache_dir: str = "cache/"
    output_dir: str = "../figures/"
    report_path: str = "outputs/report.json"

    # API
    request_timeout_s: int = 30
    max_retries: int = 3


CONFIG = ExperimentConfig()
