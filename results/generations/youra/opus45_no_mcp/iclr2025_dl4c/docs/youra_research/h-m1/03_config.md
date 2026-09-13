# Configuration Spec: h-m1 (Gradient Concentration Analysis)

**Type:** MECHANISM — analysis config, no training sweep
**Format:** Python Dataclass
**Base:** Extends H-E1 config with analysis parameters

## Codebase Analysis (Serena)

**Project Type:** incremental
**Status:** Extends H-E1 config.py with gradient analysis settings
**Config Files Found:** h-e1/code/config.py
**Pattern Used:** dataclass (same as H-E1)

**Applied:** H-E1 model/reward config + new analysis parameters

---

## Config Definitions

```python
from dataclasses import dataclass, field
from typing import List, Optional

# Reuse from H-E1
from h_e1.code.config import ModelConfig, RewardConfig, ErrorCategoryConfig


@dataclass
class AnalysisConfig:
    """H-M1 specific: gradient concentration analysis settings."""
    n_samples: int = 500                   # Total failing samples to analyze
    n_u_line: int = 250                    # Target U_line samples
    n_u_ignore: int = 250                  # Target U_ignore samples
    concentration_threshold: float = 1.0   # Primary criterion: ratio > threshold
    within_lines_threshold: float = 0.80   # Secondary: within ±2 lines
    within_lines_window: int = 2           # ±N lines for secondary metric
    random_baseline_seed: int = 42         # For random penalty baseline
    p_value_threshold: float = 0.05        # Statistical significance


@dataclass
class GradientConfig:
    """Settings for gradient extraction."""
    gradient_source: str = "embedding"     # 'embedding' | 'all_params'
    normalize_by_line_length: bool = True  # Normalize gradient by tokens per line
    min_tokens_per_line: int = 1           # Skip lines with fewer tokens
    eps: float = 1e-8                      # Numerical stability


@dataclass
class SampleCollectionConfig:
    """Settings for failing sample generation."""
    max_generation_attempts: int = 2000    # Attempts before giving up
    generation_timeout_s: int = 30         # Per-sample generation timeout
    execution_timeout_s: int = 30          # Code execution timeout (from H-E1)
    require_parseable_traceback: bool = True
    min_code_lines: int = 3                # Skip trivially short code
    max_code_lines: int = 100              # Skip extremely long code


@dataclass
class VisualizationConfig:
    """Figure generation settings."""
    figure_format: str = "png"
    figure_dpi: int = 150
    color_error_line: str = "#d62728"      # Red for error line
    color_other_lines: str = "#1f77b4"     # Blue for other
    color_random: str = "#7f7f7f"          # Gray for random baseline
    heatmap_cmap: str = "YlOrRd"


@dataclass
class H_M1_Config:
    """Complete H-M1 experiment configuration."""
    # Reused from H-E1
    model: ModelConfig = field(default_factory=ModelConfig)
    reward: RewardConfig = field(default_factory=lambda: RewardConfig(gating_mode="fine_always"))
    error_categories: ErrorCategoryConfig = field(default_factory=ErrorCategoryConfig)
    
    # H-M1 specific
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    gradient: GradientConfig = field(default_factory=GradientConfig)
    sample_collection: SampleCollectionConfig = field(default_factory=SampleCollectionConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    
    # Output paths
    output_dir: str = "h-m1/results"
    figures_dir: str = "h-m1/figures"
```

## YAML Equivalent (reference only, dataclass is source of truth)

```yaml
# Inherited from H-E1
model:
  base_model: "Salesforce/codet5-large"
  max_input_length: 512
  max_output_length: 256

reward:
  fine_penalty: -1.0
  coarse_penalty: -0.1
  pass_reward: 1.0
  gating_mode: "fine_always"  # Analyze fine-grained mode

error_categories:
  u_line: ["SyntaxError", "IndentationError", "NameError", "TypeError", "AttributeError", "KeyError", "IndexError"]
  u_ignore: ["RuntimeError", "RecursionError", "MemoryError", "TimeoutError", "AssertionError"]

# H-M1 specific
analysis:
  n_samples: 500
  n_u_line: 250
  n_u_ignore: 250
  concentration_threshold: 1.0
  within_lines_threshold: 0.80
  within_lines_window: 2
  random_baseline_seed: 42
  p_value_threshold: 0.05

gradient:
  gradient_source: "embedding"
  normalize_by_line_length: true
  min_tokens_per_line: 1
  eps: 1.0e-8

sample_collection:
  max_generation_attempts: 2000
  generation_timeout_s: 30
  execution_timeout_s: 30
  require_parseable_traceback: true
  min_code_lines: 3
  max_code_lines: 100

visualization:
  figure_format: "png"
  figure_dpi: 150
  color_error_line: "#d62728"
  color_other_lines: "#1f77b4"
  color_random: "#7f7f7f"
  heatmap_cmap: "YlOrRd"

output:
  output_dir: "h-m1/results"
  figures_dir: "h-m1/figures"
```

## Default Value Sources

| Field | Value | Source |
|-------|-------|--------|
| n_samples | 500 | 02c_experiment_brief.md specification |
| concentration_threshold | 1.0 | Gate condition: ratio > 1.0 |
| within_lines_threshold | 0.80 | Gate condition: >80% within ±2 lines |
| within_lines_window | 2 | Standard ±2 lines from RLTF analysis |
| p_value_threshold | 0.05 | Standard significance level |
| gradient_source | embedding | Most interpretable gradient signal |
| max_generation_attempts | 2000 | ~4x samples needed for 500 valid |
| model.* | (from H-E1) | CodeT5-large defaults |
| reward.* | (from H-E1) | RLTF paper equations 4-5 |

## Validation Rules

- `analysis.n_samples == analysis.n_u_line + analysis.n_u_ignore` (for balanced stratification)
- `analysis.concentration_threshold > 0` — ratio threshold must be positive
- `analysis.within_lines_threshold` in (0, 1] — percentage threshold
- `gradient.gradient_source in {"embedding", "all_params"}` — valid gradient sources
- `sample_collection.max_generation_attempts >= analysis.n_samples` — enough attempts
- `reward.gating_mode == "fine_always"` for H-M1 — analyze fine-grained mechanism
- `visualization.figure_format in {"png", "pdf", "svg"}` — supported formats

## Subtasks

No subtask decomposition — config is static definition file only.

## Differences from H-E1

| Aspect | H-E1 | H-M1 |
|--------|------|------|
| Purpose | Training PoC | Mechanism analysis |
| reward.gating_mode | Both modes | fine_always only |
| training.* | Full PPO config | Not used |
| analysis.* | Not present | 500 samples, thresholds |
| gradient.* | Not present | Gradient extraction settings |
