# Architecture: h-m3 — Within-Prompt Quality Probe via Chosen/Rejected Δ-Cosine Analysis

**Hypothesis**: h-m3 (MECHANISM, INCREMENTAL)
**Date**: 2026-03-15
**Base**: h-m2 (VALIDATED)
**Infrastructure**: FULL tier (YAML + dataclass config, structured logging, unit tests)

Applied: copy-extend pattern (h-m2 modules extended with chosen/rejected pair parsing and Δ-operationalization framework)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (Read tool used — Serena project not active for this path)
**Analyzed Path**: `docs/youra_research/20260315_bi_align/h-m2/code/`
**Findings**: h-m2 uses flat local imports (no package prefix). `config.py` uses nested dataclasses (ExperimentConfig, CacheConfig, StatisticsConfig, FigureConfig). `data_loader.py::extract_pairs()` parses `chosen` field only (not `rejected`); `parse_conversation()` uses regex split on `\n\nHuman: |\n\nAssistant: `. `accommodation.py` has per-pair `compute_h_given_a_csem_array()` and `compute_a_given_h_csem_array()` using normalized dot product. `embedder.py::encode_tier()` uses cache key `{model}_{prefix}_{tier}.npy`. `statistics.py` has `bootstrap_c_sem()` with `rng.integers` pattern. h-m3 needs new `delta_probe.py` module and `data_loader` extension to parse `rejected` field.

---

## File Organization

- `h-m3/code/`
  - `config.py` — copy-extend from h-m2 (update hypothesis_id, add delta config fields)
  - `data_loader.py` — copy-extend from h-m2 (add `parse_chosen_rejected_pairs()`)
  - `embedder.py` — copy as-is from h-m2
  - `controls.py` — copy as-is from h-m2
  - `accommodation.py` — copy as-is from h-m2 (imported for `compute_cosine_similarities`)
  - `statistics.py` — copy-extend from h-m2 (add `bootstrap_delta_ci`, `ttest_delta`, `gate_evaluation_m3`, `verify_mechanism_activated_m3`)
  - `delta_probe.py` — NEW: 3-operationalization Δ computation engine
  - `visualize.py` — copy-extend from h-m2 (add 6 h-m3 figures)
  - `run_experiment.py` — rewrite as h-m3 orchestrator
  - `config.yaml` — single fixed experiment config
  - `tests/`
    - `test_delta_probe.py`
    - `test_data_loader.py`
    - `test_statistics.py`
    - `test_visualize.py`
    - `test_run_experiment.py`
- `h-m3/results/` — output directory for JSON results
- `h-m3/results/figures/` — output directory for figures

---

## Module Interfaces

### config (`config.py`)

**Dependencies**: none (stdlib only)

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class CacheConfig:
    cache_dir: str = ".data_cache/datasets/hh-rlhf"
    embeddings_dir: str = "../h-m2/code/embeddings"
    models: List[str] = field(default_factory=lambda: [
        "all-MiniLM-L6-v2",
        "paraphrase-MiniLM-L6-v2",
        "all-mpnet-base-v2",
    ])
    tiers: List[str] = field(default_factory=lambda: [
        "helpful-base",
        "helpful-rejection-sampled",
        "helpful-online",
    ])
    encode_batch_size: int = 256

@dataclass
class StatisticsConfig:
    seed: int = 42
    alpha: float = 0.05
    n_bootstrap: int = 1000
    knn_n_jobs: int = 1   # CRITICAL: never -1 at 155k scale
    min_n_pairs: int = 1000
    ops_required: int = 2  # >= 2/3 operationalizations must pass

@dataclass
class FigureConfig:
    figures_dir: str = "../results/figures"
    dpi: int = 150
    save_format: str = "png"

@dataclass
class ExperimentConfig:
    hypothesis_id: str = "h-m3"
    cache: CacheConfig = field(default_factory=CacheConfig)
    stats: StatisticsConfig = field(default_factory=StatisticsConfig)
    figures: FigureConfig = field(default_factory=FigureConfig)
    results_dir: str = "../results"
    dry_run: bool = False
    n_samples_dry_run: int = 500

    @property
    def cache_dir(self) -> str: ...
    @property
    def figures_dir(self) -> str: ...

def load_config(yaml_path: Optional[str] = None) -> ExperimentConfig: ...
```

---

### data_loader (`data_loader.py`)

**Dependencies**: config, datasets

```python
from typing import Dict, List, Tuple

