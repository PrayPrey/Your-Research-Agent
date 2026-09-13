# Architecture: h-m3 Archetype Recovery via Shape Descriptor Alignment

**Applied**: standard-dl-experiment-module-pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (h-m2 and h-e1 actual files read via Read tool; Serena project not active, direct file read used)
**Analyzed Path**: `docs/youra_research/20260325_mldpr/h-m2/code/` and `docs/youra_research/20260325_mldpr/h-e1/code/`
**Findings**: h-m2 uses 5-file pattern (config.py, data.py, model.py, evaluate.py, main.py) with dataclass config and absolute path overrides in `__main__`. h-e1 cache verified at `hf_dataset_cache.json` (not `dataset_cache.json` as PRD specifies — trust actual code).

---

## File Organization

- `h-m3/code/config.py` - ExperimentConfig dataclass
- `h-m3/code/data.py` - Data loading (h-e1 cache + h-m2 descriptors)
- `h-m3/code/model.py` - ArchetypeRecoveryMatcher + RandomBaselineMatcher
- `h-m3/code/evaluate.py` - Metrics, gate check, figures, report
- `h-m3/code/main.py` - Experiment orchestration entry point
- `h-m3/figures/` - Output figures directory

---

## Module Definitions

### ExperimentConfig (`h-m3/code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    # Data
    n_clusters: int = 4
    n_archetypes: int = 5
    random_state: int = 42

    # Alignment
    alignment_threshold: float = 0.70
    min_archetypes_recovered: int = 3

    # Normalization ranges (from h-m2 observed values)
    norm_ranges: dict = None  # populated in __post_init__

    # Paths
    h_e1_cache_path: str = "../h-e1/code/hf_dataset_cache.json"
    figures_dir: str = "h-m3/figures"
    output_path: str = "h-m3/04_validation.md"

    def __post_init__(self): ...
```

---

### DataLoader (`h-m3/code/data.py`)

**Dependencies**: ExperimentConfig, h-e1 cache, h-m2 ShapeDescriptorAnalyzer

```python
from typing import Dict, Tuple, List
import numpy as np
from config import ExperimentConfig

