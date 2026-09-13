# Architecture: H-M2

**Type:** MECHANISM
**Applied:** SAM sharpness measurement pattern (Foret et al. 2021), task-specific landscape comparison

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** patterns found from base code (H-M1 code matches spec; reusable as-is for sharpness measurement)
**Analyzed Path:** `docs/youra_research/h-m1/code/`, `docs/youra_research/h-e1/code/`
**Findings:** `h-m1/code/landscape.py` provides `measure_sharpness_sam` (epsilon=0.05, grad-perturb, param-restore) — reuse directly, no re-implementation. `h-m1/code/data.py` provides `load_benchmark`/`format_for_causal_lm` — reuse for GSM8K/NQ tokenization. `h-m1/code/model.py` provides `MambaWithLoRA`/`load_proposed_model` (Mamba-only, no transformer needed for H-M2). `h-e1/code/train.py` provides `train_one_benchmark` LoRA fine-tuning loop pattern — reuse for per-task fine-tuning (new: H-M2 needs per-task checkpoints, not H-E1's multi-benchmark loop).

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| measure_sharpness_sam | `from h_m1.code.landscape import measure_sharpness_sam` | `h-m1/code/landscape.py` |
| compute_loss | `from h_m1.code.landscape import compute_loss` | `h-m1/code/landscape.py` |
| load_benchmark | `from h_m1.code.data import load_benchmark` | `h-m1/code/data.py` |
| format_for_causal_lm | `from h_m1.code.data import format_for_causal_lm` | `h-m1/code/data.py` |
| load_proposed_model | `from h_m1.code.model import load_proposed_model` | `h-m1/code/model.py` |
| MambaWithLoRA | `from h_m1.code.model import MambaWithLoRA` | `h-m1/code/model.py` |
| train_one_benchmark (pattern ref) | `from h_e1.code.train import train_one_benchmark` | `h-e1/code/train.py` |

**Verified from**: `h-m1/code/` and `h-e1/code/` (actual implementation)

---

## Module Structure

```
h-m2/code/
├── config.py
├── data.py           (adds NQ to BENCHMARKS, thin wrapper over h_m1.data)
├── finetune.py        (per-task LoRA fine-tuning, adapted from h_e1.train)
├── sharpness.py        (task-comparison wrapper over h_m1.landscape)
├── gate.py               (ratio computation + gate check)
├── run_experiment.py
└── visualize.py
```

### config.py

**Dependencies**: none

```python
LORA_CONFIG = dict(r=16, lora_alpha=32, target_modules=["in_proj", "out_proj"])
TRAIN_CONFIG = dict(lr=2e-4, epochs=3, batch_size=16, warmup_pct=0.06, seed=42)
SHARPNESS_CONFIG = dict(sam_epsilon=0.05, max_batches=100)
BENCHMARKS = {
    "gsm8k": dict(hf_id="gsm8k", subset="main", split="test", num_samples=1319),
    "nq": dict(hf_id="natural_questions", subset=None, split="validation", num_samples=3610),
}
GATE_THRESHOLD = 0.8
```

### data.py (`code/data.py`)

**Dependencies**: config.py, h_m1.code.data

```python
def load_task_loader(name: str, tokenizer, max_length: int = 512) -> "DataLoader":
    """Wraps h_m1.code.data.load_benchmark + format_for_causal_lm for gsm8k/nq; batch_size=16"""
    ...
```

### finetune.py (`code/finetune.py`)

**Dependencies**: config.py, data.py, h_m1.code.model

```python
def finetune_on_task(base_model_fn: "Callable", task_name: str, tokenizer,
                      train_config: dict = None) -> "nn.Module":
    """LoRA fine-tune load_proposed_model() on task_name for 3 epochs.
    Pattern from h_e1.code.train.train_one_benchmark, single-task variant."""
    ...
```

### sharpness.py (`code/sharpness.py`)

**Dependencies**: config.py, h_m1.code.landscape

```python
def measure_task_sharpness(model: "nn.Module", dataloader: "DataLoader",
                            max_batches: int = 100) -> dict:
    """Calls h_m1.landscape.measure_sharpness_sam per-batch, collects distribution.
    Returns {'mean_sharpness': float, 'per_batch': list[float]}"""
    ...

def compare_task_sharpness(seq_result: dict, ret_result: dict) -> dict:
    """Returns {'sequential_sharpness', 'retrieval_sharpness', 'ratio'}"""
    ...
```

### gate.py (`code/gate.py`)

**Dependencies**: config.py

```python
def evaluate_gate(compare_result: dict, threshold: float = 0.8) -> dict:
    """ratio = seq/ret; pass if ratio < threshold. Returns dict with ratio, pass, both sharpness values."""
    ...

def verify_mechanism(compare_result: dict) -> tuple:
    """Checks: sharpness computed, tasks differentiated (>0.01 delta), ratio in (0,10)"""
    ...
```

### visualize.py (`code/visualize.py`)

**Dependencies**: gate.py

```python
def plot_gate_comparison(seq_sharpness: float, ret_sharpness: float,
                          threshold: float, out_path: str) -> None:
    """Bar chart: GSM8K vs NQ sharpness with 0.8 ratio threshold line"""
    ...

def plot_sharpness_distribution(seq_per_batch: list, ret_per_batch: list, out_path: str) -> None:
    """Histogram of per-batch sharpness for both tasks"""
    ...
```

### run_experiment.py (`code/run_experiment.py`)

**Dependencies**: config.py, data.py, finetune.py, sharpness.py, gate.py, visualize.py, h_m1.code.model

```python
def main() -> dict:
    """Load tokenizer, fine-tune Mamba+LoRA separately on GSM8K/NQ (finetune.py),
    measure SAM sharpness per task (sharpness.py, 100 batches each),
    compute ratio + gate (gate.py), save figures (visualize.py) to h-m2/figures/"""
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M2-1 | Setup & config | config.py with LORA_CONFIG, TRAIN_CONFIG, SHARPNESS_CONFIG, BENCHMARKS (gsm8k+nq) | 3 | 1+0+1+1 |
| M2-2 | Data loading | Wrap h_m1.data.load_benchmark for GSM8K test (1319) + NQ validation (3610), tokenize, batch=16 | 6 | 2+2+1+1 |
| M2-3 | LoRA fine-tune GSM8K | finetune_on_task using h_m1.model.load_proposed_model, 3 epochs, save checkpoint | 8 | 2+2+2+2 |
| M2-4 | LoRA fine-tune NQ | Same finetune_on_task path applied to NQ, independent checkpoint | 4 | 1+2+1+0 |
| M2-5 | Sharpness measurement wrapper | measure_task_sharpness calling h_m1.landscape.measure_sharpness_sam over 100 batches, collect per-batch distribution | 7 | 2+3+1+1 |
| M2-6 | Task comparison + ratio | compare_task_sharpness combining seq/ret results into ratio | 3 | 1+1+1+0 |
| M2-7 | Gate + mechanism verification | evaluate_gate (ratio<0.8) + verify_mechanism checks per PRD FR-4 | 5 | 1+1+2+1 |
| M2-8 | Visualization | Bar chart (gate comparison) + histogram (per-batch distribution) to h-m2/figures/ | 5 | 2+1+1+1 |
| M2-9 | End-to-end integration run | Wire config->data->finetune(x2)->sharpness(x2)->gate->visualize->report | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M2-9], Low(4-8): [M2-1, M2-2, M2-3, M2-4, M2-5, M2-6, M2-7, M2-8]
