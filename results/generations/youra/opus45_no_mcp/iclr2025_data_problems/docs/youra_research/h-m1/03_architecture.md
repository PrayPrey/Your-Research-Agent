# Architecture: H-M1 (Contamination Injection Creates Training Exposure — MECHANISM)

Applied: LoRA fine-tuning contamination injection pattern (PEFT, reused from H-E1)
Applied: Item-level accuracy tracking pattern for mechanism validation (DL experiment architecture contamination)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Actual H-E1 code read directly (file read, not symbol search — Serena MCP unavailable in this run; used direct file inspection as fallback per PRD mandate to trust actual code over specs)
**Analyzed Path**: `h-e1/code/data.py`, `h-e1/code/model.py`, `h-e1/code/config.py`
**Findings**: H-E1 implements `load_mmlu()`, `load_base_model()`, `build_lora_config()`, `inject_contamination()` (single-dataset, no separate "general" corpus), `format_training_example()`. Signatures differ from 03_architecture.md spec (e.g., `inject_contamination` takes only `contamination_items`, not `general_data`; LoRA target_modules is `["q_proj","v_proj"]` not 4 modules). H-M1 reuses these directly and extends `build_lora_config` call site with k_proj/o_proj per PRD FR-2.2.

---

## Module Structure

### data.py (`h-m1/code/data.py`)

**Dependencies**: H-E1 `data.load_mmlu` (reused), datasets

```python
from h_e1.code.data import load_mmlu  # reused as-is

def sample_contamination_ids(test_set: Dataset, frac: float, seed: int) -> set[int]:
    """Deterministic index selection from TEST set (not aux_train) per PRD FR-1.2/1.5"""

def build_training_dataset(test_set: Dataset, contaminated_ids: set[int]) -> Dataset:
    """Subset test_set by contaminated_ids -> Dataset for injection"""

def format_mmlu_prompt(item: dict) -> str:
    """Question: {q}\\nA. {A}...\\nAnswer: {correct} -- PRD FR-1.3 exact format"""
```

### model.py (`h-m1/code/model.py`)

**Dependencies**: H-E1 `model.load_base_model`, `model.build_lora_config` (reused), peft, transformers

```python
from h_e1.code.model import load_base_model  # reused as-is

def build_lora_config_m1(rank: int = 16, alpha: int = 32, dropout: float = 0.05) -> LoraConfig:
    """target_modules=[q_proj,v_proj,k_proj,o_proj] per PRD FR-2.2 (extends H-E1's 2-module config)"""

def inject_contamination(base_model, tokenizer, contaminated_items: Dataset,
                          lora_cfg: LoraConfig, seed: int,
                          epochs: int = 3, lr: float = 2e-5,
                          batch_size: int = 4, grad_accum: int = 8) -> PeftModel:
    """Fine-tune; set_seed(seed) before Trainer init for reproducibility"""

def get_answer_token_ids(tokenizer) -> list[int]:
    """Reused from H-E1 model.py as-is"""
```

### evaluate.py (`h-m1/code/evaluate.py`)

**Dependencies**: model.py, numpy, lm-eval-harness (optional) or direct logit extraction

```python
def evaluate_full_test_set(model, tokenizer, test_set: Dataset,
                            answer_token_ids: list[int]) -> list[dict]:
    """Runs all 14,042 items -> [{"id": int, "correct": bool, "pred": str}, ...]"""

def compute_item_accuracy(eval_results: list[dict], contaminated_ids: set[int]) -> dict:
    """Returns {"contaminated_accuracy": float, "clean_accuracy": float, "effect_size": float}"""
```

### mechanism.py (`h-m1/code/mechanism.py`)

**Dependencies**: evaluate.py, numpy

```python
def verify_contamination_mechanism(cont_acc: float, clean_acc: float) -> dict:
    """mechanism_active = cont_acc > clean_acc; logs [MECHANISM CHECK] per PRD FR-5.3"""

def verify_monotonic_trend(effect_sizes_by_level: dict[float, float]) -> bool:
    """effect_size(5%) < effect_size(10%) < effect_size(20%) < effect_size(50%)"""

def aggregate_across_seeds(results_per_seed: list[dict]) -> dict:
    """Mean/std of effect_size across 3 seeds per contamination level"""
```

