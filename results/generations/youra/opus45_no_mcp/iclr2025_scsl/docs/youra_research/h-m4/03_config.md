# Configuration: H-M4 — Benchmark-Relative Crystallization Timing Validation

Applied: signal-detection-pipeline (reused from H-M3, unmodified) + cross-benchmark-normalization-layer
Applied: multi-seed-statistical-validation (dataclass config, gate thresholds as fields)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M3) + upstream (H-E1)
**Status**: config classes verified from base code (direct file read; Serena MCP unavailable in this environment)
**Config Files Found**: `h-m3/code/config.py` (`DetectionConfig`)
**Pattern Used**: dataclass with `field(default_factory=...)` for lists/dicts, path-join helper methods, module-level `CONFIG` singleton

---

## Inherited Configuration (Base Hypothesis)

H-M4 reuses H-M3's detection functions (`compute_wga_second_derivative`, `detect_crystallization_peak`) unmodified (FR-2), and follows the same config style. It does **not** subclass `DetectionConfig` — H-M4 adds a new per-benchmark dimension (`BenchmarkConfig`) not present in H-M3.

```python
# From: h-m3/code/config.py (ACTUAL CODE, params reused as-is)
@dataclass
class DetectionConfig:
    primary_window: int = 5              # -> window_size in H-M4
    prominence_threshold: float = 0.005  # -> same value reused
```

**Verified from**: `h-m3/code/config.py`. Detection params (`window_size=5`, `prominence_threshold=0.005`) copied verbatim per FR-2 acceptance criteria ("Reuse H-M3 code without modification").

---

## A-1: Config module [Complexity: 5, Budget: 5]

**Applied**: dataclass + default_factory + path-helper pattern (from H-M3), per-benchmark nested config (from experiment brief)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class BenchmarkConfig:
    name: str
    total_epochs: int
    expected_range: tuple          # (min_percent, max_percent)
    lr: float
    batch_size: int = 128
    optimizer: str = "sgd"
    momentum: float = 0.9
    checkpoint_pattern: str = "{benchmark}_seed{seed}_epoch{epoch}.pt"


@dataclass
class TimingAnalysisConfig:
    window_size: int = 5                      # reused from H-M3 primary_window
    prominence_threshold: float = 0.005        # reused from H-M3, unmodified (FR-2)
    expected_range: tuple = (20, 40)           # % of training duration


@dataclass
class GateConfig:
    range_compliance_target: float = 1.0       # 3/3 benchmarks in range
    range_compliance_conditional: float = 0.67  # <1 -> fail (per PRD table)
    variance_target_percent: float = 10.0       # std dev across benchmarks
    variance_conditional_percent: float = 15.0
    detection_rate_target: float = 0.8
    detection_rate_conditional: float = 0.6
    seed_variance_target_percent: float = 5.0   # per-benchmark, secondary metric


@dataclass
class ExperimentConfig:
    seeds: list = field(default_factory=lambda: [0, 1, 2, 3, 4])

    benchmarks: dict = field(default_factory=lambda: {
        "waterbirds": BenchmarkConfig(
            name="Waterbirds", total_epochs=100, expected_range=(20, 40),
            lr=1e-3,
        ),
        "celeba": BenchmarkConfig(
            name="CelebA", total_epochs=50, expected_range=(20, 40),
            lr=1e-4,
        ),
        "coloredmnist": BenchmarkConfig(
            name="ColoredMNIST", total_epochs=30, expected_range=(20, 40),
            lr=1e-3,
        ),
    })

    timing: TimingAnalysisConfig = field(default_factory=TimingAnalysisConfig)
    gate: GateConfig = field(default_factory=GateConfig)

    # Checkpoint source (H-E1 full training runs, or new runs if not covered)
    h_e1_checkpoint_dir: str = "../../h-e1/code/checkpoints"
    checkpoint_dir: str = "./checkpoints"

    # Output
    output_dir: str = "./outputs"
    figures_dir: str = "../figures"
    results_file: str = "timing_results.json"
    metrics_file: str = "aggregated_metrics.yaml"

    def get_checkpoint_path(self, benchmark: str, seed: int, epoch: int) -> str:
        cfg = self.benchmarks[benchmark]
        fname = cfg.checkpoint_pattern.format(benchmark=benchmark, seed=seed, epoch=epoch)
        return str(Path(self.checkpoint_dir) / fname)

    def get_n_epochs(self, benchmark: str) -> int:
        return self.benchmarks[benchmark].total_epochs


CONFIG = ExperimentConfig()
```

### Subtasks [5/5 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | `BenchmarkConfig` | Per-benchmark training params + expected range |
| C-1-2 | `TimingAnalysisConfig` | Detection window/prominence/expected range (reused from H-M3) |
| C-1-3 | `GateConfig` | Range compliance, variance, detection-rate thresholds |
| C-1-4 | `ExperimentConfig` | Seeds, benchmark dict, output paths, checkpoint helpers |
| C-1-5 | `CONFIG` singleton | Module-level instantiation |

---

## Output File Formats

### `outputs/timing_results.json`
Per-seed, per-benchmark raw timing results:
```json
[
  {"benchmark": "waterbirds", "seed": 0, "detected": true,
   "peak_epoch": 3, "total_epochs": 100,
   "normalized_timing_percent": 3.0, "in_expected_range": false,
   "snr": 5.64}
]
```

### `outputs/aggregated_metrics.yaml`
```yaml
per_benchmark:
  waterbirds:
    mean_normalized_timing_percent: 3.2
    seed_variance_percent: 0.8
    detection_rate: 1.0
    in_expected_range: false
  celeba:
    mean_normalized_timing_percent: 24.1
    seed_variance_percent: 2.3
    detection_rate: 1.0
    in_expected_range: true
  coloredmnist:
    mean_normalized_timing_percent: 31.5
    seed_variance_percent: 3.1
    detection_rate: 0.8
    in_expected_range: true
cross_benchmark:
  mean_timing_percent: 19.6
  variance_percent: 12.9
  range_compliance: 0.67
  detection_rate_overall: 0.93
gate:
  passed: false
  status: CONDITIONAL_PASS
  range_compliance: {value: 0.67, target: 1.0, failure_threshold: 0.33}
  timing_variance_percent: {value: 12.9, target: 10.0, failure_threshold: 15.0}
  detection_rate: {value: 0.93, target: 0.8, failure_threshold: 0.5}
```

**Gate logic** (`evaluate_gate`):
```python
def evaluate_gate(cross_benchmark: dict, gate: GateConfig) -> str:
    rc, var, dr = cross_benchmark["range_compliance"], cross_benchmark["variance_percent"], cross_benchmark["detection_rate_overall"]
    if rc >= gate.range_compliance_target and var < gate.variance_target_percent and dr > gate.detection_rate_target:
        return "PASS"
    if rc >= gate.range_compliance_conditional and var < gate.variance_conditional_percent and dr > gate.detection_rate_conditional:
        return "CONDITIONAL_PASS"
    return "FAIL"
```

---

## Self-Validation
- [x] ONE format (dataclass only)
- [x] No ASCII diagrams
- [x] "Applied" lines present (2)
- [x] Rationale only for non-standard (reused H-M3 detection params noted inline)
- [x] Subtasks match budget (5/5 for A-1, complexity 5)
- [x] Codebase Analysis (Serena) section included
- [x] Inherited Configuration section included, field names verified from actual `h-m3/code/config.py`
