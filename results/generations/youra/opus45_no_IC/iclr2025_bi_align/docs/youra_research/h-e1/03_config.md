# Configuration: H-E1 (Accommodation Patterns Detectable in LMSYS-Chat-1M)

**Type:** EXISTENCE (PoC) | Single fixed config, no hyperparameter sweep.

**Applied:** Directly from PRD/02c_experiment_brief specifications.

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field - new config design
**Config Files Found:** None
**Pattern Used:** Module-level constants

---

## Configuration (config.py)

```python
# config.py

# Dataset
DATASET_NAME = "lmsys/lmsys-chat-1m"

# Model
MODEL_NAME = "s-nlp/deberta-large-formality-ranker"

# Preprocessing
MIN_TURNS_PER_SIDE = 2  # ≥2 human turns AND ≥2 AI turns

# Gate Thresholds
COVERAGE_TARGET = 0.50      # 50% coverage
COHENS_D_TARGET = 0.30      # Cohen's d > 0.3
P_VALUE_THRESHOLD = 0.001   # p < 0.001

# Batch Processing
BATCH_SIZE = 32             # DeBERTa inference batch size
SEED = 42                   # For shuffled baseline reproducibility

# Device
DEVICE = "cuda"             # GPU recommended for DeBERTa-large

# Output Paths
OUTPUT_DIR = "h-e1/results"
FIGURES_DIR = "h-e1/figures"
RESULTS_JSON = "h-e1/experiment_results.json"
```

**Rationale:**
- `MIN_TURNS_PER_SIDE = 2`: From hypothesis statement (≥2 turns per side)
- `COVERAGE_TARGET = 0.50`: Gate threshold from PRD
- `COHENS_D_TARGET = 0.30`: Gate threshold from PRD (matches Niederhoffer & Pennebaker r ~ 0.3)
- `BATCH_SIZE = 32`: Balance between GPU memory and throughput for DeBERTa-large

---

## Gate Check Config

```python
GATE_CONDITIONS = {
    "coverage_min": COVERAGE_TARGET,    # 0.50
    "cohens_d_min": COHENS_D_TARGET,    # 0.30
    "p_value_max": P_VALUE_THRESHOLD,   # 0.001
}
```

---

## Directory Setup

```python
import os

def setup_directories():
    """Create output directories if missing."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)
```
