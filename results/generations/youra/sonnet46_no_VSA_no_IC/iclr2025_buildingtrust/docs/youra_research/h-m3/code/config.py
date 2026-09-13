"""H-M3 configuration: per-pair adversarial rank disruption analysis."""
from pathlib import Path

RHO_THRESHOLD: float = 0.4
ALPHA: float = 0.05
N_BOOTSTRAP: int = 1000
RANDOM_SEED: int = 42
N_COMMON_MIN: int = 10
RANK_REVERSAL_MIN_SHIFT: int = 5

RHO_FAIRNESS_HM1: float = 0.60  # fallback; loaded from h-m1 results.json at runtime

_HERE = Path(__file__).parent.parent
FIGURES_DIR = _HERE / "figures"
RESULTS_JSON = _HERE / "results.json"

H_M2_DATA_DIR = _HERE.parent / "h-m2" / "data"
H_M1_RESULTS = _HERE.parent / "h-m1" / "results" / "results.json"
