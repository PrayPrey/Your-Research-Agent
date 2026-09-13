# Configuration Design
# Hypothesis: H-E1 - Base-Rate Validation Study

**Version:** 1.0  
**Date:** 2026-04-19  
**Hypothesis ID:** h-e1  
**Infrastructure Level:** Minimal (LIGHT tier)

---

## Configuration Philosophy

**Applied:** LIGHT-tier minimal configuration pattern (KB-003-MinimalConfig)

**Approach:** Hardcoded YAML configuration file with fixed parameters (no environment variables, no multi-environment support for LIGHT tier)

---

## 1. Configuration File Structure

### 1.1 Main Configuration (`config.yaml`)

```yaml
# Experiment Configuration for H-E1
# Base-Rate Validation Study

experiment:
  name: "h-e1-base-rate-validation"
  hypothesis_id: "h-e1"
  description: "Human annotation study to validate base-rate of genuine safety violations in HH-RLHF rejected responses"
  seed: 42
  
sampling:
  sample_size: 500
  stratification_column: "length_quartile"
  n_quartiles: 4
  samples_per_quartile: 125  # 500 / 4
  
annotation:
  n_annotators: 3
  violation_criteria:
    - "Direct harm/violence encouragement"
    - "Toxic/offensive language"
    - "Privacy violations or personal information disclosure"
    - "Dangerous/illegal advice"
    - "Deception or misinformation"
    - "Other safety policy violations"
  
dataset:
  name: "Anthropic/hh-rlhf"
  subset: "harmless-base"
  split: "train"
  cache_dir: "./cache/datasets"
  
hypothesis_test:
  null_hypothesis_threshold: 0.40
  alpha: 0.05
  alternative: "greater"  # One-tailed test (H1: p >= 0.40)
  confidence_level: 0.95
  
statistical_analysis:
  kappa_threshold: 0.75  # Substantial agreement target
  kappa_interpretation:
    poor: [0.00, 0.20]
    slight: [0.21, 0.40]
    fair: [0.41, 0.60]
    moderate: [0.61, 0.75]
    substantial: [0.76, 1.00]
  
outputs:
  data_dir: "./data"
  figures_dir: "./outputs/figures"
  results_file: "./outputs/results.json"
  report_file: "./outputs/report.md"
  
  # File naming
  samples_file: "hh_rlhf_samples.csv"
  annotations_file: "annotations.csv"
  final_labels_file: "final_labels.csv"
  
logging:
  level: "INFO"  # Print-based logging for LIGHT tier
  format: "simple"  # No structured logging
```

---

## 2. Configuration Loading

### 2.1 Config Loader (`src/config.py`)

**Note:** For LIGHT tier, config loading is minimal (no validation, no environment overrides)

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

## 3. Hyperparameters & Default Values

### 3.1 Sampling Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `sample_size` | 500 | Total samples to draw from HH-RLHF |
| `seed` | 42 | Random seed for reproducibility |
| `n_quartiles` | 4 | Number of length strata |
| `samples_per_quartile` | 125 | Samples per stratum (balanced) |

### 3.2 Annotation Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `n_annotators` | 3 | Number of independent annotators |
| `violation_criteria` | List[6] | Checklist of safety violation types |

### 3.3 Statistical Test Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `null_hypothesis_threshold` | 0.40 | H0: p < 0.40 threshold |
| `alpha` | 0.05 | Significance level |
| `alternative` | "greater" | One-tailed test direction |
| `confidence_level` | 0.95 | CI confidence level |

### 3.4 Agreement Thresholds

| Parameter | Default | Description |
|-----------|---------|-------------|
| `kappa_threshold` | 0.75 | Target for substantial agreement |
| `kappa_interpretation` | Dict | Landis & Koch interpretation ranges |

---

## 4. Output Paths Configuration

### 4.1 Directory Structure

```
h-e1/
├── data/                           # Data directory
│   ├── hh_rlhf_samples.csv        # Sampled 500 responses
│   ├── annotations.csv            # Annotation results
│   └── final_labels.csv           # Majority vote labels
├── outputs/                        # Results directory
│   ├── figures/                   # Visualizations
│   │   ├── base_rate.png
│   │   ├── agreement_heatmap.png
│   │   ├── violation_types.png
│   │   └── length_bias.png
│   ├── results.json               # Statistical results
│   └── report.md                  # Summary report
└── cache/                          # HuggingFace cache
    └── datasets/
```

### 4.2 Path Resolution

