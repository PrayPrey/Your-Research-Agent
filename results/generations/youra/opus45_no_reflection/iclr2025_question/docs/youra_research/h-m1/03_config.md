# Config: H-M1 (Forward Hook Non-Intrusiveness Verification)

**Applied**: Standard PyTorch/HF experiment dataclass pattern (single fixed config, no sweep — MUST_WORK gate verification, not tuning)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: Config classes verified from base code (read via Read tool — `h-e1/code/config.py`)
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`
**Pattern Used**: dataclass

---

## M-1: Setup config & data loading [Complexity: 6, Budget: 6]

**Applied**: Standard PyTorch/HF experiment dataclass pattern

### Configuration (Python Dataclass)

```python
@dataclass
class Config:
    seed: int = 42
    model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    torch_dtype: str = "float16"   # Non-standard vs H-E1 (bfloat16): PRD FR requires float16
    device_map: str = "auto"
    target_layer: int = 19
    n_samples: int = 1000
    max_new_tokens: int = 128
    identity_gate: float = 1.0
    overhead_gate_pct: float = 10.0
    memory_gate_pct: float = 20.0
    figures_dir: str = "figures/"
    cache_dir: str = "cache/"

def set_seed(seed: int = 42) -> None: ...
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M1-1 | Config dataclass | Define `Config` per above, `CFG = Config()` |
| C-M1-2 | Data loading | `load_triviaqa_subset(n=1000)` (reuse H-E1 `load_triviaqa`/`format_prompt` logic, split="validation[:1000]") |

---

## M-2: HiddenStateExtractor [Complexity: 10, Budget: 10]

**Applied**: Context-managed hook lifecycle (multigrid Recorder pattern), non-intrusive read (hook returns None)

### Configuration (Python Dataclass)

No new config fields — uses `Config.target_layer`. Extractor accepts `layer_indices: list[int] = [CFG.target_layer]`.

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-M2-1 | Hook attach/detach | `__enter__`/`__exit__`, `register_forward_hook`, `handles` list cleanup |
| C-M2-2 | Capture logic | `_create_hook` stores `output[0].detach().cpu()` into `hidden_states` dict, returns None |

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class Config:
    seed: int = 42
    model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    torch_dtype: str = "bfloat16"   # H-M1 overrides to "float16" per PRD FR
    device_map: str = "auto"
    target_layer: int = 19
    hidden_dim: int = 4096
    dataset_name: str = "trivia_qa"
    dataset_config: str = "rc"
    train_size: int = 9500
    val_size: int = 1700
    max_new_tokens: int = 32        # H-M1 overrides to 128 per PRD FR-2
    figures_dir: str = "figures/"
    cache_dir: str = "cache/"

def set_seed(seed: int = 42) -> None: ...
```

**Not inherited** (H-E1 probe-training fields unused in H-M1, a pure mechanism-verification hypothesis): `lr`, `epochs`, `batch_size`, `optimizer`, `loss`, `auroc_gate`, `auroc_baseline`, `train_size`, `val_size`.

**Reused as-is**: `seed=42`, `model_name`, `device_map="auto"`, `target_layer=19`, `dataset_name="trivia_qa"`, `dataset_config="rc"`, `figures_dir`, `cache_dir`, `set_seed()`.

**Verified from**: `docs/youra_research/h-e1/code/config.py` (actual implementation)

---

## Hyperparameter Defaults Justification

| Field | Value | Justification |
|-------|-------|----------------|
| `torch_dtype` | `"float16"` | PRD FR/§5.1 explicitly requires float16 (differs from H-E1's bfloat16) |
| `target_layer` | `19` | Same layer as H-E1 (60% depth) for consistency of extraction point |
| `n_samples` | `1000` | PRD §4.1 fixed subset size |
| `max_new_tokens` | `128` | PRD FR-2 fixed generation length |
| `identity_gate` | `1.0` | PRD §6.1 MUST_WORK gate: 100% output identity |
| `overhead_gate_pct` | `10.0` | PRD §6.2 secondary gate: <10% inference overhead |
| `memory_gate_pct` | `20.0` | PRD §6.2 secondary gate: <20% GPU peak overhead |
| `seed` | `42` | NFR-1 reproducibility, greedy decoding, deterministic |
