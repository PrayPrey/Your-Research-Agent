# Architecture: H-M4 — Benchmark-Relative Crystallization Timing Validation

**Type**: MECHANISM | **Epic Tasks**: 9

Applied: multi-benchmark-training-pipeline (train -> checkpoint-WGA -> detect -> normalize -> cross-benchmark-stats)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M3)
**Status**: patterns found from base code (Serena MCP unavailable — direct file reads used instead)
**Analyzed Path**: `h-m3/code/`
**Findings**:
- `h-m3/code/detector.py` implements `smooth_curve`, `second_derivative`, `detect_peak(d2_wga, prominence=0.005)` — matches FR-2 exactly (window_size, prominence_threshold identical). H-M4 imports these functions unmodified rather than reimplementing (spec named them `compute_wga_second_derivative`/`detect_crystallization_peak`; actual code names differ — see External Dependencies table for exact import names).
- `h-m3/code/data.py` has `load_wga_from_checkpoint`, `synthesize_curve` — H-M4 needs real full-benchmark training (FR-1 MUST), so this is not reused; H-M4's own `train.py` produces real WGA curves instead of H-M3's synthetic fallback path.
- `h-m3/code/config.py` dataclass pattern (`DetectionConfig`) reused as template for `TimingConfig`.
- `h-m3/code/analyzer.py` `aggregate_seed_results` pattern informs `aggregate_benchmark_timing` but H-M4 needs cross-*benchmark* (not just cross-seed) variance — new function required.
- No existing WILDS training loop or ColoredMNIST constructor exists anywhere in the codebase — `train.py` and `datasets.py` are new.

**Consequence for design**: H-M4 needs actual training infra (`datasets.py`, `models.py`, `train.py`) that no prior hypothesis built, plus a thin reuse layer over H-M3's `detector.py`.

---

## Module Structure

### config.py (`h-m4/code/config.py`)

**Dependencies**: dataclasses

```python
@dataclass
class BenchmarkSpec:
    name: str
    total_epochs: int
    lr: float
    num_classes: int
    image_size: int

@dataclass
class TimingConfig:
    benchmarks: dict = field(default_factory=lambda: {
        "waterbirds": BenchmarkSpec("waterbirds", 100, 1e-3, 2, 224),
        "celebA": BenchmarkSpec("celebA", 50, 1e-4, 2, 224),
        "coloredmnist": BenchmarkSpec("coloredmnist", 30, 1e-3, 10, 32),
    })
    seeds: list[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])
    batch_size: int = 128
    momentum: float = 0.9
    prominence_threshold: float = 0.005
    smoothing_window: int = 5
    expected_range: tuple = (20.0, 40.0)
    variance_target: float = 10.0
    data_root: str = "./data"
    checkpoint_dir: str = "./checkpoints"
    output_dir: str = "./outputs"
    figures_dir: str = "../figures"

CONFIG = TimingConfig()
```

### datasets.py (`h-m4/code/datasets.py`)

**Dependencies**: wilds, torchvision, torch

```python
def get_waterbirds_loaders(config: TimingConfig) -> tuple[DataLoader, DataLoader]: ...
def get_celebA_loaders(config: TimingConfig) -> tuple[DataLoader, DataLoader]: ...
def construct_colored_mnist(correlation: float = 0.95) -> torch.utils.data.Dataset: ...
def get_coloredmnist_loaders(config: TimingConfig) -> tuple[DataLoader, DataLoader]: ...
def get_loaders(benchmark: str, config: TimingConfig) -> tuple[DataLoader, DataLoader]:
    """Dispatch by benchmark name -> (train_loader, val_loader)."""
def compute_wga(model, val_loader, device) -> float:
    """Worst-group accuracy over WILDS val metadata groups (or digit x color groups for ColoredMNIST)."""
```

### models.py (`h-m4/code/models.py`)

**Dependencies**: torchvision

```python
def build_resnet50(num_classes: int, image_size: int) -> torch.nn.Module:
    """ImageNet-pretrained ResNet50, fc replaced; adapts first conv/pool for 32px ColoredMNIST if needed."""
```

### train.py (`h-m4/code/train.py`)

**Dependencies**: datasets, models, config, torch

```python
def train_one_run(benchmark: str, seed: int, config: TimingConfig, device: str) -> np.ndarray:
    """Full training loop, SGD+momentum, records WGA every epoch.
    Saves outputs/{benchmark}_seed{seed}_wga.npy. Returns wga_curve array."""
def run_all_benchmarks(config: TimingConfig, device: str) -> dict[str, dict[int, np.ndarray]]:
    """Returns {benchmark: {seed: wga_curve}} for all 3 benchmarks x 5 seeds (15 runs).
    Skips training if cached .npy exists on disk (resumability)."""
```

### detection.py (`h-m4/code/detection.py`)

**Dependencies**: h-m3 detector module (imported, not reimplemented)

