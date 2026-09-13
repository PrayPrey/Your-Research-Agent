# Architecture: H-M1

**Hypothesis:** H-M1 (MECHANISM PoC)
**Type:** Statistical Analysis — no GPU, no new inference
**Applied:** statistical-analysis-pipeline (scipy.stats + numpy, YAML config + dataclass, structured logging, unit tests)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: Patterns found from base code (direct file reads; Serena project activation unavailable but files read directly)
**Analyzed Path**: `docs/youra_research/20260315_question/h-e1/code/`
**Findings**: H-E1 uses flat module layout (`config.py`, `data.py`, `model.py`, `evaluate.py`, `run_experiment.py`) with `from config import ExperimentConfig` (relative imports, no package structure). `TaskData` dataclass in `data.py`; `TaskResult` dataclass in `evaluate.py`. H-M1 reuses `data.py` label-loading logic and `evaluate.py`'s `cohen_d()`.

---

## File Organization

```
h-m1/code/
├── config.py           # ExperimentConfig dataclass + load_config()
├── config.yaml         # YAML configuration
├── data.py             # Score loading + label loading (extends h-e1/data.py pattern)
├── analyze.py          # KL divergence, Wilcoxon, near-uniform, Cohen's d
├── visualize.py        # 5 required figures
├── run_experiment.py   # Main entry point
└── tests/
    ├── __init__.py
    ├── test_config.py
    ├── test_data.py
    ├── test_analyze.py
    └── test_run_experiment.py
h-m1/results/
├── h_m1_results.json
└── h_m1_summary.json
h-m1/figures/
├── gate_metrics_comparison.png
├── score_distributions_violin.png
├── kl_divergence_summary.png
├── score_separation_boxplot.png
└── near_uniform_proportion.png
```

---

## Module Definitions

### ExperimentConfig (`config.py`)

**Dependencies**: dataclasses, yaml, pathlib

```python
from dataclasses import dataclass, field
from typing import Tuple, Dict
import yaml

@dataclass
class ExperimentConfig:
    # Data paths
    h_e1_results_path: str = "../../h-e1/results/h-e1_results.json"
    halueval_hf_id: str = "pminervini/HaluEval"
    tasks: Tuple[str, ...] = ("dialogue", "qa", "summarization")
    hf_config_names: Dict[str, str] = field(default_factory=lambda: {
        "dialogue": "dialogue", "qa": "qa", "summarization": "summarization"
    })
    # HaluEval column names (same as h-e1)
    premise_fields: Dict[str, str] = field(default_factory=lambda: {
        "dialogue": "knowledge", "qa": "knowledge", "summarization": "document"
    })
    hypothesis_right_fields: Dict[str, str] = field(default_factory=lambda: {
        "dialogue": "right_response", "qa": "right_answer", "summarization": "right_summary"
    })
    hypothesis_hall_fields: Dict[str, str] = field(default_factory=lambda: {
        "dialogue": "hallucinated_response", "qa": "hallucinated_answer",
        "summarization": "hallucinated_summary"
    })
    # Statistical thresholds
    kl_threshold: float = 0.05
    wilcoxon_alpha: float = 0.05
    near_uniform_threshold: float = 0.05
    near_uniform_warn_threshold: float = 0.50
    wilcoxon_tasks_required: int = 2
    seed: int = 42
    # Output
    results_dir: str = "../results"
    figures_dir: str = "../figures"
    results_filename: str = "h_m1_results.json"
    summary_filename: str = "h_m1_summary.json"

def load_config(path: str = "config.yaml") -> ExperimentConfig: ...
```

---

### DataLoader (`data.py`)

**Dependencies**: config.py, numpy, datasets, json, logging

