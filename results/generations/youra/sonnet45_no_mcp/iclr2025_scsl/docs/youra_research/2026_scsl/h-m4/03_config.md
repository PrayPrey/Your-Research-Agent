# Configuration Design: H-M4 Geometry-Phenotype Coupling

**Project:** H-M4 Implementation
**Date:** 2026-04-24
**Author:** Configuration Agent
**Hypothesis Type:** MECHANISM (FULL tier)

---

## Applied Patterns

**Applied:** Configuration as Code Pattern (Archon KB)
- YAML for experiment settings
- Python dataclasses for type safety
- Environment variable overrides for flexibility

---

## Configuration Schema

### 1. Experiment Configuration (experiment_config.yaml)

```yaml
# H-M4 Geometry-Phenotype Coupling Experiment Configuration
version: "1.0"
hypothesis_id: "h-m4"

# Experiment metadata
experiment:
  name: "geometry_phenotype_coupling"
  description: "Test functional coupling between A(w) and WGA along mode-connected paths"
  gate_type: "SHOULD_WORK"
  random_seed: 42
  
# Path sampling configuration
path_sampling:
  num_samples: 20  # M=20 checkpoints
  methods:
    - "fge"      # Fast Geometric Ensembling (linear interpolation)
    - "linear"   # Linear interpolation baseline (validation)
  
# Endpoint checkpoints (from h-e1)
checkpoints:
  erm:
    path: "../h-e1/checkpoints/erm_final.pt"
    expected_alignment: 0.72  # From h-e1 validation
    expected_wga: 0.65        # Approximate (60-75% range)
  dro:
    path: "../h-e1/checkpoints/dro_final.pt"
    expected_alignment: 0.32  # From h-e1 validation
    expected_wga: 0.78        # Approximate (75-80% range)
  fallback:
    retrain_if_missing: false  # Document in validation report instead
    
# Model configuration
model:
  architecture: "resnet50"
  num_classes: 2
  pretrained: true  # ImageNet weights
  
# Dataset configuration
dataset:
  name: "waterbirds"
  version: "1.0"
  path: "~/data/waterbirds_v1.0"
  download_if_missing: true
  splits:
    train: 4795
    val: 1199
    test: 5794
  num_groups: 4
  
# Data loading
dataloader:
  batch_size: 128
  num_workers: 4
  shuffle_train: false  # Not training, just evaluation
  shuffle_val: false
  shuffle_test: false
  pin_memory: true
  
# Preprocessing
preprocessing:
  image_size: 224
  normalize:
    mean: [0.485, 0.456, 0.406]
    std: [0.229, 0.224, 0.225]
  augmentation:
    enabled: false  # No augmentation for evaluation
    
# Metrics computation
metrics:
  alignment:
    method: "h-m2"  # Reuse h-m2 implementation
    minority_groups: [1, 3]  # Landbird-water, Waterbird-land
    aggregation: "mean"  # Average over minority groups
  wga:
    groups: [0, 1, 2, 3]  # All 4 groups
    aggregation: "min"    # Worst-group = min
    
# Curvature computation (reuse h-m1, h-m2)
curvature:
  hessian_method: "power_iteration"  # From h-m1
  num_eigenvalues: 100
  marchenko_pastur:
    gamma: 0.1  # Dataset aspect ratio (from h-m1)
    significance_level: 0.01
    
# Correlation analysis
correlation:
  method: "spearman"
  alternative: "two-sided"
  significance_level: 0.01  # p < 0.01 for PASS
  
# Success criteria (SHOULD_WORK gate)
success_criteria:
  primary:
    metric: "fge_rho"
    threshold: -0.6
    comparison: "less_than"  # ρ < -0.6
    p_value_threshold: 0.01
  secondary:
    metric: "linear_rho"
    threshold: -0.7
    comparison: "less_than"
  partial:
    rho_range: [-0.6, -0.3]  # Weak coupling
    
# Visualization
visualization:
  output_dir: "h-m4/figures/"
  format: "png"
  dpi: 300
  plots:
    - type: "coupling_scatter"
      filename: "coupling_scatter.png"
    - type: "trajectory"
      filename: "trajectory_plot.png"
    - type: "comparison"
      filename: "fge_vs_linear.png"
    - type: "group_accuracy"
      filename: "group_accuracy_path.png"
      
# Output configuration
output:
  results_dir: "h-m4/results/"
  validation_report: "h-m4/04_validation.md"
  metrics_file: "h-m4/results/metrics.json"
  checkpoint_file: "h-m4/04_checkpoint.yaml"
  
# Compute configuration
compute:
  device: "cuda"  # Will be set via CUDA_VISIBLE_DEVICES
  mixed_precision: false  # Not needed for evaluation
  
# Logging
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "h-m4/logs/experiment.log"
  console: true
```

