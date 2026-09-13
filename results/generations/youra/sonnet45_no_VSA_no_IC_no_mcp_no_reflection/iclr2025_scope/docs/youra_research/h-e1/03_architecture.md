# System Architecture: H-E1

**Hypothesis:** Mamba-130M checkpoint validation  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-08-28  
**Author:** yoon303@ust.ac.kr

Applied: DL minimal inference pattern, zero-shot evaluation pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch - no existing code  
**Analyzed Path**: N/A  
**Findings**: First hypothesis in pipeline, no prior codebase to analyze

---

## Module Structure

### CheckpointLoader (`code/model.py`)

**Dependencies**: transformers, torch

```python
class CheckpointLoader:
    def __init__(self, model_name: str, device: str, dtype: str): ...
    def load_model(self) -> AutoModelForCausalLM: ...
    def load_tokenizer(self) -> AutoTokenizer: ...
    def get_memory_stats(self) -> dict: ...
```

### DataLoader (`code/data.py`)

**Dependencies**: datasets, transformers

```python
class GLUELoader:
    def __init__(self, task_names: list[str]): ...
    def load_task(self, task_name: str, split: str) -> Dataset: ...
    def get_task_info(self, task_name: str) -> dict: ...
```

### ZeroShotEvaluator (`code/evaluate.py`)

**Dependencies**: torch, numpy, code.model

```python
class ZeroShotEvaluator:
    def __init__(self, model, tokenizer, device: str): ...
    def classify(self, text: str, choices: list[str]) -> int: ...
    def evaluate_task(self, dataset, task_name: str, batch_size: int) -> dict: ...
```

### Experiment (`code/train.py`)

**Dependencies**: code.model, code.data, code.evaluate

```python
def run_experiment(config: dict) -> dict: ...
def validate_memory(model, threshold_gb: float) -> bool: ...
def save_results(results: dict, output_path: str): ...
```

### Config (`code/config.py`)

**Dependencies**: None

```python
CHECKPOINT_NAME: str = "state-spaces/mamba-130m-hf"
GLUE_TASKS: list[str] = ["mnli", "qqp", "sst2"]
BATCH_SIZE: int = 16
MAX_LENGTH: int = 512
DEVICE: str = "cuda"
DTYPE: str = "float16"
MEMORY_LIMIT_GB: float = 16.0
RANDOM_SEED: int = 42
```

### Visualization (`code/visualize.py`)

**Dependencies**: matplotlib, code.evaluate

```python
def plot_gate_metrics(results: dict, output_dir: str): ...
def generate_performance_table(results: dict, output_dir: str): ...
```

---

## File Organization

```
h-e1/
├── code/
│   ├── model.py         # CheckpointLoader
│   ├── data.py          # GLUELoader
│   ├── evaluate.py      # ZeroShotEvaluator
│   ├── train.py         # Experiment runner
│   ├── config.py        # Fixed configuration
│   └── visualize.py     # Plotting functions
├── figures/             # Created at runtime
└── results.json         # Created at runtime
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1-1 | Setup infrastructure | Install dependencies, verify CUDA, create directories | 5 | 1+1+1+2 (module=1, deps=1, algo=1, integration=2) |
| E1-2 | Implement checkpoint loading | CheckpointLoader class with HF integration | 8 | 2+2+2+2 (module=2, deps=2, algo=2, integration=2) |
| E1-3 | Implement data loading | GLUELoader for three tasks | 7 | 2+2+1+2 (module=2, deps=2, algo=1, integration=2) |
| E1-4 | Implement zero-shot evaluator | Log-probability classification | 10 | 3+2+3+2 (module=3, deps=2, algo=3, integration=2) |
| E1-5 | Run experiments | Execute evaluation, validate gates | 9 | 2+2+2+3 (module=2, deps=2, algo=2, integration=3) |

**Distribution**: High(9-13): [E1-4, E1-5], Medium(6-8): [E1-2, E1-3], Low(4-5): [E1-1]

---

## Data Flow

1. Config → CheckpointLoader → Model/Tokenizer
2. Config → GLUELoader → Validation datasets
3. Model + Tokenizer + Dataset → ZeroShotEvaluator → Accuracy metrics
4. Metrics → Visualization → figures/
5. Metrics → JSON → results.json

---

## Memory Constraints

- Model FP16: ~260MB
- Activations (batch=16, seq=512): ~2GB
- Dataset cache: ~500MB
- Total estimate: <3GB (well under 16GB limit)

---

## Gate Validation Flow

```python
# E1-5 implements this check
gates = {
    "checkpoint_loads": model is not None,
    "memory_ok": peak_memory < 16.0,
    "mnli_acc": results["mnli"]["accuracy"] > 0.333,
    "qqp_acc": results["qqp"]["accuracy"] > 0.50,
    "sst2_acc": results["sst2"]["accuracy"] > 0.50
}
assert all(gates.values()), f"Gate failures: {gates}"
```

---

## Dependencies

**External Libraries:**
- transformers>=4.35.0 (Mamba model)
- datasets>=2.14.0 (GLUE)
- torch>=2.0.0
- numpy>=1.24.0
- matplotlib>=3.7.0
- evaluate>=0.4.0

**Hardware:**
- GPU: 16GB VRAM
- RAM: 32GB
- Storage: 10GB

---

## Implementation Notes

**EXISTENCE simplifications:**
- Single config file (no hyperparameter grid)
- No ablation modules
- Minimal error handling (fail fast)
- Basic visualizations only

**Not included (out of PoC scope):**
- Training loops
- LoRA adapters
- Model architecture modifications
- Comprehensive logging infrastructure
