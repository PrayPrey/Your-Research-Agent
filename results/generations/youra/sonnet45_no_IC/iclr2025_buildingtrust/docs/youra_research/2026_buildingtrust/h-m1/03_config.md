# Configuration Schema: h-m1

**Date:** 2026-07-12
**Hypothesis:** h-m1 (MECHANISM - Reliability-Robustness Correlation via Memorization)
**Type:** MECHANISM
**Author:** Configuration Agent

---

## Applied Patterns

**Archon KB:**
- Applied: Standard statistical analysis defaults (scipy.stats)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config classes verified from h-e1 base code
**Config Files Found:** h-e1/code/src/config.py
**Pattern Used:** dataclass

**Verified from:** `/workspace/TEST_buildingtrust/docs/youra_research/h-e1/code/src/config.py` (actual implementation)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited from h-e1:

```python
# From: h-e1/code/src/config.py (ACTUAL CODE)
@dataclass
class DatasetConfig:
    name: str = "truthful_qa"
    split: str = "generation"
    validation_split: str = "validation"
    expected_samples: int = 817
    cache_dir: str = field(default_factory=lambda: os.path.expanduser("~/.cache/huggingface/datasets"))

@dataclass
class ModelConfig:
    model_sizes: List[str] = field(default_factory=lambda: ["7b"])
    model_name_template: str = "meta-llama/Llama-2-{size}-chat-hf"
    torch_dtype: str = "float16"
    device_map: str = "auto"
    cache_dir: str = field(default_factory=lambda: os.path.expanduser("~/.cache/huggingface/hub"))

@dataclass
class GenerationConfig:
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 256
    do_sample: bool = True
    seed_base: int = 42

@dataclass
class ReliabilityConfig:
    model: str = "gpt-4"
    validation_sample_size: int = 100
    agreement_threshold: float = 0.90
    max_retries: int = 5
    retry_delay: float = 1.0
    api_key_env: str = "OPENAI_API_KEY"

@dataclass
class RobustnessConfig:
    sbert_model: str = "all-MiniLM-L6-v2"
    paraphrase_method: str = "backtranslation"
    translation_source: str = "fr"
```

**Note:** Field names verified from h-e1 implementation (not spec docs).

---

## B-1: Stratified Dataset Preparation [Complexity: 9, Budget: 1]

**Applied:** Standard PyTorch/HuggingFace defaults

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List
import os

@dataclass
class StratificationConfig:
    factual_categories: List[str] = field(default_factory=lambda: [
        "Science", "History", "Geography", "Health"
    ])
    misinformation_categories: List[str] = field(default_factory=lambda: [
        "Misconceptions", "Myths and Fairytales", "Conspiracies"
    ])
    min_stratum_size: int = 350
    max_stratum_size: int = 450
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Category-based stratification | Split TruthfulQA by category into factual/misinformation strata |

---

## B-2: Response Generation Pipeline [Complexity: 11, Budget: 1]

**Applied:** Inherits from h-e1 GenerationConfig

### Configuration (Python Dataclass)

```python
# Reuse h-e1 GenerationConfig (no changes needed)
# Extended with checkpoint management:

@dataclass
class CheckpointConfig:
    checkpoint_dir: str = "checkpoints"
    save_frequency: int = 100
    resume_enabled: bool = True
    stratum_checkpoint_pattern: str = "{model}_{stratum}_{idx}.pt"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Batch generation with checkpointing | Generate responses for 3 models × 2 strata with fault tolerance |

---

## B-3: Reliability and Robustness Scoring [Complexity: 13, Budget: 1]

**Applied:** Inherits from h-e1 ReliabilityConfig and RobustnessConfig

### Configuration (Python Dataclass)

```python
# Reuse h-e1 ReliabilityConfig and RobustnessConfig
# No new config needed - same scorers, doubled sample size
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Stratified scoring orchestration | Apply h-e1 scorers to factual and misinformation strata separately |

---

## B-4: Correlation Analysis Module [Complexity: 15, Budget: 1]

**Applied:** Standard scipy.stats defaults (alpha=0.05, 95% CI)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class CorrelationConfig:
    alpha: float = 0.05
    correlation_threshold: float = 0.3
    ci_lower_threshold: float = 0.2
    n_permutations: int = 1000
    confidence_level: float = 0.95
    method: str = "pearson"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Pearson r with Fisher z CI | Compute correlation, confidence intervals, and permutation test |

---

## B-5: Stratification Analysis [Complexity: 12, Budget: 1]

**Applied:** Standard comparison defaults

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class StratificationAnalysisConfig:
    primary_stratum: str = "factual"
    comparison_stratum: str = "misinformation"
    gate_validation_stratum: str = "factual"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Per-stratum correlation comparison | Compute and compare correlation coefficients across strata |

---

## B-6: Statistical Validation [Complexity: 10, Budget: 0]

**Applied:** Hypothesis-defined gate thresholds

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class GateValidationConfig:
    mechanism_gate_r_threshold: float = 0.3
    mechanism_gate_p_threshold: float = 0.05
    mechanism_gate_ci_threshold: float = 0.2
