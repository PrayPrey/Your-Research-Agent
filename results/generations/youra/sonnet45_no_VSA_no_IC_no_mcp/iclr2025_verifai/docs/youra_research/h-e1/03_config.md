# Configuration Design: h-e1 Beam Search Infrastructure PoC

**Date:** 2026-08-25  
**Author:** Anonymous  
**Hypothesis:** h-e1 (EXISTENCE)  
**Subtask Budget:** 0 subtasks (minimal config for PoC)

---

## Applied Patterns

**Applied:** Dataclass Configuration Pattern (Archon KB: Python Config Best Practices)  
**Applied:** YAML Serialization Pattern (Archon KB: Experiment Reproducibility)  
**Applied:** Default Values Pattern (Archon KB: Configuration Hierarchies)

**Rationale:** Dataclasses provide type safety and default values. YAML enables easy modification without code changes.

---

## Configuration Schema

### Experiment Configuration

**File:** `config.yaml`

```yaml
# h-e1 Beam Search PoC Configuration

# Dataset Configuration
dataset:
  name: "openai_humaneval"
  split: "test"
  poc_subset_size: 5  # First 5 problems for PoC

# Model Configuration
model:
  name: "meta-llama/CodeLlama-7b-hf"
  device: "auto"  # 'cuda', 'cpu', or 'auto'
  dtype: "float16"  # 'float16' for GPU, 'float32' for CPU

# Beam Search Configuration
beam_search:
  k: 5  # Beam width
  max_new_tokens: 256
  temperature: 1.0
  do_sample: false  # Deterministic beam search

# Custom Scoring Configuration
scoring:
  alpha: 0.7  # Fluency weight
  beta: 0.3   # Validity weight (AST-based)

# Gate Metrics Configuration
gate:
  time_target_seconds: 1800  # 30 minutes
  latency_target_ms: 50      # AST parse latency

# Output Configuration
output:
  figures_dir: "figures"
  results_file: "outputs/results.json"
  log_file: "outputs/poc_log.txt"

# Reproducibility
random_seed: 42
```

---

### Python Dataclass Representation

**File:** `config.py`

```python
from dataclasses import dataclass, field
from typing import Literal
import yaml

@dataclass
class DatasetConfig:
    """Dataset configuration."""
    name: str = "openai_humaneval"
    split: str = "test"
    poc_subset_size: int = 5

@dataclass
class ModelConfig:
    """Model configuration."""
    name: str = "meta-llama/CodeLlama-7b-hf"
    device: Literal["auto", "cuda", "cpu"] = "auto"
    dtype: Literal["float16", "float32"] = "float16"

@dataclass
class BeamSearchConfig:
    """Beam search hyperparameters."""
    k: int = 5  # Beam width
    max_new_tokens: int = 256
    temperature: float = 1.0
    do_sample: bool = False

@dataclass
class ScoringConfig:
    """Custom scoring weights."""
    alpha: float = 0.7  # Fluency weight
    beta: float = 0.3   # Validity weight

@dataclass
class GateConfig:
    """Gate validation thresholds."""
    time_target_seconds: int = 1800  # 30 minutes
    latency_target_ms: int = 50      # milliseconds

@dataclass
class OutputConfig:
    """Output paths configuration."""
    figures_dir: str = "figures"
    results_file: str = "outputs/results.json"
    log_file: str = "outputs/poc_log.txt"

@dataclass
class ExperimentConfig:
    """Complete experiment configuration."""
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    beam_search: BeamSearchConfig = field(default_factory=BeamSearchConfig)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    random_seed: int = 42

    @classmethod
    def from_yaml(cls, path: str) -> 'ExperimentConfig':
        """Load configuration from YAML file."""
        with open(path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        return cls(
            dataset=DatasetConfig(**config_dict.get('dataset', {})),
            model=ModelConfig(**config_dict.get('model', {})),
            beam_search=BeamSearchConfig(**config_dict.get('beam_search', {})),
            scoring=ScoringConfig(**config_dict.get('scoring', {})),
            gate=GateConfig(**config_dict.get('gate', {})),
            output=OutputConfig(**config_dict.get('output', {})),
            random_seed=config_dict.get('random_seed', 42)
        )
    
    def to_yaml(self, path: str) -> None:
        """Save configuration to YAML file."""
        config_dict = {
            'dataset': {
                'name': self.dataset.name,
                'split': self.dataset.split,
                'poc_subset_size': self.dataset.poc_subset_size
            },
            'model': {
                'name': self.model.name,
                'device': self.model.device,
                'dtype': self.model.dtype
            },
            'beam_search': {
                'k': self.beam_search.k,
                'max_new_tokens': self.beam_search.max_new_tokens,
                'temperature': self.beam_search.temperature,
                'do_sample': self.beam_search.do_sample
            },
            'scoring': {
                'alpha': self.scoring.alpha,
                'beta': self.scoring.beta
            },
            'gate': {
                'time_target_seconds': self.gate.time_target_seconds,
                'latency_target_ms': self.gate.latency_target_ms
            },
            'output': {
                'figures_dir': self.output.figures_dir,
                'results_file': self.output.results_file,
                'log_file': self.output.log_file
            },
            'random_seed': self.random_seed
        }
        
        with open(path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
```

---

## Hyperparameter Descriptions

### Dataset Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | `openai_humaneval` | HuggingFace dataset identifier |
| `split` | str | `test` | Dataset split to use |
| `poc_subset_size` | int | `5` | Number of problems for PoC (full=164) |

**Rationale:** Small subset for fast validation, easily scalable to full 164 problems.

---

### Model Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | `meta-llama/CodeLlama-7b-hf` | HuggingFace model identifier |
| `device` | str | `auto` | Device selection: 'auto', 'cuda', or 'cpu' |
| `dtype` | str | `float16` | Precision: 'float16' (GPU) or 'float32' (CPU) |