TIER_ORDER: List[str]  # ["helpful-base", "helpful-rejection-sampled", "helpful-online"]
MIN_N_PAIRS_PER_TIER: int = 1000

def split_by_tier(cache_dir: str) -> Dict[str, Dict]:
    """Returns tier_name -> {h_next, a_actual, h_prompt, token_counts,
    jaccard_overlaps, h_curr, a_next}  (h-m2 fields — unchanged)"""
    ...

def extract_pairs(conversations: List[dict]) -> Dict:
    """h-m2 function — unchanged. Parses `chosen` field only."""
    ...

def parse_conversation(text: str) -> List[str]:
    """Regex split on Human:/Assistant: pattern — unchanged from h-m2."""
    ...

def parse_chosen_rejected_pairs(
    records: List[dict],
) -> Tuple[Dict, int]:
    """NEW for h-m3: extract (H_next, A_chosen, A_rejected, H_prompt) tuples.

    Parses both `chosen` and `rejected` fields from each record.
    Shares the same prompt prefix up to first Assistant turn.
    If chosen/rejected prompts differ: use chosen-side H_next as reference.
    Filters invalid pairs (empty H_next, empty A_chosen, empty A_rejected).

    Returns:
        pairs_dict: {h_next, a_chosen, a_rejected, h_prompt,
                     a_chosen_token_len, a_rejected_token_len}
        n_pairs: int
    Logs: "N_pairs: {n} from {total} records (tier={tier})"
    """
    ...

def split_chosen_rejected_by_tier(cache_dir: str) -> Dict[str, Dict]:
    """NEW for h-m3: load each tier, call parse_chosen_rejected_pairs().

    Returns tier_name -> {h_next, a_chosen, a_rejected, h_prompt,
                          a_chosen_token_len, a_rejected_token_len, n_pairs}
    Logs warning if n_pairs < MIN_N_PAIRS_PER_TIER (does NOT raise — auto-demote).
    """
    ...

def verify_embedding_cache(
    cache_dir: str,
    model_names: List[str],
    tiers: List[str],
) -> Dict[str, bool]: ...

def compute_jaccard(s1: str, s2: str) -> float: ...
def compute_token_count(text: str) -> int: ...
```

---

### embedder (`embedder.py`)

**Dependencies**: sentence-transformers, numpy

Copied as-is from h-m2. Interface unchanged.

```python
class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: str = "embeddings"): ...
    def encode(self, texts: List[str], cache_key: str) -> np.ndarray: ...
    def encode_tier(self, texts: List[str], prefix: str, tier: str, n_pairs: int) -> np.ndarray: ...
    def load_cache(self, cache_key: str) -> Optional[np.ndarray]: ...
    def save_cache(self, embeddings: np.ndarray, cache_key: str) -> None: ...
```

---

### delta_probe (`delta_probe.py`)

**Dependencies**: embedder, numpy

NEW module. Core Δ computation with 3 operationalizations.

```python
import numpy as np
from typing import Dict, List, Tuple

OPERATIONALIZATIONS: List[str] = ["raw", "length_matched", "prompt_projected"]

def truncate_to_rejected_length(
    a_chosen_texts: List[str],
    a_chosen_token_lens: List[int],
    a_rejected_token_lens: List[int],
) -> List[str]:
    """Truncate A_chosen tokens to len(A_rejected) before embedding.

    Token approximation: whitespace split (consistent with compute_token_count).
    Returns list of truncated A_chosen strings.
    """
    ...

def project_out(
    vecs: np.ndarray,
    direction: np.ndarray,
) -> np.ndarray:
    """Project out direction from vecs: v - (v·d)d (assumes d is L2-normalized).

    Args:
        vecs: [N, D] L2-normalized embeddings
        direction: [N, D] L2-normalized prompt embeddings (per-pair direction)
    Returns:
        [N, D] projected embeddings (NOT re-normalized)
    """
    ...

def compute_delta_raw(
    emb_h_next: np.ndarray,
    emb_a_chosen: np.ndarray,
    emb_a_rejected: np.ndarray,
) -> np.ndarray:
    """OP1: Δ_raw = cos(H_next, A_chosen) - cos(H_next, A_rejected).

    Uses dot product for L2-normalized embeddings.
    Returns np.ndarray shape (N,).
    """
    ...

