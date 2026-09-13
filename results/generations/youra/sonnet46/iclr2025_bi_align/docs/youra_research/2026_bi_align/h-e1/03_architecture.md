# Architecture: h-e1 — Semantic Accommodation Existence (EXISTENCE PoC)

**Hypothesis:** h-e1
**Type:** EXISTENCE (PoC)
**Date:** 2026-03-15
**Applied:** HuggingFace datasets load pattern; SBERT batch encoding pattern (Archon KB — low domain match, standard API patterns applied from PRD/brief specs)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base hypothesis code exists. All modules designed from PRD and experiment brief specifications.

---

## File Structure

```
h-e1/code/
├── data_loader.py       # Load HH-RLHF splits, parse turns, compute lexical features
├── embedder.py          # SBERT encoding with disk caching
├── controls.py          # Random shuffle + KNN topic-matched control construction
├── accommodation.py     # C_sem computation + OLS residualization
├── statistics.py        # Bootstrap CI, Mann-Whitney U, Cohen's d, verify_mechanism_activated
├── visualize.py         # Gate metrics bar chart + 5 additional figures
└── run_experiment.py    # Main orchestration
```

Output directories (auto-created by run_experiment.py):
- `h-e1/embeddings/` — cached .npy embedding arrays
- `h-e1/figures/` — all visualization outputs
- `h-e1/results.json` — final experiment results

---

## Module Definitions

### DataLoader (`code/data_loader.py`)

**Dependencies**: datasets, numpy, tqdm

```python
SPLITS = ["helpful-base", "helpful-rejection-sampled", "helpful-online"]

def load_all_splits(cache_dir: str | None = None) -> list[dict]:
    """Load and pool all 3 helpfulness splits. Returns list of conversation dicts."""
    ...

def parse_conversation(chosen: str) -> list[str]:
    """Split chosen string on \\n\\nHuman: / \\n\\nAssistant: markers. Returns alternating turns."""
    ...

def extract_pairs(conversations: list[list[str]]) -> dict:
    """
    Extract (H_next, A_actual, H_prompt) triples from parsed conversations.
    Filters: min 2 turns, non-empty turns.
    Returns dict with keys: h_next, a_actual, h_prompt, token_counts, jaccard_overlaps
    Each value is a list of length N_pairs.
    """
    ...

def compute_jaccard(s1: str, s2: str) -> float:
    """Token-level Jaccard overlap for lexical residualization."""
    ...

def compute_token_count(text: str) -> int:
    """Whitespace-split token count for length residualization."""
    ...
```

---

### Embedder (`code/embedder.py`)

**Dependencies**: sentence_transformers, numpy, os, tqdm

```python
DEFAULT_MODEL = "all-MiniLM-L6-v2"
EMBED_DIM = 384
BATCH_SIZE = 256

class Embedder:
    def __init__(self, model_name: str = DEFAULT_MODEL, cache_dir: str = "embeddings"): ...

    def encode(self, texts: list[str], cache_key: str) -> np.ndarray:
        """
        Encode texts with normalize_embeddings=True, batch_size=256.
        Load from {cache_dir}/{cache_key}.npy if exists; else encode and save.
        Returns (N, 384) float32 array.
        """
        ...

    def load_cache(self, cache_key: str) -> np.ndarray | None: ...
    def save_cache(self, embeddings: np.ndarray, cache_key: str) -> None: ...
```

---

### Controls (`code/controls.py`)

**Dependencies**: numpy, sklearn.neighbors

```python
SEED = 42
KNN_K = 5

def build_random_control(
    ai_embeddings: np.ndarray,
    seed: int = SEED
) -> np.ndarray:
    """
    Shuffle ai_embeddings indices with seed=42.
    Returns (N, D) array of shuffled AI embeddings as A_random.
    """
    ...

def build_topic_control(
    prompt_embeddings: np.ndarray,
    ai_embeddings: np.ndarray,
    k: int = KNN_K
) -> np.ndarray:
    """
    Fit NearestNeighbors(n_neighbors=k+1, metric='cosine') on prompt_embeddings.
    For each row, retrieve K nearest from OTHER conversations (exclude self index).
    Return mean embedding of K matched AI turns as A_topic_matched.
    Returns (N, D) float32 array.
    """
    ...
```

---

### Accommodation (`code/accommodation.py`)