**Rationale:**
- `float16` halves GPU memory usage (7B params: 14GB → 7GB)
- `auto` device enables seamless CPU fallback

---

### Beam Search Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `k` | int | `5` | Beam width (number of parallel candidates) |
| `max_new_tokens` | int | `256` | Maximum tokens to generate per problem |
| `temperature` | float | `1.0` | Sampling temperature (1.0 = no scaling) |
| `do_sample` | bool | `false` | Deterministic beam search (no sampling) |

**Rationale:**
- k=5 balances diversity and compute cost
- 256 tokens sufficient for HumanEval solutions (avg ~100 tokens)
- Deterministic beam search for reproducibility

**Tuning Guidance:**
- Increase k (10, 20) for higher coverage (slower runtime)
- Decrease max_new_tokens if solutions are shorter

---

### Custom Scoring Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `alpha` | float | `0.7` | Weight for fluency (log-likelihood) |
| `beta` | float | `0.3` | Weight for validity (AST parsing) |

**Rationale:**
- α=0.7 prioritizes fluent code (model confidence)
- β=0.3 adds validity bias without dominating
- Sum to 1.0 for interpretability

**Tuning Guidance:**
- Increase β (0.5) to prioritize syntactic correctness
- Decrease β (0.1) if AST parsing too restrictive

---

### Gate Metrics Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `time_target_seconds` | int | `1800` | Maximum PoC runtime (30 minutes) |
| `latency_target_ms` | int | `50` | Maximum AST parse latency per sample |

**Rationale:**
- 30 min for 5 problems → extrapolates to <4 hours for 164
- 50ms AST latency ensures negligible overhead

**No tuning needed:** Gate thresholds from Phase 2C experiment design.

---

### Output Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `figures_dir` | str | `figures` | Directory for visualization outputs |
| `results_file` | str | `outputs/results.json` | Metrics JSON file path |
| `log_file` | str | `outputs/poc_log.txt` | Execution log file path |

**Rationale:** Separate folders for figures and structured outputs.

---

## Usage

### Loading Configuration

```python
from config import ExperimentConfig

# Load from YAML
config = ExperimentConfig.from_yaml('config.yaml')

# Access nested fields
beam_width = config.beam_search.k  # 5
alpha = config.scoring.alpha        # 0.7
```

### Using in Code

```python
# In run_poc.py
def main():
    config = ExperimentConfig.from_yaml('config.yaml')
    
    # Setup
    device = setup_device(config.model.device)
    model, tokenizer = load_codellama(config.model.name, device, config.model.dtype)
    
    # Data
    dataset = load_humaneval(config.dataset.name)
    problems = extract_poc_subset(dataset, config.dataset.poc_subset_size)
    
    # Beam search
    candidates = run_beam_search(
        model, 
        tokenizer, 
        prompts, 
        k=config.beam_search.k,
        max_new_tokens=config.beam_search.max_new_tokens
    )
    
    # Metrics
    gate_metrics = compute_gate_metrics(
        time_sec, 
        latency_ms,
        time_target=config.gate.time_target_seconds,
        latency_target=config.gate.latency_target_ms
    )
```

---

## Default Configuration Justification

| Parameter | Default | Justification |
|-----------|---------|---------------|
| `k=5` | 5 beams | Phase 2C experiment design specification |
| `α=0.7, β=0.3` | 70/30 split | Prioritize fluency with validity constraint |
| `max_new_tokens=256` | 256 | 2x HumanEval avg solution length (safety margin) |
| `poc_subset_size=5` | 5 problems | Fast PoC validation, scales to 164 |
| `time_target=1800s` | 30 minutes | Phase 2C gate threshold |
| `latency_target=50ms` | 50 milliseconds | Phase 2C gate threshold |

All defaults chosen to match Phase 2C experiment brief specifications.

---

## Environment Variables (None Required)

PoC uses only local files and HuggingFace public models. No API keys or secrets needed.

**Optional:**
- `HF_HOME`: HuggingFace cache directory (default: `~/.cache/huggingface`)

---

## Reproducibility Settings

```python
import torch
import random
import numpy as np

def set_random_seed(seed: int):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

# In run_poc.py
config = ExperimentConfig.from_yaml('config.yaml')
set_random_seed(config.random_seed)
```

**Note:** HuggingFace beam search with `do_sample=False` is deterministic without manual seeding.

---

## Configuration Validation

```python
def validate_config(config: ExperimentConfig) -> list[str]:
    """Validate configuration constraints."""
    errors = []
    
    # Scoring weights must sum to 1.0
    if abs(config.scoring.alpha + config.scoring.beta - 1.0) > 1e-6:
        errors.append(f"Scoring weights must sum to 1.0 (got {config.scoring.alpha + config.scoring.beta})")
    
    # Beam width must be >= 1
    if config.beam_search.k < 1:
        errors.append(f"Beam width must be >= 1 (got {config.beam_search.k})")
    
    # PoC subset must be <= 164 (full HumanEval size)
    if config.dataset.poc_subset_size > 164:
        errors.append(f"PoC subset cannot exceed 164 (got {config.dataset.poc_subset_size})")
    
    return errors
```

---

## Configuration Files Generated

**Locations:**
```
h-e1/
├── code/
│   ├── config.yaml          # User-editable YAML
│   └── config.py            # Dataclass definitions
└── outputs/
    └── config_used.yaml     # Saved copy of config used in run
```

**Workflow:**
1. User edits `config.yaml`
2. `run_poc.py` loads config
3. Config validated
4. Copy saved to `outputs/config_used.yaml` for reproducibility

---

**Document Status:** Ready for Complexity Assessment (Step 6)