def compute_delta_length_matched(
    h_next_texts: List[str],
    a_chosen_texts: List[str],
    a_rejected_texts: List[str],
    a_chosen_token_lens: List[int],
    a_rejected_token_lens: List[int],
    embedder,
    tier: str,
) -> np.ndarray:
    """OP2: Truncate A_chosen to |A_rejected| tokens, recompute delta.

    Returns np.ndarray shape (N,).
    """
    ...

def compute_delta_prompt_projected(
    emb_h_next: np.ndarray,
    emb_a_chosen: np.ndarray,
    emb_a_rejected: np.ndarray,
    emb_h_prompt: np.ndarray,
) -> np.ndarray:
    """OP3: Project out prompt direction from A_chosen and A_rejected, then compute delta.

    Returns np.ndarray shape (N,).
    """
    ...

def compute_all_deltas(
    tier_pairs: Dict,
    embedder,
    tier: str,
) -> Dict[str, np.ndarray]:
    """Compute all 3 operationalizations for one tier + one model.

    Args:
        tier_pairs: {h_next, a_chosen, a_rejected, h_prompt,
                     a_chosen_token_len, a_rejected_token_len}
        embedder: Embedder instance
        tier: tier name (for cache key naming)
    Returns:
        {"raw": np.ndarray, "length_matched": np.ndarray, "prompt_projected": np.ndarray}
        Each array shape (N,) per-pair Δ values.
    Logs: "[FR-M3] Tier {tier}: N_pairs={n}, E[Δ_raw]={:.4f}, E[Δ_len]={:.4f}, E[Δ_proj]={:.4f}"
    """
    ...
```

---

### statistics (`statistics.py`)

**Dependencies**: numpy, scipy

Copy-extend from h-m2. Add h-m3 functions.

```python
from typing import Dict, List, Tuple

# --- h-e1 / h-m1 / h-m2 functions (unchanged) ---
def bootstrap_c_sem(cos_actual, cos_random, n_bootstrap=1000, seed=42) -> Tuple[float, np.ndarray]: ...
def bootstrap_cohen_d(arr_a, arr_b, n_bootstrap=1000, seed=42) -> Tuple[float, np.ndarray]: ...
def mann_whitney_test(arr_a, arr_b) -> Dict: ...
def jonckheere_terpstra_test(tier_results, tier_order) -> Dict: ...
def bonferroni_mannwhitney(tier_results, tier_order, n_bootstrap=1000, seed=42) -> Dict: ...
def ks_test_tier_distributions(tier_prompt_embeddings, tier_order) -> Dict: ...
def compute_ipw_csem(tier_results, tier_prompt_embeddings) -> Dict: ...

# --- NEW for h-m3 ---
def bootstrap_delta_ci(
    delta_values: np.ndarray,
    n_resamples: int = 1000,
    seed: int = 42,
) -> Tuple[float, float, float]:
    """Bootstrap mean Δ with 95% CI.

    Returns: (mean_delta, ci_lower, ci_upper)
    Uses rng.choice (consistent with experiment brief pseudo-code).
    """
    ...

def ttest_delta(
    delta_values: np.ndarray,
) -> Dict:
    """One-sample t-test: H0: E[Δ] = 0.

    Returns: {t_stat, p_value, df, significant}
    """
    ...

def cohens_d_onesample(
    delta_values: np.ndarray,
) -> float:
    """Cohen's d for one-sample test: mean(Δ) / std(Δ).

    Returns: float d value.
    """
    ...

def gate_evaluation_m3(
    ops_results: Dict[str, Dict],
    min_n_pairs: int = 1000,
) -> Dict:
    """Evaluate SHOULD_WORK gate.

    Args:
        ops_results: {op_name: {mean_delta, ci_lower, ci_upper, n_pairs}}
                     keyed by "raw", "length_matched", "prompt_projected"
        min_n_pairs: threshold for auto-demote condition
    Returns:
        {gate_passed: bool, ops_passing: int, ops_passing_list: List[str],
         auto_demote: bool, n_pairs_min: int, gate_result: str}
    """
    ...

def check_model_consistency_m3(
    all_model_results: Dict,
    ops: List[str] = None,
) -> Dict:
    """Gate: >= 2/3 models show consistent Δ > 0 sign in >= 2/3 operationalizations.

    Returns: {models_consistent: int, consistent_models: List[str], gate_passed: bool}
    """
    ...

