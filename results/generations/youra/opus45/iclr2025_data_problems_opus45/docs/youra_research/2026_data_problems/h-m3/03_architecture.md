# Architecture: H-M3 Method Disagreement Analysis

**Hypothesis**: Methods with different design paradigms show persistent relative advantages on different metrics, with top-k Jaccard < 0.70.
**Type**: MECHANISM (INCREMENTAL)
**Base Code**: `h-e1/code/`

Applied: Incremental reuse pattern - extend base hypothesis infrastructure
Applied: Layered analysis pattern - compute scores, then analyze agreement

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Serena MCP unavailable (no active project); analyzed via direct file reads
**Analyzed Path**: `docs/youra_research/20260323_data_problems/h-e1/code/`
**Findings**: H-E1 has `attribution.py` with `AttributionMethod` ABC + 4 concrete classes (TRAKMethod, TracInMethod, IFMethod, FastIFMethod); `data.py` with subset loading; `config.py` with `ExperimentConfig`. Attribution methods return `[n_train, n_test]` — must transpose for h-m3 usage.

---

## File Organization

- `h-m3/code/config.py` - experiment config
- `h-m3/code/jaccard.py` - top-k Jaccard computation (gate metric)
- `h-m3/code/persistence.py` - relative advantage tracking
- `h-m3/code/visualize.py` - 4+ visualization figures
- `h-m3/code/run_experiment.py` - main orchestrator

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| AttributionMethod | `from attribution import AttributionMethod` | `h-e1/code/attribution.py` |
| TRAKMethod | `from attribution import TRAKMethod` | `h-e1/code/attribution.py` |
| TracInMethod | `from attribution import TracInMethod` | `h-e1/code/attribution.py` |
| IFMethod | `from attribution import IFMethod` | `h-e1/code/attribution.py` |
| FastIFMethod | `from attribution import FastIFMethod` | `h-e1/code/attribution.py` |
| get_transform | `from data import get_transform` | `h-e1/code/data.py` |
| get_subset_indices | `from data import get_subset_indices` | `h-e1/code/data.py` |
| get_loo_test_indices | `from data import get_loo_test_indices` | `h-e1/code/data.py` |
| ExperimentConfig | `from config import ExperimentConfig` | `h-e1/code/config.py` |

**Verified from**: `h-e1/code/` (actual implementation)
**Note**: `compute_scores` returns `[n_train, n_test]`; transpose to `[n_test, n_train]` before Jaccard.

---

## Modules

### H3Config (`config.py`)

**Dependencies**: none

```python
@dataclass
class H3Config:
    # Data (matching H-E1)
    data_root: str = './data'
    train_subset_size: int = 5000
    loo_test_size: int = 100
    subset_seed: int = 42

    # Attribution
    methods: List[str] = field(default_factory=lambda: ['TRAK', 'TracIn', 'IF', 'FastIF'])
    compute_budgets: List[int] = field(default_factory=lambda: [10, 25, 50, 75, 100])
    method_seeds: List[int] = field(default_factory=lambda: [0, 1, 2])

    # Jaccard Analysis
    top_k: int = 50
    jaccard_threshold: float = 0.70

    # Paths
    base_code_dir: str = '../h-e1/code'
    checkpoint_path: str = '../h-e1/code/checkpoints/model_seed0_final.pt'
    results_dir: str = './results'
    figures_dir: str = './figures'

def get_config() -> H3Config: ...
```

---

### JaccardAnalyzer (`jaccard.py`)

**Dependencies**: H3Config, numpy

```python
class JaccardAnalyzer:
    def __init__(self, cfg: H3Config): ...

    def get_topk_indices(self, scores: np.ndarray, k: int = 50) -> List[Set[int]]:
        """scores: (n_test, n_train) -> list of sets, one per test sample"""
        ...

    def compute_pairwise_jaccard(
        self,
        attribution_scores_dict: Dict[str, np.ndarray],
        k: int = 50
    ) -> Tuple[np.ndarray, float]:
        """
        Returns:
            jaccard_matrix: (n_methods, n_methods) float
            min_jaccard: float (gate metric, must be < 0.70)
        """
        ...

    def compute_jaccard_by_budget(
        self,
        results_dict: Dict[int, Dict[str, np.ndarray]],
        budgets: List[int],
        k: int = 50
    ) -> Dict[int, Dict[str, Any]]:
        """Returns {budget: {'matrix': ndarray, 'min': float, 'mean': float}}"""
        ...

    def check_gate(self, min_jaccard: float) -> bool:
        """Returns True if min_jaccard < cfg.jaccard_threshold"""
        ...
```

---

### PersistenceAnalyzer (`persistence.py`)

**Dependencies**: H3Config, numpy

```python
class PersistenceAnalyzer:
    def __init__(self, cfg: H3Config): ...

    def compute_relative_advantages(
        self,
        metrics_by_budget: Dict[int, Dict[str, Dict[str, float]]]
    ) -> Dict[int, Dict[str, str]]:
        """
        Args: metrics_by_budget: {budget: {method: {'rho_r': float, 'rho_m': float}}}
        Returns: {budget: {'best_rho_r': method, 'best_rho_m': method}}
        """
        ...

    def check_persistence(
        self,
        advantages: Dict[int, Dict[str, str]],
        threshold: float = 0.60
    ) -> Dict[str, bool]:
        """Returns {method: is_persistent} where persistent = leads >60% of budgets"""
        ...

    def save_results(self, advantages: dict, persistence: dict) -> None:
        """Saves to cfg.results_dir/metric_advantages.csv"""
        ...
```