```

No subtasks decomposition (0/0 budget used - single validation function).

---

## B-7: Visualization Suite [Complexity: 14, Budget: 1]

**Applied:** Standard matplotlib/seaborn defaults

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class VisualizationConfig:
    figure_format: str = "png"
    dpi: int = 300
    figsize: tuple = (10, 6)
    style: str = "seaborn-v0_8-darkgrid"
    mandatory_figures: List[str] = field(default_factory=lambda: [
        "gate_metrics_comparison"
    ])
    optional_figures: List[str] = field(default_factory=lambda: [
        "scatter_with_regression",
        "model_comparison",
        "permutation_test",
        "confidence_intervals",
        "stratification_comparison"
    ])
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Six-figure generation suite | Generate all correlation visualizations including mandatory gate plot |

---

## B-8: Results Management [Complexity: 8, Budget: 0]

**Applied:** Standard JSON/CSV serialization

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class OutputConfig:
    output_dir: str = "outputs"
    figures_dir: str = "figures"
    responses_factual_file: str = "responses_factual.json"
    responses_misinfo_file: str = "responses_misinfo.json"
    results_factual_file: str = "results_factual.csv"
    results_misinfo_file: str = "results_misinfo.csv"
    correlation_results_file: str = "correlation_results.json"
    validation_report_file: str = "04_validation.md"
```

No subtasks decomposition (0/0 budget used).

---

## Master Configuration

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
import os

@dataclass
class ExperimentConfig:
    # Inherited from h-e1
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    reliability: ReliabilityConfig = field(default_factory=ReliabilityConfig)
    robustness: RobustnessConfig = field(default_factory=RobustnessConfig)
    
    # New for h-m1
    stratification: StratificationConfig = field(default_factory=StratificationConfig)
    checkpoint: CheckpointConfig = field(default_factory=CheckpointConfig)
    correlation: CorrelationConfig = field(default_factory=CorrelationConfig)
    stratification_analysis: StratificationAnalysisConfig = field(default_factory=StratificationAnalysisConfig)
    gate_validation: GateValidationConfig = field(default_factory=GateValidationConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    
    # API keys
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    
    def validate(self) -> bool:
        """Validate configuration completeness"""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        os.makedirs(self.output.output_dir, exist_ok=True)
        os.makedirs(self.checkpoint.checkpoint_dir, exist_ok=True)
        os.makedirs(self.output.figures_dir, exist_ok=True)
        
        return True

def load_config() -> ExperimentConfig:
    """Load experiment configuration with validation"""
    config = ExperimentConfig()
    config.validate()
    return config
```

---

## Usage Example

```python
from src.config import load_config

# Load validated configuration
config = load_config()

# Access inherited configs
print(f"Temperature: {config.generation.temperature}")
print(f"Models: {config.model.model_sizes}")

# Access new correlation configs
print(f"Correlation threshold: {config.correlation.correlation_threshold}")
print(f"Gate r threshold: {config.gate_validation.mechanism_gate_r_threshold}")

# Pass to components
data_loader = StratifiedTruthfulQALoader(config.dataset, config.stratification)
generator = LlamaResponseGenerator(config.model, config.generation)
corr_analyzer = PearsonCorrelationAnalyzer(config.correlation)
strat_analyzer = StratificationAnalyzer(config.stratification_analysis, corr_analyzer)
visualizer = CorrelationVisualizer(config.visualization, config.output.figures_dir)
```

---

## Model Size Configuration

```python
# For full experiment (3 models):
config.model.model_sizes = ["7b", "13b", "70b"]

# For PoC (single model):
config.model.model_sizes = ["7b"]
```

---

## MECHANISM Gate Validation Logic

```python
def validate_mechanism_gate(factual_result: dict, config: GateValidationConfig) -> bool:
    """
    Validate MECHANISM hypothesis gate on factual stratum.
    
    Returns:
        True if r>0.3, p<0.05, CI>0.2, else False
    """
    r = factual_result["correlation"]
    p = factual_result["p_value"]
    ci_lower = factual_result["ci_95"][0]
    
    gate_passed = (
        r > config.mechanism_gate_r_threshold and
        p < config.mechanism_gate_p_threshold and
        ci_lower > config.mechanism_gate_ci_threshold
    )
    
    return gate_passed
```

---

## Rationale for Non-Standard Values

- **n_permutations=1000**: Standard for permutation tests (provides p<0.001 resolution)
- **correlation_threshold=0.3**: Defined by hypothesis specification for moderate effect size
- **ci_lower_threshold=0.2**: Conservative threshold ensuring CI excludes weak correlation
- **min_stratum_size=350**: Statistical power requirement (n≥350 for detecting r=0.3 at α=0.05, power=0.8)

All other values inherit from h-e1 with standard defaults from literature.

---

## Environment Variables

Required environment variables:

```bash
export OPENAI_API_KEY="sk-..."
```

---

## Configuration File Location

Save as: `h-m1/code/src/config.py`

This configuration extends h-e1 with:
- Stratification parameters for factual/misinformation split
- Correlation analysis configuration (Pearson r, Fisher z CI, permutation test)
- MECHANISM gate validation thresholds
- Extended visualization suite

**Subtask Budget:** 6/6 used across 8 tasks

---

**Document Status:** FINAL
**Last Updated:** 2026-07-12
**Next Phase:** Phase 4 - Implementation (Coder Agent)
