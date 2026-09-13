# Configuration Design: H-M2 Metamorphic Contract Validation

**Hypothesis ID:** h-m2  
**Document Type:** Configuration Specification  
**Phase:** 3 - Implementation Planning  
**Status:** DRAFT  
**Generated:** 2026-07-11

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Config classes verified from base code  
**Config Files Found**: /workspace/TEST_scope/docs/youra_research/_archive/20260711T091706_routing_recovery/h-m1/code/config.py  
**Pattern Used**: Dataclass (nested configuration following h-m1 pattern)

**Base Hypothesis Pattern**: h-m1 uses nested dataclass structure with factory pattern (`get_config()`) and validation methods. Pattern is reused for consistency.

---

## Applied Patterns

**Applied**: PyTorch config.py pattern (nested dataclasses), PyTorch tolerance defaults (rtol=1e-5, atol=1e-7)

---

## 1. Configuration Schema

### 1.1 Metamorphic Validation Configuration

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

@dataclass
class MetamorphicConfig:
    """Metamorphic property validation settings."""
    
    # Tolerance settings (PyTorch test suite defaults)
    rtol: float = 1e-5
    atol: float = 1e-7
    
    # Probe generation
    softmax_probe_batch_size: int = 4
    softmax_probe_num_classes: int = 10
    dropout_probe_size: int = 100
    
    # Validation flags
    enable_softmax_validation: bool = True
    enable_dropout_validation: bool = True
    
    # Numerical stability
    sum_dimension: int = -1  # Softmax sum dimension
```

### 1.2 Test Scenario Configuration

```python
@dataclass
class ScenarioConfig:
    """Test scenario generation settings."""
    
    # Scenario distribution
    num_control_scenarios: int = 10
    num_softmax_violation_scenarios: int = 20
    num_dropout_violation_scenarios: int = 20
    
    # Defect injection
    softmax_violation_multiplier: float = 0.9  # Multiply output by 0.9 to violate sum=1.0
    dropout_force_train_mode: bool = True  # Force dropout in eval mode
    
    # Test execution
    enable_ground_truth_validation: bool = True
    track_detection_stage: bool = True
```

### 1.3 Experiment Configuration

```python
@dataclass
class ExperimentConfig:
    """Experiment execution settings."""
    
    # Run configuration
    total_test_cases: int = 50  # 10 control + 20 softmax + 20 dropout
    execution_timeout_seconds: float = 10.0
    
    # Baseline comparison
    run_baseline: bool = True  # No contracts (0% detection)
    run_with_contracts: bool = True  # Metamorphic validation enabled
    
    # Metrics
    target_detection_rate: float = 0.70
    minimum_detection_rate: float = 0.50  # SHOULD_WORK gate threshold
    false_positive_threshold: float = 0.05
```

### 1.4 Results Configuration

```python
@dataclass
class ResultsConfig:
    """Results collection and output settings."""
    
    # Output paths
    results_dir: Path = Path("./results")
    detection_results_json: Path = Path("./results/detection_results.json")
    metrics_summary_json: Path = Path("./results/metrics_summary.json")
    
    # Figure output
    figure_output_dir: Path = Path("./figures")
    gate_metrics_figure: str = "gate_metrics_comparison.png"
    detection_breakdown_figure: str = "detection_rate_breakdown.png"
    
    # Logging
    log_execution_times: bool = True
    log_violation_details: bool = True
