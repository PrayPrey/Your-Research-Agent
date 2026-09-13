---
hypothesis_id: h-m1
hypothesis_type: MECHANISM
phase: Phase 3
date: 2026-03-21
applied_patterns: ["PyTorch determinism setup", "Pairwise distance metric", "Statistical independence testing"]
---

# Architecture: H-M1 Seed Independence

**Hypothesis:** Random seed initialization creates independent training runs without cross-run contamination.

**Gate Type:** MUST_WORK

**Success Criteria:** Mean pairwise weight distance > 0 with p < 0.05 for all 4 conditions (2 architectures × 2 datasets).

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Analyzed h-e1 base code structure for reuse
**Analyzed Path:** `/home/anonymous/YouRA_results_new_4_sonnet45/TEST_question/docs/youra_research/20260318_question/h-e1/code/`
**Findings:** Reusable components identified - model architectures (SimpleMLP1Layer, SimpleMLP2Layer), data loaders (MNIST/Fashion-MNIST), determinism setup. H-M1 is initialization-only (no training), so train.py not needed.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From h-e1 Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| SimpleMLP1Layer | `from h_e1.code.model import SimpleMLP1Layer` | `h-e1/code/model.py` |
| SimpleMLP2Layer | `from h_e1.code.model import SimpleMLP2Layer` | `h-e1/code/model.py` |
| load_dataset | `from h_e1.code.data import load_dataset` | `h-e1/code/data.py` |

**Verified from:** `h-e1/code/` (actual implementation)

**Note:** H-M1 will create minimal wrappers in its own code directory but reuse h-e1 model/data infrastructure.

---

## System Architecture

### File Structure

```
h-m1/
└── code/
    ├── config.py          # Experiment configuration
    ├── seed_tester.py     # Seed independence core logic
    ├── statistics.py      # Pairwise distance + t-test
    ├── visualize.py       # Histograms, heatmaps, comparison
    └── run_experiment.py  # Main entry point
```

---

## Module Specifications

### 1. Configuration (`code/config.py`)

**Dependencies:** None

```python
from dataclasses import dataclass
from typing import List

@dataclass
class ExperimentConfig:
    seeds: List[int]
    architectures: List[str]
    datasets: List[str]
    data_root: str
    device: str
    output_dir: str

@dataclass
class DeterminismConfig:
    cublas_workspace_config: str
    cudnn_deterministic: bool
    cudnn_benchmark: bool
```

---

### 2. Seed Independence Tester (`code/seed_tester.py`)

**Dependencies:** torch, h_e1.code.model

```python
import torch
import torch.nn as nn
from typing import Dict, List

def setup_determinism(seed: int) -> None: ...

def initialize_model_with_seed(architecture: str, seed: int) -> nn.Module: ...

def extract_parameters(model: nn.Module) -> torch.Tensor: ...

def run_seed_independence_test(
    architecture: str,
    seeds: List[int],
    device: str
) -> Dict[str, torch.Tensor]: ...
```

---

### 3. Statistical Analysis (`code/statistics.py`)

**Dependencies:** numpy, scipy

```python
import numpy as np
from scipy import stats
from itertools import combinations
from typing import Dict, List

def compute_pairwise_distances(
    models_dict: Dict[int, torch.Tensor]
) -> np.ndarray: ...

def test_independence(distances: np.ndarray) -> Dict[str, float]: ...

def compute_all_statistics(
    models_dict: Dict[int, torch.Tensor]
) -> Dict[str, float]: ...
```

---

### 4. Visualization (`code/visualize.py`)

**Dependencies:** matplotlib, seaborn, numpy

```python
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import Dict, List

def plot_distance_distribution(
    distances: np.ndarray,
    condition: str,
    save_path: Path
) -> None: ...

def plot_distance_heatmap(
    models_dict: Dict[int, torch.Tensor],
    condition: str,
    save_path: Path
) -> None: ...

def plot_condition_comparison(
    all_results: Dict[str, np.ndarray],
    save_path: Path
) -> None: ...

def plot_gate_metrics(
    results: Dict[str, Dict[str, float]],
    save_path: Path
) -> None: ...
```

---

### 5. Experiment Runner (`code/run_experiment.py`)

**Dependencies:** seed_tester, statistics, visualize, config

```python
import torch
from pathlib import Path
from typing import Dict
import json

def run_single_condition(
    architecture: str,
    dataset: str,
    config: ExperimentConfig
) -> Dict[str, float]: ...

def run_all_conditions(config: ExperimentConfig) -> Dict[str, Dict[str, float]]: ...

def save_results(
    results: Dict[str, Dict[str, float]],
    output_dir: Path
) -> None: ...

def generate_validation_report(
    results: Dict[str, Dict[str, float]],
    output_dir: Path
) -> None: ...

def main() -> None: ...
```

---

## Data Flow

