# Configuration Specification: h-m1 Benchmark Distinctiveness Analysis

**Hypothesis:** h-m1 (MECHANISM)  
**Date:** 2026-04-15  
**Author:** Configuration Agent  
**Type:** Statistical Analysis Configuration  

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Config verified from h-e1 actual implementation  
**Analyzed Path:** `/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_dl4c_2/docs/youra_research/20260415_dl4c/h-e1/code/src/config.py`  
**Findings:** h-e1 uses dataclass pattern with modular config classes. h-m1 reuses data loading infrastructure but adds statistical analysis configurations.

---

## Applied Patterns

**Applied:** Statistical Analysis Configuration Pattern (scipy-based analysis settings, gate thresholds)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited from h-e1 for data loading:

```python
# From: h-e1/code/src/config.py (ACTUAL CODE - VERIFIED)
@dataclass
class FeatureSchemaConfig:
    """Feature definitions and validation rules."""
    passk_values: List[int] = field(default_factory=lambda: [1, 10, 100])
    runtime_quartiles: List[float] = field(default_factory=lambda: [0.25, 0.50, 0.75])
    error_categories: List[str] = field(default_factory=lambda: ["syntax", "runtime", "timeout"])
    
    required_features: Dict[str, type] = field(default_factory=lambda: {
        'pass@1': float,
        'pass@10': float,
        'pass@100': float,
        'runtime_q25': float,
        'runtime_q50': float,
        'runtime_q75': float,
        'error_syntax': float,
        'error_runtime': float,
        'error_timeout': float
    })
    
    completeness_threshold: float = 95.0
```

**Verified from:** `h-e1/code/src/config.py` (actual implementation)

---

## M-1: Data Loading Infrastructure [Complexity: 6, Budget: 2 subtasks]

**Applied:** Reuse h-e1 data loading with validation

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List, Dict
from pathlib import Path

@dataclass
class DataLoadingConfig:
    """Configuration for loading h-e1 execution trace data."""
    
    # Path to h-e1 outputs (relative to h-m1/code/)
    h_e1_features_path: str = "../../../h-e1/code/outputs/features.csv"
    h_e1_validation_path: str = "../../../h-e1/code/outputs/validation_report.json"
    
    # Benchmarks available from h-e1 (APPS not included)
    available_benchmarks: List[str] = field(default_factory=lambda: ["HumanEval", "MBPP"])
    
    # Minimum requirements for analysis
    min_models_required: int = 8
    min_features_required: int = 9
    
    # Data quality validation
    require_validation_report: bool = True
    min_completeness_threshold: float = 90.0
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Data Path Configuration | Define paths to h-e1 outputs, benchmark list |
| C-1-2 | Quality Validation | Specify minimum requirements for loaded data |

---

## M-2: Ranking Correlation Analysis [Complexity: 9, Budget: 2 subtasks]

**Applied:** Standard scipy.stats configuration

### Configuration (Python Dataclass)

```python
@dataclass
class CorrelationConfig:
    """Configuration for Spearman correlation analysis."""
    
    # Statistical method
    method: str = "spearman"  # scipy.stats.spearmanr
    
    # Significance threshold
    significance_level: float = 0.05
    
    # Feature for ranking comparison
    ranking_feature: str = "pass@1"
    
    # Benchmark pairs to analyze (single pair from h-e1 data)
    benchmark_pairs: List[tuple] = field(default_factory=lambda: [
        ("HumanEval", "MBPP")
    ])
    
    # Output configuration
    save_correlation_matrix: bool = True
    correlation_matrix_path: str = "outputs/correlation_matrix.csv"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Statistical Method Config | Define correlation method, significance level |
| C-2-2 | Analysis Scope | Specify benchmark pairs, ranking features |

---

## M-3: Distribution Divergence Analysis [Complexity: 10, Budget: 2 subtasks]

**Applied:** Standard KL divergence configuration

### Configuration (Python Dataclass)

```python
@dataclass
class DivergenceConfig:
    """Configuration for KL divergence computation."""
    
    # Features to analyze for distribution differences
    divergence_features: List[str] = field(default_factory=lambda: [
        "pass@1",
        "runtime_q50",
        "runtime_q75"
    ])
    
    # Histogram binning for probability estimation
    histogram_bins: int = 20
    density_normalization: bool = True
    
    # Numerical stability
    epsilon: float = 1e-10  # Avoid log(0)
    
    # Output configuration
    save_divergence_scores: bool = True
    divergence_scores_path: str = "outputs/divergence_scores.csv"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Feature Selection | Define features for divergence analysis |
| C-3-2 | Histogram Parameters | Configure binning, normalization, numerical stability |

---

## M-4: Gate Condition Evaluation [Complexity: 7, Budget: 2 subtasks]

**Applied:** Threshold-based gate logic configuration

### Configuration (Python Dataclass)

