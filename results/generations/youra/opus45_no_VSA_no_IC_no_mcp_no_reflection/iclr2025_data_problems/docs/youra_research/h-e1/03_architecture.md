# Architecture: h-e1 (E5-large Embedding Similarity — EXISTENCE PoC)

**Applied**: sentence-embedding-similarity-pipeline (encode → normalize → cosine-sim → aggregate)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze (no `src/`, no base hypothesis folder)
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; PRD's code skeleton (Section 10 of experiment brief) defines the reference implementation directly.

---

## File Structure

```
docs/youra_research/h-e1/code/
├── config.py
├── data.py
├── model.py
├── analysis.py
├── train.py          # entrypoint (no training, just the pipeline run)
```

- `data/h-e1/` — cached Pile + MMLU parquet
- `embeddings/` — domain_emb.pt, task_emb.pt
- `results/` — similarities.csv, domain_scores.json, h-e1_analysis.md
- `figures/` — domain_similarity_bar.png

---

## Modules

### config.py

**Dependencies**: none

```python
DOMAINS = ['pile-cc', 'wikipedia', 'github', 'arxiv',
           'stackexchange', 'pubmed', 'books3', 'openwebtext2']
SAMPLES_PER_DOMAIN = 1000
MAX_TOKENS = 512
SEEDS = [42, 43, 44]
MODEL_NAME = 'intfloat/e5-large-v2'
BATCH_SIZE = 32
DATA_DIR = "data/h-e1"
```

### data.py (`code/data.py`)

**Dependencies**: config, datasets (HF)

```python
def load_pile_subset(domains: list[str], n_samples: int, seed: int) -> tuple[list[str], list[str]]: ...
def load_mmlu_validation() -> list[str]: ...
def cache_processed(domain_texts, domain_labels, task_texts, path: str) -> None: ...
def load_cached(path: str) -> tuple[list[str], list[str], list[str]] | None: ...
```

### model.py (`code/model.py`)

**Dependencies**: config, sentence_transformers, torch

```python
def load_embedder(model_name: str = MODEL_NAME) -> "SentenceTransformer": ...
def embed_domains(model, texts: list[str], batch_size: int) -> Tensor: ...  # "passage: " prefix
def embed_tasks(model, texts: list[str], batch_size: int) -> Tensor: ...    # "query: " prefix
def random_baseline_embeddings(n: int, dim: int = 1024, seed: int = 42) -> Tensor: ...
def compute_domain_scores(domain_emb: Tensor, task_emb: Tensor, domain_labels: list[str]) -> dict[str, float]: ...
```

### analysis.py (`code/analysis.py`)

**Dependencies**: scipy, numpy, matplotlib

```python
def descriptive_stats(scores: dict[str, float]) -> dict: ...          # mean/std/min/max
def anova_test(similarities: Tensor, domain_labels: list[str]) -> tuple[float, float]: ...  # F, p
def reproducibility_check(runs: list[dict[str, float]]) -> float: ...  # variance across seeds
def plot_domain_bar(scores: dict[str, float], out_path: str) -> None: ...
def write_report(scores, stats, anova, repro_var, pass_fail: bool, out_path: str) -> None: ...
```

### train.py (`code/train.py`) — entrypoint

**Dependencies**: config, data, model, analysis

```python
def run_single_seed(seed: int) -> dict[str, float]: ...   # returns domain_scores
def run_baselines() -> dict: ...                            # random-embedding baseline
def main() -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading + caching | Load 8 Pile domains + MMLU, cache to parquet | 8 | 2+2+2+2 |
| A-2 | E5-large embedding pipeline | Load model, embed domains/tasks with prefixes, normalize | 9 | 2+3+2+2 |
| A-3 | Similarity + domain aggregation | Cosine sim matrix, mean per sample, per-domain scores | 6 | 1+2+2+1 |
| A-4 | Random-embedding baseline | Replace E5 with random vectors, recompute scores | 4 | 1+1+1+1 |
| A-5 | Statistical analysis | Descriptive stats, ANOVA F-test | 5 | 1+2+2+0 |
| A-6 | Reproducibility check | Run 3 seeds, compute variance across runs | 5 | 1+2+1+1 |
| A-7 | Visualization + report | Bar chart, markdown analysis report, pass/fail decision | 5 | 1+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2], Low(4-8): [A-1, A-3, A-4, A-5, A-6, A-7]

---

## Execution Order

A-1 → A-2 → A-3 → (A-4 parallel) → A-5 → A-6 (reruns A-1→A-3 x3 seeds) → A-7
