# Configuration: H-M2 — RLHF Representation Rigidity Reduces Adversarial Robustness

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-M1)
**Status**: Config classes verified from `h-m1/code/config.py` (actual implementation)
**Config Files Found**: `h-m1/code/config.py` — module-level constants, no dataclass
**Pattern Used**: Hardcoded module-level constants (matching H-M1 style)

Applied: Standard scipy statistical analysis defaults (no matching KB pattern for this domain)

---

## Inherited Configuration (Base Hypothesis)

### Config Constants (From Actual H-M1 Code)

```python
# Verified from: h-m1/code/config.py (actual implementation)
DIMENSIONS = ["truthfulness", "safety", "fairness", "robustness", "privacy", "machine_ethics"]
SAFETY_IDX = 1                        # unchanged
# ETHICS_IDX = 5                      # H-M1 only — NOT inherited
SECONDARY_GATE_MIN = 2                # >=2 of 3 pairs — unchanged
N_PAIRS = 3                           # unchanged
BONFERRONI_ALPHA = 0.0033             # 0.05/15 — unchanged
LLAMA2_SCALES = ["7b", "13b", "70b"]
LLAMA2_BASE_NAMES = ["LLaMA-2-7b-base", "LLaMA-2-13b-base", "LLaMA-2-70b-base"]
LLAMA2_CHAT_NAMES = ["LLaMA-2-7b-chat", "LLaMA-2-13b-chat", "LLaMA-2-70b-chat"]
LLAMA2_PAIRS = list(zip(LLAMA2_BASE_NAMES, LLAMA2_CHAT_NAMES, LLAMA2_SCALES))
```

---

## A-6: Pythia Scale-Only Control [Complexity: 2, Budget: 3 subtasks]

### Configuration

```python
# config.py (h-m2/code/)
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_HM2 = os.path.dirname(_HERE)
_RESEARCH = os.path.dirname(_HM2)

# --- Inherited from H-M1 (verified field names) ---
DIMENSIONS = ["truthfulness", "safety", "fairness", "robustness", "privacy", "machine_ethics"]
SAFETY_IDX = 1
ROBUSTNESS_IDX = 3               # New: replaces ETHICS_IDX=5 from H-M1
RHO_THRESHOLD = -0.4             # New: signed threshold (H-M1 used 0.5 unsigned)
SECONDARY_GATE_MIN = 2
N_PAIRS = 3
BONFERRONI_ALPHA = 0.0033
LLAMA2_SCALES = ["7b", "13b", "70b"]
LLAMA2_BASE_NAMES = ["LLaMA-2-7b-base", "LLaMA-2-13b-base", "LLaMA-2-70b-base"]
LLAMA2_CHAT_NAMES = ["LLaMA-2-7b-chat", "LLaMA-2-13b-chat", "LLaMA-2-70b-chat"]
LLAMA2_PAIRS = list(zip(LLAMA2_BASE_NAMES, LLAMA2_CHAT_NAMES, LLAMA2_SCALES))

# --- Paths (updated from H-M1) ---
HE1_JSON = os.path.join(_RESEARCH, "h-e1", "experiment_results_phase3.json")
RESULTS_JSON = os.path.join(_HM2, "experiment_results_h_m2.json")
FIGURES_DIR = os.path.join(_HM2, "figures")
LOG_PATH = os.path.join(_HM2, "experiment.log")

# --- Pythia control (A-6) ---
PYTHIA_SIZES = ["70m", "160m", "410m", "1b", "1.4b", "2.8b", "6.9b", "12b"]
PYTHIA_MODEL_PREFIX = "EleutherAI/pythia-"
PYTHIA_LMEVAL_TASK = "advglue"
PYTHIA_CACHE_KEY = "pythia_results"   # key to check in HE1_JSON before running lm-eval
# If lm-eval unavailable or cache miss: set pythia_rho to null, log limitation

# --- Reproducibility ---
SEED = 1
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Cache check | Check HE1_JSON for `pythia_results` key; skip lm-eval if present |
| C-6-2 | lm-eval fallback | Config for optional `lm_eval` CLI call per PYTHIA_SIZES |
| C-6-3 | Null result handling | If unavailable: pythia_rho = null, note as limitation |

---

## A-5: Ablation Configuration [Complexity: 2, Budget: 2 subtasks]

### Configuration

```python
# Ablation modes appended to config.py
ABLATION_MODES = {
    "uncontrolled": {
        "covariates": [],              # raw Spearman, no OLS residualization
        "description": "No covariate control — baseline Spearman(safety, robustness)"
    },
    "scale_only": {
        "covariates": ["log_params"],  # control for scale only
        "description": "Partial Spearman controlling for log(param_count) only"
    },
    "rlhf_only": {
        "covariates": ["is_RLHF"],     # control for alignment status only
        "description": "Partial Spearman controlling for RLHF status only"
    },
}

# Primary analysis uses both covariates (not an ablation mode):
PRIMARY_COVARIATES = ["log_params", "is_RLHF"]

# Model metadata (log10 of param count, is_RLHF flag)
MODEL_METADATA = {
    "llama_2_7b":        {"log_params": 6.845, "is_RLHF": 0},
    "llama_2_7b_chat":   {"log_params": 6.845, "is_RLHF": 1},
    "llama_2_13b":       {"log_params": 7.114, "is_RLHF": 0},
    "llama_2_13b_chat":  {"log_params": 7.114, "is_RLHF": 1},
    "llama_2_70b":       {"log_params": 7.845, "is_RLHF": 0},
    "llama_2_70b_chat":  {"log_params": 7.845, "is_RLHF": 1},
    # remaining 10 TrustLLM models loaded from HE1_JSON annotations
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Ablation mode loop | Iterate ABLATION_MODES, call compute_partial_spearman with each covariate set |
| C-5-2 | Ablation results key | Save per-mode rho/p-value under `"ablations"` key in RESULTS_JSON |
