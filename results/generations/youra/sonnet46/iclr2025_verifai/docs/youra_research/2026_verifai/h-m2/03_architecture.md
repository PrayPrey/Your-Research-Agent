# Architecture: H-M2 Difficulty Tier Stratification — Cross-Model Jaccard Analysis

**Hypothesis:** h-m2
**Type:** MECHANISM (SHOULD_WORK gate)
**Date:** 2026-03-18

Applied: pipeline-orchestrator + domain-module pattern (from h-m1 verify_coverage.py style)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Patterns found from base code (filesystem reads; Serena project connection unavailable but direct file reads succeeded)
**Analyzed Path:** `docs/youra_research/20260316_verifia/h-m1/code/src/h_m1/`
**Findings:** h-m1 uses argparse CLI orchestrator (`run_hm1_verification.py`) calling domain module (`verify_coverage.py`) with flat constants, numpy stats, and matplotlib visualization (`visualize_hm1.py`). All patterns reused directly in h-m2.

---

## External Dependencies (Base Hypothesis)

### Key Data Contract — Actual Schema from h-m1 Implementation

The actual `pass_at_1_hm1_verified.json` written by `run_hm1_verification.py:save_verified_output()`:
```json
{
  "metadata": { "source": "h-e1", "verification_status": "PASS", "coverage_combined": {...}, "timestamp": "..." },
  "models": {
    "<hf_model_id>": { "<task_id>": <pass_at_1_float> }
  }
}
```

**CRITICAL:** Top-level key is `"models"`, not `{model_id: {task_id: {...}}}`. h-m2 loader must read `data["models"]`.

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| MODEL_SHORT_NAMES | `from h_m1.verify_coverage import MODEL_SHORT_NAMES` | `h-m1/code/src/h_m1/verify_coverage.py` |
| BENCHMARK_PREFIXES | `from h_m1.verify_coverage import BENCHMARK_PREFIXES` | `h-m1/code/src/h_m1/verify_coverage.py` |
| split_by_benchmark | `from h_m1.verify_coverage import split_by_benchmark` | `h-m1/code/src/h_m1/verify_coverage.py` |
| HIST_BINS | `from h_m1.verify_coverage import HIST_BINS` | `h-m1/code/src/h_m1/verify_coverage.py` |

**Verified from:** `docs/youra_research/20260316_verifia/h-m1/code/src/h_m1/verify_coverage.py`

### h-m1 Constants (Reuse in h-m2)

```python
MODEL_IDS = ["NousResearch/Meta-Llama-3-8B", "codellama/CodeLlama-7b-hf", "deepseek-ai/deepseek-coder-6.7b-base"]
MODEL_SHORT_NAMES = {"NousResearch/Meta-Llama-3-8B": "llama3_8b", "codellama/CodeLlama-7b-hf": "codellama_7b", "deepseek-ai/deepseek-coder-6.7b-base": "deepseek_6.7b"}
BENCHMARK_PREFIXES = {"HumanEval/": "humaneval", "Mbpp/": "mbpp"}
HIST_BINS = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
```

---

## File Organization

```
h-m2/
  code/
    src/
      h_m2/
        __init__.py
        stratify.py          # Tier assignment + benchmark split
        jaccard.py           # Jaccard + cross-model pair computation
        analyze.py           # Histogram + distribution stats
        evaluate.py          # Gate evaluation + mechanism verification
        visualize_hm2.py     # 5 figure generators
        run_hm2_stratification.py  # CLI orchestrator (entry point)
    requirements.txt
    setup.py                 # or pyproject.toml
  results/
    stratification_results.json
    tier_assignments.csv
  figures/
    jaccard_similarity_bars.png
    pass_at_1_histograms.png
    tier_size_summary.png
    jaccard_heatmap.png
    consensus_hard_pie.png
  tests/
    test_stratify.py
    test_jaccard.py
    test_evaluate.py
```

---

## Module Definitions

### stratify (`h-m2/code/src/h_m2/stratify.py`)

**Dependencies:** json, pathlib, h_m1.verify_coverage (constants only, optional)

