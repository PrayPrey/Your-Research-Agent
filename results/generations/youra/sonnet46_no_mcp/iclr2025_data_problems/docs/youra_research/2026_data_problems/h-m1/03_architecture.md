# Architecture Document: H-M1
# Cross-Corpus Contamination Variance: The Pile v1, C4 en.noclean, RedPajama-v1

**Hypothesis**: H-M1 | **Type**: MECHANISM (PoC) | **Date**: 2026-05-04

Applied: MECHANISM-multi-corpus-pipeline (extends H-E1 EXISTENCE baseline; adds corpus index construction, 59×3 matrix, extended statistics)

---

## Codebase Analysis (Serena)

**Project Type**: green-field (incremental over H-E1 specification)
**Status**: green-field - no existing code to analyze (h-e1/code/ was not implemented)
**Analyzed Path**: N/A
**Findings**: H-E1 architecture spec provides module interface patterns to extend. All modules implemented from scratch. H-E1 modules (data_loader, ngram_extractor, stats_analyzer, visualizer) are reused and extended; new modules added for corpus index construction and matrix computation.

---

## File Structure

- `code/config.py` — YAML config + dataclass for all 3 corpora + matrix settings
- `code/data_loader.py` — 59 benchmark sub-task loading (MMLU×57, HellaSwag, BBH) — extended from H-E1
- `code/ngram_extractor.py` — 13-gram extraction + MinHash construction — extended from H-E1
- `code/corpus_indexer.py` — MinHash LSH index construction for Pile/C4/RedPajama with checkpointing
- `code/matrix_builder.py` — 59×3 contamination matrix query and aggregation
- `code/stats_analyzer.py` — Kruskal-Wallis, Dunn's test, Spearman, sanity check — extended from H-E1
- `code/visualizer.py` — 6 required figures — extended from H-E1
- `code/run_experiment.py` — pipeline orchestration entry point
- `indices/` — corpus index checkpoints (c4_ckpt_{N}.pkl, redpajama_ckpt_{N}.pkl, pile_index.pkl)
- `results/contamination_matrix.csv` — 177-row output (59×3)
- `results/statistical_tests.json` — gate result + all stats
- `figures/` — all 6 generated plots

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Config:
    # N-gram parameters (fixed per H-E1/WIMBD)
    ngram_n: int = 13
    num_perm: int = 128
    lsh_threshold: float = 0.5
    seed: int = 1
    min_token_length: int = 13
    text_format: str = "question_choices"   # or "question_only"

    # Corpus index paths
    pile_index_path: str = "../h-e1/pile_index.pkl"   # reuse H-E1 if exists
    c4_index_path: str = "indices/c4_index.pkl"
    redpajama_index_path: str = "indices/redpajama_index.pkl"

    # Corpus HF identifiers
    corpus_configs: dict = field(default_factory=lambda: {
        "pile":      {"hf_path": "EleutherAI/pile",                     "config": None},
        "c4":        {"hf_path": "allenai/c4",                          "config": "en.noclean"},
        "redpajama": {"hf_path": "togethercomputer/RedPajama-Data-1T",  "config": None},
    })

    # Checkpoint and retry
    checkpoint_interval: int = 500_000
    retry_attempts: int = 3
    sample_fraction: float = 0.1   # fallback if streaming fails

    # Output paths
    results_dir: str = "results"
    figures_dir: str = "figures"
    indices_dir: str = "indices"

    # Gate thresholds
    gate_p_threshold: float = 0.05
    min_pair_diff_pp: float = 0.02
    wimbd_spearman_min_rho: float = 0.7
    wimbd_pile_tolerance_pp: float = 0.05

def load_config(path: Optional[str] = None) -> Config: ...
```

---

### DataLoader (`code/data_loader.py`)

**Dependencies**: Config

```python
class DataLoader:
    def __init__(self, config: Config): ...
    def load_mmlu(self) -> dict[str, list[str]]:
        """Returns {subtask_name: [formatted_text, ...]} for 57 sub-tasks."""
        ...
    def load_hellaswag(self) -> dict[str, list[str]]:
        """Returns {"hellaswag": [formatted_text, ...]}."""
        ...
    def load_bbh(self) -> dict[str, list[str]]:
        """Returns {"bbh": [formatted_text, ...]}."""
        ...
    def load_all(self) -> dict[str, list[str]]:
        """Merged dict of all 59 sub-tasks."""
        ...
    def format_text(self, item: dict, dataset: str) -> str:
        """Applies question+choices or question-only format per config.text_format."""
        ...
```

---

### NgramExtractor (`code/ngram_extractor.py`)

**Dependencies**: Config

```python
from datasketch import MinHash

class NgramExtractor:
    def __init__(self, config: Config): ...
    def extract(self, text: str) -> list[str]:
        """Sliding-window 13-gram extraction. Returns [] if < min_token_length."""
        ...
    def extract_batch(self, texts: list[str]) -> list[list[str]]:
        """Batch extraction; logs skipped items."""
        ...
    def text_to_minhash(self, text: str) -> MinHash:
        """Converts text to MinHash object (num_perm=128, seed=1)."""
        ...
