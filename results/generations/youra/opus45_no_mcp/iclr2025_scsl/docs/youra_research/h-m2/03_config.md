# Configuration: H-M2 Post-Crystallization Feature Commitment

## Codebase Analysis (Serena)

**Project Type**: incremental_hypothesis (base: h-m1)
**Status**: config class verified from actual code (`h-m1/code/config.py`)
**Config Files Found**: `h-m1/code/config.py` — `@dataclass GradientStarvationConfig` extends h-e1 `Config`
**Pattern Used**: dataclass inheritance

**Field name note**: h-m1 uses `epochs_waterbirds` (not `epochs`), `checkpoint_dir`, `data_root`. Extended config below adds probe-specific fields.

---

## Inherited Configuration (Base Hypothesis: H-M1)

```python
# From: h-m1/code/config.py (ACTUAL CODE)
from dataclasses import dataclass, field

@dataclass
class GradientStarvationConfig:
    # Training (inherited from h-e1)
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    batch_size: int = 128
    epochs_waterbirds: int = 100
    seed: int = 42
    
    # Detection (inherited from h-e1)
    smoothing_window: int = 5
    detection_threshold: float = -0.01
    search_fraction: float = 0.5
    
    # Paths
    data_root: str = "./data"
    checkpoint_dir: str = "./checkpoints"
    output_dir: str = "./outputs"
    
    # Gradient tracking (h-m1 specific)
    track_gradients: bool = True
    minority_group_id: int = 3
    majority_group_id: int = 0
    
    # LR schedule
    lr_milestones: list = field(default_factory=lambda: [30, 60])
    lr_gamma: float = 0.1
    
    # Correlation
    correlation_threshold: float = 0.7
    
    # Dataset (single dataset for MECHANISM PoC)
    datasets: list = field(default_factory=lambda: ["waterbirds"])
```

---

## M2-1: Feature Probe Config [Complexity: FULL, Budget: ≤30 tasks]

**Applied**: Standard dataclass extension pattern

### Configuration (Python Dataclass — extends h-m1 Config)

```python
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class FeatureProbeConfig:
    """Configuration for H-M2 post-crystallization feature commitment analysis."""
    
    # --- Inherited from h-m1 (for compatibility) ---
    batch_size: int = 128
    seed: int = 42
    epochs_waterbirds: int = 100
    data_root: str = "./data"
    
    # --- Checkpoint source (from h-m1) ---
    h_m1_checkpoint_dir: str = "../h-m1/code/checkpoints"
    checkpoint_pattern: str = "epoch_{epoch}.pt"
    
    # --- Crystallization timing (auto-detect from h-m1/h-e1) ---
    crystallization_epoch: int = -1  # -1 = auto-detect
    final_epoch: int = 100  # Last epoch to analyze
    checkpoint_stride: int = 1  # Analyze every N epochs (1 = all)
    
    # --- Feature extraction ---
    feature_layer: str = "avgpool"
    feature_dim: int = 2048
    
    # --- Linear probe training ---
    probe_lr: float = 0.01
    probe_iterations: int = 100
    probe_optimizer: str = "sgd"  # Options: "sgd", "adam"
    reinitialize_probes: bool = True  # Fresh probes per checkpoint
    
    # --- Commitment detection ---
    noise_margin: float = 0.02  # Tolerance for spurious accuracy fluctuation
    core_suppression_threshold: float = 0.85  # Core acc below this = suppressed
    
    # --- Group/label mapping (Waterbirds) ---
    # Group ID: 0=landbird/land, 1=landbird/water, 2=waterbird/land, 3=waterbird/water
    # Core label (y): 0=landbird, 1=waterbird
    # Spurious label: derived from group_id % 2 (0=land, 1=water)
    group_to_spurious: dict = field(default_factory=lambda: {0: 0, 1: 1, 2: 0, 3: 1})
    
    # --- Paths ---
    output_dir: str = "./outputs"
    figures_dir: str = "../figures"
    results_file: str = "probe_results.yaml"
    
    # --- Dataset ---
    datasets: list = field(default_factory=lambda: ["waterbirds"])
    use_test_for_eval: bool = True  # Evaluate probes on test split
    use_val_for_train: bool = True  # Train probes on val split
    
    # --- Reproducibility ---
    deterministic: bool = True
    
    def get_checkpoint_path(self, epoch: int) -> str:
        """Return full path to checkpoint for given epoch."""
        return str(Path(self.h_m1_checkpoint_dir) / self.checkpoint_pattern.format(epoch=epoch))
    
    def get_analysis_epochs(self) -> list[int]:
        """Return list of epochs to analyze."""
        if self.crystallization_epoch < 0:
            raise ValueError("crystallization_epoch must be set before calling get_analysis_epochs")
        return list(range(self.crystallization_epoch, self.final_epoch + 1, self.checkpoint_stride))


CONFIG = FeatureProbeConfig()
```

