# Architecture: h-m2 — Bidirectional C_sem Directional Asymmetry

**Hypothesis**: h-m2 (MECHANISM, INCREMENTAL)
**Date**: 2026-03-15
**Base**: h-m1 (VALIDATED)
**Infrastructure**: FULL tier (YAML + dataclass config, structured logging, unit tests)

Applied: copy-extend pattern (h-m1 modules extended with bidirectional direction support)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (Read tool used — Serena project not active for this path)
**Analyzed Path**: `docs/youra_research/20260315_bi_align/h-m1/code/`
**Findings**: h-m1 uses flat local imports (no package prefix). All modules import from same directory. `run_experiment.py` uses `from data_loader import ...`, `from embedder import ...`, etc. `controls.py` uses `n_jobs=1` in NearestNeighbors (critical for 155k scale). `statistics.py` has `bonferroni_mannwhitney`, `ks_test_tier_distributions`, `compute_ipw_csem` already implemented. `accommodation.py` `compute_tier_csem_matrix` is the core function to extend with `A←H` direction.

---

## File Organization

- `h-m2/code/`
  - `config.py` — ExperimentConfig dataclass + YAML loader
  - `data_loader.py` — copy-extend from h-m1 (add `h_curr`, `a_next` fields)
  - `embedder.py` — copy as-is from h-m1
  - `controls.py` — copy as-is from h-m1
  - `accommodation.py` — copy-extend (add `compute_bidirectional_csem_per_tier`)
  - `statistics.py` — copy-extend (add `test_directional_asymmetry`, `verify_mechanism_activated_m2`, `compute_asymmetry_monotonicity`)
  - `visualize.py` — copy-extend (add 6 bidirectional figures)
  - `run_experiment.py` — rewrite as h-m2 orchestrator
  - `config.yaml` — single fixed experiment config
  - `tests/`
    - `test_accommodation.py`
    - `test_statistics.py`
    - `test_data_loader.py`
    - `test_visualize.py`
    - `test_run_experiment.py`
- `h-m2/figures/` — output directory for all figures

---

## Module Interfaces

### config (`config.py`)

**Dependencies**: none (stdlib only)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class ExperimentConfig:
    cache_dir: str = ".data_cache/datasets/hh-rlhf"
    embedding_cache_dir: str = "../h-m1/code/embeddings"
    h_m1_embedding_cache_dir: str = "../h-m1/code/embeddings"
    figures_dir: str = "../figures"
    results_dir: str = "../results"
    model_names: List[str] = field(default_factory=lambda: [
        "all-MiniLM-L6-v2",
        "paraphrase-MiniLM-L6-v2",
        "all-mpnet-base-v2",
    ])
    knn_k: int = 5
    knn_n_jobs: int = 1  # CRITICAL: not -1
    seed: int = 42
    n_bootstrap: int = 1000
    alpha: float = 0.05
    tiers_required: int = 2
    models_required: int = 2

def load_config(yaml_path: str) -> ExperimentConfig: ...
```

---

### data_loader (`data_loader.py`)

**Dependencies**: config, datasets

```python
from typing import Dict, List

TIER_ORDER: List[str]  # ["helpful-base", "helpful-rejection-sampled", "helpful-online"]

def split_by_tier(cache_dir: str) -> Dict[str, Dict]:
    """Returns tier_name -> {h_next, a_actual, h_prompt, h_curr, a_next, token_counts, jaccard_overlaps}"""
    ...

def load_all_splits(cache_dir: str) -> List[dict]: ...

def extract_pairs(records: List[dict]) -> Dict:
    """Returns {h_next, a_actual, h_prompt, h_curr, a_next, token_counts, jaccard_overlaps}"""
    ...

def verify_embedding_cache(
    cache_dir: str,
    model_names: List[str],
    tiers: List[str],
) -> Dict[str, bool]:
    """Check presence of all required .npy files including h_curr and a_next.
    Returns {cache_key: exists_bool} for all 4 × 3 models × 3 tiers = 36 files."""
    ...
