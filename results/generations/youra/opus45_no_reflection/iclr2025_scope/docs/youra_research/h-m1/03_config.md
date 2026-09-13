# Configuration: H-M1 (Attention Entropy Analysis)

**Applied**: No relevant KB pattern found — config follows PRD/architecture spec directly.

## Codebase Analysis (Serena)

**Project Type**: green-field (analysis experiment, no prior code)
**Status**: green-field - new config design
**Config Files Found**: None
**Pattern Used**: dataclass (matches architecture spec)

---

## A-1: Config + C4 Streaming/Filter Pipeline [Complexity: 8, Budget: 2]

**Applied**: Standard PyTorch/HF analysis-script defaults; seed fixed per NFR-2.

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class AnalysisConfig:
    # Model
    model_name: str = "microsoft/phi-1_5"

    # Dataset
    dataset_name: str = "allenai/c4"
    dataset_config: str = "en"
    dataset_split: str = "validation"
    min_doc_tokens: int = 32768   # filter threshold (FR-1.2)
    num_samples: int = 500

    # Analysis grid
    target_lengths: List[int] = field(default_factory=lambda: [2048, 4096, 8192, 16384, 32768])
    middle_layers: List[int] = field(default_factory=lambda: [8, 12, 16])

    # Metrics
    top_k: int = 32
    entropy_clamp_min: float = 1e-10

    # Reproducibility
    seed: int = 42

    # Output paths
    output_dir: str = "results"
    figures_dir: str = "figures"
```

### Gate Thresholds

```python
GATE_ENTROPY_INCREASE_PCT: float = 0.20   # entropy must increase >20% from 2K -> 16K (SC-2)
GATE_BASE_LENGTH: int = 2048
GATE_TARGET_LENGTH: int = 16384
```

### YAML Schema (equivalent, for reference)

```yaml
model_name: microsoft/phi-1_5
dataset_name: allenai/c4
dataset_config: en
dataset_split: validation
min_doc_tokens: 32768
num_samples: 500
target_lengths: [2048, 4096, 8192, 16384, 32768]
middle_layers: [8, 12, 16]
top_k: 32
entropy_clamp_min: 1.0e-10
seed: 42
output_dir: results
figures_dir: figures
gate:
  entropy_increase_pct: 0.20
  base_length: 2048
  target_length: 16384
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Define AnalysisConfig dataclass | All fields above with defaults, in `code/config.py` |
| C-1-2 | C4 streaming filter + seeded sample | Stream `allenai/c4:en:validation`, filter `len(tokens) >= min_doc_tokens`, take first `num_samples` with seeded order |

---

## Model Loading Settings (used by A-2, no separate dataclass — part of AnalysisConfig)

```python
# code/model.py uses config.model_name with fixed kwargs (not configurable, no variation needed):
# AutoModelForCausalLM.from_pretrained(
#     config.model_name,
#     trust_remote_code=True,
#     torch_dtype=torch.float16,
#     device_map="auto",
#     output_attentions=True,
# )
```