---

### 2. Python Dataclass (config.py)

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path

@dataclass
class CheckpointConfig:
    """Checkpoint configuration"""
    path: str
    expected_alignment: float
    expected_wga: float

@dataclass
class PathSamplingConfig:
    """Path sampling configuration"""
    num_samples: int = 20
    methods: List[str] = field(default_factory=lambda: ["fge", "linear"])

@dataclass
class DatasetConfig:
    """Dataset configuration"""
    name: str = "waterbirds"
    version: str = "1.0"
    path: str = "~/data/waterbirds_v1.0"
    download_if_missing: bool = True
    num_groups: int = 4

@dataclass
class DataLoaderConfig:
    """DataLoader configuration"""
    batch_size: int = 128
    num_workers: int = 4
    shuffle_train: bool = False
    shuffle_val: bool = False
    shuffle_test: bool = False
    pin_memory: bool = True

@dataclass
class MetricsConfig:
    """Metrics computation configuration"""
    alignment_method: str = "h-m2"
    minority_groups: List[int] = field(default_factory=lambda: [1, 3])
    alignment_aggregation: str = "mean"
    wga_groups: List[int] = field(default_factory=lambda: [0, 1, 2, 3])
    wga_aggregation: str = "min"

@dataclass
class CorrelationConfig:
    """Correlation analysis configuration"""
    method: str = "spearman"
    alternative: str = "two-sided"
    significance_level: float = 0.01

@dataclass
class SuccessCriteriaConfig:
    """Success criteria for SHOULD_WORK gate"""
    primary_metric: str = "fge_rho"
    primary_threshold: float = -0.6
    primary_comparison: str = "less_than"
    p_value_threshold: float = 0.01
    secondary_metric: str = "linear_rho"
    secondary_threshold: float = -0.7
    partial_rho_range: List[float] = field(default_factory=lambda: [-0.6, -0.3])

@dataclass
class VisualizationConfig:
    """Visualization configuration"""
    output_dir: str = "h-m4/figures/"
    format: str = "png"
    dpi: int = 300
    plots: List[Dict[str, str]] = field(default_factory=list)

@dataclass
class OutputConfig:
    """Output configuration"""
    results_dir: str = "h-m4/results/"
    validation_report: str = "h-m4/04_validation.md"
    metrics_file: str = "h-m4/results/metrics.json"
    checkpoint_file: str = "h-m4/04_checkpoint.yaml"

@dataclass
class ComputeConfig:
    """Compute configuration"""
    device: str = "cuda"
    mixed_precision: bool = False

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "h-m4/logs/experiment.log"
    console: bool = True

