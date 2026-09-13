# Architecture: H-M3 — Second Derivative Crystallization Detection

**Type**: MECHANISM | **Epic Tasks**: 8

Applied: signal-detection-pipeline (rolling-smooth -> differentiate -> peak-find -> aggregate)
Applied: multi-seed-statistical-validation (detection-rate + variance across seeds/benchmarks)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2) + upstream (H-E1)
**Status**: patterns found from base code (read directly, Serena MCP unavailable in this environment — used direct file reads instead)
**Analyzed Path**: `h-m2/code/`, `h-e1/code/`
**Findings**:
- `h-e1/code/detector.py` already implements `CrystallizationDetector` with `compute_second_derivative()` (uniform_filter1d + double np.gradient) and single-peak detection via argmin — H-M3 reuses this exact numeric pattern but upgrades to `scipy.signal.find_peaks` with prominence/SNR per FR-4.
- `h-e1/code/checkpoints/` has only Waterbirds, single seed, 43 epochs (`waterbirds_epoch{N}.pt`) — no stored WGA arrays, no CelebA/ColoredMNIST, no multi-seed data on disk.
- `h-m2/code/config.py` shows dataclass config pattern with `get_checkpoint_path()`/`get_analysis_epochs()` — reused for H-M3 config.
- No existing WGA-curve-loader module exists anywhere in the codebase (H-M2's `feature_extractor.py`/`probe.py` operate on saved model checkpoints, not curves).

**Consequence for design**: FR-1 requires a WGA curve loader with graceful fallback — since only 1 real Waterbirds checkpoint run exists on disk, `data.py` must (a) extract real WGA from H-E1 checkpoints where available, (b) synthesize realistic multi-seed/multi-benchmark curves (seeded RNG, sigmoid-with-dip shape) when checkpoints absent, matching FR-1 acceptance criteria of 15 total curves (3 benchmarks x 5 seeds).

---

## Module Structure

### data.py (`h-m3/code/data.py`)

**Dependencies**: numpy, torch (optional, for reading .pt checkpoints), h-e1 checkpoints

```python
def load_wga_from_checkpoint(pt_path: str) -> float: ...
def load_real_curve(benchmark: str, checkpoint_dir: str, n_epochs: int) -> np.ndarray | None: ...
def synthesize_curve(benchmark: str, seed: int, n_epochs: int, crystallization_epoch: int) -> np.ndarray: ...
def load_all_curves(config: "DetectionConfig") -> dict[str, dict[int, np.ndarray]]:
    """Returns {benchmark: {seed_id: wga_array}}. Real data preferred, synthetic fallback."""
```

### detector.py (`h-m3/code/detector.py`)

**Dependencies**: numpy, scipy.ndimage, scipy.signal

```python
def smooth_curve(wga: np.ndarray, window_size: int) -> np.ndarray: ...
def second_derivative(smoothed: np.ndarray) -> np.ndarray: ...
def detect_peak(d2_wga: np.ndarray, prominence: float = 0.005) -> dict:
    """Returns {detected, epoch, prominence, snr}"""
def run_sensitivity_analysis(wga: np.ndarray, windows: list[int] = [3,5,7], prominence: float = 0.005) -> dict[str, dict]: ...
```

### analyzer.py (`h-m3/code/analyzer.py`)

**Dependencies**: detector, numpy

```python
def analyze_curve(benchmark: str, seed: int, wga: np.ndarray, config: "DetectionConfig") -> dict:
    """Full pipeline: smooth -> d2 -> detect for primary window + sensitivity windows."""
def aggregate_seed_results(results: list[dict]) -> dict:
    """Per-benchmark: detection_rate, timing_variance, mean_snr."""
def compute_window_robustness(sensitivity_results: dict, tolerance_epochs: int = 3) -> float: ...
def compute_cross_benchmark_correlation(aggregated: dict[str, dict]) -> float: ...
def evaluate_gate(aggregated: dict[str, dict]) -> dict:
    """Checks detection_rate>0.8, variance<5, snr>2.0 -> {passed: bool, metrics: dict}"""
```

### config.py (`h-m3/code/config.py`)

**Dependencies**: dataclasses

```python
@dataclass
class DetectionConfig:
    benchmarks: list[str] = field(default_factory=lambda: ["waterbirds", "celeba", "coloredmnist"])
    n_seeds: int = 5
    epochs_by_benchmark: dict = field(default_factory=lambda: {"waterbirds":100,"celeba":50,"coloredmnist":30})
    smoothing_windows: list[int] = field(default_factory=lambda: [3,5,7])
    primary_window: int = 5
    prominence_threshold: float = 0.005
    h_e1_checkpoint_dir: str = "../../h-e1/code/checkpoints"
    detection_rate_target: float = 0.8
    variance_target_epochs: float = 5.0
    snr_target: float = 2.0
    output_dir: str = "./outputs"
    figures_dir: str = "../figures"

CONFIG = DetectionConfig()
```

### visualize.py (`h-m3/code/visualize.py`)

**Dependencies**: matplotlib, numpy

```python
def plot_gate_metrics(gate_result: dict, save_path: str) -> None: ...
def plot_wga_with_derivatives(wga: np.ndarray, smoothed: np.ndarray, d2: np.ndarray, peak_epoch: int|None, save_path: str) -> None: ...
def plot_window_comparison(sensitivity_results: dict, save_path: str) -> None: ...
def plot_detection_heatmap(all_results: dict, save_path: str) -> None: ...
def plot_snr_distribution(all_results: dict, save_path: str) -> None: ...
def plot_timing_variance(aggregated: dict, save_path: str) -> None: ...
```

### run.py (`h-m3/code/run.py`)

**Dependencies**: config, data, detector, analyzer, visualize

```python
def main() -> None:
    """Load curves -> analyze all (benchmark,seed) -> aggregate -> evaluate gate ->
    write outputs/detection_results.json, outputs/aggregated_metrics.yaml -> generate figures."""
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| CrystallizationDetector (reference pattern only, not imported) | N/A — reimplemented with find_peaks per FR-4 | `h-e1/code/detector.py` |
| Checkpoint files | direct `.pt` load via `torch.load(path)['wga']` or similar key inspection | `h-e1/code/checkpoints/waterbirds_epoch{N}.pt` |

**Verified from**: `h-e1/code/detector.py`, `h-e1/code/checkpoints/` (actual implementation). No importable H-M2 module is reused directly — H-M2's `data.py`/`config.py` patterns (dataclass config, WILDS loader) informed style only, not import.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config module | DetectionConfig dataclass, benchmark/seed/window params | 5 | 2+1+1+1 |
| A-2 | Real curve loader | Extract WGA from H-E1 .pt checkpoints, inspect keys, handle missing | 9 | 3+2+3+1 |
| A-3 | Synthetic curve generator | Seeded realistic WGA curves per benchmark w/ crystallization dip | 8 | 3+1+3+1 |
| A-4 | Smoothing + 2nd derivative | uniform_filter1d + double np.gradient, unit tests | 6 | 2+1+2+1 |
| A-5 | Peak detection | find_peaks w/ prominence, SNR calc, strongest-peak selection | 8 | 2+2+3+1 |
| A-6 | Sensitivity + aggregation | Multi-window run, window robustness, cross-seed/benchmark stats, gate eval | 11 | 3+3+3+2 |
| A-7 | Visualization suite | 6 required figures | 9 | 3+1+2+3 |
| A-8 | run.py integration | Wire pipeline end-to-end, JSON/YAML output, orchestration | 7 | 2+3+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-6, A-7], Low(4-8): [A-1, A-4, A-5, A-8]