```

---

### embedder (`embedder.py`)

**Dependencies**: sentence-transformers, numpy

Copied as-is from h-m1. Interface unchanged.

```python
class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: str = "embeddings"): ...
    def encode(self, texts: List[str], cache_key: str) -> np.ndarray: ...
    def encode_tier(self, texts: List[str], prefix: str, tier: str, n_pairs: int) -> np.ndarray: ...
    def load_cache(self, cache_key: str) -> Optional[np.ndarray]: ...
    def save_cache(self, embeddings: np.ndarray, cache_key: str) -> None: ...
```

---

### controls (`controls.py`)

**Dependencies**: numpy, scikit-learn

Copied as-is from h-m1. Interface unchanged.

```python
def build_random_control(ai_embeddings: np.ndarray, seed: int = 42) -> np.ndarray: ...

def build_topic_control(
    prompt_embeddings: np.ndarray,
    ai_embeddings: np.ndarray,
    k: int = 5,
) -> np.ndarray:
    """KNN topic-matched control. n_jobs=1 (CRITICAL for 155k scale)."""
    ...
```

---

### accommodation (`accommodation.py`)

**Dependencies**: controls, embedder, numpy

```python
from typing import Dict, Callable

TIER_ORDER: List[str]

def compute_cosine_similarities(
    h_next: np.ndarray,
    a_actual: np.ndarray,
    a_topic: np.ndarray,
    a_random: np.ndarray,
) -> Dict[str, np.ndarray]: ...

def compute_c_sem(cos_actual: np.ndarray, cos_random: np.ndarray) -> float: ...

def residualize(cos_array: np.ndarray, covariate: np.ndarray) -> np.ndarray: ...

def apply_residualization(
    cos_dict: Dict[str, np.ndarray],
    token_counts: List[int],
    jaccard_overlaps: List[float],
) -> Dict[str, np.ndarray]: ...

def compute_tier_csem_matrix(
    tier_pairs: Dict,
    embedder,
    controls_fn_random: Callable,
    controls_fn_topic: Callable,
    seed: int = 42,
) -> Dict[str, Dict]:
    """H-m1 H←A direction. Returns {tier: {c_sem, raw_cos_actual, raw_cos_random, n_pairs}}"""
    ...

def compute_bidirectional_csem_per_tier(
    tier_pairs: Dict,
    embedder,
    controls_fn_random: Callable,
    controls_fn_topic: Callable,
    ipw_weights: Optional[Dict[str, np.ndarray]] = None,
    seed: int = 42,
) -> Dict[str, Dict]:
    """NEW for h-m2: both H←A and A←H directions.

    For each tier:
      - Direction H←A: cos(H_{t+1}, A_t) - cos(H_{t+1}, A_t[shuffle_H])
      - Direction A←H: cos(A_{t+1}, H_t) - cos(A_{t+1}, H_t[shuffle_A])
    Logs: [FR-M2] Tier {tier}: C_sem^H<-A={:.4f}, C_sem^A<-H={:.4f}

    Returns:
        {tier: {csem_H_given_A, csem_A_given_H,
                raw_cos_H_given_A, raw_cos_A_given_H, n_pairs}}
    """
    ...

def aggregate_model_results(all_model_results: Dict) -> Dict: ...
```

---

### statistics (`statistics.py`)

**Dependencies**: numpy, scipy, scikit-learn

```python
from typing import Dict, List, Tuple

