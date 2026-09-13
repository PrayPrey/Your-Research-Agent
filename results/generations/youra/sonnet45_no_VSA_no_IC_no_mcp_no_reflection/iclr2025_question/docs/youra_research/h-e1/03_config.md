# Configuration Design: h-e1
## Hyperparameters, Settings, and YAML Schemas

**Date:** 2026-08-28  
**Hypothesis:** h-e1 (EXISTENCE)  
**Subtask Budget:** 2 tasks

---

## Codebase Analysis (Serena)

*MCP unavailable — manual design patterns applied*

**Applied Patterns:**
- Applied: `frozen_inference_config` — No training hyperparameters, only inference settings
- Applied: `dataset_config` — Split specification and preprocessing flags
- Applied: `evaluation_config` — Metric thresholds and significance levels

---

## Configuration Schema

### 1. Experiment Configuration

```yaml
# config.yaml — Main experiment configuration

experiment:
  name: "h-e1-entropy-correlation"
  hypothesis_id: "h-e1"
  type: "EXISTENCE"
  gate: "MUST_WORK"
  
dataset:
  name: "trivia_qa"
  config: "unfiltered"
  split: "validation[:1000]"
  cache_dir: "~/.cache/huggingface/datasets"
  
model:
  name: "meta-llama/Llama-2-7b-hf"
  cache_dir: "~/.cache/huggingface/hub"
  device: "cuda"  # Auto-fallback to "cpu" if CUDA unavailable
  max_input_length: 512
  
inference:
  batch_size: 1  # Sequential processing for PoC
  no_grad: true  # Frozen model
  
metrics:
  correlation_method: "spearman"
  significance_threshold: 0.05
  
gates:
  extraction_rate_threshold: 0.95
  p_value_threshold: 0.05
  q3_population_threshold: 0.05
  
output:
  figures_dir: "./figures"
  validation_report: "./04_validation.md"
  
logging:
  level: "INFO"
  log_file: "./experiment.log"
```

---

### 2. Environment Configuration

```yaml
# environment.yaml — System and dependency settings

python:
  version: ">=3.8"
  
dependencies:
  - torch>=2.0
  - transformers>=4.30
  - datasets>=2.10
  - scipy>=1.10
  - numpy>=1.24
  - matplotlib>=3.7
  
cuda:
  version: ">=11.8"  # Optional
  required: false
  
system:
  min_disk_space_gb: 20
  min_ram_gb: 16
  recommended_ram_gb: 32
```

---

## Configuration Dataclasses

### Python Configuration Objects

```python
# config.py — Dataclass definitions for type-safe configuration

from dataclasses import dataclass, field
from typing import Literal

@dataclass
class DatasetConfig:
    """TriviaQA dataset configuration."""
    name: str = "trivia_qa"
    config: str = "unfiltered"
    split: str = "validation[:1000]"
    cache_dir: str = "~/.cache/huggingface/datasets"

@dataclass
class ModelConfig:
    """Llama-2 model configuration."""
    name: str = "meta-llama/Llama-2-7b-hf"
    cache_dir: str = "~/.cache/huggingface/hub"
    device: Literal["cuda", "cpu"] = "cuda"
    max_input_length: int = 512

@dataclass
class InferenceConfig:
    """Inference settings (frozen model)."""
    batch_size: int = 1
    no_grad: bool = True

@dataclass
class MetricsConfig:
    """Evaluation metric configuration."""
    correlation_method: Literal["spearman", "pearson"] = "spearman"
    significance_threshold: float = 0.05

@dataclass
class GateConfig:
    """Gate validation thresholds."""
    extraction_rate_threshold: float = 0.95
    p_value_threshold: float = 0.05
    q3_population_threshold: float = 0.05

@dataclass
class OutputConfig:
    """Output path configuration."""
    figures_dir: str = "./figures"
    validation_report: str = "./04_validation.md"

@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_file: str = "./experiment.log"

@dataclass
class ExperimentConfig:
    """Top-level experiment configuration."""
    name: str
    hypothesis_id: str
    type: Literal["EXISTENCE", "MECHANISM", "COMPARISON"]
    gate: Literal["MUST_WORK", "SHOULD_WORK"]
    
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    inference: InferenceConfig = field(default_factory=InferenceConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    gates: GateConfig = field(default_factory=GateConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
```

---

## Configuration Loading

### YAML Loader

```python
# config_loader.py

import yaml
from pathlib import Path
from typing import Optional

def load_config(config_path: str = "config.yaml") -> ExperimentConfig:
    """
    Load experiment configuration from YAML file.
    
    Args:
        config_path: Path to config.yaml
    
    Returns:
        Populated ExperimentConfig dataclass
    
    Raises:
        FileNotFoundError: If config file not found
        ValueError: If config validation fails
    """
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    # Parse nested configs
    dataset = DatasetConfig(**config_dict.get("dataset", {}))
    model = ModelConfig(**config_dict.get("model", {}))
    inference = InferenceConfig(**config_dict.get("inference", {}))
    metrics = MetricsConfig(**config_dict.get("metrics", {}))
    gates = GateConfig(**config_dict.get("gates", {}))
    output = OutputConfig(**config_dict.get("output", {}))
    logging = LoggingConfig(**config_dict.get("logging", {}))
    
    # Build top-level config
    experiment = ExperimentConfig(
        name=config_dict["experiment"]["name"],
        hypothesis_id=config_dict["experiment"]["hypothesis_id"],
        type=config_dict["experiment"]["type"],
        gate=config_dict["experiment"]["gate"],
        dataset=dataset,
        model=model,
        inference=inference,
        metrics=metrics,
        gates=gates,
        output=output,
        logging=logging
    )
    
    return experiment

def validate_config(config: ExperimentConfig) -> None:
    """
    Validate configuration for internal consistency.
    
    Raises:
        ValueError: If validation fails
    """
    # Check device availability
    if config.model.device == "cuda":
        import torch
        if not torch.cuda.is_available():
            raise ValueError("CUDA requested but not available. Set device='cpu' or install CUDA.")
    
    # Check output directory exists
    output_dir = Path(config.output.figures_dir)
    if not output_dir.parent.exists():
        raise ValueError(f"Parent directory for figures_dir does not exist: {output_dir.parent}")
```

