# Configuration Design: h-m2

**Date:** 2026-04-20  
**Hypothesis ID:** h-m2  
**Type:** MECHANISM (Causal)  
**Config Designer:** Phase 3 Orchestrator  
**Budget:** 4 subtasks  
**Base Hypothesis:** h-m1

Applied: Configuration inheritance pattern - reuse h-m1 settings with divergence analysis extensions

---

## Inherited Configuration

### From h-m1 (Verified Fields)

All h-m1 configuration settings are reused without modification:

```python
from h_m1.code.config import H_M1_Config

# h-m1 configuration (inherited)
@dataclass
class H_M1_Config:
    # Dataset (from h-e1)
    dataset_name: str = "LeanDojo"
    sample_size: int = 100
    random_seed: int = 42
    
    # Model (from h-e1)
    model_name: str = "ReProver"
    model_path: str = "lean-dojo/ReProver"
    
    # Experiment (from h-e1)
    timeout_seconds: int = 300
    confidence_window: int = 15
    max_steps: int = 30
    
    # Analysis (h-m1 specific)
    metric: str = "variance"
    analysis_type: str = "group_comparison"
    
    # Output
    results_dir: str = "h-m1/results"
    figures_dir: str = "h-m1/figures"
```

**Reuse Level:** 100% - All experimental settings identical

---

## H-M2 Specific Configuration

### Configuration Schema (YAML)

```yaml
# h-m2/config.yaml
experiment:
  hypothesis_id: "h-m2"
  type: "MECHANISM"
  base_hypothesis: "h-m1"
  
  # INHERITED: All dataset, model, and experiment settings from h-m1
  inherit_from: "../h-m1/config.yaml"
  
  # H-M2 SPECIFIC: Divergence analysis settings
  analysis:
    metric: "variance"  # Same as h-m1 (inherited)
    analysis_type: "timeout_subgroup_comparison"  # NEW: divergent vs difficult
    subgroup_classification: "divergence"  # NEW: classification method
    gate_condition: "mean_variance(divergent) > mean_variance(difficult)"
  
  # H-M2 SPECIFIC: Divergence classification thresholds
  divergence_detection:
    collision_threshold: 2  # Min state hash collisions for divergence
    backtrack_threshold: 5  # Min backtrack events for divergence
    classification_rule: "OR"  # collisions > threshold OR backtracks > threshold
  
  # H-M2 SPECIFIC: Search tree tracking
  tree_tracking:
    enabled: true
    capture_state_sequence: true
    capture_branching_points: true
    capture_backtrack_events: true
  
  # H-M2 SPECIFIC: Reuse optimization
  reuse_h_m1_results: true
  h_m1_results_path: "../h-m1/results/experiment_results.pkl"
  rerun_timeout_group_only: true  # Efficiency: only re-run timeouts for tree tracking
  
  # Output paths (h-m2 specific)
  output:
    results_dir: "h-m2/results"
    figures_dir: "h-m2/figures"
    divergence_classification_file: "divergence_classification.json"
    timeout_subgroup_analysis_file: "timeout_subgroup_analysis.json"
    markers_data_file: "divergence_markers.csv"

# Visualization settings (extended from h-m1)
visualization:
  # INHERITED: matplotlib style, DPI, colors from h-m1
  
  # H-M2 SPECIFIC: Divergence analysis plots
  plots:
    timeout_subgroup_comparison_bar:
      enabled: true  # MANDATORY
      title: "Mean Confidence Variance: Divergent vs Difficult Timeouts"
      xlabel: "Timeout Classification"
      ylabel: "Mean Variance (std dev of entropy)"
      colors: ["#e74c3c", "#f39c12"]  # divergent=red, difficult=orange
    
    variance_by_divergence_boxplot:
      enabled: true  # RECOMMENDED
      title: "Variance Distribution by Divergence Type"
      showfliers: true
      notch: false
      colors: ["#e74c3c", "#f39c12"]
    
    divergence_marker_scatter:
      enabled: true  # RECOMMENDED
      plots:
        collision_vs_variance:
          xlabel: "State Collisions"
          ylabel: "Confidence Variance"
          title: "State Collisions vs Confidence Variance"
        backtrack_vs_variance:
          xlabel: "Backtrack Frequency"
          ylabel: "Confidence Variance"
          title: "Backtrack Frequency vs Confidence Variance"
      marker_size: 50
      alpha: 0.6
    
    divergence_classification_pie:
      enabled: true  # RECOMMENDED
      title: "Timeout Classification: Divergent vs Difficult"
      colors: ["#e74c3c", "#f39c12"]
      explode: [0.05, 0]  # Emphasize divergent slice
    
    trajectory_examples:
      enabled: true  # RECOMMENDED
      num_examples: 3  # per subgroup
      divergent_color: "#e74c3c"
      difficult_color: "#f39c12"
      plot_markers: true  # Show collision/backtrack events
```