---

### Visualizer (`visualize.py`)

**Dependencies**: H3Config, matplotlib, seaborn, numpy

```python
class Visualizer:
    def __init__(self, cfg: H3Config): ...

    def plot_jaccard_heatmap(
        self,
        jaccard_matrix: np.ndarray,
        method_names: List[str],
        budget: int,
        save_path: str
    ) -> None:
        """Gate figure: pairwise Jaccard heatmap with 0.70 threshold annotation"""
        ...

    def plot_jaccard_by_budget(
        self,
        jaccard_by_budget: Dict[int, Dict],
        budgets: List[int],
        save_path: str
    ) -> None:
        """Line plot: min/mean Jaccard vs budget with 0.70 threshold"""
        ...

    def plot_topk_overlap(
        self,
        topk_sets: Dict[str, List[Set[int]]],
        test_indices: List[int],
        save_path: str
    ) -> None:
        """Venn/UpSet diagram for 2-3 representative test samples"""
        ...

    def plot_method_ranking_persistence(
        self,
        advantages: Dict[int, Dict[str, str]],
        budgets: List[int],
        save_path: str
    ) -> None:
        """Stacked bar showing method rank persistence across budgets"""
        ...

    def plot_paradigm_clustering(
        self,
        jaccard_matrix: np.ndarray,
        method_names: List[str],
        save_path: str
    ) -> None:
        """Dendrogram/MDS based on Jaccard distance between methods"""
        ...
```

---

### ExperimentRunner (`run_experiment.py`)

**Dependencies**: H3Config, JaccardAnalyzer, PersistenceAnalyzer, Visualizer, H-E1 attribution/data modules

```python
def load_model(cfg: H3Config, device: str) -> nn.Module:
    """Load ResNet-18 from h-e1 checkpoint, CIFAR-10 modifications applied"""
    ...

def load_data(cfg: H3Config) -> Tuple[DataLoader, DataLoader]:
    """Load CIFAR-10 subsets using H-E1 indices (subset_seed=42)"""
    ...

def load_or_compute_scores(
    cfg: H3Config,
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    device: str
) -> Dict[int, Dict[str, np.ndarray]]:
    """
    Returns: {budget: {method: (n_test, n_train) scores}}
    Loads cached npz if exists, else computes via H-E1 attribution classes.
    Note: H-E1 returns [n_train, n_test]; transpose to [n_test, n_train] here.
    """
    ...

def run(cfg: H3Config) -> Dict[str, Any]:
    """Main orchestrator. Returns gate result dict."""
    ...

if __name__ == '__main__':
    cfg = get_config()
    results = run(cfg)
    print(f"Gate: min(Jaccard)={results['min_jaccard']:.3f}, PASS={results['gate_pass']}")
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | Project structure, H3Config, path validation to H-E1 assets | 6 | 2+1+1+2 |
| A-2 | Data & Model Loading | Load CIFAR-10 subsets with H-E1 indices, load ResNet-18 checkpoint | 7 | 2+2+1+2 |
| A-3 | Attribution Score Computation | Run all 4 methods x 5 budgets x 3 seeds via H-E1 classes; cache to npz | 14 | 3+4+3+4 |
| A-4 | Jaccard Analyzer | Implement JaccardAnalyzer: top-k extraction, pairwise Jaccard, budget loop | 10 | 3+2+3+2 |
| A-5 | Gate Evaluation | Compute min(Jaccard) across all budgets/seeds; check < 0.70 | 7 | 2+2+2+1 |
| A-6 | Persistence Analysis | PersistenceAnalyzer: relative advantage tracking, 60% persistence check | 9 | 3+2+2+2 |
| A-7 | Visualization - Gate Figure | Jaccard heatmap with 0.70 threshold annotation | 8 | 2+2+2+2 |
| A-8 | Visualization - Additional Figures | jaccard_by_budget, topk_overlap, ranking_persistence, paradigm_clustering | 10 | 3+2+2+3 |
| A-9 | Results Serialization | Save attribution_scores.npz, jaccard_analysis.csv, metric_advantages.csv | 6 | 2+1+1+2 |
| A-10 | Experiment Orchestrator | run_experiment.py tying all modules; CLI entry point | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-4, A-6, A-8, A-10], Low(4-8): [A-1, A-2, A-5, A-7, A-9]

---

## Key Interface Notes

- H-E1 `compute_scores` returns `[n_train, n_test]` — must transpose to `[n_test, n_train]` in `load_or_compute_scores`
- Import H-E1 modules via `sys.path.insert(0, cfg.base_code_dir)` before imports
- Scores cached at `results/attribution_scores.npz` with keys `{method}_{budget}_{seed}`
- Gate evaluated per budget; overall gate passes if any budget achieves min(Jaccard) < 0.70
