# Configuration: H-M1 — Grammar-Constrained Decoding

**Applied**: Standard PyTorch/HF inference config defaults (no close KB match for grammar-decoding configs; used PRD/architecture specs directly)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## A-1: Config & Scaffolding [Complexity: 5, Budget: 3 subtasks]

Single fixed PoC config (no hyperparameter sweep — MECHANISM/PoC gate is directional only).

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    # Model
    model_id: str = "meta-llama/CodeLlama-7b-hf"
    dtype: str = "bfloat16"
    device: str = "cuda"

    # Dataset
    dataset_id: str = "openai/openai_humaneval"
    split: str = "test"

    # Generation
    num_samples: int = 10          # samples per problem, both conditions
    temperature: float = 0.2
    max_new_tokens: int = 512

    # Constrained decoding (SynCode)
    syncode_mode: str = "grammar_strict"
    grammar: str = "python"
    quantize: bool = True

    # Reproducibility
    seed: int = 1

    # Paths
    output_dir: str = "results"
    figures_dir: str = "figures"
```

### YAML Schema (equivalent, optional override file)

```yaml
model_id: meta-llama/CodeLlama-7b-hf
dtype: bfloat16
device: cuda

dataset_id: openai/openai_humaneval
split: test

num_samples: 10
temperature: 0.2
max_new_tokens: 512

syncode_mode: grammar_strict
grammar: python
quantize: true

seed: 1

output_dir: results
figures_dir: figures
```

### Environment Variables and Paths

| Var/Path | Value | Purpose |
|----------|-------|---------|
| `HF_TOKEN` | (user-provided) | Required for gated `meta-llama/CodeLlama-7b-hf` download |
| `results/` | relative to `h-m1/code/` | Raw generation outputs (JSON per condition) |
| `figures/` | relative to `h-m1/code/` | Bar chart, heatmap, summary table |

No other env vars required — single GPU, no distributed/quantization service config beyond `quantize=True` flag passed to SynCode.

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Define ExperimentConfig | dataclass in `config.py` with fields above |
| C-1-2 | Seeding + dir setup | `torch.manual_seed`, `random.seed`, create `output_dir`/`figures_dir` if missing |
| C-1-3 | Config validation | Assert `num_samples>0`, `0<temperature<=1`, `max_new_tokens>0` at load time |
