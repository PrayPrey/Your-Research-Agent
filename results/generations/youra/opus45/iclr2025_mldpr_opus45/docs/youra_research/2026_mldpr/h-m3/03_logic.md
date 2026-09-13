# Logic: h-m3 Archetype Recovery via Shape Descriptor Alignment

**Applied**: standard-dl-experiment-module-pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Serena project activation failed (no active project); API signatures verified via direct file reads from actual h-m2/h-e1 code
**Analyzed Path**: `docs/youra_research/20260325_mldpr/h-m2/code/` and `docs/youra_research/20260325_mldpr/h-e1/code/`
**Relevant Symbols**:
- `ShapeDescriptorAnalyzer.compute_descriptors(centroid: np.ndarray) -> Dict[str, float]`
- `ShapeDescriptorAnalyzer.compute_descriptor_matrix(centroids: np.ndarray) -> Tuple[np.ndarray, List[str]]`
- `load_raw_series(config) -> List[np.ndarray]`
- `preprocess_series(raw_series) -> np.ndarray`  # returns [N, T, 1]
- `perform_clustering(X, config) -> Tuple[np.ndarray, np.ndarray]`  # centroids (k,T), labels (N,)
- `load_series_and_clusters(config) -> Tuple[List, np.ndarray, np.ndarray]`  # (all_series, labels, centroids)

---

## External Dependencies API

### API Signatures (From Actual h-m2 Code)

```python
# From: h-m2/code/model.py (ACTUAL CODE)
class ShapeDescriptorAnalyzer:
    def __init__(self, config: ExperimentConfig) -> None: ...

    def compute_descriptors(self, centroid: np.ndarray) -> Dict[str, float]:
        """centroid: (T,) -> {growth_ratio, peak_timing, changepoint_count, derivative_variance}"""

    def compute_descriptor_matrix(
        self, centroids: np.ndarray
    ) -> Tuple[np.ndarray, List[str]]:
        """centroids: (k, T) -> (descriptor_matrix (k,4), descriptor_names List[str])"""

# From: h-m2/code/data.py (ACTUAL CODE)
def load_raw_series(config: ExperimentConfig) -> List[np.ndarray]:
    """Loads from config.h_e1_cache_path (resolved relative to __file__)"""

def preprocess_series(raw_series: List[np.ndarray]) -> np.ndarray:
    """Returns X: [N, T, 1] tslearn format"""

def perform_clustering(X: np.ndarray, config: ExperimentConfig) -> Tuple[np.ndarray, np.ndarray]:
    """Returns (centroids (k,T), labels (N,))"""

def load_series_and_clusters(config: ExperimentConfig) -> Tuple[List[np.ndarray], np.ndarray, np.ndarray]:
    """Returns (all_series, cluster_labels (N,), centroids (k,T))"""
```

**CRITICAL NOTE**: h-e1 cache file is `hf_dataset_cache.json` (verified from h-m2/code/data.py line 22), NOT `dataset_cache.json` as stated in PRD FR-1.1.

**Verified from**: `h-m2/code/model.py` and `h-m2/code/data.py` actual implementations.

---

## A-1: Project Setup [Complexity: 5, Budget: 1]

**Applied**: Standard PyTorch dataclass config pattern

### API Signatures

```python
# config.py
from dataclasses import dataclass, field
from typing import Dict, Tuple

@dataclass
class ExperimentConfig:
    """Experiment configuration for h-m3 archetype recovery."""
    n_clusters: int = 4
    n_archetypes: int = 5
    random_state: int = 42
    alignment_threshold: float = 0.70
    min_archetypes_recovered: int = 3
    # Normalization ranges from h-m2 observed values
    norm_ranges: Dict[str, Tuple[float, float]] = field(default_factory=lambda: {
        "growth_ratio": (0.3, 0.6),
        "peak_timing": (0.0, 0.03),
        "changepoint_count": (0.0, 5.0),
        "derivative_variance": (0.1, 0.4),
    })
    # Paths (overridden in __main__ with absolute paths)
    h_e1_cache_path: str = "../h-e1/code/hf_dataset_cache.json"
    figures_dir: str = "h-m3/figures"
    output_path: str = "h-m3/04_validation.md"
    # h-m2 config params (needed to instantiate ShapeDescriptorAnalyzer)
    min_prominence: float = 0.1
    pelt_model: str = "rbf"
    pelt_min_size: int = 3
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Config dataclass | ExperimentConfig with all fields and norm_ranges default_factory |

---

## A-2: Data Loading [Complexity: 14, Budget: 1]

**Applied**: Standard PyTorch dataclass config pattern

### API Signatures

```python
# data.py
import sys, os, json
import numpy as np
from typing import Dict, List, Tuple
from config import ExperimentConfig

