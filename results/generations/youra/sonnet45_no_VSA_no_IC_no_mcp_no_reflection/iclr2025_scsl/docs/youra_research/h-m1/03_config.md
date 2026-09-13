# Configuration Design: h-m1 Layer-Neuron Consistency Analysis

**Date:** 2026-08-29  
**Hypothesis:** h-m1 (MECHANISM)  
**Author:** Configuration Agent  
**Input:** 03_architecture.md, 03_prd.md

---

## Applied: Dataclass Configuration Pattern

**Source:** Python dataclass for type-safe experiment configuration  
**Pattern:** Hierarchical config with data/model/analysis/output sections  
**Justification:** h-m1 is analysis-only (no training) → simplified config vs h-e1

---

## Configuration Schema

### Dataclass Definition

```python
from dataclasses import dataclass, field
from typing import List, Tuple
from pathlib import Path

@dataclass
class DataConfig:
    """CMNIST dataset configuration (reused from h-e1)."""
    dataset_name: str = "CMNIST"
    data_path: Path = Path("./data/mnist")
    download: bool = True  # Auto-download if missing
    batch_size: int = 256  # Same as h-e1
    num_workers: int = 4
    
    # Spurious feature
    spurious_feature: str = "color"  # Color corruption (0-9)
    spurious_train_correlation: float = 0.95
    spurious_test_correlation: float = 0.10

@dataclass
class ModelConfig:
    """ResNet-18 model configuration (loaded from h-e1)."""
    architecture: str = "resnet18"
    num_classes: int = 10
    pretrained: bool = False  # h-e1 trained from scratch
    
    # h-e1 checkpoint
    checkpoint_path: Path = Path("../h-e1/checkpoints/baseline_seed0.pt")
    checkpoint_key: str = "model_state_dict"  # Verified from h-e1
    
    # Layers to analyze
    layer_names: List[str] = field(default_factory=lambda: [
        'conv1', 'layer1', 'layer2', 'layer3', 'layer4'
    ])

@dataclass
class AnalysisConfig:
    """Layer-neuron correlation analysis configuration."""
    # Statistical test
    alpha: float = 0.05  # Significance threshold
    test_type: str = "one_sided"  # alternative='greater'
    
    # Layer grouping
    early_layers: List[str] = field(default_factory=lambda: ['conv1', 'layer1'])
    late_layers: List[str] = field(default_factory=lambda: ['layer3', 'layer4'])
    
    # Correlation method
    correlation_method: str = "pearson"  # scipy.stats.pearsonr
    
    # Visualization
    max_neurons_heatmap: int = 100  # Subsample if >100 neurons/layer
    figure_dpi: int = 300
    cdf_bins: int = 50

@dataclass
class OutputConfig:
    """Output paths and formats."""
    output_folder: Path = Path("./docs/youra_research/h-m1")
    figures_folder: Path = Path("./docs/youra_research/h-m1/figures")
    
    # Output files
    validation_report: str = "04_validation.md"
    
    # Figure filenames
    bar_chart: str = "layer_correlation_means.png"
    heatmap: str = "neuron_correlation_heatmap.png"
    cdf_plot: str = "correlation_cdf.png"

@dataclass
class ExperimentConfig:
    """Top-level experiment configuration."""
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    
    # Reproducibility
    seed: int = 0  # Match h-e1 seed
    device: str = "cuda"  # Assume GPU available
```

---

## YAML Configuration File