**Dependencies**: numpy, statsmodels.api

```python
def compute_cosine_similarities(
    h_next: np.ndarray,
    a_actual: np.ndarray,
    a_topic: np.ndarray,
    a_random: np.ndarray
) -> dict:
    """
    Compute elementwise dot products (embeddings are L2-normalized).
    Returns dict: {cos_actual, cos_topic, cos_random} each shape (N,).
    """
    ...

def residualize(
    cos_array: np.ndarray,
    covariate: np.ndarray
) -> np.ndarray:
    """
    OLS regression: cos_array ~ covariate.
    Returns residuals (N,) as float32.
    """
    ...

def compute_c_sem(
    cos_actual: np.ndarray,
    cos_random: np.ndarray
) -> float:
    """C_sem = cos_actual.mean() - cos_random.mean()"""
    ...

def apply_residualization(
    cos_dict: dict,
    token_counts: np.ndarray,
    jaccard_overlaps: np.ndarray
) -> dict:
    """
    Apply length then lexical overlap residualization to each cos array.
    Returns updated dict with residualized arrays.
    """
    ...
```

---

### Statistics (`code/statistics.py`)

**Dependencies**: numpy, scipy.stats

```python
BOOTSTRAP_N = 1000
SEED = 42
MIN_N_PAIRS = 1000
ALPHA = 0.05

def bootstrap_c_sem(
    cos_actual: np.ndarray,
    cos_random: np.ndarray,
    n_bootstrap: int = BOOTSTRAP_N,
    seed: int = SEED
) -> tuple[float, np.ndarray]:
    """
    Bootstrap CI for C_sem.
    Returns (c_sem_mean, [ci_lower, ci_upper]) at 95% percentile.
    """
    ...

def bootstrap_cohen_d(
    a: np.ndarray,
    b: np.ndarray,
    n_bootstrap: int = BOOTSTRAP_N,
    seed: int = SEED
) -> tuple[float, np.ndarray]:
    """
    Bootstrap Cohen's d: pooled-std formula.
    Returns (d_mean, [ci_lower, ci_upper]).
    """
    ...

def mann_whitney_test(
    a: np.ndarray,
    b: np.ndarray,
    alternative: str = "greater"
) -> tuple[float, float]:
    """
    scipy.stats.mannwhitneyu wrapper.
    Returns (statistic, p_value).
    """
    ...

def verify_mechanism_activated(results: dict) -> tuple[bool, dict]:
    """
    Check all gate indicators.
    Indicators: embeddings_computed, c_sem_positive, ci_lower_positive,
                ordering_holds, sufficient_pairs.
    Returns (passed: bool, indicators: dict).
    """
    ...

def run_all_tests(
    cos_actual: np.ndarray,
    cos_topic: np.ndarray,
    cos_random: np.ndarray,
    n_pairs: int
) -> dict:
    """
    Run bootstrap CI, all Mann-Whitney U tests, and Cohen's d for each pair contrast.
    Returns full results dict for results.json.
    """
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: matplotlib, numpy

```python
FIGURES_DIR = "figures"

def plot_gate_metrics(results: dict, output_dir: str = FIGURES_DIR) -> None:
    """
    Bar chart: C_sem with 95% CI + three bars for cos_actual/cos_topic/cos_random
    with error bars. Saves to figures/gate_metrics.png.
    """
    ...

def plot_partner_specificity_gradient(results: dict, output_dir: str = FIGURES_DIR) -> None:
    """Line plot with error bars, Cohen's d annotations between levels."""
    ...

def plot_bootstrap_distribution(bootstrap_samples: np.ndarray, ci: np.ndarray, output_dir: str = FIGURES_DIR) -> None:
    """Histogram of bootstrap C_sem with 95% CI shading and zero-line reference."""
    ...

def plot_cosine_distributions(
    cos_actual: np.ndarray,
    cos_topic: np.ndarray,
    cos_random: np.ndarray,
    output_dir: str = FIGURES_DIR
) -> None:
    """Violin/box plots comparing three control levels."""
    ...

def plot_residualization_check(
    cos_raw: np.ndarray,
    cos_residualized: np.ndarray,
    label: str,
    output_dir: str = FIGURES_DIR
) -> None:
    """Scatter: raw vs residualized cosine similarities."""
    ...

