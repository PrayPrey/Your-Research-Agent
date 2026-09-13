# Configuration: H-C1

**Applied**: single-dataclass-singleton-config pattern (matches H-M1 `CFG = Config()` convention)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: config classes verified from base code (`h-m1/code/config.py`)
**Config Files Found**: `docs/youra_research/h-m1/code/config.py`
**Pattern Used**: dataclass (`@dataclass class Config` + module-level `CFG = Config()` singleton)

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-m1/code/config.py (ACTUAL CODE)
@dataclass
class Config:
    seed: int = 42
    data_dir: str = "data"
    results_dir: str = "results"
    humaneval_n: int = 164
    mbpp_n: int = 500
    timeout_s: int = 10
    memory_mb: int = 512
    network_disabled: bool = True
```

H-C1 does not subclass this (separate experiment, per architecture's own `config.py`). Only naming convention (`seed`, `results_dir`, `timeout_s`, `memory_mb`) and singleton pattern are reused. Reused modules `data_loader.py` / `sandbox_executor.py` are copied unmodified and consume this same field naming.

---

## A-1/A-2: Config + ModelClient [Complexity: 16, Budget: 2 subtasks]

**Applied**: single-dataclass-singleton-config pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class Config:
    seed: int = 42
    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    temperature: float = 0.2
    max_new_tokens: int = 512
    timeout_s: int = 10
    memory_mb: int = 512
    results_dir: str = "results"
    # MBPP-sanitized has 427 problems (per PRD FR-1), not H-M1's mbpp_n=500
    mbpp_n: int = 427
    humaneval_n: int = 164

CFG = Config()
```

This is a direct copy of the architecture's `config.py` spec, matching field names exactly (no drift from 03_architecture.md). `mbpp_n` added (not in architecture snippet) since PRD FR-1 requires loading 427 MBPP problems and `data_loader.py` (reused from H-M1) expects an `n` argument.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Config setup | Write `config.py` with `Config` dataclass + `CFG` singleton; copy `data_loader.py`, `sandbox_executor.py` unmodified from `h-m1/code/base/` |
| C-1-2 | ModelClient config wiring | `ModelClient(model_id=CFG.model_id, temperature=CFG.temperature)`; `generate()` uses `CFG.max_new_tokens`, seeded via `CFG.seed` |
