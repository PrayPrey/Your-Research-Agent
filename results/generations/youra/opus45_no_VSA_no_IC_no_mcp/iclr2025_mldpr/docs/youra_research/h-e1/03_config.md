# Config: h-e1 (EXISTENCE PoC)

**Applied**: Fixed-constants config pattern (single hardcoded dict, no hyperparameter search) — standard for EXISTENCE/PoC metric-computation experiments.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (no base hypothesis, no existing repo code)
**Config Files Found**: None - new config
**Pattern Used**: dict (hardcoded constants)

---

## A-Config: Fixed Experiment Constants [Complexity: 5, Budget: 2 subtasks]

**Applied**: Fixed-constants config pattern (single hardcoded dict) — EXISTENCE hypotheses omit hyperparameter grids/variations.

### Configuration (Hardcoded Dict)

```python
# code/config.py

CONFIG = {
    "seed": 1,
    "window_months": 6,
    "min_sota_entries": 50,
    "min_history_years": 3,
    "dnsi_valid_range": (0.0, 2.0),
    "success_rate_threshold": 0.5,
    "data_dir": "data/pwc",
    "figures_dir": "figures",
    "pwc_repo_url": "https://github.com/paperswithcode/paperswithcode-data",
}

# Non-standard: difficulty_proxy values are dataset class counts / vocab sizes,
# not tunable hyperparameters — fixed by dataset definition (PRD FR-4).
TARGET_BENCHMARKS = {
    "ImageNet": 1000,
    "CIFAR-10": 10,
    "CIFAR-100": 100,
    "MNIST": 10,
    "GLUE": None,        # varies per task, resolved at match time
    "SQuAD": None,        # vocab_size, resolved from tokenizer/data
    "WMT En-De": None,    # vocab_size, resolved from tokenizer/data
    "COCO Detection": 80,
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1 | Define CONFIG dict | Fixed constants: seed, window, thresholds, dirs, repo URL |
| C-2 | Define TARGET_BENCHMARKS dict | 8 target benchmarks with difficulty_proxy values (None = resolve at runtime) |
