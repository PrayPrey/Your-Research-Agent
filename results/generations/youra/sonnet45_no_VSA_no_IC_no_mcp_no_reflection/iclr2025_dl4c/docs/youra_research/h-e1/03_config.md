# Configuration Design: Fix-Impact-Ratio Measurement System

**Hypothesis:** h-e1  
**Type:** EXISTENCE (LIGHT tier)  
**Generated:** 2026-08-28  
**Phase:** 3 — Implementation Planning

---

## Codebase Analysis (Serena)

**MCP Status:** Serena MCP not available  
**Analysis Mode:** Green-field (no existing config to analyze)

**Applied:** Light-tier Config Pattern (Archon KB) — minimal hyperparameters, focused on reproducibility

---

## Configuration Schemas

### 1. Dataset Configuration

```yaml
# config/dataset_config.yaml

dataset:
  source: "codeforces"  # or "codecontests"
  
  # Codeforces API settings
  codeforces:
    api_url: "https://codeforces.com/api"
    timeout_seconds: 30
  
  # CodeContests fallback
  codecontests:
    dataset_url: "https://huggingface.co/datasets/deepmind/code_contests"
    cache_dir: "data/codecontests_cache"
  
  # Filtering criteria
  filters:
    min_rating: 1200
    max_rating: 1800
    min_solve_count: 1000
    min_test_cases: 15
  
  # Dataset size
  target_problem_count: 200
  validation_subset_size: 50  # Phase 1 validation
  
  # Caching
  cache_path: "data/codeforces_curated/problems.json"
  force_refetch: false
```

**Dataclass Representation:**
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatasetConfig:
    source: str = "codeforces"
    
    codeforces_api_url: str = "https://codeforces.com/api"
    codeforces_timeout: int = 30
    
    codecontests_url: str = "https://huggingface.co/datasets/deepmind/code_contests"
    codecontests_cache: str = "data/codecontests_cache"
    
    min_rating: int = 1200
    max_rating: int = 1800
    min_solve_count: int = 1000
    min_test_cases: int = 15
    
    target_problem_count: int = 200
    validation_subset_size: int = 50
    
    cache_path: str = "data/codeforces_curated/problems.json"
    force_refetch: bool = False
```

---

### 2. Experiment Configuration

```yaml
# config/experiment_config.yaml

experiment:
  # General settings
  random_seed: 42
  max_iterations_per_problem: 10
  
  # Code execution
  execution:
    timeout_per_test: 10  # seconds
    use_docker: false  # true = Docker sandbox, false = subprocess
    docker_image: "python:3.9-slim"
    resource_limits:
      memory_mb: 512
      cpu_cores: 1
  
  # Baselines
  baselines:
    random_sampling:
      temperature: 0.7
      num_samples: 10
    
    sequential:
      fix_prompt_template: "Fix the code to pass test {i}: input={x}, expected={y}, got={z}"
    
    zeroshot:
      prompt_template: "Write Python code to solve: {problem_statement}"
  
  # Agents
  agents:
    gpt4_baseline:
      model: "gpt-4-turbo"
      temperature: 0.2
      max_tokens: 2048
      prompt_template: "Fix the code to pass all test cases.\nProblem: {statement}\nCode: {code}\nFailures: {failures}"
    
    gpt4_memory:
      model: "gpt-4-turbo"
      temperature: 0.2
      max_tokens: 2048
      memory_max_entries: 100
      prompt_template: "Review past errors: {memory}\n\nFix the code to pass all test cases.\nProblem: {statement}\nCode: {code}\nFailures: {failures}"
    
    gpt4_explicit:
      model: "gpt-4-turbo"
      temperature: 0.2
      max_tokens: 2048
      prompt_template: |
        Step 1: Group failing tests by root cause.
        Step 2: Prioritize the highest-impact fix.
        Step 3: Apply the fix.
        
        Problem: {statement}
        Code: {code}
        Failing tests: {failures}
  
  # Results storage
  results:
    output_dir: "results/h-e1"
    save_intermediate: true  # Save after each iteration
    cache_responses: true  # Cache GPT-4 responses for reproducibility
