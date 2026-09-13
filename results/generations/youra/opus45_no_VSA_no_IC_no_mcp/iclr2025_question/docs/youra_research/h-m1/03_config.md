# Configuration: H-M1 (Token Entropy Captures Epistemic Uncertainty)

**Applied**: Standard PyTorch/Transformers defaults (single fixed config — MECHANISM test, no sweep)

## Codebase Analysis (Serena)

**Project Type**: green-field (h-m1 folder has no `code/` yet)
**Status**: green-field - new config design
**Config Files Found**: None
**Pattern Used**: dataclass

Note: PRD references reusing `src/metrics/entropy.py` from H-E1, but no base
config dataclass exists to inherit field names from — designing fresh.

---

## A-1: Experiment Config

### YAML Schema (all hyperparameters)

```yaml
model:
  model_name: "meta-llama/Llama-2-7b-hf"
  dtype: "float16"
  device_map: "auto"

generation:
  dataset: "truthful_qa"
  dataset_config: "generation"
  max_new_tokens: 100
  do_sample: false

analysis:
  effect_size_threshold: 0.2
  significance_threshold: 0.05

reproducibility:
  seed: 42

paths:
  output_dir: "docs/youra_research/h-m1/results"
  figures_dir: "docs/youra_research/h-m1/results/figures"
```

### Python Dataclass

```python
from dataclasses import dataclass, field

@dataclass
class HM1Config:
    # Model
    model_name: str = "meta-llama/Llama-2-7b-hf"
    dtype: str = "float16"          # torch.float16
    device_map: str = "auto"

    # Generation / dataset
    dataset: str = "truthful_qa"
    dataset_config: str = "generation"  # HF config name
    max_new_tokens: int = 100
    do_sample: bool = False         # greedy decoding, deterministic

    # Statistical analysis
    effect_size_threshold: float = 0.2   # Cohen's d minimum (SECONDARY criterion)
    significance_threshold: float = 0.05 # p-value cutoff (TERTIARY criterion)

    # Reproducibility
    seed: int = 42

    # Paths
    output_dir: str = "docs/youra_research/h-m1/results"
    figures_dir: str = field(default="")  # set in __post_init__

    def __post_init__(self):
        if not self.figures_dir:
            self.figures_dir = f"{self.output_dir}/figures"
        assert self.dtype in ("float16", "bfloat16", "float32"), "invalid dtype"
        assert self.max_new_tokens > 0, "max_new_tokens must be positive"
        assert 0.0 < self.significance_threshold < 1.0, "significance_threshold must be in (0,1)"
        assert self.effect_size_threshold > 0, "effect_size_threshold must be positive"


CONFIG = HM1Config()
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Config module | Single `HM1Config` dataclass with validation, instantiated as `CONFIG` |
