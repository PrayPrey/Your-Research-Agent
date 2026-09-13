# Configuration Schema: h-m3

**Date:** 2026-07-12
**Hypothesis:** h-m3 (MECHANISM - Stratified Correlation Comparison)
**Type:** MECHANISM
**Author:** Configuration Agent

---

## Applied Patterns

**Archon KB:**
- Applied: Statistical hypothesis testing workflow (scipy.stats)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config classes verified from h-m1 base code
**Config Files Found:** h-m1/code/src/config.py
**Pattern Used:** dataclass

**Verified from:** `/workspace/TEST_buildingtrust/docs/youra_research/h-m1/code/` (actual implementation)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

H-M3 reuses file paths and output patterns from h-m1. No dataclass configs are inherited since h-m1 used hardcoded parameters in main().

```python
# H-M1 used hardcoded values in run_experiment.py:
# - threshold_r=0.3 (correlation threshold)
# - threshold_p=0.05 (p-value threshold)
# - threshold_ci=0.2 (confidence interval threshold)
# - max_samples_per_stratum from env var
# - model_size from env var

# H-M3 extends with Fisher z-test parameters
```

**Critical Path Verified:**
- H-M1 outputs: `outputs/results.csv` with columns: `stratum,r,p_value,ci_lower,ci_upper,n`
- H-M1 figures: `figures/gate_metrics_comparison.png`, `figures/stratification_comparison.png`

---

## C-1: Cached Data Loading [Complexity: 6, Budget: 3]

**Applied:** Standard file I/O with pandas defaults

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
import os

@dataclass
class DataLoaderConfig:
    h_m1_output_path: str = os.path.join("docs", "youra_research", "h-m1", "code", "outputs", "results.csv")
    required_columns: list = None
    factual_stratum_label: str = "factual"
    misinfo_stratum_label: str = "misinformation"
    min_sample_size: int = 10
    
    def __post_init__(self):
        if self.required_columns is None:
            self.required_columns = ["stratum", "r", "p_value", "ci_lower", "ci_upper", "n"]
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | CSV loading | Load results.csv from h-m1 outputs |
| C-1-2 | Data validation | Verify required columns and sample sizes |
| C-1-3 | Stratum extraction | Extract factual and misinformation correlation results |

---

## C-4: Effect Size Calculation [Complexity: 7, Budget: 3]

**Applied:** Standard Cohen's q and Fisher z-transform

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class EffectSizeConfig:
    confidence_level: float = 0.95
    effect_size_thresholds: dict = None
    
    def __post_init__(self):
        if self.effect_size_thresholds is None:
            self.effect_size_thresholds = {
                "small": 0.1,
                "medium": 0.3,
                "large": 0.5
            }
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Cohen's q computation | Compute q = z1 - z2 for correlation difference |
| C-4-2 | CI computation | Compute 95% CI using Fisher z back-transform |
| C-4-3 | Effect magnitude classification | Classify effect size as small/medium/large |

---

## C-7: Validation Report Generation [Complexity: 8, Budget: 3]

**Applied:** Standard markdown report generation

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
import os

@dataclass
class ReportConfig:
    validation_report_path: str = "04_validation.md"
    results_json_path: str = "fisher_test_results.json"
    figures_references: list = None
    
    def __post_init__(self):
        if self.figures_references is None:
            self.figures_references = [
                "gate_metrics_comparison.png",
                "forest_plot.png",
                "scatter_comparison.png"
            ]
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Statistics table formatting | Format Fisher test results as markdown table |
| C-7-2 | Gate evaluation formatting | Write SHOULD_WORK gate evaluation section |
| C-7-3 | JSON results serialization | Save complete results to JSON |

---

## Master Configuration

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
import os

@dataclass
class FisherTestConfig:
    """Fisher z-test parameters"""
    alpha: float = 0.05
    confidence_level: float = 0.95
    p_threshold: float = 0.05
    delta_r_threshold: float = 0.1

@dataclass
class GateConfig:
    """SHOULD_WORK gate thresholds"""
    factual_r_threshold: float = 0.4
    misinfo_r_threshold: float = 0.3
    p_threshold: float = 0.05
    delta_r_threshold: float = 0.1

@dataclass
class VisualizationConfig:
    """Figure generation settings"""
    figure_format: str = "png"
    dpi: int = 300
    figsize_gate: tuple = (8, 6)
    figsize_forest: tuple = (10, 6)
    figsize_scatter: tuple = (12, 5)
    style: str = "seaborn-v0_8-darkgrid"
    colors: dict = None
    
    def __post_init__(self):
        if self.colors is None:
            self.colors = {
                "factual": "steelblue",
                "misinfo": "coral",
                "threshold": "red"
            }

