from dataclasses import dataclass
from pathlib import Path


@dataclass
class StudyConfig:
    """H-M1 inter-rater agreement study configuration."""

    # Study Parameters
    hypothesis_id: str = "h-m1"
    protocol_version: str = "1.0.0"
    n_benchmarks: int = 20
    random_seed: int = 42

    # Agreement Thresholds
    kappa_threshold: float = 0.80
    kappa_fail_threshold: float = 0.70

    # API Settings
    pwc_api_url: str = "https://paperswithcode.com/api/v1/datasets/"
    api_timeout: int = 30

    # File Paths
    taxonomy_path: str = "src/data/h-m1/taxonomy.json"
    metrics_patterns_path: str = "src/data/h-m1/metrics_patterns.json"
    output_dir: str = "data/h-m1"
    figures_dir: str = "../../docs/youra_research/h-m1/figures"

    # Annotation Workflow
    calibration_samples: int = 3
    time_limit_minutes: int = 120

    def __post_init__(self):
        """Create output directories if needed."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.figures_dir).mkdir(parents=True, exist_ok=True)
