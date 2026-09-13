---
hypothesis_id: h-m1
type: MECHANISM
gate: MUST_WORK
date: 2026-03-18
generated_by: Phase 3 Configuration Design
---

# Configuration Specification: Low-Rank Compression Mechanism (h-m1)

**Applied:** PyTorch dataclass patterns (from Archon KB)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from base code
**Config Files Found**: h-e1/code/src/config.py
**Pattern Used**: Python dataclass
**Verified From**: /home/anonymous/YouRA_results_new_4_sonnet45/TEST_scope/docs/youra_research/20260318_scope/h-e1/code/src/config.py

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited from base hypothesis h-e1:

```python
# From: h-e1/code/src/config.py (ACTUAL CODE)
@dataclass
class AnalysisConfig:
    """Configuration for low-rank structure analysis."""

    # Model configuration
    model_name: str = "mistralai/Mistral-7B-v0.1"
    target_layers: range = field(default_factory=lambda: range(20, 32))
    variance_threshold: float = 0.99

    # Data configuration
    num_samples: int = 50
    context_length: int = 512
    batch_size: int = 1

    # Runtime configuration
    random_seed: int = 42
    output_dir: str = "../figures"
    device: str = "cuda"
    use_fp16: bool = True

    # HuggingFace authentication
    hf_token: Optional[str] = None
```

**Verified from**: h-e1/code/src/config.py (actual implementation)

---

## M-1: Setup h-e1 Integration (Complexity: 6, Budget: 4)

**Applied**: Python module import patterns

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class IntegrationConfig:
    """Configuration for h-e1 base hypothesis integration."""

    base_hypothesis_path: str = "../h-e1/code"
    reuse_base_results: bool = True
    base_results_file: str = "../h-e1/results/analysis_results.json"
```

### Subtasks (4/4 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M-1-1 | DependencySetup | Install h-e1 as local package dependency |
| M-1-2 | ImportValidation | Verify AnalysisConfig and LowRankAnalyzer imports |
| M-1-3 | PathConfiguration | Configure relative paths to h-e1 modules |
| M-1-4 | BaseAnalyzerTest | Run base analyzer on single layer to verify integration |

---

## M-2: Context Length Data Pipeline (Complexity: 9, Budget: 4)

**Applied**: HuggingFace dataset streaming patterns

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class ContextDataConfig:
    """Configuration for multi-context length data generation."""

    context_lengths: List[int] = field(default_factory=lambda: [8192, 16384, 32768, 65536, 131072])
    # Non-standard: Using 5 context lengths for stability validation (standard: 1)
    samples_per_context: int = 10
    dataset_name: str = "EleutherAI/pile"
    dataset_split: str = "train"
    streaming: bool = True
    max_tokens: int = 131072
```

### Subtasks (4/4 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M-2-1 | MultiContextLoader | Extend data module to generate samples at 5 context lengths |
| M-2-2 | TokenizerExtension | Handle variable context lengths with same tokenizer |
| M-2-3 | SampleGenerator | Generate 10 samples per context length (50 total) |
| M-2-4 | DataValidation | Verify token count matches target context length |

---

## M-3: Stability Testing Module (Complexity: 10, Budget: 4)

**Applied**: Variance analysis patterns

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class StabilityConfig:
    """Configuration for context length stability testing."""

    baseline_context_length: int = 8192
    stability_threshold: float = 1.2
    # Non-standard: Using 1.2x threshold for variance (allows 20% deviation across contexts)
    variance_metric: str = "entropy"
    aggregation_method: str = "per_layer"
```

### Subtasks (4/4 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M-3-1 | ContextStabilityTester | Implement stability tester class with variance computation |
| M-3-2 | VarianceComputation | Calculate entropy variance across context lengths per layer |
| M-3-3 | StabilityValidation | Check variance against 1.2x baseline threshold |
| M-3-4 | ResultAggregation | Aggregate stability metrics across all layers |

---

## M-4: Mechanism Verification Logic (Complexity: 8, Budget: 4)

**Applied**: Boolean validation patterns

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from typing import Dict

@dataclass
class MechanismVerificationConfig:
    """Configuration for mechanism activation verification."""

    required_indicators: Dict[str, bool] = field(default_factory=lambda: {
        "svd_computed": True,
        "rank_measured": True,
        "entropy_measured": True,
        "regression_valid": True
    })
    compression_trend_direction: str = "decreasing"
    regression_significance_alpha: float = 0.01
```

