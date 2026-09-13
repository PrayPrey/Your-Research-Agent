# Configuration Specification: h-m1 Hessian Outlier Concentration

**Hypothesis ID:** h-m1  
**Type:** MECHANISM (Step 1 of 4)  
**Infrastructure:** FULL (YAML config + dataclass, structured logging)  
**Date:** 2026-04-24  
**Configuration Agent:** Autonomous  
**Prerequisites:** h-e1 (COMPLETED ✅)

---

## Codebase Analysis (Serena)

**Project Type**: Incremental (extends h-e1)  
**Status**: Building on h-e1 config patterns  
**Analyzed Path**: `../h-e1/code/config.py`  
**Base Hypothesis:** h-e1

**Config Pattern from h-e1:**
- h-e1 used hardcoded dict (LIGHT tier)
- h-m1 upgrades to YAML + dataclass (FULL tier)
- Reuse h-e1 values where applicable

**Inherited Configuration Values from h-e1:**
```python
# From h-e1 CONFIG dict
SEED = 42
BATCH_SIZE = 128
NUM_EIGENTHINGS = 100
POWER_ITER_STEPS = 20
MP_FIT_RANGE = (20, 80)
```

---

## Applied Patterns

Applied: YAML + Dataclass Pattern (FULL tier)  
Applied: Incremental Hypothesis Config (inherit from baseline)  
Applied: Path-based Config Organization  

---

## Configuration Schema (YAML + Dataclass)

**Format**: YAML file with Python dataclass for validation and type safety.

### config.yaml

```yaml
# h-m1 Configuration
# Extends h-e1 baseline for outlier concentration analysis

project:
  hypothesis_id: h-m1
  hypothesis_type: MECHANISM
  tier: FULL
  base_hypothesis: h-e1

paths:
  # h-e1 dependencies
  h_e1_checkpoints:
    erm: ../h-e1/checkpoints/erm_best.pth
    dro: ../h-e1/checkpoints/dro_best.pth
  
  # h-m1 outputs
  results_dir: ./results/
  figures_dir: ./figures/
  
  # Shared with h-e1
  data_dir: ./data/waterbird_complete95_forest2water2/

reproducibility:
  seed: 42  # Inherit from h-e1

dataset:
  batch_size: 128  # Inherit from h-e1
  num_workers: 4
  num_classes: 2
  num_groups: 4

hessian:
  num_eigenthings: 100  # Inherit from h-e1
  power_iter_steps: 20  # Inherit from h-e1
  batch_size: 32  # Smaller for memory during Hessian computation

marchenko_pastur:
  fit_range:
    start: 20  # Inherit from h-e1
    end: 80    # Inherit from h-e1
  optimization:
    sigma_sq_init: 1.0
    gamma_init: 0.1
    sigma_sq_bounds: [0.01, 10.0]
    gamma_bounds: [0.01, 1.0]

outlier_analysis:
  # NEW for h-m1
  histogram_bins: 20
  spacing_analysis: true
  distribution_plots: true

visualization:
  dpi: 300
  format: png
  colors:
    erm: red
    dro: blue
    bulk_edge: darkred
  alpha: 0.7
  
  figures:
    gate_metric: fig1_outlier_comparison.png
    spectra: fig2_spectra_comparison.png
    distributions: fig3_outlier_distributions.png
    mp_fit_erm: fig4_mp_fit_quality_erm.png
    mp_fit_dro: fig5_mp_fit_quality_dro.png
    decay: fig6_eigenvalue_decay.png

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  log_file: ./logs/h_m1_experiment.log
  csv_outputs:
    outlier_metrics: outlier_metrics.csv
    hessian_stats_erm: hessian_stats_erm.csv
    hessian_stats_dro: hessian_stats_dro.csv
  json_output: comparison_results.json

testing:
  unit_tests: true
  smoke_test: false  # Use full pipeline
```

### config.py (Dataclass Implementation)

