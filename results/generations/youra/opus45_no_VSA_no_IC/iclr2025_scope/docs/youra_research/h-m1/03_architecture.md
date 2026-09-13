# Architecture: h-m1

**Hypothesis:** Attention entropy at optimal LoRA rank correlates with model size (Pearson r > 0.6, p < 0.05)
**Type:** MECHANISM

Applied: PEFT LoraConfig adapter pattern (huggingface/peft conceptual guide)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no code to analyze (no `code/` folder exists for h-m1, no base_hypothesis_folder referenced in inputs)
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## File Organization

```
code/
  config.py       # constants: MODEL_SIZES, RANKS, hyperparams
  data.py         # SQuAD v2.0 loading + tokenization
  model.py        # Pythia loading + LoRA adapter creation
  train.py        # training loop (AdamW, warmup+cosine)
  evaluate.py      # F1 scoring (QA)
  entropy.py       # attention entropy computation
  correlate.py      # Pearson correlation analysis
  visualize.py      # 4 required figures
  main.py         # orchestrates full 4x6 grid sweep
```

---

## Modules

### config.py

```python
MODEL_SIZES: list[str] = ["1b", "2.8b", "6.9b", "12b"]
MODEL_PARAMS: dict[str, float] = {"1b": 1e9, "2.8b": 2.8e9, "6.9b": 6.9e9, "12b": 12e9}
RANKS: list[int] = [4, 8, 16, 32, 64, 128]
MAX_SEQ_LEN: int = 512
SEED: int = 42

class TrainConfig:
    epochs: int = 3
    lr: float = 1e-4
    batch_size: int = 4
    grad_accum: int = 4
    warmup_ratio: float = 0.1
```

### data.py

**Dependencies**: config.py

```python
def load_squad_v2(train_n: int = 5000, val_n: int = 1000) -> tuple[Dataset, Dataset]: ...
def tokenize_qa(dataset: Dataset, tokenizer, max_len: int = 512) -> Dataset: ...
def make_dataloader(dataset: Dataset, batch_size: int, shuffle: bool) -> DataLoader: ...
```

### model.py

**Dependencies**: config.py

```python
def load_base_model(size: str) -> tuple[PreTrainedModel, PreTrainedTokenizer]: ...
def create_lora_model(base_model: PreTrainedModel, rank: int) -> PeftModel: ...
```

### train.py

**Dependencies**: model.py, data.py, config.py

```python
def train_qa(
    model: PeftModel,
    train_loader: DataLoader,
    val_loader: DataLoader,
    cfg: TrainConfig,
    seed: int = SEED,
) -> PeftModel: ...
```

### evaluate.py

**Dependencies**: data.py

```python
def evaluate_qa(model: PeftModel, tokenizer, val_data: Dataset) -> float:
    """Returns F1 score."""
```

### entropy.py

**Dependencies**: (none — pure tensor ops)

```python
def compute_attention_entropy(
    model: PeftModel,
    input_ids: Tensor,
    attention_mask: Tensor,
) -> float:
    """Mean Shannon entropy over attentions, masked + renormalized, averaged over layers/heads/positions."""
```

### correlate.py

**Dependencies**: config.py (MODEL_PARAMS)

```python
def find_optimal_rank(f1_scores: list[float], ranks: list[int]) -> int: ...
def compute_correlation(results: dict, model_params: dict) -> dict:
    """Returns {"pearson_r": float, "p_value": float, "pass": bool}."""
```

### visualize.py

**Dependencies**: correlate.py

```python
def plot_gate_metrics(results: dict, correlation: dict, out_path: str) -> None:
    """Required: scatter model_size vs entropy@optimal_rank + regression line."""
def plot_rank_f1_curves(results: dict, out_path: str) -> None: ...
def plot_entropy_heatmap(results: dict, out_path: str) -> None: ...
def plot_optimal_rank_bar(results: dict, out_path: str) -> None: ...
```

### main.py

**Dependencies**: all modules above

```python
def run_experiment() -> dict:
    """Sweeps MODEL_SIZES x RANKS, trains, evaluates, computes entropy,
    finds optimal rank per model, computes correlation, saves JSON, generates figures."""
def main() -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config & seeding | config.py constants, seed utils | 4 | 1+1+1+1 |
| A-2 | Data pipeline | Load SQuAD v2.0, tokenize, dataloaders | 8 | 2+2+2+2 |
| A-3 | Model loading | Load 4 Pythia sizes (fp16, device_map=auto), caching | 9 | 3+3+1+2 |
| A-4 | LoRA adapter creation | create_lora_model across 6 ranks via PEFT | 6 | 2+2+1+1 |
| A-5 | Training loop | AdamW + warmup/cosine, grad accum, checkpointing, early stop | 14 | 4+3+4+3 |
| A-6 | QA evaluation (F1) | SQuAD F1 scoring on val set | 7 | 2+2+2+1 |
| A-7 | Attention entropy computation | Masked, renormalized Shannon entropy, output_attentions hook | 10 | 3+2+4+1 |
| A-8 | Full sweep orchestration | main.py: 4x6=24 combos, results collection, JSON save | 12 | 3+4+2+3 |
| A-9 | Correlation analysis | Optimal-rank selection + Pearson r/p computation | 6 | 2+1+2+1 |
| A-10 | Visualization suite | 4 required figures (scatter, line, heatmap, bar) | 9 | 3+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5], Medium(9-13): [A-3, A-7, A-8, A-10], Low(4-8): [A-1, A-2, A-4, A-6, A-9]