### YAML Schema (for external configuration)

```yaml
# h-m2/config.yaml
feature_probe:
  # Checkpoint source
  h_m1_checkpoint_dir: "../h-m1/code/checkpoints"
  checkpoint_pattern: "epoch_{epoch}.pt"
  
  # Crystallization timing
  crystallization_epoch: -1  # Auto-detect from h-m1
  final_epoch: 100
  checkpoint_stride: 1
  
  # Feature extraction
  feature_layer: "avgpool"
  feature_dim: 2048
  
  # Linear probe training
  probe_lr: 0.01
  probe_iterations: 100
  probe_optimizer: "sgd"
  reinitialize_probes: true
  
  # Commitment detection
  noise_margin: 0.02
  core_suppression_threshold: 0.85
  
  # Paths
  output_dir: "./outputs"
  figures_dir: "../figures"
  results_file: "probe_results.yaml"
  
  # Dataset
  datasets:
    - "waterbirds"
  use_test_for_eval: true
  use_val_for_train: true
  
  # Reproducibility
  seed: 42
  batch_size: 128
  deterministic: true
```

### Subtasks [5/30 used — remainder allocated to Logic implementation tasks]

| ID | Subtask | Description |
|----|---------|--------------|
| C-M2-1 | Config dataclass | `FeatureProbeConfig` with probe/commitment fields |
| C-M2-2 | Checkpoint path helper | `get_checkpoint_path(epoch)` method |
| C-M2-3 | Analysis epochs helper | `get_analysis_epochs()` method |
| C-M2-4 | Group-to-spurious mapping | Dict mapping group_id to spurious label (background) |
| C-M2-5 | YAML loader | Load config from `config.yaml` with defaults fallback |

---

## Group Label Reference

### Waterbirds Group Structure

| Group ID | Bird Type (Core/y) | Background (Spurious) | Frequency |
|----------|-------------------|----------------------|-----------|
| 0 | 0 (Landbird) | 0 (Land) | Majority |
| 1 | 0 (Landbird) | 1 (Water) | Minority |
| 2 | 1 (Waterbird) | 0 (Land) | Minority |
| 3 | 1 (Waterbird) | 1 (Water) | Majority |

### Label Derivation from Metadata

```python
# In WILDS Waterbirds dataloader:
# x: [B, 3, 224, 224] image
# y: [B] core label (bird type: 0=landbird, 1=waterbird)
# metadata: [B, 1] group_id (0-3)

# Derive spurious label (background):
spurious_label = metadata[:, 0] % 2  # 0=land, 1=water

# Alternative using mapping:
spurious_label = torch.tensor([GROUP_TO_SPURIOUS[g.item()] for g in metadata[:, 0]])
```

---

## Notes

- H-M2 is analysis-only: no model training, only checkpoint loading + probe training
- Probes reinitialized per checkpoint to avoid carryover effects
- Crystallization epoch auto-detected from h-m1 outputs (stored in h-m1/outputs/)
- Full test set (5794 samples) used for probe evaluation per PRD
