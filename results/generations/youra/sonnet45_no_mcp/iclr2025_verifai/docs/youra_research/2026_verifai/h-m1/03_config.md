# Configuration Design: h-m1

**Date:** 2026-04-20  
**Hypothesis ID:** h-m1  
**Type:** MECHANISM (Causal)  
**Config Designer:** Phase 3 Orchestrator  
**Budget:** 4 subtasks  
**Base Hypothesis:** h-e1

Applied: Configuration inheritance pattern - reuse h-e1 settings with minimal overrides

---

## Inherited Configuration

### From h-e1 (Verified Fields)

All h-e1 configuration settings are reused without modification:

```python
from h_e1.code.config import ExperimentConfig

# h-e1 configuration (inherited)
@dataclass
class H_E1_Config:
    # Dataset
    dataset_name: str = "LeanDojo"
    sample_size: int = 100
    random_seed: int = 42
    
    # Model
    model_name: str = "ReProver"
    model_path: str = "lean-dojo/ReProver"
    
    # Experiment
    timeout_seconds: int = 300
    confidence_window: int = 15
    max_steps: int = 30
    
    # Output
    results_dir: str = "h-e1/results"
    figures_dir: str = "h-e1/figures"
```

**Reuse Level:** 100% - All settings identical

---

## H-M1 Specific Configuration

### Configuration Schema (YAML)

```yaml
# h-m1/config.yaml
experiment:
  hypothesis_id: "h-m1"
  type: "MECHANISM"
  base_hypothesis: "h-e1"
  
  # INHERITED: All dataset and model settings from h-e1
  inherit_from: "../h-e1/config.yaml"
  
  # H-M1 SPECIFIC: Analysis settings
  analysis:
    metric: "variance"  # vs h-e1's "derivative"
    analysis_type: "group_comparison"  # vs h-e1's "correlation"
    gate_condition: "mean_variance(success) < mean_variance(timeout)"
  
  # H-M1 SPECIFIC: Reuse optimization
  reuse_h_e1_results: true
  h_e1_results_path: "../h-e1/results/confidence_trajectories.pkl"
  
  # Output paths (h-m1 specific)
  output:
    results_dir: "h-m1/results"
    figures_dir: "h-m1/figures"
    analysis_file: "variance_analysis.json"
    group_comparison_file: "group_comparison.json"

# Visualization settings (extended from h-e1)
visualization:
  # INHERITED: matplotlib style, DPI, colors from h-e1
  
  # H-M1 SPECIFIC: Group comparison plots
  plots:
    variance_comparison_bar:
      enabled: true  # MANDATORY
      title: "Mean Confidence Variance by Outcome"
      xlabel: "Proof Outcome"
      ylabel: "Mean Variance (std dev of entropy)"
      colors: ["#2ecc71", "#e74c3c"]  # success=green, timeout=red
    
    variance_distributions:
      enabled: true  # RECOMMENDED
      bins: 20
      alpha: 0.6
      overlay: true
    
    variance_boxplot:
      enabled: true  # RECOMMENDED
      showfliers: true
      notch: false
    
    trajectory_examples:
      enabled: true  # RECOMMENDED
      num_examples: 5  # per group
      stable_color: "#3498db"
      unstable_color: "#e67e22"
```

### Configuration Dataclass (Python)

```python
from dataclasses import dataclass, field
from typing import Dict, Optional
from h_e1.code.config import ExperimentConfig as H_E1_Config

@dataclass
class H_M1_Config(H_E1_Config):
    """
    H-M1 configuration extending h-e1 settings.
    
    Inherits all dataset, model, and experiment settings from h-e1.
    Adds h-m1 specific analysis and visualization config.
    """
    
    # H-M1 Identity
    hypothesis_id: str = "h-m1"
    experiment_type: str = "MECHANISM"
    base_hypothesis: str = "h-e1"
    
    # Analysis Settings (H-M1 SPECIFIC)
    metric: str = "variance"
    analysis_type: str = "group_comparison"
    gate_condition: str = "mean_variance(success) < mean_variance(timeout)"
    
    # Result Reuse (H-M1 OPTIMIZATION)
    reuse_h_e1_results: bool = True
    h_e1_results_path: str = "../h-e1/results/confidence_trajectories.pkl"
    
    # Output Paths (OVERRIDE h-e1 paths)
    results_dir: str = "h-m1/results"
    figures_dir: str = "h-m1/figures"
    analysis_file: str = "variance_analysis.json"
    group_comparison_file: str = "group_comparison.json"
    
    # Visualization Config (H-M1 SPECIFIC)
    plot_variance_bar: bool = True  # MANDATORY
    plot_variance_dist: bool = True  # RECOMMENDED
    plot_variance_boxplot: bool = True  # RECOMMENDED
    plot_trajectory_examples: bool = True  # RECOMMENDED
    trajectory_examples_per_group: int = 5
    
    # Group Comparison Colors
    success_color: str = "#2ecc71"  # Green
    timeout_color: str = "#e74c3c"  # Red
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        # Verify h-e1 results path if reuse enabled
        if self.reuse_h_e1_results:
            import os
            if not os.path.exists(self.h_e1_results_path):
                print(f"Warning: h-e1 results not found at {self.h_e1_results_path}")
                print("Will fall back to running experiments from scratch")
                self.reuse_h_e1_results = False
        
        # Create output directories
        import os
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.figures_dir, exist_ok=True)
```

---

## Configuration Loading

### Default Configuration

