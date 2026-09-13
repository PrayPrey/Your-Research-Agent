# Configuration: H-E1 (EXISTENCE PoC)

**Hypothesis:** Category-dependent calibration variation exists in LLMs on TruthfulQA
**Format:** Hardcoded dict (single fixed config, no tuning — EXISTENCE test)

Applied: Standard PyTorch/HF defaults (no KB config pattern matched — search returned unrelated diffusion-model scripts).

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** No existing code — new config design
**Config Files Found:** None
**Pattern Used:** Hardcoded dict (module-level constants in `config.py`, matching architecture spec)

---

## A-1: Experiment Config [Complexity: 8, Budget: 1 subtask]

**Applied:** Standard PyTorch defaults + gpleiss/temperature_scaling ECE convention (15 bins)

### Configuration (`code/config.py`)

```python
import torch

SEED = 42

# Model
MODEL_ID = "meta-llama/Llama-2-7b-hf"
DTYPE = torch.float16
DEVICE_MAP = "auto"

# Dataset
DATASET_ID = "truthfulqa/truthful_qa"
DATASET_CONFIG = "multiple_choice"
DATASET_SPLIT = "validation"
MIN_CLUSTER_SIZE = 50  # NFR: statistical validity

# Inference
BATCH_SIZE = 8

# Metrics
N_BINS = 15            # standard ECE binning (Guo et al. 2017)
N_BOOTSTRAP = 100
CI = 0.95
ALPHA = 0.05            # ANOVA significance threshold (gate condition)
ECE_RANGE_TARGET = 0.05 # secondary success criterion

# Output paths
RESULTS_JSON = "04_results.json"
VALIDATION_MD = "04_validation.md"
FIGURES_DIR = "figures/"

CLUSTER_NAMES = {
    1: "Health/Nutrition/Psychology",
    2: "Law/Politics/Government",
    3: "Finance/Economics",
    4: "Science/Technology/Math",
    5: "History/Geography/Culture",
    6: "Religion/Philosophy/Ethics",
    7: "Misconceptions/Myths/Superstitions",
}

CATEGORY_TO_CLUSTER = {
    "Health": 1, "Nutrition": 1, "Psychology": 1,
    "Law": 2, "Politics": 2, "Government": 2,
    "Finance": 3, "Economics": 3,
    "Science": 4, "Technology": 4, "Math": 4, "Physics": 4, "Biology": 4,
    "History": 5, "Geography": 5, "Culture": 5, "Weather": 5,
    "Language": 5, "Education": 5, "Confusion: Places": 5,
    "Religion": 6, "Philosophy": 6, "Ethics": 6, "Sociology": 6,
    "Misconceptions": 7, "Myths": 7, "Superstitions": 7, "Conspiracies": 7,
    "Paranormal": 7, "Indexical Error: Identity": 7, "Indexical Error: Time": 7,
    "Indexical Error: Location": 7, "Indexical Error: Other": 7,
    "Indexical Error: All": 7, "Subjective": 7, "Logical Falsehood": 7,
    "Stereotypes": 7, "Fiction": 7, "Advertising": 7, "Misquotations": 7,
    "Proverbs": 7, "Mandela Effect": 7, "Confusion: People": 7,
    "Confusion: Other": 7, "Distraction": 7,
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Write config.py | Emit above constants as module-level `config.py`, importable by data/model/metrics/train modules |

---

## Self-Validation

- [x] Single format (dict), no dataclass mixed in
- [x] No ASCII diagrams
- [x] KB search noted in 1 line, no logs
- [x] Rationale only for non-standard values (N_BINS=15, ALPHA=0.05 — both standard, no other rationale added)
- [x] 1 subtask (matches budget)
- [x] Green-field — Serena skip acceptable
