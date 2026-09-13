# Architecture: h-m1 — Tier-Monotonic Semantic Accommodation

**Hypothesis:** h-m1
**Type:** MECHANISM
**Date:** 2026-03-14
**Prerequisite:** h-e1 (VALIDATED — C_sem=0.3292, MUST_WORK PASS)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending h-e1)
**Status**: Serena activation failed (no active project session). Direct file reads performed on all 7 h-e1 source files — full symbol analysis completed via Read tool as equivalent.
**Analyzed Path**: `docs/youra_research/20260315_bi_align/h-e1/code/`
**Findings**: 7 modules confirmed. Key symbols verified from actual code (not specs):
- `data_loader.py`: `load_all_splits(cache_dir)`, `extract_pairs(conversations)`, `parse_conversation(chosen)`, `compute_jaccard()`, `compute_token_count()`. Returns flat list of dicts; `extract_pairs` returns dict with keys `h_next, a_actual, h_prompt, token_counts, jaccard_overlaps`.
- `embedder.py`: `class Embedder` with `__init__(model_name, cache_dir)`, `encode(texts, cache_key)`, `load_cache(cache_key)`, `save_cache(embeddings, cache_key)`. Cache key pattern: `{prefix}_{model_slug}_{n_pairs}`.
- `controls.py`: `build_random_control(ai_embeddings, seed=42)`, `build_topic_control(prompt_embeddings, ai_embeddings, k=5)`. KNN uses `n_jobs=1` (critical).
- `accommodation.py`: `compute_cosine_similarities(h_next, a_actual, a_topic, a_random)`, `residualize(cos_array, covariate)`, `compute_c_sem(cos_actual, cos_random)`, `apply_residualization(cos_dict, token_counts, jaccard_overlaps)`.
- `statistics.py`: `bootstrap_c_sem()`, `bootstrap_cohen_d()`, `mann_whitney_test()`, `run_all_tests()`, `verify_mechanism_activated(results, embeddings_computed)`. Note: actual signature takes `embeddings_computed` as second arg (differs from spec).
- `visualize.py`: 6 plot functions — `plot_gate_metrics`, `plot_partner_specificity`, `plot_bootstrap_dist`, `plot_cosine_distributions`, `plot_residualization_check`, `plot_knn_quality`. All save to `figures_dir` passed as arg.
- `run_experiment.py`: `run_experiment(config: dict)`, `run_robustness_checks(base_config: dict)`, `main()`. Config dict pattern: `{cache_dir, model_name, output_dir, n_samples}`. Uses local imports (no package prefix).

---

## External Dependencies

### Module Paths (From Actual h-e1 Code)

h-m1 copies and extends h-e1 modules to `h-m1/code/`. Import style is local (no package prefix) as verified in `run_experiment.py` lines 17-29:

| Module | Import in h-m1 | Source File |
|--------|----------------|-------------|
| load_all_splits, extract_pairs | `from data_loader import load_all_splits, extract_pairs` | `h-e1/code/data_loader.py` → copy-extend |
| Embedder | `from embedder import Embedder` | `h-e1/code/embedder.py` → copy-extend |
| build_random_control, build_topic_control | `from controls import build_random_control, build_topic_control` | `h-e1/code/controls.py` → reuse as-is |
| compute_cosine_similarities, compute_c_sem, apply_residualization | `from accommodation import compute_cosine_similarities, compute_c_sem, apply_residualization` | `h-e1/code/accommodation.py` → copy-extend |
| bootstrap_c_sem, bootstrap_cohen_d, mann_whitney_test, run_all_tests, verify_mechanism_activated | `from statistics import ...` | `h-e1/code/statistics.py` → copy-extend |
| plot functions | `from visualize import ...` | `h-e1/code/visualize.py` → copy-extend |

**Verified from**: direct file reads of all 7 files in `h-e1/code/` (actual implementation).

**Critical facts from actual code (NOT specs):**
- `verify_mechanism_activated(results, embeddings_computed)` — takes 2 args, not 1
- `run_experiment(config: dict)` — takes config dict, not named kwargs
- `run_robustness_checks(base_config: dict)` — sequential loop over `ROBUSTNESS_MODELS`
- Cache key uses suffix pattern: `f"{prefix}_{model_slug}_{n_pairs}"` — extend to `f"{prefix}_{model_slug}_{tier}_{n_pairs}"`
- All visualize functions take `figures_dir` as positional arg (not keyword `output_dir`)

---

## Architecture Overview