```python
from h_m3_detector import smooth_curve, second_derivative, detect_peak  # see External Dependencies

def detect_and_normalize(wga_curve: np.ndarray, total_epochs: int, config: TimingConfig) -> dict:
    """smooth_curve -> second_derivative -> detect_peak -> normalize epoch to %.
    Returns {detected, peak_epoch, normalized_timing_percent, prominence, snr, in_expected_range}."""
```

### analyzer.py (`h-m4/code/analyzer.py`)

**Dependencies**: detection, numpy

```python
def analyze_all_runs(wga_curves: dict[str, dict[int, np.ndarray]], config: TimingConfig) -> dict:
    """Per (benchmark, seed): detect_and_normalize. Returns nested results dict."""
def aggregate_per_benchmark(results: dict, config: TimingConfig) -> dict:
    """Per-benchmark: mean/std normalized timing across 5 seeds, detection_rate, in_range flag."""
def compute_cross_benchmark_variance(aggregated: dict) -> dict:
    """Std dev of per-benchmark mean normalized timing across 3 benchmarks (FR-5)."""
def compute_range_compliance(aggregated: dict, expected_range: tuple) -> float:
    """% of benchmarks (mean timing) within expected_range (FR-4)."""
def detect_seed_outliers(results: dict, config: TimingConfig) -> dict:
    """Flag seeds >2 std from per-benchmark mean (FR-6)."""
def evaluate_gate(aggregated: dict, cross_var: dict, compliance: float, config: TimingConfig) -> dict:
    """PASS: compliance==100% and cross_var<10. CONDITIONAL: outside range but consistent
    (cross_var<15). FAIL: otherwise. Returns {status, metrics}."""
```

### visualize.py (`h-m4/code/visualize.py`)

**Dependencies**: matplotlib, numpy

```python
def plot_gate_metrics(gate_result: dict, save_path: str) -> None: ...
def plot_normalized_timing_bars(aggregated: dict, expected_range: tuple, save_path: str) -> None: ...
def plot_wga_curves_overlay(wga_curves: dict, config: TimingConfig, save_path: str) -> None: ...
def plot_timing_distribution_boxplot(results: dict, save_path: str) -> None: ...
def plot_cross_benchmark_regression(aggregated: dict, config: TimingConfig, save_path: str) -> None: ...
def plot_gate_dashboard(gate_result: dict, aggregated: dict, save_path: str) -> None: ...
```

### run.py (`h-m4/code/run.py`)

**Dependencies**: config, train, detection, analyzer, visualize

```python
def main() -> None:
    """run_all_benchmarks -> analyze_all_runs -> aggregate_per_benchmark ->
    compute_cross_benchmark_variance -> compute_range_compliance -> evaluate_gate ->
    write outputs/timing_results.json, outputs/aggregated_metrics.yaml -> generate 6 figures."""
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| smooth_curve | `from h_m3.code.detector import smooth_curve` (or path-append `h-m3/code`, `import detector as h_m3_detector`) | `h-m3/code/detector.py` |
| second_derivative | `from h_m3.code.detector import second_derivative` | `h-m3/code/detector.py` |
| detect_peak | `from h_m3.code.detector import detect_peak` | `h-m3/code/detector.py` |

**Verified from**: `h-m3/code/detector.py` (actual implementation). Note: PRD/brief pseudo-code names these `compute_wga_second_derivative`/`detect_crystallization_peak`, but actual H-M3 code uses `smooth_curve`+`second_derivative` (split) and `detect_peak` — Phase 4 Coder must use the real names above, not the spec names. Signature of `detect_peak(d2_wga, prominence=0.005)` returning `{detected, epoch, prominence, snr}` matches spec exactly.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config module | TimingConfig + BenchmarkSpec dataclasses, 3-benchmark params | 4 | 1+1+1+1 |
| A-2 | Dataset loaders | WILDS Waterbirds/CelebA loaders + custom ColoredMNIST construction | 10 | 3+2+3+2 |
| A-3 | WGA computation | Worst-group accuracy over WILDS metadata groups + ColoredMNIST digit x color groups | 7 | 2+2+2+1 |
| A-4 | Model builder | ResNet50 adaptation for 3 benchmarks (224px + 32px) | 4 | 1+1+1+1 |
| A-5 | Training loop (3 benchmarks x 5 seeds) | Full training runs, per-epoch WGA checkpointing, resumability cache | 13 | 4+3+3+3 |
| A-6 | Detection integration | Import H-M3 detector functions, normalize timing, per-run detection | 6 | 2+1+2+1 |
| A-7 | Cross-benchmark statistics | Per-benchmark aggregation, cross-benchmark variance, range compliance, seed outlier detection | 10 | 3+2+3+2 |
| A-8 | Gate evaluation | PASS/CONDITIONAL/FAIL logic per FR-7 | 5 | 1+1+2+1 |
| A-9 | Visualization + orchestration | 6 figures, run.py pipeline wiring, JSON/YAML output | 10 | 3+2+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-7, A-9], Low(4-8): [A-1, A-3, A-4, A-6, A-8], Note: A-5=13 (High-adjacent, largest task — full 15-run training)