@dataclass
class ExperimentConfig:
    """Master experiment configuration"""
    version: str = "1.0"
    hypothesis_id: str = "h-m4"
    name: str = "geometry_phenotype_coupling"
    description: str = "Test functional coupling between A(w) and WGA"
    gate_type: str = "SHOULD_WORK"
    random_seed: int = 42
    
    # Sub-configurations
    path_sampling: PathSamplingConfig = field(default_factory=PathSamplingConfig)
    checkpoints: Dict[str, CheckpointConfig] = field(default_factory=dict)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    dataloader: DataLoaderConfig = field(default_factory=DataLoaderConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    correlation: CorrelationConfig = field(default_factory=CorrelationConfig)
    success_criteria: SuccessCriteriaConfig = field(default_factory=SuccessCriteriaConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    compute: ComputeConfig = field(default_factory=ComputeConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> "ExperimentConfig":
        """Load configuration from YAML file"""
        import yaml
        
        with open(yaml_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        # Parse nested configurations
        path_sampling = PathSamplingConfig(**config_dict.get("path_sampling", {}))
        
        checkpoints = {
            "erm": CheckpointConfig(**config_dict["checkpoints"]["erm"]),
            "dro": CheckpointConfig(**config_dict["checkpoints"]["dro"])
        }
        
        dataset = DatasetConfig(**config_dict.get("dataset", {}))
        dataloader = DataLoaderConfig(**config_dict.get("dataloader", {}))
        metrics = MetricsConfig(
            alignment_method=config_dict["metrics"]["alignment"]["method"],
            minority_groups=config_dict["metrics"]["alignment"]["minority_groups"],
            alignment_aggregation=config_dict["metrics"]["alignment"]["aggregation"],
            wga_groups=config_dict["metrics"]["wga"]["groups"],
            wga_aggregation=config_dict["metrics"]["wga"]["aggregation"]
        )
        correlation = CorrelationConfig(**config_dict.get("correlation", {}))
        success_criteria = SuccessCriteriaConfig(
            primary_metric=config_dict["success_criteria"]["primary"]["metric"],
            primary_threshold=config_dict["success_criteria"]["primary"]["threshold"],
            primary_comparison=config_dict["success_criteria"]["primary"]["comparison"],
            p_value_threshold=config_dict["success_criteria"]["primary"]["p_value_threshold"],
            secondary_metric=config_dict["success_criteria"]["secondary"]["metric"],
            secondary_threshold=config_dict["success_criteria"]["secondary"]["threshold"],
            partial_rho_range=config_dict["success_criteria"]["partial"]["rho_range"]
        )
        visualization = VisualizationConfig(**config_dict.get("visualization", {}))
        output = OutputConfig(**config_dict.get("output", {}))
        compute = ComputeConfig(**config_dict.get("compute", {}))
        logging = LoggingConfig(**config_dict.get("logging", {}))
        
        return cls(
            version=config_dict["version"],
            hypothesis_id=config_dict["hypothesis_id"],
            name=config_dict["experiment"]["name"],
            description=config_dict["experiment"]["description"],
            gate_type=config_dict["experiment"]["gate_type"],
            random_seed=config_dict["experiment"]["random_seed"],
            path_sampling=path_sampling,
            checkpoints=checkpoints,
            dataset=dataset,
            dataloader=dataloader,
            metrics=metrics,
            correlation=correlation,
            success_criteria=success_criteria,
            visualization=visualization,
            output=output,
            compute=compute,
            logging=logging
        )
    
    def validate(self) -> None:
        """Validate configuration parameters"""
        assert self.path_sampling.num_samples > 0, "num_samples must be positive"
        assert self.dataset.num_groups == 4, "Waterbirds has exactly 4 groups"
        assert self.dataloader.batch_size > 0, "batch_size must be positive"
        assert self.correlation.method in ["spearman", "pearson"], "Invalid correlation method"
        assert self.success_criteria.primary_threshold < 0, "Expected negative correlation"
        assert 0 < self.correlation.significance_level < 1, "Invalid significance level"
        assert self.compute.device in ["cuda", "cpu"], "Invalid device"
```

---

### 3. Hyperparameter Defaults

**Path Sampling:**
- `num_samples`: 20 (M=20 checkpoints, from Phase 2C experiment brief)
- Rationale: Sufficient for correlation with good statistical power

**Metrics:**
- `minority_groups`: [1, 3] (landbird-water, waterbird-land)
- Rationale: Consistent with h-m2 (minority alignment validation)

**Correlation:**
- `method`: "spearman" (monotonic coupling, robust to outliers)
- `significance_level`: 0.01 (p < 0.01 for PASS)

**Success Thresholds:**
- `primary_threshold`: -0.6 (strong negative correlation)
- `secondary_threshold`: -0.7 (validation path)
- Rationale: From Phase 2C success criteria

---

### 4. Environment Variables

```bash
# GPU selection
export CUDA_VISIBLE_DEVICES=0  # Use single empty GPU

# Paths
export WATERBIRDS_DATA_PATH="/home/anonymous/data/waterbirds_v1.0"
export H_E1_CHECKPOINTS_PATH="../h-e1/checkpoints"

# Experiment settings
export H_M4_NUM_SAMPLES=20
export H_M4_BATCH_SIZE=128
export H_M4_SEED=42

# Output directories
export H_M4_RESULTS_DIR="h-m4/results"
export H_M4_FIGURES_DIR="h-m4/figures"
```

---

### 5. Logging Configuration

```python
import logging
from pathlib import Path

def setup_logging(config: LoggingConfig) -> logging.Logger:
    """Setup experiment logging"""
    
    # Create log directory
    log_file = Path(config.file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("h-m4")
    logger.setLevel(getattr(logging, config.level))
    
    # File handler
    file_handler = logging.FileHandler(config.file)
    file_handler.setFormatter(logging.Formatter(config.format))
    logger.addHandler(file_handler)
    
    # Console handler
    if config.console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(config.format))
        logger.addHandler(console_handler)
    
    return logger
```

---

### 6. Configuration Validation

```python
def validate_checkpoint_paths(config: ExperimentConfig) -> bool:
    """Validate that checkpoint files exist"""
    from pathlib import Path
    
    erm_path = Path(config.checkpoints["erm"].path)
    dro_path = Path(config.checkpoints["dro"].path)
    
    if not erm_path.exists():
        logging.warning(f"ERM checkpoint not found: {erm_path}")
        return False
    
    if not dro_path.exists():
        logging.warning(f"DRO checkpoint not found: {dro_path}")
        return False
    
    return True

def validate_gpu_availability(config: ComputeConfig) -> bool:
    """Validate GPU is available if device='cuda'"""
    import torch
    
    if config.device == "cuda" and not torch.cuda.is_available():
        logging.error("CUDA requested but not available")
        return False
    
    return True
```

---

### 7. Configuration Override Example

```python
# Load base configuration
config = ExperimentConfig.from_yaml("h-m4/experiment_config.yaml")

# Override specific parameters (e.g., for ablation study)
config.path_sampling.num_samples = 50  # Increase to M=50
config.success_criteria.primary_threshold = -0.5  # Relax threshold

# Validate
config.validate()

# Run experiment
experiment = CouplingExperiment(config)
results = experiment.run()
```

---

### 8. Results Schema (metrics.json)

```json
{
  "hypothesis_id": "h-m4",
  "timestamp": "2026-04-24T18:45:00Z",
  "gate_type": "SHOULD_WORK",
  "gate_result": "PASS",
  "fge_path": {
    "rho": -0.78,
    "p_value": 0.0023,
    "alignment_values": [0.72, 0.69, 0.66, "...", 0.32],
    "wga_values": [0.65, 0.68, 0.71, "...", 0.78],
    "num_samples": 20
  },
  "linear_path": {
    "rho": -0.82,
    "p_value": 0.0008,
    "alignment_values": [0.72, 0.69, 0.66, "...", 0.32],
    "wga_values": [0.65, 0.68, 0.71, "...", 0.78],
    "num_samples": 20
  },
  "success_criteria": {
    "primary": {
      "metric": "fge_rho",
      "threshold": -0.6,
      "actual": -0.78,
      "passed": true
    },
    "secondary": {
      "metric": "linear_rho",
      "threshold": -0.7,
      "actual": -0.82,
      "passed": true
    },
    "p_value": {
      "threshold": 0.01,
      "fge_actual": 0.0023,
      "linear_actual": 0.0008,
      "passed": true
    }
  },
  "figures": [
    "h-m4/figures/coupling_scatter.png",
    "h-m4/figures/trajectory_plot.png",
    "h-m4/figures/fge_vs_linear.png",
    "h-m4/figures/group_accuracy_path.png"
  ]
}
```

---

## Configuration Summary

**Total Configuration Files:** 2
- `experiment_config.yaml` (runtime configuration)
- `config.py` (dataclass schema with validation)

**Environment Variables:** 6 (GPU, paths, experiment settings)

**Logging:** Structured logging to file + console

**Validation:** 
- Schema validation via dataclasses
- Checkpoint path validation
- GPU availability check
- Parameter range validation

---

*Configuration Design v1.0 | Generated for Phase 3 Implementation Planning*
*Applied pattern: Configuration as Code*