```python
# Constants
HARD_THRESHOLD: float = 0.0
EASY_THRESHOLD: float = 0.6
HE_PREFIX: str = "HumanEval/"
MBPP_PREFIX: str = "Mbpp/"
DEFAULT_HM1_RESULTS: str = "../../h-m1/results"
HM1_VERIFIED_FILENAME: str = "pass_at_1_hm1_verified.json"

def load_hm1_pass_at_1(hm1_results_dir: Path) -> dict[str, dict[str, float]]:
    """Load pass_at_1_hm1_verified.json.
    Returns: {hf_model_id: {task_id: float}}
    Raises: FileNotFoundError, KeyError (missing 'models' key), ValueError (< 3 models or < 500 problems)
    """
    ...

def split_by_benchmark(
    pass_at_1: dict[str, float],
) -> tuple[dict[str, float], dict[str, float]]:
    """Returns: (he_dict, mbpp_dict) splitting on task_id prefix."""
    ...

def compute_difficulty_tiers(
    pass_at_1_data: dict[str, dict[str, float]],
    hard_threshold: float = HARD_THRESHOLD,
    easy_threshold: float = EASY_THRESHOLD,
) -> dict[str, dict[str, set]]:
    """Assign hard/easy/medium tiers per model.
    Returns: {model_id: {"hard": set, "easy": set, "medium": set}}
    """
    ...

def compute_per_benchmark_tiers(
    pass_at_1_data: dict[str, dict[str, float]],
    hard_threshold: float = HARD_THRESHOLD,
    easy_threshold: float = EASY_THRESHOLD,
) -> dict[str, dict[str, dict[str, set]]]:
    """Compute tiers split by benchmark.
    Returns: {model_id: {"humaneval": {"hard": set, "easy": set}, "mbpp": {"hard": set, "easy": set}}}
    """
    ...

def validate_tier_sizes(
    tiers: dict[str, dict[str, set]],
    min_size: int = 20,
) -> dict[str, dict[str, bool]]:
    """Check n_hard >= min_size and n_easy >= min_size per model.
    Returns: {model_id: {"hard_ok": bool, "easy_ok": bool}}
    """
    ...
```

---

### jaccard (`h-m2/code/src/h_m2/jaccard.py`)

**Dependencies:** itertools, stratify

```python
def jaccard_similarity(set_a: set, set_b: set) -> float:
    """Jaccard: |A ∩ B| / |A ∪ B|. Returns 0.0 if both empty."""
    ...

def compute_cross_model_jaccard(
    tiers: dict[str, dict[str, set]],
    tier_name: str = "hard",
) -> dict[tuple[str, str], float]:
    """Compute Jaccard for all 3 model pairs on specified tier.
    Returns: {(model_a, model_b): float} — 3 entries
    """
    ...

def compute_per_benchmark_jaccard(
    per_benchmark_tiers: dict[str, dict[str, dict[str, set]]],
    tier_name: str = "hard",
) -> dict[str, dict[tuple[str, str], float]]:
    """Compute per-benchmark Jaccard for all pairs.
    Returns: {"humaneval": {(a, b): float}, "mbpp": {(a, b): float}}
    """
    ...

def compute_overlap_matrix(
    tiers: dict[str, dict[str, set]],
    tier_name: str = "hard",
) -> dict[tuple[str, str], dict[str, int]]:
    """Compute n_intersection and n_union for all pairs.
    Returns: {(a, b): {"n_intersection": int, "n_union": int, "jaccard": float}}
    """
    ...

def compute_consensus_set(
    tiers: dict[str, dict[str, set]],
    tier_name: str = "hard",
) -> dict[str, object]:
    """Compute consensus set (hard for all 3 models).
    Returns: {"task_ids": set, "n": int, "percentage": float}
    """
    ...

def compute_overlap_counts_by_n_models(
    tiers: dict[str, dict[str, set]],
    tier_name: str = "hard",
    total_problems: int = 542,
) -> dict[int, int]:
    """Count problems hard for exactly n models (1, 2, 3).
    Returns: {1: count, 2: count, 3: count}
    """
    ...
```

---

### analyze (`h-m2/code/src/h_m2/analyze.py`)

**Dependencies:** numpy, stratify

```python
HIST_BINS: list[float] = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

def compute_histograms(
    pass_at_1_data: dict[str, dict[str, float]],
    per_benchmark: bool = True,
) -> dict[str, dict[str, dict[str, int]]]:
    """Compute 6-point pass@1 histogram per model (and optionally per benchmark).
    Returns: {model_id: {"combined": {bin_str: count}, "humaneval": {...}, "mbpp": {...}}}
    """
    ...

def compute_distribution_stats(
    pass_at_1: dict[str, float],
) -> dict[str, float]:
    """Compute mean, std, min, max + tier percentages.
    Returns: {"mean": float, "std": float, "min": float, "max": float,
              "pct_hard": float, "pct_easy": float, "pct_medium": float}
    """
    ...

def classify_distribution_shape(
    histogram: dict[str, int],
) -> str:
    """Return distribution shape: "bimodal", "skewed_hard", "skewed_easy", "uniform", "other"."""
    ...

def build_tier_assignments_df(
    pass_at_1_data: dict[str, dict[str, float]],
    tiers: dict[str, dict[str, set]],
) -> "pd.DataFrame":
    """Build tier_assignments.csv dataframe.
    Columns: task_id, benchmark, llama3_tier, codellama_tier, deepseek_tier,
             n_models_hard, n_models_easy
    """
    ...
```