```

**Dataclass Representation:**
```python
@dataclass
class ExecutionConfig:
    timeout_per_test: int = 10
    use_docker: bool = False
    docker_image: str = "python:3.9-slim"
    memory_mb: int = 512
    cpu_cores: int = 1

@dataclass
class BaselineConfig:
    random_sampling_temp: float = 0.7
    random_sampling_n: int = 10
    sequential_prompt: str = "Fix the code to pass test {i}"
    zeroshot_prompt: str = "Write Python code to solve: {problem_statement}"

@dataclass
class AgentConfig:
    model: str = "gpt-4-turbo"
    temperature: float = 0.2
    max_tokens: int = 2048
    prompt_template: str = ""

@dataclass
class ExperimentConfig:
    random_seed: int = 42
    max_iterations: int = 10
    
    execution: ExecutionConfig = ExecutionConfig()
    baselines: BaselineConfig = BaselineConfig()
    
    gpt4_baseline: AgentConfig = AgentConfig()
    gpt4_memory: AgentConfig = AgentConfig()
    gpt4_explicit: AgentConfig = AgentConfig()
    
    results_dir: str = "results/h-e1"
    save_intermediate: bool = True
    cache_responses: bool = True
```

---

### 3. API Keys Configuration

```yaml
# config/api_keys.yaml (git-ignored)

openai:
  api_key: "sk-..."
  organization_id: null  # optional

# Note: Add to .gitignore
```

**Dataclass Representation:**
```python
@dataclass
class APIKeysConfig:
    openai_api_key: str
    openai_org_id: Optional[str] = None
    
    @classmethod
    def from_env(cls):
        """Load from environment variables."""
        import os
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_org_id=os.getenv("OPENAI_ORG_ID")
        )
```

---

### 4. Statistical Analysis Configuration

```yaml
# config/analysis_config.yaml

analysis:
  # Hypothesis testing
  hypothesis_test:
    test_type: "mann_whitney_u"
    alternative: "greater"  # one-tailed: agent > baseline
    alpha: 0.05  # significance threshold
  
  # Effect size
  effect_size:
    method: "cohens_d"
    min_acceptable: 0.5  # medium effect
  
  # Correlation
  correlation:
    method: "pearson"
    min_expected: 0.5  # fix-impact-ratio vs pass_rate
  
  # Confidence intervals
  confidence_level: 0.95
  bootstrap_iterations: 1000
```

**Dataclass Representation:**
```python
@dataclass
class AnalysisConfig:
    test_type: str = "mann_whitney_u"
    alternative: str = "greater"
    alpha: float = 0.05
    
    effect_size_method: str = "cohens_d"
    min_effect_size: float = 0.5
    
    correlation_method: str = "pearson"
    min_correlation: float = 0.5
    
    confidence_level: float = 0.95
    bootstrap_iterations: int = 1000
```

---

### 5. Validation Report Configuration

```yaml
# config/report_config.yaml

report:
  output_file: "results/h-e1/04_validation.md"
  
  # Visualization settings
  visualizations:
    figures_dir: "results/h-e1/figures"
    dpi: 300
    format: "png"
    
    # Plot styles
    distribution_plot:
      bins: 20
      alpha: 0.7
      colors: ["#1f77b4", "#ff7f0e", "#2ca02c"]
    
    scatter_plot:
      marker_size: 50
      alpha: 0.6
      regression_line: true
    
    convergence_plot:
      line_width: 2
      marker_size: 8
  
  # Gate criteria (MUST_WORK)
  gate_criteria:
    min_agent_ratio: 2.0
    baseline_ratio_range: [0.8, 1.2]
    max_p_value: 0.05
    min_effect_size: 0.5
```

**Dataclass Representation:**
```python
@dataclass
class VisualizationConfig:
    figures_dir: str = "results/h-e1/figures"
    dpi: int = 300
    format: str = "png"
    
    dist_bins: int = 20
    dist_alpha: float = 0.7
    dist_colors: List[str] = None
    
    scatter_marker_size: int = 50
    scatter_alpha: float = 0.6
    scatter_regression: bool = True
    
    conv_line_width: int = 2
    conv_marker_size: int = 8