### train.py (`h-m1/code/train.py`)

**Dependencies**: data.py, model.py, evaluate.py, mechanism.py

```python
def run_experiment(config: Config) -> None:
    """
    For each seed in (42,123,456):
      For each level in (0,0.05,0.10,0.20,0.50):
        1. sample_contamination_ids, build_training_dataset
        2. load_base_model, build_lora_config_m1, inject_contamination
        3. evaluate_full_test_set (14042 items)
        4. compute_item_accuracy, verify_contamination_mechanism
    aggregate_across_seeds, verify_monotonic_trend
    Save results/mechanism_results.json
    """
```

### visualize.py (`h-m1/code/visualize.py`)

**Dependencies**: matplotlib, mechanism_results.json

```python
def plot_accuracy_by_level(results: dict) -> None:
    """Line plot contaminated vs clean acc across 5 levels -> figures/accuracy_by_level.png"""

def plot_effect_size_bars(results: dict) -> None:
    """Bar chart effect_size per level -> figures/effect_size.png"""

def plot_item_accuracy_distribution(eval_results: list[dict], contaminated_ids: set) -> None:
    """Histogram contaminated vs clean per-item accuracy -> figures/item_distribution.png"""
```

### config.py (`h-m1/code/config.py`)

```python
@dataclass
class Config:
    model_id: str = "mistralai/Mistral-7B-v0.1"
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: tuple = ("q_proj", "v_proj", "k_proj", "o_proj")
    lr: float = 2e-5
    batch_size: int = 4
    grad_accum: int = 8
    epochs: int = 3
    contamination_levels: tuple = (0.0, 0.05, 0.10, 0.20, 0.50)
    seeds: tuple = (42, 123, 456)
    n_test_items: int = 14042
    effect_size_target: float = 0.05
```

---

## File Organization

```
h-m1/code/
  config.py
  data.py
  model.py
  evaluate.py
  mechanism.py
  train.py
  visualize.py
h-m1/results/
  mechanism_results.json
h-m1/figures/
  accuracy_by_level.png
  effect_size.png
  item_distribution.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Data pipeline extension | Reuse load_mmlu; add test-set contamination sampling (5 levels), prompt formatting | 8 | 2+2+2+2 |
| M-2 | LoRA config extension | Extend H-E1 LoRA to 4 target modules per FR-2.2 | 4 | 1+1+1+1 |
| M-3 | Contamination injection orchestration | Train 5 levels x 3 seeds = 15 model variants via reused inject_contamination | 15 | 3+4+4+4 |
| M-4 | Full test-set evaluation | Evaluate 14,042 items per variant, extract per-item correctness | 12 | 3+3+3+3 |
| M-5 | Item-level accuracy aggregation | Split contaminated/clean, compute effect_size per level/seed | 8 | 2+2+2+2 |
| M-6 | Mechanism verification | mechanism_active check, monotonic trend check, cross-seed aggregation | 9 | 2+2+3+2 |
| M-7 | Visualization | 3 required figures (line, bar, distribution) | 6 | 2+1+1+2 |
| M-8 | Experiment orchestration | Wire full seed x level loop, persist results JSON, logging | 10 | 3+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [M-3], Medium(9-13): [M-4, M-6, M-8], Low(4-8): [M-1, M-2, M-5, M-7]

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| load_mmlu | `from h_e1.code.data import load_mmlu` | `h-e1/code/data.py` |
| load_base_model | `from h_e1.code.model import load_base_model` | `h-e1/code/model.py` |
| get_answer_token_ids | `from h_e1.code.model import get_answer_token_ids` | `h-e1/code/model.py` |
| format_training_example | `from h_e1.code.model import format_training_example` | `h-e1/code/model.py` |

**Verified from**: `h-e1/code/data.py`, `h-e1/code/model.py`, `h-e1/code/config.py` (actual implementation, read directly — signatures differ from H-E1's own 03_architecture.md spec, e.g. `inject_contamination` has no `general_data` param and LoRA defaults to 2 target modules not 4).
