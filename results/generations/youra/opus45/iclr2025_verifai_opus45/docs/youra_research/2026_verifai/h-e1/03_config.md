# Configuration: H-E1 — Runtime Error Prevalence in LLM-Generated Code

**Hypothesis Type**: EXISTENCE
**Date**: 2026-03-30

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new implementation
**Pattern Used**: dataclass

Applied: Standard Python dataclass (no domain-specific KB match)

---

## A-7: Integration & Run [Complexity: 9, Budget: 2 subtasks]

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    # Model
    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    max_new_tokens: int = 512
    temperature: float = 0.0
    do_sample: bool = False

    # Dataset
    dataset_name: str = "mbpp"
    task_id_min: int = 11
    task_id_max: int = 510

    # Execution
    execution_timeout: int = 10

    # Reproducibility
    seed: int = 1

    # Paths
    results_dir: str = "results"
    figures_dir: str = "results/figures"
    output_json: str = "results/execution_results.json"
    output_metrics: str = "results/metrics.yaml"

    # Gate
    gate_threshold: float = 0.30
    # Non-standard: Wilson CI lower bound used as gate (not point estimate)
    ci_confidence: float = 0.95
    ci_method: str = "wilson"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | ExperimentConfig | Dataclass with all fields above in `code/config.py` |
| C-7-2 | Runner wiring | `run_experiment(config)` integrates all modules using config fields |
