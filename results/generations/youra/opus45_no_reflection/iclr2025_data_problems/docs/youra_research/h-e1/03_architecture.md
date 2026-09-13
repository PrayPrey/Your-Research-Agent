# Architecture: H-E1 (EXISTENCE PoC)

**Hypothesis:** Architecture-method interaction exists (attribution method x BERT/GPT-2)
**Type:** EXISTENCE — minimal architecture, 4-8 epic tasks

Applied: unified-attribution-API-pattern (single interface wrapping TRAK/EK-FAC/TracIn for fair comparison)

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch

## Module Structure

### data.py

**Dependencies:** datasets, transformers

```python
def load_sst2() -> DatasetDict: ...
def inject_label_noise(dataset, rate: float = 0.05, seed: int = 42) -> tuple[Dataset, set[int]]: ...
def tokenize_dataset(dataset, tokenizer, max_length: int = 128) -> Dataset: ...
def get_loaders(train_ds, val_ds, batch_size: int = 32) -> tuple[DataLoader, DataLoader]: ...
```

### model.py

**Dependencies:** transformers

```python
def build_bert(num_labels: int = 2) -> tuple[PreTrainedModel, PreTrainedTokenizer]: ...
def build_gpt2(num_labels: int = 2) -> tuple[PreTrainedModel, PreTrainedTokenizer]: ...
```

### train.py

**Dependencies:** model.py, data.py

```python
def train_model(model, train_loader, seed: int, epochs: int = 3, lr: float = 2e-5) -> PreTrainedModel: ...
def run_all_seeds(model_name: str, train_loader, seeds: list[int]) -> dict[int, PreTrainedModel]: ...
```

### attribution.py

**Dependencies:** train.py, traker, kronfluence, captum

```python
def compute_trak_scores(model, train_loader, train_size: int) -> np.ndarray: ...
def compute_ekfac_scores(model, train_loader) -> np.ndarray: ...
def compute_tracin_scores(model, train_loader, checkpoint: dict) -> np.ndarray: ...

def compute_attribution(model, train_loader, method: str, **kwargs) -> np.ndarray:
    """Dispatch to trak/ekfac/tracin. Returns self-influence scores."""
```

### evaluate.py

**Dependencies:** attribution.py, sklearn, scipy

```python
def mislabeled_auc(scores: np.ndarray, mislabeled_indices: set[int]) -> float: ...
def paired_ttest(bert_aucs: list[float], gpt2_aucs: list[float]) -> tuple[float, float]: ...
def cohens_d(x: list[float], y: list[float]) -> float: ...
def run_gate_check(results: dict) -> dict:
    """Returns PASS/FAIL per success criteria (>5% AUC diff, p<0.05, d>0.3)."""
```

### visualize.py

**Dependencies:** matplotlib, evaluate.py

```python
def plot_auc_comparison(results: dict, out_path: str) -> None: ...
def plot_method_arch_heatmap(results: dict, out_path: str) -> None: ...
def plot_diff_significance(results: dict, stats: dict, out_path: str) -> None: ...
```

### main.py

**Dependencies:** all modules above

```python
def run_experiment() -> None:
    """Full pipeline: data -> train (2 arch x 5 seeds) -> attribution (3 methods) -> eval -> viz -> gate."""
```

## File Organization

```
code/
  data.py
  model.py
  train.py
  attribution.py
  evaluate.py
  visualize.py
  main.py
  config.py       # fixed hyperparams (lr, epochs, batch_size, seeds, noise_rate)
checkpoints/       # per (arch, seed) final checkpoint
figures/           # 3 required plots
results.json       # AUC per (method, arch, seed) + stats
```

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Load SST-2, inject 5% noise (seed=42), tokenize for both tokenizers | 6 | 2+1+2+1 |
| A-2 | Model builders | BERT + GPT-2 classification heads, GPT-2 pad token config | 4 | 1+1+1+1 |
| A-3 | Training loop | Fine-tune both models x 5 seeds, checkpoint saving | 9 | 3+2+2+2 |
| A-4 | TRAK integration | Wrap traker API, self-influence diagonal extraction | 8 | 2+3+2+1 |
| A-5 | EK-FAC integration | Wrap kronfluence API, fit factors + self-scores | 8 | 2+3+2+1 |
| A-6 | TracIn integration | Wrap captum TracInCPFast, self-influence | 6 | 2+2+1+1 |
| A-7 | Evaluation + stats | AUC computation, paired t-test, Cohen's d, gate check | 7 | 2+2+2+1 |
| A-8 | Visualization + orchestration | 3 required plots + main.py pipeline wiring | 6 | 2+1+1+2 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3], Low(4-8): [A-1, A-2, A-4, A-5, A-6, A-7, A-8]
