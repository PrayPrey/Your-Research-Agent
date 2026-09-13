# Configuration Design: H-E1 — FAIR Score Variance Existence

Applied: hardcoded-constants-with-argparse pattern (from KB search)
Applied: LIGHT-tier-config pattern (from KB search)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: hardcoded dict / module-level constants with argparse override

---

## Configuration Philosophy

LIGHT tier: hardcoded constants in `config.py` as module-level variables, with an optional `parse_args()` function that allows CLI overrides for key operational parameters. No dataclass, no YAML, no WandB. Copy-paste ready.

---

## config.py — Complete Implementation

### Constants (Hardcoded Defaults)

```python
# config.py
# H-E1 — FAIR Score Variance Existence
# LIGHT tier: hardcoded constants with optional argparse override

import argparse
import os

# --- OpenML Cohort ---
OPENML_UPLOAD_DATE_MIN: str = "2018-01-01"
OPENML_TASK_TYPES: list = ["supervised_classification", "supervised_regression"]

# --- F-UJI API ---
FUJI_API_BASE: str = "http://localhost:1071"
FUJI_CONCURRENCY: int = 10       # asyncio.Semaphore concurrency limit
FUJI_RETRY_MAX: int = 3          # max retries per request on HTTP error
FUJI_RETRY_BASE_S: float = 2.0   # exponential backoff base seconds

# --- FAIR Scoring ---
FAIR_THRESHOLD: float = 0.5      # threshold: >= high-FAIR, < low-FAIR
FAIR_N_SUBCRITERIA: int = 17     # F-UJI sub-criteria count

# --- Gate Thresholds ---
CV_GATE: float = 0.15            # minimum CV to pass existence gate
GROUP_SIZE_GATE: int = 500       # minimum n_high and n_low to pass gate

# --- Secondary Metric Thresholds ---
R_QUALITY_MIN: float = 0.10      # Spearman FAIR vs metadata_richness lower bound
R_DATE_MAX: float = 0.20         # Spearman FAIR vs upload_date upper bound (retroactive tagging check)

# --- Reproducibility ---
SEED: int = 1                    # fixed seed (deterministic — no random sampling used)

# --- I/O Paths ---
RESULTS_DIR: str = "results"
FIGURES_DIR: str = "figures"
CACHE_DIR: str = "cache"         # intermediate F-UJI response cache
BATCH_SAVE_INTERVAL: int = 100   # save intermediate results every N datasets
```

### argparse Integration

```python
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="H-E1 FAIR Score Variance Existence")
    parser.add_argument(
        "--fuji-api-base", type=str, default=FUJI_API_BASE,
        help="F-UJI REST API base URL (default: %(default)s)"
    )
    parser.add_argument(
        "--fuji-concurrency", type=int, default=FUJI_CONCURRENCY,
        help="Async concurrency limit (default: %(default)s)"
    )
    parser.add_argument(
        "--fuji-retry-max", type=int, default=FUJI_RETRY_MAX,
        help="Max retries on HTTP error (default: %(default)s)"
    )
    parser.add_argument(
        "--results-dir", type=str, default=RESULTS_DIR,
        help="Output results directory (default: %(default)s)"
    )
    parser.add_argument(
        "--figures-dir", type=str, default=FIGURES_DIR,
        help="Output figures directory (default: %(default)s)"
    )
    parser.add_argument(
        "--cache-dir", type=str, default=CACHE_DIR,
        help="F-UJI response cache directory (default: %(default)s)"
    )
    parser.add_argument(
        "--use-fallback", action="store_true", default=False,
        help="Use OpenML machine-computed qualities as FAIR proxy (skip F-UJI)"
    )
    parser.add_argument(
        "--upload-date-min", type=str, default=OPENML_UPLOAD_DATE_MIN,
        help="OpenML cohort start date (default: %(default)s)"
    )
    return parser.parse_args()
```

### Environment Variables

```python
# Optional: OpenML API key for authenticated access (public data works without key)
OPENML_API_KEY: str = os.environ.get("OPENML_API_KEY", "")
```

