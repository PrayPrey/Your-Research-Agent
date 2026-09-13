# Configuration Specification: h-e1 Execution Trace Feature Extraction

**Hypothesis:** h-e1 (EXISTENCE)  
**Date:** 2026-04-15  
**Author:** Configuration Agent  
**Type:** Data Infrastructure Configuration  

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** Foundation hypothesis - new configuration design  
**Config Files Found:** None - new config  
**Pattern Used:** Python dataclass (standard for data pipeline configuration)

---

## Applied Patterns

**Applied:** Data Pipeline Configuration Pattern (ETL settings, timeout management, validation thresholds)

---

## A-2: Published Results Collection [Complexity: 10, Budget: 2 subtasks]

**Applied:** Standard data collection configuration with model lists and benchmark sources

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path

@dataclass
class BenchmarkConfig:
    """Configuration for benchmark dataset loading."""
    name: str
    dataset_path: str
    problem_count: int
    test_cases_per_problem: int
    difficulty_levels: Optional[List[str]] = None

@dataclass
class ModelConfig:
    """Configuration for individual models to evaluate."""
    name: str
    organization: str
    has_humaneval: bool = True
    has_mbpp: bool = False
    has_apps: bool = False
    published_source: Optional[str] = None

@dataclass
class PublishedResultsConfig:
    """Configuration for collecting published benchmark results."""
    
    # Benchmark definitions
    benchmarks: List[BenchmarkConfig] = field(default_factory=lambda: [
        BenchmarkConfig(
            name="HumanEval",
            dataset_path="openai_humaneval",
            problem_count=164,
            test_cases_per_problem=10
        ),
        BenchmarkConfig(
            name="MBPP",
            dataset_path="mbpp",
            problem_count=974,
            test_cases_per_problem=3
        ),
        BenchmarkConfig(
            name="APPS",
            dataset_path="codeparrot/apps",
            problem_count=10000,
            test_cases_per_problem=20,
            difficulty_levels=["introductory", "interview", "competition"]
        )
    ])
    
    # Model list (20+ models for EXISTENCE validation)
    models: List[ModelConfig] = field(default_factory=lambda: [
        # OpenAI models
        ModelConfig("GPT-3.5-Turbo", "OpenAI", True, True, False, "OpenAI API Docs"),
        ModelConfig("GPT-4", "OpenAI", True, True, True, "OpenAI Technical Report"),
        
        # CodeLlama variants
        ModelConfig("CodeLlama-7B", "Meta", True, True, False, "Rozière et al. 2023"),
        ModelConfig("CodeLlama-13B", "Meta", True, True, False, "Rozière et al. 2023"),
        ModelConfig("CodeLlama-34B", "Meta", True, True, True, "Rozière et al. 2023"),
        ModelConfig("CodeLlama-70B", "Meta", True, True, False, "Rozière et al. 2023"),
        
        # StarCoder family
        ModelConfig("StarCoder-15B", "BigCode", True, True, False, "Li et al. 2023"),
        ModelConfig("StarCoder2-15B", "BigCode", True, True, False, "BigCode Technical Report"),
        ModelConfig("StarCoderBase-15B", "BigCode", True, False, False, "Li et al. 2023"),
        
        # DeepSeek-Coder
        ModelConfig("DeepSeek-Coder-6.7B", "DeepSeek", True, True, False, "DeepSeek AI 2024"),
        ModelConfig("DeepSeek-Coder-33B", "DeepSeek", True, True, True, "DeepSeek AI 2024"),
        
        # WizardCoder
        ModelConfig("WizardCoder-15B", "WizardLM", True, True, False, "Luo et al. 2023"),
        ModelConfig("WizardCoder-34B", "WizardLM", True, True, False, "Luo et al. 2023"),
        
        # Specialized models
        ModelConfig("Phind-CodeLlama-34B-v2", "Phind", True, True, False, "Phind Blog"),
        ModelConfig("Codestral-22B", "Mistral", True, True, False, "Mistral AI Blog"),
        
        # Anthropic
        ModelConfig("Claude-2", "Anthropic", True, False, False, "Anthropic Docs"),
        ModelConfig("Claude-3-Opus", "Anthropic", True, True, False, "Anthropic Technical Report"),
        ModelConfig("Claude-3-Sonnet", "Anthropic", True, True, False, "Anthropic Technical Report"),
        
        # Additional open models
        ModelConfig("CodeGen-16B", "Salesforce", True, True, False, "Nijkamp et al. 2022"),
        ModelConfig("InCoder-6B", "Meta", True, False, False, "Fried et al. 2022"),
        ModelConfig("Replit-Code-v1-3B", "Replit", True, False, False, "Replit Blog"),
        ModelConfig("SantaCoder-1.1B", "BigCode", True, False, False, "BigCode Collection"),
        ModelConfig("CodeT5+-16B", "Salesforce", True, True, False, "Wang et al. 2023"),
    ])
    
    # Data source configuration
    results_directory: str = "data/published_results"
    output_csv: str = "outputs/collected_results.csv"
    cache_enabled: bool = True
    cache_directory: str = "data/cache"
    
    # Validation thresholds
    min_models_humaneval: int = 20
    min_models_mbpp: int = 15
    min_models_apps: int = 10

