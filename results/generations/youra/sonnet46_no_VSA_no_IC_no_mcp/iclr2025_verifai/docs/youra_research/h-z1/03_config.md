---
hypothesis_id: H-Z1
phase: 3
type: config
base_hypothesis: H-E1
date: 2026-08-26
---

# Config: H-Z1 — Z3 Formal Counterexample Feedback for LLM Code Repair

Applied: Dataclass configuration pattern (Z1Config extends H-E1 ExperimentConfig fields)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: Config classes verified from base code (Read tool used)
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    model: str = "gpt-4o-mini"
    temperature: float = 0.8          # single temperature in H-E1
    max_tokens: int = 1024
    seeds: list = field(default_factory=lambda: [42, 123, 456])
    mypy_timeout: int = 30
    mypy_flags: list = field(default_factory=lambda: ["--ignore-missing-imports", "--no-strict-optional"])
    results_dir: Path = Path("docs/youra_research/h-e1/results")
    figures_dir: Path = Path("docs/youra_research/h-e1/figures")
    gate_pass: float = 0.10
    gate_borderline: float = 0.05
```

### Inherited vs New Fields

| Field | Source | Note |
|-------|--------|-------|
| `model` | H-E1 | Same default |
| `mypy_timeout` | H-E1 | Same default |
| `mypy_flags` | H-E1 | Same default |
| `gen_temperature` | H-E1 `temperature` | Renamed; generation stays 0.8 |
| `max_tokens` | H-E1 | Increased to 2048 for repair prompts |
| `seed` | H-E1 `seeds[0]` | Single seed (PoC, 1 run) |
| `repair_temperature` | **NEW** | Deterministic repair |
| `k_repair_rounds` | **NEW** | CEGIS loop depth |
| `z3_timeout` | **NEW** | Per-check Z3 budget |
| `min_valid_z3_specs` | **NEW** | Gate assertion threshold |
| `target_curated_size` | **NEW** | Curation target |
| `z3_spec_model` | **NEW** | Separate model slot for spec gen |
| `z3_spec_temperature` | **NEW** | Deterministic spec generation |
| `z3_spec_max_tokens` | **NEW** | Spec output is shorter than code |
| `results_dir` | H-E1 pattern | Redirected to h-z1 |
| `figures_dir` | H-E1 pattern | Redirected to h-z1 |
| `h_e1_code_dir` | **NEW** | sys.path wiring to base code |

---

## A-1: Z1Config [Complexity: LIGHT, Budget: 0 subtasks]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from pathlib import Path
import os
import yaml


@dataclass
class Z1Config:
    # --- Inherited from H-E1 (adapted) ---
    model: str = "gpt-4o-mini"
    gen_temperature: float = 0.8
    max_tokens: int = 2048          # Non-standard: increased from H-E1's 1024; repair prompts are longer
    seed: int = 42
    mypy_timeout: int = 30
    mypy_flags: list = field(default_factory=lambda: [
        "--ignore-missing-imports",
        "--no-strict-optional",
    ])

    # --- New in H-Z1 ---
    repair_temperature: float = 0.0
    k_repair_rounds: int = 5
    z3_timeout: int = 10            # seconds per Z3 solver.check() call
    min_valid_z3_specs: int = 30    # gate assertion: experiment aborts below this
    target_curated_size: int = 50

    # Z3 spec generation uses separate slots (deterministic, shorter output)
    z3_spec_model: str = "gpt-4o-mini"
    z3_spec_temperature: float = 0.0
    z3_spec_max_tokens: int = 1024

    results_dir: Path = Path("docs/youra_research/h-z1/results")
    figures_dir: Path = Path("docs/youra_research/h-z1/figures")
    h_e1_code_dir: Path = Path("docs/youra_research/h-e1/code")

    @classmethod
    def from_yaml(cls, path: str = "docs/youra_research/h-z1/config.yaml") -> "Z1Config":
        with open(path) as f:
            data = yaml.safe_load(f)
        for key in ("results_dir", "figures_dir", "h_e1_code_dir"):
            if key in data:
                data[key] = Path(data[key])
        return cls(**data)

    @property
    def openai_api_key(self) -> str:
        key = os.environ.get("OPENAI_API_KEY", "")
        if not key:
            raise EnvironmentError("OPENAI_API_KEY not set")
        return key
```

---

## YAML Config Template

`docs/youra_research/h-z1/config.yaml` (human-editable):

```yaml
# H-Z1 Experiment Config — edit here, not in config.py
model: gpt-4o-mini
gen_temperature: 0.8
max_tokens: 2048
seed: 42
mypy_timeout: 30
mypy_flags:
  - "--ignore-missing-imports"
  - "--no-strict-optional"

repair_temperature: 0.0
k_repair_rounds: 5
z3_timeout: 10
min_valid_z3_specs: 30
target_curated_size: 50

z3_spec_model: gpt-4o-mini
z3_spec_temperature: 0.0
z3_spec_max_tokens: 1024

results_dir: docs/youra_research/h-z1/results
figures_dir: docs/youra_research/h-z1/figures
h_e1_code_dir: docs/youra_research/h-e1/code
```

---

## Environment Variables

| Variable | Required | Usage |
|----------|----------|-------|
| `OPENAI_API_KEY` | Yes | Accessed via `cfg.openai_api_key` property; raises on missing |

---

## Curation Criteria Constants

```python
# In z3_utils.py — problem curation filter constants
CURATION_CRITERIA = {
    "min_input_args": 1,
    "arithmetic_keywords": ["int", "float", "sum", "count", "max", "min", "mod", "div"],
    "exclude_string_only": True,    # skip problems whose inputs are only str
    "exclude_list_heavy": True,     # skip problems requiring complex list manipulation
    "require_numeric_output": True, # output type must be int or float
}
```

---

## Z3 Prompt Template Constants

```python
# In z3_utils.py — prompt constants for Z3 spec generation
Z3_SPEC_SYSTEM_PROMPT = """\
You are a formal verification expert. Given a Python function signature and docstring,
write a self-contained Python script using the z3-solver library that:
1. Declares symbolic Z3 variables matching the function's input types
2. Asserts the formal postcondition (what the function must return)
3. Ends with: result = solver.check(); print(result)

Output ONLY executable Python code. No explanation."""

Z3_SPEC_USER_TEMPLATE = """\
Function signature and docstring:
{docstring}

Canonical solution (for reference):
{canonical_solution}

Write the Z3 spec code:"""
```