---

## Output Path Configuration

```python
# Resolved output paths (use in main.py after parse_args)
import os

def resolve_paths(args) -> dict:
    return {
        "scores_csv":         os.path.join(args.results_dir, "fair_scores.csv"),
        "metrics_json":       os.path.join(args.results_dir, "existence_metrics.json"),
        "gate_json":          os.path.join(args.results_dir, "gate_result.json"),
        "figures_dir":        args.figures_dir,
        "cache_dir":          args.cache_dir,
        "fuji_cache_json":    os.path.join(args.cache_dir, "fuji_responses.json"),
    }
```

---

## Subtask Decomposition (2 subtasks for A-6)

### ST-A6-1: Main Orchestration Loop

**ID**: ST-A6-1
**Title**: Implement `main()` orchestration in `src/main.py`
**Description**: Wire all modules in sequence — parse args, build cohort, score datasets, run analysis, evaluate gate, save all outputs, print summary. Create results/figures/cache directories if they do not exist. Handle fallback flag (`--use-fallback`) to bypass F-UJI and use `fuji_fallback_proxy()`.
**Acceptance Criteria**:
- `python src/main.py` runs end-to-end without errors
- All three output files (`fair_scores.csv`, `existence_metrics.json`, `gate_result.json`) are written to `results/`
- Final print includes: CV value, n_high, n_low, PASS/FAIL decision
- `--use-fallback` flag switches scorer to `fuji_fallback_proxy()` without code changes

### ST-A6-2: Persistence Helpers + Smoke Test

**ID**: ST-A6-2
**Title**: Implement persistence helpers and smoke test
**Description**: Implement `save_scores_csv()`, `save_metrics_json()`, `save_gate_json()` inline in `src/main.py`. Write `smoke_test.py` at project root that runs the full pipeline on a 10-dataset subset (first 10 rows of cohort) with `--use-fallback` to verify the pipeline executes without errors in under 60 seconds.
**Acceptance Criteria**:
- `python smoke_test.py` exits with code 0
- Output files are created in `results/` with correct schema
- `gate_result.json` contains keys: `passed`, `cv`, `n_high`, `n_low`, `reason`
- `existence_metrics.json` contains keys: `cv`, `n_high`, `n_low`, `r_quality`, `r_date`

---

## Hyperparameter Reference Table

| Parameter | Default | Type | Valid Range | Source |
|-----------|---------|------|-------------|--------|
| OPENML_UPLOAD_DATE_MIN | "2018-01-01" | str | ISO date | Vanschoren (2019) |
| FUJI_API_BASE | "http://localhost:1071" | str | valid URL | F-UJI docs |
| FUJI_CONCURRENCY | 10 | int | 1–50 | F-UJI rate limit recommendation |
| FUJI_RETRY_MAX | 3 | int | 1–10 | NFR-2 |
| FUJI_RETRY_BASE_S | 2.0 | float | 0.5–10.0 | NFR-2 exponential backoff |
| FAIR_THRESHOLD | 0.5 | float | 0.0–1.0 | FR-3 group assignment |
| FAIR_N_SUBCRITERIA | 17 | int | fixed | F-UJI spec |
| CV_GATE | 0.15 | float | > 0 | Devaraju & Huber (2021) |
| GROUP_SIZE_GATE | 500 | int | > 0 | lifelines power analysis |
| R_QUALITY_MIN | 0.10 | float | 0.0–1.0 | Devaraju & Huber (2021) |
| R_DATE_MAX | 0.20 | float | 0.0–1.0 | verification_plan §4.2 |
| SEED | 1 | int | any int | NFR-3 |
| BATCH_SAVE_INTERVAL | 100 | int | 10–1000 | NFR-2 reliability |

---

## Dependency Version Pins

```
# requirements.txt
openml>=0.14.0
aiohttp>=3.9.0
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.11.0
matplotlib>=3.7.0
seaborn>=0.12.0
diptest>=0.7.0
pyyaml>=6.0.0
```
