# Architecture: H-M2 — Budget-Ratio Dose-Response Analysis

**Applied**: budget-sweep-evaluation pattern (multi-budget LongBench inference loop with Spearman monotonicity gate)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-M1, which extends H-E1)
**Status**: patterns found from base code (direct file reads; Serena MCP unavailable in no-mcp environment)
**Analyzed Path**: `h-e1/code/` and `h-m1/code/`
**Findings**: H-M1 uses `importlib` dynamic loading to import H2OEvictionAwareAttention and inject_h2o_wrappers from H-E1's model.py. H2OEvictionAwareAttention.forward() applies eviction only when `self.training=True`; H-M1 uses `set_h2o_training_mode()` to toggle. No `set_h2o_budget()` function exists in actual H-E1 code — budget ratio change requires direct attribute assignment (`module.kv_budget_ratio = r`) on all H2OEvictionAwareAttention instances.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Pattern | File Location |
|--------|---------------|---------------|
| H2OEvictionAwareAttention | importlib dynamic load | `h-e1/code/model.py` |
| inject_h2o_wrappers | importlib dynamic load | `h-e1/code/model.py` |
| load_base_model | importlib dynamic load | `h-e1/code/model.py` |
| LongBenchDataLoader | `from data import LongBenchDataLoader` | `h-m1/code/data.py` |
| LONGBENCH_CATEGORIES | `from data import LONGBENCH_CATEGORIES` | `h-m1/code/data.py` |
| load_adapter_model | `from model import load_adapter_model` | `h-m1/code/model.py` |
| set_h2o_training_mode | `from model import set_h2o_training_mode` | `h-m1/code/model.py` |

**Verified from**: `h-e1/code/model.py` and `h-m1/code/` (actual implementation)

**Critical note**: `set_h2o_budget(model, r)` does NOT exist in H-E1 code. H-M2 must implement it as:
```python
def set_h2o_budget(model, kv_budget_ratio):
    for module in model.modules():
        if isinstance(module, H2OEvictionAwareAttention):
            module.kv_budget_ratio = kv_budget_ratio
```

---

## File Organization

```
h-m2/code/
  config.py          # BudgetSweepConfig dataclass, H-E1 adapter paths
  dataset.py         # Re-exports from h-m1/code/data.py (thin wrapper)
  model.py           # load_adapter_for_sweep(), set_h2o_budget()
  evaluate.py        # BudgetSweepEvaluator, run_task_evaluation, compute_category_accuracies
  analyze.py         # SpearmanAnalyzer, GapMatrix, MonotonicityChecker
  visualize.py       # plot_gap_vs_budget, plot_spearman_bar, plot_heatmap, plot_absolute_curves
  run_experiment.py  # Orchestrator: 12-run sweep -> analyze -> visualize
  smoke_test.py      # FR-8 smoke test: 1 adapter + 3 budget ratios on short input
  tests/
    test_config.py
    test_model.py
    test_evaluate.py
    test_analyze.py
    test_visualize.py
outputs/h-m2/       # CSV per-run results, JSON Spearman summary
figures/            # PNG figures
```

---

## Module Structure

### config.py

**Dependencies**: none (stdlib only)

```python
import os
from dataclasses import dataclass, field
from typing import List

_H_E1_OUTPUTS = os.path.join(os.path.dirname(__file__), "../../h-e1/code/outputs/h-e1")
_H_M1_CODE = os.path.join(os.path.dirname(__file__), "../../h-m1/code")

BUDGET_RATIOS: List[float] = [0.25, 0.50, 0.75]

@dataclass
class AdapterSpec:
    model_name: str        # "meta-llama/Llama-2-7b-hf" | "mistralai/Mistral-7B-v0.1"
    adapter_path: str      # path to H-E1 adapter checkpoint dir
    adapter_type: str      # "sequential" | "eviction-aware"

@dataclass
class BudgetSweepConfig:
    experiment_id: str = "h-m2"
    budget_ratios: List[float] = field(default_factory=lambda: list(BUDGET_RATIOS))
    adapters: List[AdapterSpec] = field(default_factory=list)
    max_seq_length: int = 4096
    batch_size: int = 1
    seed: int = 1
    fp16: bool = True
    figures_dir: str = "figures"
    results_dir: str = "outputs/h-m2"

def get_default_config() -> BudgetSweepConfig: ...
def validate_config(cfg: BudgetSweepConfig) -> None: ...
```

