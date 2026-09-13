# H-M4 Configuration: Layer-wise Grassmann Distance Analysis

Applied: flat-module hardcoded-dict config pattern (H-M3 base)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M3)
**Status**: Config classes verified from H-M3 base code
**Config Files Found**: `h-m3/code/config.py`
**Pattern Used**: hardcoded dict (flat module, no dataclass)

Key findings from H-M3 actual code:
- Seeds are integers `[42, 43, 44, 45, 46]` (NOT `seed_42` format as PRD states)
- LORA_CONFIG uses `lora_alpha` (not `alpha`), `lora_dropout` included
- VIZ_CONFIG uses named figsize keys per chart type
- ANALYSIS_CONFIG separate from TAXONOMY_CONFIG

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-m3/code/config.py (ACTUAL CODE - verified)
SEEDS: list = [42, 43, 44, 45, 46]          # integer seeds, NOT seed_42 format
N_ADAPTERS: int = 40

LORA_CONFIG = {
    "r": 32,
    "lora_alpha": 64,
    "lora_dropout": 0.05,
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "up_proj", "down_proj", "gate_proj"],
}

TASK_CATEGORIES = {
    "gsm8k": "reasoning", "arc": "reasoning",
    "logiqa": "reasoning", "strategyqa": "reasoning",
    "mnli": "nlu", "qqp": "nlu", "sst2": "nlu", "mrpc": "nlu",
}

VIZ_CONFIG = {
    "dpi": 150,
    "format": "png",
    "reasoning_color": "#4C72B0",
    "nlu_color": "#DD8452",
    "threshold_line_color": "red",
    "style": "whitegrid",
    "font_scale": 1.1,
}
```

**Verified from**: `h-m3/code/config.py` (actual implementation)

---

## A-2: Adapter Loading [Complexity: 10, Budget: 2 subtasks]

Applied: flat-module hardcoded-dict config pattern

### Configuration

```python
# In config.py

import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# H-E1 paths (adapter data source)
H_E1_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, "../../h-e1"))
H_E1_RESULTS_DIR = os.path.join(H_E1_DIR, "results")
H_E1_ADAPTER_DIR = os.path.join(H_E1_DIR, "adapters")
H_E1_CODE_DIR = os.path.join(H_E1_DIR, "code")

if H_E1_CODE_DIR not in sys.path:
    sys.path.append(H_E1_CODE_DIR)

# H-M4 output paths
HYPOTHESIS_FOLDER = os.path.dirname(_SCRIPT_DIR)
RESULTS_DIR = os.path.join(HYPOTHESIS_FOLDER, "results")
FIGURES_DIR = os.path.join(HYPOTHESIS_FOLDER, "figures")

for _dir in [RESULTS_DIR, FIGURES_DIR]:
    os.makedirs(_dir, exist_ok=True)

# Tasks and seeds (verified: integer seeds from h-e1/results/adapter_metadata.json)
TASKS: list = ["gsm8k", "arc", "logiqa", "strategyqa", "mnli", "qqp", "sst2", "mrpc"]
SEEDS: list = [0, 1, 2, 3, 4]   # Non-standard: actual metadata uses 0-4 (not 42-46 as in H-M3)
N_ADAPTERS: int = 40

TASK_CATEGORIES: dict = {
    "gsm8k": "reasoning", "arc": "reasoning",
    "logiqa": "reasoning", "strategyqa": "reasoning",
    "mnli": "nlu", "qqp": "nlu", "sst2": "nlu", "mrpc": "nlu",
}

# Layer type definitions
ATTENTION_LAYER_TYPES: list = ["q_proj", "k_proj", "v_proj", "o_proj"]
MLP_LAYER_TYPES: list = ["up_proj", "down_proj", "gate_proj"]
ALL_LAYER_TYPES: list = ATTENTION_LAYER_TYPES + MLP_LAYER_TYPES  # 7 total
N_TRANSFORMER_LAYERS: int = 22  # TinyLlama architecture

LORA_CONFIG: dict = {
    "r": 32,
    "lora_alpha": 64,
    "lora_dropout": 0.05,
    "target_modules": ALL_LAYER_TYPES,
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Path Config | H_E1_DIR, H_E1_RESULTS_DIR, H_E1_ADAPTER_DIR, H_E1_CODE_DIR, RESULTS_DIR, FIGURES_DIR with makedirs |
| C-2-2 | Adapter Constants | TASKS, SEEDS (integer 0-4), N_ADAPTERS, TASK_CATEGORIES, layer type lists, N_TRANSFORMER_LAYERS, LORA_CONFIG |

---

## A-5: Visualization [Complexity: 10, Budget: 2 subtasks]

Applied: flat-module hardcoded-dict config pattern

### Configuration

```python
# In config.py (continuation)

VIZ_CONFIG: dict = {
    # Figure sizes per chart type
    "bar_chart_figsize": (10, 6),      # cohens_d_by_layer_type
    "ranking_figsize": (8, 6),         # layer_type_ranking (horizontal bars)
    "comparison_figsize": (8, 6),      # attention_vs_mlp box/violin
    "heatmap_figsize": (9, 7),         # best_layer_heatmap 8x8

    # Colors
    "attention_color": "#4C72B0",      # blue for attention layers
    "mlp_color": "#DD8452",            # orange for MLP layers
    "threshold_line_color": "red",

    # Style
    "style": "whitegrid",
    "font_scale": 1.1,
    "dpi": 150,
    "format": "png",
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Figure Size Config | Per-chart figsize entries in VIZ_CONFIG |
| C-5-2 | Color & Style Config | attention_color, mlp_color, threshold_line_color, style, dpi, format |

---

## A-7: Tests [Complexity: 9, Budget: 1 subtask]

Applied: Standard PyTorch defaults

### Configuration

```python
# In config.py (continuation)

ANALYSIS_CONFIG: dict = {
    "cohens_d_threshold": 0.8,
    "n_bootstrap": 2000,
    "random_seed": 42,
    "ci_level": 0.95,
    "p_threshold": 0.05,
}

# Test config (used by tests/test_core.py)
TEST_CONFIG: dict = {
    "random_seed": 42,
    "n_adapters_small": 4,    # small fixture: 2 tasks x 2 seeds
    "n_layers_small": 3,      # reduced layers for fast unit tests
    "lora_r": 4,              # small rank for test matrices
    "hidden_dim": 16,         # small hidden dim for test matrices
    "atol": 1e-5,             # tolerance for numerical comparisons
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Test Constants | TEST_CONFIG with small fixtures for unit tests (n_adapters_small, n_layers_small, lora_r, hidden_dim, atol) |

---

## Complete config.py Reference

The full `config.py` combines all sections above in this order:
1. Path setup (imports, `_SCRIPT_DIR`, H-E1 paths, output paths, makedirs)
2. Task/adapter constants (TASKS, SEEDS, N_ADAPTERS, TASK_CATEGORIES)
3. Layer type constants (ATTENTION_LAYER_TYPES, MLP_LAYER_TYPES, ALL_LAYER_TYPES, N_TRANSFORMER_LAYERS)
4. LORA_CONFIG
5. ANALYSIS_CONFIG
6. VIZ_CONFIG
7. TEST_CONFIG
