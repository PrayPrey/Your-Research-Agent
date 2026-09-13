# Config: H-M3 Feedback-Guided Repair Loop

**Date:** 2026-08-31
**Author:** yoon303@etri.re.kr
**Type:** MECHANISM — incremental from H-M2

Applied: repair-loop-per-iteration-tracking pattern (Olausson 2023 / Reflexion)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2 exists)
**Status**: config verified from base code (`h-m2/code/src/measure.py`, `run_h_m2.py`)
**Config Files Found**: No `config.py` in H-M2 — uses inline constructor args and module-level path constants
**Pattern Used**: dataclass (new for H-M3; H-M2 used none)

---

## Inherited Configuration (Base Hypothesis)

H-M2 has no config dataclass. Relevant defaults verified from actual code:

```python
# From: h-m2/code/src/measure.py (ACTUAL CODE)
# FeedbackMeasurer.__init__(self, timeout_secs: int = 10)
# measure_z3 uses: solver.set("timeout", (self.timeout * 1000) - 500)

# From: h-m2/code/run_h_m2.py (ACTUAL CODE)
FIGURES_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results", "h-m2")
# Workers: ThreadPoolExecutor used but worker count not extracted to constant
```

**Verified defaults inherited by H-M3:**
- `timeout_secs = 10` (pyright, mypy, execution — FeedbackMeasurer default)
- Z3 effective timeout = `timeout_secs * 1000 - 500` ms (30s → 29500ms used below)
- Figures at sibling `figures/` directory relative to `code/`

---

## A-4 / A-7: RepairLoopConfig + ExperimentConfig [Budget: 2 subtasks]

```python
from dataclasses import dataclass, field

@dataclass
class RepairLoopConfig:
    model: str = "gpt-4o-mini"
    max_iterations: int = 3          # Olausson 2023: diminishing returns after 3
    temperature: float = 0.0         # Olausson 2023 / Shinn 2023: deterministic repair
    repair_prompt_template: str = (
        "Problem: {problem_prompt}\n\n"
        "Previous solution (FAILED):\n```python\n{previous_solution}\n```\n\n"
        "Feedback from {feedback_category} verifier:\n{feedback_text}\n\n"
        "Fix the solution. Return only the corrected code:\n```python\n"
    )

@dataclass
class ExperimentConfig:
    n_workers: int = 4               # ThreadPoolExecutor; problem-level parallelism
    output_dir: str = "results/h-m3"
    figures_dir: str = "../figures"  # sibling to code/, matches H-M2 pattern
    h_m1_results_path: str = "../../h-m1/code/results/h-m1/results.jsonl"
    h_m2_code_path: str = "../../h-m2/code"
    datasets: list = field(default_factory=lambda: ["humaneval", "mbpp"])
    seed: int = 42                   # unused (temperature=0.0 is deterministic), kept for reproducibility docs
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | RepairLoopConfig | dataclass with model/iterations/temperature/prompt |
| C-7-1 | ExperimentConfig | dataclass with workers/paths/datasets |

---

## A-2: VerifierConfig [Budget: 1 subtask]

```python
@dataclass
class VerifierConfig:
    pyright_timeout: int = 10    # Inherited: FeedbackMeasurer default
    execution_timeout: int = 5   # Non-standard: shorter than default; execution errors are fast
    mypy_timeout: int = 10       # Inherited: FeedbackMeasurer default
    z3_timeout: int = 30         # Non-standard: Z3 SMT solving needs more time than text tools
    z3_max_problems: int = 50    # Guard against Z3 over-running on large batches
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | VerifierConfig | timeout wiring for all 4 verifier adapters |

---

## A-8: AnalysisConfig [Budget: 1 subtask]

```python
@dataclass
class AnalysisConfig:
    n_bootstrap: int = 1000          # Bootstrap CI iterations (standard)
    ci: float = 0.95                 # 95% CI
    include_z3_in_correlation: bool = True   # Primary gate uses all 4 categories
    ablation_flags: list = field(default_factory=lambda: [
        "without_z3",
        "iter2_correlation",
        "by_dataset",
        "bug_type_subgroup",
    ])
    specificity_ranks: dict = field(default_factory=lambda: {
        "pyright": 1,
        "execution": 2,
        "mypy": 3,
        "z3": 4,
    })
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | AnalysisConfig | bootstrap, ablation flags, specificity rank map |

---

## A-9: VisualizationConfig [Budget: 1 subtask]

```python
@dataclass
class VisualizationConfig:
    figure_output_dir: str = "../figures"
    figsize: tuple = (10, 6)
    dpi: int = 150
    style: str = "seaborn-v0_8-whitegrid"
    figures: list = field(default_factory=lambda: [
        "bar_iter1_rate.png",
        "line_cumulative_repair.png",
        "heatmap_mean_iterations.png",
        "scatter_length_vs_rate.png",
        "scatter_z3_subgroup.png",
    ])
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | VisualizationConfig | figure paths, size, dpi, style |

---

## Full Config YAML: experiment.yaml

```yaml
# docs/youra_research/h-m3/code/experiment.yaml
repair_loop:
  model: gpt-4o-mini
  max_iterations: 3
  temperature: 0.0

experiment:
  n_workers: 4
  output_dir: results/h-m3
  figures_dir: ../figures
  h_m1_results_path: ../../h-m1/code/results/h-m1/results.jsonl
  h_m2_code_path: ../../h-m2/code
  datasets:
    - humaneval
    - mbpp

verifier:
  pyright_timeout: 10
  execution_timeout: 5
  mypy_timeout: 10
  z3_timeout: 30
  z3_max_problems: 50

analysis:
  n_bootstrap: 1000
  ci: 0.95
  include_z3_in_correlation: true
  ablation_flags:
    - without_z3
    - iter2_correlation
    - by_dataset
    - bug_type_subgroup
  specificity_ranks:
    pyright: 1
    execution: 2
    mypy: 3
    z3: 4

visualization:
  figure_output_dir: ../figures
  figsize: [10, 6]
  dpi: 150
  style: seaborn-v0_8-whitegrid
```

---

## Valid Ranges & Constraints

| Parameter | Type | Valid Range | Notes |
|-----------|------|-------------|-------|
| max_iterations | int | 1–10 | >3 has diminishing returns (Olausson 2023) |
| temperature | float | 0.0–2.0 | Fixed at 0.0 for determinism |
| n_workers | int | 1–16 | 4 matches PRD NFR |
| pyright_timeout | int | 5–60 | seconds |
| execution_timeout | int | 1–30 | seconds |
| mypy_timeout | int | 5–60 | seconds |
| z3_timeout | int | 10–120 | seconds |
| z3_max_problems | int | 1–538 | guard against full batch Z3 hangs |
| n_bootstrap | int | 100–10000 | 1000 is standard |
| ci | float | 0.80–0.99 | 0.95 standard |
| dpi | int | 72–300 | 150 balances file size and quality |
