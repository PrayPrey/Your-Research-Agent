# Configuration Design: h-e1
**Hypothesis:** Reformulation rate decrease AND diversity correlation exist in HH-RLHF conversations with ≥5 turns
**Type:** EXISTENCE (LIGHT tier)
**Date:** 2026-08-25
**Subtask Budget:** 3 subtasks

---

## Applied Patterns

**Applied:** Dataclass Configuration Pattern (manual reference)
- Type-safe configuration via Python dataclasses
- Hierarchical config structure (dataset, model, analysis, output)
- Default values for all hyperparameters

**Applied:** Experiment Reproducibility Pattern
- Fixed random seed
- Versioned dependencies
- All thresholds configurable

---

## Configuration Schema

### Top-Level Configuration

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ExperimentConfig:
    """
    Top-level experiment configuration for h-e1.
    """
    # Dataset
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    
    # Reformulation Detection
    reformulation: ReformulationConfig = field(default_factory=ReformulationConfig)
    
    # Statistical Testing
    statistics: StatisticsConfig = field(default_factory=StatisticsConfig)
    
    # Output
    output: OutputConfig = field(default_factory=OutputConfig)
    
    # Reproducibility
    random_seed: int = 42
```

### Dataset Configuration

```python
@dataclass
class DatasetConfig:
    """
    HH-RLHF dataset loading and filtering settings.
    """
    # Source
    name: str = "Anthropic/hh-rlhf"
    split: str = "train"  # or "test" for final validation
    
    # Filtering
    min_turns: int = 5
    """Minimum conversation length for slope estimation"""
    
    max_conversations: Optional[int] = None
    """Max conversations to load (None = all). For debugging."""
    
    cache_dir: Optional[str] = None
    """HuggingFace cache directory"""
```

#### Subtask C.1: Dataset Filter Tuning

**Purpose:** Allow dynamic adjustment of turn threshold if ≥5 turns yields insufficient data.

**Tunable Parameters:**
- `min_turns`: [3, 4, 5, 6] (default: 5)
- `min_helpfulness`: Optional filter for high-quality conversations

**Fallback Logic:**
```python
if len(filtered_conversations) < 1000:
    config.dataset.min_turns = 4  # Relax constraint
```

### Reformulation Detection Configuration

```python
@dataclass
class ReformulationConfig:
    """
    Dual-signal reformulation detection settings.
    """
    # SBERT Model
    sbert_model_name: str = "all-MiniLM-L6-v2"
    """SentenceTransformer model for semantic similarity"""
    
    sbert_batch_size: int = 1000
    """Batch size for SBERT encoding (memory vs speed tradeoff)"""
    
    # Thresholds
    semantic_threshold: float = 0.7
    """Min cosine similarity for semantic match"""
    
    syntactic_threshold: float = 0.3
    """Min normalized edit distance for syntactic change"""
    
    # Device
    device: str = "cpu"
    """SBERT device: 'cpu' or 'cuda' (GPU optional for this experiment)"""
```

#### Subtask C.2: Threshold Calibration

**Purpose:** Allow threshold tuning to optimize reformulation detection precision/recall.

**Tunable Parameters:**
- `semantic_threshold`: [0.6, 0.7, 0.8] (default: 0.7)
- `syntactic_threshold`: [0.2, 0.3, 0.4] (default: 0.3)

**Calibration Protocol:**
1. Sample 100 query pairs
2. Manual annotation (is reformulation? yes/no)
3. Grid search over threshold pairs
4. Select pair maximizing F1 score

### Statistical Testing Configuration

```python
@dataclass
class StatisticsConfig:
    """
    Hypothesis testing and validation settings.
    """
    # Hypothesis Test
    alpha: float = 0.05
    """Significance level for hypothesis testing"""
    
    test_type: str = "one_sample_t"
    """Test type: 'one_sample_t', 'sign_test', or 'both'"""
    
    baseline_mean: float = 0.0
    """Null hypothesis mean (0 = no learning)"""
    
    # Effect Size
    compute_effect_size: bool = True
    """Compute Cohen's d effect size"""
    
    effect_size_baseline: float = 0.0
    """Baseline for effect size computation"""
