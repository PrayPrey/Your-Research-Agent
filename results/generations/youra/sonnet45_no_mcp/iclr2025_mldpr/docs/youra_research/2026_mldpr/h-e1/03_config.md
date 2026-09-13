# Configuration Design Document
# Hypothesis: H-E1 - Documentation Copilot Existence Test

**Version:** 1.0  
**Date:** 2026-04-15  
**Author:** Configuration Agent (TEST mode)  
**Hypothesis ID:** h-e1  
**Hypothesis Type:** EXISTENCE (FOUNDATION)  
**Phase:** 3 - Implementation Planning  
**Budget:** 3 subtasks (from Epic E-5)

---

## 1. Configuration Overview

### 1.1 Purpose
Define all configuration schemas, hyperparameters, and settings for the documentation copilot pilot deployment experiment.

### 1.2 Hypothesis Context
- **Type:** EXISTENCE (PoC validation)
- **Base Hypothesis:** None (foundation hypothesis - no inherited config)
- **Tier:** LIGHT (minimal infrastructure, single model)

---

## 2. Applied Patterns from Archon KB

**Applied:** Dataclass-Based Configuration (Pattern ID: DBC-001)
- Core: Python dataclasses for type-safe config management
- Rationale: Type hints, validation, easy serialization to YAML
- Source: Archon Knowledge Base - "Python configuration patterns"

**Applied:** Experiment Tracking Configuration (Pattern ID: ETC-002)
- Core: Deployment settings, user assignment, survey collection
- Rationale: Systematic pilot experiment management
- Source: Archon Knowledge Base - "User study configurations"

---

## 3. Core Configuration Schemas

### 3.1 Model Configuration

**File:** `src/config.py`

```python
from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class ModelConfig:
    """LLM model configuration for suggestion generation."""
    
    # Model selection
    model_name: str = "meta-llama/Llama-3-8B-Instruct"
    use_api: bool = False  # False = local inference, True = API call
    api_provider: Optional[str] = None  # 'openai' | 'anthropic' | None
    api_key: Optional[str] = None
    
    # Generation parameters
    temperature: float = 0.7  # Balance creativity and consistency
    max_length: int = 500  # Max tokens per suggestion
    top_p: float = 0.95  # Nucleus sampling
    do_sample: bool = True  # Enable sampling (vs. greedy)
    
    # Hardware configuration
    device: int = 0  # GPU device ID (0 for first GPU, -1 for CPU)
    torch_dtype: str = "float16"  # "float16" | "float32" | "bfloat16"
    
    # Performance settings
    batch_size: int = 1  # Single suggestion at a time for low latency
    num_workers: int = 4  # DataLoader workers (for corpus loading)
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.use_api and not self.api_provider:
            raise ValueError("api_provider required when use_api=True")
        if self.temperature < 0 or self.temperature > 2.0:
            raise ValueError("temperature must be in [0, 2.0]")
        if self.max_length < 50 or self.max_length > 2048:
            raise ValueError("max_length must be in [50, 2048]")
```

---

### 3.2 Corpus Configuration

**File:** `src/config.py`

```python
@dataclass
class CorpusConfig:
    """Configuration for example corpus management."""
    
    # Corpus paths
    corpus_dir: str = "data/corpus"
    vision_dir: str = "data/corpus/vision"
    nlp_dir: str = "data/corpus/nlp"
    tabular_dir: str = "data/corpus/tabular"
    
    # Corpus requirements
    total_examples: int = 500  # Total corpus size
    vision_count: int = 200  # Vision dataset cards
    nlp_count: int = 200  # NLP dataset cards
    tabular_count: int = 100  # Tabular dataset cards
    
    # Quality filters
    min_completeness: float = 0.85  # Min completeness score (85%)
    required_sections: List[str] = field(default_factory=lambda: [
        "Dataset Description",
        "Data Collection",
        "Uses and Limitations"
    ])
    
    # Example selection
    examples_per_prompt: int = 3  # 3-shot prompting
    max_example_length: int = 300  # Truncate examples for context length
```

---

### 3.3 Deployment Configuration

**File:** `src/config.py`