### Configuration Dataclass (Python)

```python
from dataclasses import dataclass, field
from typing import Dict, Optional
from h_m1.code.config import H_M1_Config

@dataclass
class H_M2_Config(H_M1_Config):
    """
    H-M2 configuration extending h-m1 settings.
    
    Inherits all dataset, model, and experiment settings from h-m1.
    Adds h-m2 specific divergence detection and subgroup analysis config.
    """
    
    # H-M2 Identity
    hypothesis_id: str = "h-m2"
    experiment_type: str = "MECHANISM"
    base_hypothesis: str = "h-m1"
    
    # Analysis Settings (H-M2 SPECIFIC)
    metric: str = "variance"  # Inherited from h-m1
    analysis_type: str = "timeout_subgroup_comparison"  # NEW
    subgroup_classification: str = "divergence"  # NEW
    gate_condition: str = "mean_variance(divergent) > mean_variance(difficult)"
    
    # Divergence Detection Thresholds (H-M2 SPECIFIC)
    collision_threshold: int = 2  # Min collisions for divergence
    backtrack_threshold: int = 5  # Min backtracks for divergence
    classification_rule: str = "OR"  # OR vs AND logic
    
    # Search Tree Tracking (H-M2 SPECIFIC)
    enable_tree_tracking: bool = True
    capture_state_sequence: bool = True
    capture_branching_points: bool = True
    capture_backtrack_events: bool = True
    
    # Result Reuse (H-M2 OPTIMIZATION)
    reuse_h_m1_results: bool = True
    h_m1_results_path: str = "../h-m1/results/experiment_results.pkl"
    rerun_timeout_group_only: bool = True  # Efficiency optimization
    
    # Output Paths (OVERRIDE h-m1 paths)
    results_dir: str = "h-m2/results"
    figures_dir: str = "h-m2/figures"
    divergence_classification_file: str = "divergence_classification.json"
    timeout_subgroup_analysis_file: str = "timeout_subgroup_analysis.json"
    markers_data_file: str = "divergence_markers.csv"
    
    # Visualization Config (H-M2 SPECIFIC)
    plot_timeout_subgroup_bar: bool = True  # MANDATORY
    plot_variance_boxplot: bool = True  # RECOMMENDED
    plot_divergence_marker_scatter: bool = True  # RECOMMENDED
    plot_divergence_classification_pie: bool = True  # RECOMMENDED
    plot_trajectory_examples: bool = True  # RECOMMENDED
    trajectory_examples_per_subgroup: int = 3
    
    # Subgroup Colors
    divergent_color: str = "#e74c3c"  # Red
    difficult_color: str = "#f39c12"  # Orange
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        # Verify h-m1 results path if reuse enabled
        if self.reuse_h_m1_results:
            import os
            if not os.path.exists(self.h_m1_results_path):
                print(f"Warning: h-m1 results not found at {self.h_m1_results_path}")
                print("Will fall back to running experiments from scratch")
                self.reuse_h_m1_results = False
        
        # Validate divergence thresholds
        assert self.collision_threshold >= 0, "Collision threshold must be non-negative"
        assert self.backtrack_threshold >= 0, "Backtrack threshold must be non-negative"
        assert self.classification_rule in ["OR", "AND"], "Rule must be OR or AND"
        
        # Validate inherited settings match h-m1
        assert self.sample_size == 100, "Must use same 100 theorems as h-m1"
        assert self.random_seed == 42, "Must use same seed as h-m1"
        assert self.timeout_seconds == 300, "Must use same timeout as h-m1"
        assert self.confidence_window == 15, "Must use same window as h-m1"
        
        # Create output directories
        import os
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.figures_dir, exist_ok=True)
        
        print("✓ H-M2 configuration validated")
```

---

## Configuration Loading

### Default Configuration

```python
# h-m2/code/config.py
from dataclasses import dataclass
from h_m1.code.config import H_M1_Config

@dataclass
class H_M2_Config(H_M1_Config):
    """See dataclass definition above."""
    pass

# Default instance
DEFAULT_CONFIG = H_M2_Config()
```

### Configuration from File

