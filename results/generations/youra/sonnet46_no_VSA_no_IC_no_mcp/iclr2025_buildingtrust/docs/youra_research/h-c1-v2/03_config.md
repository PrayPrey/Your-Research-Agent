# Config: h-c1-v2
# RLHF Calibration Moderation — Task-Type-Conditional ΔΔECE Analysis

Applied: dataclass inheritance pattern (base_hypothesis extension)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from base code
**Config Files Found**: `docs/youra_research/h-c1/code/config.py`
**Pattern Used**: dataclass inheritance (HC1V2Config extends HC1Config)

---

## Inherited Configuration (Base Hypothesis)

```python
# From: docs/youra_research/h-c1/code/config.py (ACTUAL CODE)
@dataclass
class HC1Config(ExperimentConfig):
    models: List[str] = field(default_factory=lambda: [
        "meta-llama/Llama-2-7b-hf",
        "meta-llama/Llama-2-7b-chat-hf",
    ])
    subsample_clean: int = 1000
    subsample_adv: int = 1000
    n_bins: int = 15
    eval_cells: Dict[str, Tuple[str, str]] = field(default_factory=lambda: {
        "NLI-AdvGLUE":  ("mnli",      "advglue_mnli"),
        "NLI-ANLI-R1":  ("multi_nli", "anli_r1"),
        "NLI-ANLI-R2":  ("multi_nli", "anli_r2"),
        "NLI-ANLI-R3":  ("multi_nli", "anli_r3"),
    })
    moderation_rate_threshold: float = 0.60
    ddece_nli_threshold: float = 0.01      # field name in actual code
    he1_base_ece_clean_nli: float = 0.279
    he1_base_delta_ece_nli: float = 0.071
    consistency_tolerance: float = 0.005
    consistency_failure_mode: str = "warn"
    results_dir: str = "docs/youra_research/h-c1/results"
    figures_dir: str = "docs/youra_research/h-c1/figures"
    errors_log: str = "docs/youra_research/h-c1/results/errors.log"
    results_file: str = "docs/youra_research/h-c1/results/hc1_results.json"
    validation_report: str = "docs/youra_research/h-c1/04_validation.md"
```

**Verified from**: `docs/youra_research/h-c1/code/config.py` (actual implementation)

---

## A-7: Visualization [Complexity: 13, Budget: 2 subtasks]

Applied: Standard matplotlib/seaborn config dataclass

### Configuration

```python
@dataclass
class PlotConfig:
    # Figure dimensions (width, height) in inches
    fig_size_bar: tuple = (10, 6)
    fig_size_reliability: tuple = (12, 5)
    fig_size_hist: tuple = (8, 5)
    fig_size_heatmap: tuple = (10, 6)
    fig_size_scatter: tuple = (7, 5)
    dpi: int = 300
    font_size: int = 12

    # Color scheme for DDECE bar chart
    color_moderation: str = "#2ca02c"   # green: DDECE > 0.01
    color_reversal: str = "#d62728"     # red: DDECE < 0
    color_neutral: str = "#7f7f7f"      # gray: |DDECE| <= 0.01

    # Color scheme for heatmap (DECE values)
    heatmap_cmap: str = "RdYlGn_r"     # Non-standard: reversed so red=high degradation
    heatmap_vmin: float = -0.15
    heatmap_vmax: float = 0.15

    # Output paths
    figures_dir: str = "docs/youra_research/h-c1-v2/figures"
    fig1_bar: str = "figures/ddece_comparison_bar.png"
    fig2_reliability: str = "figures/reliability_diagram_{split}.png"
    fig3_hist: str = "figures/confidence_distribution_adv.png"
    fig4_heatmap: str = "figures/moderation_heatmap.png"
    fig5_scatter: str = "figures/ddece_vs_difficulty.png"

    # Reliability diagram settings
    n_bins: int = 15                    # must match ECE computation bins

    # Scatter plot x-axis labels (ANLI difficulty)
    difficulty_labels: tuple = (1, 2, 3)  # R1=1, R2=2, R3=3
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | PlotConfig dataclass | PlotConfig with figure sizes, DPI, color schemes, output paths |
| C-7-2 | YAML plot defaults | YAML schema for all 5 figure settings with defaults |

---

## A-2: Cache Loader [Complexity: 9, Budget: 2 subtasks]

Applied: Standard path config dataclass

### Configuration

```python
@dataclass
class CacheConfig:
    # H-C1 cache paths
    h_c1_results_file: str = "docs/youra_research/h-c1/results/hc1_results.json"
    h_m1_label_mask_path: str = "docs/youra_research/h-m1/results/label_preservation_mask.npy"

    # Schema validation: required keys in each cell entry
    required_cache_keys: tuple = ("logits", "labels", "split_id")
    schema_version: str = "h-c1-v1"

    # Expected cell IDs in cache
    expected_cells: tuple = (
        "NLI-ANLI-R1", "NLI-ANLI-R2", "NLI-ANLI-R3", "NLI-AdvGLUE"
    )
    expected_models: tuple = (
        "meta-llama/Llama-2-7b-hf",
        "meta-llama/Llama-2-7b-chat-hf",
    )

    # Validation strictness: "raise" or "warn"
    validation_mode: str = "raise"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | CacheConfig dataclass | Paths, schema version, validation rules, mask path |
| C-2-2 | YAML cache schema | YAML schema for cache configuration with defaults |

---