```python
"""
h-m1 Configuration Module
YAML-based config with dataclass validation (FULL tier)
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple
import yaml

@dataclass
class ProjectConfig:
    """Project-level configuration"""
    hypothesis_id: str = "h-m1"
    hypothesis_type: str = "MECHANISM"
    tier: str = "FULL"
    base_hypothesis: str = "h-e1"

@dataclass
class PathsConfig:
    """File paths configuration"""
    h_e1_checkpoints: Dict[str, str] = field(default_factory=lambda: {
        'erm': '../h-e1/checkpoints/erm_best.pth',
        'dro': '../h-e1/checkpoints/dro_best.pth'
    })
    results_dir: str = './results/'
    figures_dir: str = './figures/'
    data_dir: str = './data/waterbird_complete95_forest2water2/'
    
    def __post_init__(self):
        """Create directories if they don't exist"""
        Path(self.results_dir).mkdir(parents=True, exist_ok=True)
        Path(self.figures_dir).mkdir(parents=True, exist_ok=True)

@dataclass
class ReproducibilityConfig:
    """Reproducibility settings"""
    seed: int = 42

@dataclass
class DatasetConfig:
    """Dataset configuration"""
    batch_size: int = 128
    num_workers: int = 4
    num_classes: int = 2
    num_groups: int = 4

@dataclass
class HessianConfig:
    """Hessian computation configuration"""
    num_eigenthings: int = 100
    power_iter_steps: int = 20
    batch_size: int = 32

@dataclass
class MarchenkoPasturConfig:
    """Marchenko-Pastur fitting configuration"""
    fit_range: Tuple[int, int] = (20, 80)
    sigma_sq_init: float = 1.0
    gamma_init: float = 0.1
    sigma_sq_bounds: Tuple[float, float] = (0.01, 10.0)
    gamma_bounds: Tuple[float, float] = (0.01, 1.0)

@dataclass
class OutlierAnalysisConfig:
    """Outlier analysis configuration (NEW for h-m1)"""
    histogram_bins: int = 20
    spacing_analysis: bool = True
    distribution_plots: bool = True

@dataclass
class VisualizationConfig:
    """Visualization settings"""
    dpi: int = 300
    format: str = 'png'
    colors: Dict[str, str] = field(default_factory=lambda: {
        'erm': 'red',
        'dro': 'blue',
        'bulk_edge': 'darkred'
    })
    alpha: float = 0.7
    figures: Dict[str, str] = field(default_factory=lambda: {
        'gate_metric': 'fig1_outlier_comparison.png',
        'spectra': 'fig2_spectra_comparison.png',
        'distributions': 'fig3_outlier_distributions.png',
        'mp_fit_erm': 'fig4_mp_fit_quality_erm.png',
        'mp_fit_dro': 'fig5_mp_fit_quality_dro.png',
        'decay': 'fig6_eigenvalue_decay.png'
    })

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = 'INFO'
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = './logs/h_m1_experiment.log'
    csv_outputs: Dict[str, str] = field(default_factory=lambda: {
        'outlier_metrics': 'outlier_metrics.csv',
        'hessian_stats_erm': 'hessian_stats_erm.csv',
        'hessian_stats_dro': 'hessian_stats_dro.csv'
    })
    json_output: str = 'comparison_results.json'

@dataclass
class TestingConfig:
    """Testing configuration"""
    unit_tests: bool = True
    smoke_test: bool = False

@dataclass
class H_M1_Config:
    """Complete h-m1 configuration"""
    project: ProjectConfig = field(default_factory=ProjectConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    reproducibility: ReproducibilityConfig = field(default_factory=ReproducibilityConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    hessian: HessianConfig = field(default_factory=HessianConfig)
    marchenko_pastur: MarchenkoPasturConfig = field(default_factory=MarchenkoPasturConfig)
    outlier_analysis: OutlierAnalysisConfig = field(default_factory=OutlierAnalysisConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    testing: TestingConfig = field(default_factory=TestingConfig)
    
    @classmethod
    def from_yaml(cls, yaml_path: str = 'config.yaml') -> 'H_M1_Config':
        """Load configuration from YAML file"""
        with open(yaml_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        return cls(
            project=ProjectConfig(**config_dict.get('project', {})),
            paths=PathsConfig(**config_dict.get('paths', {})),
            reproducibility=ReproducibilityConfig(**config_dict.get('reproducibility', {})),
            dataset=DatasetConfig(**config_dict.get('dataset', {})),
            hessian=HessianConfig(**config_dict.get('hessian', {})),
            marchenko_pastur=MarchenkoPasturConfig(
                fit_range=tuple(config_dict.get('marchenko_pastur', {}).get('fit_range', {}).values()),
                **{k: v for k, v in config_dict.get('marchenko_pastur', {}).get('optimization', {}).items()}
            ),
            outlier_analysis=OutlierAnalysisConfig(**config_dict.get('outlier_analysis', {})),
            visualization=VisualizationConfig(**config_dict.get('visualization', {})),
            logging=LoggingConfig(**config_dict.get('logging', {})),
            testing=TestingConfig(**config_dict.get('testing', {}))
        )
    
    def to_yaml(self, yaml_path: str = 'config.yaml'):
        """Save configuration to YAML file"""
        # Convert dataclass to dict for YAML serialization
        # (Implementation omitted for brevity)
        pass

# Load default configuration
config = H_M1_Config.from_yaml()
```

---

## Configuration Usage Example

```python
# run_h_m1_experiment.py

import torch
import numpy as np
import random
import logging
from pathlib import Path
from config import H_M1_Config

def setup_environment(config: H_M1_Config):
    """Setup experiment environment"""
    # Set random seeds
    seed = config.reproducibility.seed
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    
    # Setup logging
    Path(config.logging.log_file).parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, config.logging.level),
        format=config.logging.format,
        handlers=[
            logging.FileHandler(config.logging.log_file),
            logging.StreamHandler()
        ]
    )
    
    # Create output directories
    Path(config.paths.results_dir).mkdir(parents=True, exist_ok=True)
    Path(config.paths.figures_dir).mkdir(parents=True, exist_ok=True)
    
    # Verify h-e1 dependencies
    erm_ckpt = Path(config.paths.h_e1_checkpoints['erm'])
    dro_ckpt = Path(config.paths.h_e1_checkpoints['dro'])
    assert erm_ckpt.exists(), f"h-e1 ERM checkpoint not found: {erm_ckpt}"
    assert dro_ckpt.exists(), f"h-e1 DRO checkpoint not found: {dro_ckpt}"
    
    logging.info(f"Environment setup complete (seed={seed})")

def main():
    # Load configuration
    config = H_M1_Config.from_yaml('config.yaml')
    
    # Setup environment
    setup_environment(config)
    
    # Run experiment with config
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logging.info(f"Using device: {device}")
    
    # ... (experiment code using config parameters)

if __name__ == '__main__':
    main()
```

