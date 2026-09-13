# Config: h-m1

**Applied**: Standard PyTorch/HuggingFace dataclass defaults (KB search returned no closely-matched DL config pattern; using conventional PEFT/transformers defaults per PRD FR-2/FR-3).

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (no `code/` folder, no base_hypothesis_folder)
**Config Files Found**: None
**Pattern Used**: Dataclass (Python)

---

## A-1: Config & Seeding [Complexity: 4, Budget: 4]

**Applied**: Constant lists + dataclass for training hyperparams (standard experiment sweep pattern)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

MODEL_SIZES: list[str] = ["1b", "2.8b", "6.9b", "12b"]
MODEL_PARAMS: dict[str, float] = {"1b": 1e9, "2.8b": 2.8e9, "6.9b": 6.9e9, "12b": 12e9}
MODEL_HF_IDS: dict[str, str] = {
    "1b": "EleutherAI/pythia-1b",
    "2.8b": "EleutherAI/pythia-2.8b",
    "6.9b": "EleutherAI/pythia-6.9b",
    "12b": "EleutherAI/pythia-12b",
}
RANKS: list[int] = [4, 8, 16, 32, 64, 128]
MAX_SEQ_LEN: int = 512
SEED: int = 42

@dataclass
class TrainConfig:
    epochs: int = 3
    lr: float = 1e-4
    batch_size: int = 4
    grad_accum: int = 4
    warmup_ratio: float = 0.1
    # LoRA-specific (alpha scales with rank per FR-3)
    lora_alpha_multiplier: int = 2   # alpha = rank * 2
    lora_dropout: float = 0.05
    lora_target_modules: list[str] = field(default_factory=lambda: ["query_key_value"])

@dataclass
class DataConfig:
    train_n: int = 5000
    val_n: int = 1000
    max_len: int = MAX_SEQ_LEN
    dataset_name: str = "squad_v2"
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Constants | MODEL_SIZES, MODEL_PARAMS, MODEL_HF_IDS, RANKS |
| C-1-2 | TrainConfig | Dataclass with LoRA/AdamW/warmup fields |
| C-1-3 | DataConfig | Dataclass for SQuAD v2.0 sample sizes, seq len |
| C-1-4 | Seed utils | `set_seed(seed: int)` — sets torch/numpy/random/cuda seeds |

---

## A-3: Model Loading [Complexity: 9, Budget: 2 subtasks allocated for config]

**Applied**: HF `device_map="auto"` + fp16 loading pattern (standard for multi-GPU large model inference)

### Configuration (Python Dataclass)

```python
@dataclass
class ModelLoadConfig:
    torch_dtype: str = "float16"
    device_map: str = "auto"
    cache_dir: str = "./model_cache"
    trust_remote_code: bool = False
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-3-1 | ModelLoadConfig | fp16 + device_map="auto" + local cache_dir dataclass |
| C-3-2 | load_base_model wiring | Use MODEL_HF_IDS + ModelLoadConfig to instantiate model/tokenizer |

---

## Notes

- LoRA `PeftConfig` (rank, alpha, dropout, target_modules) is constructed at runtime in `model.py` from `TrainConfig` fields — not a separate config class, avoids duplicate config for a single derived value (`alpha = rank * lora_alpha_multiplier`).
- No YAML — single-run PoC-style sweep script, dataclasses are copy-paste ready for `main.py`.
- Total combos: `len(MODEL_SIZES) * len(RANKS)` = 24, no separate config needed for sweep bookkeeping (computed in `main.py`).