def load_cluster_centroids(config: ExperimentConfig) -> Tuple[np.ndarray, np.ndarray]:
    """Load h-e1 cache, preprocess, DTW cluster. Returns (centroids (k,T), labels (N,))."""
    ...

def compute_shape_descriptors(
    centroids: np.ndarray,
    config: ExperimentConfig
) -> Dict[int, Dict[str, float]]:
    """Use h-m2 ShapeDescriptorAnalyzer. Returns {cluster_id: {descriptor: value}}."""
    ...

def load_data(config: ExperimentConfig) -> Dict[int, Dict[str, float]]:
    """Top-level: centroids -> descriptors -> cluster_profiles dict."""
    ...

def validate_cluster_profiles(
    cluster_profiles: Dict[int, Dict[str, float]],
    config: ExperimentConfig
) -> Tuple[bool, dict]:
    """Validate k=4 clusters with 4 descriptors each."""
    ...
```

### Pseudo-code (data loading pipeline)

```
load_cluster_centroids(config):
    sys.path.insert(0, h_m2_code_dir)
    import h_m2 data functions
    raw_series = load_raw_series(config)     # List[np.ndarray]
    X = preprocess_series(raw_series)        # [N, T, 1]
    centroids, labels = perform_clustering(X, config)  # (k,T), (N,)
    return centroids, labels

compute_shape_descriptors(centroids, config):
    analyzer = ShapeDescriptorAnalyzer(config)
    profiles = {}
    for i in range(k):
        profiles[i] = analyzer.compute_descriptors(centroids[i])  # Dict[str, float]
    return profiles
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Data pipeline | load_cluster_centroids + compute_shape_descriptors via h-m2 ShapeDescriptorAnalyzer |

---

## A-3 & A-4: Archetype Definitions + ArchetypeRecoveryMatcher [Complexity: 17, Budget: 2]

**Applied**: Standard PyTorch dataclass config pattern

### API Signatures

```python
# model.py
import numpy as np
from scipy.spatial.distance import cosine
from typing import Dict, List, Tuple
from config import ExperimentConfig

ARCHETYPE_PROFILES: Dict[str, Dict[str, float]] = {
    "sustained_growth": {"growth_ratio": 0.8, "peak_timing": 0.9, "changepoint_count": 0.2, "derivative_variance": 0.2},
    "flash_in_pan":     {"growth_ratio": 0.3, "peak_timing": 0.2, "changepoint_count": 0.8, "derivative_variance": 0.8},
    "plateau":          {"growth_ratio": 0.5, "peak_timing": 0.5, "changepoint_count": 0.2, "derivative_variance": 0.1},
    "slow_burn":        {"growth_ratio": 0.7, "peak_timing": 0.8, "changepoint_count": 0.1, "derivative_variance": 0.2},
    "revival":          {"growth_ratio": 0.4, "peak_timing": 0.6, "changepoint_count": 0.6, "derivative_variance": 0.5},
}

DESCRIPTOR_ORDER: List[str] = ["growth_ratio", "peak_timing", "changepoint_count", "derivative_variance"]


class ArchetypeRecoveryMatcher:
    """Map k=4 cluster profiles to 5 archetypes via cosine similarity."""

    def __init__(self, config: ExperimentConfig) -> None:
        self.config = config
        self.archetypes = ARCHETYPE_PROFILES
        self.threshold = config.alignment_threshold

    def normalize_profile(self, profile: Dict[str, float]) -> Dict[str, float]:
        """Min-max normalize using config.norm_ranges. Returns clipped [0,1] values."""
        ...  # profile: {descriptor: raw_value} -> {descriptor: [0,1]}

    def compute_alignment(
        self, cluster_profile: Dict[str, float], archetype_name: str
    ) -> float:
        """Cosine similarity (1 - cosine distance). Returns float in [0, 1]."""
        ...  # -> scalar alignment score

    def build_alignment_matrix(
        self, cluster_profiles: Dict[int, Dict[str, float]]
    ) -> np.ndarray:
        """Returns alignment_matrix: (k, n_archetypes) = (4, 5)."""
        ...

    def match_clusters(
        self, cluster_profiles: Dict[int, Dict[str, float]]
    ) -> Tuple[Dict[int, Tuple[str, float]], int]:
        """
        Greedy best-match above threshold. Returns (assignments, n_recovered).
        assignments: {cluster_id: (archetype_name, score)}
        n_recovered: distinct archetypes matched
        """
        ...


class RandomBaselineMatcher:
    """Random archetype assignment baseline (seed=42)."""

    def __init__(self, config: ExperimentConfig) -> None:
        self.config = config
        self.archetypes = ARCHETYPE_PROFILES

    def match_clusters(
        self, cluster_profiles: Dict[int, Dict[str, float]]
    ) -> Tuple[Dict[int, Tuple[str, float]], int]:
        """Random assignment without replacement. seed=42."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| cluster_vec | (4,) | normalized descriptor vector |
| archetype_vec | (4,) | archetype profile vector |
| alignment_matrix | (4, 5) | cosine similarity scores |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | ArchetypeRecoveryMatcher | normalize_profile, compute_alignment, build_alignment_matrix, match_clusters |
| L-4-2 | RandomBaselineMatcher | random assignment baseline seed=42 |

---

## A-5 & A-6: Gate Metrics + Verification [Complexity: 16, Budget: 1]

**Applied**: Standard PyTorch dataclass config pattern

### API Signatures

```python
# evaluate.py
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
from config import ExperimentConfig

