# Architecture: H-M2 (MECHANISM)

**Applied**: Sampling-loop + embedding-similarity + group-statistical-test pattern (SelfCheckGPT-style consistency scoring), reusing H-M1's generation/correctness/stats/checkpoint/pipeline skeleton.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: `h-m1/code/` exists and is fully implemented (PASS result on disk).
**Analyzed Path**: `h-m1/code/` (generate.py, load_data.py, correctness.py, stats.py, checkpoint.py, visualize.py, run_pipeline.py, config.py, results/h-m1_results.json, results/checkpoint.json)
**Findings**: H-M1 stores only `majority_answer` (truncated to 100 chars) in results/checkpoint, NOT the 10 raw response texts or embeddings needed for pairwise similarity. **Raw responses cannot be reused — H-M2 must regenerate 10 responses/question.** `generate_responses()` signature confirmed: `(model, tokenizer, question, n_samples, temperature, max_new_tokens, seed) -> list[{"text": str, "scores": list[Tensor]}]`. `correctness.py`, `checkpoint.py`, `config.py` module patterns are directly copyable. `entropy.py` (`compute_token_entropy`) also copied to keep entropy in output for H-M3 scatter preview.

---

## System Components

- `data/triviaqa_val.jsonl` -> `load_data.py` (copied) -> `list[{qid, question, answer_aliases}]`
- `generate.py` (copied from h-m1) -> 10 responses/question (text + scores)
- `entropy.py` (copied from h-m1) -> mean_response_entropy per question (for scatter preview)
- `correctness.py` (copied from h-m1) -> exact-match label + majority-vote answer
- `consistency.py` (NEW) -> SemanticConsistencyScorer, pairwise cosine similarity, avg score
- `stats.py` (NEW, extends h-m1 pattern) -> t-test/AUROC/Cohen's d for consistency + Pearson r vs entropy
- `checkpoint.py` (copied from h-m1) -> resume support
- `run_pipeline.py` (NEW) -> orchestrates generate -> entropy -> consistency -> correctness -> stats -> figures
- `visualize.py` (NEW, extends h-m1 pattern) -> gate bar, consistency histograms, ROC curve, entropy-vs-consistency scatter

Data flow: dataset -> generate (10 samples/question) -> [entropy per response averaged; consistency via pairwise cosine sim of embeddings] -> correctness label from majority answer -> merge {qid, entropy, consistency, correct} -> group stats (t-test/AUROC on consistency) -> figures + results JSON.

---

## Modules

### DataLoader (`h-m2/code/load_data.py`)

**Dependencies**: none (copied verbatim from h-m1)

```python
def load_triviaqa_val(limit: int | None = None) -> list[dict]: ...
# returns [{"qid": str, "question": str, "answer_aliases": list[str]}, ...]
```

### Generator (`h-m2/code/generate.py`)

**Copied from h-m1/code/generate.py** (identical config: temp=0.7, top_p=0.9, seed=42)

```python
def load_model(model_name: str = None): ...
def generate_responses(model, tokenizer, question: str, n_samples: int = None,
                       temperature: float = None, max_new_tokens: int = None,
                       seed: int = None) -> list[dict]: ...
# each dict: {"text": str, "scores": list[Tensor]}
```

### EntropyCalculator (`h-m2/code/entropy.py`)

**Copied from h-m1/code/entropy.py**

```python
def compute_token_entropy(scores: list[Tensor]) -> float: ...
```

### SemanticConsistencyScorer (`h-m2/code/consistency.py`)

**Dependencies**: sentence-transformers, numpy

```python
class SemanticConsistencyScorer:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"): ...
    def compute_consistency(self, responses: list[str]) -> float: ...
    # encodes N responses -> (N,384), returns mean of N*(N-1)/2 pairwise cosine sims
```

### CorrectnessEvaluator (`h-m2/code/correctness.py`)

**Copied from h-m1/code/correctness.py**

```python
def evaluate_correctness(generated: str, aliases: list[str]) -> bool: ...
def majority_answer(responses: list[str]) -> str: ...
```

### StatsAnalyzer (`h-m2/code/stats.py`)

**Dependencies**: scipy, sklearn, numpy

```python
def compute_correlation(consistencies: list[float], correctness: list[bool]) -> dict: ...
# returns {t_stat, p_value, auroc, cohens_d, mean_correct, mean_incorrect,
#          n_correct, n_incorrect}
# t-test alternative='greater' (correct > incorrect), AUROC uses +consistency as score

def pearson_entropy_consistency(entropies: list[float], consistencies: list[float]) -> float: ...
# Pearson r for H-M3 preview scatter
```

