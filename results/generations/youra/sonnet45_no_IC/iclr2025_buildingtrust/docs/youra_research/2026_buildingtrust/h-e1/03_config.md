# Configuration Schema: h-e1

**Date:** 2026-07-12
**Hypothesis:** h-e1 (EXISTENCE - Synchronized Multi-Dimensional Trustworthiness Evaluation)
**Type:** EXISTENCE (PoC)
**Author:** Configuration Agent

---

## Applied Patterns

**Archon KB:**
- Applied: Standard deep learning defaults pattern

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - designing new config schema
**Config Files Found:** None - new config
**Pattern Used:** dataclass

---

## Configuration Overview

EXISTENCE hypothesis requires minimal configuration with fixed parameters for proof-of-concept. All configurations use standard defaults from literature without hyperparameter tuning.

**Key Principles:**
- Single fixed config per component (no variations)
- Defaults from research papers
- 1 seed for deterministic generation
- Minimal epochs/samples (sufficient to measure variance)

---

## A-1: Dataset & Model Setup

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from typing import List

@dataclass
class DatasetConfig:
    dataset_name: str = "truthful_qa"
    subset: str = "generation"
    split: str = "validation"
    expected_size: int = 817

@dataclass
class ModelConfig:
    model_sizes: List[str] = None
    torch_dtype: str = "float16"
    device_map: str = "auto"
    
    def __post_init__(self):
        if self.model_sizes is None:
            self.model_sizes = [
                "meta-llama/Llama-2-7b-chat-hf",
                "meta-llama/Llama-2-13b-chat-hf",
                "meta-llama/Llama-2-70b-chat-hf"
            ]
```

---

## A-2: Response Generation Pipeline

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class GenerationConfig:
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 256
    do_sample: bool = True
    seed_base: int = 42

@dataclass
class CheckpointConfig:
    checkpoint_dir: str = "checkpoints"
    save_frequency: int = 100
    resume_from_checkpoint: bool = True
```

---

## A-3: Reliability Scoring

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class ReliabilityConfig:
    model_name: str = "gpt-4"
    max_retries: int = 3
    retry_delay_base: float = 1.0
    timeout: int = 30
    validation_sample_size: int = 100
    agreement_threshold: float = 0.9
```

---

## A-4: Robustness Scoring

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class RobustnessConfig:
    sbert_model: str = "all-MiniLM-L6-v2"
    translation_target_lang: str = "fr"
    max_retries: int = 3
    retry_delay_base: float = 1.0
    timeout: int = 30
```

---

## A-5: Fairness Scoring

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from typing import List

@dataclass
class FairnessConfig:
    demographic_categories: dict = None
    generation_params: dict = None
    
    def __post_init__(self):
        if self.demographic_categories is None:
            self.demographic_categories = {
                "race": ["Black", "White", "Asian", "Hispanic", "Indigenous"],
                "gender": ["male", "female", "non-binary"],
                "age": ["young adult", "middle-aged", "senior"]
            }
        if self.generation_params is None:
            self.generation_params = {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 256
            }
```

---

## A-6: Evaluation Orchestration

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class ValidationConfig:
    variance_threshold: float = 0.2
    required_dimensions: list = None
    completeness_threshold: float = 1.0
    
    def __post_init__(self):
        if self.required_dimensions is None:
            self.required_dimensions = ["reliability", "robustness", "fairness"]

@dataclass
class PipelineConfig:
    batch_size: int = 1
    parallel_scoring: bool = True
    max_workers: int = 3
    error_tolerance: float = 0.05
```

---

## A-7: Results Management & Visualization

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from typing import List

@dataclass
class OutputConfig:
    output_dir: str = "results"
    checkpoint_dir: str = "checkpoints"
    figures_dir: str = "figures"
    responses_file: str = "responses.json"
    results_file: str = "evaluation_results.csv"
    variance_stats_file: str = "variance_statistics.json"