h-m1 extends the h-e1 7-module pipeline with:
1. Per-tier data splitting (3 RLHF tiers loaded separately)
2. Multi-model loop (3 SBERT models × 3 tiers = 9 embedding sets)
3. Jonckheere-Terpstra monotonicity test + Bonferroni-corrected pairwise Mann-Whitney
4. KS test + IPW robustness check
5. 7 tier-comparison visualization types
6. New orchestrator with nested model × tier loop

All new h-m1 code lives in `h-m1/code/`. No cross-directory imports.

---

## Module Structure

### DataLoader (`code/data_loader.py`)

**Base**: h-e1 `data_loader.py` — copy and extend
**Dependencies**: datasets, re

```python
SPLITS = [
    ("helpful-base", "train"),
    ("helpful-rejection-sampled", "train"),
    ("helpful-online", "train"),
]
TIER_NAMES = ["helpful-base", "helpful-rejection-sampled", "helpful-online"]

def load_all_splits(cache_dir: str) -> list[dict]: ...  # unchanged from h-e1

def parse_conversation(chosen: str) -> list[str]: ...  # unchanged from h-e1

def compute_jaccard(s1: str, s2: str) -> float: ...  # unchanged

def compute_token_count(text: str) -> int: ...  # unchanged

def extract_pairs(conversations: list[dict]) -> dict: ...  # unchanged from h-e1

def split_by_tier(cache_dir: str) -> dict[str, dict]:
    """Load each tier separately and extract pairs.

    Returns:
        {tier_name: {h_next, a_actual, h_prompt, token_counts, jaccard_overlaps}}
        Each inner dict value is a list of length N_pairs_for_tier.
    Gate: assert len(pairs) >= 1000 per tier.
    """
    ...
```

---

### Embedder (`code/embedder.py`)

**Base**: h-e1 `embedder.py` — copy and extend
**Dependencies**: sentence_transformers, numpy, os

```python
class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: str = "embeddings"): ...
    def encode(self, texts: list[str], cache_key: str) -> np.ndarray: ...
    def load_cache(self, cache_key: str) -> np.ndarray | None: ...
    def save_cache(self, embeddings: np.ndarray, cache_key: str) -> None: ...
    def encode_tier(self, texts: list[str], prefix: str, tier: str, n_pairs: int) -> np.ndarray:
        """Tier-aware encoding with cache key: {prefix}_{model_slug}_{tier}_{n_pairs}.

        Wraps encode() with tier-namespaced cache key.
        """
        ...
```

---

### Controls (`code/controls.py`)

**Base**: h-e1 `controls.py` — reuse as-is (no changes)
**Dependencies**: numpy, sklearn.neighbors

```python
def build_random_control(ai_embeddings: np.ndarray, seed: int = 42) -> np.ndarray: ...
def build_topic_control(
    prompt_embeddings: np.ndarray,
    ai_embeddings: np.ndarray,
    k: int = 5,
) -> np.ndarray: ...
```

---

### Accommodation (`code/accommodation.py`)

**Base**: h-e1 `accommodation.py` — copy and extend
**Dependencies**: numpy, statsmodels.api

```python
def compute_cosine_similarities(
    h_next: np.ndarray, a_actual: np.ndarray,
    a_topic: np.ndarray, a_random: np.ndarray,
) -> dict: ...  # unchanged

def residualize(cos_array: np.ndarray, covariate: np.ndarray) -> np.ndarray: ...  # unchanged

def compute_c_sem(cos_actual: np.ndarray, cos_random: np.ndarray) -> float: ...  # unchanged

def apply_residualization(
    cos_dict: dict, token_counts: list[int], jaccard_overlaps: list[float],
) -> dict: ...  # unchanged

def compute_tier_csem_matrix(
    tier_pairs: dict[str, dict],
    embedder: object,
    controls_fn_random: callable,
    controls_fn_topic: callable,
    seed: int = 42,
) -> dict[str, dict]:
    """Compute C_sem for all tiers for a single model.

    Args:
        tier_pairs: {tier_name: {h_next, a_actual, h_prompt, token_counts, jaccard_overlaps}}
        embedder: Embedder instance (already initialized with model)
        controls_fn_random: build_random_control
        controls_fn_topic: build_topic_control
    Returns:
        {tier_name: {c_sem, cos_actual_mean, cos_random_mean, cos_topic_mean,
                     raw_cos_actual, raw_cos_random, raw_cos_topic, n_pairs}}
    """
    ...
```

---

### Statistics (`code/statistics.py`)

**Base**: h-e1 `statistics.py` — copy and extend
**Dependencies**: numpy, scipy.stats