```python
@dataclass
class DeploymentConfig:
    """Pilot deployment experiment configuration."""
    
    # Experiment parameters
    pilot_duration_days: int = 14  # 2-week deployment
    target_users: int = 50  # Minimum pilot users
    max_users: int = 100  # Maximum pilot users
    
    # User assignment
    treatment_ratio: float = 0.5  # 50% treatment, 50% control
    randomization_seed: int = 42  # For reproducible assignment
    
    # Deployment settings
    platform: str = "huggingface"
    integration_url: str = "https://huggingface.co/datasets/upload"
    
    # Session management
    max_suggestions_per_session: int = 30  # Limit per documentation session
    suggestion_timeout_seconds: int = 5  # Max time for suggestion generation
    
    # Survey settings
    collect_survey: bool = True
    survey_questions: List[str] = field(default_factory=lambda: [
        "How helpful were the AI suggestions? (1-5)",
        "Did the suggestions save you time? (Yes/No)",
        "Would you use this feature again? (Yes/No)"
    ])
```

---

### 3.4 Tracking Configuration

**File:** `src/config.py`

```python
@dataclass
class TrackingConfig:
    """User interaction tracking configuration."""
    
    # Logging paths
    log_dir: str = "data/logs/interactions"
    backup_dir: str = "data/logs/backups"
    
    # Logging settings
    log_format: str = "json"  # 'json' | 'csv'
    log_level: str = "INFO"  # Python logging level
    
    # Backup schedule
    backup_interval_hours: int = 24  # Daily backups
    
    # Metrics to track
    track_timestamps: bool = True
    track_time_to_decision: bool = True
    track_dataset_metadata: bool = True
    track_user_experience: bool = True  # Self-reported experience level
```

---

### 3.5 Evaluation Configuration

**File:** `src/config.py`

```python
@dataclass
class EvaluationConfig:
    """PoC evaluation metrics configuration."""
    
    # Primary success criteria
    target_acceptance_rate: float = 70.0  # >=70% median acceptance
    threshold_acceptance_rate: float = 40.0  # <40% = mechanism failure
    
    # Secondary success criteria
    target_helpfulness: float = 3.5  # >=3.5/5.0 average rating
    
    # Statistical analysis
    confidence_level: float = 0.95  # 95% confidence intervals
    min_sample_size: int = 50  # Minimum users for valid analysis
    
    # Stratification factors
    stratify_by_dataset_type: bool = True
    stratify_by_user_experience: bool = True
    
    # Metrics to calculate
    metrics: List[str] = field(default_factory=lambda: [
        "acceptance_rate",
        "acceptance_rate_by_type",
        "helpfulness_rating",
        "time_to_decision",
        "session_completion_rate"
    ])
```

---

## 4. Master Configuration

**File:** `src/config.py`

```python
@dataclass
class Config:
    """Master configuration for H-E1 experiment."""
    
    model: ModelConfig = field(default_factory=ModelConfig)
    corpus: CorpusConfig = field(default_factory=CorpusConfig)
    deployment: DeploymentConfig = field(default_factory=DeploymentConfig)
    tracking: TrackingConfig = field(default_factory=TrackingConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    
    # Experiment metadata
    hypothesis_id: str = "h-e1"
    experiment_name: str = "documentation_copilot_existence"
    random_seed: int = 42
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'Config':
        """Load configuration from YAML file."""
        import yaml
        with open(yaml_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        return cls(**config_dict)
    
    def to_yaml(self, yaml_path: str) -> None:
        """Save configuration to YAML file."""
        import yaml
        from dataclasses import asdict
        with open(yaml_path, 'w') as f:
            yaml.dump(asdict(self), f, default_flow_style=False)
```

---

## 5. YAML Configuration Templates

### 5.1 Default Configuration (config/default.yaml)