```yaml
# config.yaml for h-m1

experiment:
  name: "h-m1-layer-neuron-consistency"
  hypothesis_id: "h-m1"
  hypothesis_type: "MECHANISM"
  prerequisite: "h-e1"

data:
  dataset_name: "CMNIST"
  data_path: "./data/mnist"
  download: true
  batch_size: 256
  num_workers: 4
  spurious_feature: "color"
  spurious_train_correlation: 0.95
  spurious_test_correlation: 0.10

model:
  architecture: "resnet18"
  num_classes: 10
  pretrained: false
  checkpoint_path: "../h-e1/checkpoints/baseline_seed0.pt"
  checkpoint_key: "model_state_dict"
  layer_names:
    - conv1
    - layer1
    - layer2
    - layer3
    - layer4

analysis:
  alpha: 0.05
  test_type: "one_sided"
  early_layers:
    - conv1
    - layer1
  late_layers:
    - layer3
    - layer4
  correlation_method: "pearson"
  max_neurons_heatmap: 100
  figure_dpi: 300
  cdf_bins: 50

output:
  output_folder: "./docs/youra_research/h-m1"
  figures_folder: "./docs/youra_research/h-m1/figures"
  validation_report: "04_validation.md"
  bar_chart: "layer_correlation_means.png"
  heatmap: "neuron_correlation_heatmap.png"
  cdf_plot: "correlation_cdf.png"

reproducibility:
  seed: 0
  device: "cuda"
```

---

## Inherited Configuration (from h-e1)

### Verified Fields from h-e1 Code

**Data Loading:**
```python
# h-e1 used these exact values (verified from checkpoint metadata)
batch_size: 256  # Same batch size for consistency
data_path: "./data/mnist"  # Shared dataset location
```

**Model Architecture:**
```python
# h-e1 checkpoint format (verified from saved file)
checkpoint = torch.load(path)
# Keys: 'model_state_dict', 'epoch', 'optimizer_state_dict'
# Note: Use 'model_state_dict' key (not 'state_dict')
```

**Spurious Feature Mapping:**
```python
# h-e1 color corruption (10 colors mapped to digits)
# Train: 95% correlation, Test: 10% correlation
# h-m1 reuses same mapping for spurious label extraction
spurious_train_correlation: 0.95
spurious_test_correlation: 0.10
```

---

## Environment Configuration

### requirements.txt

```txt
# Core dependencies
torch>=1.9.0
torchvision>=0.10.0
numpy>=1.21.0

# Statistical analysis
scipy>=1.7.0

# Visualization
matplotlib>=3.3.0
seaborn>=0.11.0

# Utilities
pyyaml>=5.4
```

### Environment Setup Script

```python
# setup_env.py
import subprocess
import sys
from pathlib import Path

def setup_environment():
    """Install dependencies and verify h-e1 checkpoint exists."""
    
    # Install packages
    print("Installing dependencies...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
    ])
    
    # Verify h-e1 checkpoint
    checkpoint_path = Path("../h-e1/checkpoints/baseline_seed0.pt")
    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"h-e1 checkpoint not found at {checkpoint_path}. "
            f"Run h-e1 validation first."
        )
    
    print("✓ Environment ready")
    print(f"✓ h-e1 checkpoint verified: {checkpoint_path}")

if __name__ == "__main__":
    setup_environment()
```

---

## Configuration Loading Utility

```python
# config_loader.py
import yaml
from pathlib import Path
from typing import Dict, Any

def load_config(config_path: str = "config.yaml") -> ExperimentConfig:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to YAML config file
    
    Returns:
        config: ExperimentConfig dataclass instance
    
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config is malformed
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    # Convert to dataclass
    config = ExperimentConfig(
        data=DataConfig(**config_dict['data']),
        model=ModelConfig(**config_dict['model']),
        analysis=AnalysisConfig(**config_dict['analysis']),
        output=OutputConfig(**config_dict['output'])
    )
    
    # Override with reproducibility settings
    config.seed = config_dict['reproducibility']['seed']
    config.device = config_dict['reproducibility']['device']
    
    return config

def validate_config(config: ExperimentConfig) -> None:
    """
    Validate configuration values.
    
    Args:
        config: Loaded configuration
    
    Raises:
        ValueError: If any config value is invalid
    """
    # Check paths exist
    if not config.model.checkpoint_path.exists():
        raise ValueError(f"Checkpoint not found: {config.model.checkpoint_path}")
    
    # Check alpha in valid range
    if not 0 < config.analysis.alpha < 1:
        raise ValueError(f"alpha must be in (0, 1), got {config.analysis.alpha}")
    
    # Check layer groups are disjoint
    early = set(config.analysis.early_layers)
    late = set(config.analysis.late_layers)
    if early & late:
        raise ValueError("Early and late layer groups must be disjoint")
    
    print("✓ Configuration validated")
```

