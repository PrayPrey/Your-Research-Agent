# Logic: H-M1 (Forward Hook Non-Intrusiveness Verification)

**Applied**: PyTorch register_forward_hook non-intrusive pattern (KB: torch.nn.Module hooks, torch.no_grad)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: API signatures verified from actual code (Read tool; Serena not registered for this path)
**Analyzed Path**: `docs/youra_research/h-e1/code/model.py`, `data.py`
**Relevant Symbols**: `HiddenStateExtractor.__init__/_capture_hook/get_last_hidden/remove` (model.py), `load_triviaqa`, `format_prompt` (data.py)
**Note**: H-E1's `HiddenStateExtractor` lacks context-manager and only captures last token — H-M1 builds a new context-managed, full-sequence version per PRD FR-1.

---

## A-1: Config & Data Loading [Complexity: 6, Budget: 6]

**Applied**: dataclass config (H-E1 pattern), reused verbatim

### API Signatures

```python
# config.py
@dataclass
class Config:
    seed: int = 42
    model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    torch_dtype: str = "float16"          # PRD override (H-E1 used bfloat16)
    device_map: str = "auto"
    target_layer: int = 19
    n_samples: int = 1000
    max_new_tokens: int = 128
    identity_gate: float = 1.0
    overhead_gate_pct: float = 10.0
    figures_dir: str = "figures/"
    cache_dir: str = "cache/"

def set_seed(seed: int = 42) -> None: ...

# data.py
def load_triviaqa_subset(n: int = 1000) -> "Dataset":
    """validation[:n] via load_dataset('trivia_qa', 'rc', split=f'validation[:{n}]')"""
    ...

def format_prompt(example: dict) -> str:
    """Identical to h-e1/code/data.py:format_prompt (chat-template string)."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Config dataclass + set_seed | Fields above; torch/np/random seeding |
| L-1-2 | load_triviaqa_subset + format_prompt | HF datasets load, reuse H-E1 prompt format |

---

## A-2: HiddenStateExtractor (Context Manager) [Complexity: 10, Budget: 2]

**Applied**: multigrid Recorder pattern (context-managed handle cleanup) + non-intrusive hook (return None)

### API Signatures

```python
# hooks.py
class HiddenStateExtractor:
    def __init__(self, model: "PreTrainedModel", layer_indices: list[int] = None):
        """layer_indices default [19]. Stores refs, no hooks yet."""
        ...

    def __enter__(self) -> "HiddenStateExtractor":
        """Registers forward hooks on model.model.layers[i] for i in layer_indices."""
        ...

    def __exit__(self, *exc) -> None:
        """Calls handle.remove() for all handles; clears self.handles."""
        ...

    def _create_hook(self, layer_idx: int) -> "Callable":
        """Returns closure hook(module, input, output) -> None."""
        ...

    hidden_states: dict[int, torch.Tensor]   # {layer_idx: [B, T, H]} accumulated per forward call
    handles: list  # RemovableHandle
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| output[0] (layer output) | [B, T, 4096] | Llama decoder layer hidden states |
| hidden_states[layer_idx] | [B, T, 4096] | `.detach().cpu()`, overwritten per forward call |

### Pseudo-code

```
_create_hook(layer_idx):
    def hook(module, input, output):
        self.hidden_states[layer_idx] = output[0].detach().cpu()  # [B,T,H]
        return None   # non-intrusive: do not alter output
    return hook

__enter__:
    for idx in layer_indices:
        h = model.model.layers[idx].register_forward_hook(self._create_hook(idx))
        handles.append(h)
    return self

__exit__:
    for h in handles: h.remove()
    handles = []
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | `__init__`/`_create_hook` | Store model/layer_indices, closure factory |
| L-2-2 | `__enter__`/`__exit__` | Register/remove handles, lifecycle safety (try/finally in caller) |

---

## A-3/A-4: Generation Pipelines (baseline + hooked) [Complexity: 8+7, Budget: 2]

**Applied**: greedy decode + `time.perf_counter()` wall-clock timing

### API Signatures

```python
# generate.py
def generate_baseline(
    model, tokenizer, prompts: list[str], max_new_tokens: int
) -> tuple[list[str], float]:
    """No hooks. Greedy decode. Returns (decoded_outputs, elapsed_seconds)."""
    ...

