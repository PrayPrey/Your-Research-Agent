"""
H-E1 — FAIR Score Variance Existence
LIGHT tier: hardcoded constants with optional argparse override
"""
import argparse
import os

# --- OpenML Cohort ---
OPENML_UPLOAD_DATE_MIN: str = "2018-01-01"
OPENML_TASK_TYPES: list = ["supervised_classification", "supervised_regression"]

# --- F-UJI API ---
FUJI_API_BASE: str = "http://localhost:1071"
FUJI_CONCURRENCY: int = 10
FUJI_RETRY_MAX: int = 3
FUJI_RETRY_BASE_S: float = 2.0

# --- FAIR Scoring ---
FAIR_THRESHOLD: float = 0.5
FAIR_N_SUBCRITERIA: int = 17

# --- Gate Thresholds ---
CV_GATE: float = 0.15
GROUP_SIZE_GATE: int = 500

# --- Secondary Metric Thresholds ---
R_QUALITY_MIN: float = 0.10
R_DATE_MAX: float = 0.20

# --- Reproducibility ---
SEED: int = 1

# --- I/O Paths ---
RESULTS_DIR: str = "results"
FIGURES_DIR: str = "figures"
CACHE_DIR: str = "results/fuji_cache"
BATCH_SAVE_INTERVAL: int = 100

# --- Optional OpenML API key ---
OPENML_API_KEY: str = os.environ.get("OPENML_API_KEY", "")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="H-E1 FAIR Score Variance Existence")
    parser.add_argument("--fuji-api-base", type=str, default=FUJI_API_BASE,
                        help="F-UJI REST API base URL (default: %(default)s)")
    parser.add_argument("--fuji-concurrency", type=int, default=FUJI_CONCURRENCY,
                        help="Async concurrency limit (default: %(default)s)")
    parser.add_argument("--fuji-retry-max", type=int, default=FUJI_RETRY_MAX,
                        help="Max retries on HTTP error (default: %(default)s)")
    parser.add_argument("--results-dir", type=str, default=RESULTS_DIR,
                        help="Output results directory (default: %(default)s)")
    parser.add_argument("--figures-dir", type=str, default=FIGURES_DIR,
                        help="Output figures directory (default: %(default)s)")
    parser.add_argument("--cache-dir", type=str, default=CACHE_DIR,
                        help="F-UJI response cache directory (default: %(default)s)")
    parser.add_argument("--use-fallback", action="store_true", default=False,
                        help="Use OpenML machine-computed qualities as FAIR proxy (skip F-UJI)")
    parser.add_argument("--upload-date-min", type=str, default=OPENML_UPLOAD_DATE_MIN,
                        help="OpenML cohort start date (default: %(default)s)")
    parser.add_argument("--max-datasets", type=int, default=None,
                        help="Limit cohort size for testing (default: no limit)")
    return parser.parse_args()


def resolve_paths(args) -> dict:
    return {
        "scores_csv":      os.path.join(args.results_dir, "fair_scores.csv"),
        "metrics_json":    os.path.join(args.results_dir, "existence_metrics.json"),
        "gate_json":       os.path.join(args.results_dir, "gate_result.json"),
        "figures_dir":     args.figures_dir,
        "cache_dir":       args.cache_dir,
    }
