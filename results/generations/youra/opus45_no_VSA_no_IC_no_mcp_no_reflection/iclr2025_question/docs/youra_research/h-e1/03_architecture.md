# Architecture: h-e1 (EXISTENCE PoC)

**Hypothesis:** UQ methods produce discriminative uncertainty scores (AUROC > 0.55) for hallucination detection on TruthfulQA mc1
**Type:** EXISTENCE — minimal architecture, no training, inference + scoring only.

Applied: no-train PoC inference pipeline (dataset -> model -> UQ scorers -> eval)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field experiment - no existing codebase
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base hypothesis, no prior code to reuse.

---

## File Organization

```
docs/youra_research/h-e1/code/
├── config.py          # fixed hyperparams (model id, seed, N samples, temp, threshold)
├── data.py            # TruthfulQA mc1 loading + caching
├── model.py           # Llama-3-8B-Instruct load + generation helpers
├── uq_methods.py       # 4 UQ scorers: token_entropy, semantic_entropy, p_true, selfcheckgpt
├── evaluate.py         # AUROC/AUPRC computation + gate check
├── visualize.py         # ROC curves, score distributions, bar chart
├── run_experiment.py   # main entrypoint wiring all stages
└── results/             # scores.csv, metrics.json
docs/youra_research/h-e1/figures/   # output figures
```

## Data Flow

1. `data.py` loads TruthfulQA mc1 (817 Qs) -> list of `{question, choices, correct_idx}`
2. For each question, `model.py` generates: (a) greedy main response, (b) N=10 temp-sampled responses
3. `uq_methods.py` consumes generations + logits -> 4 uncertainty scalars per question
4. Ground truth label derived: correct=0 (no hallucination) vs incorrect=1 (hallucination), based on whether greedy answer matches `correct_idx`
5. `evaluate.py` computes AUROC/AUPRC per method against labels, applies 0.55 gate
6. `visualize.py` renders required + optional figures from `results/scores.csv`

---

## Module Interfaces

### config.py

```python
SEED: int = 42
MODEL_ID: str = "meta-llama/Meta-Llama-3-8B-Instruct"
NLI_MODEL_ID: str = "microsoft/deberta-v3-large"
NUM_SAMPLES: int = 10
TEMPERATURE: float = 0.7
MAX_NEW_TOKENS: int = 256
AUROC_THRESHOLD: float = 0.55
```

### data.py (`code/data.py`)

**Dependencies**: config, datasets (HF)

```python
def load_truthfulqa_mc1(cache_dir: str = ".cache") -> list[dict]: ...
# returns [{"question": str, "choices": list[str], "correct_idx": int, "category": str}]
```

### model.py (`code/model.py`)

**Dependencies**: config, transformers, torch

```python
def load_model_and_tokenizer(model_id: str) -> tuple: ...  # (model, tokenizer)

def generate_greedy(model, tokenizer, prompt: str) -> tuple[str, object]: ...
# returns (text, last_step_logits)

def generate_samples(model, tokenizer, prompt: str, n: int, temperature: float) -> list[str]: ...
```

### uq_methods.py (`code/uq_methods.py`)

**Dependencies**: model, torch, scipy, selfcheckgpt

```python
class UQMethodsWrapper:
    def __init__(self, model, tokenizer, num_samples: int = 10): ...
    def token_entropy(self, logits) -> float: ...
    def semantic_entropy(self, prompt: str, temperature: float) -> float: ...
    def p_true(self, question: str, response: str) -> float: ...
    def selfcheck_nli(self, response: str, sampled_responses: list[str]) -> float: ...

def score_all_methods(wrapper: UQMethodsWrapper, question: dict) -> dict: ...
# returns {"token_entropy": float, "semantic_entropy": float, "p_true": float, "selfcheck": float}
```

### evaluate.py (`code/evaluate.py`)

**Dependencies**: sklearn.metrics, config

```python
def compute_metrics(y_true: list[int], scores: dict[str, list[float]]) -> dict: ...
# returns {method: {"auroc": float, "auprc": float}}

def apply_gate(metrics: dict, threshold: float = 0.55) -> bool: ...
# True if max(auroc across methods) > threshold, else pipeline STOP
```

### visualize.py (`code/visualize.py`)

**Dependencies**: matplotlib, evaluate

```python
def plot_gate_comparison(metrics: dict, threshold: float, out_path: str) -> None: ...
def plot_roc_curves(y_true, scores: dict, out_path: str) -> None: ...
def plot_score_distributions(y_true, scores: dict, out_dir: str) -> None: ...
```

### run_experiment.py (`code/run_experiment.py`)

**Dependencies**: all above

```python
def main() -> None: ...
# loads data -> model -> loops questions -> scores -> evaluate -> gate check -> visualize -> write results/
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup data loading | TruthfulQA mc1 load + cache + parse | 6 | 2+1+1+2 |
| A-2 | Setup model loading | Llama-3-8B load, bf16, device_map, generation helpers | 8 | 2+2+2+2 |
| A-3 | Implement token entropy + P(True) | Logit-based entropy, Yes/No prompt scoring | 7 | 2+1+2+2 |
| A-4 | Implement semantic entropy | N-sample generation, NLI clustering, cluster entropy | 10 | 3+3+3+1 |
| A-5 | Implement SelfCheckGPT | Integrate selfcheckgpt package, K-sample consistency scoring | 8 | 2+3+1+2 |
| A-6 | Build evaluation pipeline | AUROC/AUPRC per method, gate check logic | 6 | 2+1+2+1 |
| A-7 | Build visualization + logging | ROC curves, distributions, gate bar chart, CSV/JSON output | 6 | 2+1+1+2 |
| A-8 | Integrate end-to-end run | Wire all modules in run_experiment.py, run on full 817 Qs | 8 | 2+3+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4], Low(4-8): [A-1, A-2, A-3, A-5, A-6, A-7, A-8]
