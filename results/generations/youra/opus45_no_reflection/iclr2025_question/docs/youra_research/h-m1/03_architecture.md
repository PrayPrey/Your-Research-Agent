# Architecture: H-M1 (Forward Hook Non-Intrusiveness Verification)

**Type:** MECHANISM | **Gate:** MUST_WORK (100% output identity)

Applied: PyTorch register_forward_hook non-intrusive read pattern (return None) + context-managed handle cleanup (multigrid Recorder pattern)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: Patterns found from base code (read directly via Read tool; Serena project not registered for this workspace path, so file-level inspection used instead)
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**:
- `h-e1/code/model.py` has `HiddenStateExtractor` but WITHOUT context-manager (`__enter__`/`__exit__`) and captures only last-token hidden state (`output[0][:, -1, :]`) — not reusable as-is for H-M1, which needs full-sequence capture during `generate()` and context-manager lifecycle per PRD FR-1.
- `h-e1/code/config.py` defines `Config` dataclass (seed=42, model_name, target_layer=19, torch_dtype="bfloat16") — reuse pattern, but H-M1 PRD specifies `float16` (use PRD value, per FR requirement, not H-E1 default).
- `h-e1/code/data.py` has `load_triviaqa(split, n)` and `format_prompt(example)` — directly reusable for H-M1's 1000-sample subset.
- No test/verification module exists in H-E1 — new for H-M1.

---

## File Organization

```
h-m1/code/
├── config.py       # Config dataclass (seed, model, layer, paths)
├── data.py         # load_triviaqa subset (reuse H-E1 pattern)
├── hooks.py        # HiddenStateExtractor (context-managed, new)
├── generate.py     # baseline/hooked generation pipelines
├── verify.py       # identity check, overhead calc, memory profile
├── run_experiment.py  # orchestrates full verification + figures
└── figures/
```

---

## Modules

### Config (`config.py`)

**Dependencies**: None

```python
@dataclass
class Config:
    seed: int = 42
    model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    torch_dtype: str = "float16"
    device_map: str = "auto"
    target_layer: int = 19
    n_samples: int = 1000
    max_new_tokens: int = 128
    identity_gate: float = 1.0
    overhead_gate_pct: float = 10.0
    figures_dir: str = "figures/"
    cache_dir: str = "cache/"

def set_seed(seed: int = 42) -> None: ...
```

### Data (`data.py`)

**Dependencies**: None (reuses H-E1 `load_triviaqa`/`format_prompt` logic)

```python
def load_triviaqa_subset(n: int = 1000) -> "Dataset": ...
def format_prompt(example: dict) -> str: ...
```

### HiddenStateExtractor (`hooks.py`)

**Dependencies**: torch

```python
class HiddenStateExtractor:
    def __init__(self, model, layer_indices: list[int] = None): ...
    def __enter__(self) -> "HiddenStateExtractor": ...
    def __exit__(self, *exc) -> None: ...
    def _create_hook(self, layer_idx: int) -> callable: ...
    hidden_states: dict[int, torch.Tensor]
    handles: list
```

### Generation Pipelines (`generate.py`)

**Dependencies**: hooks.HiddenStateExtractor, data

```python
def generate_baseline(model, tokenizer, prompts: list[str], max_new_tokens: int) -> tuple[list[str], float]: ...
def generate_hooked(model, tokenizer, prompts: list[str], max_new_tokens: int, layer_idx: int) -> tuple[list[str], float]: ...
```
Returns `(decoded_outputs, elapsed_seconds)`.

### Verification (`verify.py`)

**Dependencies**: None (pure Python + torch.cuda for memory)

```python
def check_output_identity(outputs_a: list[str], outputs_b: list[str]) -> tuple[float, list[int]]: ...
def compute_overhead_pct(time_without: float, time_with: float) -> float: ...
def profile_memory(model, tokenizer, prompt: str, layer_idx: int) -> dict: ...
def gate_check(identity_rate: float, overhead_pct: float, cfg: "Config") -> bool: ...
```

### Orchestration (`run_experiment.py`)

**Dependencies**: config, data, generate, verify, matplotlib

```python
def main() -> None: ...
def plot_gate_metrics(identity_rate: float, overhead_pct: float, cfg) -> None: ...
def plot_time_histogram(times_without: list[float], times_with: list[float], cfg) -> None: ...
def plot_memory_profile(mem_stats: dict, cfg) -> None: ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| load_triviaqa | reference pattern only (not imported — H-M1 uses own `load_triviaqa_subset`, same logic, split="validation[:1000]") | `h-e1/code/data.py` |
| format_prompt | reference pattern only (chat-template prompt format reused verbatim) | `h-e1/code/data.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

**Note**: H-E1's `HiddenStateExtractor` (model.py) is NOT reused directly — it lacks context-manager lifecycle and only captures last-token state. H-M1 implements a new context-managed version per PRD FR-1, matching the experiment brief's `hooks.py` design.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Setup config & data loading | Config dataclass, seed control, TriviaQA 1000-sample subset load + prompt formatting | 6 | 2+1+1+2 |
| M-2 | Implement HiddenStateExtractor | Context-managed hook attach/detach, layer 19, detach().cpu(), return None | 10 | 3+2+3+2 |
| M-3 | Implement baseline generation pipeline | Greedy decode, 1000 samples, no hooks, timing capture | 8 | 2+2+2+2 |
| M-4 | Implement hooked generation pipeline | Same pipeline wrapped in extractor context manager | 7 | 2+2+2+1 |
| M-5 | Implement identity verification | Byte-by-byte comparison, mismatch index logging, identity rate calc | 6 | 1+1+2+2 |
| M-6 | Implement overhead & memory profiling | Time delta %, torch.cuda.max_memory_allocated tracking | 7 | 2+1+2+2 |
| M-7 | Implement gate check logic | Compare identity_rate==1.0 and overhead<10%, pass/fail decision | 5 | 1+1+2+1 |
| M-8 | Build orchestration script | run_experiment.py wiring all modules end-to-end, results logging | 9 | 3+3+2+1 |
| M-9 | Implement figure generation | Gate metrics bar chart, time histogram, memory profile plot | 8 | 2+2+2+2 |
| M-10 | Integration test on full pipeline | Run full 1000-sample verification, validate gate on real model | 12 | 3+4+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-2, M-8, M-10], Low(4-8): [M-1, M-3, M-4, M-5, M-6, M-7, M-9]
