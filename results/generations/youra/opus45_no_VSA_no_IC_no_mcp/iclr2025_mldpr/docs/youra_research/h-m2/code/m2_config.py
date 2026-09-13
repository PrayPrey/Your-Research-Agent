"""Configuration for h-m2: Temporal DNSI prediction experiment."""

# Temporal cutoff
CUTOFF_DATE: str = "2019-01-01"
MIN_HISTORY_YEARS_PRE_CUTOFF: int = 3  # ponytail: reduced for PoC with synthetic data
MIN_PRE_CUTOFF_ENTRIES: int = 10
WINDOW_MONTHS: int = 6

# Regression / resampling
N_BOOTSTRAP: int = 10000
SEED: int = 1

# Gate thresholds
R2_PASS_THRESHOLD: float = 0.3
R2_FAIL_THRESHOLD: float = 0.1
LOO_R2_THRESHOLD: float = 0.1
CI_LOWER_THRESHOLD: float = 0.1

# Gap ground truth (from published papers, all 2019+)
GAP_GROUND_TRUTH: dict = {
    "ImageNet": {"gap": 0.125, "source": "Recht et al. 2019"},
    "CIFAR-10": {"gap": 0.04, "source": "Recht et al. 2019"},
    "CIFAR-100": {"gap": 0.05, "source": "Recht (scaled)"},
    "ObjectNet": {"gap": 0.425, "source": "Barbu et al. 2019", "uses_history_of": "ImageNet"},
}

# Output paths
FIGURES_DIR: str = "figures"
H_E1_CODE_DIR: str = "../../h-e1/code"
