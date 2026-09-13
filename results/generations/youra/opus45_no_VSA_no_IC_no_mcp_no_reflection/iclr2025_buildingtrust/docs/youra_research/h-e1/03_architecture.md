# Architecture: h-e1 (EXISTENCE PoC)

**Applied:** Official reference patterns — lorenzkuhn/semantic_uncertainty (NLI clustering), potsawee/selfcheckgpt (BERTScore consistency)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch

---

## Module Structure

### Data Loading (`data.py`)

**Dependencies:** none

```python
def load_truthfulqa() -> list[dict]:  # {question, correct_answers, incorrect_answers}
    ...

def load_halueval_qa() -> list[dict]:  # {question, right_answer, hallucinated_answer, label}
    ...
```

### Generator (`generate.py`)

**Dependencies:** transformers, data.py

```python
class ResponseGenerator:
    def __init__(self, model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct", seed: int = 42): ...
    def generate_n(self, question: str, n: int = 10, temperature: float = 0.7, max_tokens: int = 256) -> list[str]: ...
```

### Detectors (`detectors.py`)

**Dependencies:** transformers, bert_score

```python
class SemanticEntropyDetector:
    def __init__(self, nli_model: str = "microsoft/deberta-v3-large-mnli"): ...
    def _cluster_by_entailment(self, responses: list[str], threshold: float = 0.5) -> list[list[str]]: ...
    def compute_entropy(self, responses: list[str]) -> float: ...

class SelfConsistencyDetector:
    def __init__(self, lang: str = "en"): ...
    def compute_consistency(self, responses: list[str]) -> float: ...
```

### Labels (`labels.py`)

**Dependencies:** none

```python
def label_truthfulqa(sample: dict, responses: list[str]) -> int: ...   # 1=hallucinated via string match to incorrect_answers
def label_halueval(sample: dict) -> int: ...                            # direct from dataset label
```

### Evaluation (`evaluate.py`)

**Dependencies:** sklearn, numpy

```python
def compute_auroc(y_true: np.ndarray, scores: np.ndarray, n_bootstrap: int = 1000) -> tuple[float, float, float]:
    ...  # returns (auroc, ci_low, ci_high)

def check_gate(results: dict, threshold: float = 0.55) -> bool: ...
```

### Visualization (`plots.py`)

**Dependencies:** matplotlib, evaluate.py

```python
def plot_gate_comparison(results: dict, threshold: float, out_path: str) -> None: ...
def plot_roc_curves(results: dict, out_path: str) -> None: ...
def plot_score_distributions(scores: dict, labels: dict, out_path: str) -> None: ...
def plot_score_correlation(se_scores: np.ndarray, sc_scores: np.ndarray, out_path: str) -> None: ...
```

### Orchestration (`run_experiment.py`)

**Dependencies:** all modules above

```python
def main() -> None:
    ...  # load data -> generate -> detect -> label -> evaluate -> plot -> save results.json
```

---

## File Organization

```
h-e1/code/
  data.py
  generate.py
  detectors.py
  labels.py
  evaluate.py
  plots.py
  run_experiment.py
  config.py
h-e1/figures/
h-e1/results.json
```

### Config (`config.py`)

```python
SEED = 42
N_SAMPLES = 10
TEMPERATURE = 0.7
MAX_TOKENS = 256
GATE_THRESHOLD = 0.55
GENERATOR_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"
NLI_MODEL = "microsoft/deberta-v3-large-mnli"
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | Load TruthfulQA + HaluEval-QA, normalize schema | 6 | 2+1+1+2 |
| A-2 | Response generation | Llama-3-8B-Instruct, N=10 sampling, seed 42 | 10 | 3+3+2+2 |
| A-3 | Semantic entropy detector | Deberta NLI bidirectional entailment clustering + entropy | 13 | 3+3+4+3 |
| A-4 | Self-consistency detector | Pairwise BERTScore, exclude diagonal, average F1 | 8 | 2+3+2+1 |
| A-5 | Ground-truth labeling | Map correct/incorrect answers & HaluEval labels to binary | 5 | 2+1+1+1 |
| A-6 | Evaluation pipeline | AUROC + bootstrap 95% CI, gate check vs 0.55 | 7 | 2+2+2+1 |
| A-7 | Visualization | Gate bar chart (required), ROC overlay, distributions, correlation | 6 | 2+1+1+2 |
| A-8 | End-to-end orchestration | Wire all modules, run both datasets, save results.json | 8 | 2+3+1+2 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3], Low(4-8): [A-1, A-4, A-5, A-6, A-7, A-8]
