# Configuration Design
# Hypothesis: h-m1 - Annotation Consistency Study

**Version:** 1.0  
**Date:** 2026-04-19  
**Hypothesis ID:** h-m1  
**Hypothesis Type:** MECHANISM (Step 1)  
**Budget:** 2 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Config verified from h-e1 base code  
**Config Files Found:** h-e1/code/config.yaml  
**Pattern Used:** Hardcoded YAML configuration (LIGHT tier)

**Note:** h-e1 uses YAML-based configuration with dictionary access pattern. h-m1 extends this approach for consistency.

---

## Configuration Philosophy

**Applied:** LIGHT-tier minimal YAML configuration (KB-003-MinimalConfig)

**Approach:** Single hardcoded YAML file extending h-e1 structure with training protocol parameters.

---

## Inherited Configuration (Base Hypothesis)

### Base Config Structure (From h-e1 Actual Code)

The following configuration structure is inherited from h-e1:

```yaml
# From: h-e1/code/config.yaml (ACTUAL CODE - VERIFIED)
experiment:
  name: str
  hypothesis_id: str
  description: str
  seed: 42

sampling:
  sample_size: int
  stratification_column: str
  n_quartiles: int
  samples_per_quartile: int

annotation:
  n_annotators: 3
  violation_criteria: List[str]

dataset:
  name: "Anthropic/hh-rlhf"
  subset: null
  split: "train"
  cache_dir: str

hypothesis_test:
  null_hypothesis_threshold: float
  alpha: 0.05
  alternative: str
  confidence_level: 0.95

statistical_analysis:
  kappa_threshold: float
  kappa_interpretation: Dict[str, List[float]]

outputs:
  data_dir: str
  figures_dir: str
  results_file: str
  report_file: str
  samples_file: str
  annotations_file: str
  final_labels_file: str

logging:
  level: str
  format: str
```

**Verified from:** h-e1/code/config.yaml and main.py (actual implementation)

---

## Extended Configuration (h-m1)

### Main Configuration File (config.yaml)

```yaml
# Experiment Configuration for H-M1
# Annotation Consistency Study with Training Protocol

experiment:
  name: "h-m1-annotation-consistency"
  hypothesis_id: "h-m1"
  description: "Validate that explicit criteria training improves annotation consistency"
  seed: 42
  test_sample_size: 300
  calibration_sample_size: 50
  n_annotators: 3

# Training protocol configuration (NEW for h-m1)
training:
  guidelines_source: "Bai et al. 2022 (HH-RLHF paper)"
  guidelines_path: "./training_materials/hhrlhf_guidelines.yaml"
  presentation_duration_min: 30
  calibration_threshold_kappa: 0.60
  calibration_gold_labels_path: "./data/calibration_gold_labels.csv"

# Sampling strategy (EXTENDED from h-e1)
sampling:
  # Test set
  test_sample_size: 300
  stratification_method: "violation_type"
  violation_types:
    - "harmful_content"
    - "misinformation"
    - "instruction_violation"
  samples_per_type: 100
  
  # Calibration set (NEW)
  calibration_sample_size: 50
  calibration_stratified: true
  
  # Randomization per annotator
  randomize_per_annotator: true
  seed: 42

annotation:
  n_annotators: 3
  violation_criteria:
    - "Direct harm/violence encouragement"
    - "Toxic/offensive language"
    - "Privacy violations or personal information disclosure"
    - "Dangerous/illegal advice"
    - "Deception or misinformation"
    - "Other safety policy violations"
  allow_uncertain_flag: true

dataset:
  name: "Anthropic/hh-rlhf"
  subset: null
  split: "train"
  cache_dir: "/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_bi_align_3/docs/youra_research/20260419_bi_align/.data_cache/datasets"

# Gate conditions (MODIFIED for h-m1)
gates:
  primary_kappa_threshold: 0.70
  secondary_agreement_threshold: 0.75
  alpha: 0.05
  both_required: true

# Statistical testing (EXTENDED)
statistical_analysis:
  # Inter-annotator agreement
  kappa_threshold: 0.70
  kappa_interpretation:
    poor: [0.00, 0.20]
    slight: [0.21, 0.40]
    fair: [0.41, 0.60]
    moderate: [0.61, 0.75]
    substantial: [0.76, 1.00]
  
  # Hypothesis test
  test_type: "one_sample_t_test"
  h0_threshold: 0.60
  h1_threshold: 0.70
  alpha: 0.05

# Baseline comparison (NEW)
baseline_comparison:
  h_e1_kappa: 0.498
  expected_improvement_min: 0.15
  expected_improvement_max: 0.25

outputs:
  data_dir: "./data"
  figures_dir: "./outputs/figures"
  results_file: "./outputs/results.json"
  report_file: "./outputs/report.md"
  
  # File naming
  test_samples_file: "hh_rlhf_test_samples.csv"
  calibration_samples_file: "hh_rlhf_calibration.csv"
  calibration_results_file: "calibration_results.csv"
  annotations_file: "annotations.csv"
  
  # Figures (4 required)
  gate_metrics_figure: "gate_metrics.png"
  inter_annotator_matrix_figure: "inter_annotator_matrix.png"
  agreement_distribution_figure: "agreement_distribution.png"
  confusion_matrices_figure: "confusion_matrices.png"

logging:
  level: "INFO"
  format: "simple"
```

