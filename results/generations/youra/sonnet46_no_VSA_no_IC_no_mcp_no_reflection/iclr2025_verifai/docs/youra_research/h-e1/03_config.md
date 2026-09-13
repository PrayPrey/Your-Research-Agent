---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
tier: LIGHT
generated: 2026-08-31
author: yoon303@ust.ac.kr
---

Applied: standard dataclass config pattern

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

# Config: h-e1 — Multi-Verifier Activation Measurement

---

### Subtask C-E2-1: ExperimentConfig Dataclass
**Parent Epic:** E2

**Schema:**
```python
from dataclasses import dataclass, field

@dataclass
class GenerationConfig:
    model: str = "gpt-4o-mini"
    temperature: float = 0.2
    max_tokens: int = 512

@dataclass
class VerifierTimeouts:
    execution_timeout: float = 3.0
    static_timeout: float = 10.0
    type_timeout: float = 10.0
    smt_timeout: float = 10.0

@dataclass
class SmtPilotConfig:
    n_problems: int = 20
    seed: int = 1
    gate_threshold: float = 0.30

@dataclass
class PathsConfig:
    results_dir: str = "results"
    figures_dir: str = "figures"
    completions_checkpoint: str = "results/completions.jsonl"
    smt_pilot_results: str = "results/smt_pilot_results.json"
    verifier_results: str = "results/verifier_results.jsonl"
    activation_stats: str = "results/activation_stats.json"

@dataclass
class ExperimentConfig:
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    timeouts: VerifierTimeouts = field(default_factory=VerifierTimeouts)
    smt_pilot: SmtPilotConfig = field(default_factory=SmtPilotConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    activation_threshold: float = 0.10  # gate: each category must meet this
    random_seed: int = 1
```

**Defaults:**

| Field | Default |
|-------|---------|
| generation.model | "gpt-4o-mini" |
| generation.temperature | 0.2 |
| generation.max_tokens | 512 |
| timeouts.execution_timeout | 3.0 |
| timeouts.static_timeout | 10.0 |
| timeouts.type_timeout | 10.0 |
| timeouts.smt_timeout | 10.0 |
| smt_pilot.n_problems | 20 |
| smt_pilot.seed | 1 |
| smt_pilot.gate_threshold | 0.30 |
| paths.results_dir | "results" |
| paths.figures_dir | "figures" |
| paths.completions_checkpoint | "results/completions.jsonl" |
| activation_threshold | 0.10 |
| random_seed | 1 |

---

### Subtask C-E5-1: YAML Config File Schema
**Parent Epic:** E5

**Schema** (`config/experiment.yaml`):
```yaml
# h-e1 experiment configuration
# All fields mirror ExperimentConfig dataclass

generation:
  model: "gpt-4o-mini"
  temperature: 0.2        # valid range: 0.0 - 1.0
  max_tokens: 512         # must be > 0

timeouts:
  execution_timeout: 3.0  # seconds, must be > 0
  static_timeout: 10.0    # seconds, must be > 0
  type_timeout: 10.0      # seconds, must be > 0
  smt_timeout: 10.0       # seconds, must be > 0

smt_pilot:
  n_problems: 20          # integer, must be > 0
  seed: 1                 # reproducibility seed
  gate_threshold: 0.30    # valid range: 0.0 - 1.0; gate for enabling full SMT run

paths:
  results_dir: "results"
  figures_dir: "figures"
  completions_checkpoint: "results/completions.jsonl"
  smt_pilot_results: "results/smt_pilot_results.json"
  verifier_results: "results/verifier_results.jsonl"
  activation_stats: "results/activation_stats.json"

activation_threshold: 0.10  # valid range: 0.0 - 1.0; gate for each verifier category
random_seed: 1
```

**Loading snippet** (for `run_experiment.py`):
```python
import yaml
from dataclasses import fields

def load_config(path: str = "config/experiment.yaml") -> ExperimentConfig:
    with open(path) as f:
        data = yaml.safe_load(f)
    cfg = ExperimentConfig()
    if "generation" in data:
        cfg.generation = GenerationConfig(**data["generation"])
    if "timeouts" in data:
        cfg.timeouts = VerifierTimeouts(**data["timeouts"])
    if "smt_pilot" in data:
        cfg.smt_pilot = SmtPilotConfig(**data["smt_pilot"])
    if "paths" in data:
        cfg.paths = PathsConfig(**data["paths"])
    if "activation_threshold" in data:
        cfg.activation_threshold = data["activation_threshold"]
    if "random_seed" in data:
        cfg.random_seed = data["random_seed"]
    return cfg
```

---

### Subtask C-E5-2: Requirements.txt
**Parent Epic:** E5

**File** (`requirements.txt`):
```
openai>=1.0.0
datasets>=2.14.0
human-eval>=1.0
mypy>=1.0.0
pyright>=1.1.300
z3-solver>=4.12.0
matplotlib>=3.7.0
pandas>=2.0.0
numpy>=1.24.0
tqdm>=4.65.0
pyyaml>=6.0
```