def load_cluster_centroids(config: ExperimentConfig) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load h-e1 time series and re-run DTW clustering to get centroids and labels.
    Mirrors h-m2/data.py: load_raw_series -> preprocess_series -> perform_clustering.

    Returns:
        centroids: (k, T) float array
        labels: (N,) int array
    """
    ...

def compute_shape_descriptors(
    centroids: np.ndarray,
    config: ExperimentConfig
) -> Dict[int, Dict[str, float]]:
    """
    Compute shape descriptors per centroid using h-m2 ShapeDescriptorAnalyzer.
    Returns dict: cluster_id -> {growth_ratio, peak_timing, changepoint_count, derivative_variance}
    """
    ...

def load_data(config: ExperimentConfig) -> Dict[int, Dict[str, float]]:
    """
    Top-level loader: returns cluster_profiles dict ready for archetype matching.
    Calls load_cluster_centroids then compute_shape_descriptors.

    Returns:
        cluster_profiles: {cluster_id: {descriptor: value, ...}}
    """
    ...

def validate_cluster_profiles(
    cluster_profiles: Dict[int, Dict[str, float]],
    config: ExperimentConfig
) -> Tuple[bool, dict]:
    """Validate k=4 clusters with 4 descriptors each."""
    ...
```

---

### ArchetypeRecoveryMatcher (`h-m3/code/model.py`)

**Dependencies**: ExperimentConfig, scipy, numpy

```python
import numpy as np
from scipy.spatial.distance import cosine
from typing import Dict, Tuple, Set
from config import ExperimentConfig

ARCHETYPE_PROFILES = {
    "sustained_growth": {"growth_ratio": 0.8, "peak_timing": 0.9, "changepoint_count": 0.2, "derivative_variance": 0.2},
    "flash_in_pan":     {"growth_ratio": 0.3, "peak_timing": 0.2, "changepoint_count": 0.8, "derivative_variance": 0.8},
    "plateau":          {"growth_ratio": 0.5, "peak_timing": 0.5, "changepoint_count": 0.2, "derivative_variance": 0.1},
    "slow_burn":        {"growth_ratio": 0.7, "peak_timing": 0.8, "changepoint_count": 0.1, "derivative_variance": 0.2},
    "revival":          {"growth_ratio": 0.4, "peak_timing": 0.6, "changepoint_count": 0.6, "derivative_variance": 0.5},
}

class ArchetypeRecoveryMatcher:
    def __init__(self, config: ExperimentConfig) -> None: ...

    def normalize_profile(self, profile: Dict[str, float]) -> Dict[str, float]: ...

    def compute_alignment(
        self, cluster_profile: Dict[str, float], archetype_name: str
    ) -> float: ...

    def build_alignment_matrix(
        self, cluster_profiles: Dict[int, Dict[str, float]]
    ) -> np.ndarray:
        """Returns (k, n_archetypes) alignment matrix."""
        ...

    def match_clusters(
        self, cluster_profiles: Dict[int, Dict[str, float]]
    ) -> Tuple[Dict[int, Tuple[str, float]], int]:
        """
        Returns (assignments, n_recovered).
        assignments: {cluster_id: (archetype_name, alignment_score)}
        n_recovered: count of distinct archetypes matched above threshold
        """
        ...


class RandomBaselineMatcher:
    def __init__(self, config: ExperimentConfig) -> None: ...

    def match_clusters(
        self, cluster_profiles: Dict[int, Dict[str, float]]
    ) -> Tuple[Dict[int, Tuple[str, float]], int]:
        """Random assignment baseline. seed=42."""
        ...
```

---

### Evaluator (`h-m3/code/evaluate.py`)

**Dependencies**: ExperimentConfig, numpy, matplotlib, seaborn

```python
import numpy as np
from typing import Dict, List, Tuple
from config import ExperimentConfig

def compute_gate_metrics(
    assignments: Dict[int, Tuple[str, float]],
    n_recovered: int,
    alignment_matrix: np.ndarray,
    config: ExperimentConfig
) -> Dict:
    """
    Evaluate SHOULD_WORK gate: n_recovered >= 3, mean_alignment > 0.70, uniqueness.
    Returns dict with gate_pass, n_recovered, mean_alignment, uniqueness.
    """
    ...

def verify_mechanism_activated(results: Dict) -> Tuple[bool, Dict]:
    """Check 5 activation indicators from PRD FR-5.3."""
    ...

def generate_figures(
    alignment_matrix: np.ndarray,
    assignments: Dict,
    cluster_profiles: Dict,
    baseline_assignments: Dict,
    n_recovered: int,
    config: ExperimentConfig
) -> List[str]:
    """
    Generate and save figures to config.figures_dir:
    1. gate_metrics_bar.png  (MANDATORY)
    2. alignment_heatmap.png
    3. radar_chart.png
    4. assignment_diagram.png
    5. descriptor_space.png
    Returns list of saved paths.
    """
    ...

def write_validation_report(results: Dict, config: ExperimentConfig) -> str:
    """Write 04_validation.md. Returns 'PASS' or 'FAIL'."""
    ...
```

---

### Main (`h-m3/code/main.py`)

**Dependencies**: config, data, model, evaluate

```python
import sys
import os
import numpy as np
from typing import Dict
from config import ExperimentConfig
from data import load_data, validate_cluster_profiles
from model import ArchetypeRecoveryMatcher, RandomBaselineMatcher
from evaluate import compute_gate_metrics, verify_mechanism_activated, generate_figures, write_validation_report

def run_experiment(config: ExperimentConfig) -> Dict: ...

if __name__ == "__main__":
    base_dir = "/home/anonymous/YouRA_results_new_4_sonnet45/TEST_mldpr_opus45/docs/youra_research/20260325_mldpr"
    config = ExperimentConfig(
        h_e1_cache_path=os.path.join(base_dir, "h-e1/code/hf_dataset_cache.json"),
        figures_dir=os.path.join(base_dir, "h-m3/figures"),
        output_path=os.path.join(base_dir, "h-m3/04_validation.md"),
    )
    results = run_experiment(config)
    sys.exit(0 if results["gate_pass"] else 1)
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ShapeDescriptorAnalyzer | `sys.path.insert` + `from model import ShapeDescriptorAnalyzer` | `h-m2/code/model.py` |
| h-e1 cache | direct file read (json) | `h-e1/code/hf_dataset_cache.json` |
| load_raw_series pattern | inline reimplementation (mirrors h-m2/data.py) | `h-m2/code/data.py` |
| perform_clustering pattern | inline reimplementation (mirrors h-m2/data.py) | `h-m2/code/data.py` |

**Verified from**: `h-m2/code/` and `h-e1/code/` actual files.

**CRITICAL NOTE**: h-e1 cache file is `hf_dataset_cache.json` (verified from `h-e1/code/data.py` line 41), NOT `dataset_cache.json` as stated in PRD FR-1.1. Trust actual code.

---

## Data Flow

- `main.py` calls `load_data(config)` -> returns `cluster_profiles: Dict[int, Dict[str, float]]`
- `ArchetypeRecoveryMatcher.build_alignment_matrix(cluster_profiles)` -> `(4, 5)` matrix
- `ArchetypeRecoveryMatcher.match_clusters(cluster_profiles)` -> `(assignments, n_recovered)`
- `RandomBaselineMatcher.match_clusters(cluster_profiles)` -> baseline `(assignments, n_recovered)`
- `compute_gate_metrics(...)` -> gate result dict
- `generate_figures(...)` -> saved PNG paths
- `write_validation_report(...)` -> `h-m3/04_validation.md`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create directory structure, config.py with dataclass, verify h-e1 cache path | 5 | 1+1+1+2 |
| A-2 | Data Loading | Implement data.py: load h-e1 cache, re-run DTW clustering (mirrors h-m2 pattern), compute shape descriptors via h-m2 ShapeDescriptorAnalyzer | 14 | 3+4+4+3 |
| A-3 | Archetype Definitions | Implement ARCHETYPE_PROFILES constant and normalization ranges in model.py | 5 | 2+1+1+1 |
| A-4 | ArchetypeRecoveryMatcher | Implement normalize_profile, compute_alignment (cosine), build_alignment_matrix, match_clusters | 12 | 3+2+4+3 |
| A-5 | RandomBaselineMatcher | Implement random assignment baseline (seed=42) and baseline alignment scoring | 6 | 1+1+2+2 |
| A-6 | Gate Metrics & Verification | compute_gate_metrics (n_recovered >= 3, mean_alignment, uniqueness), verify_mechanism_activated | 10 | 2+2+3+3 |
| A-7 | Figures - Gate Bar Chart | Mandatory: recovery target vs actual bar chart with pass/fail indicator | 8 | 2+1+3+2 |
| A-8 | Figures - Additional | alignment_heatmap, radar_chart, assignment_diagram, descriptor_space (4 figures) | 12 | 2+2+4+4 |
| A-9 | Validation Report | write_validation_report generating 04_validation.md with all metrics and gate verdict | 8 | 2+2+2+2 |
| A-10 | Main Orchestration | run_experiment pipeline, absolute path config, sys.exit gate result | 7 | 2+2+1+2 |
| A-11 | Integration Test | End-to-end run, verify alignment_matrix shape (4,5), n_recovered >= 0, figures saved | 10 | 2+3+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2], Medium(9-13): [A-4, A-6, A-8, A-11], Low(4-8): [A-1, A-3, A-5, A-7, A-9, A-10]