---

### dataset.py

**Dependencies**: h-m1/code/data.py (re-export + scoring utilities)

```python
# Thin wrapper re-exporting H-M1 data pipeline
from importlib.util import spec_from_file_location, module_from_spec
# Dynamic import of h-m1/code/data.py

# Re-exported symbols:
LongBenchDataLoader     # class: load + tokenize LongBench with middle truncation
LONGBENCH_TASKS         # List[str]: 21 task names
LONGBENCH_CATEGORIES    # Dict[str, List[str]]: 6 categories

# H-M2-specific scoring per task
TASK_SCORER_MAP: dict   # task_name -> scorer_fn (F1 | ROUGE-L | accuracy | edit-distance)

def score_prediction(task_name: str, prediction: str, answers: list) -> float: ...
def run_task_evaluation(
    model,
    tokenizer,
    task_name: str,
    max_seq_length: int = 4096,
    device: str = "cuda",
) -> float:
    """Run full test split for one task; return mean score. batch_size=1."""
    ...

def compute_category_accuracies(per_task_scores: dict) -> dict:
    """Aggregate per-task scores to 6-category means.
    Returns: {category_name: mean_score}
    """
    ...
```

---

### model.py

**Dependencies**: h-e1/code/model.py (via importlib), h-m1/code/model.py (via importlib), peft, transformers

```python
import os, importlib.util
from typing import Optional
import torch.nn as nn

# Dynamic imports from H-E1 and H-M1 (same pattern as h-m1/code/model.py)
H2OEvictionAwareAttention  # imported from h-e1/code/model.py
inject_h2o_wrappers        # imported from h-e1/code/model.py
load_base_model            # imported from h-e1/code/model.py
load_adapter_model         # imported from h-m1/code/model.py
set_h2o_training_mode      # imported from h-m1/code/model.py

def set_h2o_budget(model: nn.Module, kv_budget_ratio: float) -> None:
    """Set kv_budget_ratio on all H2OEvictionAwareAttention wrappers.
    Raises ValueError if no H2O wrappers found (budget not applied).
    """
    ...

def verify_budget_applied(model: nn.Module, expected_ratio: float) -> bool:
    """Check all H2OEvictionAwareAttention instances have expected kv_budget_ratio."""
    ...

def load_model_for_sweep(
    model_name: str,
    adapter_path: str,
    adapter_type: str,       # "sequential" | "eviction-aware"
    initial_budget: float = 0.5,
) -> nn.Module:
    """Load base model + PEFT adapter; inject H2O wrappers for eviction-aware type.
    Sets attn_implementation='eager'. Returns model in eval mode.
    """
    ...
```

---

### evaluate.py

**Dependencies**: config.py, dataset.py, model.py

