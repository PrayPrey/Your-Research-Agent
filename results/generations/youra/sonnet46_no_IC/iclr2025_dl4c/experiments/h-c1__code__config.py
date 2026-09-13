from dataclasses import dataclass


@dataclass
class ScanConfig:
    """Fixed configuration for H-C1 doctest prevalence scanning pipeline."""

    # Dataset
    dataset: str = "bigcode/the-stack-dedup"
    data_dir: str = "data/python"
    split: str = "train"

    # Sampling
    seed: int = 42
    n_samples: int = 10_000
    buffer_size: int = 10_000

    # Quality filters (The Stack paper methodology)
    avg_line_len_max: int = 100
    max_line_len_max: int = 1_000
    alphanum_frac_min: float = 0.25

    # Phase C execution
    timeout_sec: int = 5
    n_workers: int = 4

    # Token estimation
    token_ratio: float = 1.3

    # Corpus scale
    full_python_subset_files: int = 12_960_052

    # Gate thresholds
    pass_threshold: float = 0.03
    scope_threshold: float = 0.01

    # Output paths (relative to repo root, but run_scan uses absolute)
    results_json: str = "docs/youra_research/h-c1/results.json"
    per_file_jsonl: str = "docs/youra_research/h-c1/per_file_results.jsonl"
    figures_dir: str = "docs/youra_research/h-c1/figures"
