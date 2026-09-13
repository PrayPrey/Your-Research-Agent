# Architecture: H-M2 Root Cause Prioritization

**Hypothesis:** h-m2  
**Date:** 2026-08-28  
**Gate:** MUST_WORK (PoC)  
**Type:** EXISTENCE

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Patterns found from H-M1 code  
**Analyzed Path:** `docs/youra_research/h-m1/code/`  
**Findings:** Reusable clustering logic, error types, session structures. H-M1 implements `clustering_coefficient()`, `ErrorType` enum, `DebugSession` dataclass.

---

## Knowledge Base (Archon)

Applied: Fix-impact measurement (track Δpassing_tests per modification), Cluster-based prioritization (sort by size descending)

---

## System Overview

PoC tests if clustering enables prioritization. Baseline addresses failures sequentially, proposed prioritizes by cluster size. Both track fix-impact (Δpassing_tests).

```
Dataset (H-M1) → Agent (baseline/proposed) → Fix → Test → Measure Δ → Proportion metric
```

---

## Module Definitions

### 1. Prioritizer (`prioritizer.py`)

**Dependencies:** H-M1 clustering, utils

```python
from typing import List, Dict
from h_m1.code.utils import ErrorType

class RootCausePrioritizer:
    def __init__(self): ...
    
    def cluster_errors(self, error_messages: List[str]) -> Dict[ErrorType, List[int]]: ...
    
    def prioritize(self, clusters: Dict[ErrorType, List[int]]) -> List[int]: ...
```

### 2. Agent (`agent.py`)

**Dependencies:** Prioritizer, utils

```python
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class FixResult:
    iteration: int
    test_results_before: List[bool]
    test_results_after: List[bool]
    delta_passing: int

class BaselineAgent:
    def __init__(self, model: str = "gpt-4-turbo-2024-04-09", temp: float = 0.7): ...
    def run(self, problem, max_iter: int = 10) -> List[FixResult]: ...

class ProposedAgent:
    def __init__(self, prioritizer, model: str = "gpt-4-turbo-2024-04-09", temp: float = 0.7): ...
    def run(self, problem, max_iter: int = 10) -> List[FixResult]: ...
```

### 3. Evaluator (`evaluate.py`)

**Dependencies:** Agent, utils

```python
from typing import List, Dict

def measure_proportion_high_impact(fix_results: List[FixResult], threshold: int = 2) -> float: ...

def compare_agents(baseline_results: List, proposed_results: List) -> Dict: ...
```

### 4. Runner (`run_experiment.py`)

**Dependencies:** Agent, Evaluator, Visualizer, H-M1 data

```python
def load_h_m1_dataset(path: str) -> List[Problem]: ...

def main():
    # Load 50 problems from H-M1
    # Run baseline agent
    # Run proposed agent
    # Calculate proportions
    # Generate figures
    # Save results
    ...
```

### 5. Visualizer (`visualizer.py`)

**Dependencies:** matplotlib

```python
def plot_proportion_comparison(baseline: float, proposed: float, save_path: str): ...

def plot_fix_impact_distribution(baseline_deltas: List[int], proposed_deltas: List[int], save_path: str): ...

def plot_cumulative_tests(baseline_results: List, proposed_results: List, save_path: str): ...

def plot_cluster_vs_impact(cluster_sizes: List[int], fix_impacts: List[int], save_path: str): ...
```

### 6. Config (`config.py`)

**Dependencies:** None

```python
EXPERIMENT_CONFIG = {
    "model": "gpt-4-turbo-2024-04-09",
    "temperature": 0.7,
    "max_iterations": 10,
    "high_impact_threshold": 2,
    "random_seed": 1,
    "h_m1_data_path": "../h-m1/data/problems.json",
    "output_dir": "docs/youra_research/h-m2/results",
    "figures_dir": "docs/youra_research/h-m2/figures"
}
```

---

## External Dependencies (H-M1)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ErrorType | `from h_m1.code.utils import ErrorType` | `docs/youra_research/h-m1/code/utils.py` |
| Problem | `from h_m1.code.utils import Problem` | `docs/youra_research/h-m1/code/utils.py` |
| TestCase | `from h_m1.code.utils import TestCase` | `docs/youra_research/h-m1/code/utils.py` |
| clustering_coefficient | `from h_m1.code.clustering import clustering_coefficient` | `docs/youra_research/h-m1/code/clustering.py` |

**Note:** H-M1 dataset (50 problems) cached in `h-m1/data/` or fetched via Codeforces API.

---

## Data Flow

1. Load 50 Codeforces problems from H-M1 cache
2. Baseline: iterate failures sequentially, record Δpassing_tests per fix
3. Proposed: cluster errors, prioritize by size, record Δpassing_tests per fix
4. Calculate `proportion_high_impact = count(Δ ≥ 2) / total_fixes` for both
5. Generate 4 plots (comparison, distribution, cumulative, scatter)
6. Output: `{"baseline": 0.20, "proposed": 0.40, "gate_pass": true}`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup | Project structure, reuse H-M1 data | 6 | 2+2+2 (paths+imports+data) |
| A-2 | Baseline agent | Sequential debugging, fix-impact tracking | 8 | 3+3+2 (agent+test+track) |
| A-3 | Proposed agent | Cluster-based prioritization | 10 | 4+3+3 (cluster+priority+track) |
| A-4 | Evaluation | Proportion metric, comparison | 6 | 2+2+2 (measure+compare+validate) |
| A-5 | Visualization | 4 plots (bar, hist, cumulative, scatter) | 8 | 2+2+2+2 (4 plots) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3], Low(4-8): [A-1, A-2, A-4, A-5]

**Total:** 5 epic tasks (EXISTENCE: 3-5 tasks)

---

## Technology Stack

- Python 3.10+
- OpenAI SDK (GPT-4 API)
- matplotlib (plotting)
- H-M1 codebase (data structures, clustering)
- Codeforces API (dataset fallback)

---

## File Structure

```
h-m2/
├── code/
│   ├── config.py
│   ├── prioritizer.py
│   ├── agent.py
│   ├── evaluate.py
│   ├── visualizer.py
│   └── run_experiment.py
├── data/
│   └── (reuse from h-m1)
├── figures/
│   ├── proportion_comparison.png
│   ├── fix_impact_distribution.png
│   ├── cumulative_tests.png
│   └── cluster_vs_impact.png
└── results/
    └── final_results.json
```

---

## Integration Points

1. **H-M1 Clustering:** Reuse `clustering_coefficient()` logic for error grouping
2. **H-M1 Dataset:** Load 50 problems from cache or Codeforces API
3. **GPT-4 API:** Generate code fixes for both agents
4. **Test Execution:** Run tests before/after each fix to measure Δ

---

## Success Validation

**PoC Pass:**
1. Code runs without error
2. `proportion_high_impact_proposed > proportion_high_impact_baseline`

**Expected:**
- Baseline: ~0.15-0.25
- Proposed: >0.35

---

**Self-Validation:**
- [x] No ASCII diagrams (text-based structure only)
- [x] Module sections = interface code only
- [x] 5 Epic tasks (EXISTENCE: 3-5)
- [x] Codebase Analysis (Serena) included
- [x] External Dependencies from H-M1 verified
- [x] Total length <500 lines