### Subtasks (4/4 used)

| ID | Subtask | Description |
|----|---------|-------------|
| M-4-1 | ActivationChecks | Implement indicator checks for mechanism activation |
| M-4-2 | CompressionValidation | Verify effective rank decreases with depth (L20→L32) |
| M-4-3 | RegressionVerification | Check β < 0 with p < 0.01 significance |
| M-4-4 | MechanismValidator | Combine all checks into unified validator class |

---

## Extended Configuration (Current Hypothesis)

### MechanismConfig (Extends AnalysisConfig)

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from h_e1.src.config import AnalysisConfig

@dataclass
class MechanismConfig(AnalysisConfig):
    """Extended configuration for mechanism validation experiment.

    Inherits from h-e1 AnalysisConfig:
    - model_name: str = "mistralai/Mistral-7B-v0.1"
    - target_layers: range = range(20, 32)
    - variance_threshold: float = 0.99
    - num_samples: int = 50
    - context_length: int = 512
    - batch_size: int = 1
    - random_seed: int = 42
    - output_dir: str = "../figures"
    - device: str = "cuda"
    - use_fp16: bool = True
    - hf_token: Optional[str] = None
    """

    # Context stability testing
    context_lengths: List[int] = field(default_factory=lambda: [8192, 16384, 32768, 65536, 131072])
    samples_per_context: int = 10
    baseline_context_length: int = 8192

    # Stability validation
    stability_threshold: float = 1.2
    # Non-standard: Allows 20% variance increase across contexts for mechanism validation

    # Mechanism verification
    max_effective_rank: int = 256
    entropy_slope_max: float = 0.0
    regression_alpha: float = 0.01

    # Integration with h-e1
    base_hypothesis_path: str = "../h-e1/code"
    reuse_base_results: bool = True
    base_results_file: str = "../h-e1/results/analysis_results.json"

    # Output configuration
    validation_report_path: str = "../04_validation.md"
    stability_heatmap_path: str = "../figures/entropy_stability_heatmap.png"


def load_config() -> MechanismConfig:
    """Load configuration from environment or use defaults."""
    import os

    config = MechanismConfig()

    # Override from environment variables
    if "HF_TOKEN" in os.environ:
        config.hf_token = os.environ["HF_TOKEN"]

    if "NUM_SAMPLES" in os.environ:
        config.num_samples = int(os.environ["NUM_SAMPLES"])

    if "OUTPUT_DIR" in os.environ:
        config.output_dir = os.environ["OUTPUT_DIR"]

    if "MODEL_NAME" in os.environ:
        config.model_name = os.environ["MODEL_NAME"]

    if "BASE_HYPOTHESIS_PATH" in os.environ:
        config.base_hypothesis_path = os.environ["BASE_HYPOTHESIS_PATH"]

    return config
```

---

## Gate Validation Configuration

### Thresholds (From PRD Section: Success Criteria)

```python
GATE_CRITERIA = {
    "deep_layer_rank": {
        "threshold": 256,
        "condition": "max(r_eff[20:32]) < 256",
        "gate_type": "MUST_WORK"
    },
    "entropy_slope": {
        "threshold": 0.0,
        "condition": "β < 0 with p < 0.01",
        "gate_type": "MUST_WORK"
    },
    "context_stability": {
        "threshold": 1.2,
        "condition": "variance ≤ 1.2× baseline",
        "gate_type": "MUST_WORK"
    }
}
```

---

## Environment Configuration

### GPU Setup Script

```bash
#!/bin/bash
# File: code/run_mechanism.sh

# Check GPU availability
nvidia-smi

# Select empty GPU
echo "Available GPUs shown above. Select empty GPU ID:"
read GPU_ID
export CUDA_VISIBLE_DEVICES=$GPU_ID

# Set HuggingFace token
if [ -z "$HF_TOKEN" ]; then
    echo "Warning: HF_TOKEN not set. Model download may fail."
fi

# Run mechanism validation
python src/main.py
```

### Requirements

```txt
# File: code/requirements.txt

# Inherit all h-e1 dependencies
torch>=2.0.0
transformers>=4.30.0
datasets>=2.12.0
scipy>=1.10.0
matplotlib>=3.5.0
seaborn>=0.12.0

