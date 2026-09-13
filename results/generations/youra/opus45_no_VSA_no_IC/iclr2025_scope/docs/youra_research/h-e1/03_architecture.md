# Architecture: h-e1

**Type**: EXISTENCE (PoC) | **Gate**: MUST_WORK

Applied: HF Trainer + PEFT LoRA config sweep pattern (transformers/peft docs)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no code to analyze
**Analyzed Path**: N/A
**Findings**: Archived `h-e1/code/` folders under `_archive/` belong to prior unrelated hypothesis content (routing/eviction domain) and are not applicable to this LoRA-scaling PRD. New implementation from scratch.

---

## File Structure

- `config.py` — model list, rank grid, seeds, training hyperparams
- `data.py` — SQuAD-v2 load + tokenization
- `model.py` — Pythia + LoRA wrapper factory
- `train.py` — training loop for one (model, rank, seed) run + F1 eval
- `main.py` — sweep driver: loop 72 runs, write rank_sweep.csv
- `analyze.py` — r_opt extraction, log-linear regression, bootstrap CI, plot

## Modules

### Config (`config.py`)

**Dependencies**: none

```python
MODELS = {"pythia-1b": 1.0e9, "pythia-2.8b": 2.8e9, "pythia-6.9b": 6.9e9, "pythia-12b": 1.2e10}
RANKS = [4, 8, 16, 32, 64, 128]
SEEDS = [42, 1337, 2024]

@dataclass
class TrainConfig:
    epochs: int = 3
    lr: float = 1e-4
    batch_size: int = 8
    grad_accum: int = 4
    warmup_steps: int = 100
    max_length: int = 384
```

### Data (`data.py`)

**Dependencies**: Config

```python
def load_squad_v2() -> DatasetDict: ...
def tokenize_squad(dataset: DatasetDict, tokenizer, max_length: int) -> DatasetDict: ...
```

### Model (`model.py`)

**Dependencies**: Config

```python
def load_base_model(model_id: str) -> PreTrainedModel: ...
def apply_lora(model: PreTrainedModel, rank: int, alpha: int, dropout: float = 0.05) -> PeftModel: ...
```

### Train (`train.py`)

**Dependencies**: Data, Model, Config

```python
def train_one_run(model_id: str, rank: int, seed: int, cfg: TrainConfig) -> float:
    """Trains LoRA adapter, returns SQuAD-v2 F1 on full validation set."""
    ...

def compute_squad_f1(predictions: list, references: list) -> float: ...
```

### Main / Sweep Driver (`main.py`)

**Dependencies**: Train, Config

```python
def run_sweep() -> None:
    """Loops MODELS x RANKS x SEEDS (72 runs), appends each F1
    to results/h-e1_rank_sweep.csv: (model,rank,seed,f1_score)."""
    ...
```

### Analyze (`analyze.py`)

**Dependencies**: Config

```python
def compute_r_opt(sweep_csv: str) -> pd.DataFrame:
    """Per (model,seed): argmax F1 over rank; ties -> geometric mean.
    Writes results/h-e1_optimal_ranks.csv."""
    ...

def fit_scaling_law(optimal_ranks: pd.DataFrame, n_bootstrap: int = 1000) -> dict:
    """OLS on log(r_opt) vs log(N); bootstrap 95% CI for alpha.
    Writes results/h-e1_scaling_fit.json: {alpha, alpha_ci_low, alpha_ci_high, c, r2}."""
    ...

def plot_scaling(fit_result: dict, optimal_ranks: pd.DataFrame) -> None:
    """Writes figures/h-e1_scaling_plot.png (log-log + fit + CI band)."""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config & data pipeline | Config dataclass, SQuAD-v2 load/tokenize | 6 | 2+1+1+2 |
| A-2 | Model + LoRA factory | Load Pythia sizes, apply PEFT LoRA config | 6 | 2+2+1+1 |
| A-3 | Train/eval single run | Training loop + SQuAD-v2 F1 scoring | 10 | 3+2+3+2 |
| A-4 | Sweep driver | Orchestrate 72 runs, checkpoint/resume, write rank_sweep.csv | 9 | 2+2+2+3 |
| A-5 | r_opt extraction | argmax per (model,seed), tie handling | 4 | 1+1+1+1 |
| A-6 | Scaling law fit | Log-linear OLS + bootstrap CI (B=1000) | 7 | 2+1+3+1 |
| A-7 | Visualization + report | Log-log plot, pass/fail check against criteria | 5 | 1+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-4], Low(4-8): [A-1, A-2, A-5, A-6, A-7]