# --- h-e1 / h-m1 functions (unchanged) ---
def bootstrap_c_sem(cos_actual, cos_random, n_bootstrap=1000, seed=42) -> Tuple[float, np.ndarray]: ...
def bootstrap_cohen_d(arr_a, arr_b, n_bootstrap=1000, seed=42) -> Tuple[float, np.ndarray]: ...
def mann_whitney_test(arr_a, arr_b) -> Dict: ...
def run_all_tests(cos_actual, cos_topic, cos_random, n_pairs) -> Dict: ...
def verify_mechanism_activated(results, embeddings_computed) -> Tuple[bool, Dict]: ...
def jonckheere_terpstra_test(tier_results, tier_order) -> Dict: ...
def bonferroni_mannwhitney(tier_results, tier_order, n_bootstrap=1000, seed=42) -> Dict: ...
def ks_test_tier_distributions(tier_prompt_embeddings, tier_order) -> Dict: ...
def compute_ipw_csem(tier_results, tier_prompt_embeddings) -> Dict: ...
def check_model_consistency(all_model_results, jt_alpha=0.05, d_threshold=0.1) -> Dict: ...
def verify_mechanism_activated_m1(all_model_results, experiment_log) -> Tuple[bool, Dict]: ...

# --- NEW for h-m2 ---
def test_directional_asymmetry(
    bidir_results_by_tier: Dict,
    alpha: float = 0.05,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> Dict:
    """Per-tier Mann-Whitney U (one-sided: H←A > A←H).

    Args:
        bidir_results_by_tier: {tier: {csem_H_given_A, csem_A_given_H, ...}}
    Returns:
        {tier: {mw_statistic, p_value, cohen_d, cohen_d_ci, delta_asymmetry},
         'tiers_passing': int, 'gate_passed': bool}
    Logs: [FR-M2] Tier {tier}: C_sem^H<-A={:.4f}, C_sem^A<-H={:.4f}, p={:.4f}, d={:.4f}
    """
    ...

def compute_asymmetry_monotonicity(
    bidir_results_by_tier: Dict,
    tier_order: List[str],
) -> Dict:
    """Secondary: check if delta_asymmetry = H←A - A←H increases T1 < T2 < T3.
    Returns {deltas: {tier: float}, is_monotonic: bool, jt_result: Dict}"""
    ...

def check_model_consistency_m2(
    all_model_bidir_results: Dict,
    alpha: float = 0.05,
) -> Dict:
    """Gate: >= 2/3 models show H←A > A←H with p < 0.05 at >= 2/3 tiers.
    Returns {models_passing: int, passing_models: List[str], gate_passed: bool}"""
    ...

def verify_mechanism_activated_m2(
    all_model_bidir_results: Dict,
    experiment_log: str,
) -> Tuple[bool, Dict]:
    """4 indicators: both_directions_computed, shapes_match,
       asymmetry_nonzero, fr_m2_logs_found."""
    ...

def compute_ipw_csem_bidir(
    bidir_results_by_tier: Dict,
    tier_prompt_embeddings: Dict,
) -> Dict:
    """IPW-adjusted C_sem for both H←A and A←H directions.
    Returns {tier: {ipw_csem_H_given_A, ipw_csem_A_given_H}}"""
    ...
```

---

### visualize (`visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy

```python
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class VisualizationConfig:
    figure_size: tuple = (12, 5)
    figure_size_wide: tuple = (18, 6)
    dpi: int = 150
    figures_dir: str = "figures"

# --- h-m1 functions (unchanged) ---
def plot_tier_csem_bars(tier_results, models_results, config, save_path) -> None: ...
def plot_tier_monotonicity_lines(models_results, config, save_path) -> None: ...
def plot_cohend_heatmap(cohend_results, config, save_path) -> None: ...
def plot_ipw_comparison(raw_csem, ipw_csem, config, save_path) -> None: ...

# --- NEW for h-m2 ---
def plot_bidirectional_bars(
    bidir_results: Dict,
    tier_order: List[str],
    save_path: str,
    config: Optional[VisualizationConfig] = None,
) -> None:
    """REQUIRED: Grouped bar chart C_sem^H<-A vs C_sem^A<-H per tier, CI whiskers."""
    ...

def plot_directional_asymmetry_bars(
    all_model_bidir_results: Dict,
    tier_order: List[str],
    save_path: str,
    config: Optional[VisualizationConfig] = None,
) -> None:
    """C_sem^H<-A vs C_sem^A<-H x 3 tiers x 3 models grouped bar + CI."""
    ...

def plot_asymmetry_delta_line(
    all_model_bidir_results: Dict,
    tier_order: List[str],
    save_path: str,
    config: Optional[VisualizationConfig] = None,
) -> None:
    """Line plot: delta_asymmetry = H<-A minus A<-H across tiers per model."""
    ...

def plot_pairwise_distributions_violin(
    bidir_results_by_tier: Dict,
    tier_order: List[str],
    save_path: str,
    config: Optional[VisualizationConfig] = None,
) -> None:
    """Violin/KDE: per-pair csem distribution H<-A vs A<-H."""
    ...

def plot_significance_heatmap(
    asymmetry_test_results: Dict,
    model_names: List[str],
    tier_order: List[str],
    save_path: str,
    config: Optional[VisualizationConfig] = None,
) -> None:
    """Heatmap: p-values for H<-A > A<-H across tier x model grid."""
    ...

def plot_bootstrap_ci_comparison(
    bidir_results: Dict,
    tier_order: List[str],
    save_path: str,
    n_bootstrap: int = 1000,
    seed: int = 42,
    config: Optional[VisualizationConfig] = None,
) -> None:
    """Bootstrap CI for both directions per tier."""
    ...

def plot_ipw_asymmetry(
    raw_bidir: Dict,
    ipw_bidir: Dict,
    tier_order: List[str],
    save_path: str,
    config: Optional[VisualizationConfig] = None,
) -> None:
    """Bar + error: raw vs IPW-corrected delta_asymmetry."""
    ...
```

---

### run_experiment (`run_experiment.py`)

**Dependencies**: all modules above

```python
import argparse
import logging
from typing import Dict

def parse_args() -> argparse.Namespace: ...

def verify_embedding_cache(config) -> Dict[str, bool]:
    """Check h-m1 cache for all required .npy files. Log missing."""
    ...

def run_single_model(
    model_name: str,
    tier_pairs: Dict,
    config,
) -> Dict:
    """Full pipeline for one SBERT model:
    1. Verify/encode embeddings (H_next, A_curr, H_curr, A_next)
    2. Build controls for both directions
    3. KS test + IPW if triggered
    4. compute_bidirectional_csem_per_tier()
    5. test_directional_asymmetry()
    6. compute_asymmetry_monotonicity()
    Returns: {tier_results, asymmetry_test, monotonicity}
    """
    ...

def main() -> None:
    """Orchestrates 3-model loop:
    1. Load config
    2. Load data via split_by_tier()
    3. For each model: run_single_model()
    4. check_model_consistency_m2()
    5. verify_mechanism_activated_m2()
    6. Generate all 7 figures
    7. Save results JSON
    8. Log gate result: PASS/FAIL with tiers_passing count
    """
    ...

if __name__ == "__main__":
    main()
```

---

## External Dependencies

### Module Paths (From Actual h-m1 Code)

| Module | Import in h-m2 | Source File | Reuse Pattern |
|--------|----------------|-------------|---------------|
| split_by_tier | `from data_loader import split_by_tier` | `h-m1/code/data_loader.py` | copy-extend |
| Embedder | `from embedder import Embedder` | `h-m1/code/embedder.py` | copy as-is |
| build_random_control | `from controls import build_random_control` | `h-m1/code/controls.py` | copy as-is |
| build_topic_control | `from controls import build_topic_control` | `h-m1/code/controls.py` | copy as-is |
| compute_tier_csem_matrix | `from accommodation import compute_tier_csem_matrix` | `h-m1/code/accommodation.py` | copy-extend |
| bonferroni_mannwhitney | `from statistics import bonferroni_mannwhitney` | `h-m1/code/statistics.py` | copy-extend |
| ks_test_tier_distributions | `from statistics import ks_test_tier_distributions` | `h-m1/code/statistics.py` | copy-extend |
| compute_ipw_csem | `from statistics import compute_ipw_csem` | `h-m1/code/statistics.py` | copy-extend |
| VisualizationConfig | `from visualize import VisualizationConfig` | `h-m1/code/visualize.py` | copy-extend |

**Verified from**: `docs/youra_research/20260315_bi_align/h-m1/code/` (actual implementation)

**Import pattern**: flat local imports, no package prefix (e.g., `from accommodation import ...` not `from h_m1.accommodation import ...`)

**Critical note from h-m1**: `NearestNeighbors(n_jobs=1)` — must not change to `n_jobs=-1` (crashes at 155k scale).

---

## Epic Tasks

| ID | Task | Description | Complexity |
|----|------|-------------|------------|
| A-1 | Setup & Config | Create config.py, config.yaml, directory structure, verify h-m1 cache paths | **8/20** (Module_Size=2 + Dependencies=1 + Algorithm=2 + Integration=3) |
| A-2 | Extend data_loader | Copy-extend data_loader.py: add h_curr and a_next fields to extract_pairs(), add verify_embedding_cache() | **10/20** (Module_Size=3 + Dependencies=2 + Algorithm=2 + Integration=3) |
| A-3 | Copy embedder + controls | Copy embedder.py and controls.py as-is; verify n_jobs=1 and cache key naming matches h-m1 | **6/20** (Module_Size=2 + Dependencies=1 + Algorithm=1 + Integration=2) |
| A-4 | Extend accommodation | Copy-extend accommodation.py: add compute_bidirectional_csem_per_tier() with H←A and A←H direction, FR-M2 logging | **14/20** (Module_Size=4 + Dependencies=3 + Algorithm=4 + Integration=3) |
| A-5 | Extend statistics | Copy-extend statistics.py: add test_directional_asymmetry(), compute_asymmetry_monotonicity(), check_model_consistency_m2(), verify_mechanism_activated_m2(), compute_ipw_csem_bidir() | **16/20** (Module_Size=4 + Dependencies=4 + Algorithm=4 + Integration=4) |
| A-6 | Extend visualize | Copy-extend visualize.py: add 7 bidirectional figures (1 required + 6 autonomous) | **13/20** (Module_Size=4 + Dependencies=2 + Algorithm=3 + Integration=4) |
| A-7 | Implement run_experiment | Rewrite run_experiment.py as h-m2 orchestrator: 3-model loop, bidirectional pipeline, gate evaluation, figure generation, results JSON | **16/20** (Module_Size=4 + Dependencies=4 + Algorithm=4 + Integration=4) |
| A-8 | Embedding cache check + encode | Verify h-m1 cache; if A_next or H_curr missing, run additional encoding pass for all 3 models | **11/20** (Module_Size=3 + Dependencies=3 + Algorithm=2 + Integration=3) |
| A-9 | Unit tests | pytest for accommodation (bidirectional), statistics (test_directional_asymmetry, verify_m2), data_loader (verify_cache), visualize (figure output), run_experiment (mock run) | **12/20** (Module_Size=3 + Dependencies=3 + Algorithm=2 + Integration=4) |
| A-10 | Run full experiment | Execute run_experiment.py on full 155k dataset (3 models × 3 tiers), collect results | **10/20** (Module_Size=2 + Dependencies=3 + Algorithm=2 + Integration=3) |
| A-11 | Gate evaluation + reporting | Evaluate tiers_passing >= 2, models_passing >= 2, verify_mechanism_activated_m2(), save results JSON, log PASS/FAIL | **9/20** (Module_Size=2 + Dependencies=3 + Algorithm=2 + Integration=2) |

**Distribution**:
- VeryHigh (18-20): []
- High (14-17): [A-4, A-5, A-7]
- Medium (9-13): [A-2, A-6, A-8, A-9, A-10, A-11]
- Low (4-8): [A-1, A-3]