---

### evaluate (`h-m2/code/src/h_m2/evaluate.py`)

**Dependencies:** jaccard, stratify

```python
JACCARD_GATE_THRESHOLD: float = 0.3
GATE_TYPE: str = "SHOULD_WORK"

def evaluate_gate(
    jaccard_results: dict[tuple[str, str], float],
) -> tuple[bool, dict]:
    """SHOULD_WORK gate: any pair Jaccard > 0.3.
    Returns: (gate_pass: bool, gate_detail: dict)
    gate_detail keys: gate_type, threshold, results, passing_pairs, gate_satisfied
    """
    ...

def verify_mechanism_activated(
    tiers: dict[str, dict[str, set]],
    jaccard_results: dict[tuple[str, str], float],
) -> tuple[bool, dict]:
    """Check 4 mechanism indicators.
    Returns: (all_activated: bool, indicators: dict)
    indicators keys: tiers_populated, jaccard_computed, jaccard_non_trivial, tier_sizes_valid
    """
    ...

def build_stratification_results(
    pass_at_1_data: dict[str, dict[str, float]],
    tiers: dict[str, dict[str, set]],
    per_benchmark_tiers: dict,
    jaccard_results: dict[tuple[str, str], float],
    per_benchmark_jaccard: dict,
    consensus: dict,
    gate_detail: dict,
    mechanism_indicators: dict,
) -> dict:
    """Assemble full stratification_results.json payload."""
    ...
```

---

### visualize_hm2 (`h-m2/code/src/h_m2/visualize_hm2.py`)

**Dependencies:** matplotlib, numpy, analyze, jaccard

```python
import matplotlib
matplotlib.use("Agg")

FIG_DPI: int = 150
TIER_COLORS: dict = {"hard": "red", "medium": "gray", "easy": "green"}
JACCARD_THRESHOLD_COLOR: str = "red"
JACCARD_THRESHOLD_STYLE: str = "--"

def plot_jaccard_bars(
    jaccard_results: dict[tuple[str, str], float],
    output_path: str,
    threshold: float = 0.3,
) -> None:
    """Bar chart: 3 model pairs × Jaccard score + dashed threshold line."""
    ...

def plot_pass_at_1_histograms(
    pass_at_1_data: dict[str, dict[str, float]],
    output_path: str,
) -> None:
    """3×2 subplot grid: 3 models × 2 benchmarks, 6-point bins, tier-colored bars."""
    ...

def plot_tier_size_summary(
    per_benchmark_tiers: dict,
    output_path: str,
) -> None:
    """Stacked bar chart: hard/medium/easy counts per model per benchmark."""
    ...

def plot_jaccard_heatmap(
    jaccard_results: dict[tuple[str, str], float],
    output_path: str,
) -> None:
    """3×3 symmetric Jaccard matrix heatmap (0=white, 1=dark blue)."""
    ...

def plot_consensus_hard_pie(
    overlap_counts: dict[int, int],
    output_path: str,
) -> None:
    """Pie chart: problems hard for 1/3, 2/3, 3/3 models."""
    ...
```

---

### run_hm2_stratification (`h-m2/code/src/h_m2/run_hm2_stratification.py`)

**Dependencies:** argparse, json, csv, logging, pathlib, stratify, jaccard, analyze, evaluate, visualize_hm2

```python
DEFAULT_HM1_RESULTS: str = "../../h-m1/results"
DEFAULT_OUTPUT_DIR: str = "results"
DEFAULT_FIGURES_DIR: str = "figures"

def parse_args() -> argparse.Namespace:
    """--hm1_results_dir, --output_dir, --figures_dir, --smoke_test"""
    ...

def save_stratification_results(results: dict, output_path: Path) -> None:
    """Write stratification_results.json."""
    ...

def save_tier_assignments_csv(df: "pd.DataFrame", output_path: Path) -> None:
    """Write tier_assignments.csv."""
    ...

def format_gate_output(gate_pass: bool, gate_detail: dict) -> str:
    """Format gate result for structured stdout."""
    ...

def main() -> None:
    """Orchestrate: load → tier → jaccard → histogram → gate → visualize → save.
    Exit codes: 0=PASS, 1=FAIL, 2=runtime error
    """
    ...

if __name__ == "__main__":
    main()
```

---

