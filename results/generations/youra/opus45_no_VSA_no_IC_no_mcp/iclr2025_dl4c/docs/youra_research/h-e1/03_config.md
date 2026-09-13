# Config: H-E1 (EXISTENCE / PoC)

**Applied**: Single fixed config dataclass (flat, no variations) — matches EXISTENCE PoC rules

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - new config design (matches architecture's config.py constants)
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## A-1..A-8: Experiment Config [Complexity: 8, Budget: 1 subtask]

**Applied**: Fixed single-run PoC config, no hyperparameter sweep (EXISTENCE rule)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class ExperimentConfig:
    seed: int = 42
    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    max_iterations: int = 3
    temperature: float = 0.2
    max_tokens: int = 512
    top_p: float = 0.95
    timeout_sec: int = 10
    mem_limit_mb: int = 512
    datasets: list[str] = field(default_factory=lambda: ["humaneval", "mbpp"])
    feedback_types: list[str] = field(default_factory=lambda: ["execution", "random"])
    results_path: str = "h-e1/results.json"
    figures_dir: str = "h-e1/figures/"

CONFIG = ExperimentConfig()
```

### YAML Schema (config.yaml)

```yaml
seed: 42
model_id: "codellama/CodeLlama-7b-Instruct-hf"
max_iterations: 3
temperature: 0.2
max_tokens: 512
top_p: 0.95
timeout_sec: 10
mem_limit_mb: 512
datasets: ["humaneval", "mbpp"]
feedback_types: ["execution", "random"]
results_path: "h-e1/results.json"
figures_dir: "h-e1/figures/"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Config module | Write `config.py` with `ExperimentConfig` dataclass + `CONFIG` instance, matching architecture's constants |
