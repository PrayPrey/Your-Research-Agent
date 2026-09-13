# Configuration Specification: h-m3 SGD Trajectory Directional Bias Analysis

**Hypothesis ID:** h-m3  
**Type:** MECHANISM (Step 3 of 4)  
**Infrastructure:** FULL (YAML + Dataclass for 100-epoch training)  
**Date:** 2026-04-24  
**Configuration Agent:** Autonomous  
**Prerequisites:** h-m2 (COMPLETED ✅)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-m2)  
**Status**: h-m2 config verified - using hardcoded dict (STANDARD tier)  
**Config Pattern**: h-m3 uses YAML + dataclass (FULL tier) for 100-epoch training complexity  
**Analysis**: h-m3 requires full training (100 epochs), multiple seeds, checkpoint management → FULL tier infrastructure

---

## Applied Patterns

Applied: YAML Configuration Pattern (FULL tier)  
Applied: Dataclass Schema Pattern  
Applied: Multi-Seed Configuration  
Applied: Checkpoint Management Configuration

---

## Configuration Schema (YAML + Dataclass)

**Format**: YAML file + Python dataclass for type safety and validation.

### config.yaml

```yaml
# h-m3 Configuration
# SGD Trajectory Directional Bias Analysis
# 100-epoch training with trajectory logging

# Project metadata
project:
  hypothesis_id: h-m3
  hypothesis_type: MECHANISM
  tier: FULL
  base_hypothesis: h-m2
  gate_type: SHOULD_WORK

# Paths configuration
paths:
  # Data
  data_dir: /home/anonymous/data/waterbirds_v1.0
  
  # Checkpoints
  checkpoint_dir: ./checkpoints/
  checkpoint_prefix: h_m3_seed
  
  # Output directories
  results_dir: ./results/
  figures_dir: ./figures/
  logs_dir: ./logs/
  
  # Base hypothesis references (h-m2)
  h_m2_code: ../h-m2/code/
  h_m2_config: ../h-m2/code/config.py

# Reproducibility
random_seed:
  seeds: [42, 43, 44]  # 3 seeds for statistical validation
  deterministic: true
  benchmark: false

# Dataset configuration
dataset:
  name: waterbirds
  batch_size: 128
  num_workers: 4
  pin_memory: true
  
  # Group configuration (same as h-m2)
  minority_group_ids: [1, 3]  # landbirds on water, waterbirds on land
  majority_group_ids: [0, 2]  # landbirds on land, waterbirds on water
  
  # Preprocessing (same as h-m2)
  image_size: 224
  normalize_mean: [0.485, 0.456, 0.406]
  normalize_std: [0.229, 0.224, 0.225]

# Model configuration
model:
  architecture: resnet50
  pretrained: true
  num_classes: 2
  freeze_backbone: false

# Training configuration (100 epochs, not 5 like h-m2)
training:
  epochs: 100  # Full training for trajectory analysis
  
  # Optimizer (SGD, same as h-m2)
  optimizer:
    type: sgd
    lr: 0.001
    momentum: 0.9
    weight_decay: 0.0001
    nesterov: false
  
  # Learning rate scheduler
  scheduler:
    type: steplr
    step_size: 1
    gamma: 0.96  # Decay every epoch
  
  # Loss function
  loss: cross_entropy
  
  # Device
  device: cuda
  
  # Checkpointing
  save_checkpoints: true
  checkpoint_epochs: [10, 20, 30]  # For early prediction experiment
  save_best: true
  save_last: true

# Hessian eigenvector computation
hessian:
  # Library: pytorch-hessian-eigenthings
  num_eigenthings: 50
  mode: power_iter
  power_iter_steps: 20
  momentum: 0.0
  use_gpu: true
  
  # Marchenko-Pastur parameters
  sigma_sq_estimate: 1.0
  
  # Validation
  validate_orthonormality: true
  check_not_random: true  # Critical: verify NOT random basis (h-m2 fix)

# Trajectory logging configuration
trajectory:
  enabled: true
  log_frequency: 10  # Log every 10 steps (memory-efficient)
  
  # What to log
  log_bulk_alignment: true
  log_outlier_alignment: true
  log_directional_bias: true
  log_loss: true
  log_grad_norm: false  # Optional, can add if needed
  
  # Save options
  save_to_csv: true
  csv_filename_template: "trajectory_seed{seed}.csv"
  save_full_trajectory: true

# Gate metric configuration
gate_metric:
  metric_name: mean_directional_bias
  threshold: 0.0
  comparison: greater_than  # mean_bias > 0
  statistical_test: one_sample_ttest
  alpha: 0.05
  min_seeds: 3

# Early prediction experiment
early_prediction:
  enabled: true
  checkpoint_epoch: 10  # Use epoch 10 checkpoint
  compute_early_Aw: true
  secondary_metric_threshold: 0.1  # R² > 0.1

# Visualization configuration
visualization:
  enabled: true
  dpi: 300
  format: png
  
  # Color scheme
  colors:
    seed1: blue
    seed2: green
    seed3: red
    mean: black
    threshold: darkred
    bulk: blue
    outlier: red
  
  # Figures to generate
  figures:
    gate_metric:
      filename: fig1_gate_metric.png
      title: "Gate Metric: Directional Bias Across Seeds"
      type: bar
    
    bias_over_time:
      filename: fig2_bias_over_time.png
      title: "SGD Directional Bias Over Training"
      type: line_with_std
    
    bulk_vs_outlier:
      filename: fig3_bulk_vs_outlier.png
      title: "Bulk vs Outlier Alignment Trajectories"
      type: line
    
    early_prediction:
      filename: fig4_early_prediction.png
      title: "Early A(w) vs Final Worst-Group Accuracy"
      type: scatter_with_regression
    
    eigenvalue_spectrum:
      filename: fig5_eigenvalue_spectrum.png
      title: "Hessian Eigenvalue Spectrum with MP Bulk Edge"
      type: logscale_spectrum

# Logging configuration
logging:
  level: INFO
  console: true
  file: true
  log_filename_template: "h_m3_seed{seed}.log"
  
  # Metrics to log
  log_train_loss: true
  log_val_loss: true
  log_val_accuracy: true
  log_worst_group_acc: true
  log_trajectory_stats: true

# Output files
outputs:
  # CSV outputs
  trajectory_csv: "trajectory_seed{seed}.csv"
  training_history_csv: "training_history_seed{seed}.csv"
  directional_bias_results: "directional_bias_results.json"
  early_prediction_results: "early_prediction_results.json"
  
  # Aggregated results
  gate_metric_summary: "gate_metric_summary.json"
  multi_seed_comparison: "multi_seed_comparison.csv"
```