## A-6: Cross-size Validation [Complexity: 9, Budget: 2 subtasks]

### Configuration

```python
import sys, os
_HC1_CODE = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../h-c1/code"))
if _HC1_CODE not in sys.path:
    sys.path.insert(0, _HC1_CODE)

from config import HC1Config
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class HC1V2Config(HC1Config):
    # Override: add 13B model
    models: List[str] = field(default_factory=lambda: [
        "meta-llama/Llama-2-7b-hf",
        "meta-llama/Llama-2-7b-chat-hf",
        "meta-llama/Llama-2-13b-chat-hf",
    ])

    # Benchmark-type groupings
    anli_cells: List[str] = field(default_factory=lambda: [
        "NLI-ANLI-R1", "NLI-ANLI-R2", "NLI-ANLI-R3"
    ])
    advglue_cells: List[str] = field(default_factory=lambda: ["NLI-AdvGLUE"])

    # Model pairs: (base_model_id, chat_model_id)
    model_pairs: List[Tuple[str, str]] = field(default_factory=lambda: [
        ("meta-llama/Llama-2-7b-hf", "meta-llama/Llama-2-7b-chat-hf"),
        ("meta-llama/Llama-2-7b-hf", "meta-llama/Llama-2-13b-chat-hf"),
    ])

    # Cache paths (h-c1 pre-computed results)
    h_c1_results_file: str = "docs/youra_research/h-c1/results/hc1_results.json"
    h_m1_label_mask_path: str = "docs/youra_research/h-m1/results/label_preservation_mask.npy"

    # Key hyperparameters
    n_bins: int = 15                        # inherited from HC1Config, re-stated for clarity
    ddece_threshold: float = 0.01           # Non-standard field name: HC1Config uses ddece_nli_threshold
    moderation_rate_threshold: float = 0.60 # gate: >=60% ANLI cells moderated
    seed: int = 1                           # matches h-e1 fixed seed

    # Output paths (override h-c1 defaults)
    results_dir: str = "docs/youra_research/h-c1-v2/results"
    figures_dir: str = "docs/youra_research/h-c1-v2/figures"
    results_file: str = "docs/youra_research/h-c1-v2/results/hc1v2_results.json"
    validation_report: str = "docs/youra_research/h-c1-v2/04_validation.md"
    errors_log: str = "docs/youra_research/h-c1-v2/results/errors.log"
    new_inference_output: str = "docs/youra_research/h-c1-v2/results/13b_chat"

    # Fallback paths (if 13B inference not yet run)
    fallback_13b_results: str = ""          # empty = no fallback, raise on missing
```

### Full HC1V2Config YAML Schema

```yaml
# h-c1-v2 experiment config (all defaults shown)
# Override any field by setting it here.

# Key hyperparameters
n_bins: 15
ddece_threshold: 0.01
moderation_rate_threshold: 0.60
seed: 1
subsample_clean: 1000
subsample_adv: 1000

# Models
models:
  - "meta-llama/Llama-2-7b-hf"
  - "meta-llama/Llama-2-7b-chat-hf"
  - "meta-llama/Llama-2-13b-chat-hf"

model_pairs:
  - ["meta-llama/Llama-2-7b-hf", "meta-llama/Llama-2-7b-chat-hf"]
  - ["meta-llama/Llama-2-7b-hf", "meta-llama/Llama-2-13b-chat-hf"]

# Benchmark cell groupings
anli_cells:
  - "NLI-ANLI-R1"
  - "NLI-ANLI-R2"
  - "NLI-ANLI-R3"
advglue_cells:
  - "NLI-AdvGLUE"

# Cache paths (h-c1 pre-computed)
h_c1_results_file: "docs/youra_research/h-c1/results/hc1_results.json"
h_m1_label_mask_path: "docs/youra_research/h-m1/results/label_preservation_mask.npy"
fallback_13b_results: ""

# Output paths
results_dir: "docs/youra_research/h-c1-v2/results"
figures_dir: "docs/youra_research/h-c1-v2/figures"
results_file: "docs/youra_research/h-c1-v2/results/hc1v2_results.json"
new_inference_output: "docs/youra_research/h-c1-v2/results/13b_chat"
validation_report: "docs/youra_research/h-c1-v2/04_validation.md"
errors_log: "docs/youra_research/h-c1-v2/results/errors.log"

# Visualization
plot:
  dpi: 300
  font_size: 12
  fig_size_bar: [10, 6]
  fig_size_reliability: [12, 5]
  fig_size_hist: [8, 5]
  fig_size_heatmap: [10, 6]
  fig_size_scatter: [7, 5]
  color_moderation: "#2ca02c"
  color_reversal: "#d62728"
  color_neutral: "#7f7f7f"
  heatmap_cmap: "RdYlGn_r"
  heatmap_vmin: -0.15
  heatmap_vmax: 0.15

# Cache validation
cache:
  schema_version: "h-c1-v1"
  required_keys: ["logits", "labels", "split_id"]
  validation_mode: "raise"

# Environment variable overrides (prefix: HC1V2_)
# HC1V2_H_C1_RESULTS_FILE  -> h_c1_results_file
# HC1V2_NEW_INFERENCE_OUTPUT -> new_inference_output
# HC1V2_SEED               -> seed
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | CrossSizeConfig fields | 13B model ID, new_inference_output, fallback_13b_results, model_pairs |
| C-6-2 | Full HC1V2Config YAML | Complete YAML schema with all defaults and env var overrides |
