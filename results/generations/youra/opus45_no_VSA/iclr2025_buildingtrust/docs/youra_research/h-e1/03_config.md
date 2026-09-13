# Phase 3: Configuration — H-E1

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: Archived `config.py` variants exist under `_archive/*/h-e1/code/` but target a different benchmark set (HELM/truthfulqa) without OLS residualization — not applicable to current PRD (Open LLM Leaderboard, 6-benchmark residualized PCA). Not reused.
**Pattern Used**: Hardcoded dict

---

## Configuration

**Applied**: Standard PyTorch/sklearn-free scientific pipeline defaults (no KB match; using PRD/brief specified values directly).

```python
CONFIG = {
    # Data parameters
    "dataset_id": "open-llm-leaderboard/results",
    "benchmarks": ["ifeval", "bbh", "math_hard", "gpqa", "musr", "mmlu_pro"],
    "min_benchmarks": 4,          # FR-02.2: require >=4 of 6 scores non-null
    "date_range": ("2023-01-01", "2025-12-31"),  # FR-02.3
    "cache_path": "outputs/cache/open_llm_leaderboard.parquet",

    # Analysis parameters
    "n_permutations": 1000,       # FR-05.1
    "significance_level": 0.05,   # success criterion: p < 0.05
    "min_sample_size": 80,        # NFR-03: assert N >= 80 after filtering
    "vif_threshold": 5.0,         # brief 5.2: no extreme multicollinearity
    "random_seed": 42,

    # Output parameters
    "output_dir": "outputs",
    "results_filename": "h_e1_results.json",
    "figure_dpi": 150,
}
```

### Validation Rules

| Parameter | Rule |
|-----------|------|
| `benchmarks` | must have exactly 6 entries, matching Data Contract §4.1 |
| `min_benchmarks` | int in [1, len(benchmarks)] |
| `date_range` | (start, end) ISO date strings, start < end |
| `cache_path` | parent dir writable; created if missing |
| `n_permutations` | int > 0 (spec fixes at 1000, no tuning per EXISTENCE rules) |
| `significance_level` | float in (0, 1) |
| `min_sample_size` | int > 0; pipeline raises `ValueError` if N < this after filtering (NFR-03) |
| `vif_threshold` | float > 1.0 |
| `random_seed` | int, fixed (reproducibility, NFR-02) |
| `output_dir` | created if missing |
| `figure_dpi` | int in [72, 300] |

**Non-standard**: `min_sample_size=80` and `vif_threshold=5.0` come directly from brief §2.5/§5.2, not framework defaults.

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-E1-1 | Data config | `dataset_id`, `benchmarks`, `min_benchmarks`, `date_range`, `cache_path` |
| C-E1-2 | Analysis config | `n_permutations`, `significance_level`, `min_sample_size`, `vif_threshold`, `random_seed` |
| C-E1-3 | Output config | `output_dir`, `results_filename`, `figure_dpi` |

This is a single fixed EXISTENCE config (PoC): no hyperparameter grid, one seed, values taken directly from PRD/brief without tuning.
