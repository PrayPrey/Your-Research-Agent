# Configuration: h-m2 (Cross-Model Probe Transfer)

Applied: fixed-single-config pattern (KB returned only unrelated diffusion-model results; used h-e1 base-hypothesis convention instead — hardcoded dict, no format switch).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from actual h-e1 code (`h-e1/code/config.py`), read directly via file tool (Serena project not registered for this path)
**Config Files Found**: `h-e1/code/config.py` (module-level constants, no dataclass)
**Pattern Used**: Hardcoded dict (module-level constants) — matches base hypothesis pattern, extended for h-m2

---

## Inherited Configuration (Base Hypothesis)

Verified from `h-e1/code/config.py` (actual implementation):

```python
# Inherited unchanged from h-e1
SEED = 42

MODELS = {
    "llama3-8b": {
        "id": "meta-llama/Meta-Llama-3-8B-Instruct",
        "n_layers": 32,
        "hidden_dim": 4096,
    },
    "mistral-7b": {
        "id": "mistralai/Mistral-7B-Instruct-v0.2",
        "n_layers": 32,
        "hidden_dim": 4096,
    },
    "qwen2-7b": {
        "id": "Qwen/Qwen2-7B-Instruct",
        "n_layers": 28,
        "hidden_dim": 3584,
    },
}

NLI_MODEL_ID = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli"

N_SAMPLES = 5
TEMPERATURE = 0.7
TRAIN_SPLIT = 0.8
LAYER_FRACTION = 2 / 3

TORCH_DTYPE = "float16"
DEVICE_MAP = "auto"
```

**Field names confirmed matching**: `MODELS`, `SEED`, `LAYER_FRACTION`, `TRAIN_SPLIT` used as-is by vendored `data.py`/`models.py`/`sep.py` (per architecture.md External Dependencies table).

---

## A-1: Config module (extends base) [Complexity: 2, Budget: 1 subtask]

**Applied**: h-e1 base config extension — inherited constants unchanged + new transfer-specific paths/thresholds

### Configuration (Hardcoded dict)

```python
# config.py — h-m2
import os

# --- Inherited from h-e1 (unchanged) ---
SEED = 42

MODELS = {
    "llama3-8b": {"id": "meta-llama/Meta-Llama-3-8B-Instruct", "n_layers": 32, "hidden_dim": 4096},
    "mistral-7b": {"id": "mistralai/Mistral-7B-Instruct-v0.2", "n_layers": 32, "hidden_dim": 4096},
    "qwen2-7b": {"id": "Qwen/Qwen2-7B-Instruct", "n_layers": 28, "hidden_dim": 3584},
}

NLI_MODEL_ID = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli"
N_SAMPLES = 5
TEMPERATURE = 0.7
TRAIN_SPLIT = 0.8
LAYER_FRACTION = 2 / 3
TORCH_DTYPE = "float16"
DEVICE_MAP = "auto"

# --- New for h-m2 ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
CACHE_DIR = os.path.join(BASE_DIR, "cache")

# Transfer gap thresholds (PRD success criteria)
GAP_ALIGNMENT_TRIGGER = 0.10   # if direct-transfer gap exceeds this, retry with affine alignment
MEAN_GAP_SUCCESS_THRESHOLD = 0.10
MAX_GAP_SUCCESS_THRESHOLD = 0.15
```

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Config module | `config.py`: inherited MODELS/SEED/LAYER_FRACTION/etc. unchanged + new CACHE_DIR/RESULTS_DIR/FIGURES_DIR + gap thresholds |

---

## A-2: Hidden state cache [Complexity: 5, Budget: 1 subtask]

**Applied**: Standard NPY disk-cache convention keyed by `(model_key, split)`

### Configuration (Hardcoded dict)

```python
# cache.py config (consumed by HiddenStateCache)
CACHE_FILENAME_TEMPLATE = "{model_key}_{split}.npy"  # e.g. "llama3-8b_train.npy"
CACHE_SPLITS = ("train", "val")
```

Uses `CACHE_DIR` from A-1. No new tunable hyperparameters — cache is pure I/O (save/load/exists via `np.save`/`np.load`).

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-2-1 | Cache path/filename config | `CACHE_FILENAME_TEMPLATE`, `CACHE_SPLITS` consumed by `HiddenStateCache.path()` |

---

## Fixed Experiment Parameters (No Tuning — MECHANISM test)

| Param | Value | Source |
|-------|-------|--------|
| Dataset | TruthfulQA (817 questions) | PRD |
| Train/val split | 80/20 (654/163), `TRAIN_SPLIT=0.8`, `SEED=42` | Inherited h-e1 |
| Label binarization | Median threshold on semantic entropy | PRD FR-2 |
| Probe | `LogisticRegression(max_iter=1000, C=1.0)` | h-e1 SEP methodology (reused, unchanged) |
| Layer selection | `LAYER_FRACTION = 2/3` per model | Inherited h-e1 |
| Affine alignment | `np.linalg.lstsq`, fit on train split only | PRD FR-4 |
| Evaluations | 9 (3 baseline + 6 transfer) | PRD FR-3 |

No hyperparameter grid — single fixed config per MECHANISM verification protocol (direct transfer first, affine alignment fallback only if `gap > GAP_ALIGNMENT_TRIGGER`).
