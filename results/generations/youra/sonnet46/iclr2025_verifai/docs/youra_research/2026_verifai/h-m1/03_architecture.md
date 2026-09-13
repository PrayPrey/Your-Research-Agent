# Architecture: H-M1 Pass@1 Coverage Verification

**Applied: incremental-extension pattern** (reuse h-e1 modules, add verify_coverage + visualize_hm1)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-e1)
**Status**: patterns found via direct file reads (Serena project selection error — fallback to Read tool)
**Analyzed Path**: `docs/youra_research/20260316_verifia/h-e1/code/src/h_e1/`
**Findings**: h-e1 uses module-per-concern pattern with relative imports inside `h_e1` package. `run_experiment.py` is the orchestrator importing from `.generate_solutions`, `.evaluate_solutions`, `.analyze_tiers`, `.visualize`. `evaluate_solutions.py` defines `compute_coverage_rate(evaluated_ids, total_ids)` and `MODEL_SHORT_NAMES` dict. `analyze_tiers.py` defines `compute_pass_at_1`, `assign_tiers`, `evaluate_gate`. `visualize.py` uses matplotlib Agg backend with explicit output_path parameters.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| compute_pass_at_1 | `from h_e1.analyze_tiers import compute_pass_at_1` | `h-e1/code/src/h_e1/analyze_tiers.py` |
| evaluate_solutions | `from h_e1.evaluate_solutions import evaluate_all_solutions, save_correctness` | `h-e1/code/src/h_e1/evaluate_solutions.py` |
| generate_solutions | `from h_e1.generate_solutions import MODEL_IDS, MODEL_SHORT_NAMES` | `h-e1/code/src/h_e1/generate_solutions.py` |
| MODEL_SHORT_NAMES | `from h_e1.evaluate_solutions import MODEL_SHORT_NAMES` | `h-e1/code/src/h_e1/evaluate_solutions.py` |

**Verified from**: `h-e1/code/src/h_e1/` (actual implementation)

**Note**: h-m1 code lives in `h-m1/code/src/h_m1/`. The `h-e1` package is available via the shared `youra-h-e1` conda env (installed editable). Import prefix is `h_e1` (underscore).

---

## File Organization

- `h-m1/code/`
  - `src/h_m1/`
    - `__init__.py`
    - `verify_coverage.py` — primary new module
    - `visualize_hm1.py` — h-m1-specific figures
    - `run_hm1_verification.py` — orchestrator entry point
  - `setup.py` or `pyproject.toml`
- `h-m1/results/` — output JSON/CSV files
- `h-m1/figures/` — output PNG figures

---

## Module Definitions

### VerifyCoverage (`src/h_m1/verify_coverage.py`)

**Dependencies**: numpy, json, pathlib, h_e1.analyze_tiers (compute_pass_at_1), h_e1.evaluate_solutions (MODEL_SHORT_NAMES)

```python
HE_TOTAL: int = 164
MBPP_TOTAL: int = 378
COMBINED_TOTAL: int = 542
COVERAGE_GATE: float = 0.95
MODELS: dict[str, str]  # {hf_id: short_name} — from h_e1.evaluate_solutions.MODEL_SHORT_NAMES
BENCHMARKS: dict[str, str]  # {"HumanEval/": "humaneval", "Mbpp/": "mbpp"}

def load_or_recompute_pass_at_1(
    h_e1_results_dir: Path,
    model_short: str,
) -> dict[str, float]: ...
# Returns {task_id: float} — primary: pass_at_1_{model}.json; fallback: correctness_{model}.json

def split_by_benchmark(
    pass_at_1: dict[str, float],
) -> tuple[dict[str, float], dict[str, float]]: ...
# Returns (he_dict, mbpp_dict) split by task_id prefix

def compute_coverage(
    pass_at_1_split: dict[str, dict[str, float]],
) -> dict[str, dict[str, float]]: ...
# Returns {model: {"humaneval": float, "mbpp": float, "combined": float}}

def compute_distribution_stats(
    pass_at_1: dict[str, float],
) -> dict: ...
# Returns {mean, std, min, max, histogram_6pt, non_trivial}

def verify_gate(
    coverage_combined: float,
    stats: dict,
) -> tuple[bool, list[str]]: ...
# Returns (gate_pass, check_messages)

def verify_mechanism_activated(
    pass_at_1_dicts: dict[str, dict],
    results: dict,
) -> tuple[bool, dict]: ...

def run_verification(
    h_e1_results_dir: Path,
    output_dir: Path,
    smoke_test: bool = False,
) -> dict: ...
# Orchestrates load → split → coverage → stats → gate → returns full results dict
```

---

### VisualizeHM1 (`src/h_m1/visualize_hm1.py`)

**Dependencies**: matplotlib, numpy

