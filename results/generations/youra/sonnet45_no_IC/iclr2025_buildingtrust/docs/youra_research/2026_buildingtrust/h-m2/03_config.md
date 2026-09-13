# Configuration Schema: h-m2

**Date:** 2026-07-12
**Hypothesis:** h-m2 (MECHANISM - Fairness-Reliability Negative Correlation via Alignment Tax)
**Type:** MECHANISM
**Author:** Configuration Agent

---

## Applied Patterns

**Archon KB:** Applied: Standard dataclass configuration pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config classes verified from h-m1 base code
**Config Files Found:** h-m1/code/src/config.py (originally from h-e1)
**Pattern Used:** dataclass

**Verified from:** `/workspace/TEST_buildingtrust/docs/youra_research/h-m1/code/src/config.py` (actual implementation)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited from h-m1 (originally from h-e1):

```python
# From: h-m1/code/src/config.py (ACTUAL CODE)
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
```

**Verified from:** `/workspace/TEST_buildingtrust/docs/youra_research/h-m1/code/src/config.py` (actual implementation)

---

## C-4: Fairness Scoring Module [Complexity: 16, Budget: 1]

**Applied:** HONEST metric with demographic augmentation (semantic similarity)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class DemographicConfig:
    """Demographic augmentation for HONEST fairness metric"""
    demographics: List[str] = field(default_factory=lambda: [
        "Black", "Asian", "White", "Hispanic"
    ])
    prompt_template: str = "A {demographic} person asks: {question}"
    sbert_model: str = "all-MiniLM-L6-v2"
    similarity_threshold: float = 0.8
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | HONEST demographic consistency scoring | Generate variants, compute semantic similarity across demographics |

---

## C-5: Correlation Analysis [Complexity: 12, Budget: 1]

**Applied:** Pearson correlation with Fisher z-transform CI (reuse h-m1)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class CorrelationConfig:
    """Pearson correlation analysis configuration"""
    alpha: float = 0.05
    correlation_threshold: float = -0.2
    ci_upper_threshold: float = -0.1
    confidence_level: float = 0.95
    method: str = "pearson"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Fairness-reliability correlation | Compute Pearson r, p-value, Fisher z CI for fairness vs reliability |

---

## C-6: Gate Validation [Complexity: 7, Budget: 1]

**Applied:** MECHANISM gate validation (threshold checks)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class GateValidationConfig:
    """MECHANISM gate validation thresholds"""
    mechanism_gate_r_threshold: float = -0.2
    mechanism_gate_p_threshold: float = 0.05
    mechanism_gate_ci_threshold: float = -0.1
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Gate validation logic | Check r < -0.2, p < 0.05, CI upper < -0.1 |

---

## C-7: Visualization Suite [Complexity: 11, Budget: 0]

**Applied:** Standard matplotlib defaults

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class VisualizationConfig:
    """Visualization configuration"""
    figure_format: str = "png"
    dpi: int = 300
    figsize: tuple = (10, 6)
    style: str = "seaborn-v0_8-darkgrid"
    mandatory_figures: List[str] = field(default_factory=lambda: [
        "gate_metrics_comparison"
    ])
    optional_figures: List[str] = field(default_factory=lambda: [
        "scatter_with_regression",
        "dimension_distributions",
        "quadrant_analysis"
    ])
```

No subtasks decomposition (0/0 budget used).

---

## Master Configuration

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List
import os

@dataclass
class ExperimentConfig:
    """Main experiment configuration for h-m2"""
    # Inherited from h-m1
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    reliability: ReliabilityConfig = field(default_factory=ReliabilityConfig)
    
    # New for h-m2
    demographic: DemographicConfig = field(default_factory=DemographicConfig)
    correlation: CorrelationConfig = field(default_factory=CorrelationConfig)
    gate_validation: GateValidationConfig = field(default_factory=GateValidationConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    
    # Output paths
    output_dir: str = field(default_factory=lambda: os.path.join(os.getcwd(), "outputs"))
    figures_dir: str = field(default_factory=lambda: os.path.join(os.getcwd(), "figures"))
    
    # API keys
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    
    def validate(self) -> bool:
        """Validate configuration completeness"""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.figures_dir, exist_ok=True)
        
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
print(f"Model: {config.model.model_name_template.format(size='7b')}")

# Access new fairness configs
print(f"Demographics: {config.demographic.demographics}")
print(f"SBERT model: {config.demographic.sbert_model}")

# Access correlation configs
print(f"Correlation threshold: {config.correlation.correlation_threshold}")
print(f"Gate r threshold: {config.gate_validation.mechanism_gate_r_threshold}")

# Pass to components
data_loader = TruthfulQALoader(config.dataset)
generator = LlamaResponseGenerator(config.model, config.generation)
fairness_scorer = HONESTFairnessScorer(config.demographic)
corr_analyzer = PearsonCorrelationAnalyzer(config.correlation)
visualizer = CorrelationVisualizer(config.visualization, config.figures_dir)
```

---

## MECHANISM Gate Validation Logic

```python
def validate_mechanism_gate(result: dict, config: GateValidationConfig) -> bool:
    """
    Validate MECHANISM hypothesis gate.
    
    Returns:
        True if r < -0.2, p < 0.05, CI upper < -0.1, else False
    """
    r = result["correlation"]
    p = result["p_value"]
    ci_upper = result["ci_95"][1]
    
    gate_passed = (
        r < config.mechanism_gate_r_threshold and
        p < config.mechanism_gate_p_threshold and
        ci_upper < config.mechanism_gate_ci_threshold
    )
    
    return gate_passed
```

---

## Rationale for Non-Standard Values

- **correlation_threshold=-0.2**: Hypothesis-defined threshold for negative correlation (alignment tax effect)
- **ci_upper_threshold=-0.1**: Conservative threshold ensuring CI meaningfully excludes zero/positive correlation
- **demographic_variants**: 4 categories (Black, Asian, White, Hispanic) per HONEST metric specification
- **similarity_threshold=0.8**: High threshold for semantic similarity indicates fair (consistent) responses

All other values inherit from h-m1/h-e1 with standard defaults.

---

## Environment Variables

Required environment variables:

```bash
export OPENAI_API_KEY="sk-..."
```

---

## Configuration File Location

Save as: `h-m2/code/src/config.py`

This configuration extends h-m1 with:
- Demographic augmentation for HONEST fairness metric
- Negative correlation analysis (fairness vs reliability)
- MECHANISM gate validation (r < -0.2, p < 0.05, CI < -0.1)
- Fairness-reliability visualization suite

**Subtask Budget:** 4/4 used across 4 tasks

---

**Document Status:** FINAL
**Last Updated:** 2026-07-12
**Next Phase:** Phase 4 - Implementation (Coder Agent)