---

## Configuration Loading

### Config Loader (Reused from h-e1)

```python
import yaml
from typing import Dict, Any

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config.yaml
    
    Returns:
        Dict with all configuration parameters
    
    Note: No validation or environment overrides for LIGHT tier
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config
```

---

## M-1: Data Preparation Configuration

**Complexity:** 8/20, **Budget:** 2 subtasks allocated

### Configuration Parameters

```yaml
sampling:
  test_sample_size: 300
  calibration_sample_size: 50
  stratification_method: "violation_type"
  violation_types: ["harmful_content", "misinformation", "instruction_violation"]
  samples_per_type: 100
  calibration_stratified: true
  randomize_per_annotator: true
  seed: 42
```

**Rationale for Non-Standard Values:**
- `test_sample_size: 300` - Reduced from h-e1's 500 for focused consistency study
- `calibration_sample_size: 50` - Sufficient for training validation (Cohen's κ estimation)
- `stratification_method: "violation_type"` - Uses h-e1 taxonomy instead of length quartiles

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-1-1 | Violation-Type Stratification | Implement stratified sampling by h-e1 violation taxonomy |
| M-1-2 | Calibration Set Creation | Create disjoint 50-sample calibration set with gold labels |

---

## M-2: Training Protocol Configuration

**Complexity:** 10/20, **Budget:** Implementation managed within M-2 epic

### Configuration Parameters

```yaml
training:
  guidelines_source: "Bai et al. 2022 (HH-RLHF paper)"
  guidelines_path: "./training_materials/hhrlhf_guidelines.yaml"
  presentation_duration_min: 30
  calibration_threshold_kappa: 0.60
  calibration_gold_labels_path: "./data/calibration_gold_labels.csv"
```

**Rationale:**
- `calibration_threshold_kappa: 0.60` - Minimum for moderate agreement (Landis & Koch), gate condition for proceeding to main annotation
- `presentation_duration_min: 30` - Standard guideline presentation time

---

## Configuration Usage Examples

### In Main Experiment Runner

```python
from typing import Dict, Any
import yaml

def run_h_m1_experiment(config_path: str = "config.yaml") -> Dict:
    """Main experiment orchestration."""
    config = load_config(config_path)
    
    # Access training config
    calibration_threshold = config["training"]["calibration_threshold_kappa"]
    guidelines_path = config["training"]["guidelines_path"]
    
    # Access sampling config
    test_size = config["sampling"]["test_sample_size"]
    calibration_size = config["sampling"]["calibration_sample_size"]
    violation_types = config["sampling"]["violation_types"]
    
    # Access gate conditions
    primary_gate = config["gates"]["primary_kappa_threshold"]
    secondary_gate = config["gates"]["secondary_agreement_threshold"]
    
    # Run pipeline
    # 1. Sample data
    test_samples = stratified_sample_by_violation_type(
        dataset, 
        sample_size=test_size,
        violation_types=violation_types,
        seed=config["experiment"]["seed"]
    )
    
    calibration_samples = create_calibration_set(
        dataset,
        calibration_size=calibration_size,
        seed=config["experiment"]["seed"]
    )
    
    # 2. Run training protocol
    for annotator_id in range(1, config["experiment"]["n_annotators"] + 1):
        calibration_kappa, passed = run_calibration_phase(
            annotator_id, 
            calibration_samples,
            threshold=calibration_threshold
        )
        if not passed:
            raise ValueError(f"Annotator {annotator_id} failed calibration (κ={calibration_kappa:.3f})")
    
    # 3. Collect annotations
    annotations = collect_annotations_with_training(
        test_samples, 
        config["experiment"]["n_annotators"]
    )
    
    # 4. Compute agreement
    avg_kappa = compute_pairwise_kappa(annotations)
    avg_agreement = compute_agreement_with_original(annotations)
    
    # 5. Gate decision
    gate_passed = (
        avg_kappa >= primary_gate and 
        avg_agreement >= secondary_gate
    )
    
    return {"gate_passed": gate_passed, "kappa": avg_kappa, "agreement": avg_agreement}
```

### In Training Protocol Module

```python
def run_calibration_phase(
    annotator_id: int,
    calibration_samples: pd.DataFrame,
    threshold: float
) -> Tuple[float, bool]:
    """
    Run calibration and check gate.
    
    Args:
        annotator_id: Annotator ID
        calibration_samples: 50 calibration samples
        threshold: Minimum κ for passing (from config)
    
    Returns:
        (calibration_kappa, passed_gate)
    """
    config = load_config()
    gold_labels = pd.read_csv(config["training"]["calibration_gold_labels_path"])
    
    # Collect calibration annotations
    calibration_annotations = collect_annotations_batch(
        calibration_samples, 
        annotator_id
    )
    
    # Calculate agreement with gold standard
    from sklearn.metrics import cohen_kappa_score
    kappa = cohen_kappa_score(
        gold_labels["label"], 
        calibration_annotations["judgment"]
    )
    
    passed = kappa >= threshold
    return kappa, passed
```

---

## Reproducibility Configuration

### Random Seed Management

```yaml
experiment:
  seed: 42
```

**Usage:**
```python
import random
import numpy as np

seed = config["experiment"]["seed"]
random.seed(seed)
np.random.seed(seed)

# Per-annotator randomization
for annotator_id in range(1, n_annotators + 1):
    annotator_seed = seed + annotator_id
    np.random.seed(annotator_seed)
    randomized_samples = samples.sample(frac=1.0, random_state=annotator_seed)
```

---

## Output Paths Configuration

### Directory Structure

```
h-m1/
├── data/
│   ├── hh_rlhf_test_samples.csv          # 300 test samples
│   ├── hh_rlhf_calibration.csv           # 50 calibration samples
│   ├── calibration_gold_labels.csv       # Gold labels for calibration
│   ├── calibration_results.csv           # Calibration annotations
│   └── annotations.csv                   # Main annotations (3 × 300)
├── outputs/
│   ├── figures/
│   │   ├── gate_metrics.png
│   │   ├── inter_annotator_matrix.png
│   │   ├── agreement_distribution.png
│   │   └── confusion_matrices.png
│   ├── results.json
│   └── report.md
├── training_materials/
│   └── hhrlhf_guidelines.yaml            # Annotation guidelines
└── config.yaml
```

### Path Resolution

```python
from pathlib import Path

def resolve_output_paths(config: Dict[str, Any]) -> Dict[str, Path]:
    """Resolve all output paths from config."""
    outputs = config["outputs"]
    
    paths = {
        "data_dir": Path(outputs["data_dir"]),
        "figures_dir": Path(outputs["figures_dir"]),
        "results_file": Path(outputs["results_file"]),
        "report_file": Path(outputs["report_file"]),
        "test_samples_file": Path(outputs["data_dir"]) / outputs["test_samples_file"],
        "calibration_samples_file": Path(outputs["data_dir"]) / outputs["calibration_samples_file"],
        "calibration_results_file": Path(outputs["data_dir"]) / outputs["calibration_results_file"],
        "annotations_file": Path(outputs["data_dir"]) / outputs["annotations_file"]
    }
    
    # Create directories
    paths["data_dir"].mkdir(parents=True, exist_ok=True)
    paths["figures_dir"].mkdir(parents=True, exist_ok=True)
    
    return paths
```

---

## Configuration Differences from h-e1

### New Parameters (h-m1 specific)

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `training.calibration_threshold_kappa` | 0.60 | Gate for proceeding to main annotation |
| `training.guidelines_path` | path | HH-RLHF annotation guidelines |
| `gates.primary_kappa_threshold` | 0.70 | Substantial agreement target |
| `gates.secondary_agreement_threshold` | 0.75 | Agreement with original labels |
| `baseline_comparison.h_e1_kappa` | 0.498 | Baseline from h-e1 for comparison |

### Modified Parameters

| Parameter | h-e1 | h-m1 | Reason |
|-----------|------|------|--------|
| `sample_size` | 500 | 300 (test) + 50 (calibration) | Focused consistency study |
| `stratification` | length_quartile | violation_type | Uses h-e1 taxonomy |
| `hypothesis_test.threshold` | 0.40 | 0.70 (κ) | Different metric (agreement vs base-rate) |

---

## Configuration Validation

### Basic Sanity Checks

```python
def validate_config(config: Dict[str, Any]) -> None:
    """Basic config validation for h-m1."""
    # Required sections
    assert "experiment" in config
    assert "training" in config
    assert "sampling" in config
    assert "gates" in config
    
    # Sample sizes
    assert config["experiment"]["test_sample_size"] > 0
    assert config["experiment"]["calibration_sample_size"] > 0
    assert config["experiment"]["n_annotators"] == 3
    
    # Training thresholds
    assert 0 < config["training"]["calibration_threshold_kappa"] <= 1
    
    # Gate thresholds
    assert 0 < config["gates"]["primary_kappa_threshold"] <= 1
    assert 0 < config["gates"]["secondary_agreement_threshold"] <= 1
    
    # Stratification
    assert len(config["sampling"]["violation_types"]) == 3
    assert config["sampling"]["samples_per_type"] * 3 == config["experiment"]["test_sample_size"]
    
    print("✓ Configuration validated")
```

---

## Dependencies Summary

### Configuration Dependencies

```python
import yaml         # Config file parsing
from pathlib import Path  # Path resolution
from typing import Dict, Any, Tuple  # Type hints
```

**No additional config libraries needed** for LIGHT tier (same as h-e1).

---

## Self-Validation Checklist

### Quick Checks
- [x] ONE format only (Hardcoded YAML - consistent with h-e1)
- [x] No ASCII diagrams
- [x] Codebase Analysis (Serena) section included
- [x] Applied: KB-003-MinimalConfig noted
- [x] Rationale only for non-standard values
- [x] Subtask count within budget (2/2 used for M-1)
- [x] Total length < 400 lines
- [x] Inherited Configuration section included with verified field names

### Base Hypothesis Checks
- [x] Read actual config from h-e1/code/config.yaml
- [x] Field names verified from actual implementation (YAML dict keys)
- [x] Default values match actual base config
- [x] Extended configuration clearly separated from inherited

### Serena MCP Validation
- [x] Base hypothesis exists → Config verified from h-e1 code
- [x] Codebase Analysis section included with findings

---

**Document Status:** COMPLETE  
**Next Phase:** Phase 4 Implementation  
**Applied Patterns:** KB-003-MinimalConfig, LIGHT-tier YAML configuration  
**Base Hypothesis:** h-e1 (config structure verified and extended)
