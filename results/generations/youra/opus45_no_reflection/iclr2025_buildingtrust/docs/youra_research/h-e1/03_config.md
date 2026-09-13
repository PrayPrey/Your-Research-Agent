# Config: H-E1 (EXISTENCE)

Applied: single fixed evaluation config (no hyperparameter sweep, no tuning) — PoC correlation study.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (matches architecture doc, no existing code)
**Config Files Found**: None
**Pattern Used**: Hardcoded dict (Python module-level constants, per architecture.py spec)

---

## A-1: Setup Config & Data Loading [Complexity: 6, Budget: 6]

**Applied**: single fixed config, no variations (EXISTENCE PoC rule)

### Configuration (`code/config.py`)

```python
MODEL_IDS = [
    "meta-llama/Llama-2-7b-hf",
    "meta-llama/Llama-2-13b-hf",
    "meta-llama/Llama-2-70b-hf",
    "meta-llama/Meta-Llama-3-8B",
    "meta-llama/Meta-Llama-3-70B",
    "mistralai/Mistral-7B-v0.1",
    "mistralai/Mistral-7B-Instruct-v0.1",
    "google/flan-t5-base",
    "google/flan-t5-large",
    "google/flan-t5-xl",
    "microsoft/phi-2",
    "microsoft/Phi-3-mini-4k-instruct",
]

MODEL_FAMILY = {
    "meta-llama/Llama-2-7b-hf": "llama2",
    "meta-llama/Llama-2-13b-hf": "llama2",
    "meta-llama/Llama-2-70b-hf": "llama2",
    "meta-llama/Meta-Llama-3-8B": "llama3",
    "meta-llama/Meta-Llama-3-70B": "llama3",
    "mistralai/Mistral-7B-v0.1": "mistral",
    "mistralai/Mistral-7B-Instruct-v0.1": "mistral",
    "google/flan-t5-base": "flan-t5",
    "google/flan-t5-large": "flan-t5",
    "google/flan-t5-xl": "flan-t5",
    "microsoft/phi-2": "phi",
    "microsoft/Phi-3-mini-4k-instruct": "phi",
}

# Params in billions (used for log(params) partial correlation control)
MODEL_PARAMS = {
    "meta-llama/Llama-2-7b-hf": 7.0,
    "meta-llama/Llama-2-13b-hf": 13.0,
    "meta-llama/Llama-2-70b-hf": 70.0,
    "meta-llama/Meta-Llama-3-8B": 8.0,
    "meta-llama/Meta-Llama-3-70B": 70.0,
    "mistralai/Mistral-7B-v0.1": 7.0,
    "mistralai/Mistral-7B-Instruct-v0.1": 7.0,
    "google/flan-t5-base": 0.25,
    "google/flan-t5-large": 0.78,
    "google/flan-t5-xl": 3.0,
    "microsoft/phi-2": 2.7,
    "microsoft/Phi-3-mini-4k-instruct": 3.8,
}

# 70B models require offloaded/sequential inference (NFR-3 fallback)
LARGE_MODELS = {"meta-llama/Llama-2-70b-hf", "meta-llama/Meta-Llama-3-70B"}

# Dataset config
TRUTHFULQA_TASK = "truthfulqa_mc1"      # lm-eval-harness task name
TRUTHFULQA_SPLIT = "validation"
TRUTHFULQA_NUM_QUESTIONS = 817           # full test set

SST2_DATASET = "glue/sst2"
SST2_SPLIT = "validation"
TEXTFOOLER_RECIPE = "textfooler"
TEXTFOOLER_NUM_EXAMPLES = 1000

# Eval params
BATCH_SIZE = 4
SEED = 42
N_BOOTSTRAP = 1000

# Success thresholds (gate condition)
R_THRESHOLD = 0.5
P_THRESHOLD = 0.05
BOOTSTRAP_CI_EXCLUDES = 0.3
PARTIAL_R_THRESHOLD = 0.3

# Paths
RESULTS_PATH = "results/results.json"
ANALYSIS_PATH = "results/analysis.json"
FIGURES_DIR = "figures/"
```

### YAML Schema Equivalent (reference only, not used — dict is source of truth)

```yaml
models:
  ids: [12 HF model ids, see MODEL_IDS]
  family_map: {model_id: family}
  params_billions: {model_id: float}
  large_models: [llama2-70b, llama3-70b]

datasets:
  truthfulqa: {task: truthfulqa_mc1, split: validation, n: 817}
  sst2: {dataset: glue/sst2, split: validation, attack_recipe: textfooler, n: 1000}

eval:
  batch_size: 4
  seed: 42

stats:
  n_bootstrap: 1000
  r_threshold: 0.5
  p_threshold: 0.05
  bootstrap_ci_excludes: 0.3
  partial_r_threshold: 0.3

paths:
  results: results/results.json
  analysis: results/analysis.json
  figures: figures/
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | config.py | All constants above (models, datasets, stats, thresholds, paths) — single file, no loader needed since it's a plain Python module |
