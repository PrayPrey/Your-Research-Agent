# Configuration: H-E1 — Frozen-Model Variance Profiling (MBPP)

**Hypothesis:** h-e1 | **Type:** EXISTENCE (PoC) | **Date:** 2026-08-21

Applied: HuggingFace dataclass config pattern (flat dataclass + from_yaml classmethod)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — new config design, no existing codebase to verify
**Config Files Found:** None — new config
**Pattern Used:** dataclass

---

## ProfileConfig (Python Dataclass)

Single dataclass covering all experiment parameters. Loadable from YAML for reproducibility.

```python
from dataclasses import dataclass, field
from typing import Optional
import yaml


@dataclass
class ProfileConfig:
    # --- Model ---
    model_id: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
    torch_dtype: str = "bfloat16"
    device_map: str = "auto"

    # --- Generation ---
    k: int = 8                      # completions per problem
    temperature: float = 1.0        # i.i.d. sampling requires high temp
    top_p: float = 0.95
    max_new_tokens: int = 512
    do_sample: bool = True

    # --- Execution ---
    timeout: int = 10               # subprocess timeout (seconds)
    seed: int = 42

    # --- Gate ---
    variance_threshold: float = 0.1 # p_i*(1-p_i) > this to count
    min_count: int = 50             # gate: count(variance > threshold) >= min_count

    # --- Dataset ---
    dataset_id: str = "google-research-datasets/mbpp"
    dataset_config: str = "full"
    split: str = "train"
    expected_size: int = 374

    # --- Output ---
    results_dir: str = "docs/youra_research/h-e1/results"
    figures_dir: str = "docs/youra_research/h-e1/figures"
    checkpoint_every: int = 50

    @classmethod
    def from_yaml(cls, path: str) -> "ProfileConfig":
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def to_yaml(self, path: str) -> None:
        import dataclasses
        with open(path, "w") as f:
            yaml.dump(dataclasses.asdict(self), f, default_flow_style=False)
```

### Section Descriptions

| Section | Controls |
|---------|----------|
| **Model** | Which checkpoint to load, dtype, device placement |
| **Generation** | Sampling parameters for k i.i.d. completions per problem |
| **Execution** | Subprocess sandbox timeout; base seed for reproducibility |
| **Gate** | MUST_WORK threshold: variance_threshold and min_count define pass condition |
| **Dataset** | HuggingFace dataset identifier, split, and expected row count for validation |
| **Output** | Directory paths for JSON results and figures; checkpoint frequency |

---

## YAML Schema (config.yaml)

Drop-in default config file. Pass to `ProfileConfig.from_yaml("config.yaml")`.

```yaml
# H-E1 Profiling Config
# Model
model_id: "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
torch_dtype: "bfloat16"
device_map: "auto"

# Generation
k: 8
temperature: 1.0
top_p: 0.95
max_new_tokens: 512
do_sample: true

# Execution
timeout: 10
seed: 42

# Gate
variance_threshold: 0.1
min_count: 50

# Dataset
dataset_id: "google-research-datasets/mbpp"
dataset_config: "full"
split: "train"
expected_size: 374

# Output
results_dir: "docs/youra_research/h-e1/results"
figures_dir: "docs/youra_research/h-e1/figures"
checkpoint_every: 50
```

---

## Usage in profile_mbpp.py

```python
# Load from YAML (reproducible)
cfg = ProfileConfig.from_yaml("docs/youra_research/h-e1/config.yaml")

# Or use defaults directly
cfg = ProfileConfig()

# Save config alongside results for audit trail
cfg.to_yaml(f"{cfg.results_dir}/run_config.yaml")
```

---

## Subtasks

Budget: 0 dedicated config subtasks — config is integrated into A-1 (Environment & Structure).

Config file (`config.yaml`) is created during A-1 alongside directory setup. `ProfileConfig` dataclass is defined at the top of `profile_mbpp.py` and used throughout.
