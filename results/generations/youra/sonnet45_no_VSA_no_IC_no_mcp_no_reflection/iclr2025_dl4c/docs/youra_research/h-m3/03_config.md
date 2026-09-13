# Configuration Design Document
## Transfer Learning to Held-Out Tests - h-m3

**Version:** 1.0  
**Date:** 2026-08-28  
**Hypothesis:** h-m3 (MECHANISM)  
**Subtask Budget:** 6

---

## Applied Patterns

**Applied:** Standard DL config structure (data, model, training, evaluation)  
**Applied:** YAML-first configuration with dataclass validation

---

## Configuration Schema

### 1. Experiment Configuration (`config/experiment.yaml`)

```yaml
experiment:
  name: "h-m3-pattern-transfer"
  hypothesis_id: "h-m3"
  version: "1.0"
  random_seed: 42
  
data:
  source: "codeforces"
  n_problems: 50
  rating_range: [1200, 1800]
  min_solve_count: 1000
  min_test_cases: 15
  test_split_ratio: 0.5  # 50% revealed / 50% held-out
  cache_dir: "data/"
  baseline_code_temperature: 0.7
  
agent:
  model: "gpt-4-turbo-2024-04-09"
  temperature: 0.7
  top_p: 0.95
  max_tokens: 2048
  n_iterations: 10
  api_key_env: "OPENAI_API_KEY"
  
baselines:
  random:
    n_mutations_per_problem: 20
    mutation_types: ["rename_var", "change_operator", "modify_constant"]
  revealed_only:
    model: "gpt-4-turbo-2024-04-09"
    temperature: 0.7
    n_iterations: 10
    
analysis:
  permutation_test_samples: 1000
  significance_level: 0.05
  early_stopping:
    enabled: true
    min_problems: 30
    p_threshold: 0.2  # Stop if p > 0.2 after 30 problems
    
output:
  results_dir: "results/"
  plots_dir: "results/plots/"
  checkpoint_file: "results/checkpoint.json"
  validation_report: "04_validation.md"
```

### 2. Data Configuration Dataclass

```python
from dataclasses import dataclass, field

@dataclass
class DataConfig:
    source: str = "codeforces"
    n_problems: int = 50
    rating_range: tuple[int, int] = (1200, 1800)
    min_solve_count: int = 1000
    min_test_cases: int = 15
    test_split_ratio: float = 0.5
    cache_dir: str = "data/"
    baseline_code_temperature: float = 0.7
    
    def __post_init__(self):
        assert 0 < self.test_split_ratio < 1, "test_split_ratio must be in (0, 1)"
        assert self.n_problems > 0, "n_problems must be positive"
        assert self.min_test_cases >= 4, "Need at least 4 test cases for 50% split"
```

### 3. Agent Configuration Dataclass

```python
@dataclass
class AgentConfig:
    model: str = "gpt-4-turbo-2024-04-09"
    temperature: float = 0.7
    top_p: float = 0.95
    max_tokens: int = 2048
    n_iterations: int = 10
    api_key_env: str = "OPENAI_API_KEY"
    
    def __post_init__(self):
        assert 0 <= self.temperature <= 2, "temperature must be in [0, 2]"
        assert 0 < self.top_p <= 1, "top_p must be in (0, 1]"
        assert self.n_iterations > 0, "n_iterations must be positive"
```

### 4. Baseline Configuration Dataclass

```python
@dataclass
class RandomBaselineConfig:
    n_mutations_per_problem: int = 20
    mutation_types: list[str] = field(default_factory=lambda: [
        "rename_var", "change_operator", "modify_constant"
    ])

@dataclass
class RevealedOnlyBaselineConfig:
    model: str = "gpt-4-turbo-2024-04-09"
    temperature: float = 0.7
    n_iterations: int = 10
```

### 5. Analysis Configuration Dataclass

```python
@dataclass
class AnalysisConfig:
    permutation_test_samples: int = 1000
    significance_level: float = 0.05
    early_stopping_enabled: bool = True
    early_stopping_min_problems: int = 30
    early_stopping_p_threshold: float = 0.2
    
    def __post_init__(self):
        assert 0 < self.significance_level < 1, "significance_level in (0, 1)"
        assert self.permutation_test_samples >= 100, "Need >= 100 samples"
```

### 6. Master Configuration Dataclass