```python
from dataclasses import dataclass
from typing import Dict, List, Optional
import torch.nn as nn

@dataclass
class RunResult:
    model_name: str
    adapter_type: str    # "sequential" | "eviction-aware"
    budget_ratio: float
    per_task_scores: Dict[str, float]
    category_scores: Dict[str, float]  # 6-category means

class BudgetSweepEvaluator:
    def __init__(self, cfg): ...

    def evaluate_single_run(
        self,
        model: nn.Module,
        tokenizer,
        adapter_type: str,
        budget_ratio: float,
        model_name: str,
        device: str,
    ) -> RunResult:
        """Set budget, activate eviction (train mode), run all 21 tasks, return RunResult."""
        ...

    def run_all(self, device: str = "cuda") -> List[RunResult]:
        """Execute all 12 evaluation runs: 2 adapters × 3 budgets × 2 models.
        Loads/unloads models to manage GPU memory. Returns List[RunResult].
        """
        ...

def verify_mechanism_activated(
    model: nn.Module,
    budget_ratio: float,
    results_by_r: Dict[float, float],
) -> tuple[bool, dict]:
    """Check budget set + gap variance non-zero. Returns (all_pass, indicators)."""
    ...

def save_run_results(results: List[RunResult], output_dir: str) -> str:
    """Save per-run results as CSV. Returns path."""
    ...
```

---

### analyze.py

**Dependencies**: evaluate.py (RunResult), scipy, numpy

```python
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np

@dataclass
class GapMatrix:
    """Per-model, per-r, per-category accuracy gap (eviction-aware minus sequential)."""
    model_name: str
    # gaps[r][category] = float
    gaps: Dict[float, Dict[str, float]]
    mean_gaps: Dict[float, float]  # mean over 6 categories per r

@dataclass
class SpearmanResult:
    model_name: str
    rho: float
    pval: float
    gate_passed: bool   # rho < -0.8

@dataclass
class MonotonicityResult:
    model_name: str
    # per-category: True if gap(0.25) > gap(0.50) > gap(0.75)
    per_category: Dict[str, bool]
    fraction_monotone: float  # out of 6

class SpearmanAnalyzer:
    def compute_gap_matrix(
        self,
        results: List,   # List[RunResult]
    ) -> Dict[str, GapMatrix]:
        """Build GapMatrix per model from RunResult list."""
        ...

    def compute_spearman(
        self,
        gap_matrix: GapMatrix,
    ) -> SpearmanResult:
        """spearmanr([0.25, 0.50, 0.75], [mean_gap_25, mean_gap_50, mean_gap_75])."""
        ...

    def check_monotonicity(self, gap_matrix: GapMatrix) -> MonotonicityResult: ...

    def run_full_analysis(
        self,
        results: List,   # List[RunResult]
    ) -> dict:
        """Returns: {gap_matrices, spearman_results, monotonicity, gate_passed}."""
        ...

    def save_summary(self, analysis: dict, output_path: str) -> None:
        """Save Spearman summary as JSON."""
        ...
```

---

### visualize.py

**Dependencies**: analyze.py (GapMatrix, SpearmanResult), matplotlib, pandas

```python
from typing import Dict, List

def plot_gap_vs_budget(
    gap_matrices: Dict[str, object],  # model_name -> GapMatrix
    output_path: str,
) -> None:
    """Line plot: x=budget ratio, y=mean gap, lines per model. Mandatory gate visual."""
    ...

def plot_spearman_bar(
    spearman_results: List[object],   # List[SpearmanResult]
    threshold: float = -0.8,
    output_path: str = "",
) -> None:
    """Bar chart: Spearman rho per model, reference line at threshold."""
    ...

def plot_gap_heatmap(
    gap_matrices: Dict[str, object],
    output_path: str,
) -> None:
    """6-category x 3-budget-ratio heatmap, color=gap magnitude, per model."""
    ...

def plot_absolute_accuracy_curves(
    results: List[object],            # List[RunResult]
    output_path: str,
) -> None:
    """Per-model line plots of absolute accuracy (both adapter types at each r)."""
    ...

def save_all_figures(analysis: dict, results: List, figures_dir: str) -> None:
    """Save all 4 mandatory figures to figures_dir."""
    ...
```

---

### run_experiment.py

**Dependencies**: config.py, evaluate.py, analyze.py, visualize.py

