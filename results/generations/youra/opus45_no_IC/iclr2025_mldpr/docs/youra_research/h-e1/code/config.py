from dataclasses import dataclass, field
from typing import List

VENUES = ["NeurIPS", "ICML", "ICLR"]
YEARS = list(range(2018, 2025))
EXPECTED_VENUE_YEAR_COUNT = 21

@dataclass
class HHIAnalysisConfig:
    hf_papers_dataset: str = "pwc-archive/papers-with-abstracts"
    hf_evaltables_dataset: str = "pwc-archive/evaluation-tables"
    use_api_fallback: bool = True
    venues: List[str] = field(default_factory=lambda: ["NeurIPS", "ICML", "ICLR"])
    year_start: int = 2018
    year_end: int = 2024
    results_dir: str = "results"
    figures_dir: str = "../figures"
    results_csv: str = "results/hhi_metrics.csv"
    validation_json: str = "results/validation.json"
    expected_venue_years: int = 21
    hhi_min: float = 0.0
    hhi_max: float = 1.0
    min_papers_per_venue_year: int = 100
    seed: int = 42
