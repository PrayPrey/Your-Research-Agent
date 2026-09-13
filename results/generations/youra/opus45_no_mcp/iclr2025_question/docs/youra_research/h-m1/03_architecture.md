# Architecture: H-M1 (MECHANISM)

**Applied**: Sampling-loop + correctness-labeling + group-statistical-test pattern for uncertainty-correctness validation.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: h-e1/code/ does not exist yet (h-e1 architecture is spec-only, no implementation found on disk) — falling back to h-e1/03_architecture.md interface specs as reference.
**Analyzed Path**: h-e1/code/ (not found)
**Findings**: No actual code to verify; using h-e1 03_architecture.md module interfaces (generate.py, entropy.py, checkpoint.py, config.py) as the reuse contract. Phase 4 must verify these paths exist before import, or reimplement locally if h-e1 code was never generated.

---

## System Components

- `data/triviaqa_val.jsonl` -> `load_data.py` -> `list[{qid, question, answer_aliases}]`
- `generate.py` (reused from h-e1) -> 10 responses/question + logits
- `entropy.py` (reused from h-e1) -> mean_response_entropy per response
- `correctness.py` (NEW) -> exact-match label vs answer aliases, majority-vote answer per question
- `stats.py` (NEW) -> t-test, AUROC, Cohen's d, Pearson r
- `checkpoint.py` (reused from h-e1) -> resume support
- `run_pipeline.py` (NEW) -> orchestrates generate -> entropy -> correctness -> aggregate -> stats -> figures
- `visualize.py` (NEW) -> gate metrics bar, entropy histograms, ROC curve

Data flow: dataset -> generate (10 samples/question, reused) -> entropy per response averaged per question -> correctness label from majority answer -> merge {qid, entropy, correct} -> group stats (t-test/AUROC) -> figures + results JSON.

---

## Modules

### DataLoader (`h-m1/code/load_data.py`)

**Dependencies**: none (datasets lib)

```python
def load_triviaqa_val(limit: int | None = None) -> list[dict]: ...
# returns [{"qid": str, "question": str, "answer_aliases": list[str]}, ...]
```

### Generator (`h-m1/code/generate.py`)

**Reused from h-e1** (copy or import if h-e1/code available)

```python
class ResponseGenerator:
    def __init__(self, model_name: str = "meta-llama/Llama-2-7b-chat-hf",
                 temperature: float = 0.7, max_new_tokens: int = 128,
                 num_responses: int = 10): ...
    def generate(self, question: str) -> list[dict]: ...
    # each dict: {"text": str, "token_ids": list[int], "logits": list[Tensor]}
```

### EntropyCalculator (`h-m1/code/entropy.py`)

**Reused from h-e1**

```python
def token_entropy(logits: list[Tensor]) -> list[float]: ...
def mean_response_entropy(logits: list[Tensor]) -> float: ...
```

### CorrectnessEvaluator (`h-m1/code/correctness.py`)

**Dependencies**: none (stdlib)

```python
def evaluate_correctness(generated: str, aliases: list[str]) -> bool: ...
def majority_answer(responses: list[str]) -> str: ...
# returns most frequent normalized response text
```

### StatsAnalyzer (`h-m1/code/stats.py`)

**Dependencies**: scipy, sklearn, numpy

```python
def compute_correlation(entropies: list[float], correctness: list[bool]) -> dict: ...
# returns {t_stat, p_value, auroc, cohens_d, pearson_r, mean_correct, mean_incorrect}
```

### CheckpointManager (`h-m1/code/checkpoint.py`)

**Reused from h-e1**

```python
class CheckpointManager:
    def __init__(self, path: str, save_every: int = 50): ...
    def load(self) -> dict: ...
    def save(self, idx: int, results: list): ...
```

### Visualizer (`h-m1/code/visualize.py`)

**Dependencies**: matplotlib

```python
def plot_gate_metrics(auroc: float, auroc_target: float, p_value: float, out_path: str): ...
def plot_entropy_distribution(entropies: list[float], correctness: list[bool], out_path: str): ...
def plot_roc_curve(entropies: list[float], correctness: list[bool], out_path: str): ...
```

### Pipeline (`h-m1/code/run_pipeline.py`)

**Dependencies**: all above

```python
def run(limit: int = 11313) -> None: ...
# orchestrates: load -> generate -> entropy -> correctness -> merge
#               -> stats -> visualize -> write results/h-m1_results.json
```

### Config (`h-m1/code/config.py`)

```python
MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"
NUM_RESPONSES = 10
TEMPERATURE = 0.7
MAX_NEW_TOKENS = 128
AUROC_TARGET = 0.55
P_VALUE_TARGET = 0.05
CHECKPOINT_PATH = "results/checkpoint.json"
OUTPUT_PATH = "results/h-m1_results.json"
FIGURES_DIR = "figures/"
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From h-e1 Spec — Code Not Yet Materialized)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| ResponseGenerator | `from h_e1.generate import ResponseGenerator` | `h-e1/code/generate.py` |
| entropy funcs | `from h_e1.entropy import token_entropy, mean_response_entropy` | `h-e1/code/entropy.py` |
| CheckpointManager | `from h_e1.checkpoint import CheckpointManager` | `h-e1/code/checkpoint.py` |

**Verified from**: h-e1/03_architecture.md only (h-e1/code/ not found on disk).
**Fallback for Phase 4**: If `h-e1/code/` does not exist at implementation time, copy the three modules above verbatim into `h-m1/code/` rather than importing cross-hypothesis.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Config | Fixed config module | 3 | 1+1+1+0 |
| M-2 | Data loading | Load TriviaQA val w/ answer aliases | 5 | 2+2+1+0 |
| M-3 | Reuse/copy generation+entropy | Port generate.py + entropy.py from h-e1 (or reimplement if code missing) | 10 | 3+3+2+2 |
| M-4 | Correctness evaluator | Exact-match + majority-vote answer labeling | 6 | 2+2+2+0 |
| M-5 | Checkpointing | Save/resume every N questions | 6 | 2+2+1+1 |
| M-6 | Stats analyzer | t-test, AUROC, Cohen's d, Pearson r | 8 | 2+2+3+1 |
| M-7 | Visualizer | Gate bar chart, entropy histograms, ROC curve | 7 | 2+1+2+2 |
| M-8 | Pipeline + full-run validation | Wire together, run on full 11K val set, verify gate criteria | 12 | 3+4+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-3, M-6, M-8], Low(4-8): [M-2, M-4, M-5, M-7], VeryLow(1-3): [M-1]

---

## Notes

- No training — inference-only, extends h-e1's validated generation pipeline.
- New logic vs h-e1: correctness labeling (M-4) and statistical correlation testing (M-6) are the core additions.
- Gate is MUST_WORK: pipeline must produce p<0.05, correct direction, AUROC>0.55 or hypothesis fails.