```python
FIG_DPI: int = 150
COVERAGE_THRESHOLD: float = 0.95
PASS_AT_1_BINS: list[float]  # [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

def plot_coverage_rates(
    coverage_data: dict,
    output_path: str,
) -> None: ...
# Bar chart: coverage per model × benchmark vs 0.95 red dashed threshold

def plot_pass_at_1_histograms(
    pass_at_1_by_model: dict[str, dict],
    output_path: str,
) -> None: ...
# 3-subplot figure: 6-point histogram per model, HumanEval+ vs MBPP+ side-by-side

def plot_coverage_heatmap(
    coverage_data: dict,
    output_path: str,
) -> None: ...
# 3×2 heatmap: models × benchmarks color-coded by coverage fraction

def plot_pass_at_1_cdf(
    pass_at_1_by_model: dict[str, dict],
    output_path: str,
) -> None: ...
# CDF per model, both benchmarks overlaid, shows bimodal structure
```

---

### RunHM1Verification (`src/h_m1/run_hm1_verification.py`)

**Dependencies**: verify_coverage, visualize_hm1, argparse, json, pathlib

```python
DEFAULT_H_E1_RESULTS: str  # relative path to h-e1/results/
DEFAULT_OUTPUT_DIR: str    # "results"
DEFAULT_FIGURES_DIR: str   # "figures"

def parse_args() -> argparse.Namespace: ...
# --h_e1_results_dir, --output_dir, --figures_dir, --smoke_test, --force_regenerate

def save_verified_output(
    pass_at_1_by_model: dict,
    coverage_data: dict,
    gate_pass: bool,
    output_path: Path,
) -> None: ...
# Writes pass_at_1_hm1_verified.json with metadata + models sections

def save_coverage_report(
    coverage_data: dict,
    stats_by_model: dict,
    gate_results: dict,
    output_dir: Path,
) -> None: ...
# Writes coverage_report.json + coverage_report.csv

def main() -> None: ...
# Entry: parse_args → run_verification → save outputs → generate figures → print gate result
```

---

## Data Flow

- **Input**: `h-e1/results/pass_at_1_{model}.json` (3 files) or `correctness_{model}.json` (fallback)
- `verify_coverage.run_verification()` → full results dict
- `run_hm1_verification.save_verified_output()` → `h-m1/results/pass_at_1_hm1_verified.json`
- `run_hm1_verification.save_coverage_report()` → `h-m1/results/coverage_report.json`, `coverage_report.csv`
- `visualize_hm1.*()` → `h-m1/figures/coverage_rates.png`, `pass_at_1_histograms.png`, `coverage_heatmap.png`, `pass_at_1_cdf.png`
- **H-M2 input**: `h-m1/results/pass_at_1_hm1_verified.json`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project setup | h-m1 package scaffold, setup.py, directories, requirements.txt reuse | 6 | 2+1+1+2 |
| A-2 | Implement verify_coverage: load | `load_or_recompute_pass_at_1` + `split_by_benchmark` + fallback logic | 9 | 2+2+3+2 |
| A-3 | Implement verify_coverage: stats | `compute_coverage`, `compute_distribution_stats`, `verify_gate`, `verify_mechanism_activated` | 10 | 3+2+3+2 |
| A-4 | Implement verify_coverage: run_verification | Orchestrates full pipeline, smoke_test mode, structured output dict | 8 | 2+2+2+2 |
| A-5 | Implement run_hm1_verification | argparse, `save_verified_output` (FR-5.1 schema), `save_coverage_report` (JSON+CSV), `main` | 11 | 3+2+3+3 |
| A-6 | Implement visualize_hm1: coverage figures | `plot_coverage_rates` + `plot_coverage_heatmap` (2 of 4 figures) | 9 | 2+1+4+2 |
| A-7 | Implement visualize_hm1: distribution figures | `plot_pass_at_1_histograms` + `plot_pass_at_1_cdf` (2 of 4 figures) | 10 | 2+1+5+2 |
| A-8 | Integration + smoke test | Wire all modules, `--smoke_test` (10 problems), validate gate PASS/FAIL output | 10 | 2+3+2+3 |
| A-9 | Fallback path | Detect missing files, rerun evaluate_solutions fallback, `--force_regenerate` flag guard | 12 | 3+3+3+3 |
| A-10 | Full experiment run + output validation | Execute on real h-e1 data, verify 4 figures + 2 JSON + 1 CSV produced, gate PASS confirmed | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-4, A-5, A-6, A-7, A-8, A-9], Low(4-8): [A-1, A-2, A-10]

---

## Interface Contract for H-M2

`h-m1/results/pass_at_1_hm1_verified.json` schema:
```json
{
  "metadata": {
    "source": "h-e1",
    "verification_status": "PASS",
    "coverage_combined": {"llama3_8b": 1.0, "codellama_7b": 1.0, "deepseek_6.7b": 1.0},
    "timestamp": "<ISO-8601>"
  },
  "models": {
    "NousResearch/Meta-Llama-3-8B": {"HumanEval/0": 0.4, "...": "..."},
    "codellama/CodeLlama-7b-hf": {},
    "deepseek-ai/deepseek-coder-6.7b-base": {}
  }
}
```