```python
from pathlib import Path

def resolve_output_paths(config: Dict[str, Any]) -> Dict[str, Path]:
    """
    Resolve all output paths from config.
    
    Args:
        config: Loaded configuration dict
    
    Returns:
        Dict mapping output names to Path objects
    """
    outputs = config["outputs"]
    
    paths = {
        "data_dir": Path(outputs["data_dir"]),
        "figures_dir": Path(outputs["figures_dir"]),
        "results_file": Path(outputs["results_file"]),
        "report_file": Path(outputs["report_file"]),
        "samples_file": Path(outputs["data_dir"]) / outputs["samples_file"],
        "annotations_file": Path(outputs["data_dir"]) / outputs["annotations_file"],
        "final_labels_file": Path(outputs["data_dir"]) / outputs["final_labels_file"]
    }
    
    # Create directories if not exist
    paths["data_dir"].mkdir(parents=True, exist_ok=True)
    paths["figures_dir"].mkdir(parents=True, exist_ok=True)
    
    return paths
```

---

## 5. No Advanced Configuration Features (LIGHT Tier)

### 5.1 Features NOT Included

❌ **Environment Variables:** All config in YAML file  
❌ **Multi-Environment Support:** No dev/staging/prod configs  
❌ **Dynamic Configuration:** No runtime overrides  
❌ **Configuration Validation:** No schema validation (pydantic, cerberus)  
❌ **Secret Management:** No secrets (public dataset only)  
❌ **Feature Flags:** No conditional execution  
❌ **Experiment Tracking:** No WandB/MLflow integration

### 5.2 Rationale

LIGHT tier infrastructure prioritizes simplicity:
- Single hardcoded config file
- No complex config management
- Easy to understand and modify
- Appropriate for PoC validation study

---

## 6. Configuration Usage Examples

### 6.1 In Main Experiment Runner

```python
# src/main.py
from config import load_config, resolve_output_paths

def run_experiment():
    # Load config
    config = load_config("config.yaml")
    paths = resolve_output_paths(config)
    
    # Use config parameters
    seed = config["experiment"]["seed"]
    sample_size = config["sampling"]["sample_size"]
    
    # Run sampling
    samples = stratified_sample(dataset, sample_size=sample_size, seed=seed)
    samples.to_csv(paths["samples_file"])
    
    # Run hypothesis test
    p_null = config["hypothesis_test"]["null_hypothesis_threshold"]
    alpha = config["hypothesis_test"]["alpha"]
    p_value, decision = binomial_test(n_violations, n_trials=500, p_null=p_null, alpha=alpha)
    
    # Save results
    results = {"base_rate": base_rate, "p_value": p_value, "decision": decision}
    with open(paths["results_file"], "w") as f:
        json.dump(results, f, indent=2)
```

### 6.2 In Visualization Module

```python
# src/visualization/plots.py
from config import load_config, resolve_output_paths

def generate_all_plots(samples, annotations, final_labels, results):
    config = load_config()
    paths = resolve_output_paths(config)
    
    # Use config for plot parameters
    threshold = config["hypothesis_test"]["null_hypothesis_threshold"]
    
    # Generate plots
    plot_base_rate_comparison(
        base_rate=results["base_rate"],
        threshold=threshold,
        p_value=results["p_value"],
        output_path=paths["figures_dir"] / "base_rate.png"
    )
```

---

## 7. Reproducibility Configuration

### 7.1 Random Seed Management

**Fixed seed for reproducibility:**
```yaml
experiment:
  seed: 42  # Used for all random operations
```

**Usage:**
```python
import random
import numpy as np

# Set all seeds
seed = config["experiment"]["seed"]
random.seed(seed)
np.random.seed(seed)
```

### 7.2 Dataset Versioning

**HuggingFace dataset snapshot:**
```yaml
dataset:
  name: "Anthropic/hh-rlhf"
  subset: "harmless-base"
  revision: null  # Use latest version (no pinning for LIGHT tier)
```

**Note:** For LIGHT tier, we use the latest dataset version. For production studies, pin `revision` to a specific commit hash.

---

## 8. Annotation Guidelines Configuration

### 8.1 Violation Criteria Checklist

```yaml
annotation:
  violation_criteria:
    - id: "V1"
      label: "Direct harm/violence encouragement"
      description: "Response encourages physical harm, violence, or self-harm"
      
    - id: "V2"
      label: "Toxic/offensive language"
      description: "Response contains hate speech, slurs, or offensive content"
      
    - id: "V3"
      label: "Privacy violations"
      description: "Response discloses personal information or violates privacy"
      
    - id: "V4"
      label: "Dangerous/illegal advice"
      description: "Response provides dangerous or illegal instructions"
      
    - id: "V5"
      label: "Deception or misinformation"
      description: "Response intentionally misleads or provides false information"
      
    - id: "V6"
      label: "Other safety policy violations"
      description: "Response violates other safety policies not covered above"
```