---

## Dataclass Schema (config_schema.py)

```python
"""
h-m3 Configuration Schema
Type-safe configuration with validation
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
import yaml

@dataclass
class ProjectConfig:
    """Project metadata"""
    hypothesis_id: str = "h-m3"
    hypothesis_type: str = "MECHANISM"
    tier: str = "FULL"
    base_hypothesis: str = "h-m2"
    gate_type: str = "SHOULD_WORK"

@dataclass
class PathsConfig:
    """Path configuration"""
    data_dir: str = "/home/anonymous/data/waterbirds_v1.0"
    checkpoint_dir: str = "./checkpoints/"
    checkpoint_prefix: str = "h_m3_seed"
    results_dir: str = "./results/"
    figures_dir: str = "./figures/"
    logs_dir: str = "./logs/"
    h_m2_code: str = "../h-m2/code/"
    h_m2_config: str = "../h-m2/code/config.py"

@dataclass
class RandomSeedConfig:
    """Random seed configuration"""
    seeds: List[int] = field(default_factory=lambda: [42, 43, 44])
    deterministic: bool = True
    benchmark: bool = False

@dataclass
class DatasetConfig:
    """Dataset configuration"""
    name: str = "waterbirds"
    batch_size: int = 128
    num_workers: int = 4
    pin_memory: bool = True
    minority_group_ids: List[int] = field(default_factory=lambda: [1, 3])
    majority_group_ids: List[int] = field(default_factory=lambda: [0, 2])
    image_size: int = 224
    normalize_mean: List[float] = field(default_factory=lambda: [0.485, 0.456, 0.406])
    normalize_std: List[float] = field(default_factory=lambda: [0.229, 0.224, 0.225])

@dataclass
class ModelConfig:
    """Model configuration"""
    architecture: str = "resnet50"
    pretrained: bool = True
    num_classes: int = 2
    freeze_backbone: bool = False

@dataclass
class OptimizerConfig:
    """Optimizer configuration"""
    type: str = "sgd"
    lr: float = 0.001
    momentum: float = 0.9
    weight_decay: float = 0.0001
    nesterov: bool = False

@dataclass
class SchedulerConfig:
    """Learning rate scheduler configuration"""
    type: str = "steplr"
    step_size: int = 1
    gamma: float = 0.96

@dataclass
class TrainingConfig:
    """Training configuration"""
    epochs: int = 100  # Full training
    optimizer: OptimizerConfig = field(default_factory=OptimizerConfig)
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)
    loss: str = "cross_entropy"
    device: str = "cuda"
    save_checkpoints: bool = True
    checkpoint_epochs: List[int] = field(default_factory=lambda: [10, 20, 30])
    save_best: bool = True
    save_last: bool = True

@dataclass
class HessianConfig:
    """Hessian eigenvector computation configuration"""
    num_eigenthings: int = 50
    mode: str = "power_iter"
    power_iter_steps: int = 20
    momentum: float = 0.0
    use_gpu: bool = True
    sigma_sq_estimate: float = 1.0
    validate_orthonormality: bool = True
    check_not_random: bool = True  # Critical: h-m2 fix

@dataclass
class TrajectoryConfig:
    """Trajectory logging configuration"""
    enabled: bool = True
    log_frequency: int = 10
    log_bulk_alignment: bool = True
    log_outlier_alignment: bool = True
    log_directional_bias: bool = True
    log_loss: bool = True
    log_grad_norm: bool = False
    save_to_csv: bool = True
    csv_filename_template: str = "trajectory_seed{seed}.csv"
    save_full_trajectory: bool = True

@dataclass
class GateMetricConfig:
    """Gate metric evaluation configuration"""
    metric_name: str = "mean_directional_bias"
    threshold: float = 0.0
    comparison: str = "greater_than"
    statistical_test: str = "one_sample_ttest"
    alpha: float = 0.05
    min_seeds: int = 3

@dataclass
class EarlyPredictionConfig:
    """Early prediction experiment configuration"""
    enabled: bool = True
    checkpoint_epoch: int = 10
    compute_early_Aw: bool = True
    secondary_metric_threshold: float = 0.1

@dataclass
class VisualizationConfig:
    """Visualization configuration"""
    enabled: bool = True
    dpi: int = 300
    format: str = "png"
    colors: Dict[str, str] = field(default_factory=lambda: {
        'seed1': 'blue',
        'seed2': 'green',
        'seed3': 'red',
        'mean': 'black',
        'threshold': 'darkred',
        'bulk': 'blue',
        'outlier': 'red'
    })
    figures: Dict[str, Dict[str, str]] = field(default_factory=dict)

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    console: bool = True
    file: bool = True
    log_filename_template: str = "h_m3_seed{seed}.log"
    log_train_loss: bool = True
    log_val_loss: bool = True
    log_val_accuracy: bool = True
    log_worst_group_acc: bool = True
    log_trajectory_stats: bool = True

@dataclass
class OutputsConfig:
    """Output files configuration"""
    trajectory_csv: str = "trajectory_seed{seed}.csv"
    training_history_csv: str = "training_history_seed{seed}.csv"
    directional_bias_results: str = "directional_bias_results.json"
    early_prediction_results: str = "early_prediction_results.json"
    gate_metric_summary: str = "gate_metric_summary.json"
    multi_seed_comparison: str = "multi_seed_comparison.csv"

@dataclass
class H_M3_Config:
    """Complete h-m3 configuration"""
    project: ProjectConfig = field(default_factory=ProjectConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    random_seed: RandomSeedConfig = field(default_factory=RandomSeedConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    hessian: HessianConfig = field(default_factory=HessianConfig)
    trajectory: TrajectoryConfig = field(default_factory=TrajectoryConfig)
    gate_metric: GateMetricConfig = field(default_factory=GateMetricConfig)
    early_prediction: EarlyPredictionConfig = field(default_factory=EarlyPredictionConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    outputs: OutputsConfig = field(default_factory=OutputsConfig)

def load_config(config_path: str = "config.yaml") -> H_M3_Config:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to YAML config file
    
    Returns:
        config: H_M3_Config instance
    """
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    # Convert nested dicts to dataclass instances
    project = ProjectConfig(**config_dict['project'])
    paths = PathsConfig(**config_dict['paths'])
    random_seed = RandomSeedConfig(**config_dict['random_seed'])
    dataset = DatasetConfig(**config_dict['dataset'])
    model = ModelConfig(**config_dict['model'])
    
    # Training config with nested optimizer and scheduler
    training_dict = config_dict['training']
    optimizer = OptimizerConfig(**training_dict['optimizer'])
    scheduler = SchedulerConfig(**training_dict['scheduler'])
    training = TrainingConfig(
        epochs=training_dict['epochs'],
        optimizer=optimizer,
        scheduler=scheduler,
        loss=training_dict['loss'],
        device=training_dict['device'],
        save_checkpoints=training_dict['save_checkpoints'],
        checkpoint_epochs=training_dict['checkpoint_epochs'],
        save_best=training_dict['save_best'],
        save_last=training_dict['save_last']
    )
    
    hessian = HessianConfig(**config_dict['hessian'])
    trajectory = TrajectoryConfig(**config_dict['trajectory'])
    gate_metric = GateMetricConfig(**config_dict['gate_metric'])
    early_prediction = EarlyPredictionConfig(**config_dict['early_prediction'])
    visualization = VisualizationConfig(**config_dict['visualization'])
    logging_cfg = LoggingConfig(**config_dict['logging'])
    outputs = OutputsConfig(**config_dict['outputs'])
    
    return H_M3_Config(
        project=project,
        paths=paths,
        random_seed=random_seed,
        dataset=dataset,
        model=model,
        training=training,
        hessian=hessian,
        trajectory=trajectory,
        gate_metric=gate_metric,
        early_prediction=early_prediction,
        visualization=visualization,
        logging=logging_cfg,
        outputs=outputs
    )
```

