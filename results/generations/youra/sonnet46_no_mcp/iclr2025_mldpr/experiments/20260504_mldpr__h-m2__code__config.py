"""H-M2 — Accessible FAIR Sub-Criteria → 12-Month Run Count config."""
import os
import argparse

OPENML_UPLOAD_DATE_MIN: str = "2018-01-01"
OPENML_TASK_TYPES: list = ["supervised_classification", "supervised_regression"]

H_E1_SCORES_CSV: str = os.path.join(
    os.path.dirname(__file__), "..", "..", "h-e1", "code", "results", "fair_scores.csv"
)

MIN_RUN_COUNT: int = 0
OBSERVATION_WINDOW_DAYS: int = 365
CALIPER_FACTOR: float = 0.2
CALIPER_RELAXED_FACTOR: float = 0.8
MIN_MATCHED_PAIRS: int = 500
MIN_MATCHED_PAIRS_SMOKE: int = 30
SMD_THRESHOLD: float = 0.1
MWU_ALPHA: float = 0.05
ACCESSIBLE_BETA_GATE: float = 0.10
SEED: int = 42

FAIR_SUB_CRITERIA_COLS: list = ["fair_F", "fair_A", "fair_I", "fair_R"]
FIG_PALETTE: dict = {"high": "#2196F3", "low": "#F44336"}
FIG_DPI: int = 150
FIG_SIZE_FOREST: tuple = (8, 6)

RESULTS_DIR: str = "results"
FIGURES_DIR: str = os.path.join(os.path.dirname(__file__), "..", "figures")
CACHE_DIR: str = "results/cache"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="H-M2 Accessible Analysis")
    parser.add_argument("--h-e1-scores-csv", type=str, default=H_E1_SCORES_CSV)
    parser.add_argument("--observation-window-days", type=int, default=OBSERVATION_WINDOW_DAYS)
    parser.add_argument("--caliper-factor", type=float, default=CALIPER_FACTOR)
    parser.add_argument("--min-matched-pairs", type=int, default=MIN_MATCHED_PAIRS)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--results-dir", type=str, default=RESULTS_DIR)
    parser.add_argument("--figures-dir", type=str, default=FIGURES_DIR)
    parser.add_argument("--cache-dir", type=str, default=CACHE_DIR)
    parser.add_argument("--dry-run", action="store_true", help="Run with synthetic data")
    return parser.parse_args()