### CheckpointManager (`h-m2/code/checkpoint.py`)

**Copied from h-m1/code/checkpoint.py** (unchanged interface)

```python
class CheckpointManager:
    def __init__(self, path: str, save_every: int = 50): ...
    def load(self) -> dict: ...
    def save(self, idx: int, results: list): ...
    def should_save(self, idx: int) -> bool: ...
```

### Visualizer (`h-m2/code/visualize.py`)

**Dependencies**: matplotlib, sklearn (roc_curve, auc)

```python
def plot_gate_metrics(auroc: float, auroc_target: float, p_value: float, out_path: str): ...
def plot_consistency_distribution(consistencies: list[float], correctness: list[bool], out_path: str): ...
def plot_roc_curve(consistencies: list[float], correctness: list[bool], out_path: str): ...
def plot_entropy_vs_consistency(entropies: list[float], consistencies: list[float],
                                 correctness: list[bool], out_path: str): ...
```

### Pipeline (`h-m2/code/run_pipeline.py`)

**Dependencies**: all above

```python
def run(limit: int = 100, resume: bool = True) -> dict: ...
# orchestrates: load -> generate(10/question) -> [entropy, consistency per question]
#               -> correctness -> merge -> stats -> visualize -> write results/h-m2_results.json
```

### Config (`h-m2/code/config.py`)

```python
MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
NUM_RESPONSES = 10
TEMPERATURE = 0.7
TOP_P = 0.9
MAX_NEW_TOKENS = 128
SEED = 42
N_QUESTIONS = 100
AUROC_TARGET = 0.55
P_VALUE_TARGET = 0.05
CHECKPOINT_PATH = "results/checkpoint.json"
CHECKPOINT_EVERY = 50
OUTPUT_PATH = "results/h-m2_results.json"
FIGURES_DIR = "figures/"
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual h-m1 Code)

| Module | Import Path / Copy Strategy | File Location |
|--------|------------------------------|----------------|
| generate.py | copy verbatim into `h-m2/code/generate.py` | `h-m1/code/generate.py` |
| entropy.py | copy verbatim into `h-m2/code/entropy.py` | `h-m1/code/entropy.py` |
| correctness.py | copy verbatim into `h-m2/code/correctness.py` | `h-m1/code/correctness.py` |
| checkpoint.py | copy verbatim into `h-m2/code/checkpoint.py` | `h-m1/code/checkpoint.py` |
| load_data.py | copy verbatim into `h-m2/code/load_data.py` | `h-m1/code/load_data.py` |

**Verified from**: `h-m1/code/` (actual implementation, cross-checked against `results/h-m1_results.json` and `results/checkpoint.json`).
**Note**: Cross-hypothesis imports NOT used — h-m1 is a sibling folder, not an installed package. Phase 4 must copy files, not import `from h_m1...`.
**Raw response reuse**: NOT possible — h-m1 discarded individual response texts (only stored truncated majority_answer). H-M2 regenerates all responses with identical seed/config for a controlled but independent run.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | Config + copy base modules | Copy config.py, load_data.py, generate.py, entropy.py, correctness.py, checkpoint.py from h-m1 | 5 | 2+1+1+1 |
| C-2 | SemanticConsistencyScorer | Implement embedding + pairwise cosine similarity averaging | 8 | 2+2+3+1 |
| C-3 | Consistency stats analyzer | t-test (greater), AUROC, Cohen's d on consistency scores | 7 | 2+2+2+1 |
| C-4 | Entropy-consistency correlation | Pearson r computation for H-M3 preview | 4 | 1+1+1+1 |
| C-5 | Visualizer | Gate bar, consistency histograms, ROC curve, entropy-vs-consistency scatter | 8 | 2+1+2+3 |
| C-6 | Pipeline integration | Wire generate->entropy->consistency->correctness->stats->figures, checkpointing | 11 | 3+4+2+2 |
| C-7 | Full-run validation | Run on 100 TriviaQA questions, verify gate criteria (p<0.05, AUROC>0.55) | 9 | 2+2+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [C-6, C-7], Low(4-8): [C-1, C-2, C-3, C-5], VeryLow(1-3): [C-4]

---

## Notes

- No training — inference-only, extends h-m1's validated generation pipeline.
- New logic vs h-m1: SemanticConsistencyScorer (C-2) and entropy-vs-consistency scatter (C-5) are the core additions.
- Gate is SHOULD_WORK: if fails, document as limitation and continue to H-M3 (no hard block).
- Responses must be regenerated (not reused) since h-m1 did not persist raw response text.