@dataclass
class GateCriteria:
    min_agent_ratio: float = 2.0
    baseline_ratio_min: float = 0.8
    baseline_ratio_max: float = 1.2
    max_p_value: float = 0.05
    min_effect_size: float = 0.5

@dataclass
class ReportConfig:
    output_file: str = "results/h-e1/04_validation.md"
    viz: VisualizationConfig = VisualizationConfig()
    gate: GateCriteria = GateCriteria()
```

---

## Hyperparameter Rationale

### Dataset Filtering
- **min_rating=1200, max_rating=1800**: Intermediate difficulty ensures LLM-solvable but non-trivial problems
- **min_solve_count=1000**: Community validation ensures quality test suites
- **min_test_cases=15**: Hypothesis constraint for multi-test-case analysis

### Experiment Execution
- **max_iterations=10**: Balance between debugging depth and API cost
- **timeout_per_test=10s**: Prevent infinite loops, typical competitive programming timeout

### GPT-4 Settings
- **temperature=0.2**: Low variance for reproducibility (not 0.0 to allow minor variation)
- **max_tokens=2048**: Sufficient for code generation + explanation
- **model=gpt-4-turbo**: Latest stable GPT-4 variant (not preview, for reliability)

### Statistical Analysis
- **alpha=0.05**: Standard significance threshold in ML research
- **min_effect_size=0.5**: Cohen's d medium effect (0.2=small, 0.5=medium, 0.8=large)
- **bootstrap_iterations=1000**: Standard for confidence interval estimation

---

## Configuration Loading Utilities

```python
import yaml
from pathlib import Path
from typing import TypeVar, Type

T = TypeVar('T')

def load_config(config_path: str, config_class: Type[T]) -> T:
    """
    Load YAML config and instantiate dataclass.
    
    Args:
        config_path: Path to YAML file
        config_class: Dataclass type to instantiate
    
    Returns:
        Instantiated config object
    """
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    # Flatten nested dicts for dataclass initialization
    flattened = _flatten_dict(config_dict)
    return config_class(**flattened)

def _flatten_dict(d: dict, parent_key: str = '', sep: str = '_') -> dict:
    """Flatten nested dict for dataclass instantiation."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
```

---

## Environment Variables

```bash
# .env (git-ignored)

# OpenAI API
OPENAI_API_KEY=sk-...
OPENAI_ORG_ID=org-...

# Dataset paths
CODEFORCES_CACHE_PATH=data/codeforces_curated/problems.json
RESULTS_DIR=results/h-e1

# Experiment settings
RANDOM_SEED=42
MAX_ITERATIONS=10
USE_DOCKER=false
```

---

## Configuration Validation

```python
def validate_config(config: ExperimentConfig) -> None:
    """
    Validate config values before experiment execution.
    
    Raises:
        ValueError: If config is invalid
    """
    if config.random_seed < 0:
        raise ValueError("random_seed must be non-negative")
    
    if config.max_iterations < 1 or config.max_iterations > 20:
        raise ValueError("max_iterations must be in [1, 20]")
    
    if not (0.0 <= config.gpt4_baseline.temperature <= 1.0):
        raise ValueError("temperature must be in [0.0, 1.0]")
    
    if config.execution.timeout_per_test < 1:
        raise ValueError("timeout_per_test must be ≥ 1 second")
    
    # Validate API key
    if not config.api_keys.openai_api_key.startswith("sk-"):
        raise ValueError("Invalid OpenAI API key format")
```

---

## Applied Patterns Summary

| Pattern | Source | Application |
|---------|--------|-------------|
| Reproducibility Pattern | Archon KB | Fixed random seeds, cached responses |
| Layered Config Pattern | Archon KB | Separate files for dataset/experiment/API/analysis |
| Dataclass Config Pattern | Archon KB | Type-safe config with validation |
| Environment Variable Pattern | Archon KB | Secrets in .env, not YAML |

---

**End of Configuration Design Document**