```python
def main() -> None:
    """Orchestrator:
    1. Load config (get_default_config)
    2. Run smoke test (smoke_test.run_smoke_test)
    3. BudgetSweepEvaluator.run_all() -> List[RunResult]
    4. save_run_results() -> CSV
    5. SpearmanAnalyzer.run_full_analysis() -> dict
    6. SpearmanAnalyzer.save_summary() -> JSON
    7. save_all_figures() -> PNGs
    8. Log gate result: rho < -0.8 on >=1 model
    """
    ...

if __name__ == "__main__":
    main()
```

---

### smoke_test.py

**Dependencies**: config.py, model.py, evaluate.py, dataset.py

```python
def run_smoke_test(device: str = "cuda") -> bool:
    """FR-8: Load one adapter, sweep r in {0.25, 0.50, 0.75} on ~512-token input.
    Verifies: set_h2o_budget changes attribute; category aggregation returns 6 non-NaN.
    Returns True if all checks pass.
    """
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Directory structure, config.py with BudgetSweepConfig and H-E1 adapter path resolution | 7 | 2+1+1+3 |
| A-2 | Dataset Module | dataset.py: re-export H-M1 LongBenchDataLoader, add TASK_SCORER_MAP, run_task_evaluation, compute_category_accuracies with F1/ROUGE/accuracy scorers | 10 | 3+2+3+2 |
| A-3 | Model Module | model.py: importlib dynamic imports from H-E1/H-M1, set_h2o_budget(), verify_budget_applied(), load_model_for_sweep() with eager attn | 11 | 2+4+3+2 |
| A-4 | BudgetSweepEvaluator | evaluate.py: BudgetSweepEvaluator class, 12-run orchestration with GPU memory management, RunResult dataclass, save_run_results CSV | 13 | 3+3+3+4 |
| A-5 | SpearmanAnalyzer | analyze.py: GapMatrix computation, spearmanr gate (rho < -0.8), monotonicity check, JSON summary | 12 | 3+2+4+3 |
| A-6 | Visualization | visualize.py: 4 mandatory figures (gap line plot, Spearman bar, heatmap, absolute curves) | 10 | 3+2+2+3 |
| A-7 | Mechanism Verification | verify_mechanism_activated() in evaluate.py: budget check + gap variance + logging | 8 | 2+2+2+2 |
| A-8 | Smoke Test | smoke_test.py: FR-8 short-input sweep, budget attribute check, category aggregation validation | 7 | 2+2+1+2 |
| A-9 | Orchestrator | run_experiment.py: main() wiring all phases, CUDA_VISIBLE_DEVICES, seed, logging | 8 | 1+3+1+3 |
| A-10 | Unit Tests | tests/: config, model, evaluate, analyze, visualize coverage | 9 | 3+2+1+3 |

**Distribution**: High(11-13): [A-3, A-4, A-5], Medium(8-10): [A-2, A-6, A-7, A-9, A-10], Low(4-7): [A-1, A-8]

**Total task budget**: 10 epics (within 6-12 range). Estimated breakdown tasks: ~28 (within 30 max).

---

## Key Constraints (From Actual Code)

1. `H2OEvictionAwareAttention.forward()` only evicts when `self.training=True`. For inference-time budget sweep, H-M2 must call `set_h2o_training_mode(model, True)` before forward pass (same as H-M1).
2. H-M1 uses `importlib.util.spec_from_file_location` to load H-E1's model.py — H-M2 must follow this same pattern.
3. H-E1 adapter checkpoint paths: `outputs/h-e1/llama2-7b-{baseline,eviction-aware}/` and `outputs/h-e1/mistral-7b-{baseline,eviction-aware}/` relative to H-E1 code dir.
4. LongBench category keys in actual H-M1 code use hyphens: `"single-doc-qa"`, `"multi-doc-qa"`, `"few-shot"` (not camelCase).
5. `load_base_model` in H-E1 uses `bfloat16` if supported, else `float16` — PRD says float16 but actual code may use bfloat16; H-M2 should respect actual behavior.
