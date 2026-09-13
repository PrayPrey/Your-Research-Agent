# Architecture: H-E1 (SSI Contamination Detection — EXISTENCE PoC)

Applied: LoRA fine-tuning pattern (PEFT) for contamination injection
Applied: Confidence-variance behavioral probe pattern (novel, no prior implementation)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base hypothesis or existing codebase.

---

## Scope Note (EXISTENCE Rules Applied)

- 5 Epic tasks (within 3-5 range)
- No ablation modules (FR-5 ablations deferred post-gate; PoC only implements PASS/FAIL gate: AUC + Cohen's d)
- Single fixed config, single train script, single model script

---

## Module Structure

### data.py (`h-e1/code/data.py`)

**Dependencies**: datasets (HuggingFace)

```python
def load_mmlu() -> tuple[Dataset, Dataset]:
    """Returns (test_split, auxiliary_train_split)"""

def sample_contamination_subset(aux_train: Dataset, frac: float, seed: int) -> Dataset:
    """frac in {0.0, 0.10, 0.50} -> MMLU items for injection"""

def generate_paraphrases(item: dict, k: int = 20) -> list[str]:
    """Rule-based synonym swap paraphrasing (PoC: single method, no T5/GPT-4 split)"""

def format_mmlu_prompt(item: dict) -> str:
    """Question + choices -> multiple-choice prompt string"""
```

### model.py (`h-e1/code/model.py`)

**Dependencies**: transformers, peft, torch

```python
def load_base_model() -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Loads mistralai/Mistral-7B-v0.1, BF16, device_map=auto"""

def build_lora_config(rank: int = 16, alpha: int = 32) -> LoraConfig: ...

def inject_contamination(base_model, tokenizer, contamination_items: Dataset,
                          general_data: Dataset, lora_cfg: LoraConfig) -> PeftModel:
    """LoRA fine-tune on general + contamination data (3 epochs, lr=2e-4)"""

def get_answer_token_ids(tokenizer) -> list[int]:
    """Token IDs for 'A','B','C','D'"""
```

### ssi.py (`h-e1/code/ssi.py`)

**Dependencies**: model.py (inference only), numpy, torch

```python
def extract_confidence(model, tokenizer, prompt: str, answer_tokens: list[int]) -> float:
    """Softmax over answer-token logits -> max prob"""

def compute_ssi(model, tokenizer, item: dict, paraphrases: list[str],
                 answer_tokens: list[int]) -> tuple[float, list[float]]:
    """SSI = 1 / (variance(confidences) + 1e-8); returns (ssi, confidences)"""

def compute_ssi_batch(model, tokenizer, items: list[dict], answer_tokens: list[int],
                       k_paraphrases: int = 20) -> list[float]:
    """Runs compute_ssi over item list, returns SSI scores"""
```

### train.py (`h-e1/code/train.py`)

**Dependencies**: data.py, model.py, ssi.py

```python
def run_experiment(config: Config) -> None:
    """
    1. Load MMLU test + aux_train
    2. Build clean/low/high contaminated models via inject_contamination
    3. Sample test subset (config.n_eval_items) + generate paraphrases
    4. compute_ssi_batch per model variant
    5. Save raw SSI scores to results/ssi_scores.json
    """
```

### evaluate.py (`h-e1/code/evaluate.py`)

**Dependencies**: sklearn, scipy, matplotlib, ssi_scores.json (from train.py)

```python
def evaluate_ssi_discrimination(ssi_clean: list[float], ssi_contaminated: list[float]) -> dict:
    """Returns {"auc": float, "cohens_d": float}"""

def plot_gate_metrics(achieved_auc: float, target: float = 0.7) -> None:
    """Bar chart: target vs achieved AUC -> figures/gate_metrics.png"""

def plot_ssi_distribution(ssi_clean, ssi_low, ssi_high) -> None:
    """Violin/box plot -> figures/ssi_distribution.png"""

def plot_roc_curve(labels, scores) -> None:
    """ROC curve with AUC annotation -> figures/roc_curve.png"""

def plot_contamination_level_analysis(levels: list[float], mean_ssi: list[float]) -> None:
    """Line plot SSI vs contamination % -> figures/contamination_level.png"""

def plot_confidence_variance_histogram(confidences_per_item: list[list[float]]) -> None:
    """Histogram of per-item confidence variance -> figures/variance_hist.png"""
```

### config.py (`h-e1/code/config.py`)

```python
@dataclass
class Config:
    model_id: str = "mistralai/Mistral-7B-v0.1"
    lora_rank: int = 16
    lora_alpha: int = 32
    lr: float = 2e-4
    batch_size: int = 4
    grad_accum: int = 8
    epochs: int = 3
    contamination_levels: tuple = (0.0, 0.10, 0.50)
    k_paraphrases: int = 20
    n_eval_items: int = 200  # PoC subset, not full 14,042
    seed: int = 42
    auc_target: float = 0.7
    cohens_d_target: float = 0.5
```

---

## File Organization

```
h-e1/code/
  config.py
  data.py
  model.py
  ssi.py
  train.py
  evaluate.py
h-e1/results/
  ssi_scores.json
h-e1/figures/
  gate_metrics.png
  ssi_distribution.png
  roc_curve.png
  contamination_level.png
  variance_hist.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Data pipeline | MMLU load, contamination sampling, paraphrase gen, prompt formatting | 10 | 2+2+3+3 |
| E-2 | Model + LoRA fine-tuning | Load Mistral-7B, LoRA config, contamination injection x3 variants | 14 | 4+3+4+3 |
| E-3 | SSI computation | Confidence extraction, variance-based SSI batch scoring | 9 | 2+2+3+2 |
| E-4 | Train orchestration | Wire data/model/ssi, run full experiment, persist scores | 8 | 2+3+1+2 |
| E-5 | Evaluation + visualization | AUC, Cohen's d, 5 required plots, gate check | 9 | 2+2+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [E-2], Medium(9-13): [E-1, E-3, E-5], Low(4-8): [E-4]

---

## External Dependencies

N/A — green-field project, no base hypothesis code to reuse.