```yaml
# H-E1 Documentation Copilot - Default Configuration
hypothesis_id: h-e1
experiment_name: documentation_copilot_existence
random_seed: 42

model:
  model_name: meta-llama/Llama-3-8B-Instruct
  use_api: false
  temperature: 0.7
  max_length: 500
  top_p: 0.95
  do_sample: true
  device: 0
  torch_dtype: float16
  batch_size: 1
  num_workers: 4

corpus:
  corpus_dir: data/corpus
  vision_dir: data/corpus/vision
  nlp_dir: data/corpus/nlp
  tabular_dir: data/corpus/tabular
  total_examples: 500
  vision_count: 200
  nlp_count: 200
  tabular_count: 100
  min_completeness: 0.85
  required_sections:
    - Dataset Description
    - Data Collection
    - Uses and Limitations
  examples_per_prompt: 3
  max_example_length: 300

deployment:
  pilot_duration_days: 14
  target_users: 50
  max_users: 100
  treatment_ratio: 0.5
  randomization_seed: 42
  platform: huggingface
  integration_url: https://huggingface.co/datasets/upload
  max_suggestions_per_session: 30
  suggestion_timeout_seconds: 5
  collect_survey: true
  survey_questions:
    - "How helpful were the AI suggestions? (1-5)"
    - "Did the suggestions save you time? (Yes/No)"
    - "Would you use this feature again? (Yes/No)"

tracking:
  log_dir: data/logs/interactions
  backup_dir: data/logs/backups
  log_format: json
  log_level: INFO
  backup_interval_hours: 24
  track_timestamps: true
  track_time_to_decision: true
  track_dataset_metadata: true
  track_user_experience: true

evaluation:
  target_acceptance_rate: 70.0
  threshold_acceptance_rate: 40.0
  target_helpfulness: 3.5
  confidence_level: 0.95
  min_sample_size: 50
  stratify_by_dataset_type: true
  stratify_by_user_experience: true
  metrics:
    - acceptance_rate
    - acceptance_rate_by_type
    - helpfulness_rating
    - time_to_decision
    - session_completion_rate
```

---

### 5.2 GPU Configuration (config/gpu.yaml)

```yaml
# H-E1 GPU-specific overrides
model:
  device: 0  # First GPU
  torch_dtype: float16  # Use FP16 for faster inference
  batch_size: 1

# Environment variable (set before running)
# export CUDA_VISIBLE_DEVICES=0
```

---

### 5.3 API-based Configuration (config/api.yaml)

```yaml
# H-E1 API-based LLM (fallback if local inference too slow)
model:
  model_name: gpt-4
  use_api: true
  api_provider: openai
  api_key: ${OPENAI_API_KEY}  # Load from environment variable
  device: -1  # CPU (API handles inference)
  temperature: 0.7
  max_length: 500
```

---

## 6. Hyperparameter Rationale

### 6.1 LLM Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `temperature` | 0.7 | Balanced creativity (0.7 > 0.5 greedy, 0.7 < 1.0 random) |
| `max_length` | 500 | Sufficient for documentation paragraphs, not excessive |
| `top_p` | 0.95 | Nucleus sampling for quality (exclude low-probability tokens) |

**Source:** Archon KB - "LLM generation best practices"

### 6.2 Corpus Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `total_examples` | 500 | Sufficient diversity for 3-shot prompting across types |
| `min_completeness` | 0.85 | High-quality examples only (>85% completeness) |
| `examples_per_prompt` | 3 | 3-shot prompting proven effective (Archon KB) |

**Source:** Archon KB - "Few-shot learning sample size"

### 6.3 Deployment Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `pilot_duration_days` | 14 | 2-week window from Phase 2B timeline |
| `target_users` | 50 | Minimum for statistical power (binomial test n>=50) |
| `treatment_ratio` | 0.5 | Balanced 50/50 for control vs treatment |

**Source:** Phase 2B verification plan

---

## 7. Subtask Specifications

### Subtask E-5-1: Web UI Components
**Parent Epic:** E-5 (Deployment Interface)  
**Files:** `src/deployment/interface.py`, `templates/suggestion_ui.html`  
**Complexity:** 4/20

**Configuration Requirements:**
- Button labels: "Accept", "Reject", "Modify"
- Suggestion display: Max 500 characters, scrollable
- Real-time generation indicator: Loading spinner during LLM inference
- Color scheme: Match HuggingFace branding