```python
from dataclasses import dataclass
from typing import Dict, List
import numpy as np

@dataclass
class TaskScores:
    task_name: str
    scores_nxt3: np.ndarray   # shape (N, 3): [P(contra), P(neutral), P(entail)]
    labels_n: np.ndarray      # shape (N,), binary {0, 1}
    n_examples: int

def load_h_e1_scores(results_path: str) -> Dict[str, np.ndarray]:
    """Load pre-computed (N,3) score matrices from h-e1_results.json.
    Raises FileNotFoundError with instructive message if missing.
    Returns: {task_name: np.ndarray shape (N,3)}
    """
    ...

def load_halueval_labels(task_name: str, config: "ExperimentConfig") -> np.ndarray:
    """Reload HaluEval labels using same interleaving logic as h-e1/data.py.
    Returns: np.ndarray shape (N,), binary labels, balanced 50/50
    """
    ...

def load_task_data(task_name: str, scores_dict: Dict[str, np.ndarray],
                   config: "ExperimentConfig") -> TaskScores:
    """Combine scores and labels for one task. Verifies N matches."""
    ...

def load_all_tasks(config: "ExperimentConfig") -> List[TaskScores]:
    """Load all 3 tasks. Verifies shapes (20000, 3) per task."""
    ...
```

---

### StatisticalAnalyzer (`analyze.py`)

**Dependencies**: data.py, numpy, scipy.stats, logging

```python
from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np

@dataclass
class TaskAnalysisResult:
    task_name: str
    kl_divergence_from_uniform: float
    kl_passes: bool
    wilcoxon_pvalue: float
    wilcoxon_statistic: float
    wilcoxon_passes: bool
    p_near_uniform: float
    class_means: List[float]   # [P(contra), P(neutral), P(entail)] means
    cohens_d: float
    not_near_uniform: bool

@dataclass
class GateResult:
    gate_pass: bool
    kl_all_pass: bool
    wilcoxon_pass_count: int
    mechanism_activated: bool

def analyze_nli_distribution(scores_nxt3: np.ndarray, labels_n: np.ndarray,
                              task_name: str,
                              config: "ExperimentConfig") -> TaskAnalysisResult:
    """KL divergence + Wilcoxon + near-uniform + Cohen's d for one task."""
    ...

def compute_cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Pooled-std Cohen's d. Reuses logic from h-e1/evaluate.py."""
    ...

def evaluate_gate(results: List[TaskAnalysisResult],
                  config: "ExperimentConfig") -> GateResult:
    """Apply MUST_WORK gate: KL > 0.05 on all 3 + Wilcoxon p < 0.05 on >= 2/3."""
    ...

def verify_mechanism_activated(results: List[TaskAnalysisResult],
                                config: "ExperimentConfig") -> Tuple[bool, Dict]:
    """Per-task indicators: kl_passes, wilcoxon_passes, not_near_uniform."""
    ...
```

---

### Visualizer (`visualize.py`)

**Dependencies**: analyze.py, data.py, matplotlib, seaborn, numpy, logging

```python
from typing import List

def plot_gate_metrics_comparison(results: List["TaskAnalysisResult"],
                                  output_path: str) -> None:
    """2-subplot: KL divergence bars + Wilcoxon p-values (log scale) with thresholds."""
    ...

def plot_score_distributions_violin(task_data_list: List["TaskScores"],
                                     output_path: str) -> None:
    """Per-task violin: P(contra/neutral/entail) for hallu vs non-hallu + uniform ref."""
    ...

def plot_kl_divergence_summary(results: List["TaskAnalysisResult"],
                                output_path: str) -> None:
    """3x3 bar chart: KL per task x per NLI class. Threshold at 0.05."""
    ...

def plot_score_separation_boxplot(task_data_list: List["TaskScores"],
                                   results: List["TaskAnalysisResult"],
                                   output_path: str) -> None:
    """Box plots: P(contradiction) hallu vs correct per task, annotated with p-values."""
    ...

def plot_near_uniform_proportion(results: List["TaskAnalysisResult"],
                                  output_path: str) -> None:
    """Stacked bar: p_near_uniform per task with target < 5% line."""
    ...

def generate_all_figures(task_data_list: List["TaskScores"],
                          results: List["TaskAnalysisResult"],
                          figures_dir: str) -> None:
    """Generate and save all 5 required figures."""
    ...
```