def plot_knn_quality(knn_distances: np.ndarray, output_dir: str = FIGURES_DIR) -> None:
    """Distribution of cosine distances to K=5 nearest prompt neighbors."""
    ...

def save_all_figures(results: dict, output_dir: str = FIGURES_DIR) -> None:
    """Call all plot functions in sequence."""
    ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: data_loader, embedder, controls, accommodation, statistics, visualize, json, logging, os

```python
HYPOTHESIS_DIR = "."  # h-e1/ root
RESULTS_PATH = "results.json"

def setup_dirs(hypothesis_dir: str) -> None:
    """Create embeddings/ and figures/ directories if not exist."""
    ...

def run_experiment(model_name: str = "all-MiniLM-L6-v2") -> dict:
    """
    Orchestration:
    1. setup_dirs
    2. load_all_splits → extract_pairs
    3. Embedder.encode (h_next, a_actual, h_prompt) with cache
    4. build_random_control + build_topic_control
    5. compute_cosine_similarities → apply_residualization
    6. run_all_tests → verify_mechanism_activated
    7. save_all_figures
    8. write results.json
    Returns results dict.
    """
    ...

def run_robustness_checks() -> dict:
    """
    Run run_experiment for paraphrase-MiniLM-L6-v2 and all-mpnet-base-v2.
    Returns dict of model_name -> results.
    """
    ...

if __name__ == "__main__":
    results = run_experiment()
    run_robustness_checks()
```

---

## Module Dependencies

```
run_experiment.py
  ├── data_loader.py
  ├── embedder.py
  ├── controls.py          ← embedder outputs
  ├── accommodation.py     ← embedder + controls outputs + data_loader features
  ├── statistics.py        ← accommodation outputs
  └── visualize.py         ← statistics + accommodation outputs
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Loading & Parsing | Implement data_loader.py: load 3 HH-RLHF splits, parse conversations, extract (H_next, A_actual, H_prompt) triples, compute token counts and Jaccard overlaps | 12 | 3+2+3+4 |
| A-2 | Embedding Generation | Implement embedder.py: SentenceTransformer batch encoding with disk cache (load/save .npy), cache-key logic for 3 text arrays | 10 | 2+2+3+3 |
| A-3 | Control Construction | Implement controls.py: random shuffle baseline + KNN K=5 topic-matched control with self-exclusion, mean embedding aggregation | 13 | 3+2+4+4 |
| A-4 | C_sem & Residualization | Implement accommodation.py: elementwise dot products, OLS residualization (length + lexical), C_sem scalar | 11 | 3+2+4+2 |
| A-5 | Statistical Testing | Implement statistics.py: bootstrap CI for C_sem, Mann-Whitney U (2 pairwise), bootstrap Cohen's d, verify_mechanism_activated | 15 | 4+2+5+4 |
| A-6 | Visualization & Orchestration | Implement visualize.py (6 figures) + run_experiment.py (orchestration, logging, results.json, robustness checks) | 14 | 4+3+3+4 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5, A-6], Medium(9-13): [A-1, A-2, A-3, A-4], Low(4-8): []

---

## Configuration Constants (Inline — No Separate config.py)

```python
# Shared across modules
SEED = 42
KNN_K = 5
BOOTSTRAP_N = 1000
BATCH_SIZE = 256
EMBED_DIM = 384
MIN_N_PAIRS = 1000
SIGNIFICANCE_LEVEL = 0.05
COHEN_D_THRESHOLD = 0.1
DEFAULT_MODEL = "all-MiniLM-L6-v2"
ROBUSTNESS_MODELS = ["paraphrase-MiniLM-L6-v2", "all-mpnet-base-v2"]
SPLITS = ["helpful-base", "helpful-rejection-sampled", "helpful-online"]
```

---

## External Dependencies

| Package | Version | Usage |
|---------|---------|-------|
| sentence-transformers | >=2.2.0 | SBERT encoding |
| datasets | >=2.0.0 | HH-RLHF loading |
| scipy | >=1.7.0 | mannwhitneyu |
| scikit-learn | >=1.0.0 | NearestNeighbors |
| numpy | >=1.21.0 | array ops, bootstrap |
| matplotlib | >=3.4.0 | figures |
| statsmodels | >=0.13.0 | OLS residualization |
| tqdm | >=4.62.0 | progress bars |
