# Configuration Specification: h-m-integrated

**Document Type**: Configuration Design
**Hypothesis ID**: h-m-integrated
**Hypothesis Type**: MECHANISM
**Created Date**: 2026-07-13
**Infrastructure Tier**: STANDARD

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from base code
**Analyzed Path**: `/workspace/TEST_question/docs/youra_research/h-e1/code/`
**Config Files Found**: `run_experiment.py` (hardcoded config dict)
**Pattern Used**: Hardcoded dict (from h-e1, extending to dataclass for h-m-integrated)

---

## Applied Patterns

Applied: PyTorch dataclass configuration pattern (extending h-e1 hardcoded config)
Applied: Modular calibration pipeline configuration (from h-e1)
Applied: Multi-method evaluation configuration pattern

---

## Inherited Configuration (Base Hypothesis)

### Config Values (From Actual Code)

The following parameters are inherited from h-e1 base hypothesis:

```python
# From: /workspace/TEST_question/docs/youra_research/h-e1/code/run_experiment.py
BASE_CONFIG = {
    "datasets": ["truthful_qa", "Anthropic/hh-rlhf", "squad"],
    "model_name": "meta-llama/Llama-2-7b-hf",
    "num_samples": 5,
    "calibration_size": 1000,
    "test_size": 1000,
    "coverage_target": 0.9,
    "temperature": 0.7,
    "max_tokens": 256,
    "seed": 42
}

# From: data_loader.py
DATA_LOADER_DEFAULTS = {
    "tokenizer_name": "meta-llama/Llama-2-7b-hf",
    "max_length": 512,
    "calibration_size": 1000,
    "test_size": 1000
}

# From: baseline_model.py
GENERATOR_DEFAULTS = {
    "model_name": "meta-llama/Llama-2-7b-hf",
    "device": "cuda",
    "torch_dtype": "float16",  # For CUDA
    "max_tokens": 256,
    "temperature": 0.7
}

# From: consistency_scorer.py
CONSISTENCY_DEFAULTS = {
    "nli_model": "roberta-large-mnli",
    "device": "cuda"
}

# From: conformal_predictor.py
CONFORMAL_DEFAULTS = {
    "coverage_target": 0.9
}
```

**Verified from**: h-e1/code/ (actual implementation)

---

## M-3: ECE Metric & Cost Tracking [Complexity: 10, Budget: 2]

Applied: Standard calibration metric defaults (10-bin ECE, forward pass counting)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class ECEConfig:
    n_bins: int = 10
    bin_range: tuple[float, float] = (0.0, 1.0)

@dataclass
class CostTrackerConfig:
    baseline_costs: dict[str, int] = None  # Computed during runtime
    
    def __post_init__(self):
        if self.baseline_costs is None:
            self.baseline_costs = {
                "selfcheck": 5000,  # 5 samples × 1000 queries
                "coin": 1500,       # 1 sample + calibration overhead
                "cascade": 6500     # SelfCheck + COIN
            }
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | ECE Implementation | 10-bin calibration error computation |
| C-3-2 | Cost Tracker | Forward pass counter for all methods |

---

## M-4: Multi-Method Evaluator [Complexity: 12, Budget: 2]

Applied: Statistical testing configuration (t-test, significance threshold)

### Configuration (Python Dataclass)

```python
@dataclass
class EvaluationConfig:
    ece_bins: int = 10
    gate_ece_max: float = 0.05
    gate_p_threshold: float = 0.05
    gate_coverage_min: float = 0.90
    gate_cost_reduction_min: float = 0.30
    gate_cost_reduction_max: float = 0.50
    statistical_test: str = "t-test"
    test_type: str = "two-tailed"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Evaluator Core | Multi-dataset, multi-method evaluation pipeline |
| C-4-2 | Statistical Tests | Pairwise t-tests with p < 0.05 validation |

---

## M-5: Ablation Study [Complexity: 11, Budget: 2]

Applied: Correlation perturbation configuration (sweet spot validation)

### Configuration (Python Dataclass)

```python
@dataclass
class AblationConfig:
    rho_values: list[float] = None
    sweet_spot_center: float = 0.5
    sweet_spot_tolerance: float = 0.1
    num_perturbations: int = 100  # For correlation simulation
    
    def __post_init__(self):
        if self.rho_values is None:
            self.rho_values = [0.2, 0.35, 0.5, 0.65, 0.8]
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Correlation Perturbation | Simulate varying ρ levels via score perturbation |
| C-5-2 | Sweet Spot Validation | ECE measurement across ρ values, quadratic fit |

---

## M-6: Visualization Suite [Complexity: 12, Budget: 2]

Applied: Matplotlib publication-quality defaults

### Configuration (Python Dataclass)

```python
@dataclass
class VisualizationConfig:
    output_dir: str = "figures/"
    format: str = "png"
    dpi: int = 300
    figsize: tuple[int, int] = (10, 6)
    style: str = "seaborn-v0_8-paper"
    plots: list[str] = None
    
    def __post_init__(self):
        if self.plots is None:
            self.plots = [
                "ece_comparison",
                "reliability_diagrams",
                "cost_quality_tradeoff",
                "coverage_comparison",
                "ablation_sweet_spot"
            ]
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Core Plots | 5 required figures (ECE, reliability, cost, coverage, ablation) |
| C-6-2 | Figure Export | PNG export with 300 DPI, publication quality |

---

## M-7: Integration Testing [Complexity: 11, Budget: 2]

Applied: PyTorch test defaults (unit + integration testing)

### Configuration (Python Dataclass)

```python
@dataclass
class TestConfig:
    test_datasets: list[str] = None
    test_sample_size: int = 100  # Reduced for fast testing
    integration_timeout: int = 300  # Seconds
    unit_test_seed: int = 42
    
    def __post_init__(self):
        if self.test_datasets is None:
            self.test_datasets = ["truthful_qa"]  # Single dataset for integration test
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Unit Tests | Test HBC, baselines, ECE, cost tracker independently |
| C-7-2 | Integration Test | End-to-end pipeline with gate validation |