**Note:** For LIGHT tier, we use simplified list format. Full schema above is for reference only.

---

## 9. Statistical Analysis Configuration

### 9.1 Cohen's Kappa Interpretation

```yaml
statistical_analysis:
  kappa_interpretation:
    poor: [0.00, 0.20]      # < 0.20
    slight: [0.21, 0.40]    # 0.21-0.40
    fair: [0.41, 0.60]      # 0.41-0.60
    moderate: [0.61, 0.75]  # 0.61-0.75
    substantial: [0.76, 1.00]  # ≥ 0.76
```

**Usage:**
```python
def interpret_kappa(kappa: float, config: Dict) -> str:
    """Return kappa interpretation label."""
    interp = config["statistical_analysis"]["kappa_interpretation"]
    
    if kappa < interp["poor"][1]:
        return "poor"
    elif kappa < interp["slight"][1]:
        return "slight"
    elif kappa < interp["fair"][1]:
        return "fair"
    elif kappa < interp["moderate"][1]:
        return "moderate"
    else:
        return "substantial"
```

---

## 10. Logging Configuration (Minimal)

### 10.1 Print-Based Logging

**LIGHT tier approach:** Simple print statements (no structured logging)

```python
def log(message: str, level: str = "INFO"):
    """Simple print-based logging for LIGHT tier."""
    print(f"[{level}] {message}")

# Usage in main.py
log("Starting stratified sampling...", "INFO")
log(f"Base-rate: {base_rate:.3f}", "INFO")
log(f"Gate decision: {'PASS' if decision else 'FAIL'}", "INFO")
```

**No logging library needed** (no `logging`, `loguru`, `structlog` for LIGHT tier)

---

## 11. Configuration Checklist

### 11.1 Required Configuration Items

✅ Experiment metadata (name, hypothesis_id, seed)  
✅ Sampling parameters (sample_size, stratification)  
✅ Annotation parameters (n_annotators, criteria)  
✅ Dataset specification (name, subset, split)  
✅ Hypothesis test parameters (threshold, alpha)  
✅ Output paths (data, figures, results)

### 11.2 Optional Configuration Items

❌ Environment variables (not used in LIGHT tier)  
❌ Multi-environment configs (not needed for PoC)  
❌ Logging configuration (print-based only)  
❌ Secret management (no secrets in this study)

---

## 12. Configuration Validation (Minimal)

### 12.1 Basic Sanity Checks

```python
def validate_config(config: Dict[str, Any]) -> None:
    """
    Basic config validation for LIGHT tier.
    
    Args:
        config: Loaded configuration dict
    
    Raises:
        AssertionError: If config is invalid
    """
    # Check required keys exist
    assert "experiment" in config
    assert "sampling" in config
    assert "annotation" in config
    assert "hypothesis_test" in config
    
    # Check sample size is positive
    assert config["sampling"]["sample_size"] > 0
    
    # Check n_annotators is 3 (required for this study)
    assert config["annotation"]["n_annotators"] == 3
    
    # Check alpha is valid
    assert 0 < config["hypothesis_test"]["alpha"] < 1
    
    print("✓ Configuration validated")
```

**Note:** No schema validation library (pydantic, cerberus) for LIGHT tier.

---

## 13. Dependencies Summary

### 13.1 Configuration Dependencies

```python
import yaml         # Config file parsing
from pathlib import Path  # Path resolution
from typing import Dict, Any  # Type hints
```

**No additional config libraries needed** for LIGHT tier.

---

## 14. Testing Guidance

### 14.1 Configuration Tests

**test_config.py:**
```python
def test_load_config():
    """Test config loading from YAML."""
    config = load_config("config.yaml")
    assert config["experiment"]["name"] == "h-e1-base-rate-validation"
    assert config["sampling"]["sample_size"] == 500

def test_resolve_output_paths():
    """Test path resolution."""
    config = load_config("config.yaml")
    paths = resolve_output_paths(config)
    assert paths["data_dir"].name == "data"
    assert paths["figures_dir"].name == "figures"

def test_config_validation():
    """Test config validation."""
    config = load_config("config.yaml")
    validate_config(config)  # Should not raise
```

---

## 15. Configuration Migration Notes

### 15.1 No Migration Needed

**Context:** This is a green-field implementation (no base hypothesis, no existing config)

**Applied:** LIGHT-tier minimal configuration from scratch

---

**Document Status:** COMPLETE  
**Next Phase:** Task Generation (03_tasks.yaml)  
**Applied Patterns:** KB-003-MinimalConfig, LIGHT-tier hardcoded YAML approach
