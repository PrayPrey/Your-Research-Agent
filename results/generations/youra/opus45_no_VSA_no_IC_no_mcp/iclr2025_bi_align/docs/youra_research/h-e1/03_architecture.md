# Architecture: H-E1 (EXISTENCE PoC)

**Type**: EXISTENCE — minimal architecture, no ablation modules.
**Applied**: eval-then-correlate pattern (compute per-sample scores first, correlate after).

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. Archived `h-e1` under `_archive/` is an unrelated prior hypothesis (routing classifier); not reused.

---

## File Structure

```
h-e1/code/
  config.py       # fixed config (model id, dataset ids, seed, threshold)
  data.py         # dataset loading + per-sample prompt formatting
  evaluate.py     # model loading + scoring for each benchmark
  correlate.py    # pairwise Pearson correlation + gate check
  visualize.py    # heatmap + gate bar + distributions
  train.py        # entrypoint: orchestrates evaluate -> correlate -> visualize
```

No `model.py`/`train.py` in the ML-training sense — this is evaluation-only. `train.py` is kept as the single run entrypoint name for pipeline convention.

---

## Data Flow

```
config.py
   |
   v
data.py --(prompts, choices/pairs)--> evaluate.py
                                          |
                                          v  (loads Llama-2-7b-hf once, reused for all 3 benchmarks)
                                    per-sample binary scores
                                    {truthfulqa: [0/1]*817,
                                     hhh_helpful: [0/1]*N,
                                     hhh_harmless: [0/1]*N}
                                          |
                                          v
                                    correlate.py
                                    (3x pearsonr, gate check |r|<0.5)
                                          |
                                          v
                                    visualize.py -> h-e1/figures/*.png
                                          |
                                          v
                                    results.json (scores, correlations, gate pass/fail)
```

---

## Interfaces

### config.py

```python
MODEL_ID = "meta-llama/Llama-2-7b-hf"
SEED = 42
CORR_THRESHOLD = 0.5
DATASETS = {
    "truthfulqa": ("truthful_qa", "multiple_choice"),
    "hh_rlhf": ("Anthropic/hh-rlhf", None),  # split into helpful/harmless subsets by data.py
}
FIGURES_DIR = "h-e1/figures"
RESULTS_PATH = "h-e1/results/results.json"
```

### data.py

**Dependencies**: config, datasets (HF)

```python
def load_truthfulqa() -> list[dict]: ...       # each: {question, choices: list[str], correct_idx: int}
def load_hhh(subset: str) -> list[dict]: ...   # subset in {"helpful","harmless"}; each: {chosen: str, rejected: str}
```

### evaluate.py

**Dependencies**: config, data, transformers, torch

```python
def load_model(model_id: str) -> tuple["PreTrainedModel", "PreTrainedTokenizer"]: ...

def score_truthfulqa_mc1(model, tokenizer, samples: list[dict]) -> list[int]: ...
    # per-sample: 1 if argmax logprob choice == correct_idx else 0

def score_hhh_preference(model, tokenizer, samples: list[dict]) -> list[int]: ...
    # per-sample: 1 if logprob(chosen) > logprob(rejected) else 0

def run_all_evaluations(model, tokenizer) -> dict[str, list[int]]: ...
    # returns {"truthfulqa": [...], "hhh_helpful": [...], "hhh_harmless": [...]}
```

### correlate.py

**Dependencies**: scipy, numpy

```python
def compute_pairwise_correlations(scores: dict[str, list[int]]) -> dict[str, dict]: ...
    # {"truthfulqa_vs_hhh_helpful": {"r": float, "p": float}, ...} (3 pairs)

def check_gate(correlations: dict, threshold: float = 0.5) -> bool: ...
    # True iff all |r| < threshold
```

### visualize.py

**Dependencies**: matplotlib, numpy, correlate

```python
def plot_correlation_heatmap(correlations: dict, out_path: str) -> None: ...
def plot_gate_status(correlations: dict, threshold: float, out_path: str) -> None: ...
def plot_score_distributions(scores: dict[str, list[int]], out_path: str) -> None: ...
```

### train.py (entrypoint)

**Dependencies**: all modules above

```python
def main() -> None: ...
    # 1. load_model
    # 2. load datasets, run_all_evaluations
    # 3. compute_pairwise_correlations, check_gate
    # 4. save results.json
    # 5. generate all figures
    # 6. print PASS/FAIL on gate
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | Load & format TruthfulQA MC + HHH helpful/harmless pairs | 6 | 2+1+2+1 |
| A-2 | Model loading & scoring | Load Llama-2-7b-hf, implement MC1 + preference logprob scoring | 10 | 3+2+4+1 |
| A-3 | Correlation analysis | Pairwise Pearson + gate check | 4 | 1+1+1+1 |
| A-4 | Visualization | Heatmap, gate bar, distribution plots | 5 | 2+1+1+1 |
| A-5 | Orchestration & run | Wire train.py entrypoint, save results.json, run end-to-end | 5 | 1+1+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2], Low(4-8): [A-1, A-3, A-4, A-5]

---

## Dependencies

- `transformers` — model/tokenizer loading, forward pass logits
- `torch` — inference (fp16/bf16 on GPU)
- `datasets` — TruthfulQA, Anthropic/hh-rlhf loading
- `scipy` — `scipy.stats.pearsonr`
- `numpy` — array ops for scores
- `matplotlib` — heatmap/bar/histogram figures