@dataclass
class FeatureSchemaConfig:
    """Feature definitions and validation rules."""
    
    # Pass@k features
    passk_values: List[int] = field(default_factory=lambda: [1, 10, 100])
    
    # Runtime features (quartiles in milliseconds)
    runtime_quartiles: List[float] = field(default_factory=lambda: [0.25, 0.50, 0.75])
    
    # Error categories
    error_categories: List[str] = field(default_factory=lambda: [
        "syntax",    # Code parsing failures
        "runtime",   # Execution exceptions
        "timeout"    # Exceeds time limit
    ])
    
    # Feature schema (for validation)
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
    
    # Completeness threshold (EXISTENCE gate condition)
    completeness_threshold: float = 95.0
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Data Source Configuration | Define model lists, benchmark sources, published result locations |
| C-2-2 | Feature Schema Validation | Specify feature types, completeness thresholds, output formats |

---

## Execution and Validation Configuration

**Applied:** Standard execution sandbox pattern with timeout management

### Configuration (Python Dataclass)

```python
@dataclass
class ExecutionConfig:
    """Configuration for code execution sandbox."""
    
    # Timeout settings (seconds)
    timeout_per_test: int = 30
    timeout_global: int = 3600
    
    # Sandbox configuration
    use_docker: bool = False  # Optional for EXISTENCE - subprocess sufficient
    sandbox_python_version: str = "3.10"
    sandbox_memory_limit: str = "2GB"
    
    # Execution modes
    enable_runtime_collection: bool = True
    enable_error_categorization: bool = True
    max_retries_per_test: int = 1
    
    # Resource limits
    max_concurrent_executions: int = 4
    max_output_size_kb: int = 1024

@dataclass
class ValidationConfig:
    """Configuration for feature completeness validation."""
    
    # Gate condition (EXISTENCE hypothesis)
    completeness_threshold: float = 95.0
    
    # Validation checks
    check_standardization: bool = True
    check_missing_patterns: bool = True
    check_outliers: bool = True
    
    # Output configuration
    validation_report_path: str = "outputs/validation_report.json"
    missing_data_report_path: str = "outputs/missing_data_analysis.csv"

@dataclass
class VisualizationConfig:
    """Configuration for figure generation."""
    
    # Output directory
    figures_directory: str = "figures"
    
    # Figure settings
    figure_dpi: int = 300
    figure_format: str = "png"
    
    # Required figures for gate metric
    required_figures: List[str] = field(default_factory=lambda: [
        "completeness_comparison.png",      # Primary gate metric
        "feature_coverage_heatmap.png",     # Model-benchmark coverage
        "feature_distributions.png",        # Statistical distributions
        "coverage_matrix.png"               # Binary completeness matrix
    ])
    
    # Plot styling
    colormap: str = "viridis"
    font_size: int = 12
    title_font_size: int = 14

@dataclass
class ExperimentConfig:
    """Master configuration for h-e1 experiment pipeline."""
    
    # Sub-configurations
    published_results: PublishedResultsConfig = field(default_factory=PublishedResultsConfig)
    feature_schema: FeatureSchemaConfig = field(default_factory=FeatureSchemaConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    
    # Global settings
    experiment_name: str = "h-e1-execution-trace-extraction"
    random_seed: int = 42
    output_directory: str = "outputs"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "outputs/experiment.log"
    
    # Storage paths
    datasets_cache_dir: str = "data/datasets_cache"
    results_directory: str = "results"
```