```
Seeds [0-29]
  → setup_determinism(seed)
  → initialize_model_with_seed(arch, seed)
  → extract_parameters(model)
  → models_dict {seed: params}
  → compute_pairwise_distances(models_dict)
  → distances [435 pairs]
  → test_independence(distances)
  → {mean, std, t-stat, p-value}
  → Gate Decision (PASS if p < 0.05 for all 4 conditions)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment Setup | Create config, determinism setup | 6 | 2+1+2+1 |
| A-2 | Seed Tester | Implement model initialization with seed control | 9 | 3+2+2+2 |
| A-3 | Distance Computation | Pairwise Euclidean distance for 435 pairs | 8 | 2+2+3+1 |
| A-4 | Statistical Testing | One-sample t-test, significance check | 7 | 2+1+3+1 |
| A-5 | Multi-Condition Runner | Execute 4 conditions (2 arch × 2 dataset) | 10 | 3+3+2+2 |
| A-6 | Visualization System | Histograms, heatmaps, comparison plots | 11 | 3+2+4+2 |
| A-7 | Results Logging | JSON output, gate validation | 6 | 2+1+2+1 |
| A-8 | Integration Testing | End-to-end test, validation report | 8 | 2+2+2+2 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-5, A-6], Low(4-8): [A-1, A-3, A-4, A-7, A-8]

**Total Complexity:** 65 (8 tasks)

---

## Complexity Scoring Details

### A-1: Environment Setup (6)
- Module_Size: 2 (config dataclasses, determinism flags)
- Dependencies: 1 (torch only)
- Algorithm: 2 (determinism setup protocol)
- Integration: 1 (standalone config)

### A-2: Seed Tester (9)
- Module_Size: 3 (seed loop, model factory, param extraction)
- Dependencies: 2 (torch, h_e1.code.model)
- Algorithm: 2 (deterministic initialization)
- Integration: 2 (calls h-e1 models)

### A-3: Distance Computation (8)
- Module_Size: 2 (flatten params, compute L2)
- Dependencies: 2 (numpy, itertools)
- Algorithm: 3 (pairwise combinations 30 choose 2)
- Integration: 1 (pure function)

### A-4: Statistical Testing (7)
- Module_Size: 2 (t-test, summary stats)
- Dependencies: 1 (scipy.stats)
- Algorithm: 3 (one-sample t-test implementation)
- Integration: 1 (pure function)

### A-5: Multi-Condition Runner (10)
- Module_Size: 3 (4 condition loops, orchestration)
- Dependencies: 3 (seed_tester, statistics, config)
- Algorithm: 2 (nested loops)
- Integration: 2 (coordinates all modules)

### A-6: Visualization System (11)
- Module_Size: 3 (4 plot types)
- Dependencies: 2 (matplotlib, seaborn)
- Algorithm: 4 (heatmap construction, boxplot aggregation)
- Integration: 2 (reads results dict)

### A-7: Results Logging (6)
- Module_Size: 2 (JSON serialization, file I/O)
- Dependencies: 1 (json, pathlib)
- Algorithm: 2 (format results, gate logic)
- Integration: 1 (file output)

### A-8: Integration Testing (8)
- Module_Size: 2 (test suite, validation)
- Dependencies: 2 (pytest, all modules)
- Algorithm: 2 (end-to-end workflow)
- Integration: 2 (validates full pipeline)

---

## Implementation Notes

### Determinism Protocol (FR-1)
```python
def setup_determinism(seed: int) -> None:
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    os.environ['CUBLAS_WORKSPACE_CONFIG'] = ':16:8'
```

### Model Initialization (FR-2)
```python
def initialize_model_with_seed(architecture: str, seed: int) -> nn.Module:
    setup_determinism(seed)
    if architecture == "1layer":
        from h_e1.code.model import SimpleMLP1Layer
        model = SimpleMLP1Layer()
    elif architecture == "2layer":
        from h_e1.code.model import SimpleMLP2Layer
        model = SimpleMLP2Layer()
    return model
```

### Pairwise Distance (FR-4)
```python
def compute_pairwise_distances(models_dict: Dict[int, torch.Tensor]) -> np.ndarray:
    distances = []
    for (seed_i, params_i), (seed_j, params_j) in combinations(models_dict.items(), 2):
        dist = torch.norm(params_i - params_j, p=2).item()
        distances.append(dist)
    return np.array(distances)
```

### Statistical Test (FR-5)
```python
def test_independence(distances: np.ndarray) -> Dict[str, float]:
    t_stat, p_value = stats.ttest_1samp(distances, 0, alternative='greater')
    return {
        'mean_distance': float(np.mean(distances)),
        'std_distance': float(np.std(distances)),
        't_statistic': float(t_stat),
        'p_value': float(p_value),
        'n_pairs': len(distances)
    }
```

---

## Success Criteria Mapping

| Criterion | Module | Metric |
|-----------|--------|--------|
| Mean distance > 0 | statistics.py | mean_distance |
| p < 0.05 | statistics.py | p_value |
| All 4 conditions pass | run_experiment.py | gate_result |
| No clustering | visualize.py | distance_histogram |

---

## Risk Mitigation

### R1: PyTorch Non-Determinism
- **Mitigation:** Set CUBLAS_WORKSPACE_CONFIG, verify with checksums
- **Module:** seed_tester.py (setup_determinism)

### R2: Import Path Issues
- **Mitigation:** Use relative imports from h-e1 code directory
- **Module:** seed_tester.py (model factory)

### R3: Statistical Power
- **Mitigation:** 30 seeds = 435 pairs, sufficient for t-test
- **Module:** statistics.py (hardcoded seed range)

---

*Generated by Phase 3 Architecture Agent*
*Next: Phase 4 Implementation (Epic Task Execution)*