```python
@dataclass
class GateConditionConfig:
    """Configuration for gate condition evaluation."""
    
    # Gate thresholds (from PRD)
    correlation_threshold: float = 0.8  # ρ < 0.8 indicates distinctiveness
    divergence_threshold: float = 0.1   # KL > 0.1 indicates distinctiveness
    
    # Gate logic (both conditions must be satisfied)
    require_both_conditions: bool = True
    
    # Reporting
    generate_detailed_report: bool = True
    report_path: str = "outputs/gate_evaluation.json"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Threshold Configuration | Define correlation and divergence thresholds |
| C-4-2 | Gate Logic | Specify evaluation logic and reporting |

---

## M-5: Visualization Generation [Complexity: 11, Budget: 2 subtasks]

**Applied:** Matplotlib/seaborn plotting configuration

### Configuration (Python Dataclass)

```python
@dataclass
class VisualizationConfig:
    """Configuration for figure generation."""
    
    # Output directory
    figures_directory: str = "figures"
    
    # Figure settings
    figure_dpi: int = 300
    figure_format: str = "png"
    
    # Required figures
    required_figures: List[str] = field(default_factory=lambda: [
        "correlation_heatmap.png",          # MANDATORY - gate metric
        "kl_divergence_bars.png",
        "ranking_scatter_humaneval_mbpp.png",
        "feature_distributions.png"
    ])
    
    # Plot styling
    colormap_correlation: str = "coolwarm"  # Blue=low, Red=high
    colormap_divergence: str = "viridis"
    font_size: int = 12
    title_font_size: int = 14
    
    # Threshold annotations
    annotate_thresholds: bool = True
    correlation_threshold_line: float = 0.8
    divergence_threshold_line: float = 0.1
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Figure Specifications | Define required figures, output format, DPI |
| C-5-2 | Styling Configuration | Configure colormaps, fonts, threshold annotations |

---

## M-6: Results Integration [Complexity: 8, Budget: 2 subtasks]

**Applied:** Standard experiment configuration pattern

### Configuration (Python Dataclass)

```python
@dataclass
class ExperimentConfig:
    """Master configuration for h-m1 analysis pipeline."""
    
    # Sub-configurations
    data_loading: DataLoadingConfig = field(default_factory=DataLoadingConfig)
    correlation: CorrelationConfig = field(default_factory=CorrelationConfig)
    divergence: DivergenceConfig = field(default_factory=DivergenceConfig)
    gate_condition: GateConditionConfig = field(default_factory=GateConditionConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    
    # Global settings
    experiment_name: str = "h-m1-benchmark-distinctiveness"
    hypothesis_type: str = "MECHANISM"
    gate_type: str = "SHOULD_WORK"
    
    # Output directories
    output_directory: str = "outputs"
    results_directory: str = "results"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "outputs/analysis.log"
    
    # Random seed (for reproducibility if any stochastic operations)
    random_seed: int = 42

# Default configuration factory
def get_default_config() -> ExperimentConfig:
    """Returns default configuration for h-m1 analysis."""
    return ExperimentConfig()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Master Configuration | Integrate all sub-configs, experiment metadata |
| C-6-2 | Output Management | Configure logging, output directories |

---

## Configuration Usage Example

```python
# config.py - Main configuration file for h-m1

from dataclasses import dataclass, field
from typing import List, Dict
from pathlib import Path

# Import all configuration classes defined above

# Usage in main.py
if __name__ == "__main__":
    config = get_default_config()
    
    # Create output directories
    Path(config.output_directory).mkdir(parents=True, exist_ok=True)
    Path(config.visualization.figures_directory).mkdir(parents=True, exist_ok=True)
    
    # Run analysis pipeline
    from src.main import AnalysisPipeline
    pipeline = AnalysisPipeline(config)
    results = pipeline.run()
    
    # Check gate condition
    gate_passed = results['gate_satisfied']
    print(f"Gate Result: {'PASS' if gate_passed else 'FAIL'}")
```

---

## File Structure

**Configuration files to create in Phase 4:**

```
h-m1/code/
├── src/
│   ├── config.py                    # All dataclasses above
│   ├── data/
│   │   └── loader.py                # Uses DataLoadingConfig
│   ├── analysis/
│   │   ├── correlation.py           # Uses CorrelationConfig
│   │   └── divergence.py            # Uses DivergenceConfig
│   ├── validation/
│   │   └── gate_checker.py          # Uses GateConditionConfig
│   ├── visualization/
│   │   └── plots.py                 # Uses VisualizationConfig
│   └── main.py                      # Uses ExperimentConfig
└── outputs/
    ├── correlation_matrix.csv
    ├── divergence_scores.csv
    ├── gate_evaluation.json
    └── analysis_results.json
```

---

## Configuration Notes

### Path Configuration

The `h_e1_features_path` uses relative path `../../../h-e1/code/outputs/features.csv` because:
- h-m1 code location: `docs/youra_research/20260415_dl4c/h-m1/code/`
- h-e1 outputs location: `docs/youra_research/20260415_dl4c/h-e1/code/outputs/`
- Relative path navigates correctly between sibling hypothesis directories

### Benchmark Pair Limitation

Single benchmark pair `(HumanEval, MBPP)` because:
- h-e1 only collected HumanEval and MBPP data (APPS not included)
- PRD specified 3 benchmarks but actual data availability determines scope
- Architecture document notes this limitation (lines 240-243)

### Statistical Method Defaults

- Spearman correlation: Standard for ranking comparison, non-parametric
- KL divergence bins=20: Balance between resolution and sample size stability
- Epsilon=1e-10: Standard numerical stability for log operations

### Gate Thresholds

- ρ < 0.8: Below this indicates benchmarks measure different aspects
- KL > 0.1: Above this indicates meaningful distribution differences
- Both from PRD requirements (lines 16, 145-147)

---

## Self-Validation Checklist

- [x] ONE format only (Python dataclass)
- [x] No ASCII diagrams
- [x] Applied patterns noted (1 line per section)
- [x] Rationale only for non-standard values (paths, thresholds)
- [x] Subtask count within budget (2/2 for each epic)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included (Serena verification)
- [x] Base hypothesis verification (h-e1 config.py actual code read)
- [x] Inherited Configuration section included
- [x] Field names verified from actual h-e1 implementation
- [x] MECHANISM hypothesis - minimal config (no hyperparameter tuning)
- [x] Copy-paste ready dataclass code

---

**Document Status:** Final Configuration for Phase 4 Implementation  
**Next Phase:** Phase 4 - Implementation (Coding)  
**Data Dependency:** h-e1 outputs (features.csv with 8 models × 2 benchmarks = 14 pairs)