```

---

### CorpusIndexer (`code/corpus_indexer.py`)

**Dependencies**: Config, NgramExtractor

```python
import pickle
from datasketch import MinHashLSH

class CorpusIndexer:
    def __init__(self, config: Config, extractor: NgramExtractor): ...

    def load_or_build(self, corpus_name: str) -> MinHashLSH:
        """Loads existing index if path exists; otherwise calls build()."""
        ...

    def build(self, corpus_name: str) -> MinHashLSH:
        """Streams HF corpus, builds MinHash LSH, checkpoints every 500k docs.
        Falls back to 10% sample if streaming fails after retry_attempts.
        Logs: f'Building {corpus_name} index: {doc_id:,} docs processed'
        """
        ...

    def _stream_corpus(self, corpus_name: str):
        """Yields (doc_id, text) with exponential-backoff retry (3 attempts)."""
        ...

    def save(self, lsh: MinHashLSH, path: str) -> None:
        """Saves index to pickle file."""
        ...

    def load(self, path: str) -> MinHashLSH:
        """Loads index from pickle file."""
        ...

    def checkpoint(self, lsh: MinHashLSH, corpus_name: str, doc_id: int) -> None:
        """Saves incremental checkpoint to indices/{corpus_name}_ckpt_{doc_id}.pkl."""
        ...
```

---

### MatrixBuilder (`code/matrix_builder.py`)

**Dependencies**: Config, NgramExtractor

```python
import pandas as pd
from datasketch import MinHashLSH

class MatrixBuilder:
    def __init__(self, config: Config, extractor: NgramExtractor): ...

    def query_cell(
        self, subtask_name: str, texts: list[str], corpus_name: str, lsh: MinHashLSH
    ) -> dict:
        """Returns {subtask, corpus, n_items, n_contaminated, rate} for one cell.
        Logs: f'Querying {corpus_name} for sub-task {subtask_name}: {n}/{total} contaminated ({rate:.3f})'
        """
        ...

    def build_matrix(
        self,
        benchmarks: dict[str, list[str]],
        indices: dict[str, MinHashLSH]
    ) -> pd.DataFrame:
        """Returns DataFrame with columns: subtask, corpus, n_items, n_contaminated, rate.
        Shape: 177 rows (59 sub-tasks × 3 corpora).
        """
        ...

    def to_wide(self, matrix_df: pd.DataFrame) -> pd.DataFrame:
        """Pivots to wide format: subtask as index, corpus columns (pile, c4, redpajama)."""
        ...
```

---

### StatsAnalyzer (`code/stats_analyzer.py`)

**Dependencies**: Config

```python
import pandas as pd
from scipy.stats import kruskal, spearmanr

class StatsAnalyzer:
    def __init__(self, config: Config): ...

    def kruskal_wallis(self, matrix_wide: pd.DataFrame) -> dict:
        """Runs kruskal(pile_rates, c4_rates, rp_rates).
        Returns {kruskal_H, kruskal_p, gate_pass, corpus_means, max_pair_diff_pp}.
        """
        ...

    def dunn_posthoc(self, matrix_wide: pd.DataFrame) -> pd.DataFrame:
        """Dunn's test with Bonferroni correction via scikit_posthocs.
        Returns 3×3 p-value DataFrame.
        """
        ...

    def spearman_wimbd(
        self, pile_rates: pd.Series, wimbd_reference: dict
    ) -> tuple[float, float]:
        """Returns (rho, p_value) for Pile column vs. WIMBD published rates."""
        ...

    def sensitivity_analysis(
        self, matrix_wide_primary: pd.DataFrame, matrix_wide_sensitivity: pd.DataFrame
    ) -> dict:
        """Computes sensitivity Kruskal-Wallis p and Spearman rho between formats."""
        ...

    def assert_gate(self, p_value: float) -> None:
        """assert p_value < 0.05, f'Gate FAILED: Kruskal-Wallis p={p_value:.4f} >= 0.05'"""
        ...
```

---

### Visualizer (`code/visualizer.py`)

**Dependencies**: Config

```python
import pandas as pd

class Visualizer:
    def __init__(self, config: Config): ...

    def plot_corpus_comparison_bar(
        self, matrix_wide: pd.DataFrame, kruskal_H: float, kruskal_p: float
    ) -> None:
        """Bar chart: mean rate per corpus ±1 SE; 2 pp reference line; H/p annotation.
        Saves: figures/corpus_comparison_barplot.png
        """
        ...

    def plot_contamination_heatmap(self, matrix_wide: pd.DataFrame) -> None:
        """59×3 heatmap; rows sorted by mean rate desc.
        Saves: figures/contamination_matrix_heatmap.png
        """
        ...

    def plot_corpus_pair_differences(self, matrix_wide: pd.DataFrame) -> None:
        """Pairwise mean difference bars (Pile-C4, Pile-RP, C4-RP) with 2 pp line.
        Saves: figures/corpus_pair_differences.png
        """
        ...

    def plot_wimbd_consistency_scatter(
        self, pile_rates: pd.Series, wimbd_rates: dict, rho: float
    ) -> None:
        """H-M1 Pile column vs WIMBD published rates; Spearman rho annotated.
        Saves: figures/wimbd_consistency_scatter.png
        """
        ...

    def plot_per_corpus_rankings(self, matrix_wide: pd.DataFrame) -> None:
        """Top-10/bottom-10 sub-tasks per corpus (horizontal bar).
        Saves: figures/per_corpus_rankings.png
        """
        ...

    def plot_dunn_posthoc_heatmap(self, posthoc_df: pd.DataFrame) -> None:
        """Dunn's test p-value heatmap for 3 corpus pairs.
        Saves: figures/dunn_posthoc_heatmap.png
        """
        ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: Config, DataLoader, NgramExtractor, CorpusIndexer, MatrixBuilder, StatsAnalyzer, Visualizer