@dataclass
class VisualizationConfig:
    figure_format: List[str] = None
    dpi: int = 300
    figsize: tuple = (10, 6)
    style: str = "seaborn-v0_8-darkgrid"
    
    def __post_init__(self):
        if self.figure_format is None:
            self.figure_format = ["png", "pdf"]
```

---

## Master Configuration

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
import os

@dataclass
class ExperimentConfig:
    # Component configs
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    checkpoint: CheckpointConfig = field(default_factory=CheckpointConfig)
    reliability: ReliabilityConfig = field(default_factory=ReliabilityConfig)
    robustness: RobustnessConfig = field(default_factory=RobustnessConfig)
    fairness: FairnessConfig = field(default_factory=FairnessConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    
    # API keys (loaded from environment)
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    translation_api_key: str = field(default_factory=lambda: os.getenv("TRANSLATION_API_KEY", ""))
    
    def validate(self) -> bool:
        """Validate configuration completeness and consistency."""
        # Check API keys
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        if not self.translation_api_key:
            raise ValueError("TRANSLATION_API_KEY environment variable not set")
        
        # Check paths exist
        os.makedirs(self.output.output_dir, exist_ok=True)
        os.makedirs(self.checkpoint.checkpoint_dir, exist_ok=True)
        os.makedirs(self.output.figures_dir, exist_ok=True)
        
        return True

def load_config() -> ExperimentConfig:
    """Load experiment configuration with validation."""
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

# Access nested configs
print(f"Temperature: {config.generation.temperature}")
print(f"Models: {config.model.model_sizes}")
print(f"Variance threshold: {config.validation.variance_threshold}")

# Pass to components
data_loader = TruthfulQALoader(config.dataset)
model_manager = LlamaModelManager(config.model)
response_generator = ResponseGenerator(config.generation, config.checkpoint)
reliability_scorer = GPT4ReliabilityScorer(config.reliability, config.openai_api_key)
robustness_scorer = ParaphraseRobustnessScorer(config.robustness, config.translation_api_key)
fairness_scorer = HONESTFairnessScorer(config.fairness)
```

---

## Environment Variables

Required environment variables for API access:

```bash
export OPENAI_API_KEY="sk-..."
export TRANSLATION_API_KEY="..."
```

---

## EXISTENCE Gate Configuration

The core validation logic uses fixed thresholds from the validation config:

```python
def validate_existence_gate(results: pd.DataFrame, config: ValidationConfig) -> bool:
    """
    Validate EXISTENCE hypothesis gate.
    
    Returns:
        True if all dimensions show σ > 0.2, False otherwise
    """
    variances = results[config.required_dimensions].std()
    
    for dimension in config.required_dimensions:
        if variances[dimension] <= config.variance_threshold:
            print(f"GATE FAILED: {dimension} σ={variances[dimension]:.3f} <= {config.variance_threshold}")
            return False
    
    print(f"GATE PASSED: All dimensions σ > {config.variance_threshold}")
    return True
```

---

## Rationale for Non-Standard Values

All configuration values use standard defaults from research:

- **temperature=0.7, top_p=0.9**: Standard values from Llama-2 paper (Touvron et al., 2023)
- **max_tokens=256**: Sufficient for TruthfulQA responses while managing API costs
- **variance_threshold=0.2**: Defined by hypothesis specification for sufficient statistical heterogeneity
- **sbert_model="all-MiniLM-L6-v2"**: Lightweight model with good performance from Sentence-BERT paper
- **validation_sample_size=100**: Minimum for 90% confidence interval on GPT-4 agreement

---

## Configuration File Location

Save as: `h-e1/code/src/config.py`

This single configuration file provides:
- Type-safe configuration with dataclasses
- Hierarchical organization matching architecture
- Environment variable integration for API keys
- Built-in validation
- Easy serialization/deserialization
- Zero subtask decomposition (0/0 budget used)

---

**Document Status:** FINAL
**Last Updated:** 2026-07-12
**Next Phase:** Phase 4 - Implementation (Coder Agent)