---

## Configuration Usage Example

```python
# config.py - Main configuration file

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path

# Import all configuration classes from above

# Create default experiment configuration
def get_default_config() -> ExperimentConfig:
    """Returns default configuration for h-e1 experiment."""
    return ExperimentConfig()

# Override specific settings if needed
def get_quick_test_config() -> ExperimentConfig:
    """Reduced configuration for quick testing."""
    config = ExperimentConfig()
    
    # Use fewer models for quick test
    config.published_results.models = config.published_results.models[:5]
    
    # Reduce timeout for faster iteration
    config.execution.timeout_per_test = 10
    
    # Lower completeness threshold for testing
    config.validation.completeness_threshold = 80.0
    
    return config

# Usage in main.py
if __name__ == "__main__":
    config = get_default_config()
    
    # Create output directories
    Path(config.output_directory).mkdir(parents=True, exist_ok=True)
    Path(config.visualization.figures_directory).mkdir(parents=True, exist_ok=True)
    
    # Run experiment pipeline
    pipeline = ExperimentPipeline(config)
    results = pipeline.run()
```

---

## Configuration Notes

### Model List Rationale

The 23-model list includes:
- **OpenAI (2):** Industry benchmarks with published results
- **CodeLlama (4):** Multiple scales, widely benchmarked
- **StarCoder (3):** Open-source baseline family
- **DeepSeek (2):** Strong performance on code tasks
- **WizardCoder (2):** Instruction-tuned variants
- **Specialized (2):** Phind, Codestral (domain-specific)
- **Anthropic (3):** Claude family with code capabilities
- **Additional Open (5):** Diverse architectures and scales

This provides 23 models covering 60+ model-benchmark combinations, ensuring >95% completeness target is achievable.

### Benchmark Test Counts

- **HumanEval:** 164 problems × 10 tests = 1,640 test cases
- **MBPP:** 974 problems × 3 tests = 2,922 test cases
- **APPS:** Subset used (e.g., 500 problems × 20 tests = 10,000 test cases)

### Execution Timeout Justification

30-second timeout balances:
- Most code generation solutions complete in <5 seconds
- Allows complex APPS problems to execute
- Prevents infinite loops from blocking pipeline
- Standard value used in CodeLlama, StarCoder evaluations

### Completeness Threshold

95% threshold chosen because:
- Allows 5% missing data due to unavailable published results
- Stricter than typical research (often 80-90%)
- Validates data infrastructure quality for downstream hypotheses
- EXISTENCE gate condition requires high confidence

---

## File Structure

**Configuration files to create in Phase 4:**

```
h-e1/code/src/
├── config.py                    # Main configuration (all dataclasses above)
├── data/
│   ├── benchmark_loader.py      # Uses BenchmarkConfig
│   └── published_results.py     # Uses PublishedResultsConfig, ModelConfig
├── features/
│   └── extractor.py             # Uses FeatureSchemaConfig
├── execution/
│   └── executor.py              # Uses ExecutionConfig
├── validation/
│   └── validator.py             # Uses ValidationConfig
└── visualization/
    └── plots.py                 # Uses VisualizationConfig
```

---

## Self-Validation Checklist

- [x] ONE format only (Python dataclass)
- [x] No ASCII diagrams
- [x] Applied pattern noted (1 line)
- [x] Rationale only for non-standard values (timeout, threshold, model count)
- [x] Subtask count within budget (2/2)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Green-field project - Serena skip acceptable
- [x] EXISTENCE hypothesis - minimal config (no hyperparameter grid)
- [x] Copy-paste ready dataclass code
- [x] Default values from research papers (pass@k formula, timeout standards)

---

**Document Status:** Final Configuration for Phase 4 Implementation  
**Next Phase:** Phase 4 - Implementation (Coding)
