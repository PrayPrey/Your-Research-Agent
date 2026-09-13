"""H-M1 — Findable FAIR Sub-Criteria → Time-to-First-Run Survival Analysis config."""
import os
import argparse

OPENML_UPLOAD_DATE_MIN: str = "2018-01-01"
OPENML_TASK_TYPES: list = ["supervised_classification", "supervised_regression"]

H_E1_SCORES_CSV: str = os.path.join(
    os.path.dirname(__file__), "..", "..", "h-e1", "code", "results", "fair_scores.csv"
)

MIN_RUN_COUNT: int = 10
OBSERVATION_WINDOW_DAYS: int = 730
F1_PID_WEIGHT: float = 0.25
F2_METADATA_WEIGHT: float = 0.50
F3_SEARCH_WEIGHT: float = 0.25
CALIPER_FACTOR: float = 0.2
CALIPER_RELAXED_FACTOR: float = 0.3
MIN_MATCHED_PAIRS: int = 100
SMD_THRESHOLD: float = 0.1
LOG_RANK_ALPHA: float = 0.05
COX_HR_GATE: float = 1.2
SCHOENFELD_ALPHA: float = 0.05
SEED: int = 42
RESULTS_DIR: str = "results"
FIGURES_DIR: str = "figures"
CACHE_DIR: str = "results/cache"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="H-M1 Survival Analysis")
    parser.add_argument("--h-e1-scores-csv", type=str, default=H_E1_SCORES_CSV)
    parser.add_argument("--min-run-count", type=int, default=MIN_RUN_COUNT)
    parser.add_argument("--observation-window-days", type=int, default=OBSERVATION_WINDOW_DAYS)
    parser.add_argument("--caliper-factor", type=float, default=CALIPER_FACTOR)
    parser.add_argument("--caliper-relaxed-factor", type=float, default=CALIPER_RELAXED_FACTOR)
    parser.add_argument("--min-matched-pairs", type=int, default=MIN_MATCHED_PAIRS)
    parser.add_argument("--log-rank-alpha", type=float, default=LOG_RANK_ALPHA)
    parser.add_argument("--cox-hr-gate", type=float, default=COX_HR_GATE)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--results-dir", type=str, default=RESULTS_DIR)
    parser.add_argument("--figures-dir", type=str, default=FIGURES_DIR)
    parser.add_argument("--cache-dir", type=str, default=CACHE_DIR)
    parser.add_argument("--dry-run", action="store_true", help="Run smoke test only")
    return parser.parse_args()


def resolve_paths(args) -> dict:
    return {
        "he1_scores_csv":   args.h_e1_scores_csv,
        "survival_csv":     os.path.join(args.results_dir, "survival_data.csv"),
        "km_json":          os.path.join(args.results_dir, "km_results.json"),
        "cox_json":         os.path.join(args.results_dir, "cox_results.json"),
        "gate_json":        os.path.join(args.results_dir, "gate_result.json"),
        "results_json":     os.path.join(args.results_dir, "results.json"),
        "results_csv":      os.path.join(args.results_dir, "results.csv"),
        "figures_dir":      args.figures_dir,
        "cache_dir":        args.cache_dir,
    }