## Data Flow

- `run_hm2_stratification.main()`
  - `stratify.load_hm1_pass_at_1()` → `pass_at_1_data`
  - `stratify.compute_difficulty_tiers(pass_at_1_data)` → `tiers`
  - `stratify.compute_per_benchmark_tiers(pass_at_1_data)` → `per_benchmark_tiers`
  - `stratify.validate_tier_sizes(tiers)`
  - `jaccard.compute_cross_model_jaccard(tiers)` → `jaccard_results`
  - `jaccard.compute_per_benchmark_jaccard(per_benchmark_tiers)` → `pb_jaccard`
  - `jaccard.compute_consensus_set(tiers)` → `consensus`
  - `jaccard.compute_overlap_counts_by_n_models(tiers)` → `overlap_counts`
  - `analyze.compute_histograms(pass_at_1_data)` → `histograms`
  - `analyze.build_tier_assignments_df(pass_at_1_data, tiers)` → `df`
  - `evaluate.evaluate_gate(jaccard_results)` → `(gate_pass, gate_detail)`
  - `evaluate.verify_mechanism_activated(tiers, jaccard_results)` → `(activated, indicators)`
  - `evaluate.build_stratification_results(...)` → `results_payload`
  - `save_stratification_results(results_payload, ...)`
  - `save_tier_assignments_csv(df, ...)`
  - `visualize_hm2.plot_jaccard_bars(...)`, `plot_pass_at_1_histograms(...)`, etc.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create h-m2/code/src/h_m2/ package, requirements.txt, setup.py, tests/ skeleton | 6 | 2+1+1+2 |
| A-2 | Data Loader | `stratify.load_hm1_pass_at_1()` with schema validation: read `data["models"]`, verify 3 model keys, >= 500 problems per model | 8 | 2+2+2+2 |
| A-3 | Tier Stratification | `stratify.compute_difficulty_tiers()`, `compute_per_benchmark_tiers()`, `validate_tier_sizes()`, `split_by_benchmark()` | 9 | 3+2+2+2 |
| A-4 | Jaccard Module | `jaccard_similarity()`, `compute_cross_model_jaccard()`, `compute_per_benchmark_jaccard()`, `compute_overlap_matrix()`, `compute_consensus_set()`, `compute_overlap_counts_by_n_models()` | 10 | 3+2+3+2 |
| A-5 | Analysis Module | `analyze.compute_histograms()`, `compute_distribution_stats()`, `classify_distribution_shape()`, `build_tier_assignments_df()` | 9 | 3+2+2+2 |
| A-6 | Gate Evaluation | `evaluate.evaluate_gate()`, `verify_mechanism_activated()`, `build_stratification_results()` | 8 | 2+2+2+2 |
| A-7 | Visualization | All 5 plot functions in `visualize_hm2.py` (jaccard bars, histograms, stacked bar, heatmap, pie) | 12 | 3+2+4+3 |
| A-8 | CLI Orchestrator | `run_hm2_stratification.main()` wiring all modules, argparse, file save, structured stdout gate output | 11 | 3+3+2+3 |
| A-9 | Unit Tests | `test_stratify.py` (tier assignment, edge cases), `test_jaccard.py` (similarity correctness), `test_evaluate.py` (gate conditions) | 9 | 2+2+3+2 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-5, A-7, A-8], Low(4-8): [A-1, A-2, A-3, A-6, A-9]

**Total Complexity:** 82 | **Epic Count:** 9

---

## Critical Implementation Notes

1. **h-m1 JSON schema:** Key is `data["models"][hf_model_id][task_id] = float` (flat float, NOT a dict). Confirmed from `save_verified_output()` in `run_hm1_verification.py`.

2. **Model ID keys:** Use full HF IDs as keys (e.g., `"NousResearch/Meta-Llama-3-8B"`), matching `MODEL_SHORT_NAMES` inverse map from h-m1.

3. **matplotlib backend:** `matplotlib.use("Agg")` before any import (follow h-m1 `visualize_hm1.py` pattern).

4. **PYTHONPATH:** Set `PYTHONPATH=h-m2/code/src` for module resolution. No h-m1 runtime imports needed — only constants may be copy-referenced.

5. **No GPU required:** Pure Python + numpy + pandas + matplotlib only. `CUDA_VISIBLE_DEVICES` not needed.

6. **Primary benchmark:** MBPP+ for all gate reporting; HumanEval+ reported as secondary (CodeLlama degenerate easy tier).

---

*Architecture generated: 2026-03-18*
*Base hypothesis code verified: h-m1/code/src/h_m1/ (verify_coverage.py, run_hm1_verification.py)*