---

## Hyperparameter Defaults

### Analysis Parameters

| Parameter | Value | Justification |
|-----------|-------|---------------|
| `alpha` | 0.05 | Standard significance threshold |
| `test_type` | "one_sided" | Directional hypothesis (early > late) |
| `correlation_method` | "pearson" | Linear correlation measure |
| `max_neurons_heatmap` | 100 | Visualization clarity (subsample if needed) |
| `figure_dpi` | 300 | Publication-quality figures |

### Data Parameters

| Parameter | Value | Justification |
|-----------|-------|---------------|
| `batch_size` | 256 | Same as h-e1 (consistency) |
| `num_workers` | 4 | Standard parallel data loading |
| `spurious_test_correlation` | 0.10 | CMNIST standard (counter-correlated test) |

### Path Parameters

| Parameter | Value | Justification |
|-----------|-------|---------------|
| `checkpoint_path` | "../h-e1/checkpoints/baseline_seed0.pt" | Relative to h-m1/code/ folder |
| `data_path` | "./data/mnist" | Shared with h-e1 (project root) |
| `figures_folder` | "./docs/youra_research/h-m1/figures" | Hypothesis-specific output |

---

## Subtask Breakdown (3 subtasks)

### Subtask 5.1: Visualization Config
- Implement figure_dpi, max_neurons_heatmap settings
- Test: Verify PNG output quality

### Subtask 7.1: Report Template Config
- Implement validation_report path and section headers
- Test: Verify markdown formatting

### Subtask 2.1: Data Loader Config
- Implement batch_size, num_workers, spurious_feature settings
- Test: Verify dataloader initialization

---

## Usage Example

```python
# analyze_layers.py (main script)
from config_loader import load_config, validate_config
from layer_analyzer import LayerNeuronAnalyzer
from visualize import plot_layer_means, plot_heatmap, plot_cdf
from report_generator import generate_validation_report

def main():
    # Load configuration
    config = load_config("config.yaml")
    validate_config(config)
    
    # Set random seed
    torch.manual_seed(config.seed)
    np.random.seed(config.seed)
    
    # Load model from h-e1
    model = load_h_e1_model(config.model.checkpoint_path)
    model = model.to(config.device)
    
    # Create analyzer
    analyzer = LayerNeuronAnalyzer(model, config.model.layer_names)
    
    # Load data
    dataloader = get_dataloader(config.data)
    spurious_labels = get_spurious_labels(dataloader.dataset)
    
    # Run analysis
    layer_rho_j = analyzer.compute_layer_correlations(dataloader, spurious_labels)
    t_stat, p_value, layer_means = analyzer.test_layer_consistency(layer_rho_j)
    
    # Generate visualizations
    config.output.figures_folder.mkdir(exist_ok=True)
    plot_layer_means(
        layer_means, layer_rho_j,
        config.output.figures_folder / config.output.bar_chart
    )
    plot_heatmap(
        layer_rho_j,
        config.output.figures_folder / config.output.heatmap,
        config.analysis.max_neurons_heatmap
    )
    plot_cdf(
        layer_rho_j,
        config.output.figures_folder / config.output.cdf_plot
    )
    
    # Generate report
    generate_validation_report(
        t_stat, p_value, layer_means, layer_rho_j,
        config.output.output_folder / config.output.validation_report
    )
    
    print(f"✓ Analysis complete. Gate: {'PASS' if p_value < config.analysis.alpha else 'FAIL'}")

if __name__ == "__main__":
    main()
```

---

**Version:** 1.0  
**Status:** Ready for Complexity Assessment