```python
MIN_N_PAIRS = 1000
BONFERRONI_ALPHA = 0.05 / 3  # = 0.0167

def bootstrap_c_sem(
    cos_actual: np.ndarray, cos_random: np.ndarray,
    n_bootstrap: int = 1000, seed: int = 42,
) -> tuple[float, np.ndarray]: ...  # unchanged

def bootstrap_cohen_d(
    arr_a: np.ndarray, arr_b: np.ndarray,
    n_bootstrap: int = 1000, seed: int = 42,
) -> tuple[float, np.ndarray]: ...  # unchanged

def mann_whitney_test(arr_a: np.ndarray, arr_b: np.ndarray) -> dict: ...  # unchanged

def run_all_tests(
    cos_actual: np.ndarray, cos_topic: np.ndarray,
    cos_random: np.ndarray, n_pairs: int,
) -> dict: ...  # unchanged

def verify_mechanism_activated(results: dict, embeddings_computed: bool) -> tuple[bool, dict]: ...  # unchanged

def jonckheere_terpstra_test(
    tier_results: dict[str, dict],
    tier_order: list[str],
) -> dict:
    """Jonckheere-Terpstra monotonicity test on raw cosine arrays.

    Args:
        tier_results: {tier_name: {raw_cos_actual: np.ndarray, ...}}
        tier_order: ['helpful-base', 'helpful-rejection-sampled', 'helpful-online']
    Returns:
        {'jt_statistic': float, 'jt_pvalue': float}
    Uses: scipy.stats.jonckheere_terpstra(*ordered_cos, alternative='increasing')
    """
    ...

def bonferroni_mannwhitney(
    tier_results: dict[str, dict],
    tier_order: list[str],
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> dict:
    """Pairwise Mann-Whitney U + Bonferroni correction + bootstrap Cohen's d.

    Pairs: (T1,T2), (T2,T3), (T1,T3). Threshold: alpha/3 = 0.0167.
    Returns:
        {pair_key: {'mw_statistic', 'mw_pvalue', 'bonferroni_significant',
                    'cohen_d', 'cohen_d_ci'}}
    """
    ...

def ks_test_tier_distributions(
    tier_prompt_embeddings: dict[str, np.ndarray],
    tier_order: list[str],
) -> dict:
    """KS test on prompt embedding distributions across tier pairs.

    Args:
        tier_prompt_embeddings: {tier_name: np.ndarray shape (N, D)}
        tier_order: ordered list of tier names
    Returns:
        {pair_key: {'ks_statistic': float, 'ks_pvalue': float, 'ipw_triggered': bool}}
    Uses: scipy.stats.ks_2samp on flattened embeddings (or first PCA component).
    """
    ...

def compute_ipw_csem(
    tier_results: dict[str, dict],
    tier_prompt_embeddings: dict[str, np.ndarray],
) -> dict[str, float]:
    """Recompute C_sem with inverse-probability weighting.

    Only called if any KS p < 0.05.
    Returns: {tier_name: ipw_c_sem}
    """
    ...

def check_model_consistency(
    all_model_results: dict[str, dict],
    jt_alpha: float = 0.05,
    d_threshold: float = 0.1,
) -> dict:
    """Count models satisfying J-T p < alpha AND max tier Cohen's d >= threshold.

    Returns:
        {'consistent_count': int, 'consistent_models': list[str],
         'gate_passed': bool}  # gate_passed = consistent_count >= 2
    """
    ...

def verify_mechanism_activated_m1(
    all_model_results: dict,
    experiment_log: str,
) -> tuple[bool, dict]:
    """5-indicator mechanism activation check for h-m1.

    Indicators: tier_logs_found, all_tiers_have_pairs,
                csem_differs_across_tiers, jt_computed, all_models_ran
    """
    ...
```

---

### Visualize (`code/visualize.py`)

**Base**: h-e1 `visualize.py` — copy and extend
**Dependencies**: matplotlib, seaborn, numpy, scipy.stats

