# Architecture: H-M1 Semantic Similarity Analysis

**Applied**: Standard sentence-transformers bi-encoder pipeline (KB search returned no closer match; using brief's specified pattern).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: Actual code read directly (Serena had no active project matching this cwd; read via file tool instead — same effect, verified against implementation not spec).
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: `rm_scores.parquet` columns come from `data.py::prepare_battles` (`resp_a`, `resp_b`, plus original `response_a`/`response_b`) and `mode_classify.py::assign_modes` (`mode`: int, values 1-4). No `mode_distribution.json` per-battle mapping — mode filtering must be done directly on `rm_scores.parquet`'s `mode` column. `mode_distribution.json` only holds aggregate counts/proportions, not usable for filtering. `config.py` uses a flat `CONFIG` dict pattern — reused below.

---

## Module Structure

- `config.py` — flat CONFIG dict (h-e1 pattern)
- `data.py` — load + filter h-e1 outputs to Mode 1 / Mode 3
- `embed.py` — MiniLM encoder + disk cache
- `similarity.py` — cosine similarity per battle
- `stats_test.py` — Welch's t-test, Cohen's d, bootstrap CI
- `run.py` — pipeline orchestration

## Data Flow

1. `data.py` loads `h-e1/code/outputs/rm_scores.parquet`, filters `mode ∈ {1,3}`, validates n≥500/mode
2. `embed.py` encodes `resp_a`/`resp_b` columns → `embeddings.npz` (cached, skip if exists)
3. `similarity.py` computes cosine sim per row → `similarity_scores.parquet` (battle_id, mode, similarity)
4. `stats_test.py` splits by mode, runs Welch's t-test + Cohen's d + bootstrap CI → `statistical_results.json`

---

## Module Interfaces

### config.py

```python
CONFIG = {
    "h_e1_scores_path": "../../h-e1/code/outputs/rm_scores.parquet",
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "batch_size": 128,
    "output_dir": "outputs/",
    "embeddings_path": "outputs/embeddings.npz",
    "similarity_path": "outputs/similarity_scores.parquet",
    "stats_path": "outputs/statistical_results.json",
    "min_n_per_mode": 500,
    "modes": [1, 3],
    "bootstrap_n": 10000,
    "seed": 42,
}
```

### data.py (`code/data.py`)

**Dependencies**: config, pandas

```python
def load_mode_pairs(scores_path: str, modes: list[int]) -> pd.DataFrame:
    """Load rm_scores.parquet, filter to given modes, return
    columns: battle_id, resp_a, resp_b, mode."""

def validate_sample_size(df: pd.DataFrame, min_n: int) -> None:
    """Raise ValueError if any mode count < min_n."""
```

### embed.py (`code/embed.py`)

**Dependencies**: config, sentence_transformers, numpy

```python
def encode_responses(texts_a: list[str], texts_b: list[str],
                      model_name: str, batch_size: int) -> tuple[np.ndarray, np.ndarray]:
    """Encode both columns; returns (emb_a, emb_b), each (N, 384)."""

def save_embeddings(path: str, emb_a: np.ndarray, emb_b: np.ndarray) -> None: ...
def load_embeddings(path: str) -> tuple[np.ndarray, np.ndarray] | None:
    """Return None if cache file absent."""
```

### similarity.py (`code/similarity.py`)

**Dependencies**: numpy

```python
def cosine_similarity_pairs(emb_a: np.ndarray, emb_b: np.ndarray) -> np.ndarray:
    """Row-wise cosine similarity, returns (N,) array in [-1, 1]."""

def build_similarity_df(df: pd.DataFrame, similarities: np.ndarray) -> pd.DataFrame:
    """Attach similarity column to battle_id/mode df."""
```

### stats_test.py (`code/stats_test.py`)

**Dependencies**: scipy, numpy

```python
def cohen_d(x: np.ndarray, y: np.ndarray) -> float:
    """Pooled-SD Cohen's d (formula per brief)."""

def welch_ttest(x: np.ndarray, y: np.ndarray) -> dict:
    """Returns {t_statistic, p_value} via scipy.stats.ttest_ind(equal_var=False)."""

def bootstrap_ci_d(x: np.ndarray, y: np.ndarray, n_boot: int, seed: int) -> tuple[float, float]:
    """Bootstrap 95% CI for Cohen's d."""

def run_analysis(sim_df: pd.DataFrame, mode_a: int, mode_b: int, n_boot: int, seed: int) -> dict:
    """Full stats bundle -> matches statistical_results.json schema in brief."""
```

### run.py (`code/run.py`)

**Dependencies**: all modules above

```python
def main() -> None:
    """Load -> filter -> validate -> embed(or load cache) -> similarity ->
    stats -> write outputs/statistical_results.json."""
```

---

## External Dependencies (Base Hypothesis: h-e1)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| N/A (data reused, no code import) | Read directly via `pd.read_parquet(CONFIG["h_e1_scores_path"])` | `h-e1/code/outputs/rm_scores.parquet` |

No h-e1 Python modules are imported — only its output parquet is consumed (schema: `resp_a`, `resp_b`, `mode`). Verified from `h-e1/code/data.py` and `h-e1/code/mode_classify.py`.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Config + data loader | CONFIG dict, load_mode_pairs, validate_sample_size | 5 | 1+1+1+2 |
| M-2 | Embedding encoder | MiniLM encode + npz cache save/load | 8 | 2+2+2+2 |
| M-3 | Similarity calculator | Cosine sim, build similarity df | 4 | 1+1+1+1 |
| M-4 | Statistics module | cohen_d, welch_ttest, bootstrap_ci_d | 9 | 2+2+3+2 |
| M-5 | Pipeline orchestration (run.py) | Wire all modules, write JSON output | 6 | 2+1+2+1 |
| M-6 | End-to-end smoke test | Run on small subset, validate schema of outputs | 5 | 1+1+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-4], Low(4-8): [M-1, M-2, M-3, M-5, M-6]
