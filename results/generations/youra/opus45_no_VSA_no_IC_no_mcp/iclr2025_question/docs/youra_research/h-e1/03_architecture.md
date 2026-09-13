# Architecture: H-E1 (EXISTENCE)

Applied: uncertainty-quantification-pipeline (token entropy + sample consistency AUROC eval)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## File Structure

```
code/h-e1/
  config.py       # fixed experiment config
  data.py         # TruthfulQA loading
  metrics.py      # entropy + consistency + BERTScore labeling
  evaluate.py      # AUROC + bootstrap CI + plots
  run.py           # main pipeline entrypoint
```

EXISTENCE PoC: single flat pipeline, no model/baseline split needed (no "proposed vs baseline" model — comparing two uncertainty signals against ground truth).

---

## Modules

### config.py

```python
MODEL_ID = "meta-llama/Llama-2-7b-hf"
EMBED_MODEL_ID = "all-MiniLM-L6-v2"
DATASET_ID = "truthfulqa/truthful_qa"
N_SAMPLES = 5
TEMPERATURE = 1.0
SEED = 42
N_BOOTSTRAP = 1000
OUTPUT_DIR = "results/h-e1"
```

### data.py (`code/h-e1/data.py`)

**Dependencies**: config

```python
def load_truthfulqa() -> list[dict]:
    """Returns list of {question_id, question, best_answer, incorrect_answers}"""
```

### metrics.py (`code/h-e1/metrics.py`)

**Dependencies**: config, torch, transformers, sentence_transformers, bert_score

```python
def generate_greedy(model, tokenizer, question: str) -> tuple[str, torch.Tensor]:
    """Returns (response_text, logits [seq_len, vocab])"""

def compute_token_entropy(logits: torch.Tensor) -> float: ...

def generate_n_samples(model, tokenizer, question: str, n: int, temperature: float) -> list[str]: ...

def compute_consistency(responses: list[str], encoder) -> float: ...

def label_response(response: str, best_answer: str, incorrect_answers: list[str]) -> int:
    """0=correct, 1=hallucinated via BERTScore F1 comparison"""
```

### evaluate.py (`code/h-e1/evaluate.py`)

**Dependencies**: sklearn, scipy, numpy, matplotlib

```python
def compute_auroc(labels: np.ndarray, scores: np.ndarray) -> float: ...

def bootstrap_ci(labels: np.ndarray, scores: np.ndarray, n_bootstrap: int, seed: int) -> tuple[float, float]: ...

def plot_roc_curves(labels: np.ndarray, entropy: np.ndarray, consistency: np.ndarray, path: str) -> None: ...
```

### run.py (`code/h-e1/run.py`)

**Dependencies**: all above modules

```python
def main() -> None:
    """
    Load data -> load model+encoder -> per-question loop
    (greedy gen -> entropy; N-sample gen -> consistency; BERTScore label)
    -> save scores.csv -> compute AUROC+CI -> save metrics.json + roc_curves.png
    """
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Load TruthfulQA, cache locally | 5 | 1+1+1+2 |
| A-2 | Model loading | Load LLaMA-2-7B fp16 + tokenizer + HF auth check | 6 | 2+2+1+1 |
| A-3 | Token entropy | Greedy gen + logits + Shannon entropy | 9 | 3+2+3+1 |
| A-4 | N-sample consistency | N=5 sampling + MiniLM embed + pairwise cosine | 9 | 3+3+2+1 |
| A-5 | Ground truth labeling | BERTScore F1 vs best/incorrect answers | 7 | 2+2+2+1 |
| A-6 | Main pipeline loop | Wire A-1..A-5, save scores.csv, error handling | 8 | 2+4+1+1 |
| A-7 | AUROC evaluation | roc_auc_score + bootstrap CI + metrics.json | 6 | 2+2+2+0 |
| A-8 | ROC plots | matplotlib ROC curve visualization | 3 | 1+1+0+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-4, A-6], Low(4-8): [A-1, A-2, A-5, A-7, A-8]

Skipped: separate baseline model, ablation configs, model.py abstraction — EXISTENCE PoC compares two signals against ground truth, no model architecture variants needed. Add if h-e1 passes and downstream hypotheses require model swapping.