```python
@dataclass
class ExperimentConfig:
    experiment_name: str
    hypothesis_id: str
    version: str
    random_seed: int
    data: DataConfig
    agent: AgentConfig
    baselines: dict  # {random: RandomBaselineConfig, revealed_only: RevealedOnlyBaselineConfig}
    analysis: AnalysisConfig
    output_results_dir: str
    output_plots_dir: str
    output_checkpoint_file: str
    output_validation_report: str
    
    @classmethod
    def from_yaml(cls, path: str) -> "ExperimentConfig":
        """Load configuration from YAML file."""
        import yaml
        with open(path) as f:
            config_dict = yaml.safe_load(f)
        
        # Parse nested configs
        data = DataConfig(**config_dict["data"])
        agent = AgentConfig(**config_dict["agent"])
        baselines = {
            "random": RandomBaselineConfig(**config_dict["baselines"]["random"]),
            "revealed_only": RevealedOnlyBaselineConfig(**config_dict["baselines"]["revealed_only"])
        }
        analysis = AnalysisConfig(
            permutation_test_samples=config_dict["analysis"]["permutation_test_samples"],
            significance_level=config_dict["analysis"]["significance_level"],
            early_stopping_enabled=config_dict["analysis"]["early_stopping"]["enabled"],
            early_stopping_min_problems=config_dict["analysis"]["early_stopping"]["min_problems"],
            early_stopping_p_threshold=config_dict["analysis"]["early_stopping"]["p_threshold"]
        )
        
        return cls(
            experiment_name=config_dict["experiment"]["name"],
            hypothesis_id=config_dict["experiment"]["hypothesis_id"],
            version=config_dict["experiment"]["version"],
            random_seed=config_dict["experiment"]["random_seed"],
            data=data,
            agent=agent,
            baselines=baselines,
            analysis=analysis,
            output_results_dir=config_dict["output"]["results_dir"],
            output_plots_dir=config_dict["output"]["plots_dir"],
            output_checkpoint_file=config_dict["output"]["checkpoint_file"],
            output_validation_report=config_dict["output"]["validation_report"]
        )
```

---

## Hyperparameter Defaults

### Model Hyperparameters
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `temperature` | 0.7 | Balance creativity vs determinism for code generation |
| `top_p` | 0.95 | Standard nucleus sampling |
| `max_tokens` | 2048 | Sufficient for code fixes (<500 lines typical) |

### Data Hyperparameters
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `n_problems` | 50 | Per Phase 2C power analysis |
| `test_split_ratio` | 0.5 | 50% revealed / 50% held-out per hypothesis |
| `rating_range` | [1200, 1800] | Intermediate difficulty, consistent with h-m1/h-m2 |
| `min_solve_count` | 1000 | High-quality test suites |
| `min_test_cases` | 15 | Minimum for meaningful 50% split |

### Baseline Hyperparameters
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `n_mutations_per_problem` | 20 | 2× agent iterations for null hypothesis strength |
| `mutation_types` | 3 types | Cover common code transformations |

### Analysis Hyperparameters
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `permutation_test_samples` | 1000 | Standard for p < 0.05 precision |
| `significance_level` | 0.05 | Standard alpha |
| `early_stopping_p_threshold` | 0.2 | Conservative stopping (only if clearly failing) |

---

## Environment Variables

```bash
# Required
export OPENAI_API_KEY="sk-..."

# Optional (defaults work for most cases)
export H_M3_CACHE_DIR="data/"
export H_M3_RESULTS_DIR="results/"
export H_M3_RANDOM_SEED=42
```

---

## Configuration Loading

### Usage in Code

```python
# Load configuration
config = ExperimentConfig.from_yaml("config/experiment.yaml")

# Set random seed
random.seed(config.random_seed)
np.random.seed(config.random_seed)

# Initialize components
agent = PatternLearningAgent(
    memory=PatternMemory(),
    model=config.agent.model,
    temperature=config.agent.temperature,
    api_key=os.getenv(config.agent.api_key_env)
)

# Access nested configs
print(f"Using {config.data.n_problems} problems")
print(f"Test split: {config.data.test_split_ratio * 100}% revealed")
```

---

## Subtask Breakdown (6 Total)

### Subtask C1: Environment Setup (E7)
**Description:** Create folder structure, install dependencies  
**Deliverable:** `requirements.txt`, folder structure created  
**Estimated Effort:** LOW

### Subtask C2: Data Config Implementation (E1)
**Description:** Implement DataConfig dataclass with validation  
**Deliverable:** `code/config/data_config.py`  
**Estimated Effort:** LOW