```python
# h-e1 functions preserved unchanged:
def plot_gate_metrics(results: dict, figures_dir: str) -> None: ...
def plot_partner_specificity(results: dict, figures_dir: str) -> None: ...
def plot_bootstrap_dist(bootstrap_samples: np.ndarray, figures_dir: str) -> None: ...
def plot_cosine_distributions(
    cos_actual: np.ndarray, cos_topic: np.ndarray,
    cos_random: np.ndarray, figures_dir: str,
) -> None: ...
def plot_residualization_check(
    cos_dict_before: dict, cos_dict_after: dict, figures_dir: str,
) -> None: ...
def plot_knn_quality(prompt_embeddings: np.ndarray, figures_dir: str) -> None: ...

# New tier-comparison functions:
def plot_tier_csem_bars(
    all_model_results: dict[str, dict],
    figures_dir: str,
) -> None:
    """FR-V1: Bar chart of C_sem per tier for each SBERT model.

    3 subplots (one per model), error bars = bootstrap 95% CI,
    annotated with J-T p-value. Saves: tier_csem_bars.png
    """
    ...

def plot_tier_monotonicity_lines(
    all_model_results: dict[str, dict],
    figures_dir: str,
) -> None:
    """FR-V2: Line plot C_sem(T1/T2/T3) across 3 models.

    Saves: tier_monotonicity_lines.png
    """
    ...

def plot_cohend_heatmap(
    pairwise_results: dict[str, dict],
    figures_dir: str,
) -> None:
    """FR-V3: Heatmap of Cohen's d for tier pairs × models.

    Saves: cohend_heatmap.png
    """
    ...

def plot_tier_violin(
    tier_results: dict[str, dict],
    primary_model: str,
    figures_dir: str,
) -> None:
    """FR-V4: Violin plot of raw cosine distributions per tier (primary model).

    Saves: tier_violin.png
    """
    ...

def plot_bootstrap_kde_tiers(
    tier_results: dict[str, dict],
    primary_model: str,
    figures_dir: str,
) -> None:
    """FR-V5: KDE of bootstrap C_sem replicates per tier × primary model.

    Saves: bootstrap_kde_tiers.png
    """
    ...

def plot_ipw_comparison(
    raw_csem: dict[str, float],
    ipw_csem: dict[str, float],
    figures_dir: str,
) -> None:
    """FR-V6 (conditional): Raw vs IPW-weighted C_sem per tier.

    Only called if KS test triggered IPW.
    Saves: ipw_comparison.png
    """
    ...

def plot_ks_summary(
    ks_results: dict[str, dict],
    figures_dir: str,
) -> None:
    """FR-V7: Bar chart of KS statistics and p-values for tier-pair comparisons.

    Saves: ks_summary.png
    """
    ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Base**: h-e1 `run_experiment.py` — new orchestrator (full rewrite)
**Dependencies**: data_loader, embedder, controls, accommodation, statistics, visualize, numpy, json, logging, yaml, argparse, time

```python
HYPOTHESIS_ID = "h-m1"
TIER_ORDER = ["helpful-base", "helpful-rejection-sampled", "helpful-online"]
TIER_SLUGS = {"helpful-base": "base", "helpful-rejection-sampled": "rs", "helpful-online": "online"}
MODEL_CONFIGS = [
    {"name": "all-MiniLM-L6-v2", "slug": "minilm", "role": "primary"},
    {"name": "paraphrase-MiniLM-L6-v2", "slug": "paraphrase", "role": "robustness1"},
    {"name": "all-mpnet-base-v2", "slug": "mpnet", "role": "robustness2"},
]

@dataclass
class TierModelResult:
    model_slug: str
    tier: str
    c_sem: float
    c_sem_ci: list[float]
    cos_actual_mean: float
    cos_random_mean: float
    cos_topic_mean: float
    n_pairs: int
    jt_statistic: float
    jt_pvalue: float
    pairwise_mw: dict
    gate_passed: bool

def _setup_logging(output_dir: str) -> logging.Logger: ...  # same pattern as h-e1

def run_single_model(
    model_cfg: dict,
    tier_pairs: dict[str, dict],
    output_dir: str,
    dry_run: bool = False,
) -> dict:
    """Run full pipeline for one SBERT model across all 3 tiers.

    Steps:
    1. Init Embedder with model_cfg['name']
    2. For each tier: encode h_next, a_actual, h_prompt (tier-aware cache key)
    3. build_random_control + build_topic_control per tier
    4. compute_tier_csem_matrix
    5. jonckheere_terpstra_test + bonferroni_mannwhitney
    6. bootstrap CI per tier
    Returns: model-level results dict with all tier metrics
    """
    ...

def run_experiment(config: dict) -> dict:
    """Main orchestrator: 3-model × 3-tier nested loop.

    config keys: cache_dir, output_dir, n_samples_dry_run, dry_run
    Steps:
    1. split_by_tier(cache_dir) → tier_pairs
    2. ks_test_tier_distributions → compute IPW if triggered
    3. For each model in MODEL_CONFIGS: run_single_model
    4. check_model_consistency across models
    5. verify_mechanism_activated_m1
    6. tier_comparison_plots (all 7 figure types)
    7. Write results.yaml + gate evaluation
    Returns: all_model_results dict
    """
    ...

