# Architecture: H-M1 (IPCR Routing)

Applied: PEFT multi-adapter `load_adapter`/`set_adapter` pattern (official HF PEFT conceptual guide).

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no code to analyze. H-E1 has no `code/` folder (probe was not persisted as artifact/module); H-M1 must retrain the MiniLM linear probe internally using the same protocol described in H-E1 docs.
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No external module imports.

---

## Module Structure

### IPCRRouter (`src/router.py`)

**Dependencies**: sentence-transformers, torch

```python
class IPCRRouter:
    def __init__(self, encoder_name: str, adapter_names: list[str], probe_path: str | None = None): ...
    def fit(self, embeddings: np.ndarray, labels: np.ndarray) -> None: ...
    def route(self, instruction: str) -> str: ...
    def route_topk(self, instruction: str, k: int = 3) -> list[str]: ...
    def save(self, path: str) -> None: ...
    def load(self, path: str) -> None: ...
```

### LoRAManager (`src/lora_manager.py`)

**Dependencies**: transformers, peft, IPCRRouter

```python
class LoRAManager:
    def __init__(self, base_model_id: str, adapter_paths: dict[str, str]): ...
    def load_all_adapters(self) -> None: ...
    def set_active(self, adapter_name: str) -> None: ...
    def set_uniform(self) -> None: ...  # set_adapters([all], weights=[1/k]*k)
    def generate(self, instruction: str, **gen_kwargs) -> str: ...
```

### AdapterTrainer (`src/train_lora.py`)

**Dependencies**: transformers, peft, datasets

```python
def train_lora_adapter(base_model_id: str, task_family: str, dataset, output_dir: str,
                        rank: int = 16, alpha: int = 32, lr: float = 2e-4,
                        epochs: int = 3, batch_size: int = 8) -> str: ...  # returns adapter path

def train_all_adapters(base_model_id: str, task_families: list[str], flan_dataset, output_root: str) -> dict[str, str]: ...
```

### EvaluationPipeline (`src/evaluate.py`)

**Dependencies**: LoRAManager, IPCRRouter, evaluate (HF)

```python
class EvaluationPipeline:
    def __init__(self, lora_manager: LoRAManager, router: IPCRRouter, task_metric_map: dict[str, str]): ...
    def eval_oracle(self, held_out_data: dict) -> dict[str, float]: ...
    def eval_ipcr(self, held_out_data: dict) -> dict[str, float]: ...
    def eval_random(self, held_out_data: dict) -> dict[str, float]: ...
    def eval_uniform(self, held_out_data: dict) -> dict[str, float]: ...
    def compute_relative_score(self, ipcr: dict, oracle: dict) -> float: ...
    def paired_ttest(self, ipcr_scores: list[float], uniform_scores: list[float]) -> tuple[float, float]: ...
```

### Visualization (`src/visualize.py`)

**Dependencies**: matplotlib

```python
def plot_gate_comparison(results: dict[str, float], out_path: str) -> None: ...
def plot_per_family_breakdown(results: dict, out_path: str) -> None: ...
def plot_routing_confusion(y_true: list, y_pred: list, labels: list, out_path: str) -> None: ...
def plot_confidence_vs_performance(confidences: list, scores: list, out_path: str) -> None: ...
```

### Data (`src/data.py`)

**Dependencies**: datasets (HF)

```python
def load_flan_families(task_families: list[str], min_samples: int = 500) -> dict[str, list]: ...
def split_train_heldout(all_families: list[str], k_heldout: int, seed: int = 42) -> tuple[list, list]: ...
```

### Config (`config.py`)

```python
BASE_MODEL_ID = "meta-llama/Llama-2-7b-chat-hf"
ENCODER_ID = "sentence-transformers/all-MiniLM-L6-v2"
LORA_RANK = 16
LORA_ALPHA = 32
TARGET_MODULES = ["q_proj", "v_proj"]
N_ADAPTERS = 8
N_HELDOUT_FAMILIES = 8
SEED = 42
MIN_SAMPLES_PER_FAMILY = 500
```

### Entrypoint (`run_experiment.py`)

```python
def main(): ...  # orchestrates: data -> train adapters -> fit router -> evaluate -> visualize -> save results
```

---

## File Organization

```
h-m1/code/
  config.py
  run_experiment.py
  src/
    data.py
    router.py
    lora_manager.py
    train_lora.py
    evaluate.py
    visualize.py
  checkpoints/          # trained LoRA adapters + probe weights
  figures/              # output plots
  results/              # metrics JSON, stats
```

---

## Data Flow

1. `data.py` loads FLAN, splits N-k train families / k held-out families (seed=42)
2. `train_lora.py` trains 8 task-specific LoRAs on train families → saved to `checkpoints/`
3. `router.py` embeds train instructions (MiniLM), fits linear probe on adapter labels → saved to `checkpoints/probe.pt`
4. `lora_manager.py` loads base model once + all 8 adapters
5. `evaluate.py` runs held-out families through Oracle / IPCR / Random / Uniform conditions, using `router.route()` to select adapter for IPCR, computing task-appropriate metrics (accuracy/ROUGE-L/EM)
6. Paired t-test IPCR vs Uniform
7. `visualize.py` renders gate comparison chart (mandatory) + 3 additional figures to `figures/`
8. Results written to `results/metrics.json`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Load FLAN, split train/held-out families, min-sample filtering | 8 | 2+2+2+2 |
| A-2 | LoRA training pipeline | Train 8 task-specific LoRAs (AdamW, r=16, 3 epochs) | 14 | 4+3+4+3 |
| A-3 | IPCR router (probe retrain) | Embed instructions w/ MiniLM, train linear probe, save/load | 10 | 3+2+3+2 |
| A-4 | LoRAManager multi-adapter setup | Load base model + 8 adapters, set_adapter/set_adapters | 9 | 3+3+2+1 |
| A-5 | Oracle + Random baselines | Ground-truth routing, random routing eval | 6 | 2+1+1+2 |
| A-6 | Uniform baseline | Equal-weight adapter combination eval | 6 | 2+2+1+1 |
| A-7 | IPCR evaluation path | Route via probe, generate, score per task type | 11 | 3+3+3+2 |
| A-8 | Task-appropriate metrics | Accuracy/ROUGE-L/EM dispatch by task type | 7 | 2+2+2+1 |
| A-9 | Statistical testing | Paired t-test IPCR vs Uniform, relative-to-oracle score | 6 | 1+2+2+1 |
| A-10 | Visualization suite | Gate chart (mandatory) + 3 additional figures | 8 | 3+1+2+2 |
| A-11 | Experiment orchestration | run_experiment.py wiring all stages, seed control, logging | 9 | 3+3+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2], Medium(9-13): [A-3, A-4, A-7, A-11], Low(4-8): [A-1, A-5, A-6, A-8, A-9, A-10]