def compute_gate_metrics(
    assignments: Dict[int, Tuple[str, float]],
    n_recovered: int,
    alignment_matrix: np.ndarray,  # (4, 5)
    config: ExperimentConfig
) -> Dict:
    """
    SHOULD_WORK gate: n_recovered >= 3, mean_alignment > 0.70, uniqueness.
    Returns: {gate_pass, n_recovered, mean_alignment, uniqueness, alignment_matrix, n_archetypes, n_clusters, alignment_threshold}
    """
    ...

def verify_mechanism_activated(results: Dict) -> Tuple[bool, Dict]:
    """Check 5 activation indicators per PRD FR-5.3."""
    ...

def generate_figures(
    alignment_matrix: np.ndarray,       # (4, 5)
    assignments: Dict,
    cluster_profiles: Dict,
    baseline_assignments: Dict,
    n_recovered: int,
    config: ExperimentConfig
) -> List[str]:
    """
    Save to config.figures_dir:
    1. gate_metrics_bar.png  (MANDATORY)
    2. alignment_heatmap.png
    3. radar_chart.png
    4. assignment_diagram.png
    5. descriptor_space.png
    Returns list of saved absolute paths.
    """
    ...

def write_validation_report(results: Dict, config: ExperimentConfig) -> str:
    """Write 04_validation.md. Returns 'PASS' or 'FAIL'."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Gate metrics + figures + report | compute_gate_metrics, verify_mechanism_activated, generate_figures, write_validation_report |

---

## A-7 (Main Orchestration) [Complexity: 7, Budget: 1]

**Applied**: Standard PyTorch dataclass config pattern

### API Signatures

```python
# main.py
import sys, os
import numpy as np
from config import ExperimentConfig
from data import load_data, validate_cluster_profiles
from model import ArchetypeRecoveryMatcher, RandomBaselineMatcher
from evaluate import compute_gate_metrics, verify_mechanism_activated, generate_figures, write_validation_report
from typing import Dict

def run_experiment(config: ExperimentConfig) -> Dict:
    """Full pipeline. Returns results dict with gate_pass key."""
    ...

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

### Pseudo-code (run_experiment)

```
run_experiment(config):
    cluster_profiles = load_data(config)           # {cluster_id: {desc: val}}
    valid, report = validate_cluster_profiles(cluster_profiles, config)

    matcher = ArchetypeRecoveryMatcher(config)
    alignment_matrix = matcher.build_alignment_matrix(cluster_profiles)  # (4,5)
    assignments, n_recovered = matcher.match_clusters(cluster_profiles)

    baseline = RandomBaselineMatcher(config)
    baseline_assignments, _ = baseline.match_clusters(cluster_profiles)

    results = compute_gate_metrics(assignments, n_recovered, alignment_matrix, config)
    activated, indicators = verify_mechanism_activated(results)
    figure_paths = generate_figures(alignment_matrix, assignments, cluster_profiles,
                                    baseline_assignments, n_recovered, config)
    gate_str = write_validation_report(results, config)
    results["gate_pass"] = results["gate_pass"] and activated
    return results
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Main orchestration | run_experiment pipeline with absolute path config |