---

### RunExperiment (`run_experiment.py`)

**Dependencies**: config.py, data.py, analyze.py, visualize.py, json, logging, pathlib

```python
import logging
from pathlib import Path

def setup_logging() -> None: ...

def save_results(results: List["TaskAnalysisResult"], gate: "GateResult",
                 config: "ExperimentConfig") -> None:
    """Save h_m1_results.json (full) and h_m1_summary.json (gate fields)."""
    ...

def main() -> None:
    """
    Execution order:
    1. load_config("config.yaml")
    2. Precondition check: verify h-e1_results.json exists + shape
    3. load_all_tasks(config)
    4. analyze_nli_distribution() per task
    5. evaluate_gate(results, config)
    6. save_results()
    7. generate_all_figures()
    8. Log gate: PASS or FAIL
    """
    ...

if __name__ == "__main__":
    main()
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Reuse Pattern | File Location |
|--------|---------------|---------------|
| ExperimentConfig structure | Extend with new fields | `h-e1/code/config.py` |
| load_task() interleaving logic | Copy/adapt into h-m1/data.py | `h-e1/code/data.py` |
| cohen_d() | Inline or import via sys.path | `h-e1/code/evaluate.py` |
| Pre-computed scores | Load via JSON path | `h-e1/results/h-e1_results.json` (actual output: `h-e1/code/outputs/h-e1_summary.json` also present) |

**Verified from**: `h-e1/code/` actual implementation.

**Import strategy**: H-M1 code uses relative imports (`from config import ...`) matching H-E1 flat module pattern. H-E1 code NOT imported directly — logic is copied/adapted to avoid sys.path manipulation.

**Note on H-E1 results path**: H-E1 `config.py` saves to `results_dir = "results"` with `scores_filename = "h-e1_results.json"`. Actual outputs found at `h-e1/code/outputs/`. H-M1 config should support configurable path with fallback detection.

---

## config.yaml

```yaml
h_e1_results_path: "../../h-e1/results/h-e1_results.json"
halueval_hf_id: "pminervini/HaluEval"
tasks: ["dialogue", "qa", "summarization"]
kl_threshold: 0.05
wilcoxon_alpha: 0.05
near_uniform_threshold: 0.05
near_uniform_warn_threshold: 0.50
wilcoxon_tasks_required: 2
seed: 42
results_dir: "../results"
figures_dir: "../figures"
results_filename: "h_m1_results.json"
summary_filename: "h_m1_summary.json"
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Directory structure, config.yaml, config.py dataclass, requirements.txt | 7 | 2+1+1+3 |
| A-2 | Data Loading | load_h_e1_scores() with precondition check + load_halueval_labels() with interleaving logic | 10 | 2+2+3+3 |
| A-3 | Statistical Analysis Core | analyze_nli_distribution(): KL divergence, Wilcoxon rank-sum, near-uniform, Cohen's d | 12 | 3+2+4+3 |
| A-4 | Gate Evaluation | evaluate_gate() + verify_mechanism_activated() + logging | 8 | 2+2+2+2 |
| A-5 | Results Persistence | save_results(): h_m1_results.json + h_m1_summary.json | 6 | 1+2+1+2 |
| A-6 | Visualization - Gate Metrics | plot_gate_metrics_comparison(): KL bars + Wilcoxon p-values (mandatory figure) | 9 | 2+2+3+2 |
| A-7 | Visualization - Distributions | plot_score_distributions_violin() + plot_kl_divergence_summary() | 10 | 2+2+4+2 |
| A-8 | Visualization - Separation | plot_score_separation_boxplot() + plot_near_uniform_proportion() | 9 | 2+2+3+2 |
| A-9 | Main Orchestration | run_experiment.py: full pipeline with structured logging | 9 | 2+3+2+2 |
| A-10 | Unit Tests | test_config, test_data, test_analyze, test_run_experiment | 11 | 3+2+3+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-6, A-7, A-8, A-9, A-10], Low(4-8): [A-1, A-4, A-5]