**UI Config Schema:**
```python
@dataclass
class UIConfig:
    button_labels: Dict[str, str] = field(default_factory=lambda: {
        'accept': 'Accept Suggestion',
        'reject': 'Reject',
        'modify': 'Edit and Use'
    })
    max_display_chars: int = 500
    show_loading_spinner: bool = True
    theme: str = "huggingface"
```

---

### Subtask E-5-2: Real-time Generation Integration
**Parent Epic:** E-5 (Deployment Interface)  
**Files:** `src/deployment/interface.py`  
**Complexity:** 5/20

**Configuration Requirements:**
- API endpoint: `/generate_suggestion` (POST)
- Request timeout: 5 seconds
- Retry policy: 1 retry on timeout, then show error
- WebSocket for real-time updates (optional)

**API Config Schema:**
```python
@dataclass
class APIConfig:
    endpoint: str = "/generate_suggestion"
    timeout_seconds: int = 5
    max_retries: int = 1
    use_websocket: bool = False
```

---

### Subtask E-5-3: Session Management and Survey
**Parent Epic:** E-5 (Deployment Interface)  
**Files:** `src/deployment/survey.py`  
**Complexity:** 3/20

**Configuration Requirements:**
- Session timeout: 30 minutes inactivity
- Survey trigger: On documentation submission
- Survey format: 5-point Likert + 2 Yes/No questions
- Survey storage: CSV format

**Session Config Schema:**
```python
@dataclass
class SessionConfig:
    timeout_minutes: int = 30
    trigger_survey_on: str = "submission"  # 'submission' | 'exit'
    survey_format: str = "likert_5"
    survey_storage: str = "csv"
    survey_path: str = "experiments/pilot_deployment/survey_results.csv"
```

---

## 8. Environment Variables

**File:** `.env.example`

```bash
# GPU Configuration
CUDA_VISIBLE_DEVICES=0

# API Keys (if using API-based LLM)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Experiment Settings
EXPERIMENT_NAME=documentation_copilot_existence
HYPOTHESIS_ID=h-e1
RANDOM_SEED=42

# Deployment
HUGGINGFACE_TOKEN=your_token_here
LOG_LEVEL=INFO
```

---

## 9. Configuration Loading Example

**File:** `src/main.py`

```python
from src.config import Config

# Load configuration
config = Config.from_yaml("config/default.yaml")

# Override for GPU
if torch.cuda.is_available():
    config.model.device = 0
    print(f"Using GPU {config.model.device}")
else:
    config.model.device = -1
    print("GPU not available, using CPU")

# Initialize components
generator = SuggestionGenerator(
    model_name=config.model.model_name,
    temperature=config.model.temperature,
    max_length=config.model.max_length,
    device=config.model.device
)

tracker = SuggestionTracker(
    log_dir=config.tracking.log_dir
)

# Run experiment
deploy_pilot(config, generator, tracker)
```

---

## 10. Validation and Testing

### 10.1 Config Validation
```python
def validate_config(config: Config) -> None:
    """Validate configuration before experiment."""
    assert config.corpus.total_examples == (
        config.corpus.vision_count +
        config.corpus.nlp_count +
        config.corpus.tabular_count
    ), "Corpus counts don't sum to total"
    
    assert 0 <= config.deployment.treatment_ratio <= 1, \
        "Treatment ratio must be in [0, 1]"
    
    assert config.evaluation.target_acceptance_rate > \
        config.evaluation.threshold_acceptance_rate, \
        "Target must be higher than threshold"
```

### 10.2 Configuration Tests
- `test_config_from_yaml()`: Load default.yaml, verify all fields
- `test_config_validation()`: Test invalid values raise errors
- `test_config_to_yaml()`: Round-trip save/load preserves values

---

## 11. Inherited Configuration (None - Foundation Hypothesis)

**Note:** This is a foundation hypothesis with no base hypothesis to extend.

**No configuration inheritance from previous hypotheses.**

---

**Document Status:** ✅ Complete  
**Subtasks Defined:** 3/3 (E-5-1, E-5-2, E-5-3)  
**Config Schemas:** 5 dataclasses + YAML templates  
**Applied Patterns:** 2 from Archon KB  
**Generated:** 2026-04-15 (Configuration Agent - TEST mode)
