from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

_H1_DIR = Path(__file__).parent.parent  # h-e1/


@dataclass
class H1Config:
    # Data loading — min_papers=38 yields N~115 on current pwc-archive dataset
    # (closest available to the N=111 in the experiment brief)
    min_papers: int = 38
    min_cov_rows: int = 3

    # PELT algorithm
    pelt_model: str = "l2"
    pelt_min_size: int = 3
    # jump=1 for primary detection (exact); permutation/bootstrap use jump=5 for speed
    pelt_jump: int = 1
    pen_range: tuple = field(default_factory=lambda: (1.0, 50.0))
    n_pen: int = 20

    # Statistical tests
    n_permutations: int = 1000
    n_bootstrap: int = 1000
    seed: int = 42

    # Gate thresholds
    p_threshold: float = 0.05
    paper_count_star_min: int = 10
    paper_count_star_max: int = 120
    bootstrap_ci_width_max: int = 20

    # Output paths
    figures_dir: str = field(default_factory=lambda: str(_H1_DIR / "figures"))
    results_json: str = field(default_factory=lambda: str(_H1_DIR / "experiment_results.json"))


CFG = H1Config()

# Module-level constants for archive compatibility (ingest_pwc.py, derive.py)
MIN_PAPERS = CFG.min_papers
NORM_REGEX = r"[^a-z0-9 ]"
REFERENCE_YEAR = 2024
MIN_MODELS_PER_COHORT = 3


def load_config(yaml_path: Path | None = None) -> H1Config:
    if yaml_path is None:
        yaml_path = Path(__file__).parent.parent / "config.yaml"
    if not yaml_path.exists():
        return CFG
    import yaml
    with open(yaml_path) as f:
        overrides = yaml.safe_load(f) or {}
    if "pen_range" in overrides:
        overrides["pen_range"] = tuple(overrides["pen_range"])
    from dataclasses import replace
    return replace(CFG, **overrides)
