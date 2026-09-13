# Architecture: H-M1 Zero-Reward Basin Mechanism Analysis

**Hypothesis**: RL binary execution reward creates flat zero-reward basin, concentrating failures in assertion errors
**Type**: MECHANISM (statistical analysis, no training/inference)
**Gate**: MUST_WORK (Fisher's exact p < 0.05, one-sided)
**Date**: 2026-03-24

Applied: statistical-analysis-reuse pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/20260323_dl4c/h-e1/code/`
**Findings**: H-E1 has 6 flat modules. `analyze.py` provides `classify_error`, `build_contingency_table`, `compute_proportions` with ICSE 2025 taxonomy. Actual RL failures = 236, assertion proportion = 0.0212 (5/236). Data files confirmed at `h-e1/code/outputs/`.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| classify_error | `sys.path.insert` + `from analyze import classify_error` | `h-e1/code/analyze.py` |
| build_contingency_table | `from analyze import build_contingency_table` | `h-e1/code/analyze.py` |
| compute_proportions | `from analyze import compute_proportions` | `h-e1/code/analyze.py` |
| ExperimentConfig | `from config import ExperimentConfig` | `h-e1/code/config.py` |

**Data Files (Verified from actual outputs):**
| Data | Path |
|------|------|
| RL execution results | `../h-e1/code/outputs/rl_execution_results.json` |
| DPO execution results | `../h-e1/code/outputs/dpo_execution_results.json` |
| H-E1 experiment results | `../h-e1/code/outputs/experiment_results.json` |
| H-E1 metrics | `../h-e1/code/outputs/metrics.json` |

**Verified from**: `docs/youra_research/20260323_dl4c/h-e1/code/` (actual implementation)

---

## File Structure

- `h-m1/code/`
  - `config.py` - H-M1 configuration and paths
  - `data_loader.py` - Load and validate H-E1 results
  - `analyze.py` - Fisher's exact test, contingency table, proportions
  - `visualize.py` - Gate metrics, proportion charts, error distribution
  - `run_experiment.py` - Main entry point
  - `outputs/` - metrics.json, experiment_results.json, contingency_table.csv
  - `figures/` - gate_metrics.png, assertion_proportion.png, error_distribution.png, contingency_table.png

---

## Module Interfaces

### Config (`code/config.py`)

**Dependencies**: None

```python
from dataclasses import dataclass

@dataclass
class HM1Config:
    # H-E1 data paths
    h_e1_code_dir: str = "../../h-e1/code"
    rl_results_path: str = "../../h-e1/code/outputs/rl_execution_results.json"
    dpo_results_path: str = "../../h-e1/code/outputs/dpo_execution_results.json"
    h_e1_experiment_results_path: str = "../../h-e1/code/outputs/experiment_results.json"

    # Output paths
    output_dir: str = "outputs"
    figures_dir: str = "figures"

    # Statistical thresholds
    fisher_p_threshold: float = 0.05
    alternative: str = "greater"  # one-sided: RL > DPO

    # Expected counts from H-E1 (for validation)
    expected_rl_failures: int = 236
    expected_dpo_failures: int = 530

CONFIG = HM1Config()
```

---

### DataLoader (`code/data_loader.py`)

**Dependencies**: config.py

```python
import json
import logging
from typing import Dict, List, Tuple
from config import HM1Config

def load_h_e1_results(config: HM1Config) -> Tuple[List[dict], List[dict]]:
    """Load RL and DPO execution results from H-E1 outputs.

    Returns:
        (rl_results, dpo_results): Lists of dicts with keys: error_trace, status
    Raises:
        FileNotFoundError: If H-E1 output files missing
    """
    ...

def validate_data_integrity(
    rl_results: List[dict],
    dpo_results: List[dict],
    config: HM1Config,
) -> Dict:
    """Validate sample counts match H-E1 expectations.

    Returns:
        Dict with keys: rl_failures, dpo_failures, warnings, valid
    """
    ...

def extract_error_counts(results: List[dict]) -> Dict[str, int]:
    """Count error types using H-E1 classify_error taxonomy.

    Uses h-e1/code/analyze.py::classify_error internally.
    Returns:
        Dict with keys: syntax, runtime, assertion, pass, other
    """
    ...
```

---

### Analyzer (`code/analyze.py`)

**Dependencies**: data_loader.py, config.py, scipy.stats

```python
import numpy as np
from scipy.stats import fisher_exact
from typing import Dict, Tuple
from config import HM1Config

def build_assertion_contingency(
    rl_counts: Dict[str, int],
    dpo_counts: Dict[str, int],
) -> np.ndarray:
    """Build 2x2 contingency table: [RL, DPO] x [assertion, non-assertion].

    Returns:
        2x2 array: [[rl_assert, rl_other], [dpo_assert, dpo_other]]
    """
    ...

def run_fisher_exact_test(
    contingency: np.ndarray,
    alternative: str = "greater",
) -> Tuple[float, float]:
    """One-sided Fisher's exact test: P(assertion|fail,RL) > P(assertion|fail,DPO).

    Returns:
        (odds_ratio, p_value)
    """
    ...

def compute_assertion_proportions(
    rl_counts: Dict[str, int],
    dpo_counts: Dict[str, int],
) -> Dict[str, float]:
    """Compute P(assertion | failure) for each model.

    Returns:
        Dict with keys: rl_assertion_prop, dpo_assertion_prop,
                        rl_total_failures, dpo_total_failures
    """
    ...

def run_analysis(
    rl_results: list,
    dpo_results: list,
    config: HM1Config,
) -> Dict:
    """Full H-M1 analysis pipeline. Saves outputs/metrics.json and experiment_results.json.

    Returns:
        Dict with keys: rl_assertion_count, rl_total_failures, rl_assertion_prop,
                        dpo_assertion_count, dpo_total_failures, dpo_assertion_prop,
                        odds_ratio, p_value, gate_pass, contingency_table,
                        direction_matches, mechanism_log
    """
    ...
```

---

### Visualizer (`code/visualize.py`)

**Dependencies**: analyze.py, config.py, matplotlib, seaborn

```python
from typing import Dict
from config import HM1Config

def plot_gate_metrics(metrics: Dict, config: HM1Config) -> None:
    """Bar chart: target p=0.05 vs actual Fisher's exact p-value.
    Saves to figures/gate_metrics.png.
    """
    ...

def plot_assertion_proportion(metrics: Dict, config: HM1Config) -> None:
    """Bar chart: P(assertion|failure) for RL vs DPO.
    Saves to figures/assertion_proportion.png.
    """
    ...

def plot_error_distribution(
    rl_counts: Dict[str, int],
    dpo_counts: Dict[str, int],
    config: HM1Config,
) -> None:
    """Stacked bar chart: syntax/runtime/assertion breakdown by model.
    Saves to figures/error_distribution.png.
    """
    ...

def plot_contingency_heatmap(contingency: list, config: HM1Config) -> None:
    """Heatmap of 2x2 Fisher's exact contingency table.
    Saves to figures/contingency_table.png.
    """
    ...

def generate_all_figures(
    metrics: Dict,
    rl_counts: Dict[str, int],
    dpo_counts: Dict[str, int],
    config: HM1Config,
) -> None:
    """Generate and save all required figures."""
    ...
```

---

### Experiment Runner (`code/run_experiment.py`)

**Dependencies**: data_loader.py, analyze.py, visualize.py, config.py

```python
from config import CONFIG

def main() -> int:
    """Main entry point for H-M1 zero-reward basin analysis.

    Returns:
        0 if gate passes, 1 if gate fails
    """
    ...

if __name__ == "__main__":
    import sys
    sys.exit(main())
```

---

## Data Flow

1. `run_experiment.py` calls `data_loader.load_h_e1_results()` - reads H-E1 JSON files
2. `data_loader.validate_data_integrity()` - checks counts match expected (RL=236, DPO=530)
3. `data_loader.extract_error_counts()` - reuses H-E1 `classify_error` taxonomy
4. `analyze.build_assertion_contingency()` - builds 2x2 table
5. `analyze.run_fisher_exact_test()` - scipy one-sided Fisher's exact
6. `analyze.run_analysis()` - saves outputs/metrics.json, outputs/experiment_results.json
7. `visualize.generate_all_figures()` - saves all PNG figures

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment Setup | Create code/ directory, install scipy/matplotlib/seaborn, verify H-E1 data files accessible | 5 | 1+1+1+2 |
| A-2 | Config Module | Implement config.py with H-E1 data paths, output dirs, Fisher threshold | 5 | 1+1+1+2 |
| A-3 | Data Loader | Implement data_loader.py: load H-E1 results, validate counts, extract error counts reusing H-E1 classify_error | 9 | 2+2+3+2 |
| A-4 | Fisher Analysis | Implement analyze.py: 2x2 contingency table, one-sided Fisher's exact test, assertion proportions, save metrics JSON | 12 | 3+2+4+3 |
| A-5 | Visualization | Implement visualize.py: gate metrics bar chart (required), assertion proportion, error distribution, contingency heatmap | 10 | 2+2+3+3 |
| A-6 | Experiment Runner | Implement run_experiment.py: orchestrate full pipeline, gate check, mechanism log, exit code | 8 | 2+2+2+2 |
| A-7 | Integration Test | End-to-end run, verify gate_pass=True, verify p-value < 0.05, validate all output files exist | 9 | 2+2+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-5, A-3, A-7], Low(4-8): [A-6, A-1, A-2]

---

## Gate Verification

The MUST_WORK gate passes when:
- `p_value < 0.05` (one-sided Fisher's exact)
- `direction_matches = True` (RL assertion prop > DPO assertion prop)

Expected from H-E1 data:
- RL: 5 assertion / 236 failures = 2.12%
- DPO: 0 assertion / 530 failures = 0.00%
- Fisher's exact (one-sided, greater): expected p << 0.05