```python
import json
import pandas as pd

def build_indices(config: Config, extractor: NgramExtractor) -> dict:
    """Calls CorpusIndexer.load_or_build() for all 3 corpora.
    Returns {corpus_name: MinHashLSH}.
    """
    ...

def run_primary(config: Config) -> tuple[pd.DataFrame, dict]:
    """Full pipeline: load benchmarks -> build indices -> build matrix -> stats -> visualize."""
    ...

def run_sensitivity(
    config: Config, indices: dict, primary_matrix: pd.DataFrame
) -> dict:
    """Repeat matrix build with question-only text format; run stats comparison."""
    ...

def save_results(matrix_df: pd.DataFrame, stats: dict, config: Config) -> None:
    """Writes results/contamination_matrix.csv and results/statistical_tests.json."""
    ...

def main() -> None:
    """Entry: load_config -> run_primary -> run_sensitivity -> save_results -> assert_gate."""
    ...

if __name__ == "__main__":
    main()
```

---

## Module Dependencies

```
run_experiment.py
  ├── config.py
  ├── data_loader.py      -> config
  ├── ngram_extractor.py  -> config
  ├── corpus_indexer.py   -> config, ngram_extractor
  ├── matrix_builder.py   -> config, ngram_extractor
  ├── stats_analyzer.py   -> config
  └── visualizer.py       -> config
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | config.py, requirements.txt, directory structure (indices/, results/, figures/), env vars | 6 | 1+1+2+2 |
| A-2 | Benchmark Data Loading | data_loader.py: 57 MMLU + HellaSwag + BBH, both text formats, version pinning | 10 | 3+2+2+3 |
| A-3 | NgramExtractor + MinHash | ngram_extractor.py: 13-gram sliding window, text_to_minhash, batch logging | 8 | 2+1+3+2 |
| A-4 | Corpus Index Construction | corpus_indexer.py: load_or_build for Pile/C4/RedPajama, streaming, retry, checkpoint | 18 | 4+4+5+5 |
| A-5 | Contamination Matrix | matrix_builder.py: 59×3 cell queries, rate aggregation, wide/long formats, progress logging | 13 | 3+3+4+3 |
| A-6 | Statistical Analysis | stats_analyzer.py: Kruskal-Wallis, Dunn posthoc, Spearman WIMBD, sensitivity, gate assert | 14 | 3+3+5+3 |
| A-7 | Visualization | visualizer.py: 6 required figures with annotations and reference lines | 11 | 3+2+3+3 |
| A-8 | Orchestration + Sensitivity | run_experiment.py: primary + sensitivity pipeline, save outputs, gate assertion | 10 | 2+3+2+3 |

**Distribution**: VeryHigh(18-20): [A-4], High(14-17): [A-6], Medium(9-13): [A-2, A-5, A-7, A-8], Low(4-8): [A-1, A-3]

---

## Output File Paths

| File | Purpose |
|------|---------|
| `code/config.py` | Config dataclass with all 3 corpus settings |
| `code/data_loader.py` | HuggingFace benchmark loading (59 sub-tasks) |
| `code/ngram_extractor.py` | 13-gram extraction + MinHash construction |
| `code/corpus_indexer.py` | MinHash LSH index build/load for 3 corpora |
| `code/matrix_builder.py` | 59×3 contamination rate matrix |
| `code/stats_analyzer.py` | Kruskal-Wallis + Dunn + Spearman + gate |
| `code/visualizer.py` | 6 figure generators |
| `code/run_experiment.py` | Entry point orchestration |
| `indices/pile_index.pkl` | Pile v1 MinHash LSH (reused from H-E1 or rebuilt) |
| `indices/c4_index.pkl` | C4 en.noclean MinHash LSH |
| `indices/redpajama_index.pkl` | RedPajama-v1 MinHash LSH |
| `results/contamination_matrix.csv` | 177-row matrix output |
| `results/statistical_tests.json` | Gate result + all stats |
| `figures/corpus_comparison_barplot.png` | Required bar chart |
| `figures/contamination_matrix_heatmap.png` | 59×3 heatmap |
| `figures/corpus_pair_differences.png` | Pairwise difference bars |
| `figures/wimbd_consistency_scatter.png` | WIMBD consistency scatter |
| `figures/per_corpus_rankings.png` | Top/bottom-10 per corpus |
| `figures/dunn_posthoc_heatmap.png` | Dunn p-value heatmap |