def generate_hooked(
    model, tokenizer, prompts: list[str], max_new_tokens: int, layer_idx: int
) -> tuple[list[str], float]:
    """Wraps generate_baseline's decode loop in HiddenStateExtractor([layer_idx]) context."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, T_prompt] | left-padded, batch_size configurable (e.g. 8) |
| generate() output | [B, T_prompt+T_new] | sliced at `[:, T_prompt:]` for decode |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | `generate_baseline` | Batched greedy `model.generate`, `do_sample=False`, timed |
| L-3-2 | `generate_hooked` | Same loop, wrapped in `with HiddenStateExtractor(model, [layer_idx]):` |

---

## A-5/A-6/A-7: Verification (identity, overhead, memory, gate) [Complexity: 6+7+5, Budget: 2]

**Applied**: byte-equality comparison, `torch.cuda.max_memory_allocated`

### API Signatures

```python
# verify.py
def check_output_identity(outputs_a: list[str], outputs_b: list[str]) -> tuple[float, list[int]]:
    """Returns (identity_rate in [0,1], mismatch_indices)."""
    ...

def compute_overhead_pct(time_without: float, time_with: float) -> float:
    """(time_with - time_without) / time_without * 100"""
    ...

def profile_memory(model, tokenizer, prompt: str, layer_idx: int) -> dict:
    """{'gpu_peak_mb': float, 'cpu_tensor_mb': float}. Uses torch.cuda.reset_peak_memory_stats/max_memory_allocated."""
    ...

def gate_check(identity_rate: float, overhead_pct: float, cfg: "Config") -> bool:
    """identity_rate >= cfg.identity_gate and overhead_pct < cfg.overhead_gate_pct"""
    ...
```

### Pseudo-code

```
check_output_identity(a, b):
    mismatches = [i for i in range(len(a)) if a[i] != b[i]]
    rate = 1.0 - len(mismatches)/len(a)
    return rate, mismatches
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | identity/overhead/memory/gate fns | 4 pure functions above, unit-testable |

---

## A-8/A-9: Orchestration + Figures [Complexity: 9+8, Budget: 1]

**Applied**: matplotlib bar chart + histogram (standard)

### API Signatures

```python
# run_experiment.py
def main() -> None:
    """cfg -> set_seed -> load data -> generate_baseline -> generate_hooked ->
       check_output_identity -> compute_overhead_pct -> profile_memory ->
       gate_check -> plot_* -> print/save results json."""
    ...

def plot_gate_metrics(identity_rate: float, overhead_pct: float, cfg) -> None: ...
def plot_time_histogram(times_without: list[float], times_with: list[float], cfg) -> None: ...
def plot_memory_profile(mem_stats: dict, cfg) -> None: ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | `main` + 3 plot fns | End-to-end wiring, save figures to `cfg.figures_dir` |

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: h-e1/code/data.py (ACTUAL CODE) — reference pattern only, not imported
def load_triviaqa(split: str, n: int):
    """load_dataset('trivia_qa','rc', split='train'|'validation').select(range(n))"""
    ...

def format_prompt(example: dict) -> str:
    """Llama-3 chat template string, reused verbatim in h-m1/code/data.py"""
    ...
```

**Verified from**: `docs/youra_research/h-e1/code/data.py` (actual implementation)

**Note**: H-E1's `HiddenStateExtractor` (`model.py`) captures only `output[0][:, -1, :]` and has no `__enter__`/`__exit__`. Not reused — H-M1 implements its own full-sequence, context-managed version (see A-2).
