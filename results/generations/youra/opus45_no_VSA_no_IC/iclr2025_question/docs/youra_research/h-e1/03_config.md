# Configuration: h-e1 (EXISTENCE PoC)

Applied: fixed-single-config-poc pattern (KB search returned only unrelated diffusion-model results; used EXISTENCE PoC convention instead).

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: Hardcoded dict (module-level constants), per architecture spec

---

EXISTENCE PoC: single fixed config, no hyperparameter grid, 1 seed.

## A-1: Config module [Complexity: 2, Budget: 1 subtask]

**Applied**: Standard PyTorch/HF reproducibility defaults (fixed seed, no tuning)

### Configuration (Hardcoded dict — matches architecture 03_architecture.md)

```python
# config.py
SEED = 42

MODELS = {
    "llama3-8b": {
        "id": "meta-llama/Meta-Llama-3-8B-Instruct",
        "n_layers": 32,
        "hidden_dim": 4096,
    },
    "mistral-7b": {
        "id": "mistralai/Mistral-7B-Instruct-v0.2",
        "n_layers": 32,
        "hidden_dim": 4096,
    },
    "qwen2-7b": {
        "id": "Qwen/Qwen2-7B-Instruct",
        "n_layers": 28,
        "hidden_dim": 3584,
    },
}

NLI_MODEL_ID = "microsoft/deberta-v3-large-mnli"

N_SAMPLES = 5
TEMPERATURE = 0.7
TRAIN_SPLIT = 0.8
LAYER_FRACTION = 2 / 3  # candidate probe layer depth (SLT position)

RESULTS_DIR = "h-e1/results"
FIGURES_DIR = "h-e1/figures"

# Model loading (FR-2): fp16 + device_map=auto, output_hidden_states=True
TORCH_DTYPE = "float16"
DEVICE_MAP = "auto"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Model loading config | `MODELS` dict entries (HF id, n_layers, hidden_dim) + `TORCH_DTYPE`/`DEVICE_MAP` consumed by `ModelWrapper.load()` |

---

## YAML Schema Equivalent (reference only — code uses Python dict above)

```yaml
seed: 42
models:
  llama3-8b:
    id: meta-llama/Meta-Llama-3-8B-Instruct
    n_layers: 32
    hidden_dim: 4096
  mistral-7b:
    id: mistralai/Mistral-7B-Instruct-v0.2
    n_layers: 32
    hidden_dim: 4096
  qwen2-7b:
    id: Qwen/Qwen2-7B-Instruct
    n_layers: 28
    hidden_dim: 3584
nli_model_id: microsoft/deberta-v3-large-mnli
n_samples: 5
temperature: 0.7
train_split: 0.8
layer_fraction: 0.6667
results_dir: h-e1/results
figures_dir: h-e1/figures
torch_dtype: float16
device_map: auto
```

## Python Dataclass Equivalent (reference only — NOT used alongside dict; pick one at implementation time)

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class ModelSpec:
    id: str
    n_layers: int
    hidden_dim: int

@dataclass(frozen=True)
class ExperimentConfig:
    seed: int = 42
    models: dict[str, ModelSpec] = field(default_factory=lambda: {
        "llama3-8b": ModelSpec("meta-llama/Meta-Llama-3-8B-Instruct", 32, 4096),
        "mistral-7b": ModelSpec("mistralai/Mistral-7B-Instruct-v0.2", 32, 4096),
        "qwen2-7b": ModelSpec("Qwen/Qwen2-7B-Instruct", 28, 3584),
    })
    nli_model_id: str = "microsoft/deberta-v3-large-mnli"
    n_samples: int = 5
    temperature: float = 0.7
    train_split: float = 0.8
    layer_fraction: float = 2 / 3
    results_dir: str = "h-e1/results"
    figures_dir: str = "h-e1/figures"
    torch_dtype: str = "float16"
    device_map: str = "auto"
```

**Recommendation for Phase 4**: Use the hardcoded dict (`config.py` module-level constants) as shown in the architecture doc — simplest for a PoC with no tuning.