# h-e1 as local dependency
-e ../h-e1/code
```

---

## Configuration Usage Example

```python
# In src/main.py
from config import load_config, MechanismConfig
from h_e1.src.analyzer import LowRankAnalyzer
from h_e1.src.config import AnalysisConfig

def main():
    # Load extended configuration
    config = load_config()

    # Initialize base analyzer with inherited config
    base_config = AnalysisConfig(
        model_name=config.model_name,
        target_layers=config.target_layers,
        variance_threshold=config.variance_threshold,
        num_samples=config.num_samples,
        context_length=config.context_length,
        batch_size=config.batch_size,
        random_seed=config.random_seed,
        output_dir=config.output_dir,
        device=config.device,
        use_fp16=config.use_fp16,
        hf_token=config.hf_token
    )

    analyzer = LowRankAnalyzer(base_config)

    # Run base analysis (reuse h-e1)
    if config.reuse_base_results:
        base_results = load_base_results(config.base_results_file)
    else:
        base_results = analyzer.analyze_all_layers()

    # Run stability tests with extended config
    stability_tester = ContextStabilityTester(
        analyzer=analyzer,
        context_lengths=config.context_lengths,
        samples_per_context=config.samples_per_context
    )

    stability_results = stability_tester.test_context_stability()

    # Validate mechanism
    validator = MechanismValidator(
        analyzer=analyzer,
        stability_tester=stability_tester,
        max_effective_rank=config.max_effective_rank,
        entropy_slope_max=config.entropy_slope_max,
        stability_threshold=config.stability_threshold
    )

    validation = validator.validate_gate_criteria(base_results, stability_results)

    # Generate report
    validator.generate_validation_report(
        validation_results=validation,
        output_path=config.validation_report_path
    )

if __name__ == "__main__":
    main()
```

---

## Configuration Validation

### Pre-run Checks

```python
def validate_mechanism_config(config: MechanismConfig) -> None:
    """Validate mechanism configuration before running experiment."""

    # Validate base config
    assert config.target_layers.stop > config.target_layers.start, "Invalid layer range"
    assert config.num_samples > 0, "num_samples must be positive"
    assert 0.0 < config.variance_threshold < 1.0, "variance_threshold must be in (0, 1)"

    # Validate context stability config
    assert len(config.context_lengths) > 0, "context_lengths must not be empty"
    assert config.baseline_context_length in config.context_lengths, "baseline must be in context_lengths"
    assert config.samples_per_context > 0, "samples_per_context must be positive"
    assert config.stability_threshold >= 1.0, "stability_threshold must be >= 1.0"

    # Validate mechanism verification config
    assert config.max_effective_rank > 0, "max_effective_rank must be positive"
    assert config.entropy_slope_max <= 0.0, "entropy_slope_max must be non-positive"
    assert 0.0 < config.regression_alpha < 1.0, "regression_alpha must be in (0, 1)"

    # Validate h-e1 integration
    import os
    assert os.path.exists(config.base_hypothesis_path), f"h-e1 path not found: {config.base_hypothesis_path}"

    # Check GPU availability
    import torch
    assert torch.cuda.is_available(), "CUDA not available"

    print("✓ Configuration validated")
    print(f"  Model: {config.model_name}")
    print(f"  Target layers: {config.target_layers}")
    print(f"  Context lengths: {config.context_lengths}")
    print(f"  Samples per context: {config.samples_per_context}")
    print(f"  Stability threshold: {config.stability_threshold}")
    print(f"  GPU: {torch.cuda.get_device_name(0)}")
```

---

## MECHANISM Hypothesis Note

This is a **mechanism validation configuration** (extends EXISTENCE h-e1). The goal is to validate:

1. **Mechanism activated**: All SVD/entropy indicators present
2. **Compression mechanism**: Effective rank decreases with depth (L20→L32)
3. **Context stability**: Entropy variance ≤ 1.2× baseline across 8K-128K contexts

**Gate Criteria (ALL must pass):**
- r_eff < 256 for all layers L≥20
- β < 0 with p < 0.01
- Variance ≤ 1.2× baseline

If any criterion fails, the mechanism is NOT validated and the entire conversion approach is ABORTED.

---

*Configuration designed for MECHANISM validation | Extends h-e1 | Adds context stability testing*
