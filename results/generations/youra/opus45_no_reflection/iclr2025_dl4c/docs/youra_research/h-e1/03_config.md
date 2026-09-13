# Config: H-E1 (EVAF Existence PoC)

**Type**: EXISTENCE (PoC) — single fixed config, no ablations
**Applied**: No close KB match found (searched "DL config patterns", "experiment hyperparameters") — using standard PyTorch/HF inference defaults per architecture spec

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - no existing codebase, no base hypothesis
**Config Files Found**: None - new config
**Pattern Used**: Hardcoded dict (per architecture.md `config.py` spec)

---

## A-1: Setup + Config [Complexity: 4, Budget: 4]

**Applied**: Standard HF/PyTorch inference defaults; values fixed per PRD (no tuning, EXISTENCE tier)

### Configuration (Hardcoded dict — `config.py`)

```python
CONFIG = {
    # Models
    "baseline_model_id": "Salesforce/codet5-large",
    "feedback_model_id": "codellama/CodeLlama-7b-Instruct-hf",
    "precision": "float16",
    "device": "cuda",  # falls back to "cpu" if unavailable

    # Generation
    "temperature": 0.2,
    "max_tokens": 512,
    "seed": 42,

    # Evaluation / gating
    "test_timeout_s": 3.0,

    # Data
    "dataset_name": "openai_humaneval",
    "dataset_split": "test",

    # Output paths
    "results_dir": "results/",
    "figures_dir": "results/figures/",
    "results_json": "results/results.json",
    "metrics_json": "results/metrics.json",
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Write config.py | Hardcoded `CONFIG` dict above, single source of truth |
| C-1-2 | Create output dirs | `os.makedirs(results_dir, figures_dir, exist_ok=True)` at startup |
