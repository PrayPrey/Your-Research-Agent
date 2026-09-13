# Logic: H-M3 Method Disagreement Analysis

**Date:** 2026-03-26
**Hypothesis:** H-M3 (MECHANISM, INCREMENTAL)
**Gate:** SHOULD_WORK
**Prerequisites:** H-M2 (VALIDATED), H-E1 (VALIDATED)

Applied: mechanism-verification-incremental
Applied: incremental-reuse pattern (H-E1 attribution infrastructure)
Applied: top-k Jaccard gate pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-E1)
**Status**: API signatures verified from actual code via direct file reads (Serena MCP requires project activation)
**Analyzed Path**: `docs/youra_research/20260323_data_problems/h-e1/code/`
**Relevant Symbols**:
- `AttributionMethod.compute_scores(model, train_loader, test_loader, budget, seed, cfg, device)` -> `np.ndarray [n_train, n_test]`
- `ExperimentConfig` dataclass: `data_root`, `train_subset_size`, `loo_test_size`, `subset_seed`, `train_batch_size`, `test_batch_size`
- `get_cifar10_loaders(cfg: ExperimentConfig)` -> `Tuple[DataLoader, DataLoader, DataLoader]`
- `get_subset_indices(cfg: ExperimentConfig)` -> `np.ndarray`
- `get_loo_test_indices(cfg: ExperimentConfig)` -> `np.ndarray`
- `TRAKMethod, TracInMethod, IFMethod, FastIFMethod` - concrete subclasses of `AttributionMethod`
- `BUDGET_MAP: Dict[str, Dict[int, Any]]` - maps method name + budget -> params

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: h-e1/code/attribution.py (ACTUAL CODE)
class AttributionMethod(ABC):
    def compute_scores(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        test_loader: DataLoader,
        budget: int,
        seed: int,
        cfg: ExperimentConfig,   # h-e1 ExperimentConfig, NOT H3Config
        device: str = 'cuda',
    ) -> np.ndarray:
        """Returns [n_train, n_test]."""  # MUST transpose for h-m3

# Concrete classes (all share same signature):
# TRAKMethod, TracInMethod, IFMethod, FastIFMethod

# From: h-e1/code/data.py (ACTUAL CODE)
def get_cifar10_loaders(cfg: ExperimentConfig) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """Returns (train_subset_loader, loo_test_loader, full_test_loader)."""

def get_subset_indices(cfg: ExperimentConfig) -> np.ndarray: ...
def get_loo_test_indices(cfg: ExperimentConfig) -> np.ndarray: ...

# From: h-e1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    data_root: str = './data'
    train_subset_size: int = 5000
    loo_test_size: int = 100
    subset_seed: int = 42
    train_batch_size: int = 128
    test_batch_size: int = 256
    results_dir: str = './results'
    figures_dir: str = './figures'
    checkpoint_dir: str = './checkpoints'
```

**Verified from**: `h-e1/code/attribution.py`, `h-e1/code/data.py`, `h-e1/code/config.py` (actual code).
**Critical**: `compute_scores` returns `[n_train, n_test]` — must transpose to `[n_test, n_train]` in `load_or_compute_scores`.

---

## A-1: Setup & Config [Complexity: 6, Budget: 1/10]

**Applied**: Standard dataclass config

### API Signatures

```python
# config.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class H3Config:
    # Data (matching H-E1 exactly)
    data_root: str = './data'
    train_subset_size: int = 5000
    loo_test_size: int = 100
    subset_seed: int = 42
    train_batch_size: int = 128
    test_batch_size: int = 256

    # Attribution
    methods: List[str] = field(default_factory=lambda: ['TRAK', 'TracIn', 'IF', 'FastIF'])
    compute_budgets: List[int] = field(default_factory=lambda: [10, 25, 50, 75, 100])
    method_seeds: List[int] = field(default_factory=lambda: [0, 1, 2])

    # Jaccard gate
    top_k: int = 50
    jaccard_threshold: float = 0.70  # gate: min(Jaccard) < this
    persistence_threshold: float = 0.60  # persistent if leads >60% of budgets

    # Paths
    base_code_dir: str = '../h-e1/code'
    checkpoint_path: str = '../h-e1/code/checkpoints/model_seed0_final.pt'
    results_dir: str = './results'
    figures_dir: str = './figures'


