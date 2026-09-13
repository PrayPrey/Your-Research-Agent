# Architecture: H-E1 (EXISTENCE PoC)

**Hypothesis:** Middle-layer hidden states encode correctness signal (AUROC > 0.60)
**Type:** EXISTENCE — minimal architecture

Applied: linear-probe-on-residual-stream pattern (venator: hook layer, extract last-token state, sigmoid(w^T h + b), BCE + Adam)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch, no base hypothesis or existing src/ to reconcile against.

---

## File Structure

- `data.py` — TriviaQA loading, prompt formatting, exact-match labeling
- `model.py` — HiddenStateExtractor (forward hook) + LinearProbe
- `config.py` — single fixed config (seed=42, layer=19, lr=1e-3, epochs=10, batch_size=256)
- `train.py` — extraction + training loop orchestration
- `evaluate.py` — AUROC, ROC curve, loss curve, gate comparison figures

---

## Modules

### Config (`config.py`)

**Dependencies**: none

```python
@dataclass
class Config:
    seed: int = 42
    model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    target_layer: int = 19
    hidden_dim: int = 4096
    train_size: int = 95000
    val_size: int = 17000
    lr: float = 1e-3
    epochs: int = 10
    batch_size: int = 256
    auroc_gate: float = 0.60
    figures_dir: str = "figures/"
```

### Data (`data.py`)

**Dependencies**: Config

```python
def load_triviaqa(split: str, n: int) -> Dataset: ...
def format_prompt(example: dict) -> str: ...
def generate_answer(model, tokenizer, prompt: str) -> str: ...
def label_correctness(pred_answer: str, gold_aliases: list[str]) -> int: ...
def build_labeled_dataset(model, tokenizer, dataset, n: int) -> list[dict]: ...
    # returns [{"prompt": str, "label": int}, ...]
```

### Model (`model.py`)

**Dependencies**: Config

```python
class HiddenStateExtractor:
    def __init__(self, model, target_layer: int = 19): ...
    def _capture_hook(self, module, input, output) -> None: ...
    def get_last_hidden(self) -> Tensor: ...   # [batch, hidden_dim]
    def remove(self) -> None: ...

class LinearProbe(nn.Module):
    def __init__(self, hidden_dim: int = 4096): ...
    def forward(self, hidden_states: Tensor) -> Tensor: ...  # sigmoid probs
```

### Train (`train.py`)

**Dependencies**: data.py, model.py, config.py

```python
def extract_hidden_states(model, tokenizer, extractor, examples: list[dict]) -> tuple[Tensor, Tensor]: ...
    # returns (hidden_states [N, hidden_dim], labels [N])
def train_probe(hidden_states: Tensor, labels: Tensor, cfg: Config) -> tuple[LinearProbe, list[float]]: ...
    # returns (trained probe, loss_per_epoch)
def main() -> None: ...
```

### Evaluate (`evaluate.py`)

**Dependencies**: model.py, config.py, sklearn, matplotlib

```python
def evaluate_auroc(probe: LinearProbe, hidden_states: Tensor, labels: Tensor) -> float: ...
def plot_gate_comparison(auroc: float, baseline: float, out_path: str) -> None: ...
def plot_roc_curve(labels: Tensor, preds: Tensor, auroc: float, out_path: str) -> None: ...
def plot_loss_curve(losses: list[float], out_path: str) -> None: ...
def plot_hidden_state_pca(hidden_states: Tensor, labels: Tensor, out_path: str) -> None: ...
def main() -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Load TriviaQA, format prompts, generate answers, label exact-match | 10 | 3+2+3+2 |
| A-2 | Hidden state extraction | Load Llama-3-8B, register hook on layer 19, extract last-token states for full dataset | 12 | 3+3+3+3 |
| A-3 | Linear probe + training | Implement LinearProbe, train loop with Adam/BCE, 10 epochs | 7 | 2+2+2+1 |
| A-4 | Evaluation + gate check | Compute AUROC, compare to 0.60 gate and 0.50 baseline | 5 | 1+2+2+0 |
| A-5 | Visualization | Gate bar chart, ROC curve, loss curve, PCA scatter, save to figures/ | 6 | 2+1+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-2], Low(4-8): [A-3, A-4, A-5]

---

## Complexity Scoring

```
Complexity = Module_Size + Dependencies + Algorithm + Integration (each 1-5)
```
