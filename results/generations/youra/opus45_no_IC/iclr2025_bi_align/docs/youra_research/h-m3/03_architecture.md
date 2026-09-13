# Architecture: H-M3 — Lower Delta Signals Accommodation

**Type:** MECHANISM (statistical analysis, no ML training)
**Applied:** No matching KB pattern found (KB results were diffusion-model repos, not relevant) — standard scipy/numpy statistical pipeline used instead.

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field — no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch. Optionally reuse cached formality scores from H-M2 output directory if present (`h-m2/cache/formality_scores.parquet`), else recompute.

---

## Module Structure

### data_loader.py (`h-m3/code/data_loader.py`)

**Dependencies:** datasets (HF)

```python
def load_conversations(split: str = "train+test") -> list[dict]: ...
def filter_multiturn(conversations: list[dict], min_turns: int = 2) -> list[dict]: ...
def extract_turn_pairs(conversations: list[dict]) -> list[dict]:
    # returns list of {conversation_id, turn_idx, human_text, ai_text, has_next_turn}
    ...
```

### formality_scorer.py (`h-m3/code/formality_scorer.py`)

**Dependencies:** transformers, torch, data_loader

```python
class FormalityScorer:
    def __init__(self, model_name: str = "s-nlp/deberta-large-formality-ranker", device: str = "cuda"): ...
    def score_batch(self, texts: list[str], batch_size: int = 32) -> list[float]: ...
    def load_cache(self, cache_path: str) -> dict | None: ...
    def save_cache(self, scores: dict, cache_path: str) -> None: ...
```

### delta_analysis.py (`h-m3/code/delta_analysis.py`)

**Dependencies:** numpy

```python
def compute_formality_delta(human_formality: float, ai_formality: float) -> float: ...
def label_continuation(turn_pairs: list[dict]) -> np.ndarray: ...
def build_analysis_frame(turn_pairs: list[dict], human_scores: list[float],
                          ai_scores: list[float]) -> "pd.DataFrame":
    # columns: conversation_id, delta, continuation
    ...
```

### tercile_stats.py (`h-m3/code/tercile_stats.py`)

**Dependencies:** numpy, scipy.stats

```python
def tercile_continuation_analysis(deltas: np.ndarray, continuations: np.ndarray,
                                   conversation_ids: np.ndarray) -> dict: ...
def cluster_bootstrap_pvalue(deltas: np.ndarray, continuations: np.ndarray,
                              conversation_ids: np.ndarray, n_boot: int = 2000,
                              seed: int = 42) -> tuple[float, np.ndarray]:
    # returns (p_robust, bootstrap_rho_distribution)
    ...
def verify_mechanism(tercile_rates: dict) -> dict: ...
```

### visualize.py (`h-m3/code/visualize.py`)

**Dependencies:** matplotlib, tercile_stats

```python
def plot_tercile_bar_chart(tercile_rates: dict, out_path: str) -> None: ...       # MANDATORY gate figure
def plot_delta_histogram(deltas: np.ndarray, t1: float, t2: float, out_path: str) -> None: ...
def plot_delta_vs_continuation_scatter(deltas: np.ndarray, continuations: np.ndarray, out_path: str) -> None: ...
def plot_bootstrap_distribution(boot_rhos: np.ndarray, observed_rho: float, out_path: str) -> None: ...
```

### run_experiment.py (`h-m3/code/run_experiment.py`)

**Dependencies:** all modules above

```python
def main(seed: int = 42) -> dict:
    # 1. load + filter + extract pairs
    # 2. score formality (cache-aware)
    # 3. compute deltas + continuation labels
    # 4. run tercile_continuation_analysis
    # 5. verify_mechanism, gate check
    # 6. generate all figures
    # 7. write results.json
    ...
```

---

## File Organization

- `h-m3/code/data_loader.py`
- `h-m3/code/formality_scorer.py`
- `h-m3/code/delta_analysis.py`
- `h-m3/code/tercile_stats.py`
- `h-m3/code/visualize.py`
- `h-m3/code/run_experiment.py`
- `h-m3/code/config.py` — seed=42, n_boot=2000, model_name, dataset_name, cache_path
- `h-m3/cache/formality_scores.parquet`
- `h-m3/figures/` — 4 PNGs
- `h-m3/results.json`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | Load hh-rlhf, filter ≥2 turns/side, extract turn pairs | 8 | 2+2+2+2 |
| A-2 | Formality scoring | Load DeBERTa, batch-score human+AI turns, cache reuse/save | 10 | 3+2+3+2 |
| A-3 | Delta computation | Compute |Δ| per pair, attach conversation_id | 5 | 1+1+2+1 |
| A-4 | Continuation labeling | Derive binary continuation flag from turn structure | 4 | 1+1+1+1 |
| A-5 | Tercile analysis | Percentile binning, per-tercile rate, monotonic check | 7 | 2+1+3+1 |
| A-6 | Cluster bootstrap | Block bootstrap by conversation_id, n=2000, p_robust | 12 | 3+3+4+2 |
| A-7 | Mechanism verification & gate | Spearman rho, gate logic (monotonic + p<0.05) | 6 | 1+2+2+1 |
| A-8 | Visualization | 4 figures (bar, histogram, scatter, bootstrap dist) | 8 | 2+2+2+2 |
| A-9 | Pipeline integration | run_experiment.py orchestration, results.json output | 7 | 2+3+1+1 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-6], Low(4-8): [A-1, A-3, A-4, A-5, A-7, A-8, A-9]

---

## Key Notes

- Reuse H-M2 cached formality scores if `h-m2/cache/formality_scores.parquet` exists (skip A-2 rescoring); else compute fresh.
- Cluster bootstrap (A-6) is the highest-complexity task: resamples whole conversations (not individual turns) to avoid inflated p-values from within-conversation correlation.
- All randomness seeded at 42 (dataset shuffling not needed; only affects bootstrap resampling).