def verify_mechanism_activated_m3(
    all_model_results: Dict,
    experiment_log: str,
) -> Tuple[bool, Dict]:
    """4 indicators: n_pairs_sufficient, delta_positive, ci_lower_positive,
       operationalizations_pass."""
    ...
```

---

### visualize (`visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy

Copy-extend from h-m2. Add 6 h-m3 figures.

```python
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class VisualizationConfig:
    figure_size: tuple = (12, 5)
    figure_size_wide: tuple = (18, 6)
    dpi: int = 150
    figures_dir: str = "results/figures"

# --- h-m1/h-m2 functions (unchanged) ---
def plot_tier_csem_bars(tier_results, models_results, config, save_path) -> None: ...
def plot_bidirectional_bars(bidir_results, tier_order, save_path, config=None) -> None: ...

# --- NEW for h-m3 ---
def plot_delta_distributions(
    delta_results_by_op: Dict[str, np.ndarray],
    save_path: str,
    config: Optional[VisualizationConfig] = None,
) -> None:
    """MANDATORY Fig 1: Violin/box per operationalization of per-pair Δ values."""
    ...

def plot_bootstrap_ci_by_op_and_model(
    all_model_op_stats: Dict,
    save_path: str,
    config: Optional[VisualizationConfig] = None,
) -> None:
    """MANDATORY Fig 2: E[Δ] bar with bootstrap CI per operationalization × model."""
    ...

def plot_n_pairs_bar(
    tier_n_pairs: Dict[str, int],
    min_threshold: int,
    save_path: str,
    config: Optional[VisualizationConfig] = None,
) -> None:
    """MANDATORY Fig 3: N_pairs per tier with gate threshold line."""
    ...

def plot_delta_by_tier(
    delta_results_by_tier_op: Dict,
    tier_order: List[str],
    save_path: str,
    config: Optional[VisualizationConfig] = None,
) -> None:
    """AUTONOMOUS Fig 4: Δ distribution by RLHF tier (base/RS/online)."""
    ...

def plot_delta_raw_vs_length_scatter(
    delta_raw: np.ndarray,
    delta_length: np.ndarray,
    save_path: str,
    config: Optional[VisualizationConfig] = None,
) -> None:
    """AUTONOMOUS Fig 5: Scatter Δ_raw vs Δ_length_matched correlation."""
    ...

def plot_model_op_heatmap(
    summary_matrix: Dict,
    model_names: List[str],
    save_path: str,
    config: Optional[VisualizationConfig] = None,
) -> None:
    """AUTONOMOUS Fig 6: Heatmap 3 models × 3 operationalizations × mean Δ."""
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

def run_single_model(
    model_name: str,
    tier_cr_pairs: Dict,
    config,
) -> Dict:
    """Full pipeline for one SBERT model:
    1. Verify/encode embeddings (H_next, A_chosen, A_rejected, H_prompt)
    2. compute_all_deltas() for each tier and all 3 operationalizations
    3. bootstrap_delta_ci() + ttest_delta() + cohens_d_onesample() per op
    4. gate_evaluation_m3()
    Returns: {tier_results, op_stats, gate_result}
    """
    ...

def main() -> None:
    """Orchestrates 3-model loop:
    1. load_config()
    2. split_chosen_rejected_by_tier() → verify N_pairs (auto-demote check)
    3. For each model: run_single_model()
    4. check_model_consistency_m3()
    5. verify_mechanism_activated_m3()
    6. Generate all 6 figures
    7. Save delta_results.json
    8. Log gate result: PASS/FAIL with ops_passing count
    """
    ...

if __name__ == "__main__":
    main()
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual h-m2 Code)

| Module | Import in h-m3 | File Location | Reuse Pattern |
|--------|----------------|---------------|---------------|
| parse_conversation | `from data_loader import parse_conversation` | `h-m2/code/data_loader.py` | copy as-is |
| extract_pairs | `from data_loader import extract_pairs` | `h-m2/code/data_loader.py` | copy as-is (h-m1 pairs) |
| compute_cosine_similarities | `from accommodation import compute_cosine_similarities` | `h-m2/code/accommodation.py` | copy as-is |
| compute_c_sem | `from accommodation import compute_c_sem` | `h-m2/code/accommodation.py` | copy as-is |
| Embedder | `from embedder import Embedder` | `h-m2/code/embedder.py` | copy as-is |
| build_random_control | `from controls import build_random_control` | `h-m2/code/controls.py` | copy as-is |
| build_topic_control | `from controls import build_topic_control` | `h-m2/code/controls.py` | copy as-is |
| bootstrap_c_sem | `from statistics import bootstrap_c_sem` | `h-m2/code/statistics.py` | copy-extend |
| ExperimentConfig | `from config import ExperimentConfig` | `h-m2/code/config.py` | copy-extend |
| VisualizationConfig | `from visualize import VisualizationConfig` | `h-m2/code/visualize.py` | copy-extend |

**Verified from**: `docs/youra_research/20260315_bi_align/h-m2/code/` (actual implementation)

**Import pattern**: flat local imports, no package prefix (e.g., `from delta_probe import compute_all_deltas`)

**Critical notes from h-m2**:
- `NearestNeighbors(n_jobs=1)` — must not change to `n_jobs=-1`
- Cache key format: `{model_slug}_{prefix}_{tier_slug}.npy` (e.g., `minilm_h_next_base.npy`)
- h-m3 needs NEW cache keys: `{model}_A_chosen_{tier}.npy`, `{model}_A_rejected_{tier}.npy`, `{model}_H_next_cr_{tier}.npy`
- `parse_conversation()` uses regex `r'\n\nHuman: |\n\nAssistant: '` — reuse for both chosen and rejected fields

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | Copy-extend config.py/config.yaml from h-m2; update hypothesis_id, add delta-specific fields; create directory structure | **8/20** | 2+1+2+3 |
| A-2 | Extend data_loader | Copy-extend data_loader.py: add `parse_chosen_rejected_pairs()`, `split_chosen_rejected_by_tier()`; handle rejected field parsing; auto-demote logic for N_pairs | **12/20** | 3+2+3+4 |
| A-3 | Copy embedder + controls | Copy embedder.py and controls.py as-is from h-m2; verify n_jobs=1 and cache key naming; identify new h-m3 cache key templates | **6/20** | 2+1+1+2 |
| A-4 | Implement delta_probe | NEW module: 3 operationalizations (raw, length_matched, prompt_projected), `truncate_to_rejected_length()`, `project_out()`, `compute_all_deltas()`; FR-M3 logging | **16/20** | 4+3+5+4 |
| A-5 | Extend statistics | Copy-extend statistics.py: add `bootstrap_delta_ci()`, `ttest_delta()`, `cohens_d_onesample()`, `gate_evaluation_m3()`, `check_model_consistency_m3()`, `verify_mechanism_activated_m3()` | **14/20** | 4+3+4+3 |
| A-6 | Extend visualize | Copy-extend visualize.py: add 6 h-m3 figures (3 mandatory + 3 autonomous) | **12/20** | 4+2+3+3 |
| A-7 | Implement run_experiment | Rewrite run_experiment.py as h-m3 orchestrator: 3-model loop, chosen/rejected Δ pipeline, auto-demote check, gate evaluation, 6 figures, results JSON | **16/20** | 4+4+4+4 |
| A-8 | Embedding encode pass | Verify h-m2/h-m1 cache; encode A_chosen, A_rejected, H_next for all 3 models × 3 tiers; cache to h-m3/code/embeddings | **11/20** | 3+3+2+3 |
| A-9 | Unit tests | pytest for delta_probe (3 ops, project_out), statistics (bootstrap_delta_ci, gate_evaluation), data_loader (parse_chosen_rejected_pairs), visualize (figure output), run_experiment (mock run) | **12/20** | 3+3+2+4 |
| A-10 | Run full experiment | Execute run_experiment.py on full dataset (3 models × 3 tiers × 3 ops); collect delta_results.json | **10/20** | 2+3+2+3 |
| A-11 | Gate evaluation + reporting | Evaluate ops_passing >= 2, models_consistent >= 2, verify_mechanism_activated_m3(); save results JSON, generate 04_validation.md | **9/20** | 2+3+2+2 |

**Distribution**:
- VeryHigh (18-20): []
- High (14-17): [A-4, A-5, A-7]
- Medium (9-13): [A-2, A-6, A-8, A-9, A-10, A-11]
- Low (4-8): [A-1, A-3]