```python
import yaml
from h_m2.code.config import H_M2_Config

def load_config(config_path: str = "h-m2/config.yaml") -> H_M2_Config:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config.yaml
    
    Returns:
        config: H_M2_Config instance
    """
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    # Flatten nested dict for dataclass
    flat_config = {
        'hypothesis_id': config_dict['experiment']['hypothesis_id'],
        'experiment_type': config_dict['experiment']['type'],
        'base_hypothesis': config_dict['experiment']['base_hypothesis'],
        'analysis_type': config_dict['experiment']['analysis']['analysis_type'],
        'subgroup_classification': config_dict['experiment']['analysis']['subgroup_classification'],
        'collision_threshold': config_dict['experiment']['divergence_detection']['collision_threshold'],
        'backtrack_threshold': config_dict['experiment']['divergence_detection']['backtrack_threshold'],
        'enable_tree_tracking': config_dict['experiment']['tree_tracking']['enabled'],
        'reuse_h_m1_results': config_dict['experiment']['reuse_h_m1_results'],
        'h_m1_results_path': config_dict['experiment']['h_m1_results_path'],
        'rerun_timeout_group_only': config_dict['experiment']['rerun_timeout_group_only'],
        'results_dir': config_dict['experiment']['output']['results_dir'],
        'figures_dir': config_dict['experiment']['output']['figures_dir'],
        # ... etc
    }
    
    return H_M2_Config(**flat_config)
```

---

## Hyperparameter Comparison

### h-m1 vs h-m2

| Hyperparameter | h-m1 | h-m2 | Changed? |
|----------------|------|------|----------|
| dataset_name | LeanDojo | LeanDojo | ✗ |
| sample_size | 100 | 100 | ✗ |
| random_seed | 42 | 42 | ✗ |
| model_name | ReProver | ReProver | ✗ |
| timeout_seconds | 300 | 300 | ✗ |
| confidence_window | 15 | 15 | ✗ |
| metric | variance | variance | ✗ |
| **analysis_type** | group_comparison | **timeout_subgroup_comparison** | ✓ |
| **tree_tracking** | N/A | **enabled** | ✓ (new) |
| **collision_threshold** | N/A | **2** | ✓ (new) |
| **backtrack_threshold** | N/A | **5** | ✓ (new) |
| results_dir | h-m1/results | h-m2/results | ✓ (path only) |

**Key Insight:** Experimental settings identical; only analysis layer changes (divergence classification + subgroup comparison).

---

## Divergence Detection Configuration

### Threshold Rationale

```yaml
# h-m2/config.yaml - Divergence Detection Thresholds
divergence_detection:
  # State hash collision threshold
  collision_threshold: 2
  # Rationale: At least 2 repeated states indicates cyclic behavior
  # - 0-1 collisions: Normal exploration (may revisit states occasionally)
  # - 2+ collisions: Likely cyclic pattern (divergence marker)
  
  # Backtrack frequency threshold
  backtrack_threshold: 5
  # Rationale: 5+ abandoned branches indicates search instability
  # - 0-4 backtracks: Normal search refinement
  # - 5+ backtracks: High instability (divergence marker)
  
  # Classification rule
  classification_rule: "OR"
  # Rationale: Divergence if EITHER marker exceeds threshold
  # - OR: More sensitive (detects divergence from any signal)
  # - AND: More conservative (requires both markers)
  # - h-m2 uses OR for PoC exploration
```

### Threshold Tuning (Optional)

```python
# Alternative threshold configurations
THRESHOLD_CONFIGS = {
    'conservative': {
        'collision_threshold': 3,
        'backtrack_threshold': 7,
        'classification_rule': 'AND'  # Stricter: both required
    },
    'default': {
        'collision_threshold': 2,
        'backtrack_threshold': 5,
        'classification_rule': 'OR'  # Balanced
    },
    'sensitive': {
        'collision_threshold': 1,
        'backtrack_threshold': 3,
        'classification_rule': 'OR'  # More divergent classifications
    }
}
```

---

## Environment Variables

### Optional Overrides

```bash
# Override h-m1 result reuse
export H_M2_REUSE_H_M1=false

# Override divergence thresholds
export H_M2_COLLISION_THRESHOLD=3
export H_M2_BACKTRACK_THRESHOLD=7

# Override tree tracking
export H_M2_TREE_TRACKING=true

# Override output directory
export H_M2_RESULTS_DIR=/path/to/custom/results
```

### Usage in Code

```python
import os

config = H_M2_Config()

# Apply environment overrides
if os.getenv('H_M2_REUSE_H_M1'):
    config.reuse_h_m1_results = os.getenv('H_M2_REUSE_H_M1').lower() == 'true'

if os.getenv('H_M2_COLLISION_THRESHOLD'):
    config.collision_threshold = int(os.getenv('H_M2_COLLISION_THRESHOLD'))

if os.getenv('H_M2_BACKTRACK_THRESHOLD'):
    config.backtrack_threshold = int(os.getenv('H_M2_BACKTRACK_THRESHOLD'))

if os.getenv('H_M2_RESULTS_DIR'):
    config.results_dir = os.getenv('H_M2_RESULTS_DIR')
```

---

## Configuration Validation

### Validation Rules