```

#### Subtask C.3: Statistical Test Selection

**Purpose:** Allow fallback to non-parametric test if slope distribution is non-normal.

**Options:**
- `one_sample_t`: Parametric t-test (assumes normality)
- `sign_test`: Non-parametric (no normality assumption)
- `both`: Run both tests, report more conservative p-value

**Selection Logic:**
```python
if shapiro_wilk_test(slopes).p_value < 0.05:
    # Non-normal distribution
    config.statistics.test_type = "sign_test"
else:
    config.statistics.test_type = "one_sample_t"
```

### Output Configuration

```python
@dataclass
class OutputConfig:
    """
    Visualization and reporting settings.
    """
    # Directories
    figures_dir: str = "h-e1/figures"
    results_dir: str = "h-e1/results"
    logs_dir: str = "h-e1/logs"
    
    # Figure Settings
    figure_format: str = "png"
    """Output format: 'png', 'pdf', 'svg'"""
    
    figure_dpi: int = 300
    """DPI for raster formats"""
    
    figure_size: tuple = (8, 6)
    """Default figure size (width, height) in inches"""
    
    # Visualization Toggles
    generate_required_figures: bool = True
    """Gate metrics comparison (mandatory)"""
    
    generate_recommended_figures: bool = True
    """Reformulation over turns, slope distribution, etc."""
    
    # Logging
    log_level: str = "INFO"
    """Logging level: 'DEBUG', 'INFO', 'WARNING', 'ERROR'"""
```

---

## YAML Configuration (Alternative)

For command-line execution, equivalent YAML config:

```yaml
# h-e1/config.yaml
experiment:
  random_seed: 42

dataset:
  name: "Anthropic/hh-rlhf"
  split: "train"
  min_turns: 5
  max_conversations: null
  cache_dir: null

reformulation:
  sbert_model_name: "all-MiniLM-L6-v2"
  sbert_batch_size: 1000
  semantic_threshold: 0.7
  syntactic_threshold: 0.3
  device: "cpu"

statistics:
  alpha: 0.05
  test_type: "one_sample_t"
  baseline_mean: 0.0
  compute_effect_size: true
  effect_size_baseline: 0.0

output:
  figures_dir: "h-e1/figures"
  results_dir: "h-e1/results"
  logs_dir: "h-e1/logs"
  figure_format: "png"
  figure_dpi: 300
  figure_size: [8, 6]
  generate_required_figures: true
  generate_recommended_figures: true
  log_level: "INFO"
```

**Loading:**
```python
import yaml
from dacite import from_dict

with open("h-e1/config.yaml") as f:
    config_dict = yaml.safe_load(f)

config = from_dict(ExperimentConfig, config_dict["experiment"])
```

---

## Hyperparameter Tuning Guide

### Critical Hyperparameters

| Parameter | Default | Range | Impact |
|-----------|---------|-------|--------|
| `min_turns` | 5 | [3, 6] | Sample size vs slope reliability |
| `semantic_threshold` | 0.7 | [0.6, 0.8] | Reformulation precision/recall |
| `syntactic_threshold` | 0.3 | [0.2, 0.4] | Reformulation precision/recall |
| `alpha` | 0.05 | [0.01, 0.1] | Type I error rate |

### Tuning Priority

1. **Dataset filtering (`min_turns`):** Tune FIRST to ensure sufficient sample size
2. **Reformulation thresholds:** Tune if reformulation detection appears unreliable (use calibration protocol)
3. **Statistical test type:** Tune if normality assumption violated
4. **Output settings:** Cosmetic, tune last

---

## Inherited Configuration

None (FOUNDATION hypothesis - no base configuration)

---

## Subtask Summary

**Total Subtasks:** 3 (within budget)

1. **Subtask C.1:** Dataset filter tuning (min_turns fallback logic)
2. **Subtask C.2:** Threshold calibration (precision/recall optimization)
3. **Subtask C.3:** Statistical test selection (parametric vs non-parametric)

---

## Dependencies

**Required Libraries:**
```python
# Configuration management
pyyaml==6.0
dacite==1.8.0  # YAML → dataclass conversion
```

---

**Configuration Status:** Complete
**Next:** Overall Complexity Assessment (Step 6)