def write_results_yaml(all_results: dict, gate: dict, output_dir: str) -> None:
    """Write metrics to results.yaml (FR-E4)."""
    ...

def evaluate_gate(all_model_results: dict) -> dict:
    """FR-G1: Check J-T p < 0.05 AND d >= 0.1 in >= 2/3 models.

    Returns: {'gate_passed': bool, 'consistent_count': int, 'details': dict}
    """
    ...

def main() -> None: ...  # argparse: --cache-dir, --output-dir, --dry-run, --n-samples
```

---

## File Organization

```
h-m1/code/
├── data_loader.py       # h-e1 base + split_by_tier()
├── embedder.py          # h-e1 base + encode_tier()
├── controls.py          # h-e1 reuse as-is
├── accommodation.py     # h-e1 base + compute_tier_csem_matrix()
├── statistics.py        # h-e1 base + jonckheere_terpstra_test(),
│                        #   bonferroni_mannwhitney(), ks_test_tier_distributions(),
│                        #   compute_ipw_csem(), check_model_consistency(),
│                        #   verify_mechanism_activated_m1()
├── visualize.py         # h-e1 base + 7 tier_comparison_plots functions
└── run_experiment.py    # New orchestrator (3-model × 3-tier loop)

h-m1/
├── figures/             # All plot outputs (auto-created)
├── embeddings/          # .npy cache per model×tier (auto-created)
├── results.yaml         # FR-E4 metrics output
└── 04_validation.md     # FR-E5 gate report (generated post-run)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Per-Tier Data Loading | Extend data_loader.py: add split_by_tier() loading 3 tiers separately via load_dataset(data_dir=tier), extract pairs per tier, gate n_pairs >= 1000 per tier | 10 | 3+2+3+2 |
| A-2 | Tier-Aware Embedder | Extend embedder.py: add encode_tier() with cache key {prefix}_{model_slug}_{tier}_{n_pairs}; validate no stale cache cross-tier | 8 | 2+2+2+2 |
| A-3 | Tier C_sem Matrix | Extend accommodation.py: add compute_tier_csem_matrix() running per-tier encode + controls + cosine + C_sem for one model | 12 | 3+3+3+3 |
| A-4 | Jonckheere-Terpstra + Bonferroni | Extend statistics.py: add jonckheere_terpstra_test() (scipy.stats.jonckheere_terpstra), bonferroni_mannwhitney() (3 pairs, alpha/3=0.0167), bootstrap Cohen's d per pair | 14 | 3+3+5+3 |
| A-5 | KS Test + IPW Robustness | Extend statistics.py: add ks_test_tier_distributions() + compute_ipw_csem(); check_model_consistency(); verify_mechanism_activated_m1() | 13 | 3+3+4+3 |
| A-6 | Tier Visualization Suite | Extend visualize.py: add 7 new plot functions (tier_csem_bars, monotonicity_lines, cohend_heatmap, tier_violin, bootstrap_kde_tiers, ipw_comparison, ks_summary) | 14 | 4+2+4+4 |
| A-7 | Multi-Model Orchestrator | New run_experiment.py: 3-model × 3-tier nested loop, dry-run mode (n=1500), gate evaluation, results.yaml output, 04_validation.md generation | 16 | 4+3+5+4 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4, A-6, A-7], Medium(9-13): [A-1, A-3, A-5], Low(4-8): [A-2]

---

## Applied Patterns

Applied: per_tier_stratified_pipeline — load each data split independently, extract pairs per tier, maintain tier label through entire pipeline to prevent cross-tier contamination
Applied: tier_aware_cache_key — cache key includes tier name ({model_slug}_{tier}_{n_pairs}) to prevent stale cache hits when running same model on different tier subsets
Applied: nested_multi_model_loop — outer loop over SBERT models, inner loop over tiers; collect all results before gate evaluation for consistency check across >= 2/3 models
Applied: knn_n_jobs_1_constraint — NearestNeighbors(n_jobs=1) enforced in controls.py; critical bug fix inherited from h-e1 (OpenBLAS double-free on 155k scale with n_jobs=-1)
Applied: raw_cosine_stats_not_residuals — all statistical tests (J-T, Mann-Whitney) operate on raw cosine arrays; residualization only for robustness reporting (residuals have zero mean by construction)