```python
def validate_config(config: H_M2_Config) -> None:
    """
    Validate h-m2 configuration.
    
    Raises:
        ValueError: If configuration is invalid
    """
    # Inherited from h-m1 (must match)
    assert config.sample_size == 100, "Must use same 100 theorems as h-m1"
    assert config.random_seed == 42, "Must use same seed as h-m1"
    assert config.timeout_seconds == 300, "Must use same timeout as h-m1"
    assert config.confidence_window == 15, "Must use same window as h-m1"
    assert config.metric == "variance", "Must use same metric as h-m1"
    
    # H-M2 specific
    assert config.analysis_type == "timeout_subgroup_comparison", "h-m2 uses subgroup comparison"
    assert config.enable_tree_tracking == True, "h-m2 requires tree tracking"
    
    # Divergence thresholds
    assert config.collision_threshold >= 0, "Collision threshold must be non-negative"
    assert config.backtrack_threshold >= 0, "Backtrack threshold must be non-negative"
    assert config.classification_rule in ["OR", "AND"], "Rule must be OR or AND"
    
    # At least one threshold must be positive
    assert (config.collision_threshold > 0 or config.backtrack_threshold > 0), \
        "At least one threshold must be positive"
    
    # Output paths
    assert config.results_dir != config.h_m1_results_path, "h-m2 output must be separate from h-m1"
    
    print("✓ H-M2 configuration validated")
```

---

## Configuration Examples

### Example 1: Default (Reuse h-m1, Standard Thresholds)

```python
config = H_M2_Config()
# Uses all defaults:
# - Reuses h-m1 results (fast)
# - collision_threshold=2, backtrack_threshold=5
# - All plots enabled
# - OR classification rule
```

### Example 2: Conservative Thresholds

```python
config = H_M2_Config(
    collision_threshold=3,  # Stricter
    backtrack_threshold=7,  # Stricter
    classification_rule="AND"  # Both required
)
# Fewer divergent classifications (more conservative)
```

### Example 3: Sensitive Detection

```python
config = H_M2_Config(
    collision_threshold=1,  # More sensitive
    backtrack_threshold=3,  # More sensitive
    classification_rule="OR"  # Either sufficient
)
# More divergent classifications (more sensitive)
```

### Example 4: Minimal Visualization

```python
config = H_M2_Config(
    plot_timeout_subgroup_bar=True,  # MANDATORY
    plot_variance_boxplot=False,  # Skip
    plot_divergence_marker_scatter=False,  # Skip
    plot_divergence_classification_pie=False,  # Skip
    plot_trajectory_examples=False  # Skip
)
# Only generates mandatory bar chart
```

### Example 5: Run from Scratch (No h-m1 Reuse)

```python
config = H_M2_Config(
    reuse_h_m1_results=False,  # Re-run all experiments
    rerun_timeout_group_only=False  # Run full 100 theorems
)
# Disables h-m1 reuse, runs all experiments with tree tracking
# (Significantly slower: ~3 hours vs ~30 minutes)
```

---

## Dependencies Configuration

### Python Packages (Inherited from h-m1)

```yaml
dependencies:
  # From h-m1 (no changes)
  - lean_dojo>=1.0
  - numpy>=1.20
  - scipy>=1.7
  - matplotlib>=3.3
  - seaborn>=0.11
  
  # H-M2 specific (minimal)
  - pyyaml>=5.4  # For config.yaml loading
```

### Installation

```bash
# Reuse h-m1 environment
cd h-m2
pip install -r requirements.txt  # Same as h-m1
```

---

## Configuration File Locations

```
h-m2/
├── config.yaml                 # Primary config file
├── code/
│   └── config.py              # Config dataclass
└── configs/                   # Optional variants
    ├── conservative.yaml      # Conservative thresholds
    ├── sensitive.yaml         # Sensitive thresholds
    ├── minimal.yaml           # Minimal visualization
    └── debug.yaml             # Debug settings
```

---

## Notes

**Configuration Philosophy:** Maximize inheritance from h-m1 to ensure controlled comparison. Only add what's necessary for h-m2's divergence detection and subgroup analysis.

**Threshold Justification:** collision_threshold=2 and backtrack_threshold=5 are PoC-level heuristics based on theoretical expectations. Refinement possible in future hypotheses if mechanism validates.

**Optimization Strategy:** `reuse_h_m1_results=True` + `rerun_timeout_group_only=True` enables fast execution by:
1. Reusing h-m1 variance calculations (validated)
2. Re-running ONLY timeout group (~30-40 experiments) for tree tracking
3. Reduces runtime from ~3 hours to ~30-60 minutes

**Validation Strategy:** Runtime validation ensures h-m2 doesn't accidentally deviate from h-m1's validated experimental setup (same data, model, timeout, variance calculation).
