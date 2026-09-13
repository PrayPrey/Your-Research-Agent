# Config: H-E1 (EXISTENCE / PoC)

**Applied**: Standard PyTorch defaults (no matching KB pattern found; searched "DL config patterns")

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dict (single fixed config, per EXISTENCE rules)

---

## A-1: Config setup [Complexity: 4, Budget: 4]

**Applied**: Fixed dict config (no tuning, no grid — EXISTENCE hypothesis)

### Configuration (Hardcoded Dict)

```python
# config.py
CONFIG = {
    "n_seeds": 20,          # seeds per layer for CV_PR variance estimation (FR-3, FR-5)
    "rank": 50,             # randomized SVD target rank (FR-3)
    "n_models": 100,        # min timm models to process (FR-1)
    "seed_base": 0,         # seeds = seed_base .. seed_base + n_seeds - 1 (NFR-3)
    "output_dir": "h-e1/results",
    "figures_dir": "h-e1/figures",
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Define CONFIG dict | Single fixed dict in config.py with all fields above, no CLI/env overrides |