def get_config() -> H3Config:
    """Return default H3Config, creating output dirs."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | config.py | H3Config dataclass + get_config() with mkdir |

---

## A-2: Data & Model Loading [Complexity: 7, Budget: 1/10]

**Applied**: Standard checkpoint load + H-E1 delegation

### API Signatures

```python
# run_experiment.py (loading section)
import sys, torch, torch.nn as nn
from torch.utils.data import DataLoader

def load_model(cfg: H3Config, device: str) -> nn.Module:
    """Load ResNet-18 from h-e1 checkpoint. Returns eval-mode model."""
    # model: [B, 3, 32, 32] -> [B, 10]

def load_data(cfg: H3Config) -> Tuple[DataLoader, DataLoader]:
    """
    Wire H3Config -> ExperimentConfig, call h-e1 get_cifar10_loaders.
    Returns (train_loader, test_loader) - drops full_test_loader.
    train_loader: 5000 samples, test_loader: 100 samples.
    """
```

### Pseudo-code

```
load_model:
  sys.path.insert(0, cfg.base_code_dir)
  from model import build_model
  model = build_model(device)
  model.load_state_dict(torch.load(cfg.checkpoint_path, map_location=device))
  model.eval(); return model

load_data:
  sys.path.insert(0, cfg.base_code_dir)
  from data import get_cifar10_loaders
  from config import ExperimentConfig
  he1_cfg = ExperimentConfig(
      data_root=cfg.data_root,
      train_subset_size=cfg.train_subset_size,
      loo_test_size=cfg.loo_test_size,
      subset_seed=cfg.subset_seed,
      train_batch_size=cfg.train_batch_size,
      test_batch_size=cfg.test_batch_size,
  )
  train_loader, test_loader, _ = get_cifar10_loaders(he1_cfg)
  return train_loader, test_loader
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | loading funcs | load_model, load_data with ExperimentConfig bridge |

---

## A-3: Attribution Score Computation [Complexity: 14, Budget: 2/10]

**Applied**: Standard attribution loop + npz cache

### API Signatures

```python
# run_experiment.py
def load_or_compute_scores(
    cfg: H3Config,
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    device: str,
) -> Dict[int, Dict[str, np.ndarray]]:
    """
    Returns: {budget: {method: scores}}
    Each scores array: [n_test=100, n_train=5000]  # transposed from H-E1
    Loads cached npz if exists at cfg.results_dir/attribution_scores.npz,
    else computes via H-E1 attribution classes (averaged over seeds).
    Cache keys: '{method}_{budget}_{seed}'
    """
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| raw scores (H-E1) | [5000, 100] | returned by compute_scores |
| scores (h-m3) | [100, 5000] | transposed, used for top-k |
| per budget dict | 4 methods x 3 seeds | 20 arrays per budget |

### Pseudo-code

```
load_or_compute_scores:
  cache_path = f"{cfg.results_dir}/attribution_scores.npz"
  if os.path.exists(cache_path):
    data = np.load(cache_path)
    return reconstruct dict from data

  sys.path.insert(0, cfg.base_code_dir)
  from attribution import TRAKMethod, TracInMethod, IFMethod, FastIFMethod
  from config import ExperimentConfig
  he1_cfg = ExperimentConfig(...)

  method_map = {'TRAK': TRAKMethod(), 'TracIn': TracInMethod(),
                'IF': IFMethod(), 'FastIF': FastIFMethod()}
  results = {}
  for budget in cfg.compute_budgets:
      results[budget] = {}
      for method_name in cfg.methods:
          seed_arrays = []
          for seed in cfg.method_seeds:
              raw = method_map[method_name].compute_scores(
                  model, train_loader, test_loader,
                  budget=budget, seed=seed, cfg=he1_cfg, device=device
              )  # [5000, 100]
              seed_arrays.append(raw.T)  # transpose -> [100, 5000]
          results[budget][method_name] = np.mean(seed_arrays, axis=0)  # [100, 5000]

  save_scores_npz(results, cache_path)
  return results
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | attribution loop | method factory + compute loop with transpose |
| L-3-2 | npz cache | save/load attribution_scores.npz with keyed arrays |

---

## A-4: Jaccard Analyzer [Complexity: 10, Budget: 2/10]

**Applied**: Set-intersection Jaccard pattern

### API Signatures

```python
# jaccard.py
from typing import Dict, List, Set, Tuple, Any
import numpy as np

class JaccardAnalyzer:
    def __init__(self, cfg: H3Config): ...

    def get_topk_indices(self, scores: np.ndarray, k: int = 50) -> List[Set[int]]:
        """scores: [n_test, n_train] -> list[set] of length n_test."""

    def compute_pairwise_jaccard(
        self,
        scores_dict: Dict[str, np.ndarray],  # {method: [n_test, n_train]}
        k: int = 50,
    ) -> Tuple[np.ndarray, float]:
        """
        Returns:
          jaccard_matrix: [n_methods, n_methods] mean Jaccard per test sample
          min_jaccard: float  (off-diagonal min, gate metric)
        """

    def compute_jaccard_by_budget(
        self,
        results_dict: Dict[int, Dict[str, np.ndarray]],
        budgets: List[int],
        k: int = 50,
    ) -> Dict[int, Dict[str, Any]]:
        """Returns {budget: {'matrix': ndarray[n_m,n_m], 'min': float, 'mean': float}}"""

    def check_gate(self, min_jaccard: float) -> bool:
        """True if min_jaccard < cfg.jaccard_threshold (0.70)."""
```

### Pseudo-code (get_topk_indices)

```
for each test sample i:
  topk_idx = argsort(-scores[i])[:k]
  sets.append(set(topk_idx))
return sets

compute_pairwise_jaccard:
  topk_sets = {m: get_topk_indices(scores_dict[m], k) for m in methods}
  for i, m1 in enumerate(methods):
    for j, m2 in enumerate(methods):
      per_test = [|A&B| / |A|B| for A,B in zip(topk_sets[m1], topk_sets[m2])]
      matrix[i,j] = mean(per_test)
  min_jaccard = matrix[~eye_mask].min()
  return matrix, min_jaccard
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | get_topk_indices | argsort-based top-k set extraction |
| L-4-2 | compute_pairwise_jaccard + compute_jaccard_by_budget | pairwise loop + budget sweep |

---

## A-5: Gate Evaluation [Complexity: 7, Budget: 1/10]

**Applied**: Standard evaluation pattern

### API Signatures

```python
# run_experiment.py
def evaluate_gate(
    jaccard_by_budget: Dict[int, Dict[str, Any]],
    cfg: H3Config,
) -> Dict[str, Any]:
    """
    Returns:
      {'gate_pass': bool, 'min_jaccard': float, 'min_budget': int,
       'per_budget_min': Dict[int, float], 'details': str}
    Gate passes if any budget has min(Jaccard) < cfg.jaccard_threshold.
    """
```

### Pseudo-code

```
per_budget_min = {b: jaccard_by_budget[b]['min'] for b in budgets}
overall_min = min(per_budget_min.values())
min_budget = argmin budget
gate_pass = overall_min < cfg.jaccard_threshold
return result dict
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | evaluate_gate | min across budgets, threshold check, result dict |

---

## A-6: Persistence Analysis [Complexity: 9, Budget: 1/10]

**Applied**: Standard ranking persistence pattern

### API Signatures

```python
# persistence.py
class PersistenceAnalyzer:
    def __init__(self, cfg: H3Config): ...

    def compute_relative_advantages(
        self,
        metrics_by_budget: Dict[int, Dict[str, Dict[str, float]]],
        # {budget: {method: {'rho_r': float, 'rho_m': float}}}
    ) -> Dict[int, Dict[str, str]]:
        """Returns {budget: {'best_rho_r': method, 'best_rho_m': method}}"""

    def check_persistence(
        self,
        advantages: Dict[int, Dict[str, str]],
    ) -> Dict[str, Dict[str, bool]]:
        """
        Returns {metric: {method: is_persistent}}
        persistent = method leads in >cfg.persistence_threshold (60%) of budgets.
        """

    def save_results(
        self,
        advantages: Dict[int, Dict[str, str]],
        persistence: Dict[str, Dict[str, bool]],
    ) -> None:
        """Saves cfg.results_dir/metric_advantages.csv"""
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | PersistenceAnalyzer | relative advantage tracking + 60% persistence check |

---

## A-7 & A-8: Visualization [Complexity: 18, Budget: 1/10]

**Applied**: Standard matplotlib/seaborn plotting

### API Signatures

```python
# visualize.py
class Visualizer:
    def __init__(self, cfg: H3Config): ...

    def plot_jaccard_heatmap(
        self,
        jaccard_matrix: np.ndarray,  # [n_methods, n_methods]
        method_names: List[str],
        budget: int,
        save_path: str,
    ) -> None:
        """Gate figure: pairwise Jaccard heatmap with 0.70 line annotation."""

    def plot_jaccard_by_budget(
        self,
        jaccard_by_budget: Dict[int, Dict],
        budgets: List[int],
        save_path: str,
    ) -> None:
        """Line plot min/mean Jaccard vs budget with 0.70 threshold line."""

    def plot_topk_overlap(
        self,
        topk_sets: Dict[str, List[Set[int]]],
        test_sample_indices: List[int],
        save_path: str,
    ) -> None:
        """Bar chart overlap counts for 2-3 representative test samples."""

    def plot_method_ranking_persistence(
        self,
        advantages: Dict[int, Dict[str, str]],
        budgets: List[int],
        save_path: str,
    ) -> None:
        """Stacked bar: which method leads each metric per budget."""

    def plot_paradigm_clustering(
        self,
        jaccard_matrix: np.ndarray,  # [n_methods, n_methods]
        method_names: List[str],
        save_path: str,
    ) -> None:
        """Dendrogram based on Jaccard distance (1 - Jaccard)."""
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | all figures | jaccard_heatmap (gate) + 4 supplementary figures |

---

## A-9: Results Serialization [Complexity: 6, Budget: 0/10]

Merged into L-3-2 (npz) and L-6-1 (CSV). No separate subtask needed.

---

## A-10: Experiment Orchestrator [Complexity: 9, Budget: 1/10]

**Applied**: Standard main() pipeline pattern

### API Signatures

```python
# run_experiment.py
def run(cfg: H3Config) -> Dict[str, Any]:
    """Main orchestrator. Returns gate result dict."""

if __name__ == '__main__':
    cfg = get_config()
    results = run(cfg)
    print(f"Gate: min(Jaccard)={results['min_jaccard']:.3f}, PASS={results['gate_pass']}")
```

### Pseudo-code

```
run(cfg):
  device = 'cuda' if torch.cuda.is_available() else 'cpu'
  os.makedirs(cfg.results_dir, exist_ok=True)
  os.makedirs(cfg.figures_dir, exist_ok=True)

  model = load_model(cfg, device)
  train_loader, test_loader = load_data(cfg)

  scores = load_or_compute_scores(cfg, model, train_loader, test_loader, device)
  # scores: {budget: {method: [100, 5000]}}

  analyzer = JaccardAnalyzer(cfg)
  jaccard_by_budget = analyzer.compute_jaccard_by_budget(scores, cfg.compute_budgets)
  # save jaccard_analysis.csv

  gate = evaluate_gate(jaccard_by_budget, cfg)

  # Optional: load LOO metrics for persistence (from h-e1 results or h-m2 metrics_df)
  # If available, run PersistenceAnalyzer
  # If not available, skip persistence (gate is primary)

  viz = Visualizer(cfg)
  best_budget = gate['min_budget']
  viz.plot_jaccard_heatmap(
      jaccard_by_budget[best_budget]['matrix'],
      cfg.methods,
      best_budget,
      f"{cfg.figures_dir}/jaccard_heatmap.png"
  )
  viz.plot_jaccard_by_budget(jaccard_by_budget, cfg.compute_budgets,
      f"{cfg.figures_dir}/jaccard_by_budget.png")
  # ... other figures

  return gate
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-10-1 | run() orchestrator | full pipeline, gate print, optional persistence |

---

## Subtask Budget Summary

| Task | Subtask IDs | Budget Used |
|------|-------------|-------------|
| A-1 Setup & Config | L-1-1 | 1 |
| A-2 Data & Model | L-2-1 | 1 |
| A-3 Attribution | L-3-1, L-3-2 | 2 |
| A-4 Jaccard Analyzer | L-4-1, L-4-2 | 2 |
| A-5 Gate Evaluation | L-5-1 | 1 |
| A-6 Persistence | L-6-1 | 1 |
| A-7/A-8 Visualization | L-7-1 | 1 |
| A-10 Orchestrator | L-10-1 | 1 |

**Total: 10/10 subtasks used**

---

## Key Data Flow

```
H3Config
  -> load_model()               -> nn.Module (ResNet-18, eval)
  -> load_data()                -> (DataLoader[5000], DataLoader[100])

(model, loaders) -> load_or_compute_scores()
  -> {budget: {method: np.ndarray[100, 5000]}}  # 5 budgets x 4 methods

scores -> JaccardAnalyzer.compute_jaccard_by_budget()
  -> {budget: {'matrix': [4,4], 'min': float, 'mean': float}}

jaccard_by_budget -> evaluate_gate()
  -> {'gate_pass': bool, 'min_jaccard': float, ...}

jaccard_by_budget -> Visualizer -> figures/*.png
```

---

## Key Interface Notes

- `compute_scores` returns `[n_train, n_test]` -> transpose `.T` -> `[n_test, n_train]` immediately
- Import H-E1 via `sys.path.insert(0, cfg.base_code_dir)` before all H-E1 imports
- NPZ cache keys: `f"{method}_{budget}_{seed}"` (raw per-seed), averaged at load time
- Gate: `any(budget['min'] < 0.70 for budget in jaccard_by_budget.values())`
- Persistence analysis requires LOO correlation metrics (rho_r, rho_m); optional if not cached