---

## Inherited Configuration (from h-e1)

| Parameter | h-e1 Value | h-m1 Value | Rationale |
|-----------|------------|------------|-----------|
| seed | 42 | 42 | Same seed for reproducibility |
| batch_size | 128 | 128 | Same training batch size |
| num_eigenthings | 100 | 100 | Same Hessian computation |
| power_iter_steps | 20 | 20 | Same convergence criteria |
| mp_fit_range | (20, 80) | (20, 80) | Same bulk edge fitting |
| data_dir | waterbirds path | waterbirds path | Same dataset |

---

## New Configuration (h-m1 specific)

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| histogram_bins | 20 | Sufficient resolution for outlier distribution analysis |
| spacing_analysis | true | Enable gap analysis between consecutive outliers |
| distribution_plots | true | Generate outlier distribution visualizations |
| tier | FULL | MECHANISM hypothesis requires structured logging and testing |

---

## Hyperparameter Rationale

**Non-Standard Values Only**:

- **histogram_bins=20**: Balances resolution (distinguish outlier magnitudes) with statistical stability (sufficient samples per bin). Too few bins (e.g., 5) lose detail; too many (e.g., 50) become noisy with limited outliers.
  
- **hessian.batch_size=32**: Smaller than training batch_size (128) to reduce GPU memory during Hessian-vector products. Hessian computation is memory-intensive (~2x model memory), so smaller batches prevent OOM.

- **mp_fit_range=(20, 80)**: Inherited from h-e1, but worth noting: Excludes top 20 (obvious outliers) and bottom 20 (noise) eigenvalues to fit bulk distribution cleanly. This range provides 60 bulk eigenvalues for stable parameter estimation.

---

## File Output Structure

```
h-m1/
├── config.yaml                        # YAML configuration
├── code/
│   └── config.py                      # Dataclass implementation
├── logs/
│   └── h_m1_experiment.log            # Structured logging
├── results/
│   ├── outlier_metrics.csv
│   ├── hessian_stats_erm.csv
│   ├── hessian_stats_dro.csv
│   └── comparison_results.json
└── figures/
    ├── fig1_outlier_comparison.png    (GATE METRIC)
    ├── fig2_spectra_comparison.png
    ├── fig3_outlier_distributions.png
    ├── fig4_mp_fit_quality_erm.png
    ├── fig5_mp_fit_quality_dro.png
    └── fig6_eigenvalue_decay.png
```

---

## Environment Variables (Optional Override)

```bash
# GPU selection (set before running experiment)
export CUDA_VISIBLE_DEVICES=0

# Optional: Override config path
export H_M1_CONFIG_PATH=/path/to/custom/config.yaml

# Optional: Override results directory
export H_M1_RESULTS_DIR=/path/to/custom/results/
```

---

## Configuration Validation

```python
def validate_config(config: H_M1_Config):
    """Validate configuration before experiment"""
    
    # Verify h-e1 dependencies
    assert Path(config.paths.h_e1_checkpoints['erm']).exists(), \
        "h-e1 ERM checkpoint missing"
    assert Path(config.paths.h_e1_checkpoints['dro']).exists(), \
        "h-e1 DRO checkpoint missing"
    assert Path(config.paths.data_dir).exists(), \
        "Waterbirds dataset missing"
    
    # Verify Hessian config
    assert config.hessian.num_eigenthings == 100, \
        "Must match h-e1 (100 eigenthings)"
    assert config.hessian.power_iter_steps == 20, \
        "Must match h-e1 (20 power iterations)"
    
    # Verify MP config
    assert config.marchenko_pastur.fit_range == (20, 80), \
        "Must match h-e1 fit range"
    
    # Verify reproducibility
    assert config.reproducibility.seed == 42, \
        "Must match h-e1 seed for reproducibility"
    
    print("✓ Configuration validation passed")
```

---

## Self-Validation Checklist

- [x] YAML + Dataclass format (FULL tier)
- [x] No ASCII diagrams
- [x] Rationale only for non-standard values
- [x] Codebase Analysis section included
- [x] Inherited configuration documented
- [x] New configuration clearly marked
- [x] Total length < 400 lines
- [x] Configuration usage example included

---

*Configuration designed for Phase 4 Implementation | h-m1 MECHANISM Hypothesis | Extends h-e1 baseline | FULL tier infrastructure*