---

## Configuration Usage Example

```python
# run_h_m3_experiment.py

import torch
import numpy as np
import random
from pathlib import Path
from config_schema import load_config, H_M3_Config

def setup_environment(config: H_M3_Config, seed: int):
    """Setup experiment environment for specific seed"""
    # Set random seed
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    
    if config.random_seed.deterministic:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    
    # Create output directories
    Path(config.paths.checkpoint_dir).mkdir(parents=True, exist_ok=True)
    Path(config.paths.results_dir).mkdir(parents=True, exist_ok=True)
    Path(config.paths.figures_dir).mkdir(parents=True, exist_ok=True)
    Path(config.paths.logs_dir).mkdir(parents=True, exist_ok=True)
    
    # Verify data directory exists
    data_path = Path(config.paths.data_dir)
    assert data_path.exists(), f"Data directory not found: {data_path}"
    
    print(f"Environment setup complete (seed={seed})")

def main():
    # Load configuration from YAML
    config = load_config("config.yaml")
    
    # Multi-seed execution
    loggers_all_seeds = []
    final_wga_all_seeds = []
    
    for seed in config.random_seed.seeds:
        print(f"\n{'='*60}")
        print(f"Running experiment with seed {seed}")
        print(f"{'='*60}\n")
        
        # Setup environment for this seed
        setup_environment(config, seed)
        
        # Load data
        from data.dataset import get_dataloaders
        dataloaders = get_dataloaders(
            data_dir=config.paths.data_dir,
            batch_size=config.dataset.batch_size,
            num_workers=config.dataset.num_workers
        )
        
        # Create model
        from models.model import get_resnet50
        model = get_resnet50(
            num_classes=config.model.num_classes,
            pretrained=config.model.pretrained
        )
        
        # Compute Hessian eigenvectors
        from hessian_eigenvectors import compute_real_hessian_eigenvectors, separate_bulk_outlier_subspaces
        print("Computing real Hessian eigenvectors...")
        eigenvalues, eigenvectors = compute_real_hessian_eigenvectors(
            model, 
            dataloaders['train'], 
            num_eigenthings=config.hessian.num_eigenthings,
            device=config.training.device
        )
        
        # Separate bulk (flat) vs outlier (sharp) subspaces
        outlier_evecs, bulk_evecs, bulk_edge = separate_bulk_outlier_subspaces(
            eigenvalues, eigenvectors, model, len(dataloaders['train'].dataset)
        )
        
        print(f"Hessian analysis: {len(outlier_evecs)} outlier, {len(bulk_evecs)} bulk eigenvectors")
        print(f"Marchenko-Pastur bulk edge: {bulk_edge:.4f}")
        
        # Create trajectory logger
        from trajectory_logger import TrajectoryLogger
        logger = TrajectoryLogger(model, outlier_evecs, bulk_evecs)
        
        # Train with trajectory logging
        from training import train_with_trajectory_logging
        print(f"Training with trajectory logging ({config.training.epochs} epochs)...")
        training_history = train_with_trajectory_logging(
            model, dataloaders['train'], dataloaders['val'], 
            logger, config, device=config.training.device
        )
        
        # Compute final worst-group accuracy
        from directional_bias import compute_worst_group_accuracy
        final_wga = compute_worst_group_accuracy(model, dataloaders['test'], config.training.device)
        
        # Save trajectory
        trajectory_csv = config.paths.results_dir + config.outputs.trajectory_csv.format(seed=seed)
        logger.save_trajectory(trajectory_csv)
        
        loggers_all_seeds.append(logger)
        final_wga_all_seeds.append(final_wga)
        
        print(f"Seed {seed} complete: Final WGA = {final_wga:.4f}")
    
    # Evaluate directional bias across seeds
    from directional_bias import evaluate_directional_bias, compute_early_prediction_r2
    print("\n" + "="*60)
    print("GATE METRIC EVALUATION")
    print("="*60 + "\n")
    
    eval_results = evaluate_directional_bias(loggers_all_seeds)
    
    print(f"Overall Mean Directional Bias: {eval_results['overall_mean_bias']:.6f}")
    print(f"Std Across Seeds: {eval_results['std_across_seeds']:.6f}")
    print(f"p-value: {eval_results['p_value']:.4f}")
    print(f"Gate Pass (SHOULD_WORK): {eval_results['gate_pass']}")
    
    # Save gate metric results
    import json
    gate_summary_path = config.paths.results_dir + config.outputs.gate_metric_summary
    with open(gate_summary_path, 'w') as f:
        json.dump(eval_results, f, indent=2)
    
    # Early prediction experiment
    if config.early_prediction.enabled:
        checkpoint_paths = [
            f"{config.paths.checkpoint_dir}{config.paths.checkpoint_prefix}{seed}_epoch{config.early_prediction.checkpoint_epoch}.pth"
            for seed in config.random_seed.seeds
        ]
        early_pred_results = compute_early_prediction_r2(
            checkpoint_paths, dataloaders['train'], final_wga_all_seeds
        )
        
        print(f"\nEarly Prediction R²: {early_pred_results['r2_score']:.4f}")
        print(f"Early Prediction Valid (R² > {config.early_prediction.secondary_metric_threshold}): {early_pred_results['early_prediction_valid']}")
        
        # Save early prediction results
        early_pred_path = config.paths.results_dir + config.outputs.early_prediction_results
        with open(early_pred_path, 'w') as f:
            json.dump(early_pred_results, f, indent=2)
    
    # Generate visualizations
    if config.visualization.enabled:
        from visualize_trajectory import (plot_directional_bias_over_time, 
                                         plot_bulk_vs_outlier_alignment,
                                         plot_gate_metric_comparison)
        print("\nGenerating visualizations...")
        trajectories = [logger.get_trajectory() for logger in loggers_all_seeds]
        
        plot_gate_metric_comparison(
            eval_results, 
            config.paths.figures_dir + config.visualization.figures['gate_metric']['filename']
        )
        plot_directional_bias_over_time(
            trajectories, 
            config.paths.figures_dir + config.visualization.figures['bias_over_time']['filename']
        )
        plot_bulk_vs_outlier_alignment(
            trajectories[0], 
            config.paths.figures_dir + config.visualization.figures['bulk_vs_outlier']['filename']
        )
        
        print(f"All figures saved to {config.paths.figures_dir}")
    
    return eval_results['gate_pass']

if __name__ == '__main__':
    import sys
    gate_pass = main()
    sys.exit(0 if gate_pass else 1)
```

---

## Inherited Configuration (from h-m2)

### Values Verified from h-m2 Config

| Parameter | h-m2 Value | h-m3 Value | Rationale |
|-----------|------------|------------|-----------|
| batch_size | 128 | 128 | Same batch size for consistency |
| lr | 0.001 | 0.001 | Same learning rate (fine-tuning) |
| momentum | 0.9 | 0.9 | Same SGD momentum |
| weight_decay | 0.0001 | 0.0001 | Same weight decay |
| device | cuda | cuda | Single GPU execution |
| minority_group_ids | [1, 3] | [1, 3] | Same group definitions |
| majority_group_ids | [0, 2] | [0, 2] | Same group definitions |

**Key Differences from h-m2**:
- **epochs**: 5 (h-m2 PoC) → 100 (h-m3 full training)
- **infrastructure**: hardcoded dict (h-m2 STANDARD) → YAML + dataclass (h-m3 FULL)
- **Hessian**: random basis (h-m2) → real eigenvectors (h-m3)

---

*Configuration designed for Phase 4 Implementation | h-m3 MECHANISM Hypothesis | FULL tier with YAML + Dataclass*
