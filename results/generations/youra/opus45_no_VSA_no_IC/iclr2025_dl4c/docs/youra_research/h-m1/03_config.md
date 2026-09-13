# Configuration: H-M1

**Format:** Python Dataclass
**Type:** MECHANISM (multi-tier scale comparison, not PoC)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - new config design
**Config Files Found:** None (archived prior H-M1 attempt exists under `_archive/`, unrelated pipeline — not reused)
**Pattern Used:** dataclass

---

## A-1: Model Tier Configs [Complexity: 2, Budget: 3]

**Applied:** Standard vLLM/OpenAI inference defaults

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import Literal

@dataclass
class ModelTierConfig:
    tier: Literal["7B", "70B", "proprietary"]
    model_id: str
    backend: Literal["vllm", "openai"]
    temperature: float = 0.0
    max_tokens: int = 10
    device_map: str = "auto"          # vLLM/HF only
    quantization: str | None = None   # e.g. "awq" for 70B if OOM

MODEL_TIERS = {
    "7B": ModelTierConfig(
        tier="7B",
        model_id="deepseek-ai/deepseek-coder-7b-instruct",
        backend="vllm",
    ),
    "70B": ModelTierConfig(
        tier="70B",
        model_id="meta-llama/CodeLlama-70b-Instruct-hf",
        backend="vllm",
        quantization="awq",  # Non-standard: 70B requires quantization for single-node inference
    ),
    "proprietary": ModelTierConfig(
        tier="proprietary",
        model_id="gpt-4-turbo",
        backend="openai",
    ),
}
```

### Subtasks [1/3 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Model registry | Instantiate `MODEL_TIERS` dict, load per backend |

---

## A-2: Evaluation Config [Complexity: 2, Budget: 3]

**Applied:** EvalPlus + judge-verdict evaluation pattern (from experiment brief)

### Configuration (Python Dataclass)

```python
@dataclass
class EvalConfig:
    dataset: str = "humaneval_plus"
    seed: int = 42
    n_seeds: int = 1                  # deterministic at temp=0
    prompt_template: str = (
        "Given the following Python function and its specification, "
        "determine if the implementation is correct.\n\n"
        "Function:\n{code}\n\nSpecification:\n{prompt}\n\n"
        "Is this implementation correct? Answer only 'correct' or 'incorrect'."
    )
    alpha: float = 0.05               # significance threshold for Kruskal-Wallis
```

### Subtasks [1/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-2-1 | Prompt formatting | Fill template per HumanEval+ problem |

---

## A-3: Experiment Config (Top-Level) [Complexity: 1, Budget: 2]

**Applied:** Standard PyTorch/experiment defaults

### Configuration (Python Dataclass)

```python
@dataclass
class ExperimentConfig:
    models: dict = field(default_factory=lambda: MODEL_TIERS)
    eval: EvalConfig = field(default_factory=EvalConfig)
    output_dir: str = "h-m1/outputs"
    figures_dir: str = "h-m1/figures"
    scales_order: list = field(default_factory=lambda: ["7B", "70B", "proprietary"])
```

### Subtasks [0/1 used]
| ID | Subtask | Description |
|----|---------|--------------|

---

## Codebase Analysis Summary

No prior base hypothesis reused for H-M1's evaluation pipeline; configs designed fresh per experiment brief. Total complexity: 5/8 budget used.