### Subtask C3: Agent Config Implementation (E1)
**Description:** Implement AgentConfig dataclass  
**Deliverable:** `code/config/agent_config.py`  
**Estimated Effort:** LOW

### Subtask C4: Baseline Config Implementation (E4)
**Description:** Implement baseline config dataclasses  
**Deliverable:** `code/config/baseline_config.py`  
**Estimated Effort:** LOW

### Subtask C5: Analysis Config Implementation (E6)
**Description:** Implement AnalysisConfig with early stopping params  
**Deliverable:** `code/config/analysis_config.py`  
**Estimated Effort:** LOW

### Subtask C6: Master Config & YAML Loader (E1)
**Description:** Implement ExperimentConfig.from_yaml() and experiment.yaml  
**Deliverable:** `code/config/experiment_config.py`, `config/experiment.yaml`  
**Estimated Effort:** MEDIUM

---

## Configuration Validation

### Validation Rules

```python
def validate_config(config: ExperimentConfig) -> list[str]:
    """Validate configuration, return list of errors."""
    errors = []
    
    # Data validation
    if config.data.n_problems < config.analysis.early_stopping_min_problems:
        errors.append(f"n_problems ({config.data.n_problems}) < early_stopping_min_problems")
    
    # Test split validation
    if config.data.test_split_ratio != 0.5:
        errors.append(f"test_split_ratio must be 0.5 for this hypothesis (not {config.data.test_split_ratio})")
    
    # Model validation
    if config.agent.model != config.baselines["revealed_only"].model:
        errors.append("Agent and revealed-only baseline must use same model")
    
    # Analysis validation
    if config.analysis.permutation_test_samples < 100:
        errors.append("permutation_test_samples must be >= 100 for valid p-value")
    
    return errors
```

---

## Checkpointing Configuration

### Checkpoint Schema

```yaml
checkpoint:
  version: "1.0"
  experiment_id: "h-m3-pattern-transfer"
  timestamp: "2026-08-28T10:30:00Z"
  
  progress:
    phase: "agent_execution"  # data_prep | agent_execution | baselines | analysis
    problems_completed: 35
    total_problems: 50
    
  data:
    problems_cached: true
    test_splits_cached: true
    baseline_codes_cached: true
    
  results:
    agent_results_path: "results/agent_results.json"
    baseline_results_path: "results/baseline_results.json"
    
  early_stopping:
    checked_at_problem: 30
    p_value_at_30: 0.15
    decision: "continue"  # continue | stop_success | stop_failure
```

### Checkpoint Dataclass

```python
@dataclass
class Checkpoint:
    version: str
    experiment_id: str
    timestamp: str
    phase: str  # data_prep | agent_execution | baselines | analysis
    problems_completed: int
    total_problems: int
    data_cached: dict  # {problems, test_splits, baseline_codes: bool}
    results_paths: dict  # {agent_results, baseline_results: str}
    early_stopping: dict  # {checked_at_problem, p_value_at_30, decision: str}
    
    def save(self, path: str) -> None:
        """Save checkpoint to YAML."""
        
    @classmethod
    def load(cls, path: str) -> "Checkpoint | None":
        """Load checkpoint if exists, else None."""
```

---

## Configuration Files Structure

```
config/
├── experiment.yaml           # Main configuration (user-editable)
├── defaults.yaml             # Default values (DO NOT EDIT)
└── README.md                 # Configuration documentation

code/config/
├── __init__.py
├── data_config.py            # DataConfig dataclass
├── agent_config.py           # AgentConfig dataclass
├── baseline_config.py        # Baseline config dataclasses
├── analysis_config.py        # AnalysisConfig dataclass
├── experiment_config.py      # Master ExperimentConfig + loader
└── checkpoint.py             # Checkpoint dataclass
```

---

## Dependencies

### Python Packages (`requirements.txt`)

```txt
# Core dependencies
openai>=1.0.0
pyyaml>=6.0
scipy>=1.11.0
matplotlib>=3.7.0
numpy>=1.24.0
pandas>=2.0.0
requests>=2.31.0

# Dev dependencies (optional)
pytest>=7.4.0
black>=23.0.0
mypy>=1.5.0
```

---

## Next Steps

1. **Step 6:** Overall complexity assessment
2. **Step 7:** Verify all documents (PRD, Architecture, Logic, Config)
3. **Step 9:** Generate 03_tasks.yaml

---

**Document Status:** Configuration Design Complete  
**Subtasks Allocated:** 6 (within budget)
