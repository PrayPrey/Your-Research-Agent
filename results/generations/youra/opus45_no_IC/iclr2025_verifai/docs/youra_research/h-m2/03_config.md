# Config: H-M2 — Static Analysis Feedback Loop

**Tier**: FULL | **Budget**: 4 subtasks

Applied: Standard PyTorch/HF ExperimentConfig dataclass (single source of truth, no YAML layer)
Applied: subprocess-tool timeout pattern (analysis_timeout_s guards hung Bandit/Pylint calls)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: `h-m1/code/` does not exist on disk; no existing `h-m2/code/` yet. Serena skipped per rules (green-field, no base code to verify field names against).
**Config Files Found**: None — new config design
**Pattern Used**: dataclass (matches `03_architecture.md` exactly, no deviation)

---

## A-1: Config & Scaffolding [Complexity: 5, Budget: 5]

**Applied**: Standard PyTorch/HF dataclass defaults; no tuning (PoC-adjacent mechanism test)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    model_id: str = "meta-llama/CodeLlama-7b-Instruct-hf"
    dataset_id: str = "s2e-lab/SecurityEval"
    temperature: float = 0.2
    max_new_tokens: int = 512
    max_iterations: int = 5          # PoC value per PRD FR-4.1 (10 for full run)
    analysis_timeout_s: int = 30     # per-tool timeout (Bandit and Pylint each)
    seed: int = 1
    device: str = "cuda"
    output_dir: str = "results"
    figures_dir: str = "figures"
```

### Gate Thresholds (`evaluate.py` uses these directly, no separate config needed)

```python
# PASS condition (PRD Section 6, Gate Condition SHOULD_WORK):
# final_security_issues < initial_security_issues
# final_reliability_issues < initial_reliability_issues
# No numeric threshold beyond strict inequality — any reduction counts.
```

### Output Directory Structure

```
results/
├── baseline_generations.jsonl   # A-8: id, prompt, cwe, code
├── loop_results.jsonl           # A-9: id, initial, final, iterations, history
├── evaluation.json              # A-10: aggregated reductions + gate PASS/FAIL
└── figures/
    ├── gate_metrics_comparison.png
    ├── issue_reduction_over_iterations.png
    └── cwe_distribution.png
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Define ExperimentConfig | Dataclass in `config.py`, exact fields above |
| C-1-2 | Seeding utility | `set_seed(seed)` — `random`, `numpy`, `torch` (cuda + cpu) |
| C-1-3 | Output dir creation | `os.makedirs(output_dir, exist_ok=True)` + `figures_dir` under it |
| C-1-4 | Path helpers | `results_path(config, filename) -> str` joins `output_dir` |