```

### 1.5 Root Configuration

```python
@dataclass
class H_M2_Config:
    """Root configuration for H-M2 metamorphic contract validation."""
    
    hypothesis_id: str = "h-m2"
    experiment_name: str = "metamorphic_contract_validation"
    seed: int = 42
    
    # Nested configurations
    metamorphic: MetamorphicConfig = field(default_factory=MetamorphicConfig)
    scenario: ScenarioConfig = field(default_factory=ScenarioConfig)
    experiment: ExperimentConfig = field(default_factory=ExperimentConfig)
    results: ResultsConfig = field(default_factory=ResultsConfig)
    
    def validate(self) -> bool:
        """Validate configuration constraints."""
        # Total test cases must match scenario distribution
        total_scenarios = (
            self.scenario.num_control_scenarios +
            self.scenario.num_softmax_violation_scenarios +
            self.scenario.num_dropout_violation_scenarios
        )
        assert total_scenarios == self.experiment.total_test_cases, \
            f"Scenario sum ({total_scenarios}) != total_test_cases ({self.experiment.total_test_cases})"
        
        # Detection thresholds must be ordered
        assert 0 <= self.experiment.minimum_detection_rate <= \
               self.experiment.target_detection_rate <= 1.0, \
            "Invalid detection rate thresholds"
        
        # Tolerance values must be positive
        assert self.metamorphic.rtol > 0 and self.metamorphic.atol > 0, \
            "Tolerance values must be positive"
        
        # Execution timeout must be positive
        assert self.experiment.execution_timeout_seconds > 0, \
            "Execution timeout must be positive"
        
        return True
    
    def setup_directories(self) -> None:
        """Create required directories."""
        self.results.results_dir.mkdir(parents=True, exist_ok=True)
        self.results.figure_output_dir.mkdir(parents=True, exist_ok=True)
    
    def setup_reproducibility(self) -> None:
        """Configure reproducibility settings."""
        import random
        import numpy as np
        import torch
        
        random.seed(self.seed)
        np.random.seed(self.seed)
        torch.manual_seed(self.seed)
        
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(self.seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False


def get_config() -> H_M2_Config:
    """Factory function to create and validate configuration."""
    config = H_M2_Config()
    config.validate()
    config.setup_directories()
    config.setup_reproducibility()
    return config
```

---

## 2. Inherited Configuration (Base Hypothesis)

### Base Pattern Reference

The following configuration pattern is inherited from h-m1:

```python
# From: h-m1/code/config.py (ACTUAL CODE)
@dataclass
class SmokeTestConfig:
    hypothesis_id: str = "h-m1"
    experiment_name: str = "auto_generated_smoke_tests"
    seed: int = 42
    
    # Nested dataclass pattern
    bug_database: BugDatabaseConfig = field(default_factory=BugDatabaseConfig)
    test_generation: TestGenerationConfig = field(default_factory=TestGenerationConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    
    def validate(self) -> bool: ...
```

**Pattern Reuse**: H-M2 follows same nested dataclass structure with:
- Root config class (`H_M2_Config` vs `SmokeTestConfig`)
- Factory pattern (`get_config()`)
- Validation method (`validate()`)
- Setup methods (`setup_directories()`, `setup_reproducibility()`)

**Verified from**: /workspace/TEST_scope/docs/youra_research/_archive/20260711T091706_routing_recovery/h-m1/code/config.py (actual implementation)

---

## 3. Task Configuration Breakdown

### B-1: Metamorphic Validators [Complexity: 12, Budget: 2]

```python
# Configuration for softmax and dropout validators
CONFIG_B1 = {
    "rtol": 1e-5,
    "atol": 1e-7,
    "softmax_probe_shape": (4, 10),
    "dropout_probe_size": 100,
    "sum_dimension": -1
}
```

**Subtasks [2/2 used]**:

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Softmax Validator | Implement `validate_softmax()` with torch.allclose |
| C-1-2 | Dropout Validator | Implement `validate_dropout_identity()` with eval mode check |

---

### B-2: Test Scenario Generation [Complexity: 10, Budget: 2]

```python
# Configuration for test scenario generation
CONFIG_B2 = {
    "num_control": 10,
    "num_softmax_violations": 20,
    "num_dropout_violations": 20,
    "enable_ground_truth": True
}
```

**Subtasks [2/2 used]**:

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Control Scenarios | Generate valid operations without violations |
| C-2-2 | Violation Scenarios | Generate softmax and dropout violation scenarios |

---

### B-3: Defect Injection [Complexity: 11, Budget: 2]

```python
# Configuration for defect injection
CONFIG_B3 = {
    "softmax_multiplier": 0.9,
    "dropout_force_train": True,
    "preserve_original": True,
    "validate_injection": True
}
```

**Subtasks [2/2 used]**:

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Softmax Injection | Multiply softmax output by 0.9 to violate sum=1.0 |
| C-3-2 | Dropout Injection | Force dropout to apply in eval mode |

---

### B-4: Experiment Runner [Complexity: 13, Budget: 2]

```python
# Configuration for experiment execution
CONFIG_B4 = {
    "run_baseline": True,
    "run_with_contracts": True,
    "execution_timeout": 10.0,
    "log_metrics": True
}
```

**Subtasks [2/2 used]**:

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Baseline Execution | Run tests without contracts (0% detection) |
| C-4-2 | Contract Execution | Run tests with metamorphic validation |

---

### B-5: Numerical Tolerance Testing [Complexity: 9, Budget: 2]

```python
# Configuration for tolerance validation
CONFIG_B5 = {
    "rtol_values": [1e-5, 1e-4, 1e-3],
    "atol_values": [1e-7, 1e-6, 1e-5],
    "test_edge_cases": True,
    "validate_stability": True
}
```

**Subtasks [2/2 used]**:

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Tolerance Edge Cases | Test boundary cases (all zeros, large values) |
| C-5-2 | Stability Validation | Validate numerical stability across tolerance settings |

---

## 4. Default Values Rationale

### 4.1 Metamorphic Validation Defaults

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `rtol` | 1e-5 | PyTorch test suite default for floating-point comparison |
| `atol` | 1e-7 | PyTorch test suite default for numerical tolerance |
| `softmax_probe_batch_size` | 4 | Minimal batch size for vectorized validation |
| `softmax_probe_num_classes` | 10 | Representative size for attention mechanisms |
| `dropout_probe_size` | 100 | Sufficient for identity property validation |

### 4.2 Test Scenario Defaults

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `num_control_scenarios` | 10 | 20% of total tests for false positive measurement |
| `num_softmax_violation_scenarios` | 20 | 40% of tests for primary metamorphic property |
| `num_dropout_violation_scenarios` | 20 | 40% of tests for secondary metamorphic property |
| `softmax_violation_multiplier` | 0.9 | 10% deviation creates detectable violation |

### 4.3 Experiment Defaults

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `total_test_cases` | 50 | Sufficient for PoC validation (matches scenario distribution) |
| `execution_timeout_seconds` | 10.0 | NFR-1 requirement from PRD |
| `target_detection_rate` | 0.70 | Primary success criterion from PRD |
| `minimum_detection_rate` | 0.50 | SHOULD_WORK gate threshold |

---

## 5. Configuration Usage

### 5.1 Basic Usage

```python
from config import get_config

# Load and validate configuration
config = get_config()

# Access metamorphic settings
print(f"Tolerance: rtol={config.metamorphic.rtol}, atol={config.metamorphic.atol}")
print(f"Total test cases: {config.experiment.total_test_cases}")
print(f"Target detection rate: {config.experiment.target_detection_rate * 100}%")
```

### 5.2 Custom Configuration Override

```python
from config import H_M2_Config, MetamorphicConfig

# Custom tolerance settings
custom_metamorphic = MetamorphicConfig(
    rtol=1e-4,
    atol=1e-6,
    softmax_probe_batch_size=8
)

# Create config with override
config = H_M2_Config(metamorphic=custom_metamorphic)
config.validate()
config.setup_directories()
config.setup_reproducibility()
```

### 5.3 Integration with Test Suite

```python
# test_suite/scenarios.py
from config import get_config

def generate_test_scenarios():
    config = get_config()
    
    scenarios = []
    
    # Control scenarios
    for i in range(config.scenario.num_control_scenarios):
        scenarios.append(create_control_scenario(i))
    
    # Softmax violation scenarios
    for i in range(config.scenario.num_softmax_violation_scenarios):
        scenarios.append(create_softmax_violation_scenario(
            i,
            multiplier=config.scenario.softmax_violation_multiplier
        ))
    
    # Dropout violation scenarios
    for i in range(config.scenario.num_dropout_violation_scenarios):
        scenarios.append(create_dropout_violation_scenario(
            i,
            force_train=config.scenario.dropout_force_train_mode
        ))
    
    return scenarios
```

---

## 6. Integration with PRD Requirements

| PRD Requirement | Configuration Parameter | Default Value |
|-----------------|-------------------------|---------------|
| FR-3.1: Softmax sum validation with tolerance | `metamorphic.rtol`, `metamorphic.atol` | 1e-5, 1e-7 |
| FR-3.2: Dropout identity validation | `metamorphic.enable_dropout_validation` | True |
| FR-3.3: Lightweight probe inputs | `metamorphic.softmax_probe_batch_size` | 4 |
| FR-4.1: Primary metric ≥70% detection | `experiment.target_detection_rate` | 0.70 |
| FR-4.2: Execution time ≤10s | `experiment.execution_timeout_seconds` | 10.0 |
| FR-4.2: False positive rate <5% | `experiment.false_positive_threshold` | 0.05 |
| NFR-2: Determinism via fixed seeds | `seed` | 42 |
| NFR-4: SHOULD_WORK gate ≥70% | `experiment.minimum_detection_rate` | 0.50 |

---

## 7. Reproducibility Checklist

Configuration ensures reproducibility through:

- [x] **Fixed random seeds** (Python, NumPy, PyTorch)
- [x] **CUDA deterministic mode** (slower but reproducible)
- [x] **Documented tolerance values** (PyTorch test suite defaults)
- [x] **Validation methods** (prevent invalid configurations)
- [x] **Path management** (cross-platform via `pathlib.Path`)
- [x] **Probe size limits** (fixed batch sizes for consistent overhead)

---

## 8. Configuration Validation

The `validate()` method enforces critical constraints:

```python
def validate(self) -> bool:
    """Validate configuration constraints."""
    
    # Scenario distribution integrity
    total_scenarios = (
        self.scenario.num_control_scenarios +
        self.scenario.num_softmax_violation_scenarios +
        self.scenario.num_dropout_violation_scenarios
    )
    assert total_scenarios == self.experiment.total_test_cases
    
    # Detection thresholds
    assert 0 <= self.experiment.minimum_detection_rate <= \
           self.experiment.target_detection_rate <= 1.0
    
    # Numerical parameters
    assert self.metamorphic.rtol > 0 and self.metamorphic.atol > 0
    assert self.experiment.execution_timeout_seconds > 0
    
    return True
```

**Validation is mandatory** - `get_config()` always calls `validate()` before returning.

---

## Summary

**Configuration Format**: Python dataclasses (nested structure)

**Key Features**:
1. Type-safe defaults for all metamorphic validation parameters
2. Validation methods prevent invalid configurations
3. Reproducibility via fixed seeds and deterministic settings
4. Path management for cross-platform compatibility
5. Pattern consistency with h-m1 base hypothesis

**Total Parameters**: 25+ configuration options organized into 5 nested dataclasses

**Subtask Allocation**: 10 subtasks (2 per epic task within budget)

**Next Steps**:
- Implement configuration in `experiments/h-m2/config.py`
- Write unit tests for validation logic
- Integrate with metamorphic validators and test scenarios

---

**Document Status:** READY FOR IMPLEMENTATION  
**Next Phase:** Phase 4 - Code Implementation  
**Configuration File Location:** `experiments/h-m2/config.py`
