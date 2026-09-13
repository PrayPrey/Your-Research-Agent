# Config: H-E1 (EXISTENCE / PoC)

**Applied**: Archon unavailable — using brief-specified defaults (no tuning, single fixed config).

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None
**Pattern Used**: Hardcoded dict (module-level constants in config.py)

---

## Config (Hardcoded dict / constants)

**Applied**: EXISTENCE PoC — single fixed config, no hyperparameter grid, 1 seed.

```python
# config.py

CONFIG = {
    # Datasets
    "dataset_humaneval": "openai/openai_humaneval",
    "dataset_mbpp": "mbpp",

    # Sampling
    "sample_size": 100,              # failing test cases (min statistically meaningful)
    "random_seed": 42,

    # Signal generation
    "conditions": ["C1", "C2", "C3", "C4", "C5", "C6"],
    "llm_temp": 0.7,                 # temp for generating buggy code
    "max_truncate_frames": 3,        # C2: truncated trace depth

    # Extraction gate
    "extraction_rate_target": 0.95,  # PoC pass: >=95% of 600 signals
    "correlation_threshold": 0.5,    # secondary: r < 0.5 between AS components

    # Output
    "output_dir": "results",
    "figures_dir": "figures",
}
```

**Non-standard**: `max_truncate_frames=3` fixed per brief (C2 definition), not tuned.

---

### Subtasks: None (budget = 0, all config in single config.py)