@dataclass
class ExperimentConfig:
    """Main configuration for h-m3 Fisher z-test experiment"""
    
    # Sub-configurations
    data_loader: DataLoaderConfig = field(default_factory=DataLoaderConfig)
    fisher_test: FisherTestConfig = field(default_factory=FisherTestConfig)
    effect_size: EffectSizeConfig = field(default_factory=EffectSizeConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    report: ReportConfig = field(default_factory=ReportConfig)
    
    # Output paths
    output_dir: str = "outputs"
    figures_dir: str = "figures"
    
    def __post_init__(self):
        """Create output directories on initialization"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.figures_dir, exist_ok=True)
    
    def validate(self) -> bool:
        """Validate configuration completeness"""
        # Check h-m1 results file exists
        if not os.path.exists(self.data_loader.h_m1_output_path):
            print(f"Error: H-M1 results not found at {self.data_loader.h_m1_output_path}")
            return False
        
        # Validate thresholds
        if self.fisher_test.alpha <= 0 or self.fisher_test.alpha >= 1:
            print("Error: alpha must be between 0 and 1")
            return False
        
        if self.fisher_test.confidence_level <= 0 or self.fisher_test.confidence_level >= 1:
            print("Error: confidence_level must be between 0 and 1")
            return False
        
        return True

def load_config() -> ExperimentConfig:
    """Load and validate experiment configuration"""
    config = ExperimentConfig()
    
    if not config.validate():
        raise ValueError("Configuration validation failed")
    
    return config
```

---

## Usage Example

```python
from src.config import load_config

# Load validated configuration
config = load_config()

# Access Fisher test parameters
print(f"Alpha: {config.fisher_test.alpha}")
print(f"Confidence level: {config.fisher_test.confidence_level}")

# Access gate thresholds
print(f"p-value threshold: {config.gate.p_threshold}")
print(f"Delta r threshold: {config.gate.delta_r_threshold}")

# Access file paths
print(f"H-M1 results path: {config.data_loader.h_m1_output_path}")
print(f"Output directory: {config.output_dir}")

# Pass to components
loader = CachedResultsLoader(config.data_loader)
fisher_test = FisherZTest(alpha=config.fisher_test.alpha)
validator = MechanismGateValidator(
    p_threshold=config.gate.p_threshold,
    delta_r_threshold=config.gate.delta_r_threshold
)
visualizer = ComparisonVisualizer(
    output_dir=config.figures_dir,
    viz_config=config.visualization
)
```

---

## Gate Validation Logic

```python
def validate_should_work_gate(
    fisher_result: dict,
    r_factual: float,
    r_misinfo: float,
    gate_config: GateConfig
) -> dict:
    """
    Validate SHOULD_WORK gate criteria:
    1. Fisher z-test p < 0.05
    2. |r_factual - r_misinfo| >= 0.1
    3. r_factual > 0.4 AND r_misinfo < 0.3
    
    Args:
        fisher_result: Dict with 'p_value' from Fisher test
        r_factual: Correlation from factual stratum
        r_misinfo: Correlation from misinformation stratum
        gate_config: GateConfig with thresholds
    
    Returns:
        dict with gate result and individual checks
    """
    primary = fisher_result["p_value"] < gate_config.p_threshold
    secondary = abs(r_factual - r_misinfo) >= gate_config.delta_r_threshold
    tertiary = (r_factual > gate_config.factual_r_threshold) and \
               (r_misinfo < gate_config.misinfo_r_threshold)
    
    gate_passed = primary and secondary and tertiary
    
    return {
        "gate_result": "PASS" if gate_passed else "FAIL",
        "gate_type": "SHOULD_WORK",
        "checks": {
            "primary_p_value": primary,
            "secondary_delta_r": secondary,
            "tertiary_directional": tertiary
        },
        "criteria": {
            "p_threshold": gate_config.p_threshold,
            "delta_r_threshold": gate_config.delta_r_threshold,
            "factual_r_threshold": gate_config.factual_r_threshold,
            "misinfo_r_threshold": gate_config.misinfo_r_threshold
        },
        "observed": {
            "p_value": fisher_result["p_value"],
            "delta_r": abs(r_factual - r_misinfo),
            "r_factual": r_factual,
            "r_misinfo": r_misinfo
        }
    }
```

---

## Rationale for Non-Standard Values

**Gate Thresholds:**
- `factual_r_threshold=0.4`: Hypothesis specifies strong coupling on factual prompts
- `misinfo_r_threshold=0.3`: Hypothesis specifies weak coupling on misinformation prompts
- `delta_r_threshold=0.1`: Minimum effect size for meaningful difference (10% correlation difference)

**Visualization:**
- `figsize_scatter=(12, 5)`: Side-by-side scatter plots require wider canvas
- Color scheme matches h-m1 for consistency (steelblue for factual, coral for misinfo)

All statistical defaults (alpha=0.05, confidence=0.95) follow standard conventions.

---

## Environment Variables

No environment variables required. All paths are relative or computed from project structure.

---

## Configuration File Location

Save as: `h-m3/code/src/config.py`

This configuration provides:
- Fisher z-test statistical parameters (alpha, confidence level)
- SHOULD_WORK gate validation thresholds
- File paths for h-m1 cached results and h-m3 outputs
- Visualization settings for 3 mandatory figures
- Report generation configuration

**Subtask Budget:** 9/9 used across 3 tasks (C-1, C-4, C-7)

---

**Document Status:** FINAL
**Last Updated:** 2026-07-12
**Next Phase:** Phase 4 - Implementation (Coder Agent)