---

## M-8: Experiment Execution [Complexity: 10, Budget: 2]

Applied: Experiment orchestration configuration (multi-dataset, multi-method)

### Configuration (Python Dataclass)

```python
@dataclass
class ExecutionConfig:
    datasets: list[str] = None
    methods: list[str] = None
    output_report_path: str = "04_validation.md"
    checkpoint_dir: str = "checkpoints/"
    save_intermediate: bool = True
    
    def __post_init__(self):
        if self.datasets is None:
            self.datasets = ["truthful_qa", "Anthropic/hh-rlhf", "squad_v2"]
        if self.methods is None:
            self.methods = ["hbc", "selfcheck", "coin", "cascade"]
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Experiment Runner | Execute 3 datasets × 4 methods with ablation |
| C-8-2 | Report Generator | Generate validation.md with pass/fail determination |

---

## Unified Configuration (Main Config Class)

### Master Configuration

```python
from dataclasses import dataclass, field

@dataclass
class HBCExperimentConfig:
    """Master configuration for h-m-integrated experiment."""
    
    # Inherited from h-e1 (verified from actual code)
    model_name: str = "meta-llama/Llama-2-7b-hf"
    num_samples: int = 5
    temperature: float = 0.7
    max_tokens: int = 256
    seed: int = 42
    
    # Data configuration (from h-e1)
    datasets: list[str] = field(default_factory=lambda: ["truthful_qa", "Anthropic/hh-rlhf", "squad_v2"])
    max_length: int = 512
    calibration_size: int = 500  # Reduced from 1000 (h-e1) for efficiency
    test_size: int = 1000
    
    # HBC-specific configuration (new for h-m-integrated)
    hbc_alpha: float = 0.1
    hbc_max_iterations: int = 3
    hbc_initial_threshold: float = 0.5
    
    # Baseline configurations
    selfcheck_thresholds: list[float] = field(default_factory=lambda: [0.3, 0.4, 0.5, 0.6, 0.7])
    coin_alpha: float = 0.1
    
    # Evaluation configuration
    ece_config: ECEConfig = field(default_factory=ECEConfig)
    cost_config: CostTrackerConfig = field(default_factory=CostTrackerConfig)
    eval_config: EvaluationConfig = field(default_factory=EvaluationConfig)
    ablation_config: AblationConfig = field(default_factory=AblationConfig)
    viz_config: VisualizationConfig = field(default_factory=VisualizationConfig)
    test_config: TestConfig = field(default_factory=TestConfig)
    exec_config: ExecutionConfig = field(default_factory=ExecutionConfig)
    
    # Device configuration
    device: str = "cuda"
    torch_dtype: str = "float16"
    
    # Consistency scoring (from h-e1)
    nli_model: str = "roberta-large-mnli"
    bertscore_model: str = "microsoft/deberta-xlarge-mnli"
    
    # Coverage target (from h-e1)
    coverage_target: float = 0.9
```

---

## Usage Example

```python
# main.py or train.py
from config import HBCExperimentConfig, ECEConfig, AblationConfig

# Use default config
config = HBCExperimentConfig()

# Or customize specific components
config = HBCExperimentConfig(
    calibration_size=500,
    hbc_max_iterations=5,
    ablation_config=AblationConfig(rho_values=[0.1, 0.3, 0.5, 0.7, 0.9])
)

# Initialize components with config
from src.hbc_calibrator import HierarchicalBayesianCalibrator
from src.multi_method_evaluator import MultiMethodEvaluator

hbc = HierarchicalBayesianCalibrator(
    alpha=config.hbc_alpha,
    max_iterations=config.hbc_max_iterations
)

evaluator = MultiMethodEvaluator(
    methods=config.exec_config.methods,
    datasets=config.datasets,
    ece_metric=ECEMetric(**vars(config.ece_config)),
    cost_tracker=ComputationalCostTracker()
)

# Run experiment
results = evaluator.run_all_experiments()
```

---

## Configuration Notes

### Key Differences from h-e1

1. **Calibration Size**: Reduced from 1000 → 500 samples (computational efficiency focus)
2. **New HBC Parameters**: `alpha`, `max_iterations`, `initial_threshold` (not in h-e1)
3. **Baseline Suite**: Expanded to include 3 baselines + HBC (h-e1 had only consistency + conformal)
4. **Ablation Config**: New component for sweet spot validation (not in h-e1)

### Field Name Verification

All field names verified from h-e1 actual implementation:
- ✅ `model_name` (not `model_id`)
- ✅ `num_samples` (not `n_samples`)
- ✅ `coverage_target` (not `target_coverage`)
- ✅ `calibration_size` (not `calib_size`)

---

## Self-Validation

- [x] ONE format only (dataclass)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values (calibration_size change noted)
- [x] Subtask count within budget (12 subtasks total, 2 per module)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Inherited Configuration section included
- [x] Field names verified from actual h-e1 code

---

**Configuration Status**: COMPLETE
**Ready for Phase 4 Implementation**: YES
**Total Budget Used**: 12/12 (100%)