```python
# h-m1/code/config.py
from dataclasses import dataclass
from h_e1.code.config import ExperimentConfig as H_E1_Config

@dataclass
class H_M1_Config(H_E1_Config):
    """See dataclass definition above."""
    pass

# Default instance
DEFAULT_CONFIG = H_M1_Config()
```

### Configuration from File

```python
import yaml
from h_m1.code.config import H_M1_Config

def load_config(config_path: str = "h-m1/config.yaml") -> H_M1_Config:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config.yaml
    
    Returns:
        config: H_M1_Config instance
    """
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    # Flatten nested dict for dataclass
    flat_config = {
        'hypothesis_id': config_dict['experiment']['hypothesis_id'],
        'experiment_type': config_dict['experiment']['type'],
        'metric': config_dict['experiment']['analysis']['metric'],
        'analysis_type': config_dict['experiment']['analysis']['analysis_type'],
        'reuse_h_e1_results': config_dict['experiment']['reuse_h_e1_results'],
        'h_e1_results_path': config_dict['experiment']['h_e1_results_path'],
        'results_dir': config_dict['experiment']['output']['results_dir'],
        'figures_dir': config_dict['experiment']['output']['figures_dir'],
        # ... etc
    }
    
    return H_M1_Config(**flat_config)
```

---

## Hyperparameter Comparison

### h-e1 vs h-m1

| Hyperparameter | h-e1 | h-m1 | Changed? |
|----------------|------|------|----------|
| dataset_name | LeanDojo | LeanDojo | ✗ |
| sample_size | 100 | 100 | ✗ |
| random_seed | 42 | 42 | ✗ |
| model_name | ReProver | ReProver | ✗ |
| timeout_seconds | 300 | 300 | ✗ |
| confidence_window | 15 | 15 | ✗ |
| **metric** | derivative | **variance** | ✓ (renamed) |
| **analysis_type** | correlation | **group_comparison** | ✓ |
| results_dir | h-e1/results | h-m1/results | ✓ (path only) |

**Key Insight:** Only analysis logic changes; all experimental settings identical.

---

## Environment Variables

### Optional Overrides

```bash
# Override h-e1 result reuse
export H_M1_REUSE_H_E1=false

# Override output directory
export H_M1_RESULTS_DIR=/path/to/custom/results

# Override visualization settings
export H_M1_PLOT_ALL=true
```

### Usage in Code

```python
import os

config = H_M1_Config()

# Apply environment overrides
if os.getenv('H_M1_REUSE_H_E1'):
    config.reuse_h_e1_results = os.getenv('H_M1_REUSE_H_E1').lower() == 'true'

if os.getenv('H_M1_RESULTS_DIR'):
    config.results_dir = os.getenv('H_M1_RESULTS_DIR')
```

---

## Configuration Validation

### Validation Rules

```python
def validate_config(config: H_M1_Config) -> None:
    """
    Validate h-m1 configuration.
    
    Raises:
        ValueError: If configuration is invalid
    """
    # Inherited from h-e1
    assert config.sample_size == 100, "Must use same 100 theorems as h-e1"
    assert config.random_seed == 42, "Must use same seed as h-e1"
    assert config.timeout_seconds == 300, "Must use same timeout as h-e1"
    assert config.confidence_window == 15, "Must use same window as h-e1"
    
    # H-M1 specific
    assert config.metric == "variance", "h-m1 uses variance metric"
    assert config.analysis_type == "group_comparison", "h-m1 uses group comparison"
    
    # Output paths
    assert config.results_dir != config.h_e1_results_path, "h-m1 output must be separate from h-e1"
    
    print("✓ Configuration validated")
```

---

## Configuration Examples

### Example 1: Default (Reuse h-e1 results)

```python
config = H_M1_Config()
# Uses all defaults:
# - Reuses h-e1 results (fast)
# - All plots enabled
# - Default colors and settings
```

### Example 2: Run from Scratch

```python
config = H_M1_Config(
    reuse_h_e1_results=False  # Re-run experiments
)
# Disables h-e1 reuse, runs new experiments
```

### Example 3: Minimal Visualization

```python
config = H_M1_Config(
    plot_variance_bar=True,  # MANDATORY
    plot_variance_dist=False,  # Skip
    plot_variance_boxplot=False,  # Skip
    plot_trajectory_examples=False  # Skip
)
# Only generates mandatory bar chart
```

---

## Dependencies Configuration

### Python Packages (Inherited from h-e1)

```yaml
dependencies:
  # From h-e1 (no changes)
  - lean_dojo>=1.0
  - numpy>=1.20
  - scipy>=1.7
  - matplotlib>=3.3
  - seaborn>=0.11
  
  # H-M1 specific (minimal)
  - pyyaml>=5.4  # For config.yaml loading
```

### Installation

```bash
# Reuse h-e1 environment
cd h-m1
pip install -r requirements.txt  # Same as h-e1 + pyyaml
```

---

## Configuration File Locations

```
h-m1/
├── config.yaml                 # Primary config file
├── code/
│   └── config.py              # Config dataclass
└── configs/                   # Optional variants
    ├── minimal.yaml           # Minimal visualization
    └── debug.yaml             # Debug settings
```

---

## Notes

**Configuration Philosophy:** Maximize inheritance from h-e1 to ensure controlled comparison. Only override what's necessary for h-m1's group analysis approach.

**Validation Strategy:** Runtime validation ensures h-m1 doesn't accidentally deviate from h-e1's validated experimental setup (same data, model, timeout).

**Optimization Toggle:** `reuse_h_e1_results` flag enables fast execution by reusing h-e1's confidence trajectories, reducing runtime from hours to minutes.
