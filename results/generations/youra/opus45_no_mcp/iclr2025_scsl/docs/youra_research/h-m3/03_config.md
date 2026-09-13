# Configuration: H-M3 — Second Derivative Crystallization Detection

Applied: signal-detection-pipeline (rolling-smooth -> differentiate -> peak-find -> aggregate)
Applied: multi-seed-statistical-validation (dataclass config w/ nested paths, gate thresholds as fields)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2) + upstream (H-E1)
**Status**: config classes verified from base code (direct file read; Serena MCP unavailable in this environment)
**Config Files Found**: `h-m2/code/config.py` (`FeatureProbeConfig`), `h-e1/code/config.py` (checked, same dataclass style)
**Pattern Used**: dataclass with `field(default_factory=...)` for lists/dicts, path-join helper methods, module-level `CONFIG` singleton

---

## Inherited Configuration (Base Hypothesis)

H-M3 does not subclass H-M2's config (different domain: curve detection vs. checkpoint probing) but reuses its **style**: dataclass + default_factory + `get_checkpoint_path()`-style helper + `CONFIG` singleton.

```python
# From: h-m2/code/config.py (ACTUAL CODE, style reference only)
@dataclass
class FeatureProbeConfig:
    h_m1_checkpoint_dir: str = "../../h-m1/code/checkpoints"
    checkpoint_pattern: str = "waterbirds_epoch{epoch}.pt"
    output_dir: str = "./outputs"
    figures_dir: str = "../figures"

    def get_checkpoint_path(self, epoch: int) -> str:
        return str(Path(self.h_m1_checkpoint_dir) / self.checkpoint_pattern.format(epoch=epoch))
```

**Verified from**: `h-m2/code/config.py`. No import — H-M3 uses its own `DetectionConfig` (per architecture, no importable H-M2 module exists to reuse directly).

---

## A-1: Config module [Complexity: 5, Budget: 5]

**Applied**: dataclass + default_factory + path-helper pattern (from H-M2)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class DetectionConfig:
    # Data
    benchmarks: list = field(default_factory=lambda: ["waterbirds", "celeba", "coloredmnist"])
    n_seeds: int = 5
    epochs_by_benchmark: dict = field(default_factory=lambda: {
        "waterbirds": 100, "celeba": 50, "coloredmnist": 30
    })

    # Detection algorithm (FR-2, FR-3, FR-4)
    smoothing_windows: list = field(default_factory=lambda: [3, 5, 7])
    primary_window: int = 5
    prominence_threshold: float = 0.005

    # Sensitivity analysis (FR-5)
    window_robustness_tolerance_epochs: int = 3

    # Checkpoint source
    h_e1_checkpoint_dir: str = "../../h-e1/code/checkpoints"
    checkpoint_pattern: str = "waterbirds_epoch{epoch}.pt"

    # Gate thresholds (FR-6, Success Criteria)
    detection_rate_target: float = 0.8
    variance_target_epochs: float = 5.0
    snr_target: float = 2.0

    # Secondary thresholds (FR-5, FR-7)
    window_robustness_target: float = 0.7
    cross_benchmark_correlation_target: float = 0.6

    # Seed for synthetic curve fallback (A-3) — reproducibility per NFR-2
    synthesis_seed_base: int = 42

    # Output
    output_dir: str = "./outputs"
    figures_dir: str = "../figures"
    results_file: str = "detection_results.json"
    metrics_file: str = "aggregated_metrics.yaml"

    def get_checkpoint_path(self, epoch: int) -> str:
        return str(Path(self.h_e1_checkpoint_dir) / self.checkpoint_pattern.format(epoch=epoch))

    def get_n_epochs(self, benchmark: str) -> int:
        return self.epochs_by_benchmark[benchmark]

CONFIG = DetectionConfig()
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Dataclass fields | Define all params above w/ defaults |
| C-1-2 | Path helpers | `get_checkpoint_path`, `get_n_epochs` |
| C-1-3 | Output dirs | `output_dir`, `figures_dir`, filenames |
| C-1-4 | CONFIG singleton | Module-level instantiation |

---

## Output File Formats

### `outputs/detection_results.json`
Per-seed, per-benchmark raw detection results (list of dicts, from `analyze_curve`):
```json
[
  {"benchmark": "waterbirds", "seed": 0, "detected": true, "epoch": 42,
   "prominence": 0.0071, "snr": 2.31,
   "sensitivity": {"w3": {"detected": true, "epoch": 41}, "w5": {...}, "w7": {...}}}
]
```

### `outputs/aggregated_metrics.yaml` (YAML schema)
```yaml
per_benchmark:
  waterbirds:
    detection_rate: 0.8
    timing_variance_epochs: 3.2
    mean_snr: 2.4
    window_robustness: 0.87
  celeba:
    detection_rate: 0.8
    timing_variance_epochs: 4.1
    mean_snr: 2.1
    window_robustness: 0.73
  coloredmnist:
    detection_rate: 0.6
    timing_variance_epochs: 2.9
    mean_snr: 1.9
    window_robustness: 0.67
cross_benchmark_correlation: 0.68
gate:
  passed: true
  detection_rate: {value: 0.73, target: 0.8, failure_threshold: 0.5}
  timing_variance_epochs: {value: 3.4, target: 5.0, failure_threshold: 10.0}
  snr: {value: 2.1, target: 2.0, failure_threshold: 1.0}
```

**Gate logic** (`evaluate_gate`): `passed = detection_rate > 0.8 and timing_variance < 5.0 and snr > 2.0` (aggregated across all benchmarks/seeds).

---

## Self-Validation
- [x] ONE format (dataclass only)
- [x] No ASCII diagrams
- [x] "Applied" lines present (2)
- [x] Rationale only for non-standard (`synthesis_seed_base` noted inline)
- [x] Subtasks match budget (4/4 for A-1, complexity 5)
- [x] Codebase Analysis (Serena) section included
- [x] Inherited Configuration section included, field names verified from actual `h-m2/code/config.py`
