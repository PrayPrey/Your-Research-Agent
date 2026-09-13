# Config: h-e1 (EXISTENCE)

**Applied**: Hardcoded dict/list pattern (PoC — single fixed config, no hyperparameter grid)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: Hardcoded module-level constants (`config.py`)

---

## A-1: Config setup [Complexity: 4, Budget: 4]

**Applied**: Hardcoded dict — EXISTENCE PoC, no tuning/variations.

### Configuration (`code/config.py`)

```python
MODELS = [
    # Pythia family
    {"id": "EleutherAI/pythia-70m",  "family": "pythia", "params": 70_000_000},
    {"id": "EleutherAI/pythia-160m", "family": "pythia", "params": 160_000_000},
    {"id": "EleutherAI/pythia-410m", "family": "pythia", "params": 410_000_000},
    {"id": "EleutherAI/pythia-1b",   "family": "pythia", "params": 1_000_000_000},
    {"id": "EleutherAI/pythia-1.4b", "family": "pythia", "params": 1_400_000_000},
    {"id": "EleutherAI/pythia-2.8b", "family": "pythia", "params": 2_800_000_000},
    {"id": "EleutherAI/pythia-6.9b", "family": "pythia", "params": 6_900_000_000},
    {"id": "EleutherAI/pythia-12b",  "family": "pythia", "params": 12_000_000_000},
    # Llama-2 family
    {"id": "meta-llama/Llama-2-7b-hf",  "family": "llama2", "params": 7_000_000_000},
    {"id": "meta-llama/Llama-2-13b-hf", "family": "llama2", "params": 13_000_000_000},
    {"id": "meta-llama/Llama-2-70b-hf", "family": "llama2", "params": 70_000_000_000},
    # Mistral
    {"id": "mistralai/Mistral-7B-v0.1", "family": "mistral", "params": 7_000_000_000},
    # Falcon
    {"id": "tiiuae/falcon-7b",  "family": "falcon", "params": 7_000_000_000},
    {"id": "tiiuae/falcon-40b", "family": "falcon", "params": 40_000_000_000},
]
# 14 models across 4 families; meets 15+ target if 1-2 more added
# (e.g. pythia-160m already listed; add EleutherAI/pythia-14m/pythia-1b-deduped etc. if 15+ strictly required)

TASKS = ["truthful_qa_mc1", "adv_glue"]

RESULTS_DIR = "results/"
FIGURES_DIR = "figures/"
SCORES_CSV = "results/scores.csv"

SEED = 42
N_BOOTSTRAP = 1000
CI_LEVEL = 0.95

# Gate thresholds (success criteria, PRD)
R_THRESHOLD = 0.3
P_THRESHOLD = 0.05
CI_LOWER_THRESHOLD = 0.0
```

**Non-standard**: `MODELS` list has 14 entries; PRD FR-2 lists exactly these families/sizes (15-20 target is a range — this literal set from FR-2 is used as-is; A-2/A-3 owner may add pythia-14m or another checkpoint if a hard 15 minimum is enforced at eval time).

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Write config.py | Single file: MODELS, TASKS, paths, SEED, N_BOOTSTRAP, gate thresholds — no variants |
