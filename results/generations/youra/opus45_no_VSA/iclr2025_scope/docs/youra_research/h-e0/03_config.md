# Config: h-e0

**Type:** EXISTENCE (PoC) | **Format:** Hardcoded dict/constants

**Applied**: No matching KB pattern (searched "DL experiment config patterns" — only diffusion-model repos returned, not applicable). Using standard sklearn/PyTorch defaults per architecture spec.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design, no existing code to analyze
**Config Files Found**: None
**Pattern Used**: Module-level constants (dict-equivalent, matches architecture's `config.py` design)

---

## A-1: Data Pipeline [Complexity: 9, Budget: 1]

**Applied**: Standard PyTorch/sklearn defaults; single fixed config (EXISTENCE — no grid, no tuning).

### Configuration (`h-e0/code/config.py`)

```python
SEED = 42
DATA_CSV_PATH = "h-e0/data/flan_metadata.csv"  # local FLAN collection dump
TEXT_COLUMN = "instruction"
LABEL_COLUMN = "task_category"  # Generic Task Category

MIN_SAMPLES_PER_FAMILY = 500
MIN_FAMILIES = 10
MAX_TOKENS = 128
TEST_SIZE = 0.2

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# LogisticRegression (FR-3.3)
LOGREG_PARAMS = {
    "multi_class": "multinomial",
    "solver": "lbfgs",
    "class_weight": "balanced",
    "max_iter": 1000,
    "random_state": SEED,
}

GATE_MACRO_F1 = 0.75
FIGURES_DIR = "h-e0/figures/"
```

**Non-standard**: `max_iter=1000` (sklearn default 100) — 384-dim multinomial LogReg on 5k+ samples needs more iterations to converge with L-BFGS.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | config.py | Single fixed config module — all constants above, no variations, no CLI args |
