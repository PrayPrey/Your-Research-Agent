# Config: H-M2 Execution Depth Analysis

Applied: analysis-hypothesis flat-module pattern (dataclass + stdlib only, verified from h-m1 actual code)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-m1)
**Status**: Config classes verified from actual base code
**Config Files Found**: `h-m1/code/config.py` - HM1Config dataclass with `__post_init__` path normalization
**Pattern Used**: dataclass with `os.path.join(os.path.dirname(__file__), ...)` defaults, module-level `CONFIG` singleton

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-m1/code/config.py (ACTUAL CODE - verified)
@dataclass
class HM1Config:
    # H-E1 data paths (relative to h-m1/code/)
    h_e1_code_dir: str = os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code")
    h_e1_output_dir: str = os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code", "outputs")
    rl_results_path: str = os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code", "outputs", "rl_execution_results.json")
    dpo_results_path: str = os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code", "outputs", "dpo_execution_results.json")
    h_e1_experiment_results_path: str = os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code", "outputs", "experiment_results.json")
    h_e1_metrics_path: str = os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code", "outputs", "metrics.json")

    # Output paths
    output_dir: str = os.path.join(os.path.dirname(__file__), "outputs")
    figures_dir: str = os.path.join(os.path.dirname(__file__), "figures")

    # Statistical thresholds
    fisher_p_threshold: float = 0.05
    alternative: str = "greater"

    # Expected counts (for validation)
    expected_rl_failures: int = 236
    expected_dpo_failures: int = 530

    def __post_init__(self): ...  # normalize all paths to absolute
```

**Verified from**: `h-m1/code/config.py` (actual implementation)

**Key differences in H-M2**:
- `fisher_p_threshold` (h-m1) -> `t_test_p_threshold` (h-m2, t-test replaces Fisher's exact)
- Adds `execution_timeout` and `random_seed` (new for depth tracing)
- Drops `h_e1_code_dir` and `h_e1_output_dir` (not needed by h-m2 modules)
- Path defaults use `os.path.join(os.path.dirname(__file__), ...)` pattern (same as h-m1)

---

## A-1: Environment Setup [Complexity: 6, Budget: 6]

Applied: Standard PyTorch defaults (N/A - stdlib only)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
import os


@dataclass
class HM2Config:
    """Configuration for H-M2 hypothesis validation.

    H-M2 tests the execution depth mechanism:
    mean_depth(RL failures) > mean_depth(DPO failures)
    using one-sided Welch's t-test.
    """

    # H-E1 data paths (relative to h-m2/code/)
    rl_results_path: str = os.path.join(
        os.path.dirname(__file__), "..", "..", "h-e1", "code", "outputs", "rl_execution_results.json"
    )
    dpo_results_path: str = os.path.join(
        os.path.dirname(__file__), "..", "..", "h-e1", "code", "outputs", "dpo_execution_results.json"
    )
    h_e1_experiment_results_path: str = os.path.join(
        os.path.dirname(__file__), "..", "..", "h-e1", "code", "outputs", "experiment_results.json"
    )
    h_e1_metrics_path: str = os.path.join(
        os.path.dirname(__file__), "..", "..", "h-e1", "code", "outputs", "metrics.json"
    )

    # Output paths
    output_dir: str = os.path.join(os.path.dirname(__file__), "outputs")
    figures_dir: str = os.path.join(os.path.dirname(__file__), "figures")

    # Statistical thresholds for SHOULD_WORK gate
    t_test_p_threshold: float = 0.05
    alternative: str = "greater"  # One-sided: mean_depth(RL) > mean_depth(DPO)

    # Execution tracing settings
    execution_timeout: float = 5.0  # seconds per sample; signal.alarm-based
    random_seed: int = 42

    # Expected counts from H-E1 (for data integrity validation)
    expected_rl_failures: int = 236
    expected_dpo_failures: int = 530

    def __post_init__(self):
        """Normalize paths to absolute."""
        self.rl_results_path = os.path.abspath(self.rl_results_path)
        self.dpo_results_path = os.path.abspath(self.dpo_results_path)
        self.h_e1_experiment_results_path = os.path.abspath(self.h_e1_experiment_results_path)
        self.h_e1_metrics_path = os.path.abspath(self.h_e1_metrics_path)
        self.output_dir = os.path.abspath(self.output_dir)
        self.figures_dir = os.path.abspath(self.figures_dir)


CONFIG = HM2Config()
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | HM2Config dataclass | Define dataclass with all fields above (paths, thresholds, timeout, seed, expected counts) |
| C-1-2 | Path normalization | `__post_init__` normalizes all path fields to absolute via `os.path.abspath` |
| C-1-3 | Module singleton | `CONFIG = HM2Config()` at module level for flat import pattern |
| C-1-4 | Output dir creation | Caller (run_experiment.py) creates `output_dir` and `figures_dir` with `os.makedirs(..., exist_ok=True)` |

---

## A-6: Statistical Analysis Config [Complexity: 12, Budget: 12]

Applied: Standard scipy.stats defaults

No separate config class needed. Analysis parameters are fields on `HM2Config`:

| Field | Value | Purpose |
|-------|-------|---------|
| `t_test_p_threshold` | `0.05` | Gate pass threshold for one-sided t-test |
| `alternative` | `"greater"` | scipy.stats.ttest_ind alternative parameter |

The `run_analysis` function receives `config: HM2Config` directly and reads these fields.

---

## A-8: Visualization Config [Complexity: 14, Budget: 14]

Applied: Standard matplotlib/seaborn defaults

No separate config class. Visualization functions receive `figures_dir: str` directly from `config.figures_dir`.

Figure filenames (hardcoded in each plot function):

| Function | Output File |
|----------|-------------|
| `plot_gate_metrics` | `gate_metrics.png` |
| `plot_depth_distribution` | `depth_distribution.png` |
| `plot_depth_by_error_type` | `depth_by_error_type.png` |
| `plot_depth_cdf` | `depth_cdf.png` |
| `plot_depth_scatter` | `depth_scatter.png` |

---

*Generated by Phase 3 Config Workflow | Anonymous Research Pipeline*
*Hypothesis: H-M2 | Type: MECHANISM | Gate: SHOULD_WORK*
*Base Config Verified from: h-m1/code/config.py (actual implementation)*