---

## Hyperparameter Defaults

### Inference Parameters

| Parameter | Default | Rationale |
|-----------|---------|-----------|
| `batch_size` | 1 | Sequential processing for PoC (GPU memory constraints) |
| `max_input_length` | 512 | Balance between context and memory |
| `device` | "cuda" (fallback "cpu") | GPU acceleration if available |

**No sampling parameters** — Using argmax for deterministic predictions.

---

### Metric Thresholds

| Metric | Threshold | Source |
|--------|-----------|--------|
| `extraction_rate` | 0.95 | Phase 2C experiment design |
| `p_value` | 0.05 | Standard statistical significance (α = 0.05) |
| `q3_population` | 0.05 | Phase 2C Assumption A2 validation |
| `correlation_direction` | Negative (ρ < 0) | Expected entropy-correctness relationship |

---

### Dataset Splits

| Split | Size | Purpose |
|-------|------|---------|
| `validation[:1000]` | 1,000 examples | PoC evaluation (LIGHT budget) |

**Rationale:** Full dev set (~11k examples) exceeds PoC scope. 1,000 examples sufficient for correlation significance testing.

---

## Environment Variables

### Optional Overrides

```bash
# .env file (optional)

# HuggingFace cache location
HF_HOME=/custom/cache/path

# CUDA device selection
CUDA_VISIBLE_DEVICES=0

# Logging level override
LOG_LEVEL=DEBUG
```

### Usage in Code

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Override config from environment
cache_dir = os.getenv("HF_HOME", config.model.cache_dir)
log_level = os.getenv("LOG_LEVEL", config.logging.level)
```

---

## Subtask Breakdown

### Subtask C-1: Configuration Schema Design (Epic-4)
**Complexity:** 1/5  
**Description:** Define YAML schema and dataclasses for all configuration sections.

**Deliverables:**
- `config.yaml` template
- `config.py` with dataclass definitions
- Validation logic

---

### Subtask C-2: Config Loader Implementation (Epic-5)
**Complexity:** 1/5  
**Description:** Implement YAML loading and validation.

**Deliverables:**
- `config_loader.py` with `load_config()` and `validate_config()`
- Environment variable override support
- Error handling for missing/invalid config

---

## Configuration Validation Rules

### Required Fields
- `experiment.name`
- `experiment.hypothesis_id`
- `dataset.split`
- `model.name`

### Type Constraints
- `device` ∈ {"cuda", "cpu"}
- `correlation_method` ∈ {"spearman", "pearson"}
- All thresholds: 0 ≤ threshold ≤ 1
- `batch_size` ≥ 1

### Cross-Field Validation
- If `device == "cuda"`, check `torch.cuda.is_available()`
- If `output.figures_dir` set, ensure parent directory exists

---

## Default Configuration File

```yaml
# config.yaml — Production defaults for h-e1

experiment:
  name: "h-e1-entropy-correlation"
  hypothesis_id: "h-e1"
  type: "EXISTENCE"
  gate: "MUST_WORK"
  
dataset:
  name: "trivia_qa"
  config: "unfiltered"
  split: "validation[:1000]"
  
model:
  name: "meta-llama/Llama-2-7b-hf"
  device: "cuda"
  max_input_length: 512
  
inference:
  batch_size: 1
  no_grad: true
  
metrics:
  correlation_method: "spearman"
  significance_threshold: 0.05
  
gates:
  extraction_rate_threshold: 0.95
  p_value_threshold: 0.05
  q3_population_threshold: 0.05
  
output:
  figures_dir: "./figures"
  validation_report: "./04_validation.md"
  
logging:
  level: "INFO"
  log_file: "./experiment.log"
```

---

## Usage Example

```python
# main.py — Using configuration

from config_loader import load_config, validate_config

# Load and validate config
config = load_config("config.yaml")
validate_config(config)

# Use in experiment
dataset = load_triviaqa_subset(split=config.dataset.split)
model, tokenizer = load_llama_model(
    model_name=config.model.name,
    device=config.model.device
)

# Gate validation
gate_pass = (
    extraction_rate > config.gates.extraction_rate_threshold and
    p_value < config.gates.p_value_threshold and
    q3_fraction > config.gates.q3_population_threshold
)
```

---

## External Dependencies

### YAML Parsing
- Library: `pyyaml`
- Function: `yaml.safe_load(file)`

### Environment Variables
- Library: `python-dotenv` (optional)
- Function: `load_dotenv()`

---

**Configuration Status:** Ready for implementation (Phase 4)
