# Architecture: H-E1 (EXISTENCE PoC)

**Hypothesis:** CCR scales monotonically with injection rate (R² ≥ 0.9); detector F1 > 0.8 @ 0.1%
**Type:** EXISTENCE — minimal architecture

Applied: contamination-attribution-pipeline pattern (n-gram detection + TRAK attribution + linear regression scaling check)

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch; no base hypothesis or prior codebase found under h-e1/code/

---

## File Structure

```
h-e1/code/
  config.py       # fixed experiment config (single dataclass)
  data.py         # load RedPajama+MMLU, injection
  model.py        # Pythia-1B load + TRAK attribution wrapper
  detect.py       # n-gram overlap detector
  train.py        # fine-tune loop per injection level
  evaluate.py     # CCR, F1, R², MMLU accuracy, figures
  main.py         # orchestrates 4 injection-level runs
figures/
```

---

## Modules

### Config (`config.py`)

**Dependencies**: None

```python
@dataclass
class Config:
    model_id: str = "EleutherAI/pythia-1b"
    injection_rates: list = (0.001, 0.01, 0.05, 0.1)
    ngram_n: int = 13
    lr: float = 1e-4
    weight_decay: float = 0.01
    betas: tuple = (0.9, 0.95)
    batch_size: int = 512
    grad_accum: int = 8
    train_steps: int = 10_000
    seed: int = 42
    out_dir: str = "figures/"
```

### Data (`data.py`)

**Dependencies**: Config

```python
def load_corpus_and_benchmark(cfg: Config) -> tuple[list[str], list[dict]]: ...
def inject_benchmark(corpus: list[str], benchmark: list[dict], rate: float, seed: int) -> tuple[list[str], list[int]]: ...
def verbalize(sample: dict) -> str: ...
```

### Detector (`detect.py`)

**Dependencies**: None

```python
def ngram_overlap_detect(corpus: list[str], benchmark: list[dict], n: int = 13) -> set[int]: ...
def evaluate_detector_precision(predicted: set[int], actual: set[int]) -> float: ...
```

### Model (`model.py`)

**Dependencies**: Config, transformers, traker

```python
def load_model_and_tokenizer(cfg: Config): ...

class Attributor:
    def __init__(self, model, train_set_size: int): ...
    def score(self, benchmark: list[dict]) -> np.ndarray: ...

def compute_ccr(scores: np.ndarray, injected_positions: list[int]) -> float: ...
```

### Train (`train.py`)

**Dependencies**: Config, Data, Model

```python
def train_one_run(cfg: Config, corpus: list[str], injection_rate: float) -> tuple[PreTrainedModel, list[int]]: ...
```

### Evaluate (`evaluate.py`)

**Dependencies**: Config, Detector, Model

```python
def eval_mmlu_accuracy(model, tokenizer, benchmark: list[dict]) -> float: ...
def fit_ccr_regression(injection_rates: list[float], ccr_values: list[float]) -> float:  # returns R²
    ...
def verify_mechanism_activation(ccr_values: list[float], injection_rates: list[float]) -> bool: ...
def plot_ccr_scaling(injection_rates: list[float], ccr_values: list[float], r2: float, out_dir: str) -> None: ...
def plot_mmlu_vs_injection(injection_rates: list[float], accs: list[float], out_dir: str) -> None: ...
def plot_attribution_distribution(scores: np.ndarray, injected_positions: list[int], out_dir: str) -> None: ...
```

### Main (`main.py`)

**Dependencies**: all above

```python
def run_all(cfg: Config) -> dict:  # {rate: {ccr, f1, mmlu_acc}}
    ...

if __name__ == "__main__":
    run_all(Config())
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Load RedPajama+MMLU, verbalize, injection fn | 8 | 2+2+2+2 |
| A-2 | N-gram detector | 13-gram overlap detection + F1 eval | 6 | 2+1+2+1 |
| A-3 | Model + TRAK attribution | Load Pythia-1B, wrap TRAKer, CCR computation | 10 | 3+3+2+2 |
| A-4 | Training loop | Fine-tune per injection level, AdamW, checkpointing | 9 | 3+2+2+2 |
| A-5 | Evaluation metrics | MMLU accuracy, R² regression, mechanism check | 7 | 2+2+2+1 |
| A-6 | Visualization | CCR scaling, MMLU vs injection, attribution dist plots | 5 | 2+1+1+1 |
| A-7 | Orchestration + run | main.py loop over 4 injection rates, save results | 6 | 2+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-4], Low(4-8): [A-1, A-2, A-5, A-6, A-7]

---

## Notes

- Green-field EXISTENCE PoC: no ablation modules, single fixed config, no base hypothesis code to reuse.
- TRAK attribution (A-3) is highest-risk/complexity module — isolate for early smoke test with small corpus subset before full 10k-step runs.
