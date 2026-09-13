# Architecture: H-M1 (Semantic Entropy / Error Correlation)

**Type:** MECHANISM | **Tier:** FULL | **Gate:** MUST_WORK (p<0.05, d>0.3)

Applied: Farquhar 2024 semantic-entropy pipeline pattern (generate → cluster → entropy → evaluate)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; reference is `jlko/semantic_uncertainty` (external repo, not local codebase)

---

## File Organization

```
h-m1/code/
  data/loader.py          # TriviaQA loading + answer normalization
  generation/generate.py  # Llama-2-7B sampling + logprob capture
  entropy/clustering.py   # DeBERTa bidirectional entailment clustering
  entropy/semantic_entropy.py  # cluster prob aggregation + Shannon entropy
  eval/correctness.py     # exact-match / F1 labeling
  eval/statistics.py      # Mann-Whitney U, Cohen's d, AUROC
  eval/visualize.py       # bar chart, violin, ROC
  config.py                # all hyperparams (temp, N, thresholds)
  run_experiment.py        # orchestrates full pipeline
  ablations/run_ablations.py  # A1 temp, A2 N, A3 threshold sweeps
```

---

## Modules

### DataLoader (`data/loader.py`)

**Dependencies**: datasets (HF)

```python
def load_triviaqa(seed: int = 42, n: int = 1000) -> list[dict]: ...
def normalize_answer(text: str) -> str: ...  # lowercase, strip punctuation
```

### ResponseGenerator (`generation/generate.py`)

**Dependencies**: transformers, torch, config.py

```python
class ResponseGenerator:
    def __init__(self, model_id: str = "meta-llama/Llama-2-7b-chat-hf",
                 temperature: float = 0.7, max_new_tokens: int = 50): ...
    def generate_n(self, question: str, n: int = 10) -> list[dict]: ...
        # returns [{"text": str, "logprob": float, "token_logprobs": list[float]}]
```

### EntailmentClusterer (`entropy/clustering.py`)

**Dependencies**: transformers (DeBERTa-v3-large-mnli)

```python
class EntailmentClusterer:
    def __init__(self, model_id: str = "microsoft/deberta-v3-large-mnli",
                 threshold: float = 0.5): ...
    def check_entailment(self, premise: str, hypothesis: str, question: str) -> float: ...
        # returns entailment probability; question prepended to both sides
    def cluster(self, responses: list[str], question: str) -> list[list[int]]: ...
        # greedy bidirectional entailment clustering
```

### SemanticEntropy (`entropy/semantic_entropy.py`)

**Dependencies**: EntailmentClusterer, numpy, scipy

```python
def compute_cluster_probs(clusters: list[list[int]], logprobs: list[float]) -> np.ndarray: ...
def compute_semantic_entropy(responses: list[str], logprobs: list[float],
                              clusterer: EntailmentClusterer, question: str) -> float: ...
    # returns entropy in nats
```

### CorrectnessLabeler (`eval/correctness.py`)

**Dependencies**: data/loader.py (normalize_answer)

```python
def token_f1(pred: str, gold: str) -> float: ...
def is_correct(response: str, gold_aliases: list[str], f1_threshold: float = 0.5) -> bool: ...
```

### StatTests (`eval/statistics.py`)

**Dependencies**: scipy.stats, sklearn.metrics

```python
def cohens_d(correct: np.ndarray, incorrect: np.ndarray) -> float: ...
def mann_whitney_test(correct: np.ndarray, incorrect: np.ndarray) -> tuple[float, float]: ...
    # returns (statistic, p_value), one-sided incorrect > correct
def compute_auroc(entropies: np.ndarray, labels: np.ndarray) -> float: ...
def evaluate_gate(entropy_correct: np.ndarray, entropy_incorrect: np.ndarray) -> dict: ...
    # {p_value, cohens_d, auroc, gate_passed}
```

### Visualizer (`eval/visualize.py`)

**Dependencies**: matplotlib, seaborn, eval/statistics.py

```python
def plot_gate_bar_chart(results: dict, out_path: str) -> None: ...  # REQUIRED figure
def plot_entropy_violin(entropy_correct, entropy_incorrect, out_path: str) -> None: ...
def plot_roc_curve(entropies, labels, out_path: str) -> None: ...
```

### Orchestrator (`run_experiment.py`)

**Dependencies**: all modules above

```python
def main() -> None: ...
    # load data -> generate -> cluster+entropy -> label correctness -> stats -> figures -> save results.json
```

### AblationRunner (`ablations/run_ablations.py`)

**Dependencies**: run_experiment.py components

```python
def run_temperature_ablation(temps: list[float] = [0.5, 0.7, 1.0]) -> dict: ...
def run_sample_count_ablation(ns: list[int] = [5, 10, 15]) -> dict: ...
def run_threshold_ablation(thresholds: list[float] = [0.3, 0.5, 0.7]) -> dict: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | TriviaQA load, sample, normalize answers | 8 | 2+1+2+3 |
| A-2 | Response generation | Llama-2-7B sampling with logprob capture, batched | 14 | 4+3+4+3 |
| A-3 | Entailment clustering | DeBERTa NLI, bidirectional check, greedy clustering | 15 | 4+3+5+3 |
| A-4 | Semantic entropy computation | Cluster prob aggregation, Shannon entropy | 9 | 2+3+3+1 |
| A-5 | Correctness labeling | Exact match + token F1 scoring vs aliases | 6 | 2+1+2+1 |
| A-6 | Statistical evaluation | Mann-Whitney U, Cohen's d, AUROC, gate check | 8 | 2+3+2+1 |
| A-7 | Visualization suite | Bar chart (required), violin, ROC curve | 7 | 3+1+2+1 |
| A-8 | Pipeline orchestration | End-to-end run script, result persistence | 10 | 3+4+2+1 |
| A-9 | Ablation studies | Temperature, N, threshold sweeps (A1-A3) | 12 | 3+4+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2, A-3], Medium(9-13): [A-1, A-4, A-6, A-8, A-9], Low(4-8): [A-5, A-7]

---

## Key Notes

- N=10 generations x 1000 questions = 10,000 responses; batch NLI clustering per-question (10 responses → ≤45 pairwise entailment checks) for throughput.
- Question prepended to both premise/hypothesis in NLI per Farquhar 2024 methodology.
- Entropy uses length-normalized mean token log-prob per generation before cluster aggregation.
- Ablations (A-9) reuse A-2/A-3 modules with parameter sweeps; no new model classes needed.
