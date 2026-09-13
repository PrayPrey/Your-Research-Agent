# Architecture: H-M1 — Token Entropy Captures Epistemic Uncertainty

**Applied**: Token-entropy uncertainty quantification (Kadavath et al. 2022) + Mann-Whitney/Cohen's d group comparison (standard stats pattern)

**PoC scope**: MUST_WORK gate, single model, no ablations, no training. Minimal file set.

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing `src/` in this project; PRD references H-E1's `src/metrics/entropy.py` but no such file exists in this repo (only in an unrelated archived run). Treating as new implementation.
**Analyzed Path**: N/A
**Findings**: New implementation from scratch — entropy computation to be written in `code/entropy.py`.

---

## File Structure

```
h-m1/code/
  config.py       # fixed hyperparameters + paths
  data.py         # TruthfulQA loading + correctness labeling
  entropy.py      # response generation + token entropy computation
  analysis.py     # group partition, Cohen's d, Mann-Whitney U
  visualize.py    # box plot, histogram+KDE, ROC curve, entropy-vs-length scatter
  run.py          # orchestrates full pipeline, saves results.json + figures
```

---

## Module Interfaces

### config.py

```python
MODEL_ID = "meta-llama/Llama-2-7b-hf"
DATASET_ID = ("truthful_qa", "generation")
MAX_NEW_TOKENS = 100
DTYPE = "float16"
SEED = 42
RESULTS_PATH = "h-m1/results.json"
FIGURES_DIR = "h-m1/figures/"
```

### data.py (`code/data.py`)

**Dependencies**: none (datasets library)

```python
def load_truthfulqa() -> list[dict]:
    """Returns list of {question, correct_answers, incorrect_answers}."""

def is_correct(response: str, correct_answers: list[str]) -> bool:
    """Substring match, case-insensitive."""
```

### entropy.py (`code/entropy.py`)

**Dependencies**: config, transformers, torch

```python
def load_model():
    """Returns (model, tokenizer) on device, float16."""

def compute_response_entropy(model, tokenizer, question: str, max_new_tokens: int) -> tuple[float, str, int]:
    """Generate greedy response, return (mean_token_entropy, response_text, num_tokens)."""
```

### analysis.py (`code/analysis.py`)

**Dependencies**: numpy, scipy.stats

```python
def cohens_d(a: list[float], b: list[float]) -> float: ...

def compare_groups(correct_entropy: list[float], incorrect_entropy: list[float]) -> dict:
    """Returns mean_correct, mean_incorrect, effect_size_d, pvalue, pass (direction & d>0.2)."""
```

### visualize.py (`code/visualize.py`)

**Dependencies**: matplotlib, seaborn, sklearn.metrics (roc_curve)

```python
def plot_box(correct: list[float], incorrect: list[float], out_path: str): ...
def plot_histogram_kde(correct: list[float], incorrect: list[float], out_path: str): ...
def plot_roc(entropies: list[float], labels: list[int], out_path: str): ...
def plot_entropy_vs_length(entropies: list[float], lengths: list[int], out_path: str): ...
```

### run.py (`code/run.py`)

**Dependencies**: all above

```python
def main():
    """
    1. load_truthfulqa()
    2. load_model()
    3. for each question: compute_response_entropy + is_correct -> record
    4. partition by correctness
    5. compare_groups()
    6. generate 4 figures
    7. dump results.json
    """
```

---

## Data Flow

`data.load_truthfulqa()` -> questions/answers
-> `entropy.load_model()` + `entropy.compute_response_entropy()` per question -> (entropy, response, token_count)
-> `data.is_correct()` -> correctness label
-> partition into correct_entropies / incorrect_entropies (+ lengths)
-> `analysis.compare_groups()` -> stats dict
-> `visualize.*()` -> 4 PNGs in `figures/`
-> `run.main()` writes `results.json` (per-item records + summary stats)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config & data loading | config.py + data.py (load TruthfulQA, is_correct) | 5 | 2+1+1+1 |
| A-2 | Model loading & generation | entropy.load_model, greedy generate with output_scores | 7 | 2+2+2+1 |
| A-3 | Token entropy computation | per-token entropy from logits, mean aggregation | 5 | 2+1+1+1 |
| A-4 | Full pipeline loop (817 Qs) | run.main loop: generate+entropy+label per question, collect records | 6 | 2+2+1+1 |
| A-5 | Statistical analysis | analysis.py: cohens_d, mannwhitneyu, compare_groups | 5 | 1+1+2+1 |
| A-6 | Visualization suite | box, histogram+KDE, ROC, scatter (4 figures) | 6 | 2+2+1+1 |
| A-7 | Results export & gate check | results.json dump, MUST_WORK pass/fail evaluation | 4 | 1+1+1+1 |

**Total complexity budget**: 38 raw / target ≤30 — collapse A-3 into A-2, A-7 into A-5 for execution (5 epics, ~28 pts) since PoC scope keeps them tightly coupled in practice.

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-6, A-7]

---

## External Dependencies

None — green-field, no base hypothesis code to reuse (H-E1 reference in PRD is stale/not present in this repo).
