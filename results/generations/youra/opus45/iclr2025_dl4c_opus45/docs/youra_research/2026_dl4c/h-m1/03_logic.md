# Logic: H-M1 Zero-Reward Basin Mechanism Analysis

**Hypothesis**: RL binary execution reward creates flat zero-reward basin, concentrating failures in assertion errors
**Type**: MECHANISM (statistical analysis, no training/inference)
**Gate**: MUST_WORK (Fisher's exact p < 0.05, one-sided)
**Date**: 2026-03-24

Applied: statistical-analysis-reuse pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-e1 code
**Analyzed Path**: `docs/youra_research/20260323_dl4c/h-e1/code/`
**Relevant Symbols**:
- `classify_error(error_trace: Optional[str]) -> str` - returns "pass"|"syntax"|"runtime"|"assertion"|"other"
- `build_contingency_table(rl_results, dpo_results) -> np.ndarray` - returns 2x3 array (NOT 2x2!)
- `compute_proportions(results: List[dict]) -> Dict[str, float]` - returns per-category proportions among failures
- `chi_square_test(contingency) -> (chi2, p_value, cramers_v, dof)` - H-E1 uses chi2, NOT Fisher's exact

**Key findings**: H-E1 `analyze.py` uses `chi2_contingency` for its 2x3 table. H-M1 builds a NEW 2x2 table (assertion vs non-assertion) and uses `fisher_exact`. Input records have key `error_trace` (not `error_type`).

---

## External Dependencies API

### API Signatures (From Actual h-e1 Code)

```python
# From: h-e1/code/analyze.py (ACTUAL CODE)

def classify_error(error_trace: Optional[str]) -> str:
    """Classify using ICSE 2025 taxonomy. error_trace=None → 'pass'."""
    # Returns: "pass" | "syntax" | "runtime" | "assertion" | "other"

def compute_proportions(results: List[dict]) -> Dict[str, float]:
    """P(type | failure) for each ERROR_CATEGORIES = ['syntax','runtime','assertion']."""
    # Input: results[i] must have key 'error_trace'
    # Returns: {'syntax': float, 'runtime': float, 'assertion': float}

def build_contingency_table(
    rl_results: List[dict],
    dpo_results: List[dict],
) -> np.ndarray:
    """2x3 table: rows=[rl,dpo], cols=[syntax,runtime,assertion]."""
    # Note: H-M1 does NOT use this directly; builds its own 2x2 for Fisher's exact
```

**Verified from**: `docs/youra_research/20260323_dl4c/h-e1/code/analyze.py` (lines 25-121)

**Data format verified**: Each result record has key `error_trace` (str or None).
**Output files**: `h-e1/code/outputs/` - need to confirm filenames via `run_experiment.py`.

---

## A-1: Config Module [Complexity: 5, Budget: 1/3]

**Applied**: Standard Python dataclass

### API Signatures

```python
# config.py
from dataclasses import dataclass, field
import os

@dataclass
class HM1Config:
    # H-E1 data paths (relative to h-m1/code/)
    h_e1_output_dir: str = "../../h-e1/code/outputs"
    rl_results_path: str = "../../h-e1/code/outputs/experiment_results.json"
    metrics_path: str = "../../h-e1/code/outputs/metrics.json"

    # Output paths
    output_dir: str = "outputs"
    figures_dir: str = "figures"

    # Statistical thresholds
    fisher_p_threshold: float = 0.05
    alternative: str = "greater"  # one-sided: P(assertion|fail,RL) > P(assertion|fail,DPO)

    # Expected counts from H-E1 (for validation)
    expected_rl_failures: int = 236
    expected_dpo_failures: int = 530

CONFIG = HM1Config()
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | HM1Config dataclass | Paths, thresholds, expected counts |

---

## A-2: Data Loader [Complexity: 9, Budget: 1/3]

**Applied**: JSON load + H-E1 classify_error reuse

### API Signatures

```python
# data_loader.py
import json
import sys
import logging
from typing import Dict, List, Tuple
from config import HM1Config

def load_h_e1_results(config: HM1Config) -> Tuple[List[dict], List[dict]]:
    """Load RL and DPO execution results from H-E1 experiment_results.json.

    Returns: (rl_results, dpo_results) each with records containing 'error_trace'.
    Raises: FileNotFoundError if H-E1 output missing.
    """
    # experiment_results.json has structure: {"rl": [...], "dpo": [...]}
    # Each record: {"task_id": str, "error_trace": str|None, "status": str}
    ...

def validate_data_integrity(
    rl_results: List[dict],
    dpo_results: List[dict],
    config: HM1Config,
) -> Dict:
    """Validate counts match H-E1 expectations.

    Returns: {'rl_failures': int, 'dpo_failures': int, 'valid': bool, 'warnings': List[str]}
    """
    ...

def extract_error_counts(
    results: List[dict],
    h_e1_code_dir: str,
) -> Dict[str, int]:
    """Count error types using H-E1 classify_error taxonomy.

    Adds h_e1_code_dir to sys.path, imports classify_error.
    Returns: {'syntax': int, 'runtime': int, 'assertion': int, 'pass': int, 'other': int}
    """
    # sys.path.insert(0, h_e1_code_dir)
    # from analyze import classify_error
    # counts failures only
    ...
```

### Pseudo-code for load_h_e1_results

```
1. open config.rl_results_path → data = json.load
2. rl_results = data["rl"]  # or data if flat list - verify structure
3. dpo_results = data["dpo"]
4. return (rl_results, dpo_results)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | load + validate + extract | Three loader functions with H-E1 classify_error reuse |

---

## A-3: Fisher Analysis + Runner [Complexity: 12+8, Budget: 1/3]

**Applied**: scipy.stats.fisher_exact, one-sided

### API Signatures

```python
# analyze.py
import numpy as np
from scipy.stats import fisher_exact
from typing import Dict, Tuple
from config import HM1Config

def build_assertion_contingency(
    rl_counts: Dict[str, int],
    dpo_counts: Dict[str, int],
) -> np.ndarray:
    """Build 2x2 table: rows=[RL,DPO], cols=[assertion, non-assertion].

    Returns: [[rl_assert, rl_non], [dpo_assert, dpo_non]]  # shape [2, 2]
    """
    ...

def run_fisher_exact_test(
    contingency: np.ndarray,  # [2, 2]
    alternative: str = "greater",
) -> Tuple[float, float]:
    """One-sided Fisher's exact. Returns: (odds_ratio, p_value)."""
    ...

def compute_assertion_proportions(
    rl_counts: Dict[str, int],
    dpo_counts: Dict[str, int],
) -> Dict[str, float]:
    """P(assertion | failure) for each model.

    Returns: {
        'rl_assertion_prop': float,   # rl_assertion / rl_total_failures
        'dpo_assertion_prop': float,  # dpo_assertion / dpo_total_failures
        'rl_total_failures': int,
        'dpo_total_failures': int,
    }
    """
    ...

def run_analysis(
    rl_results: List[dict],
    dpo_results: List[dict],
    config: HM1Config,
) -> Dict:
    """Full pipeline: count errors, build 2x2, Fisher's test, save JSON.

    Returns: {
        'rl_assertion_count': int, 'rl_total_failures': int, 'rl_assertion_prop': float,
        'dpo_assertion_count': int, 'dpo_total_failures': int, 'dpo_assertion_prop': float,
        'odds_ratio': float, 'p_value': float, 'gate_pass': bool,
        'contingency_table': List[List[int]],  # 2x2
        'direction_matches': bool,
        'mechanism_log': str,
    }
    """
    ...
```

```python
# visualize.py
from typing import Dict
from config import HM1Config

def plot_gate_metrics(metrics: Dict, config: HM1Config) -> None:
    """Bar: threshold p=0.05 vs actual p_value. Saves figures/gate_metrics.png."""
    ...

def plot_assertion_proportion(metrics: Dict, config: HM1Config) -> None:
    """Bar: P(assertion|failure) RL vs DPO. Saves figures/assertion_proportion.png."""
    ...

def plot_error_distribution(
    rl_counts: Dict[str, int],
    dpo_counts: Dict[str, int],
    config: HM1Config,
) -> None:
    """Stacked bar: syntax/runtime/assertion by model. Saves figures/error_distribution.png."""
    ...

def plot_contingency_heatmap(contingency: np.ndarray, config: HM1Config) -> None:
    """Heatmap of 2x2 table. Saves figures/contingency_table.png."""
    ...

def generate_all_figures(
    metrics: Dict,
    rl_counts: Dict[str, int],
    dpo_counts: Dict[str, int],
    config: HM1Config,
) -> None:
    """Call all four plot functions."""
    ...
```

```python
# run_experiment.py
from config import CONFIG

def main() -> int:
    """Orchestrate: load → validate → analyze → visualize → gate check.

    Returns: 0 if gate_pass, 1 otherwise.
    """
    ...

if __name__ == "__main__":
    import sys
    sys.exit(main())
```

### Pseudo-code for run_analysis

```
1. rl_counts = extract_error_counts(rl_results, config.h_e1_code_dir)
2. dpo_counts = extract_error_counts(dpo_results, config.h_e1_code_dir)
3. props = compute_assertion_proportions(rl_counts, dpo_counts)
4. contingency = build_assertion_contingency(rl_counts, dpo_counts)  # [2,2]
5. odds_ratio, p_value = run_fisher_exact_test(contingency, config.alternative)
6. gate_pass = (p_value < config.fisher_p_threshold) and (props['rl_assertion_prop'] > props['dpo_assertion_prop'])
7. save outputs/metrics.json, outputs/experiment_results.json, outputs/contingency_table.csv
8. return full metrics dict
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | analyze + visualize + runner | Fisher 2x2, plots, main entry point |

---

## Data Format Note

H-E1 `experiment_results.json` structure must be verified at runtime. The H-M1 data loader should handle both:
- `{"rl": [...], "dpo": [...]}` (dict with model keys)
- Flat list with `"model"` field per record

Fallback: read `metrics.json` for pre-computed error counts if raw results unavailable.
